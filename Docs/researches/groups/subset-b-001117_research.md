# subset-b-001117 research

Grouped research for Qualcomm clock controller sources under `sources/distributed-fs/ceph-client/drivers/clk/qcom`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpm.c

## Purpose
Implements the legacy Qualcomm RPM clock-controller provider used by older MSM/APQ/IPQ platforms where clock votes are sent directly to the RPM MFD. It exposes RPM-managed fabric, peripheral, PLL, and XO-buffer clocks to the common clock framework, translates prepare/unprepare and rate changes into active/sleep RPM votes, and registers per-SoC clock arrays selected by device-tree compatible strings.

## Important APIs, Types, And Functions
- `struct clk_rpm` is the per-clock state: RPM resource id, optional XO bit offset, active-only flag, cached rate, enabled state, branch-mode behavior, peer active/sleep clock, `clk_hw`, RPM handle, and containing `rpm_cc`.
- `struct rpm_cc` stores the clock table, number of clocks, aggregate XO-buffer bitfield, and XO-specific mutex.
- `clk_rpm_prepare`, `clk_rpm_unprepare`, and `clk_rpm_set_rate` compute aggregate votes across a normal and active-only peer, convert rate clocks to kHz, and use boolean votes for branch clocks.
- `clk_rpm_xo_prepare` and `clk_rpm_xo_unprepare` update the shared `QCOM_RPM_CXO_BUFFERS` bitfield using `QCOM_RPM_XO_MODE_ON` shifted by each buffer offset.
- `clk_rpm_handoff` sends `INT_MAX` active and sleep votes during probe to preserve already enabled RPM resources, except for PLL4 and CXO buffers.
- `rpm_clk_probe` retrieves the parent `struct qcom_rpm`, initializes every listed clock, registers the `clk_hw`s, and publishes the OF clock provider.

## Control Flow
The platform driver is registered at `core_initcall`. Probe reads the SoC descriptor from the match table, stores the parent RPM handle in each static `clk_rpm`, performs handoff writes, then registers all available clocks and `qcom_rpm_clk_hw_get`. Common-clock consumers later obtain a clock by binding index, set rates, and prepare or unprepare it. Prepare takes `rpm_clk_lock`, ignores zero-rate clocks, converts the local vote and the enabled peer vote into active/sleep votes, sends active first, then sleep, and marks the clock enabled on success. Unprepare recomputes the vote from only the enabled peer and clears `enabled` after both active and sleep writes succeed. Rate changes only send messages while the clock is already enabled, then cache the requested rate; RPM owns final rounding, so determine/recalc are intentionally pass-through/cached.

## State And Persistence
Driver state is mostly static per-clock objects plus runtime fields `rate`, `enabled`, `rpm`, `rpm_cc`, and the shared `xo_buffer_value`. Persistent hardware/firmware state is the active and sleep RPM vote for each resource id. Normal and active-only peers share a remote resource, so each operation recomputes the max aggregate vote rather than writing independent hardware state. XO buffers persist as bits in one RPM resource. No state is stored on disk.

## Dependencies And Integration Points
The file depends on the RPM MFD API `qcom_rpm_write`, RPM and clock dt-bindings, the Linux common clock framework, OF clock providers, and board-provided `pxo` or `cxo` parents. It integrates with older `qcom,rpmcc-*` nodes, downstream consumers using `qcom,rpmcc.h` clock indexes, and power-management firmware that interprets active/sleep resource votes.

## Risks And Edge Cases
Peer aggregation is subtle: disabling one side must leave the other side's vote intact, and branch resources must be reduced to 0/1 after aggregation. Sleep votes for active-only clocks must be zero or they can keep resources active through suspend. Failed sleep writes after an active write attempt a rollback to the peer active vote, but rollback failure is not separately reported. The static clock objects are reused by compatible tables, so probe lifetime assumes only one matching instance per system. XO-buffer writes require the separate `xo_lock` because several logical clocks share one remote bitfield.

## Test Signals
Useful signals include successful probe for msm8660/apq8064/ipq806x compatibles, valid OF lookup indexes and `-ENOENT` for sparse entries, active/sleep RPM messages matching max peer rates, active-only clocks dropping sleep votes to zero, branch clocks sending 0/1 values, XO buffers preserving unrelated bits, and no unintended clock drop during handoff or suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpmh.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpmh.c

## Purpose
Implements Qualcomm RPMh clock providers for modern platforms. It exposes ARC/VRM on-off clocks and BCM rate-vote clocks, resolves RPMh resource names through command DB, sends TCS commands to sleep, wake, and active-only RPMh states, and supplies many SoC-specific clock tables for RPMh-enabled Qualcomm chips.

## Important APIs, Types, And Functions
- `struct clk_rpmh` holds the common-clock handle, command-DB resource name, divider, resolved RPMh address, on value, local and aggregate state masks, last sent aggregate state, valid state mask, BCM unit, device pointer, and peer.
- `struct clk_rpmh_desc` maps dt-binding indexes to `clk_hw` pointers and marks platforms where `clka*` resources may be absent.
- `clk_rpmh_send_aggregate_command` compares `aggr_state` against `last_sent_aggr_state`, sends only changed sleep/wake/active state commands, and mirrors last-sent state to the peer.
- `clk_rpmh_aggregate_state_send_command`, `clk_rpmh_prepare`, and `clk_rpmh_unprepare` maintain peer aggregation for normal and always-on RPMh clocks.
- `clk_rpmh_bcm_set_rate`, `clk_rpmh_bcm_prepare`, and `clk_rpmh_bcm_send_cmd` implement Bus Clock Manager active-only votes using command-DB auxiliary unit data.
- `clk_rpmh_probe` resolves every clock resource through `cmd_db_read_addr`, reads optional `struct bcm_db` aux data, registers clocks, and adds the OF provider.

## Control Flow
Probe chooses a descriptor by compatible string, then walks its indexed `clk_hw` table. For each non-null clock it resolves the command-DB resource address, optionally tolerates missing `clka*` resources on descriptors with `clka_optional`, reads auxiliary data, stores the device pointer, and registers the hardware. For ARC/VRM clocks, prepare sets the clock's state to its valid mask, ORs it with the peer state, and sends only state transitions. Non-AO clocks vote sleep, wake, and active states; AO peers vote wake and active only. Active-state sends wait when a nonzero aggregate active vote is present; other sends can be asynchronous. For BCM clocks, set-rate stores a scaled aggregate state, and prepare/unprepare sends one active-only `BCM_TCS_CMD` because RPMh can reuse active state when sleep/wake votes are unset.

## State And Persistence
Each `clk_rpmh` caches command DB resolution (`res_addr`), message scaling (`unit`), current local state, aggregate peer state, and last state actually sent. Persistent state is the RPMh vote stored by firmware for the resource address in each RPMh state. For BCM clocks, `aggr_state` is a numeric bandwidth/clock vote rather than a bitmask. Static clock definitions are shared across descriptors, so state is process-global within the kernel image.

## Dependencies And Integration Points
The driver depends on `soc/qcom/cmd-db` for resource address and aux data, `soc/qcom/rpmh` and `soc/qcom/tcs` for command submission, RPMh dt-bindings for public clock indexes, and the common clock framework. It integrates with RPMh firmware resources such as `xo.lvl`, `qphy.lvl`, `rfclka*`, `clka*`, and BCM resources like `CE0`, `IP0`, `HK0`, `PKA0`, and `QP0`.

## Risks And Edge Cases
Command DB names must match firmware exactly; a missing resource fails probe except for explicitly optional `clka*` entries. State-change filtering relies on `last_sent_aggr_state`, so errors must not update it. Failed enable attempts roll back local state but aggregate state can be transiently stale until the next operation. BCM rate votes are clamped to `BCM_TCS_CMD_VOTE_MASK`, so high rates can saturate. Static objects reused across many compatible tables require only one RPMh clock device instance. Sleep/wake/active ordering matters for suspend behavior.

## Test Signals
Test signals include successful command-DB resolution for every non-optional entry, missing optional `clka*` entries being nulled without probe failure, prepare/unprepare sending only changed RPMh states, AO and non-AO peers aggregating correctly, BCM `set_rate` affecting prepared clocks immediately, active sends waiting when enabling, and recalc rates returning parent/divider or `aggr_state * unit` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpmh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-smd-rpm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-smd-rpm.c

## Purpose
Provides Qualcomm RPM clock controllers over the SMD RPM transport. It defines many reusable RPM clock templates and SoC-specific binding tables, sends active/sleep SMD RPM votes for rate and branch clocks, enables RPM-side clock scaling, and bootstraps interconnect-related RPM clocks until the interconnect driver takes ownership.

## Important APIs, Types, And Functions
- `struct clk_smd_rpm` stores RPM resource type, key, resource id, active-only flag, enabled/branch flags, peer pointer, common-clock hardware, and cached rate.
- `struct rpm_smd_clk_desc` contains the public clock table plus an interconnect clock list, count, and `scaling_before_handover` quirk.
- The `DEFINE_CLK_SMD_RPM*` macros build paired normal and active-only clocks for rate resources, branch resources, XO buffers, pin-control variants, bus clocks, and QDSS state resources.
- `clk_smd_rpm_prepare`, `clk_smd_rpm_unprepare`, and `clk_smd_rpm_set_rate` aggregate peer votes and write active/sleep requests with `qcom_rpm_smd_write`.
- `clk_smd_rpm_handoff` votes `INT_MAX` for rate clocks or 1 for branch clocks in both active and sleep sets before registration.
- `clk_smd_rpm_enable_scaling` writes `QCOM_RPM_SMD_KEY_ENABLE` to the misc scaling resource for both sleep and active states.
- `rpm_smd_clk_probe` performs handoff, enables scaling in the correct order, registers clocks, registers the OF provider, and creates the `icc_smd_rpm` platform device.

## Control Flow
Probe stores the parent `struct qcom_smd_rpm` in the global `rpmcc_smd_rpm`, selects a descriptor by compatible, optionally enables scaling before handoff, sends handoff votes for all exposed clocks and any interconnect bootstrap clocks, enables scaling after handoff for the normal case, registers each common-clock object, adds the OF clock provider, and then registers an `icc_smd_rpm` child device. Runtime prepare mirrors the legacy direct-RPM logic: under `rpm_smd_clk_lock`, it converts the local clock and enabled peer into active/sleep votes, reduces branch resources to boolean values, writes active first and sleep second, and marks enabled. Unprepare leaves only the peer vote in place. Set-rate sends new aggregate votes only for an enabled clock and then updates the cached rate.

## State And Persistence
The transport handle is global, while each static clock object tracks `enabled` and cached `rate`. Persistent firmware state consists of SMD RPM active and sleep votes keyed by resource type, id, and request key. Normal and active-only peers share one remote resource and are aggregated in software. Interconnect handoff clocks are not registered as regular consumer clocks here; they are temporarily voted to avoid premature gating before the interconnect framework initializes.

## Dependencies And Integration Points
The file depends on `linux/soc/qcom/smd-rpm.h`, RPM SMD request layout, RPM clock dt-bindings, common clock framework, OF providers, and platform-device creation. It integrates with many `qcom,rpmcc-*` compatibles from MSM8909 through SM6375/QCM2290, with RPM-managed NoC/BIMC clocks, XO buffer clocks, QDSS, CE/IPA/HWKM/PKA/QPIC resources, and the `icc_smd_rpm` interconnect driver.

## Risks And Edge Cases
Ordering around scaling and handoff is platform-specific; `msm8974` enables scaling first while most platforms do it after handoff. Branch and rate clocks use different RPM keys and value semantics, so a wrong macro or table entry can vote the wrong resource. Active-only peers must not hold sleep votes. The global RPM pointer and static objects assume a single RPM SMD clock-controller instance. Interconnect bootstrap clocks must match the later ICC topology or buses can be under-voted during driver ordering gaps. Provider lookup returns `-ENOENT` for sparse table entries, so bindings and tables must stay aligned.

## Test Signals
Signals include correct probe and clock registration for each compatible, RPM SMD writes with expected resource type/id/key/value, scaling writes in active and sleep sets, branch votes as 0/1, rate votes in kHz, active-only sleep votes of zero, successful creation and cleanup of `icc_smd_rpm`, valid sparse-index errors, and stable bus/interconnect clocks during early boot before ICC handover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-smd-rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-spmi-pmic-div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-spmi-pmic-div.c

## Purpose
Implements a common-clock provider for Qualcomm SPMI PMIC clock-divider blocks. The driver registers one or more divider clocks under a PMIC register map, computes power-of-two divider factors, gates the hardware with required nanosecond delays based on the XO period, and exposes phandle indexes starting at 1.

## Important APIs, Types, And Functions
- `struct clkdiv` holds the parent PMIC regmap, base offset for one divider block, per-clock spinlock, `clk_hw`, and cached XO period in nanoseconds.
- `div_factor_to_div` maps hardware factor 0 or 1 to divide-by-1 and larger factors to powers of two; `div_to_div_factor` maps requested divisors to a capped 3-bit hardware factor.
- `is_spmi_pmic_clkdiv_enabled`, `__spmi_pmic_clkdiv_set_enable_state`, and `spmi_pmic_clkdiv_set_enable_state` read and update `REG_EN_CTL` and apply documented enable/disable delays.
- `clk_spmi_pmic_div_enable`, `disable`, `determine_rate`, `recalc_rate`, and `set_rate` implement the common-clock operations.
- `spmi_pmic_clkdiv_probe` reads DT properties, obtains the parent regmap and XO clock rate, allocates a counted flexible-array controller, registers `div_clkN` clocks, and adds the provider.

## Control Flow
Probe reads the PMIC child node's `reg` base and `qcom,num-clkdivs`, gets the parent's regmap, obtains the `xo` input clock to calculate `cxo_period_ns`, then creates one `clkdiv` per 0x100-byte block. Each registered clock has a single parent from clock index 0 and the same divider operations. Runtime enable/disable serialize register access with `spin_lock_irqsave`. `set_rate` computes the divider factor from `parent_rate / rate`, disables the divider if it is currently enabled, writes `REG_DIV_CTL1`, and re-enables it with a delay calculated from the new factor.

## State And Persistence
Software state is per-clock base, regmap, lock, and XO period. Persistent hardware state is the divider factor in `REG_DIV_CTL1` and the enable bit in `REG_EN_CTL`; it remains in PMIC registers until changed or reset. There is no saved software copy of the selected divider, so recalc reads hardware.

## Dependencies And Integration Points
The driver depends on the parent SPMI PMIC/MFD regmap, DT properties `reg` and `qcom,num-clkdivs`, an `xo` clock, common-clock registration, and `devm_of_clk_add_hw_provider`. Consumers reference clocks by one-based phandle index. It integrates with PMIC-controlled external clocks or peripheral reference clocks that need simple divided XO outputs.

## Risks And Edge Cases
The provider intentionally subtracts one from the phandle index, so DT consumers using zero will fail. `clk_get_rate(xo)` must be nonzero or period calculation would be invalid. `parent_rate / rate` truncates in `set_rate`, while `determine_rate` rounds up before mapping to a power-of-two divider, so caller expectations should be checked. Enable/disable delays depend on accurate XO period. Register writes during rate changes temporarily gate the clock, which may not be acceptable for always-on consumers.

## Test Signals
Test with invalid and valid one-based clock indexes, missing `reg`, missing `qcom,num-clkdivs`, absent/deferred `xo`, and absent parent regmap. Runtime signals include recalc matching hardware factor, determine-rate choosing power-of-two divisions, rate changes while enabled toggling enable around the divider write, and scoped delays visible in register-level traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-spmi-pmic-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/common.c

## Purpose
Provides shared helper code for Qualcomm clock-controller drivers. It supplies frequency-table lookup helpers, parent-map lookup helpers, MMIO-to-regmap mapping, PLL FSM configuration, board clock compatibility registration, protected-clock filtering, interconnect clock registration, PLL/CBCR preconfiguration, reset/GDSC registration, common-clock registration, and generic probe wrappers used by many qcom clock controllers.

## Important APIs, Types, And Functions
- `struct qcom_cc` is the runtime container for reset controller state, registered `clk_regmap` array, clock count, and attached power-domain list.
- `qcom_find_freq`, `qcom_find_freq_multi`, and `qcom_find_freq_floor` select frequency table entries at or above a requested rate, multi-table equivalent, or floor entry.
- `qcom_find_src_index` and `qcom_find_cfg_index` map between hardware parent source/config values and common-clock parent indexes.
- `qcom_cc_map`, `qcom_cc_probe`, and `qcom_cc_probe_by_index` create an MMIO regmap and call `qcom_cc_really_probe`.
- `qcom_cc_really_probe` is the central controller-registration path for resets, GDSCs, DFS RCGs, hardware clocks, regmap clocks, OF provider, interconnect clocks, RPM runtime-PM, protected clocks, and optional driver-data initialization.
- `qcom_cc_register_board_clk` and `qcom_cc_register_sleep_clk` preserve compatibility with old DTs by creating fixed-rate and fixed-factor board clocks.

## Control Flow
A SoC-specific driver builds a `qcom_cc_desc` and calls `qcom_cc_probe`. The common path maps registers, allocates `qcom_cc`, attaches optional PM domains, resumes RPM-backed devices if requested, configures PLLs and critical CBCRs from `qcom_cc_driver_data`, registers the reset controller, registers GDSCs with cleanup, registers DFS RCGs, drops clocks listed in `protected-clocks`, registers standalone `clk_hw`s and `clk_regmap`s, adds the OF clock provider, and optionally registers interconnect clock nodes. On errors after RPM runtime get, the `put_rpm` path releases the runtime-PM reference.

## State And Persistence
Runtime state persists in devm-managed `qcom_cc`, reset controller registration, GDSC registrations, OF provider data, and optional interconnect clock data. Hardware state is changed by PLL configuration, CBCR enable writes, reset operations, GDSC power-domain operations, and optional driver-specific register configuration. Protected clocks are represented by setting entries in the runtime `rclks` table to NULL so the provider hides them.

## Dependencies And Integration Points
The file depends on regmap, platform MMIO resources, common clock framework, reset-controller core, Qualcomm reset/GDSC/branch/RCG/alpha PLL helpers, interconnect-clk support, PM runtime, OF properties, and generic device-managed cleanup. It is the integration point for most qcomcc SoC driver files, including the display controllers in this subset.

## Risks And Edge Cases
`protected-clocks` silently nulls entries, so downstream consumers must tolerate provider NULLs for firmware-owned clocks. PLL driver data requires both config and register layout; missing fields abort probe. RPM runtime handling must balance resume-and-get with put on every path. Interconnect clock registration depends on valid clock IDs in `icc_hws`. Board-clock compatibility code can create synthetic clock names only when old DT nodes are absent. Registration order matters because GDSCs and resets share the same regmap and reset controller.

## Test Signals
Test signals include frequency helpers selecting first/fastest/floor entries correctly, invalid parent lookups returning `-ENOENT`, failed MMIO/regmap mapping propagating errors, protected clocks disappearing from OF lookup, reset and GDSC registration succeeding, PLL/CBCR initialization writes occurring before clock registration, RPM runtime refs balanced on probe failure, and interconnect clock registration guarded by `CONFIG_INTERCONNECT_CLK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/common.h

## Purpose
Declares the shared Qualcomm clock-controller data structures, constants, and helper APIs implemented by `common.c` and consumed by SoC-specific qcom clock drivers. It defines the descriptor contract that lets generated-style controller files register clocks, resets, GDSCs, interconnect clocks, RPM runtime behavior, and optional preconfiguration data through one common probe path.

## Important APIs, Types, And Functions
- PLL FSM constants define bit positions and masks for bias count, lock count, FSM enable, and FSM reset fields used by `qcom_pll_set_fsm_mode`.
- `struct qcom_icc_hws_data` links an interconnect master/slave pair to a clock id in the descriptor clock table.
- `struct qcom_cc_driver_data` supplies optional alpha PLLs to configure, CBCRs to force-enable, DFS RCG descriptors, and a driver-specific register-configuration callback.
- `struct qcom_cc_desc` is the top-level controller descriptor: regmap config, regmap clocks, resets, GDSCs, standalone `clk_hw`s, interconnect hardware data, RPM runtime flag, and driver-data pointer.
- `struct parent_map` maps logical parent sources to hardware mux config values.
- The header exports frequency lookup, parent lookup, board/sleep clock registration, regmap mapping, and common probe helpers.

## Control Flow
There is no executable control flow in the header. SoC-specific drivers fill static instances of `qcom_cc_desc` and optional `qcom_cc_driver_data`, then call `qcom_cc_probe`, `qcom_cc_probe_by_index`, or `qcom_cc_really_probe`. Clock implementation files call frequency and parent helpers from their rate and mux operations.

## State And Persistence
The header itself stores no runtime state. Its structures describe state owned by controller drivers and `common.c`: clock arrays, reset maps, GDSC lists, interconnect data, and optional initialization hooks. Hardware persistence is indirect through the consumers of these declarations.

## Dependencies And Integration Points
It forward-declares key kernel and qcom types instead of including all implementation headers. It integrates SoC clock-controller files with regmap, platform devices, reset maps, GDSCs, alpha PLLs, RCG DFS data, common-clock hardware, and optional interconnect clock support.

## Risks And Edge Cases
Descriptor arrays must align with dt-binding indexes, and counts must match the actual array sizes. `icc_hws[*].clk_id` must reference a registered clock. Setting `use_rpm` changes runtime-PM behavior in common probe. Missing `driver_data` is valid, but partially filled PLL data is not. Because this header forward-declares several structs, implementation files must include the concrete subsystem headers before dereferencing fields.

## Test Signals
Useful signals are build coverage across many qcomcc drivers, static analysis for descriptor count/index mismatches, probe success for descriptors with and without GDSCs/resets/interconnect clocks, and compile-time detection when new fields require updated initializers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-eliza.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-eliza.c

## Purpose
Defines the Qualcomm Eliza display clock controller. It describes the DISPCC register map, PLLs, parent muxes, RCGs, dividers, branch gates, resets, GDSCs, critical CBCRs, and probe descriptor needed to expose MDSS, DSI, DisplayPort, HDMI, oscillator, XO, and sleep clocks through the common qcom clock framework.

## Important APIs, Types, And Functions
- Binding-order enums map external DT parent clock indexes and internal parent IDs used in parent maps.
- `disp_cc_pll0`, `disp_cc_pll1`, and `disp_cc_pll2` define two Lucid OLE PLLs sourced from `bi_tcxo` and one Pongo ELU PLL sourced from sleep clock, with detailed `alpha_pll_config` values.
- Parent maps connect RCGs to `bi_tcxo`, sleep, local PLL outputs, DSI PHY byte/DSI clocks, DP PHY link/VCO clocks, and HDMI PHY PLL clock.
- RCGs cover esync, MDSS AHB, DSI byte/escape/pixel clocks, four DPTX aux/link/pixel groups, HDMI app/pclk, MDP, oscillator, sleep, and XO sources.
- `clk_regmap_div` entries expose byte and DP/HDMI link dividers, with read-only divider ops where PHY hardware owns the divider.
- `clk_branch` entries gate the MDSS functional clocks and use branch halt checks through qcom branch ops.
- `mdss_gdsc` and `mdss_int2_gdsc` define display power domains; reset map entries cover MDSS core, INT2, and RSCC resets.
- `clk_eliza_regs_configure` sets `DISP_CC_MISC_CMD` bit 4 to enable MDP clock gating.

## Control Flow
The module registers a platform driver for `qcom,eliza-dispcc`. Probe delegates directly to `qcom_cc_probe` with `disp_cc_eliza_desc`. Common probe maps the DISPCC MMIO region, enables RPM runtime handling because `.use_rpm = true`, configures all listed PLLs, force-enables critical CBCRs for sleep/XO/RSCC clocks, runs the Eliza-specific MDP clock-gating register write, registers resets and GDSCs, registers all regmap clocks, and publishes the clock provider. Runtime clock operations are handled by the shared alpha PLL, RCG, divider, branch, reset, and GDSC helpers referenced by the descriptors.

## State And Persistence
Software state is the static descriptor table plus devm-managed common qcomcc state allocated during probe. Hardware state persists in DISPCC registers: PLL configuration at offsets 0x0, 0x1000, and 0x2000; RCG command registers; divider registers; CBCR enable bits; reset registers; GDSCR power-domain registers; and the miscellaneous MDP clock-gating bit. The provider also depends on external parent clocks supplied by other display PHY or board-clock providers.

## Dependencies And Integration Points
The driver depends on `qcom,eliza-dispcc` dt-bindings, `common.c`, alpha PLL, branch, PLL, RCG, regmap divider/mux, GDSC, and reset helpers. It integrates with the MDSS display subsystem, DSI PHYs, DP PHYs, HDMI PHY, RPM/PM runtime, and genpd consumers of `MDSS_GDSC` and `MDSS_INT2_GDSC`.

## Risks And Edge Cases
The binding enum order must match `qcom,eliza-dispcc.h` and the parent clock list in DT. Parent maps for DP/DSI/HDMI clocks must match actual PHY wiring or pixel/link clocks will select the wrong source. Critical CBCRs should not be dropped or display sleep/XO/RSCC behavior can break low-power states. `max_register` intentionally excludes TZ-owned registers above the allowed range; accidental access outside this range would fail through regmap. PLL config values are silicon-specific and high risk to edit without hardware validation.

## Test Signals
Test signals include successful probe and provider registration, PLL lock and expected rates for PLL0/1/2, MDP frequency table selections up to 660 MHz, correct DSI/DP/HDMI parent switching, branch halt status for MDSS clocks, GDSC on/off transitions retaining flip-flops, resets toggling at documented offsets, RSCC and sleep/XO critical clocks staying enabled, and working display bring-up across DSI, DP, and HDMI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-eliza.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-glymur.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-glymur.c

## Purpose
Defines the Qualcomm Glymur display clock controller. It provides the generated-style static descriptions for DISPCC PLLs, mux parents, RCGs, link dividers, branch clocks, GDSCs, resets, critical CBCRs, and the common qcomcc descriptor used to register the controller for `qcom,glymur-dispcc`.

## Important APIs, Types, And Functions
- Binding-order enums describe required external parents: `bi_tcxo`, sleep, four DP PHY link/VCO sources, two DSI PHY byte/DSI sources, and two standalone PHY link/VCO source pairs.
- `disp_cc_pll0` and `disp_cc_pll1` are Taycan EKO T alpha PLLs, configured for approximately 257.142858 MHz and 600 MHz source roles.
- Parent maps cover DP and standalone PHY VCO/link sources, DSI byte and DSICLK sources, local PLL outputs, sleep clock, and `bi_tcxo`.
- RCGs define esync, AHB, DSI byte/escape/pixel, four DPTX aux/link/pixel groups, MDP, oscillator, sleep, XO, and vsync sources; several use `clk_rcg2_shared_ops` and MDP sets `hw_clk_ctrl`.
- Divider clocks include byte dividers and both ordinary and `dpin` read-only DP link dividers for DPTX0-DPTX3.
- Branch clocks gate MDSS AHB, byte/interface, DPTX aux/link/dpin/interface/pixel/router, escape, MDP/LUT, non-GDSC AHB, pclk, RSCC, vsync, and oscillator clocks.
- `disp_cc_mdss_core_gdsc` and `disp_cc_mdss_core_int2_gdsc` define the display power domains; reset map entries cover core, INT2, and RSCC.

## Control Flow
The module platform driver matches `qcom,glymur-dispcc` and calls `qcom_cc_probe` with `disp_cc_glymur_desc`. The common qcom probe maps registers up to `0x11014`, enables RPM runtime semantics, configures PLL0 and PLL1 from `disp_cc_glymur_driver_data`, force-enables sleep and XO critical CBCRs, registers reset and GDSC providers, registers all `clk_regmap` clocks in the binding-indexed array, and publishes the OF clock provider. Runtime operations are delegated to common qcom alpha PLL, RCG, divider, branch, reset, and GDSC implementations.

## State And Persistence
The driver keeps no dynamic state beyond what common qcomcc allocates during probe. Persistent hardware state lives in DISPCC MMIO registers: PLL configuration, RCG source/divider state, read-only PHY-controlled dividers, CBCR gates, reset bits, and GDSCR power domains. External PHY and board clocks are parents rather than state owned by this driver.

## Dependencies And Integration Points
The file depends on `qcom,glymur-dispcc` dt-bindings and the qcom clock helper stack: alpha PLL, branch, PLL, RCG, regmap divider/mux, common probe, GDSC, and reset. It integrates with MDSS display, DSI PHYs, multiple DP/standalone PHY blocks, RSCC display low-power handling, runtime PM through `.use_rpm`, and genpd consumers of the two MDSS GDSCs.

## Risks And Edge Cases
Binding indexes, parent-map hardware values, and clock table indexes must stay synchronized with DT bindings and hardware documentation. Standalone PHY parent ordering is an additional source of mismatch compared with simpler DISPCC variants. Read-only `dpin` dividers must not be treated as programmable by consumers. MDP frequency table values up to 717 MHz and PLL config constants are silicon-specific. Only sleep and XO CBCRs are marked critical here, unlike Eliza's extra RSCC critical entries, so RSCC behavior should be validated on hardware.

## Test Signals
Useful signals include successful probe, valid OF clock lookup for all binding indexes, PLL lock at expected rates, MDP rate selection including 19.2 MHz and 717 MHz entries, correct parent switching for DP/standalone PHY and DSI clocks, branch halt checks for every MDSS gate, GDSC power-domain transitions, reset assertion/deassertion at core/INT2/RSCC offsets, and display operation across DSI and all DP/standalone PHY paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-glymur.c -->

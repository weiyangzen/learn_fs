# subset-b-001116 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.c

## Purpose
Implements Qualcomm alpha PLL clock operations for the common clock framework. The file covers generic alpha PLLs and many hardware families, including Huayra, Fabia, Trion/Lucid, Zonda/Regera, Lucid 5LPE/Evo/OLE, Pongo ELU, Rivian, Stromer, and slew-capable PLLs. It translates CCF rate and enable requests into regmap writes against family-specific PLL layouts.

## Important APIs, Types, And Functions
Exports the global register offset table `clk_alpha_pll_regs`, configuration helpers such as `clk_alpha_pll_configure()`, `clk_fabia_pll_configure()`, `clk_trion_pll_configure()`, `clk_lucid_evo_pll_configure()`, `clk_pongo_elu_pll_configure()`, `qcom_clk_alpha_pll_configure()`, and many `struct clk_ops` tables. Core helpers include `wait_for_pll()`, `alpha_pll_round_rate()`, `alpha_pll_calc_rate()`, `alpha_pll_find_vco()`, `clk_alpha_pll_update_latch()`, `clk_alpha_pll_update_configs()`, and per-family enable, disable, recalc, determine, and set-rate callbacks.

## Control Flow
Configuration helpers write L, alpha, config, test, user, VCO, divider, and output bits using a `struct alpha_pll_config`. Generic enable clears bypass, waits, deasserts reset, waits for lock, then enables output; FSM paths vote through `clk_enable_regmap()` and poll active/offline bits. Rate changes calculate integer and fractional fields, validate VCO ranges, update registers, and, when the PLL is running and supports dynamic updates, latch the new values and wait for update acknowledgements. Family-specific paths adjust this sequence: Huayra allows live L-only changes, Fabia and Trion use OPMODE and calibration, Lucid variants use latch bits and calibration state, Zonda polls frequency-lock in CFA mode, Pongo calibrates against XO before selecting an internal clock, and Stromer can slew within a VCO range.

## State And Persistence
Persistent state lives in hardware registers selected by `offset` and `regs`; software carries only static descriptors, VCO tables, flags, and CCF `clk_hw` objects. Hardware state includes mode bits, lock/update/offline flags, OPMODE, L/alpha/fraction fields, post-dividers, output enables, calibration fields, and VCO selection. Dynamic update and slew paths preserve enabled state while altering rate; other paths may disable or park outputs temporarily.

## Dependencies And Integration Points
Depends on regmap, Linux CCF provider APIs, divider helpers, delays, and qcom common helpers such as `qcom_pll_set_fsm_mode()`. The header supplies descriptor types and exported ops used by SoC clock controller drivers, including the MSM8996 CPU and CBF drivers in this subset. `clk_regmap` vote helpers are used when PLLs run in hardware FSM mode.

## Risks And Edge Cases
Most failures are timeout or invalid-rate paths: lock, active, offline, latch, and update bits can fail to change. Incorrect `regs` tables or alpha widths corrupt unrelated PLL fields. Several configure functions intentionally skip bootloader-enabled PLLs to avoid hanging downstream RCGs. Rate rounding has family-specific limits; Fabia, Trion, Agera, and Zonda reject rounded rates outside a small margin. Slew-capable PLLs cannot dynamically switch VCO ranges and fall back to full set-rate. Some functions ignore regmap read failures in best-effort disable paths.

## Test Signals
High-value tests are boot-time configuration for every PLL type, enable/disable transitions in normal and FSM modes, dynamic set-rate while enabled and disabled, VCO range rejection, alpha rounding/recalc consistency, post-divider programming, timeout injection for lock/update bits, bootloader-left-enabled Trion/Lucid handling, and CPU/CBF rate changes that rely on alpha PLL dynamic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.h

## Purpose
Defines the internal Qualcomm alpha PLL contract shared by SoC clock controller drivers and `clk-alpha-pll.c`. It enumerates supported PLL register layouts, register offset slots, data structures for PLLs, post-dividers, VCOs, and configuration values, plus exported operation tables and configuration functions.

## Important APIs, Types, And Functions
Important declarations include `clk_alpha_pll_regs`, `struct pll_vco`, `VCO()`, `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, and `struct alpha_pll_config`. Feature flags include `SUPPORTS_OFFLINE_REQ`, `SUPPORTS_FSM_MODE`, `SUPPORTS_DYNAMIC_UPDATE`, and `SUPPORTS_FSM_LEGACY_MODE`. The header exports many `clk_ops` variants and aliases compatible families with macros, such as Lucid using Trion fixed ops, Taycan using Lucid Evo ops, and Pongo/Rivian family aliases.

## Control Flow
SoC drivers instantiate `struct clk_alpha_pll`, choose a `regs` table entry, optional VCO table, feature flags, CCF init data, and optional `alpha_pll_config`. They either call a family-specific configure function directly or call `qcom_clk_alpha_pll_configure()` to dispatch based on the selected register table. CCF then enters the exported ops for enable, disable, recalc, determine, post-divide, and rate changes.

## State And Persistence
The header describes software metadata rather than runtime storage. Persistent fields in descriptors determine which hardware registers are touched, how VCO validation is applied, and whether updates can happen under FSM or dynamic-update rules. Configuration structs persist as static SoC data and are treated as the source of boot-time PLL programming.

## Dependencies And Integration Points
Includes CCF provider APIs and `clk-regmap.h`. It is consumed by Qualcomm clock controller files across the tree, including `clk-cpu-8996.c`, `clk-cbf-8996.c`, and multiple generated CC drivers. Its declarations are tightly coupled to `clk-alpha-pll.c` and the common regmap clock wrapper.

## Risks And Edge Cases
Register layout selection is critical because offsets are family-specific but accessed through common macros. Alias macros simplify family reuse but can hide behavioral differences if a new PLL variant diverges. Callers must provide consistent `width`, `post_div_shift`, VCO ranges, and config masks or rate and enable operations will program invalid fields.

## Test Signals
Compile coverage from multiple SoC drivers, successful registration of all ops aliases, static descriptor sanity checks for register tables, and runtime smoke tests for each configured PLL family are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.c

## Purpose
Implements Qualcomm branch clock gates that enable, disable, and verify clock branches through regmap-controlled enable and halt/status registers. It provides CCF ops for older branch status formats, CBCR v2 status fields, always-on branches, simple regmap gates, prepare/unprepare gates, and branches associated with memory power gating.

## Important APIs, Types, And Functions
Exports `clk_branch_ops`, `clk_branch2_ops`, `clk_branch2_aon_ops`, `clk_branch_simple_ops`, `clk_branch2_prepare_ops`, and `clk_branch2_mem_ops`. Internal helpers include `clk_branch_in_hwcg_mode()`, `clk_branch_check_halt()`, `clk_branch2_check_halt()`, `clk_branch_wait()`, `clk_branch_toggle()`, and memory-aware enable/disable callbacks.

## Control Flow
Enable paths first set the regmap enable bit through `clk_enable_regmap()`, then wait for the halt/status bit unless the descriptor requests skip, fixed delay, voted-disable behavior, or hardware clock gating mode. Disable clears the enable bit and performs the corresponding status wait. Branch2 status checks examine `CBCR_CLK_OFF` and `CBCR_NOC_FSM_STATUS`. Memory branches assert a memory enable field, poll an ack register, then enable the branch; disable reverses the memory field and disables the branch.

## State And Persistence
Software state is static descriptor data. Persistent hardware state resides in enable bits, halt bits, CBCR status fields, optional hardware-gating registers, and optional memory enable/ack registers. No software cache is maintained, so CCF queries read hardware through regmap.

## Dependencies And Integration Points
Depends on `clk-regmap` helpers, Linux CCF, regmap, bitfield macros, and the descriptor definitions in `clk-branch.h`. SoC clock controller tables embed `struct clk_branch` or `struct clk_mem_branch` and select the exported ops.

## Risks And Edge Cases
Wrong halt polarity or halt_check type can cause false success, spurious timeout, or boot stalls. Hardware-gated mode skips halt polling, so misconfigured H/W CG fields can hide failures. Memory branches can fail before the actual branch is enabled if the ack bit does not assert. Voted clocks delay on disable because status may not reflect a single client.

## Test Signals
Useful tests cover branch enable/disable with both halt polarities, CBCR v2 FSM status, skip and delay modes, hardware clock gating skip, voted clocks, memory ack timeout injection, and prepare/unprepare users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.h

## Purpose
Declares Qualcomm branch gate descriptors, CBCR bit definitions, inline CBCR field helpers, exported branch ops, and container helpers. It is the static data contract for branch clocks used by Qualcomm clock controller drivers.

## Important APIs, Types, And Functions
Key types are `struct clk_branch` and `struct clk_mem_branch`. Halt modes include `BRANCH_HALT`, `BRANCH_HALT_ENABLE`, voted variants, `BRANCH_HALT_DELAY`, and `BRANCH_HALT_SKIP`. CBCR definitions include `CBCR_CLK_OFF`, `CBCR_NOC_FSM_STATUS`, memory force bits, wake/sleep fields, and `CBCR_CLOCK_ENABLE`. Inline helpers update force memory, wakeup, sleep, and enable fields.

## Control Flow
Clock controller data fills branch register addresses, bit numbers, halt policy, and the embedded `clk_regmap`. CCF calls the selected exported ops from `clk-branch.c`, which use the descriptor to toggle and poll hardware. Inline helpers are available to SoC-specific code that needs direct CBCR field programming.

## State And Persistence
No runtime state is owned by the header. Descriptor fields persist in static clock tables and determine how hardware state is interpreted. CBCR fields persist in MMIO registers and may affect memory retention and clock gating across consumer enable transitions.

## Dependencies And Integration Points
Includes CCF, bitfield helpers, and `clk-regmap.h`. It integrates with the larger Qualcomm common clock controller pattern where each branch is registered through `devm_clk_register_regmap()`.

## Risks And Edge Cases
The halt policy constants are compact numeric values with a voted bit overlay, so incorrect combinations can change polling semantics. Inline helpers take `struct clk_branch` by value; callers must pass descriptors with valid `halt_reg` and `regmap`.

## Test Signals
Static build coverage of CBCR helpers, runtime reads of `is_enabled`, and branch descriptors with all halt policies validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cbf-8996.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cbf-8996.c

## Purpose
Provides the MSM8996 CPU bus fabric (CBF) clock driver. It configures a Huayra APSS alpha PLL, a fixed post-divider, and a small mux used as the exported CBF clock. When interconnect support is enabled, it also registers the CBF clock as an interconnect-backed bandwidth provider.

## Important APIs, Types, And Functions
Important objects are `cbfpll_config`, `cbf_pll`, `cbf_pll_postdiv`, `cbf_mux_parent_data`, `struct clk_cbf_8996_mux`, and `cbf_mux`. CCF callbacks are `clk_cbf_8996_mux_get_parent()`, `clk_cbf_8996_mux_set_parent()`, and `clk_cbf_8996_mux_determine_rate()`. Platform lifecycle functions include `qcom_msm8996_cbf_probe()`, remove, init, and exit. Interconnect hooks are `qcom_msm8996_cbf_icc_register()` and remove/sync-state shims.

## Control Flow
Probe maps the MMIO resource, initializes regmap, temporarily selects GPLL0, programs always-on auto clock selection, configures the CBF PLL, enables auto clock selection, switches the mux to the primary PLL, adjusts post-divider behavior for MSM8996 Pro, registers the fixed factor clock and regmap clocks, installs a notifier, exports the mux as the OF clock provider, and optionally registers the interconnect clock provider. The notifier switches to PLL/2 before downward crossings below 600 MHz and reverts on abort.

## State And Persistence
Persistent hardware state is the CBF mux register, auto-clock-select bits, PLL registers, and post-divider selection. Static software descriptors are global because the driver only supports the matching platform instance. Interconnect provider state is stored in platform driver data when `CONFIG_INTERCONNECT` is enabled.

## Dependencies And Integration Points
Depends on alpha PLL ops, regmap clock registration, platform device APIs, DT compatible strings `qcom,msm8996-cbf` and `qcom,msm8996pro-cbf`, CCF notifiers, optional interconnect clock provider APIs, and `dt-bindings/interconnect/qcom,msm8996-cbf.h`.

## Risks And Edge Cases
CBF is marked critical and initialized at `postcore_initcall` because CPU fabric rate changes are early and safety-sensitive. Incorrect threshold handling can overclock the mux during PLL reprogramming. The Pro variant mutates global config/divider values after initial PLL configuration in probe, so ordering matters. Without interconnect support, the driver warns that CBF is fixed.

## Test Signals
Boot on MSM8996 and MSM8996 Pro, OF clock provider resolution, CBF rate changes across 600 MHz, notifier abort behavior, interconnect bandwidth requests changing CBF rate, and no CPU fabric hang during PLL changes are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cbf-8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cpu-8996.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cpu-8996.c

## Purpose
Implements the MSM8996 APCC CPU clock driver for power and performance Kryo clusters. Each cluster has a primary PLL, an alternate PLL, a secondary mux for PLL/2 operation, a primary mux for CPU selection, and ACD-related fixed factors used during normal high-rate operation and voltage-droop handling.

## Important APIs, Types, And Functions
Important static descriptors include primary and alternate PLL register tables, `hfpll_config`, `altpll_config`, primary and alternate `clk_alpha_pll` objects, postdiv and ACD fixed-factor clocks, `clk_regmap_mux` SMUXes, and `struct clk_cpu_8996_pmux` PMUXes. Main functions are `clk_cpu_8996_pmux_get_parent()`, `clk_cpu_8996_pmux_set_parent()`, `clk_cpu_8996_pmux_determine_rate()`, `qcom_cpu_clk_msm8996_register_clks()`, `qcom_cpu_clk_msm8996_acd_init()`, `cpu_clk_notifier_cb()`, and platform probe.

## Control Flow
Probe maps APCC registers, creates a two-clock onecell provider, and delegates clock registration. Registration parks both clusters on GPLL0, programs auto-clock selection, configures primary and alternate PLLs, enables auto-clock selection, initializes ACD registers through Kryo L2 indirect access, programs pulse-swallow/soft-start controls, switches clusters to the ACD path, registers fixed and regmap clocks, enables alternate PLLs, and installs PMUX notifiers. Rate determination chooses SMUX/PLL2 for 300-600 MHz and ACD/primary PLL above 600 MHz. Notifiers reinitialize ACD and manually switch to SMUX before downward crossings to prevent transient overclocking.

## State And Persistence
Hardware state persists in per-cluster PLL registers, mux registers, auto-clock-select fields, ACD L2 indirect registers, soft-start/pulse-swallow registers, and alternate PLL state. Software descriptors are global. A spinlock serializes ACD indirect register programming, and the current CPU MPIDR decides which cluster receives one ACD sideband write.

## Dependencies And Integration Points
Depends on alpha PLL ops, regmap mux helpers, platform/OF APIs, CCF notifiers, fixed-factor clocks, `soc/qcom/kryo-l2-accessors.h`, and ARM CPU ID access. The exported OF provider returns the power and performance PMUX clocks to cpufreq or OPP consumers.

## Risks And Edge Cases
CPU clocks are critical and cannot be gated. PMUX threshold logic must avoid rates below 300 MHz and avoid overclocking while the primary PLL is being reprogrammed. Alternate PLL enable failures are not checked in detail after `clk_prepare_enable()`. ACD init is architecture-specific and relies on indirect L2 accessors plus current cluster affinity. Global descriptors make multiple instances unsupported.

## Test Signals
Boot on MSM8996, cpufreq transitions below and above 600 MHz, abort notifier rollback, alternate PLL availability during primary PLL changes, ACD register programming on both clusters, onecell provider indices, and no CPU stalls during repeated rate changes are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-cpu-8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.c

## Purpose
Implements legacy Qualcomm HFPLL clock ops. It initializes integer-mode PLL parameters, handles enable/disable sequencing, clamps and programs integer L rates, selects a low/high VCO through a user register, and validates bootloader-enabled PLL state.

## Important APIs, Types, And Functions
Exports `clk_ops_hfpll`. Internal helpers include `__clk_hfpll_init_once()`, `__clk_hfpll_enable()`, `clk_hfpll_enable()`, `__clk_hfpll_disable()`, `clk_hfpll_disable()`, `clk_hfpll_determine_rate()`, `clk_hfpll_set_rate()`, `clk_hfpll_recalc_rate()`, `clk_hfpll_init()`, and `hfpll_is_enabled()`.

## Control Flow
Initialization writes config, M=0, N=1, optional user/VCO bits, optional L value, and droop values once. Enable clears bypass, waits, deasserts reset, polls lock status or delays, then enables output under the PLL spinlock. Set-rate disables the PLL if it is currently enabled, selects VCO based on rate, writes L, and re-enables if needed. Init detects a bootloader-enabled PLL and disables/reinitializes it if the lock bit is inconsistent.

## State And Persistence
`struct clk_hfpll` stores a const hardware data pointer, `init_done`, embedded `clk_regmap`, and a spinlock. Hardware state persists in mode, L/M/N, user, droop, config, and status registers. The software `init_done` flag prevents rewriting defaults on every enable.

## Dependencies And Integration Points
Depends on regmap, CCF, spinlocks, delay/poll helpers, and descriptor definitions from `clk-hfpll.h`. SoC drivers instantiate `clk_hfpll` objects with `hfpll_data` register maps and register them through the CCF.

## Risks And Edge Cases
Rate programming assumes integer multiples of the parent and no active downstream consumers. The lock poll condition treats status bits according to platform-provided polarity, so bad `lock_bit` data can cause false success or timeout. `__clk_is_enabled()` is used under the lock, reflecting CCF state rather than raw hardware users.

## Test Signals
Enable sequencing, bootloader-enabled locked and unlocked cases, VCO bit selection around `low_vco_max_rate`, min/max rate clamping, set-rate while enabled, and droop/config writes are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.h

## Purpose
Declares the descriptor contract for Qualcomm HFPLL clocks. The header separates immutable register metadata from the runtime clock wrapper used by `clk-hfpll.c`.

## Important APIs, Types, And Functions
`struct hfpll_data` lists mode, L/M/N, user, droop, config, status registers, lock bit, initial values, VCO mask, low-VCO maximum rate, and min/max rates. `struct clk_hfpll` stores a descriptor pointer, init flag, embedded `clk_regmap`, and spinlock. It exports `clk_ops_hfpll` and `to_clk_hfpll()`.

## Control Flow
SoC code fills an `hfpll_data` instance, embeds a `clk_hfpll`, and registers it with `clk_ops_hfpll`. Runtime behavior is implemented by the C file, which reads descriptor fields to initialize, enable, disable, recalc, and set rates.

## State And Persistence
The header defines both static descriptor state and runtime `init_done`/lock state. Hardware persistence is represented by the register addresses and initial values in `hfpll_data`.

## Dependencies And Integration Points
Includes CCF provider APIs, spinlocks, and `clk-regmap.h`. It integrates with regmap-backed Qualcomm clock controllers needing legacy HFPLL support.

## Risks And Edge Cases
All semantics depend on accurate register addresses and initial values. Missing optional fields are represented as zero, so zero can only be used for optional registers when that is not a valid target on the platform.

## Test Signals
Build coverage for descriptors, correct container conversion, and runtime tests through `clk_ops_hfpll` validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.c

## Purpose
Implements Krait CPU/L2 clock mux and divider ops using ARM L2 indirect registers. It supports parent switching for primary/secondary muxes and a divider that is commonly used as divide-by-2 in Krait clock trees.

## Important APIs, Types, And Functions
Exports `krait_mux_clk_ops` and `krait_div2_clk_ops`. Key helpers are `__krait_mux_set_sel()`, `krait_mux_set_parent()`, `krait_mux_get_parent()`, `krait_div2_determine_rate()`, `krait_div2_set_rate()`, and `krait_div2_recalc_rate()`. A global `krait_clock_reg_lock` serializes indirect register access.

## Control Flow
Mux set-parent converts the CCF parent index to a hardware value, caches it in `en_mask`, and only writes hardware if the clock is enabled. The write path optionally disables secondary source clock gating for APQ/IPQ8064 errata, updates primary and low-power fields, restores gating, delays for switch completion, and releases the lock. Divider set-rate clears divider bits under the same lock; determine-rate asks the parent for twice the requested rate and reports half of the rounded parent.

## State And Persistence
State persists in Krait L2 indirect registers and descriptor fields such as `en_mask`, `reparent`, `safe_sel`, and `old_index`. The global lock protects shared primary/secondary mux register updates. No regmap is used; this is CPU coprocessor style register access.

## Dependencies And Integration Points
Depends on `asm/krait-l2-accessors.h`, CCF mux helpers, spinlocks, delays, and descriptor definitions in `clk-krait.h`. Krait CPU clock drivers use these ops for safe parent switching and PLL/divider composition.

## Risks And Edge Cases
Writing mux registers while a CPU clock is off is avoided because it may not work. Parent map errors produce wrong hardware selections. Low-power (`lpl`) mode duplicates fields at an offset, so descriptor shifts/masks must be correct. Errata handling must wrap the switch exactly for affected hardware.

## Test Signals
Parent switch while enabled and disabled, low-power field mirroring, errata gating toggle, divider recalc for raw divider values, and concurrent mux/divider operations are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.h

## Purpose
Declares descriptor types and exported ops for Krait mux and divide-by-2 clocks backed by L2 indirect registers.

## Important APIs, Types, And Functions
`struct krait_mux_clk` carries parent mapping, indirect register offset, mask, shift, cached enable selection, low-power flag, safe/old parent state, reparent flag, errata flag, `clk_hw`, and notifier block. `struct krait_div2_clk` carries offset, width, shift, low-power flag, and `clk_hw`. The header exports `krait_mux_clk_ops`, `krait_div2_clk_ops`, and container helpers.

## Control Flow
Krait clock controller code embeds these structures, configures CCF init data on the contained `clk_hw`, and registers them with the exported ops. Runtime code in `clk-krait.c` performs all indirect register operations.

## State And Persistence
Static descriptor fields define how the indirect register is interpreted. Runtime fields such as `en_mask` and `reparent` persist parent-switch decisions across CCF callbacks and notifiers.

## Dependencies And Integration Points
Includes only CCF provider APIs. The implementation depends on Krait L2 accessors and is used by Krait CPU clock setup code.

## Risks And Edge Cases
The descriptor exposes several coordination fields (`safe_sel`, `old_index`, `clk_nb`) that external notifier code may rely on; inconsistent updates can desynchronize software parent state from hardware.

## Test Signals
Compile coverage with Krait CPU clock drivers and runtime parent/divider transitions verify the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.c

## Purpose
Implements older Qualcomm PLL clock operations using L/M/N/config/mode/status registers. It supports direct PLL clocks, vote clocks that enable a parent PLL through an enable bit, SR configuration helpers, and an SR2 variant with explicit status polling.

## Important APIs, Types, And Functions
Exports `clk_pll_ops`, `clk_pll_vote_ops`, `clk_pll_sr2_ops`, `clk_pll_configure_sr()`, and `clk_pll_configure_sr_hpm_lp()`. Internal helpers include `clk_pll_enable()`, `clk_pll_disable()`, `clk_pll_recalc_rate()`, `find_freq()`, `clk_pll_determine_rate()`, `clk_pll_set_rate()`, `wait_for_pll()`, `clk_pll_vote_enable()`, `clk_pll_configure()`, `clk_pll_sr2_enable()`, and `clk_pll_sr2_set_rate()`.

## Control Flow
Direct enable skips already-enabled or FSM-mode PLLs, clears bypass, delays, deasserts reset, waits a fixed lock delay, and enables output. Set-rate looks up a frequency table entry, disables if currently enabled, writes L/M/N/config fields, and re-enables. Vote clocks call the generic regmap enable helper on the vote clock and then poll the parent PLL status. SR helpers configure fields and optionally enable FSM mode with different mode-register offsets. SR2 enable polls a status bit instead of fixed delay.

## State And Persistence
Hardware registers persist mode, L/M/N, config, status, and optional post-divider fields. Software state is descriptor-only: `struct clk_pll` points to register addresses, status bit, post-divider parameters, and a frequency table.

## Dependencies And Integration Points
Depends on CCF, regmap, delay helpers, qcom common helpers, and `clk-regmap`. SoC-specific clock drivers use `clk_pll_configure_sr*()` during probe and register PLLs or votes with the exported ops.

## Risks And Edge Cases
Frequency changes are limited to table entries. Direct enable uses a fixed 50 us delay and may miss lock failures unless using SR2/status paths. Vote enable assumes its parent is the actual `clk_pll` object. FSM mode is deliberately skipped by direct enable/disable, so descriptors must align with hardware ownership.

## Test Signals
Frequency table lookup, recalc with and without fractional M/N and post-divider, direct enable/disable, SR/SR2 status polling, vote enable timeout, and FSM-mode skip behavior are useful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.h

## Purpose
Defines the legacy Qualcomm PLL descriptor contract for `clk-pll.c` and SoC clock controller tables.

## Important APIs, Types, And Functions
`struct pll_freq_tbl` maps requested frequency to L/M/N/internal config bits. `struct clk_pll` stores L/M/N/config/mode/status registers, status bit, optional post-divider field, frequency table, and embedded `clk_regmap`. `struct pll_config` stores boot-time VCO, pre/post divider, M/N enable, and output masks. The header declares PLL ops and SR configuration helpers.

## Control Flow
SoC code fills `clk_pll` and optional `pll_config`, configures the hardware during probe, and registers the clock with one of the exported ops. Runtime behavior is implemented by `clk-pll.c`.

## State And Persistence
The header describes static software descriptors plus frequency/config tables. Hardware persistence is represented by the register addresses; no mutable software cache is exposed.

## Dependencies And Integration Points
Includes CCF and `clk-regmap.h`. It integrates with older Qualcomm CC drivers and common qcom PLL FSM setup helpers.

## Risks And Edge Cases
The frequency table is ceil-style and must be ordered. Register widths are fixed in the implementation, so descriptors must match hardware generation. Vote ops require parent-child topology to be correct.

## Test Signals
Build coverage, frequency-table ordering checks, and runtime PLL enable/rate tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.c

## Purpose
Implements first-generation Qualcomm root clock generator (RCG) ops. It supports parent muxing, pre-dividers, M/N:D counters, dynamic double-buffered RCGs, bypass clocks, pixel and escape clock special cases, and an LCC glitch-free mux behavior.

## Important APIs, Types, And Functions
Exports `clk_rcg_ops`, `clk_rcg_floor_ops`, `clk_rcg_bypass_ops`, `clk_rcg_bypass2_ops`, `clk_rcg_pixel_ops`, `clk_rcg_esc_ops`, `clk_rcg_lcc_ops`, and `clk_dyn_rcg_ops`. Core helpers translate fields between registers and descriptors: `ns_to_src()`, `src_to_ns()`, `md_to_m()`, `ns_to_pre_div()`, `mn_to_md()`, `ns_m_to_n()`, `mn_to_ns()`, `mn_to_reg()`, `configure_bank()`, `calc_rate()`, `__clk_rcg_set_rate()`, and dynamic RCG set-rate/parent helpers.

## Control Flow
Parent reads decode source select fields from NS registers; parent writes update source select fields. Rate recalc reads pre-divider, M/N, and mode fields and computes `parent / pre_div * m / n` when M/N is enabled. Determine-rate selects a frequency table entry and parent, optionally asking the parent to change rate. Set-rate programs M/N under reset, updates NS and optional enable-register mode bits, writes pre-divider and source, and releases reset. Dynamic RCGs program the inactive bank when enabled and flip the mux-select bit for glitch-free switching.

## State And Persistence
Hardware state resides in NS, MD, bank, and enable registers. Dynamic RCGs have two banks of NS/MD/pre-divider/source fields, with the active bank encoded by `mux_sel_bit`. Software descriptors persist register addresses, field widths, parent maps, and frequency tables.

## Dependencies And Integration Points
Depends on regmap, CCF, qcom parent/frequency helpers in `common.h`, and definitions from `clk-rcg.h`. SoC CC drivers instantiate these for older hardware generations; downstream branch gates usually consume RCG outputs.

## Risks And Edge Cases
M/N programming must assert and release reset in the correct register, which varies by descriptor. Dynamic RCGs require accurate bank descriptions or the wrong bank can be modified while live. Bypass2 and pixel/escape ops infer current parent from hardware, so invalid source fields return errors or default to parent zero. LCC clocks deliberately switch to XO while programming to avoid a stuck glitch-free mux.

## Test Signals
Recalc against known NS/MD values, set-rate with table and floor variants, dynamic bank switching while enabled and disabled, bypass and bypass2 parent behavior, pixel fraction selection, escape divider boundaries, and LCC enable/disable mux switching are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.h

## Purpose
Defines frequency-table and descriptor types for Qualcomm root clock generators, both legacy RCGs and second-generation CMD_RCGR-based RCG2 clocks.

## Important APIs, Types, And Functions
Macros `F()`, `C()`, `FM()`, and `FMS()` create frequency table entries. Types include `struct freq_tbl`, `struct freq_conf`, `struct freq_multi_tbl`, `struct mn`, `struct pre_div`, `struct src_sel`, `struct clk_rcg`, `struct clk_dyn_rcg`, `struct clk_rcg2`, `struct clk_rcg2_gfx3d`, and `struct clk_rcg_dfs_data`. The header declares exported ops for legacy RCGs, dynamic RCGs, RCG2 variants, display/byte/GPU/shared clocks, DP clocks, and `qcom_cc_register_rcg_dfs()`.

## Control Flow
SoC drivers define parent maps and frequency tables, embed one of the RCG descriptor structs, and register clocks with the matching ops. For DFS RCGs, drivers use `DEFINE_RCG_DFS()` entries and call `qcom_cc_register_rcg_dfs()` before registration so RCG2 DFS ops can replace normal ops when hardware DFS is enabled.

## State And Persistence
The header exposes descriptor state that maps software clock parents and rates to hardware register fields. Runtime persistence includes `clk_rcg2.parked_cfg` for shared RCGs and possibly allocated DFS frequency tables in the implementation.

## Dependencies And Integration Points
Includes CCF and `clk-regmap.h`. It integrates with `common.h` parent maps and frequency helpers, plus many Qualcomm SoC clock controllers.

## Risks And Edge Cases
Frequency table macros encode half-integer dividers as `(2 * h) - 1`; misuse creates wrong rates. Parent maps must match hardware source values. Shared RCGs depend on `safe_src_index` and `parked_cfg` semantics. DFS initialization mutates `clk_init_data` ops and flags.

## Test Signals
Compile coverage across SoC clock tables, table-driven rate selection, shared parked RCG behavior, and DFS registration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg2.c

## Purpose
Implements second-generation Qualcomm CMD_RCGR root clock generator ops. It handles parent selection, half-integer dividers, M/N:D counters, frequency-table and generated-rate selection, duty-cycle control, display/byte/GPU special clocks, shared parked RCGs, DFS-enabled serial-engine RCGs, and DisplayPort ratios.

## Important APIs, Types, And Functions
Exports `clk_rcg2_ops`, `clk_rcg2_gp_ops`, `clk_rcg2_floor_ops`, `clk_rcg2_fm_ops`, `clk_rcg2_mux_closest_ops`, `clk_edp_pixel_ops`, `clk_byte_ops`, `clk_byte2_ops`, `clk_pixel_ops`, `clk_gfx3d_ops`, `clk_rcg2_shared_ops`, `clk_rcg2_shared_floor_ops`, `clk_rcg2_shared_no_init_park_ops`, `qcom_cc_register_rcg_dfs()`, and `clk_dp_ops`. Key helpers include `update_config()`, `calc_rate()`, `_freq_tbl_determine_rate()`, `_freq_tbl_fm_determine_rate()`, `clk_rcg2_calc_mnd()`, `__clk_rcg2_configure_parent()`, `__clk_rcg2_configure_mnd()`, `clk_rcg2_configure()`, shared force-enable helpers, DFS table population, and DP/pixel fraction helpers.

## Control Flow
Normal RCG2 rate changes select a table entry, encode parent source, HID divider, M/N/D values, mode bits, and optional hardware-clock-control into CFG/M/N/D registers, then set CMD_UPDATE and poll until hardware clears it. GP ops synthesize M/N/HID values from parent and requested rates. Floor ops pick a floor table entry, FM ops choose among multiple equivalent configurations, and duty-cycle ops rewrite D while M/N mode is active. Display, byte, pixel, and DP ops derive fractional tables or rational approximations from the current parent. GFX3D rate changes ping-pong between PLL parents. Shared RCG ops park disabled clocks on a safe source and cache the intended CFG until re-enable.

## State And Persistence
Persistent hardware state includes CMD status/update bits, CFG source/divider/mode fields, M/N/D registers, shared force-enable bit, DFS perf-level tables, and display-specific fraction programming. Software state includes static descriptors plus `parked_cfg`, dynamically allocated DFS `freq_tbl`, and GFX3D helper parent arrays.

## Dependencies And Integration Points
Depends on regmap, CCF, rational approximation, GCD/math helpers, qcom parent/frequency helpers, and `clk-rcg.h`. It is a central utility for modern Qualcomm CC drivers and works with downstream branches, power domains, display PHYs, serial engines, and GPU clock trees.

## Risks And Edge Cases
`update_config()` timeouts indicate hardware did not accept new configuration. M/N and HID widths cap generated rates, and `clk_rcg2_calc_mnd()` may reduce scale or clamp to fit. Shared RCG parking is designed to avoid wedged GDSCs; wrong safe source indices can still wedge hardware. DFS table allocation is lazy and can fail. Display fraction tables accept only supported parent/rate combinations. GFX3D requires one fixed and two variable PLL parents or returns an error.

## Test Signals
Normal, floor, FM, and GP set-rate paths; duty-cycle set/get; update timeout injection; shared parking while disabled and re-enable restore; DFS registration and perf-level recalc; byte/pixel/eDP/DP rates; and GFX3D PLL ping-pong transitions are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.c

## Purpose
Provides a small regmap-backed divider clock implementation for Qualcomm clock controllers. It wraps generic CCF divider helpers around a register, shift, and width descriptor.

## Important APIs, Types, And Functions
Exports `clk_regmap_div_ops` and `clk_regmap_div_ro_ops`. Internal callbacks are `div_determine_rate()`, `div_ro_determine_rate()`, `div_set_rate()`, `div_recalc_rate()`, and the container helper `to_clk_regmap_div()`.

## Control Flow
Read/write ops fetch the raw divider field from `divider->reg`, shift and mask it, and pass it through generic CCF divider helpers with `CLK_DIVIDER_ROUND_CLOSEST`. Writable set-rate computes the raw divider value and updates the masked field. Read-only determine-rate uses the current raw value and does not program hardware.

## State And Persistence
No software cache is kept. Hardware register fields persist the divider selection, and descriptor fields define how to decode them.

## Dependencies And Integration Points
Depends on regmap, CCF divider helpers, and `clk-regmap-divider.h`. SoC drivers embed `struct clk_regmap_div` for simple dividers that share a regmap with other clocks.

## Risks And Edge Cases
Bad width or shift values can overwrite adjacent fields. The implementation assumes standard zero-based divider encoding accepted by generic helpers. Read errors are not surfaced by recalc beyond returning a computed value from an uninitialized local path only after regmap success is assumed.

## Test Signals
Divider determine/set/recalc for min, max, and rounded values plus read-only behavior validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.h

## Purpose
Declares the regmap divider descriptor used by `clk-regmap-divider.c`.

## Important APIs, Types, And Functions
`struct clk_regmap_div` stores register offset, shift, width, and embedded `clk_regmap`. The header exports writable and read-only divider ops.

## Control Flow
Clock controller data fills the descriptor and registers it with `clk_regmap_div_ops` or `clk_regmap_div_ro_ops`. Runtime operations are implemented in the C file.

## State And Persistence
Static descriptor state defines the hardware field. Actual divider state persists in the MMIO register.

## Dependencies And Integration Points
Includes CCF provider APIs and `clk-regmap.h`. It is used by Qualcomm SoC clock controller tables for compact divider definitions.

## Risks And Edge Cases
The descriptor has no parent map or custom table support, so callers needing nonstandard encodings must use another clock type.

## Test Signals
Build coverage and basic divider rate tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-divider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.c

## Purpose
Implements a combined regmap-backed mux and half-integer divider for Qualcomm RCG-like registers. It chooses a parent and divider together, updates CFG, triggers CMD update, and provides CCF rate/parent/recalc operations.

## Important APIs, Types, And Functions
Exports `clk_regmap_mux_div_ops` and `mux_div_set_src_div()`. Internal helpers include `mux_div_get_src_div()`, `is_better_rate()`, `mux_div_determine_rate()`, `__mux_div_set_rate_and_parent()`, `mux_div_get_parent()`, `mux_div_set_parent()`, `mux_div_set_rate()`, `mux_div_set_rate_and_parent()`, and `mux_div_recalc_rate()`.

## Control Flow
`mux_div_set_src_div()` writes source and HID divider fields into CFG and sets CMD update, polling up to 500 us for hardware to clear it. Determine-rate iterates parents and divider values, asks parents to round candidate rates, computes actual rate as `parent * 2 / div`, and selects the best rate at or above the request when possible. Set-rate and set-rate-and-parent recompute best source/divider and cache the chosen raw values after a successful hardware update. Recalc reads current source/divider and resolves the matching parent.

## State And Persistence
Hardware CFG/CMD fields persist the selected parent source and divider. Software caches `md->src` and `md->div` for subsequent parent-only or rate-only changes. Pending dirty configuration is detected and logged in get paths.

## Dependencies And Integration Points
Depends on regmap, CCF parent APIs, delays, and descriptor definitions in `clk-regmap-mux-div.h`. It is used by drivers that need a compact mux/divider not covered by full RCG2 descriptors.

## Risks And Edge Cases
The `src` parameter to `__mux_div_set_rate_and_parent()` is not used directly because the helper searches all parents; callers expecting forced parent selection may be surprised. If CMD dirty remains set, get operations log an error but continue with default output values. Bad parent maps make recalc and get-parent fall back to zero or return wrong rates.

## Test Signals
Best-rate selection across all parents/dividers, CMD update timeout, dirty CFG handling, parent map misses, cached src/div updates, and recalc from hardware fields are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.h

## Purpose
Declares the combined regmap mux/divider descriptor and exported operations.

## Important APIs, Types, And Functions
`struct clk_regmap_mux_div` stores register offset, HID divider field width/shift, source field width/shift, cached divider/source, parent map, embedded `clk_regmap`, optional input PLL pointer, and notifier block. It exports `clk_regmap_mux_div_ops` and `mux_div_set_src_div()`.

## Control Flow
Drivers fill the descriptor, define parent maps as raw hardware source values, and register it with the exported ops. Optional `pclk` and `clk_nb` are available for drivers coordinating parent PLL rate changes.

## State And Persistence
Descriptor fields persist the encoding. Runtime cached `div` and `src` mirror the last successful programming and influence rate-only or parent-only updates.

## Dependencies And Integration Points
Includes CCF and `clk-regmap.h`. It integrates with regmap-backed Qualcomm clock controllers.

## Risks And Edge Cases
The parent map is an array of raw `u32` values rather than `struct parent_map`, so callers must keep parent order and hardware encoding aligned manually.

## Test Signals
Compile coverage and runtime mux/divider rate transitions validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.c

## Purpose
Provides a simple regmap-backed mux clock with closest-rate parent selection. It decodes and writes source select fields in shared Qualcomm clock registers.

## Important APIs, Types, And Functions
Exports `clk_regmap_mux_closest_ops`. Internal callbacks are `mux_get_parent()`, `mux_set_parent()`, and `to_clk_regmap_mux()`.

## Control Flow
Get-parent reads the configured register field, applies shift and width mask, and either maps the raw value through `parent_map` or returns it directly. Set-parent maps the CCF parent index to raw hardware config when needed and updates the masked register field. Determine-rate is delegated to `__clk_mux_determine_rate_closest`.

## State And Persistence
No software cache is kept. Hardware stores the selected parent in the register field; descriptor fields define the bit layout and optional mapping.

## Dependencies And Integration Points
Depends on regmap, CCF mux helpers, `clk-regmap.h`, and `common.h` parent maps. It is used by MSM8996 SMUXes and many simple SoC muxes.

## Risks And Edge Cases
Incorrect parent maps silently produce wrong parent indices. The ops table always uses closest-rate selection, which may not be right for muxes needing exact or table-driven behavior.

## Test Signals
Parent get/set with and without parent maps, mask boundary values, and closest-rate parent selection are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.h

## Purpose
Declares the simple regmap mux descriptor used by `clk-regmap-mux.c`.

## Important APIs, Types, And Functions
`struct clk_regmap_mux` stores register, shift, width, optional `struct parent_map`, and embedded `clk_regmap`. The header exports `clk_regmap_mux_closest_ops`.

## Control Flow
Drivers instantiate the descriptor and register it with the exported ops. Runtime parent read/write behavior is implemented in the C file.

## State And Persistence
The descriptor maps CCF parent indices to hardware source fields. Hardware persists the selected source.

## Dependencies And Integration Points
Includes CCF, `clk-regmap.h`, and qcom `common.h`. It integrates with SoC clock tables that use `struct parent_map`.

## Risks And Edge Cases
The descriptor has no explicit lock, so serialization relies on regmap and higher-level clock framework locking.

## Test Signals
Build coverage and parent switching through CCF validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.c

## Purpose
Implements a tiny PHY pipe/symbol clock mux abstraction that models the PHY source as enabled and a reference/safe source as disabled. It lets PHY drivers switch a clock source around GDSC power transitions using normal CCF enable/disable calls.

## Important APIs, Types, And Functions
Exports `clk_regmap_phy_mux_ops`. Internal callbacks are `phy_mux_is_enabled()`, `phy_mux_enable()`, `phy_mux_disable()`, and `to_clk_regmap_phy_mux()`. Hardware values are `PHY_MUX_PHY_SRC` and `PHY_MUX_REF_SRC` under `PHY_MUX_MASK`.

## Control Flow
Enable writes the mux field to the PHY-provided source. Disable writes the reference source. Is-enabled reads the mux field, warns if it is neither expected value, and reports true only when the PHY source is selected.

## State And Persistence
No software cache is kept. The mux register persists whether the clock is sourced from the PHY or reference clock.

## Dependencies And Integration Points
Depends on regmap, CCF, bitfield helpers, and `clk-regmap-phy-mux.h`. It is intended for PHY pipe clocks and some UFS symbol clocks where clock source selection must track PHY/GDSC power sequencing.

## Risks And Edge Cases
Unexpected register values trigger a warning but still report disabled unless equal to the PHY value. The implementation assumes fixed two-bit encodings and is not a generic parent mux.

## Test Signals
PHY power-on/off sequences, GDSC transitions, UFS symbol clock use, and invalid raw mux value warnings are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.h

## Purpose
Declares the PHY mux descriptor and documents its CCF semantics for pipe and symbol clocks.

## Important APIs, Types, And Functions
`struct clk_regmap_phy_mux` stores the mux register and embedded `clk_regmap`. The header exports `clk_regmap_phy_mux_ops`.

## Control Flow
PHY or clock controller drivers instantiate the descriptor and register it. CCF enable selects the PHY source, disable parks the clock on the reference source, and is-enabled reflects that source choice.

## State And Persistence
Static descriptor state identifies the register. Hardware persists the selected source.

## Dependencies And Integration Points
Includes `clk-regmap.h`. The comment explains integration with PHY drivers and GDSC sequencing.

## Risks And Edge Cases
This is intentionally specialized; using it for a normal mux would invert expectations because disabled means reference source rather than no clock.

## Test Signals
Clock enable/disable around PHY/GDSC transitions validates the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-phy-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap.c

## Purpose
Provides common regmap-backed enable, disable, is-enabled, and registration helpers for Qualcomm clock types. It lets many clock implementations share the same `enable_reg`/`enable_mask` handling and regmap injection pattern.

## Important APIs, Types, And Functions
Exports `clk_is_enabled_regmap()`, `clk_enable_regmap()`, `clk_disable_regmap()`, and `devm_clk_register_regmap()`.

## Control Flow
`clk_is_enabled_regmap()` reads `enable_reg` and tests `enable_mask`, respecting inverted semantics. Enable and disable compute the correct masked value for normal or inverted bits and call `regmap_update_bits()`. Registration obtains a regmap from the device or its parent when available, stores it in the clock wrapper, and calls `devm_clk_hw_register()`.

## State And Persistence
The helper owns no global state. It mutates hardware enable bits and initializes the `clk_regmap.regmap` pointer during registration. Enable state persists in the underlying register.

## Dependencies And Integration Points
Depends on device-managed CCF registration, regmap, and the descriptor in `clk-regmap.h`. It is used by branch, PLL vote, RCG, mux, divider, and SoC-specific clock files.

## Risks And Edge Cases
If no regmap is found from the device or parent, registration still proceeds with the existing pointer, so callers must prepopulate it where needed. Inverted semantics must be set correctly or enable/disable behavior reverses. Disable ignores regmap update errors because CCF disable is void.

## Test Signals
Normal and inverted enable bits, device and parent regmap acquisition, registration without implicit regmap, and error propagation from read/enable are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap.h -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap.h

## Purpose
Defines the shared `clk_regmap` wrapper embedded by Qualcomm clock descriptors and declares the common helper APIs implemented by `clk-regmap.c`.

## Important APIs, Types, And Functions
`struct clk_regmap` contains `clk_hw`, a `struct regmap *`, enable register, enable mask, and inverted-enable flag. `to_clk_regmap()` converts a CCF `clk_hw` to the wrapper. Helper declarations cover is-enabled, enable, disable, and device-managed registration.

## Control Flow
Every regmap-backed clock embeds `clk_regmap`, sets CCF init data on `hw`, and registers via `devm_clk_register_regmap()` or a direct CCF registration path after setting `regmap`. Clock ops use `to_clk_regmap()` to reach hardware I/O.

## State And Persistence
The wrapper stores runtime regmap association and static enable-bit metadata. Hardware state persists in the configured enable register.

## Dependencies And Integration Points
Includes CCF provider APIs and forward-declares regmap. It is the common base for almost every file in this subset.

## Risks And Edge Cases
Container conversion assumes `clk_hw` is embedded exactly as the first field in `clk_regmap`; all derived structs rely on that layout. Missing or wrong regmap pointers break all regmap operations.

## Test Signals
Registration and simple enable/is-enabled calls through multiple derived clock types validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap.h -->

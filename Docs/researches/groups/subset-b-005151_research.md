# subset-b-005151 Research

Grouped research report for the requested PM domain source files. Each section is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/cpr.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/cpr.c

## Purpose
Qualcomm Core Power Reduction (CPR) generic PM domain driver for QCS404-style RB-CPR hardware. It exposes the CPR loop as a genpd provider, reads NVMEM fuse data, derives voltage/frequency corners from OPP data, and continuously trims the `vdd-apc` regulator around CPU OPP requests.

## Important APIs, Types, And Functions
- `struct cpr_drv` owns the genpd, MMIO base, regulator, CPU clock, TCSR regmap, IRQ state, fuse corners, runtime corners, current corner, and debugfs dentry.
- `struct cpr_desc`, `struct cpr_fuse`, `struct fuse_corner`, and `struct corner` encode SoC CPR timing, fuse-derived ceilings/floors/quotients, and per-OPP runtime voltage state.
- Genpd entry points are `cpr_power_on()`, `cpr_power_off()`, `cpr_set_performance_state()`, and `cpr_pd_attach_dev()`.
- Hardware helpers include `cpr_config()`, `cpr_ctl_enable()`, `cpr_ctl_disable()`, `cpr_corner_restore()`, `cpr_scale_voltage()`, and `cpr_irq_handler()`.
- Fuse/OPP setup flows through `cpr_get_fuses()`, `cpr_populate_ring_osc_idx()`, `cpr_fuse_corner_init()`, `cpr_corner_init()`, and `cpr_find_initial_corner()`.

## Control Flow
`cpr_probe()` matches `qcom,qcs404-cpr`, maps CPR registers, resolves the `acc-syscon` TCSR regmap, obtains the `vdd-apc` regulator, reads CPR fuse revision and per-corner NVMEM cells, initializes fuse corner voltages/quotients, requests a threaded IRQ, initializes a powered-off genpd, registers it as a simple provider, and creates debugfs. Device attachment is deferred until a CPU attaches to the domain because OPP-derived frequencies are only available then. `cpr_pd_attach_dev()` captures the CPU clock, counts domain OPPs, builds virtual corners, configures CPR registers, finds the boot-time corner, and enables ACC register programming. Runtime OPP changes call `cpr_set_performance_state()`: it decides UP/DOWN/NO_CHANGE, disables the CPR loop while changing the regulator, applies ACC settings before or after voltage changes depending on direction, restores per-corner RB-CPR registers, and re-enables the loop. CPR IRQs read status, handle UP/DOWN/MIN/MAX/MID priority, adjust voltage by regulator linear steps within min/max limits, ack/nack hardware, and save corner register state.

## State And Persistence Behavior
State is in memory plus hardware registers. `drv->corner` and `corner->last_uV` track the active OPP voltage after hardware-driven trimming. Each corner stores saved CPR control and interrupt registers so switching corners preserves loop state. Fuse data and OPP tables are read during probe/attach but not persisted. Debugfs exposes live CPR register and voltage state under `qcom_cpr/debug_info`.

## Dependencies And Integration Points
Depends on generic PM domains, OPP required-opps, NVMEM cells named `cpr_ring_oscN`, `cpr_init_voltageN`, `cpr_quotientN`, `cpr_quotient_offsetN`, the `cpr_fuse_revision` cell, a `vdd-apc` regulator with linear steps, a CPU clock, platform IRQ, MMIO resource, and the TCSR syscon referenced by `acc-syscon`. Integrates with cpufreq/OPP via genpd performance states and with ACC/TCSR via regmap sequences.

## Risks
Fuse parsing and voltage interpolation are sensitive to DT/NVMEM naming, OPP fuse-level annotations, regulator step size, and required-opps links to CPU OPPs. `cpr_debug_info_show()` assumes `drv->corner` and `corner->fuse_corner` are valid, so debugfs reads before CPU attach would be risky if reachable. IRQ handling must not run while loop-disabled unless hardware is actually quiet; otherwise it returns `IRQ_NONE` after logging. Voltage changes are mutex-protected, but the hardware loop and IRQ timing make ordering of ack/nack and saved registers important.

## Test Signals
Useful signals are successful probe and provider registration, `driver initialized with N OPPs`, valid debugfs output, regulator voltage changes matching OPP transitions, CPR IRQ up/down activity without timeout or unsupported voltage errors, and DT validation for required NVMEM/OPP/regulator/syscon resources. Compile coverage should include `qcom,qcs404-cpr` and genpd performance state paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/cpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmhpd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmhpd.c

## Purpose
Qualcomm RPMh power-domain driver. It maps DT power-domain specifier indices to RPMh ARC resources, exposes them as generic PM domains, aggregates normal and active-only peer votes, and sends active/wake/sleep corner votes through RPMh.

## Important APIs, Types, And Functions
- `struct rpmhpd` is one RPMh domain: genpd, optional parent, optional active-only peer, current requested corner, current active vote, enable corner, command DB level mapping, resource name/address, enable flag, sync-state flag, and retention-skip flag.
- `struct rpmhpd_desc` maps a compatible string to an indexed array of `struct rpmhpd *` domains.
- Core functions are `rpmhpd_probe()`, `rpmhpd_update_level_mapping()`, `rpmhpd_power_on()`, `rpmhpd_power_off()`, `rpmhpd_set_performance_state()`, `rpmhpd_aggregate_corner()`, and `rpmhpd_sync_state()`.
- Static descriptor arrays cover many Qualcomm SoCs such as SDM845, SC7180, SM8xxx, X1E80100, and related automotive/platform parts.

## Control Flow
At `core_initcall`, the platform driver binds to a compatible in `rpmhpd_match_table`. `rpmhpd_probe()` allocates onecell data, looks up each resource address with `cmd_db_read_addr()`, verifies `CMD_DB_HW_ARC`, reads the auxiliary level map from command DB, initializes each genpd with power and performance callbacks, and wires parent/child subdomains. `rpmhpd_set_performance_state()` maps the requested abstract level to the first command-DB level not less than the request, clamps over-max requests to the last supported corner, and if the domain is enabled aggregates and sends the new vote. `rpmhpd_power_on()` votes at least `enable_corner`; `rpmhpd_power_off()` votes zero. `rpmhpd_aggregate_corner()` combines this domain and an active-only peer, sending `RPMH_ACTIVE_ONLY_STATE`, `RPMH_WAKE_ONLY_STATE`, and `RPMH_SLEEP_STATE` as needed. Before `sync_state`, it clamps votes to the highest corner to avoid prematurely reducing bootloader-required resources; `rpmhpd_sync_state()` later marks resources synced and resends real enabled/disabled votes.

## State And Persistence Behavior
Runtime state is per static `rpmhpd` object: requested `corner`, active aggregate vote, `enabled`, `enable_corner`, `level[]`, `level_count`, and `state_synced`. The static domain objects are reused according to compatible descriptors, so this driver assumes one matching controller instance for these global descriptors. RPMh itself persists/applies votes across active, wake, and sleep states.

## Dependencies And Integration Points
Depends on `soc/qcom/cmd-db` for ARC address and level mapping, `soc/qcom/rpmh` for synchronous/asynchronous TCS writes, generic PM domains, OPP/genpd performance states, and dt-bindings indices from `qcom-rpmpd.h` and `qcom,rpmhpd.h`. Integration with consumers is through `of_genpd_add_provider_onecell()` and required-opps or power-domain references.

## Risks
Command DB data quality is critical: missing addresses, wrong slave IDs, zero-padded level arrays, or level counts over `RPMH_ARC_MAX_LEVELS` fail probe. Active-only peer aggregation is subtle: normal and AO peers share active votes but only non-AO domains contribute sleep votes. Pre-sync max-corner clamping trades power for safety; broken `sync_state` ordering can leave resources over-voted. Static global domain objects can be unsafe for multiple controller instances.

## Test Signals
Probe should show no missing RPMh resource errors, command DB level maps should be non-empty, and genpd consumers should observe performance-state votes reflected in RPMh traces. Suspend/resume tests should verify wake/sleep votes for AO peers, and `sync_state` should reduce boot-time max votes only after consumers are bound.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmhpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmpd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmpd.c

## Purpose
Qualcomm legacy SMD RPM power-domain driver. It exposes RPM regulator/corner resources as generic PM domains, sends enable and corner/floor votes over SMD RPM, and supports many pre-RPMh Qualcomm SoCs.

## Important APIs, Types, And Functions
- `struct rpmpd` describes one SMD RPM-backed domain with genpd, parent, active-only peer, requested corner, enabled state, RPM resource type/id, maximum state, key (`KEY_CORNER`, `KEY_LEVEL`, `KEY_FLOOR_CORNER`, or `KEY_FLOOR_LEVEL`), and sync-state flag.
- `struct rpmpd_req` is the little-endian SMD RPM request payload.
- Core functions are `rpmpd_probe()`, `rpmpd_send_enable()`, `rpmpd_send_corner()`, `rpmpd_aggregate_corner()`, `rpmpd_power_on()`, `rpmpd_power_off()`, `rpmpd_set_performance()`, and `rpmpd_sync_state()`.
- Descriptor tables map compatible strings for MDM/MSM/SDM/QCS/QCM/SM parts to indexed domain arrays.

## Control Flow
`rpmpd_probe()` obtains the parent `qcom_smd_rpm` handle, selects the SoC descriptor, allocates onecell data, initializes each domain with genpd callbacks and `GENPD_FLAG_ACTIVE_WAKEUP`, assigns the descriptor max state, wires optional subdomains, and registers a onecell provider. Power-on sends an explicit `KEY_ENABLE` active-state request, marks the domain enabled, and sends the current corner if any. Power-off sends disable and clears `enabled`. Performance changes clamp the requested state to `max_state`, update `pd->corner`, and either defer aggregation for disabled normal domains or immediately send for enabled/floor-vote domains. Aggregation combines normal and AO peer active/sleep votes and sends active and sleep SMD RPM messages. Before genpd `sync_state`, unsynced domains vote their max state to avoid dropping boot constraints.

## State And Persistence Behavior
State is kept in static `rpmpd` descriptors: requested corner, enabled flag, max state, and sync-state flag. RPM maintains applied active/sleep votes outside the driver. Floor-corner/floor-level domains are special because performance updates are sent even while the genpd is not enabled.

## Dependencies And Integration Points
Depends on `linux/soc/qcom/smd-rpm.h`, a parent SMD RPM device, genpd onecell providers, and Qualcomm power dt-bindings. The compatible determines which resource type/id/key tuple is exposed to DT consumers.

## Risks
The comparison in `rpmpd_set_performance()` checks `pd->key` against `cpu_to_le32(KEY_FLOOR_*)` even though `pd->key` is assigned host-order constants; on little-endian this is harmless but it documents an endian-sensitive assumption. Peer aggregation and pre-sync max-state clamping must match legacy RPM firmware expectations. Missing array entries are warned but provider indices remain sparse, so DT bindings must align exactly.

## Test Signals
Probe should retrieve a valid parent RPM handle and register the onecell provider. Runtime tests should watch SMD RPM messages for `swen`, `corn`, `vfc`, `vfl`, or `vlvl` keys on power/performance changes. Suspend tests should verify sleep-state votes and `sync_state` de-clamping after all consumers bind.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/Kconfig

## Purpose
Kconfig menu for Renesas PM domain support. It declares family selectors for legacy R-Car, R-Car Gen4, and R-Mobile SYSC drivers, then exposes per-SoC boolean options that select the correct family implementation.

## Important APIs, Types, And Functions
This file defines `SYSC_RCAR`, `SYSC_RCAR_GEN4`, `SYSC_RMOBILE`, and per-SoC symbols such as `SYSC_R8A7742`, `SYSC_R8A7795`, `SYSC_R8A779A0`, `SYSC_R8A779H0`. There are no C APIs; the integration contract is through Kconfig symbols consumed by the Makefile and `#ifdef CONFIG_SYSC_*` match tables.

## Control Flow
During configuration, selecting a concrete SoC option pulls in either `SYSC_RCAR` or `SYSC_RCAR_GEN4`. The compiled framework then includes only the compatible entries and descriptor objects for enabled SoCs.

## State And Persistence Behavior
No runtime state. Persistent build state is the selected `.config` symbols.

## Dependencies And Integration Points
The menu is gated by `SOC_RENESAS`. Per-SoC options are visible under `COMPILE_TEST` prompts and select family drivers compiled by the Renesas Makefile.

## Risks
If a new SoC descriptor is added without a matching Kconfig symbol or family selection, its source will not build or its compatible will not be compiled into the framework. Incorrect family selection would bind the wrong register model.

## Test Signals
Kconfig tests should verify each `CONFIG_SYSC_*` builds its descriptor and selects the intended family object. `COMPILE_TEST` coverage is useful because most symbols are boolean and platform-specific.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/Makefile

## Purpose
Build map for Renesas PM domain objects. It connects `CONFIG_SYSC_*` symbols to individual SoC descriptor objects and to family framework drivers.

## Important APIs, Types, And Functions
No C symbols are defined here. The important contract is object inclusion: per-SoC files such as `r8a7795-sysc.o`, family drivers `rcar-sysc.o`, `rcar-gen4-sysc.o`, and `rmobile-sysc.o`.

## Control Flow
Kbuild includes each descriptor object when its SoC config is enabled, then includes the family driver chosen by `SYSC_RCAR`, `SYSC_RCAR_GEN4`, or `SYSC_RMOBILE`.

## State And Persistence Behavior
No runtime state. Build output reflects `.config` choices.

## Dependencies And Integration Points
Depends on Renesas Kconfig symbols and the header declarations consumed by family drivers. Descriptor object names must match exported `*_sysc_info` symbols referenced from `rcar-sysc.h` or `rcar-gen4-sysc.h`.

## Risks
Object/config mismatches cause link failures or missing compatible support. The `r8a779h0` line has spacing different from the rest but still valid Makefile syntax.

## Test Signals
All Renesas `CONFIG_SYSC_*=y` combinations should link. `make drivers/pmdomain/renesas/` under representative configs catches missing objects and stale symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7742-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7742-sysc.c

## Purpose
RZ/G1H/R8A7742 R-Car-style domain table covering always-on, CA15 SCU and four CA15 CPUs, CA7 SCU and four CA7 CPUs, plus RGX GPU. CPU entries are `PD_CPU_NOCR`, SCUs are `PD_SCU`, and all non-root areas parent to their cluster or always-on domain.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7742-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7743-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7743-sysc.c

## Purpose
RZ/G1M/R8A7743 table with always-on, CA15 SCU, two CA15 CPU domains, and SGX GPU. It is reused by RZ/G1N compatible handling in `rcar-sysc.c`.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7743-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7745-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7745-sysc.c

## Purpose
RZ/G1E/R8A7745 table with always-on, CA7 SCU, two CA7 CPU domains, and SGX GPU using R-Car Gen2 register offsets.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7745-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77470-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77470-sysc.c

## Purpose
RZ/G1C/R8A77470 table with always-on, CA7 SCU, two CA7 CPU domains, and SGX GPU.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77470-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774a1-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774a1-sysc.c

## Purpose
RZ/G2M/R8A774A1 table based on R-Car M3-W: CA57 and CA53 clusters/CPUs, A3VC/A2VC video domains, and chained 3DG-A/B GPU domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774a1-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774b1-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774b1-sysc.c

## Purpose
RZ/G2N/R8A774B1 table with CA57 cluster/CPUs, A3VC/A3VP/A2VC1, and 3DG-A/B. It configures SYSC external request masking via `extmask_offs = 0x2f8` and `BIT(0)`.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774b1-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774c0-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774c0-sysc.c

## Purpose
RZ/G2E/R8A774C0 table with CA53 cluster/CPUs, A3VC/A2VC1, and 3DG domains. It includes an ES1.0 SoC revision fixup that swaps 3DG-A/B hierarchy using `soc_device_match()`.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774c0-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774e1-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774e1-sysc.c

## Purpose
RZ/G2H/R8A774E1 table based on R-Car H3 with CA57 and CA53 clusters/CPUs, A3VP/A3VC/A2VC1, and five-level 3DG-A through 3DG-E chain, plus external request mask settings.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a774e1-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7779-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7779-sysc.c

## Purpose
R-Car H1/R8A7779 table with always-on, ARM1-ARM3 CPU domains using `PD_CPU_CR`, and SGX/VDP/IMP device domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7779-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7790-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7790-sysc.c

## Purpose
R-Car H2/R8A7790 table with CA15 and CA7 clusters/CPUs, SH-4A, RGX GPU, and IMP domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7790-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7791-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7791-sysc.c

## Purpose
R-Car M2-W/N table with CA15 SCU, two CA15 CPUs, SH-4A, and SGX. `rcar-sysc.c` also maps R8A7793 to this descriptor.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7791-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7792-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7792-sysc.c

## Purpose
R-Car V2H table with CA15 SCU, two CA15 CPUs, SGX, and IMP domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7792-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7794-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7794-sysc.c

## Purpose
R-Car E2 table with CA7 SCU, two CA7 CPUs, SH-4A, and SGX domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7794-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7795-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7795-sysc.c

## Purpose
R-Car H3 table with CA57 and CA53 clusters/CPUs, A3VP, CR7, A3VC/A2VC1, 3DG-A through E, and A3IR. It has an ES2.* quirk that clears `extmask_val` because the external mask register is missing on those revisions.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a7795-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77960-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77960-sysc.c

## Purpose
R-Car M3-W/R8A77960 table using the shared r8a7796 dt-binding IDs. It includes CA57 and CA53 CPU clusters, A3VC/A3VP, A2VC, 3DG, and external request mask configuration.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77960-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77961-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77961-sysc.c

## Purpose
R-Car M3-W+/R8A77961 table with CA57/CA53 CPU hierarchy and multimedia/GPU domains similar to M3-W+, with external request masking enabled.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77961-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77965-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77965-sysc.c

## Purpose
R-Car M3-N/R8A77965 table focused on CA57 CPUs plus A3VC/A3VP/A2VC1 and 3DG-A/B domains, with external request mask support.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77965-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77970-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77970-sysc.c

## Purpose
R-Car V3M/R8A77970 table with CA53 CPU cluster/CPUs, CR7, A3IR, A2IR0/1 and IMP domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77970-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77980-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77980-sysc.c

## Purpose
R-Car V3H/R8A77980 table with CA53 CPUs, CR7, A3IR/A2IR/A2SC, A3VIP/A2VIP, and A3VP/A3VC-style media domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77980-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77990-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77990-sysc.c

## Purpose
R-Car E3/R8A77990 table with CA53 CPUs, CR7, A3VC/A2VC1, 3DG-A/B, and external request mask support.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77990-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77995-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77995-sysc.c

## Purpose
R-Car D3/R8A77995 compact table with CR7, A3IR, A2IR0, and A2SC domains under always-on.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by legacy `rcar-sysc.c`. Its primary data structures are `struct rcar_sysc_area` and `struct rcar_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a77995-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779a0-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779a0-sysc.c

## Purpose
R-Car V3U/R8A779A0 Gen4 table using `struct rcar_gen4_sysc_area`; it describes always-on, A3/A2/A1 CPU hierarchy and many accelerator/media domains such as 3DG, VIP, ISP, IR, CNN, DSP, DP, CV, CN, and IMP.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by Gen4 `rcar-gen4-sysc.c`. Its primary data structures are `struct rcar_gen4_sysc_area` and `struct rcar_gen4_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779a0-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779f0-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779f0-sysc.c

## Purpose
R-Car S4-8/R8A779F0 Gen4 table with two A3E clusters, A2E child clusters, and A1 CPU-core domains marked `PD_CPU_NOCR`.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by Gen4 `rcar-gen4-sysc.c`. Its primary data structures are `struct rcar_gen4_sysc_area` and `struct rcar_gen4_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779f0-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779g0-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779g0-sysc.c

## Purpose
R-Car V4H/R8A779G0 Gen4 table with A3E/A2E/A1 CPU hierarchy plus 3DG, VIP, DUL, ISP, IR, CNN/DSP, IMP, PSC, DMA, and CV domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by Gen4 `rcar-gen4-sysc.c`. Its primary data structures are `struct rcar_gen4_sysc_area` and `struct rcar_gen4_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779g0-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779h0-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779h0-sysc.c

## Purpose
R-Car V4M/R8A779H0 Gen4 table with C4 root, A2/A1 CPU hierarchy, CR CPU-like domains, 3DG/VIP/DUL/ISP/CN/DSP/IMP/PSC/DMA/CV/IMR/VC/PCI/PCIPHY domains.

## Important APIs, Types, And Functions
The file exports one SoC descriptor consumed by Gen4 `rcar-gen4-sysc.c`. Its primary data structures are `struct rcar_gen4_sysc_area` and `struct rcar_gen4_sysc_info`. Domain entries name each PM area, assign the hardware domain identifier/register selector, define parent-child hierarchy, and mark CPU/SCU/always-on quirks with flags such as `PD_CPU_NOCR`, `PD_CPU_CR`, `PD_SCU`, or `PD_ALWAYS_ON`.

## Control Flow
There is no runtime algorithm except optional revision fixups where present. During early/postcore SYSC initialization, the family driver selects this descriptor from the OF match table, allocates a genpd per area, initializes controllability flags, powers up controllable domains that are initially off, registers the provider, and adds subdomains according to the `parent` fields.

## State And Persistence Behavior
Descriptor data is `__initconst` or `__initdata`, so it is initialization-only. Runtime state is created by the family driver as generic PM domain objects and SYSC MMIO state; this file does not persist state itself.

## Dependencies And Integration Points
Depends on the matching dt-binding header for power-domain IDs and on the family header. It integrates with Device Tree compatibles compiled in `rcar-sysc.c` or `rcar-gen4-sysc.c`, and consumers use the exported domain IDs through `power-domains` references.

## Risks
The main risk is data accuracy: wrong parent IDs, register offsets/PDR IDs, or flags can break suspend/resume, CPU cluster handling, or device power sequencing. Revision fixups are especially sensitive because they mutate init-time descriptor tables before genpd registration.

## Test Signals
Boot logs should show successful SYSC provider registration with all expected domains. Device runtime PM should toggle non-CPU domains, while CPU/SCU/no-control domains remain always-on. DT binding tests should verify domain IDs line up with the descriptor array and consumers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/r8a779h0-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.c

## Purpose
Renesas R-Car Gen4 SYSC framework driver. It consumes Gen4 descriptor tables, creates generic PM domains, performs PDR-based power sequencing, and registers a onecell provider for R8A779A0/F0/G0/H0 style controllers.

## Important APIs, Types, And Functions
- `struct rcar_gen4_sysc_pd` wraps genpd with a PDR number, flags, and name.
- `rcar_gen4_sysc_power()` serializes and performs the PDR power transition, including interrupt mask/clear and PDRESR retry handling.
- `rcar_gen4_sysc_pwr_on_off()` waits for SYSCSR not-busy and writes PDRONCR/PDROFFCR.
- `clear_irq_flags()` clears and verifies SYSCISCR bits.
- `rcar_gen4_sysc_pd_setup()` configures genpd flags and initial state.
- `rcar_gen4_sysc_pd_init()` matches OF, maps registers, creates domains/subdomains, and registers the provider.

## Control Flow
At postcore init, the driver finds the first matching Gen4 SYSC node, maps MMIO, allocates onecell data, and walks the SoC's `rcar_gen4_sysc_area` list. CPU/SCU/no-control areas become always-on; device domains get PM clock integration with CPG MSSR attach/detach hooks and active wakeup. If a controllable device domain is off at boot, the driver powers it on before genpd registration. Power transitions compute register and bit indices from the PDR ID, enable and mask the completion interrupt, clear stale flags, repeatedly submit a power request until PDRESR is clear, then wait for the completion bit and clear it again.

## State And Persistence Behavior
Global state is the MMIO base, spinlock, and onecell data. Each runtime domain stores PDR ID and flags. Descriptor arrays are init-time only. The spinlock serializes all PDR sequences because SYSC registers and interrupt bits are shared.

## Dependencies And Integration Points
Depends on Gen4 descriptor objects declared in `rcar-gen4-sysc.h`, Device Tree compatibles, generic PM domains, simple QoS governor, and Renesas CPG MSSR clock attach helpers. Consumers use onecell power-domain indices equal to PDR IDs.

## Risks
PDR IDs index both register blocks and onecell domains, so descriptor mistakes can touch the wrong hardware. IRQ clear polling must succeed or subsequent requests may falsely complete. Initial power-on of off domains can hide bootloader power-state assumptions but is required for genpd baseline.

## Test Signals
Boot tests should show provider registration and no `Can not clear IRQ flags` or timeout errors. Runtime PM should toggle non-CPU domains and retain CPU/SCU domains as always-on. DT binding checks should match PDR IDs to onecell indices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.h -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.h

## Purpose
Shared header for R-Car Gen4 SYSC descriptors and framework. It defines Gen4 domain flags, the compact PDR-based area descriptor, the SoC info container, and extern declarations for Gen4 SoC tables.

## Important APIs, Types, And Functions
Defines `PD_CPU`, `PD_SCU`, `PD_NO_CR`, `PD_CPU_NOCR`, `PD_ALWAYS_ON`, `struct rcar_gen4_sysc_area`, and `struct rcar_gen4_sysc_info`. No executable functions are present.

## Control Flow
Compile-time descriptor contract only. Gen4 SoC files populate arrays of `rcar_gen4_sysc_area`; `rcar-gen4-sysc.c` turns those arrays into genpd domains.

## State And Persistence Behavior
No runtime state. Data described by this header is init-time descriptor metadata.

## Dependencies And Integration Points
Depends on Linux types and the family framework. Externs must match objects in `r8a779a0/f0/g0/h0-sysc.c` and Makefile/Kconfig inclusion.

## Risks
Incorrect flag semantics affect all Gen4 SoC descriptors. Parent ID semantics differ from legacy channel/isr descriptors, so mixing headers would be a serious integration bug.

## Test Signals
All Gen4 descriptors should compile and link. Boot validation should confirm onecell indices match PDR IDs from dt-bindings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.c

## Purpose
Legacy Renesas R-Car/RZ SYSC framework driver. It consumes SoC descriptor tables, creates generic PM domains, performs SYSC register power-on/off sequencing, handles external request masking, and registers onecell providers for R-Car Gen1/2/3 style power areas.

## Important APIs, Types, And Functions
- `struct rcar_sysc_pd` is the runtime genpd plus channel offset/bit, interrupt bit, flags, and name.
- `struct rcar_pm_domains` stores the onecell provider and indexed genpd array.
- `rcar_sysc_power()` is the central register sequence; `rcar_sysc_pwr_on_off()` submits one power request after SYSCSR readiness.
- `rcar_sysc_pd_setup()` sets genpd flags, attach/detach hooks, initial power state, and callbacks.
- `rcar_sysc_pd_init()` maps the SYSC node, runs optional SoC init fixups, creates domains and subdomains; `rcar_sysc_pd_init_provider()` publishes the onecell provider.
- R8A7779 CPU helpers optionally export `rcar_sysc_power_down_cpu()` and `rcar_sysc_power_up_cpu()`.

## Control Flow
An early initcall finds a matching `renesas,*-sysc` node, selects the enabled SoC descriptor, runs `info->init()`, maps MMIO, captures optional external request mask settings, allocates onecell data, and iterates descriptor areas. Each area becomes an `rcar_sysc_pd`; CPU, SCU, and no-control domains are marked always-on, while device domains get `GENPD_FLAG_PM_CLK`, active wakeup, no-stay-on, and CPG MSTP/MSSR attach hooks. Controllable domains that are off at boot are powered on before genpd init. Parent fields add genpd subdomains. A later postcore initcall registers the provider once genpd infrastructure is ready.

## State And Persistence Behavior
Global state includes `rcar_sysc_base`, the spinlock, external mask offset/value, onecell data, and provider node. Runtime state is the allocated `rcar_sysc_pd` objects and hardware SYSC registers. Descriptor data is init-only. Power operations are serialized with `rcar_sysc_lock` because SMP CPU and I/O-device power paths can overlap.

## Dependencies And Integration Points
Depends on Device Tree compatible matching, SoC descriptor objects, Renesas CPG clock-domain attach helpers (`cpg_mstp_*` or `cpg_mssr_*`), generic PM domains, simple QoS governor, and Renesas public CPU power helpers for R8A7779. Consumers integrate via onecell `power-domains` indices.

## Risks
Power sequencing is MMIO timing-sensitive: SYSCSR readiness, PWRER retries, SYSCISR completion, and interrupt mask/clear ordering must be correct. Wrong `isr_bit` indexing can overwrite onecell entries or fail subdomain links. External request masking affects CPU/3DG domains and must be restored on every error path. Early init means allocation/mapping failures can leave partial setup.

## Test Signals
Boot should find exactly one matching SYSC, register a onecell provider, and add expected subdomains. Runtime PM tests should power-cycle non-always-on domains without PWRER/SYSCISR timeouts. CPU hotplug on R8A7779 should exercise exported CPU power helpers. Clock attach coverage should include both legacy MSTP and MSSR systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.h -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.h

## Purpose
Shared header for legacy R-Car/RZ SYSC descriptor files and `rcar-sysc.c`. It defines descriptor structures, domain flag semantics, and extern declarations for all legacy SoC `*_sysc_info` objects.

## Important APIs, Types, And Functions
Defines `PD_CPU`, `PD_SCU`, `PD_NO_CR`, `PD_OFF_DELAY`, aliases `PD_CPU_CR`, `PD_CPU_NOCR`, `PD_ALWAYS_ON`, `struct rcar_sysc_area`, and `struct rcar_sysc_info`. No functions are implemented.

## Control Flow
Compile-time only. Descriptor files populate `rcar_sysc_area` arrays; `rcar-sysc.c` uses the `rcar_sysc_info` objects selected by OF compatible and Kconfig.

## State And Persistence Behavior
No runtime state. It describes init-time data consumed by the framework.

## Dependencies And Integration Points
Depends on Linux integer types and `BIT()` availability through included kernel headers in users. It is the contract between per-SoC descriptor objects and the legacy SYSC framework.

## Risks
Flag macro changes affect every descriptor. Extern declarations must match object constness: `r8a7795_sysc_info` is non-const because revision fixups mutate it.

## Test Signals
All Renesas legacy descriptor files should compile with this header, and the framework should link all enabled externs. Static review should confirm new SoCs use the correct flags and parent/isr indexing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rmobile-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rmobile-sysc.c

## Purpose
Renesas R-Mobile SYSC power-domain framework. It discovers PM domain nodes under `renesas,sysc-rmobile`, creates recursive generic PM domains, handles simple SPDCR/SWUCR/PSTR power sequencing, and marks domains containing special hardware as always-on or console-protected.

## Important APIs, Types, And Functions
- `struct rmobile_pm_domain` wraps genpd with governor, optional suspend hook, MMIO base, and PSTR bit shift.
- Power functions are `rmobile_pd_power_down()`, `__rmobile_pd_power_up()`, and `rmobile_pd_power_up()`.
- Domain setup uses `get_special_pds()`, `add_special_pd()`, `pd_type()`, `rmobile_setup_pm_domain()`, `rmobile_init_pm_domain()`, and recursive `rmobile_add_pm_domains()`.
- `rmobile_init_pm_domains()` is the postcore entry point.

## Control Flow
At postcore init, the driver scans all `renesas,sysc-rmobile` nodes, maps the controller, locates the `pm-domains` child, scans CPU/console/debug/memory-controller consumers once, and recursively creates domains for child nodes. A child with no `reg` property is treated as a top-level always-on domain; otherwise `reg` gives the PSTR bit. Normal domains get CPG MSTP PM-clock attach hooks, active wakeup, no-stay-on, and are powered up during initialization. Parent recursion adds subdomains and registers each child node as a simple provider.

## State And Persistence Behavior
Per-domain state is dynamically allocated and retained for genpd lifetime. `special_pds` is initdata used only to classify domains. Hardware state is in SPDCR/SWUCR/PSTR. Console domains can veto suspend via `rmobile_pd_suspend_console()` when console suspend is disabled.

## Dependencies And Integration Points
Depends on Device Tree hierarchy, CPG MSTP clock attach helpers, generic PM domains, PM clock support, OF console pointer, and special compatible matches for debug/memory controller devices. Consumers bind through per-domain simple providers.

## Risks
Recursive provider creation can leak partially allocated domains on failure because init code does not unwind. Special-domain classification depends on consumer `power-domains` phandles being present and matching exactly. Poll timeouts use small retry windows; hardware delays outside assumptions could fail power transitions.

## Test Signals
Boot should create providers for all PM domain child nodes and classify CPU/console/debug/memctl domains correctly. Runtime PM should power-cycle normal domains and retain console/CPU/debug/memory-controller domains. Console suspend tests should verify `no_console_suspend` prevents console domain power-off.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rmobile-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Kconfig

## Purpose
Kconfig entry for Rockchip generic power-domain support.

## Important APIs, Types, And Functions
Defines `ROCKCHIP_PM_DOMAINS`, a boolean option defaulting to `ARCH_ROCKCHIP`, depending on PM, ARM SMCCC discovery, and regulator support, and selecting `PM_GENERIC_DOMAINS`.

## Control Flow
Configuration enables compilation of `pm-domains.o` through the Rockchip Makefile.

## State And Persistence Behavior
No runtime state; it only affects kernel configuration.

## Dependencies And Integration Points
The dependency on `HAVE_ARM_SMCCC_DISCOVERY` matches the driver path that informs firmware of power-domain state through SMCCC when available. Regulator dependency supports domains with optional supplies.

## Risks
Disabling this option removes power-domain providers for Rockchip SoCs, likely breaking devices with `power-domains` references. Missing dependencies would cause compile or runtime integration failures.

## Test Signals
Build with `ARCH_ROCKCHIP=y` and `COMPILE_TEST=y` should select or expose this symbol and compile `pm-domains.o`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Makefile

## Purpose
Kbuild mapping for the Rockchip power-domain driver.

## Important APIs, Types, And Functions
Maps `CONFIG_ROCKCHIP_PM_DOMAINS` to `pm-domains.o`.

## Control Flow
Kbuild includes the driver object when the Kconfig symbol is enabled.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the Rockchip Kconfig symbol and source file name staying aligned.

## Risks
A stale object mapping would silently drop the platform provider from builds.

## Test Signals
`make drivers/pmdomain/rockchip/` under `CONFIG_ROCKCHIP_PM_DOMAINS=y` should produce `pm-domains.o`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/pm-domains.c

## Purpose
Rockchip generic PM domain provider. It supports many Rockchip PMU register layouts, creates genpd domains from static SoC tables and DT child nodes, controls power/idle/request bits, saves and restores NoC QoS registers, handles optional domain regulators, and coordinates with DRAM DVFS firmware paths.

## Important APIs, Types, And Functions
- `struct rockchip_domain_info` describes per-domain masks, offsets, wakeup behavior, regulator needs, memory/repair status, and clock ungate masks.
- `struct rockchip_pmu_info` describes per-SoC PMU register offsets, transition timings, and domain table.
- `struct rockchip_pm_domain` is the runtime genpd wrapper with QoS regmaps, clocks, DT node, and optional regulator.
- `struct rockchip_pmu` owns the PMU regmap, mutex, onecell data, and domain pointers.
- Public coordination APIs `rockchip_pmu_block()` and `rockchip_pmu_unblock()` let the DMC path block PMU transitions and keep clocks enabled during firmware operations.
- Core transition functions include `rockchip_pd_power()`, `rockchip_pmu_set_idle_request()`, `rockchip_do_pmu_set_power_domain()`, `rockchip_pmu_domain_mem_reset()`, `rockchip_pmu_save_qos()`, and `rockchip_pmu_restore_qos()`.
- Probe/setup functions include `rockchip_pm_domain_probe()`, domain registration helpers, and the postcore platform driver registration.

## Control Flow
The driver registers at postcore and matches one of many `rockchip,*-power-controller` compatibles. Probe gets the PMU syscon/regmap and SoC table, allocates a PMU object with onecell domain pointers, then creates runtime domains by matching DT child node names to static `rockchip_domain_info` entries. Each domain records clocks, QoS regmaps, optional regulator requirement, genpd callbacks, active-wakeup flags, and initial powered state. Power-on first enables a required regulator, then under the PMU mutex enables domain clocks, optionally ungates clocks in PMU, writes power bits, performs memory reset for domains with memory status, waits for status, informs firmware through SMCCC if supported, deasserts idle, restores QoS, gates helper clocks, and disables helper clocks. Power-off saves QoS, asserts idle, powers down, gates helper clocks, disables helper clocks, and then disables the regulator. DMC blocking takes a separate mutex, grabs the PMU mutex, enables all domain clocks, and keeps PMU idle registers untouched until unblock.

## State And Persistence Behavior
Runtime state is per PMU and per domain: onecell domain array, saved QoS register snapshots, lazily acquired regulator pointer, clock bulk data, and global `dmc_pmu`. Hardware state spans PMU power/status/idle/ack/memory/repair registers, firmware suspend configuration, and optional QoS syscons. The driver intentionally suppresses bind attributes because power domains cannot be removed while consumers may hold references.

## Dependencies And Integration Points
Depends on generic PM domains, PM clocks, OF child nodes, syscon/regmap PMU access, Rockchip dt-binding power IDs, optional regulators named `domain`, QoS syscon phandles, bulk clocks, ARM SMCCC discovery, and Rockchip SIP suspend-mode calls. It integrates with the DMC driver through exported block/unblock symbols and with consumers via onecell genpd providers.

## Risks
The state machine is mask/offset heavy; wrong SoC table data can write the wrong PMU bits. Idle-request ack polling and power-status polling have fixed 10 ms windows. QoS save/restore assumes configured regmaps are valid and stable. DMC block/unblock must be balanced or the PMU mutex and clocks remain held. Lazy regulator acquisition inside power-on can make first transition fail at runtime if DT supplies are missing.

## Test Signals
Boot should register domains matching DT child names without duplicate/missing warnings. Runtime PM should show successful power-on/off with no ack/status timeout logs. Suspend/DRAM DVFS tests should exercise `rockchip_pmu_block()`/`unblock()` and confirm clocks are held. QoS-sensitive display/video/network domains should retain QoS settings after power cycles. Build tests should cover newer tables such as RK3576/RK3588 and older idle-only domains.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/pm-domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Kconfig

## Purpose
Kconfig gate for Samsung Exynos generic PM domain support.

## Important APIs, Types, And Functions
Defines `EXYNOS_PM_DOMAINS`, visible for compile testing, depending on either Exynos architecture with generic PM domains or `COMPILE_TEST`.

## Control Flow
When enabled, Kbuild compiles `exynos-pm-domains.o`.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Gated by `SOC_SAMSUNG`; integrates with the Samsung Makefile and Exynos DT power-domain nodes.

## Risks
Missing `PM_GENERIC_DOMAINS` would make the runtime driver unusable, hence the dependency.

## Test Signals
Compile with Exynos configs and COMPILE_TEST should expose and build the driver.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Makefile

## Purpose
Kbuild mapping for Samsung Exynos PM domains.

## Important APIs, Types, And Functions
Maps `CONFIG_EXYNOS_PM_DOMAINS` to `exynos-pm-domains.o`.

## Control Flow
Kbuild includes the Exynos driver when the symbol is enabled.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the Kconfig symbol and source object name.

## Risks
Incorrect mapping would omit the provider from Exynos builds.

## Test Signals
A Samsung/Exynos build with the config enabled should compile this object.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/exynos-pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/exynos-pm-domains.c

## Purpose
Samsung Exynos generic PM domain driver. It creates one genpd per DT power-domain node, toggles the local power control register, waits for status, optionally links parent/child domains, and registers a simple provider.

## Important APIs, Types, And Functions
- `struct exynos_pm_domain_config` carries the `local_pwr_cfg` bit pattern for control/status.
- `struct exynos_pm_domain` stores MMIO base, genpd, and config bits.
- `exynos_pd_power()`, `exynos_pd_power_on()`, and `exynos_pd_power_off()` implement register toggling.
- `exynos_pd_probe()` maps the node, initializes genpd, registers provider, and adds an optional subdomain link.

## Control Flow
The core-init driver binds to `samsung,exynos4210-pd` or `samsung,exynos5433-pd`, allocates a domain, names it from `label` or node basename, maps registers, installs callbacks, optionally powers off Exynos4210 ARM domains at boot to reset splash-screen handoff state, reads status to choose the initial off flag, initializes genpd, registers the node as a simple provider, and if the node references a parent power domain, adds this node as a subdomain.

## State And Persistence Behavior
Per-domain runtime state is the MMIO base and local power bit mask. Hardware status at `base + 0x4` determines initial genpd state. The driver enables runtime PM on the platform device but does not implement remove/unwind.

## Dependencies And Integration Points
Depends on DT nodes with register resources, optional `label`, optional parent `power-domains`, generic PM domains, and Exynos-compatible control/status layout. Consumers reference each node as a power-domain provider.

## Risks
The polling loop has a fixed roughly 1 ms timeout. `of_iomap()` mapping is not devm-managed, and provider/subdomain failures are only partially unwound. Parent phandle parsing after provider registration means partial success can leave the child provider registered even if subdomain linking fails.

## Test Signals
Boot should register each Exynos PD node, optional subdomain log should show correct parent/child relation, and power toggles should complete without `enable/disable failed` timeout logs. Splash-screen reset behavior on Exynos4210 ARM configs should be validated.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/exynos-pm-domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/st/Kconfig

## Purpose
Kconfig option for ST-Ericsson ux500 power-domain support.

## Important APIs, Types, And Functions
Defines `UX500_PM_DOMAIN`, defaulting to `ARCH_U8500` and buildable with `COMPILE_TEST`.

## Control Flow
Enables `ste-ux500-pm-domain.o` through the ST Makefile.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the U8500 architecture or compile-test mode and integrates with DT compatible `stericsson,ux500-pm-domains`.

## Risks
The option is simple and lacks explicit `PM_GENERIC_DOMAINS` dependency; platform configs must ensure genpd support is available.

## Test Signals
U8500 and COMPILE_TEST builds should compile the driver.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/st/Makefile

## Purpose
Kbuild mapping for ux500 PM domain support.

## Important APIs, Types, And Functions
Maps `CONFIG_UX500_PM_DOMAIN` to `ste-ux500-pm-domain.o`.

## Control Flow
Kbuild includes the driver when configured.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the ST Kconfig symbol.

## Risks
A stale mapping would remove ux500 provider support.

## Test Signals
Compile with `CONFIG_UX500_PM_DOMAIN=y`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/ste-ux500-pm-domain.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/st/ste-ux500-pm-domain.c

## Purpose
Minimal ST-Ericsson ux500 genpd provider exposing the VAPE power domain.

## Important APIs, Types, And Functions
Defines no-op `pd_power_on()` and `pd_power_off()`, static `ux500_pm_domain_vape`, onecell array `ux500_pm_domains`, and probe/init functions `ux500_pm_domains_probe()` and `ux500_pm_domains_init()`.

## Control Flow
At `arch_initcall`, the platform driver binds to `stericsson,ux500-pm-domains`. Probe allocates onecell data, points it at the static VAPE domain array, initializes each domain, and registers the onecell provider.

## State And Persistence Behavior
State is static domain storage plus allocated onecell data. Power callbacks are placeholders returning success, so actual register context save/restore is expected in consumer runtime PM paths and regulator gating is not implemented here.

## Dependencies And Integration Points
Depends on ux500 DT bindings for `DOMAIN_VAPE` and `NR_DOMAINS`, generic PM domains, and a matching DT provider node.

## Risks
The callbacks do not gate hardware, so this provider mainly models dependency ordering. The probe does not check `of_genpd_add_provider_onecell()` return value and does not handle null entries in the array beyond the single VAPE domain assumption.

## Test Signals
Boot should register the VAPE provider and consumers should attach by onecell index. Functional power saving requires platform-specific regulator/runtime PM work outside this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/ste-ux500-pm-domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Kconfig

## Purpose
Kconfig option for StarFive JH71XX PMU power-domain support.

## Important APIs, Types, And Functions
Defines `JH71XX_PMU`, defaulting to `ARCH_STARFIVE`, depending on PM and selecting `PM_GENERIC_DOMAINS`.

## Control Flow
Enables compilation of `jh71xx-pmu.o`.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
The symbol is available for StarFive platforms or compile testing and supports DT compatibles handled by the PMU driver.

## Risks
Disabling it prevents JH7110 PMU providers from binding, breaking devices with PMU power-domain references.

## Test Signals
StarFive and COMPILE_TEST builds should compile the driver and select generic PM domains.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Makefile

## Purpose
Kbuild mapping for the StarFive JH71XX PMU driver.

## Important APIs, Types, And Functions
Maps `CONFIG_JH71XX_PMU` to `jh71xx-pmu.o`.

## Control Flow
Kbuild includes the PMU driver when configured.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the StarFive Kconfig symbol.

## Risks
Incorrect mapping would drop JH71XX PMU support from builds.

## Test Signals
Compile with `CONFIG_JH71XX_PMU=y`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/jh71xx-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/jh71xx-pmu.c

## Purpose
StarFive JH71XX PMU generic power-domain driver. It supports both the main JH7110 PMU with software-encourage sequencing and the always-on syscon-style PMU switch for DPHY domains.

## Important APIs, Types, And Functions
- `struct jh71xx_domain_info` describes domain name, genpd flags, and status bit.
- `struct jh71xx_pmu_match_data` selects domain table, status register, optional IRQ parser, and state setter.
- `struct jh71xx_pmu` owns device, match data, MMIO base, onecell data, IRQ, and spinlock.
- `struct jh71xx_pmu_dev` wraps a domain descriptor and genpd.
- Core functions include `jh71xx_pmu_get_state()`, `jh7110_pmu_set_state()`, `jh7110_aon_pmu_set_state()`, `jh71xx_pmu_set_state()`, `jh71xx_pmu_on/off()`, `jh71xx_pmu_interrupt()`, `jh7110_pmu_parse_irq()`, `jh71xx_pmu_init_domain()`, and `jh71xx_pmu_probe()`.

## Control Flow
The builtin platform driver matches `starfive,jh7110-pmu` or `starfive,jh7110-aon-syscon`, maps registers, initializes the spinlock, optionally requests and enables PMU interrupts, allocates onecell domain storage, and initializes each domain from match data. Main PMU transitions write the turn-on or turn-off mask, then issue the three-step SW encourage command sequence and poll `CURR_POWER_MODE` until the bit reaches the requested state. AON PMU transitions directly set or clear the switch register under the spinlock. Each genpd is initialized as off if the current state bit is not set.

## State And Persistence Behavior
Per-controller state includes MMIO base, domain array, IRQ, and lock. Per-domain state is descriptor pointer and genpd. Hardware status registers are the source of truth for current power mode. Interrupt status is logged and cleared but does not drive genpd state transitions.

## Dependencies And Integration Points
Depends on StarFive dt-bindings for domain indices, platform MMIO resources, optional IRQ, generic PM domains, and DT compatibles. Consumers bind through the onecell provider.

## Risks
SW encourage sequencing is strict; wrong command order or missing lock could corrupt PMU state. Poll timeout is only 100 us, so slow hardware or clocking issues show as `-ETIMEDOUT`. The IRQ parser enables all interrupts except P-channel failure but returns success even if `devm_request_irq()` fails after logging, because it does not return `ret`; that may hide IRQ setup failures.

## Test Signals
Boot should register all JH7110 main and AON domains. Runtime PM should toggle GPU/VDEC/VOUT/ISP/VENC/DPHY domains and see status bits change within timeout. Interrupt tests should verify sequence-done and failure status are logged and cleared.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/jh71xx-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Kconfig

## Purpose
Kconfig menu for Allwinner/Sunxi power-domain drivers in this folder.

## Important APIs, Types, And Functions
Defines tristate symbols `SUN20I_PPU`, `SUN50I_H6_PRCM_PPU`, and `SUN55I_PCK600`, each depending on Sunxi or compile-test platforms and PM, and selecting generic PM domains.

## Control Flow
Enabled symbols select matching objects from the Sunxi Makefile.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Integrates with Allwinner platform configs and distinct DT compatibles for D1/V853/A523 PPU, H6/H616 PRCM PPU, and A523 PCK-600.

## Risks
The requested file batch only includes `sun20i-ppu.c`; the Makefile also builds H6 and PCK-600 drivers when configured. Missing PM_GENERIC_DOMAINS selection would break providers, so each option selects it.

## Test Signals
Sunxi and COMPILE_TEST builds should compile selected objects. DT systems using display/video engines should verify required domains are powered.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Makefile

## Purpose
Kbuild mapping for Allwinner/Sunxi power-domain drivers.

## Important APIs, Types, And Functions
Maps `SUN20I_PPU` to `sun20i-ppu.o`, `SUN50I_H6_PRCM_PPU` to `sun50i-h6-prcm-ppu.o`, and `SUN55I_PCK600` to `sun55i-pck600.o`.

## Control Flow
Kbuild includes each driver according to the selected tristate symbol.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on Sunxi Kconfig symbols and source object names.

## Risks
Because the folder has multiple providers, Makefile drift can make one Kconfig option appear functional while the object is not compiled.

## Test Signals
Build each symbol as built-in and module where allowed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun20i-ppu.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun20i-ppu.c

## Purpose
Allwinner D1/V853/A523 PPU power-domain driver. It exposes each fixed-size PPU register block as a generic PM domain and drives command/status registers to switch domains on and off.

## Important APIs, Types, And Functions
- `struct sun20i_ppu_desc` lists domain names and count for a compatible.
- `struct sun20i_ppu_pd` wraps genpd and per-domain MMIO base.
- `sun20i_ppu_pd_is_on()` reads `PD_STATUS_STATE`.
- `sun20i_ppu_pd_set_power()` waits for idle, writes `PD_COMMAND_REG`, waits for completion/state, and clears completion.
- `sun20i_ppu_probe()` maps resources, enables clock, deasserts reset, initializes domains, and registers onecell provider.

## Control Flow
Probe matches a descriptor, allocates domain objects and onecell data, maps the controller, enables the clock, deasserts reset, then iterates `num_domains`. Each domain's base is `base + PD_REGS_SIZE * i`, so domain register blocks are contiguous. Genpd is initialized with initial off-state determined from hardware; failures for individual domains warn and continue. Provider registration returns a warning on failure but the driver returns 0.

## State And Persistence Behavior
Runtime state is per-domain genpd plus MMIO base and the onecell provider. Hardware status bits are authoritative. Clock/reset are devm-managed and remain enabled/deasserted for the controller lifetime.

## Dependencies And Integration Points
Depends on platform MMIO, clock, exclusive reset, generic PM domains, bitfield helpers, and DT compatibles `allwinner,sun20i-d1-ppu`, `allwinner,sun8i-v853-ppu`, and `allwinner,sun55i-a523-ppu`. Consumers use onecell indices matching descriptor order.

## Risks
The driver assumes uniform `0x80` register spacing. Poll windows are 1 ms with 100 us intervals; slow transitions may fail. Provider registration failure is only warned, not returned, which can leave a bound driver with no usable provider. Continuing after per-domain init failures can create sparse onecell arrays.

## Test Signals
Boot should deassert reset and register expected domains (`CPU/VE/DSP`, `RISCV/NPU/VE`, or A523 names). Runtime PM should see command/status transitions complete and completion flags clear. DT tests should verify consumer indices match descriptor order.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun20i-ppu.c -->

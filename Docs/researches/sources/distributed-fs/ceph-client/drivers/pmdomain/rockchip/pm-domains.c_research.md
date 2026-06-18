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

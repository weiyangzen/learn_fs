# subset-b-005024 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/qcom_l3_pmu.c -->
## sources/distributed-fs/ceph-client/drivers/perf/qcom_l3_pmu.c

Purpose: Qualcomm L3 cache uncore PMU driver for ACPI-described L3 cache slices. Each slice is exposed as an independent perf PMU named from parent/child ACPI UIDs, with userspace expected to aggregate per-slice counts for socket-wide cache behavior.

Important APIs, types, and functions: `struct l3cache_pmu` embeds `struct pmu`, MMIO base, counter event slots, allocation bitmap, hotplug node, and active CPU mask. `struct l3cache_event_ops` abstracts standard 32-bit counters versus chained 64-bit "long counter" mode selected by config bit `L3_EVENT_LC_BIT`. Perf callbacks are `qcom_l3_cache__event_init`, `event_add`, `event_del`, `event_start`, `event_stop`, `event_read`, `pmu_enable`, and `pmu_disable`; sysfs exposes `format/event`, `format/lc`, named cache events, and `cpumask`.

Control flow: probe requires an ACPI companion, maps the register resource, resets the basic counter and perfmon blocks through `qcom_l3_cache__init`, requests the overflow IRQ, registers a CPU hotplug instance, and finally calls `perf_pmu_register`. Event init rejects sampling and task mode, validates groups do not span unrelated hardware PMUs, and pins `event->cpu` to the exported PMU CPU. Add allocates one counter or an adjacent pair via `bitmap_find_free_region`; start programs event type, counter, interrupt/gang mode, and enables hardware. IRQ handling reads and clears `L3_M_BC_OVSR`, then updates only events with overflow bits.

State and persistence: state is entirely runtime MMIO and in-memory perf state. `used_mask`, `events[]`, `prev_count`, and `count` persist only while events are active. Hotplug migrates perf context and updates `cpumask` when the chosen CPU goes offline. No disk state exists.

Dependencies and integration: depends on Linux perf, ACPI, platform devices, IRQs, CPU hotplug, and MMIO helpers. Integrates with perf tooling through PMU sysfs event/format groups and ACPI ID `QCOM8081`.

Risks: 64-bit mode requires adjacent even/odd counter allocation and uses the odd counter as an overflow counter; mistakes in bitmap order or event grouping would corrupt counts. 32-bit overflow depends on MSB-toggle IRQ behavior and prompt ISR updates. Probe registers hotplug before perf registration; failure cleanup relies on devm and lacks explicit hotplug removal in the error path. Test signals include ACPI probe, sysfs PMU presence, `perf stat -a -e l3cache_*/read-miss/`, long-counter config, overflow-heavy 32-bit runs, and CPU offline migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/qcom_l3_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu.c -->
## sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu.c

Purpose: shared RISC-V perf PMU framework used by concrete backends such as SBI PMU and legacy CSR-only PMU. It provides generic perf callback wiring, counter accounting, mmap user-page support, period programming, and CSR read helpers.

Important APIs, types, and functions: exported helpers include `arch_perf_update_userpage`, `riscv_pmu_ctr_read_csr`, `riscv_pmu_ctr_get_width_mask`, `riscv_pmu_event_update`, `riscv_pmu_stop`, `riscv_pmu_event_set_period`, `riscv_pmu_start`, and `riscv_pmu_alloc`. Backend callbacks live in `struct riscv_pmu` from `<linux/perf/riscv_pmu.h>`: `event_map`, `ctr_get_idx`, `ctr_get_width`, `ctr_read`, `ctr_start`, `ctr_stop`, `ctr_clear_idx`, `csr_index`, and optional map/unmap hooks.

Control flow: allocation creates the PMU and per-CPU `cpu_hw_events` arrays, then installs generic `struct pmu` callbacks. Event init rejects branch stack sampling, asks the backend to map perf attributes to hardware or firmware encoding, sets `hwc->idx = -1`, stores `event_base` and `config`, and initializes non-sampling periods to half the counter width. Add asks the backend for a counter index, records the event in per-CPU slots, and starts on demand. Start computes a conservative initial value and calls the backend `ctr_start`; stop calls `ctr_stop`, updates the software count, and marks perf state bits.

State and persistence: persistent runtime state is per-CPU event slots, `n_events`, optional snapshot address fields initialized for later SBI use, and perf `local64_t` counters. `arch_perf_update_userpage` publishes counter width, optional user-readable counter index, and sched-clock conversion parameters to mmap consumers.

Dependencies and integration: depends on core perf, RISC-V CSRs, sched clock, SMP/per-CPU state, and backend platform drivers. It is intentionally backend-neutral.

Risks: wrap handling depends on accurate backend counter width; bad widths cause deltas to undercount or overcount. User mmap counter access depends on backend flags and valid CSR index. `riscv_pmu_ctr_read_csr` has a whitelist switch for cycle/instret/HPM CSR ranges; invalid CSR values return `-EINVAL` as an unsigned long and log an error. Test signals include backend registration, `perf stat` hardware/cache/raw events, mmap reads when allowed, 32-bit high/low CSR paths, and sampling period behavior near wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_legacy.c -->
## sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_legacy.c

Purpose: fallback RISC-V PMU backend for systems without the SBI PMU extension. It exposes only the always-present architectural cycle and instruction-retired counters through the shared RISC-V perf framework.

Important APIs, types, and functions: `pmu_legacy_ctr_get_idx` maps `PERF_COUNT_HW_CPU_CYCLES` to CSR cycle index 0 and `PERF_COUNT_HW_INSTRUCTIONS` to instret index 2. `pmu_legacy_read_ctr` reads `CSR_CYCLE`/`CSR_INSTRET` and their high halves on 32-bit builds. `pmu_legacy_event_mapped` and `pmu_legacy_event_unmapped` toggle `PERF_EVENT_FLAG_USER_READ_CNT` for mmap user access. `riscv_pmu_legacy_skip_init` is called by the SBI backend to suppress fallback registration.

Control flow: late init registers a simple platform driver and synthetic platform device unless `pmu_init_done` has been set. Probe allocates a shared `struct riscv_pmu`, sets its parent, then `pmu_legacy_init` fills backend callbacks, counter mask, capabilities, and registers PMU name `cpu` with raw type. Start cannot program hardware; it snapshots the current CSR into `prev_count` so generic update can calculate deltas.

State and persistence: only `pmu_init_done` persists globally during boot. Runtime state lives in generic perf structures and per-CPU slots allocated by `riscv_pmu_alloc`. The hardware counters cannot be stopped or reset by this backend.

Dependencies and integration: depends on platform-device bootstrap, generic RISC-V PMU code, RISC-V CSR access, and perf core. It intentionally marks `PERF_PMU_CAP_NO_INTERRUPT` and `PERF_PMU_CAP_NO_EXCLUDE` because it lacks overflow interrupts and privilege filtering.

Risks: unsupported events return `-ENOENT`; sampling and filtering are not useful because counters are free-running and cannot be programmed. Counts are deltas from global architectural counters, not isolated per-event hardware programs. The file comments note the implementation is temporary and intended for removal. Test signals include boot without SBI PMU, exactly two accepted hardware events, no interrupt sampling, correct 32-bit high-half reads, and SBI systems skipping legacy registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_sbi.c -->
## sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_sbi.c

Purpose: full RISC-V perf backend using the SBI PMU extension. It maps Linux perf hardware/cache/raw events to SBI event IDs, allocates counters through firmware, supports firmware and hardware counters, optional overflow sampling, optional SBI v2 snapshot shared memory, user counter access policy, CPU PM notifiers, and vendor overflow CSR alternatives.

Important APIs, types, and functions: exported helpers are `riscv_pmu_get_event_info` and `riscv_pmu_get_hpm_info`. Event tables are `pmu_hw_event_map` and `pmu_cache_event_map`. Core backend hooks include `pmu_sbi_event_map`, `pmu_sbi_ctr_get_idx`, `pmu_sbi_ctr_start`, `pmu_sbi_ctr_stop`, `pmu_sbi_ctr_read`, `pmu_sbi_ctr_clear_idx`, `pmu_sbi_event_mapped`, and `pmu_sbi_event_unmapped`. Overflow is handled by `pmu_sbi_ovf_handler`; CPU lifecycle by `pmu_sbi_starting_cpu` and `pmu_sbi_dying_cpu`; sysctl policy by `perf_user_access`.

Control flow: device init checks SBI spec >= 0.3 and PMU extension, records v2/v3 availability, registers CPU hotplug state, registers a platform driver/device, and calls `riscv_pmu_legacy_skip_init`. Probe allocates the generic PMU, obtains counter count and `SBI_EXT_PMU_COUNTER_GET_INFO` metadata into `pmu_ctr_list`, tries to set up per-CPU overflow IRQs via SSCOFPMF or vendor equivalents, installs backend callbacks, registers CPU PM notifier and perf PMU, optionally enables snapshot shared memory, registers sysctl, adds hotplug instance, and schedules asynchronous standard-event validation. Event allocation calls `COUNTER_CFG_MATCH`, applies exclude and guest flags, and maintains per-CPU used bitmaps for hardware and firmware counters.

State and persistence: global state includes SBI version booleans, snapshot static key, `pmu_ctr_list`, global counter mask, IRQ metadata, and `sysctl_perf_user_access`. Per-CPU state includes event slots, used counter bitmaps, optional snapshot page physical/virtual address, saved counter values, and IRQ reference. No disk persistence exists.

Dependencies and integration: depends on SBI PMU ecall ABI, perf core, RISC-V interrupt domains, CPU hotplug, CPU PM, sysctl, sched clock, SSCOFPMF, T-Head erratum support, and Andes custom PMU alternatives.

Risks: correctness depends on firmware counter metadata, firmware event validation, and logical-to-hardware counter mapping. Snapshot code must preserve shared-memory values across batched stop/start. Overflow handling intentionally stops all hardware counters before reading overflow state; races here can lose samples. User-access policy changes update `SCOUNTEREN` on all CPUs and can race with mmap visibility if ordering regresses. Test signals include SBI version feature probing, standard event availability after workqueue flush, raw event bit validation for v2/v3, sampling overflow interrupts, snapshot fallback, CPU hotplug, CPU suspend/resume, and sysctl modes 0/1/2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/starfive_starlink_pmu.c -->
## sources/distributed-fs/ceph-client/drivers/perf/starfive_starlink_pmu.c

Purpose: StarFive StarLink uncore PMU driver for JH8100-style interconnect/cache performance counters. It exposes named StarLink events and a cycle counter as a perf PMU backed by MMIO counters and one overflow IRQ.

Important APIs, types, and functions: `struct starlink_pmu` embeds `struct pmu`, per-CPU `starlink_hw_events`, hotplug node, CPU PM notifier, MMIO base, cpumask, and IRQ. `struct starlink_hw_events` contains event slots and used bitmap for 64 possible counter indexes, with 16 programmable event counters and index 63 reserved for cycles. Perf callbacks include `starlink_pmu_event_init`, `add`, `del`, `start`, `stop`, `update`; IRQ and power paths are `starlink_pmu_handle_irq` and `starlink_pmu_pm_notify`.

Control flow: probe allocates the PMU and per-CPU state, maps resource 0, requests IRQ, registers CPU hotplug and CPU PM callbacks, fills `struct pmu`, and registers `starfive_starlink_pmu`. Event init rejects sampling, task attach, and CPU-less events, validates groups within the same hardware PMU, stores raw config, and pins the event to the PMU cpumask CPU. Add assigns the dedicated cycle counter or the first zero programmable bit. Start programs half-range period, writes event select for non-cycle events, enables the relevant interrupt bit, and turns on global counting. IRQ scans active events, checks overflow status bits, clears them, updates software counts, and reprograms periods.

State and persistence: runtime state is per-CPU event slots/bitmap, PMU cpumask, perf `prev_count` and `event->count`, and MMIO register state. CPU PM enter stops and updates active counters; exit restarts them.

Dependencies and integration: depends on OF compatible `starfive,jh8100-starlink-pmu`, platform MMIO, perf core, IRQ, CPU hotplug, optional CPU PM, and sysfs event/format/cpumask groups.

Risks: `find_first_zero_bit` returns `n_events` when full, not a negative error, so the `idx < 0` check cannot catch exhaustion; subsequent `set_bit(idx, used_mask)` at index 16 can allocate outside the intended 0-15 programmable range though still within the 64-bit bitmap. Cycle counter deletion clears bit 63 even though add never sets it. Global enable is stopped when stopping any event, which can affect concurrent counters. Test signals include event exhaustion, cycle plus programmable events together, overflow IRQ for bit 63 and low bits, CPU hotplug IRQ affinity, and CPU PM save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/starfive_starlink_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/thunderx2_pmu.c -->
## sources/distributed-fs/ceph-client/drivers/perf/thunderx2_pmu.c

Purpose: Cavium/Marvell ThunderX2 ACPI uncore PMU driver for socket-local L3C, DMC, and CCPI2 units. It exposes each discovered uncore block as a perf PMU with event aliases and cpumask pinning.

Important APIs, types, and functions: `struct tx2_uncore_pmu` holds PMU identity, node/CPU, MMIO base, active counter bitmap, event slots, hrtimer, attribute groups, and type-specific callbacks for counter base initialization, start, and stop. Discovery uses `get_tx2_pmu_type`, `tx2_uncore_pmu_init_dev`, and `tx2_uncore_pmu_add`. Perf callbacks are `tx2_uncore_event_init`, `add`, `del`, `start`, `stop`, `read`; periodic 32-bit maintenance is `tx2_hrtimer_callback`.

Control flow: module init registers a multi-instance CPU hotplug state and platform driver. Probe requires ACPI, sets NUMA node, and walks child ACPI devices one level below `CAV901C`, accepting `CAV901D` L3C, `CAV901F` DMC, and `CAV901E` CCPI2. Each PMU maps its `_CRS` MMIO resource, sets type-specific limits and sysfs groups, selects an online CPU from the same node, registers perf, adds hotplug instance, and joins a global list. Event init rejects sampling, task attach, CPU-less events, invalid event IDs, and overlarge groups. Add allocates counters and computes register bases; start programs event controls and starts an hrtimer for 32-bit L3C/DMC only.

State and persistence: runtime state is in `tx2_pmus`, per-PMU active counter bitmaps, event arrays, hrtimer state, selected CPU, and MMIO counters. L3C/DMC are 32-bit and use a 2-second hrtimer to sample before overflow; CCPI2 uses 64-bit reads without hrtimer. Counts are prorated for L3 tiles or DMC channels.

Dependencies and integration: depends on ACPI namespace/resources, perf, hrtimer, cpuhotplug, MMIO, and NUMA CPU masks.

Risks: no hardware overflow IRQ for L3C/DMC means high-rate events can still wrap between 2-second ticks. DMC data-transfer events are divided by four to convert 16-byte granularity to 64-byte units, so event semantics must match documentation. Hotplug can leave `cpu >= nr_cpu_ids` if no local CPU remains. Test signals include ACPI child discovery, sysfs PMUs `uncore_l3c_N`, `uncore_dmc_N`, `uncore_ccpi2_N`, group sizing, hrtimer count monotonicity, and node-local CPU migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/thunderx2_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/xgene_pmu.c -->
## sources/distributed-fs/ceph-client/drivers/perf/xgene_pmu.c

Purpose: AppliedMicro/APM X-Gene SoC PMU driver for multiple uncore blocks: L3C, IOB/IOB slow, MCB, and MC. It supports PCP PMU v1/v2 via OF or ACPI and v3 via ACPI, exposing each hardware block as its own perf PMU.

Important APIs, types, and functions: `struct xgene_pmu` owns the top-level PCP PMU interrupt registers, active masks, selected CPU, IRQ, lock, ops table, and per-type PMU lists. `struct xgene_pmu_dev` embeds each child `struct pmu`, counter bitmap, max period, attributes, and active event pointers. `struct xgene_pmu_ops` abstracts v1/v2 32-bit and v3 64-bit counter operations, interrupt masks, event type and agent-mask writes. Perf callbacks include `xgene_perf_event_init`, `add`, `del`, `start`, `stop`, `read`, `pmu_enable`, and `pmu_disable`.

Control flow: top-level probe installs CPU hotplug state, allocates and initializes `xgene_pmu`, chooses ops by firmware match data, maps PCP PMU registers, requests a no-thread unbalanced IRQ, probes active MCB/MC/L3C topology from CSW/MCB registers or syscon regmaps, registers hotplug instance, walks child PMU devices from ACPI or OF, and unmasks top-level interrupts. Child discovery maps each child resource, derives names and enable masks, filters inactive L3C/MCB/MC blocks, selects version-specific sysfs groups, initializes hardware counters, and registers perf. IRQ handling reads top-level interrupt status under raw spinlock, dispatches to matching child lists, stops child counters, reads and clears overflow flags, updates and reprograms active events, then restarts counters.

State and persistence: runtime state is child lists, active topology masks, counter assignment bitmaps, event pointer arrays, MMIO registers, selected CPU mask, and perf counts. No persistent storage exists. CPU offline migrates all child perf contexts and IRQ affinity to another online CPU.

Dependencies and integration: integrates with perf sysfs formats/events, OF compatibles `apm,xgene-pmu*`, ACPI IDs `APMC0D5B/5C/83` and child type IDs, platform resources, syscon regmaps, cpuhotplug, and IRQ handling.

Risks: topology detection fallback defaults to single MCB/MC if CSW probing fails, hiding hardware. v3 uses paired 32-bit reads for 64-bit counters and different event encodings; attr group mistakes would misprogram events. Group validation checks PMU identity but not total counter count until add time. Test signals include OF and ACPI discovery, each child PMU sysfs group, v1 single-counter behavior, v2/v3 four-counter allocation, overflow IRQ dispatch for all child types, agent-mask filtering on non-v3 IOB, and CPU hotplug migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/xgene_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/phy/Kconfig

Purpose: top-level Linux PHY subsystem Kconfig menu. It defines core PHY framework options, a few root-level PHY drivers, common-property KUnit support, and includes all vendor PHY submenus.

Important APIs, types, and functions: this is declarative Kconfig rather than C. Key symbols are `PHY_COMMON_PROPS`, `PHY_COMMON_PROPS_TEST`, `GENERIC_PHY`, `GENERIC_PHY_MIPI_DPHY`, and root drivers such as `PHY_AIROHA_PCIE`, `PHY_CAN_TRANSCEIVER`, `PHY_GOOGLE_USB`, `USB_LGM_PHY`, `PHY_LPC18XX_USB_OTG`, `PHY_NXP_PTN3222`, `PHY_PISTACHIO_USB`, `PHY_SNPS_EUSB2`, and `PHY_XGENE`.

Control flow: Kconfig evaluation presents `menu "PHY Subsystem"`, resolves dependencies such as `OF`, architecture gates, `USB_SUPPORT`, `RESET_CONTROLLER`, or `TYPEC`, applies `select GENERIC_PHY`/other support libraries, and recursively sources vendor files from `drivers/phy/allwinner/Kconfig` through `drivers/phy/xilinx/Kconfig`.

State and persistence: generated build configuration persists in `.config`; this file itself has no runtime state. Defaults such as `PHY_COMMON_PROPS_TEST default KUNIT_ALL_TESTS` influence test builds.

Dependencies and integration: integrates with kernel Kconfig, PHY core, DT binding helper code, USB, regulator, MFD/syscon, and numerous vendor directories. It is paired with `drivers/phy/Makefile`, where enabled symbols map to objects and subdirectories.

Risks: incorrect `select` entries can force incompatible support code into builds; missing `depends on` can break compile-test coverage or real architecture builds. Vendor submenu inclusion order affects menu organization but not runtime. Test signals include `olddefconfig`, `allyesconfig`, `allmodconfig`, architecture-specific builds, and KUnit execution for common PHY properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/Makefile -->
## sources/distributed-fs/ceph-client/drivers/phy/Makefile

Purpose: top-level build manifest for the Linux PHY subsystem. It maps Kconfig symbols to core PHY objects, root-level PHY drivers, and vendor subdirectories.

Important APIs, types, and functions: this is kbuild syntax, not C. Main object mappings include `phy-core.o`, `phy-core-mipi-dphy.o`, `phy-common-props.o`, `phy-common-props-test.o`, and root drivers such as `phy-airoha-pcie.o`, `phy-can-transceiver.o`, `phy-google-usb.o`, `phy-lgm-usb.o`, `phy-lpc18xx-usb-otg.o`, `phy-nxp-ptn3222.o`, `phy-pistachio-usb.o`, `phy-snps-eusb2.o`, and `phy-xgene.o`.

Control flow: kbuild evaluates `obj-$(CONFIG_...)` assignments and descends into vendor directories only when `CONFIG_GENERIC_PHY` is enabled. The backslash-continued vendor list covers Allwinner, Amlogic, Apple, Broadcom, Cadence, Qualcomm, Rockchip, TI, Xilinx, and others.

State and persistence: no runtime state. Build artifacts are generated by kbuild according to `.config`.

Dependencies and integration: tightly paired with `drivers/phy/Kconfig`. The broad vendor descent under `CONFIG_GENERIC_PHY` means individual vendor Makefiles decide their own object inclusion once the core framework is enabled.

Risks: adding a Kconfig symbol without a matching object line, or vice versa, creates silent non-builds or dead options. Gating all vendor directories on `GENERIC_PHY` assumes every vendor PHY depends on that framework. Test signals include `make drivers/phy/`, `modpost`, `allmodconfig`, and verifying enabled symbols produce expected `.o` or module files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/phy/allwinner/Kconfig

Purpose: Allwinner-specific PHY driver configuration menu for USB2, USB3, and MIPI D-PHY blocks.

Important APIs, types, and functions: declarative symbols are `PHY_SUN4I_USB`, `PHY_SUN6I_MIPI_DPHY`, `PHY_SUN9I_USB`, and `PHY_SUN50I_USB3`. They select core dependencies such as `GENERIC_PHY`, `USB_COMMON`, `GENERIC_PHY_MIPI_DPHY`, and `REGMAP_MMIO`.

Control flow: Kconfig exposes tristate options gated by `ARCH_SUNXI || COMPILE_TEST`, `HAS_IOMEM`, `RESET_CONTROLLER`, `USB_SUPPORT`, `EXTCON`, `POWER_SUPPLY`, `COMMON_CLK`, and `OF` as appropriate. The selected symbols drive object inclusion in the Allwinner Makefile.

State and persistence: only kernel configuration state in `.config`; no runtime behavior.

Dependencies and integration: integrates Allwinner SoC PHY drivers with generic PHY framework, USB common helpers, extcon/power-supply infrastructure for OTG detection, reset controller, regmap MMIO, and MIPI D-PHY helpers.

Risks: `PHY_SUN4I_USB` has broad dependencies because the driver supports OTG extcon and VBUS power-supply notification; missing any dependency breaks compile. MIPI D-PHY selection must include `GENERIC_PHY_MIPI_DPHY` or timing validation helpers are unavailable. Test signals include SUNXI defconfig coverage, compile-test builds, and module naming (`sun6i_mipi_dphy`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/Makefile -->
## sources/distributed-fs/ceph-client/drivers/phy/allwinner/Makefile

Purpose: kbuild object mapping for Allwinner PHY drivers.

Important APIs, types, and functions: maps `CONFIG_PHY_SUN4I_USB` to `phy-sun4i-usb.o`, `CONFIG_PHY_SUN6I_MIPI_DPHY` to `phy-sun6i-mipi-dphy.o`, `CONFIG_PHY_SUN9I_USB` to `phy-sun9i-usb.o`, and `CONFIG_PHY_SUN50I_USB3` to `phy-sun50i-usb3.o`.

Control flow: when the parent PHY Makefile descends into `allwinner/`, kbuild includes objects whose config symbols are `y` or `m`.

State and persistence: no runtime state; build output depends on `.config`.

Dependencies and integration: paired with `drivers/phy/allwinner/Kconfig`; integrates the four Allwinner source files into the kernel or modules.

Risks: the file is small, so main risk is symbol/object drift if drivers are renamed or new Kconfig entries are added without object mappings. Test signals include `make drivers/phy/allwinner/` and checking modules appear under expected names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun4i-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun4i-usb.c

Purpose: broad Allwinner sun4i/sun5i/sun6i/sun7i/sun8i/sun20i/sun50i USB2 PHY driver. It manages up to four PHYs, OTG ID/VBUS detection for PHY0, VBUS regulators, passby/PMU settings, SoC-specific calibration, and extcon reporting.

Important APIs, types, and functions: `struct sun4i_usb_phy_cfg` captures compatible-specific quirks such as PHYCTL offset, HSIC index, dual-route PHY0, SIDDQ placement, missing PHYs, and polling requirements. `struct sun4i_usb_phy_data` owns shared registers, extcon, GPIOs, power-supply notifier, delayed detection work, and per-PHY clocks/resets/regulators. PHY ops are `sun4i_usb_phy_init`, `exit`, `power_on`, `power_off`, and `set_mode`; exported helper `sun4i_usb_phy_set_squelch_detect` adjusts squelch bits.

Control flow: probe maps `phy_ctrl`, reads optional ID/VBUS GPIOs and power supply, creates and registers extcon, creates each non-missing PHY by acquiring reset, optional regulator, clocks, optional PMU resource, and registering the provider. It then requests GPIO IRQs or falls back to polling and registers a power-supply notifier. Init enables clocks, deasserts reset, handles PHY2 SIDDQ dependencies, programs calibration/tuning or base SIDDQ bits, enables passby, enables PHY0 pullups, and schedules detection. Detection work reads ID/VBUS, forces session-end transitions when needed, updates ISCR force bits, publishes extcon states, toggles passby and dual-route MUSB/EHCI routing, and reschedules polling when necessary.

State and persistence: runtime state includes regulator-on flags, PHY0 initialized flag, cached ID/VBUS values, force-session-end flag, delayed work, extcon state, and register programming. Nothing persists beyond driver lifetime.

Dependencies and integration: generic PHY, USB mode helpers, extcon, GPIO descriptors/IRQs, power supply, regulators, clocks, resets, workqueues, DT compatibles, and PMU MMIO resources.

Risks: OTG correctness depends on debouncing and prompt VBUS reporting within 100 ms. PHY0 route switching must match controller ownership. Multiple SoC quirks make regression risk high when adding compatibles. Cleanup manually cancels work and unregisters notifiers. Test signals include each compatible variant, regulator conflict with external VBUS, GPIO IRQ and polling modes, power-supply notification, PHY0 host/device/OTG mode changes, missing PHY phandle translation, suspend-like init/exit cycles, and squelch export users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun4i-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun50i-usb3.c -->
## sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun50i-usb3.c

Purpose: Allwinner H6 USB3 PHY driver for a single USB 2+3 host PHY combo. It performs clock/reset sequencing and writes vendor PHY tuning registers.

Important APIs, types, and functions: `struct sun50i_usb3_phy` stores the generic PHY, MMIO base, reset, and clock. `sun50i_usb3_phy_open` programs external VBUS, spread-spectrum/reference enables, PIPE clock, forced VBUS, and low/high PHY tune values. PHY ops are init and exit.

Control flow: probe gets the unnamed clock and reset, maps resource 0, creates a PHY with `sun50i_usb3_phy_ops`, stores driver data, and registers a simple OF PHY provider. Init enables the clock, deasserts reset, then calls `sun50i_usb3_phy_open`. Exit asserts reset and disables the clock.

State and persistence: state is only the current clock/reset state and MMIO programming. The BSP-derived tuning values are reapplied on every init.

Dependencies and integration: generic PHY, OF compatible `allwinner,sun50i-h6-usb3-phy`, platform MMIO, common clock framework, reset controller, and xHCI/DWC consumers through the PHY provider.

Risks: register magic values are undocumented BSP imports; changes need board-level signal validation. There is no regulator or runtime PM handling in this file. Init failure unwinds clock if reset deassert fails. Test signals include probe deferral for clock/reset, successful SuperSpeed link training, repeated init/exit cycles, and PHY provider phandle resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun50i-usb3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun6i-mipi-dphy.c -->
## sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun6i-mipi-dphy.c

Purpose: Allwinner MIPI D-PHY driver for A31-style and A100-style PHY blocks. It supports TX mode for display and RX mode only on variants that mark RX support.

Important APIs, types, and functions: `struct sun6i_dphy_variant` supplies variant analog TX power-on callback and RX capability. `struct sun6i_dphy` stores reset, module clock, regmap, generic PHY, MIPI D-PHY configuration, variant, and direction. PHY ops include `configure`, `power_on`, `power_off`, `init`, and `exit`. Timing validation uses `phy_mipi_dphy_config_validate`.

Control flow: probe maps MMIO through `devm_regmap_init_mmio_clk`, gets shared reset and `mod` clock, creates a PHY, defaults direction to TX, optionally switches to RX if DT property `allwinner,direction = "rx"` and variant supports it, then registers a simple provider. Init deasserts reset, enables the module clock, and exclusively sets it to 150 MHz. Configure validates and copies MIPI timing options. TX power-on programs digital timing registers, then calls variant-specific analog setup: A31 hardcodes analog lane masks, A100 computes PLL divider/N from `hs_clk_rate` and enables combo PHY bits. RX power-on programs BSP-derived receive timing from module clock and symbol rate, enables forced RX lanes, and enables global control. Power-off clears global and analog registers; exit releases exclusive clock rate, disables clock, and asserts reset.

State and persistence: runtime state is copied `phy_configure_opts_mipi_dphy`, selected direction, register state, reset and clock state. No disk persistence.

Dependencies and integration: generic PHY, generic MIPI D-PHY helpers, regmap MMIO, clock/reset, DT compatibles `allwinner,sun6i-a31-mipi-dphy` and `allwinner,sun50i-a100-mipi-dphy`, and display/camera consumers.

Risks: many timing and analog values are hardcoded or BSP-derived; invalid `hs_clk_rate` can cause divide behavior problems. A100 RX is unsupported by variant data. Exclusive clock rate must be released on exit. Test signals include DSI panel bring-up, RX rejection on unsupported variant, configure validation failures, power cycle register cleanup, and scope/link validation across lane counts and symbol rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun6i-mipi-dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun9i-usb.c -->
## sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun9i-usb.c

Purpose: Allwinner sun9i A80 USB PHY driver for individual USB2 host PHYs, including optional HSIC mode.

Important APIs, types, and functions: `struct sun9i_usb_phy` stores the generic PHY, PMU MMIO, reset, main clock, optional HSIC 12 MHz clock, and `enum usb_phy_interface` type. `sun9i_usb_phy_passby` toggles AHB burst, alignment, ULPI bypass, and HSIC-specific PMU bits. PHY ops are init and exit.

Control flow: probe reads PHY interface mode from DT. HSIC mode acquires `hsic_480M`, `hsic_12M`, and `hsic` reset; non-HSIC mode acquires `phy` clock and reset. It maps PMU resource 0, creates the PHY, stores driver data, and registers a simple provider. Init enables clocks, deasserts reset, and enables passby. Exit disables passby, asserts reset, and disables clocks.

State and persistence: runtime state is clock/reset state, PMU passby bits, and PHY type. No persistent storage.

Dependencies and integration: generic PHY, USB OF mode helper, clock/reset frameworks, platform MMIO, and compatible `allwinner,sun9i-a80-usb-phy`.

Risks: HSIC clock/reset names differ from regular PHY names, so DT binding errors lead to probe failure. `clk_disable_unprepare` is called on `hsic_clk` in exit even for non-HSIC mode; because the field is zeroed by `devm_kzalloc`, this relies on common clock helpers tolerating NULL. Test signals include regular and HSIC DT nodes, init failure unwinding at each clock/reset stage, and host controller enumeration after passby enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun9i-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/phy/amlogic/Kconfig

Purpose: Amlogic/Meson PHY driver configuration menu covering HDMI TX, USB2, USB3/PCIe combo, PCIe, and MIPI D-PHY analog/digital PHYs.

Important APIs, types, and functions: symbols are `PHY_MESON8_HDMI_TX`, `PHY_MESON8B_USB2`, `PHY_MESON_GXL_USB2`, `PHY_MESON_G12A_MIPI_DPHY_ANALOG`, `PHY_MESON_G12A_USB2`, `PHY_MESON_G12A_USB3_PCIE`, `PHY_MESON_AXG_PCIE`, `PHY_MESON_AXG_MIPI_PCIE_ANALOG`, and `PHY_MESON_AXG_MIPI_DPHY`.

Control flow: Kconfig gates most drivers on `OF && (ARCH_MESON || COMPILE_TEST)` and defaults many to `ARCH_MESON`. Symbols select needed infrastructure such as `GENERIC_PHY`, `REGMAP_MMIO`, `MFD_SYSCON`, `USB_COMMON`, and `GENERIC_PHY_MIPI_DPHY`. The paired Makefile maps enabled symbols to C objects.

State and persistence: configuration only; no runtime state.

Dependencies and integration: integrates Amlogic PHY drivers with generic PHY core, USB support, regmap MMIO, MFD syscon, and MIPI D-PHY helpers.

Risks: defaulting several symbols to `ARCH_MESON` increases build coverage but can pull drivers into platform configs unexpectedly. Analog and digital MIPI pieces require matching consumer/controller expectations. Test signals include Meson defconfigs, compile-test builds, dependency resolution for `REGMAP_MMIO`/`MFD_SYSCON`, and module/object generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/phy/amlogic/Makefile

Purpose: kbuild object mapping for Amlogic/Meson PHY drivers.

Important APIs, types, and functions: maps Meson Kconfig symbols to objects: `phy-meson8-hdmi-tx.o`, `phy-meson8b-usb2.o`, `phy-meson-gxl-usb2.o`, `phy-meson-g12a-usb2.o`, `phy-meson-g12a-usb3-pcie.o`, `phy-meson-g12a-mipi-dphy-analog.o`, `phy-meson-axg-pcie.o`, `phy-meson-axg-mipi-pcie-analog.o`, and `phy-meson-axg-mipi-dphy.o`.

Control flow: when the parent Makefile descends into `amlogic/`, kbuild includes each object based on its `CONFIG_PHY_*` value.

State and persistence: no runtime state; only build outputs according to `.config`.

Dependencies and integration: paired with `drivers/phy/amlogic/Kconfig` and the Meson source files in the same directory.

Risks: symbol/object drift is the main risk. Combo PHYs and analog/digital MIPI split drivers require all relevant objects to be selectable together through Kconfig. Test signals include `make drivers/phy/amlogic/`, `allmodconfig`, and ensuring selected options produce expected built-in or module artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/amlogic/Makefile -->

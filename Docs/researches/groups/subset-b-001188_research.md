# subset-b-001188 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynq/pll.c

Purpose: implements a Xilinx Zynq-7000 PLL as a Linux common clock framework provider backed by memory-mapped PLL control and status registers.

Important APIs/types/functions: `struct zynq_pll` stores `clk_hw`, control/status register bases, a shared spinlock, and the lock-bit index. `clk_register_zynq_pll()` allocates and registers the clock. `zynq_pll_determine_rate()`, `zynq_pll_recalc_rate()`, `zynq_pll_enable()`, `zynq_pll_disable()`, and `zynq_pll_is_enabled()` form the `clk_ops`.

Control flow: registration clears the bypass qualifier bit under the caller-supplied lock, then calls `clk_register()`. Rate selection clamps feedback divider values to 13..66. Enable clears reset/powerdown and busy-waits for the PLL lock status bit; disable asserts reset and powerdown.

State and persistence: state lives in SoC registers and in the allocated `struct zynq_pll`; there is no teardown path in this file. Register access is serialized with the shared spinlock.

Dependencies and integration points: depends on CCF, `linux/clk/zynq.h`, MMIO helpers, and the parent Zynq clock controller that supplies mapped registers and lock. Consumers interact through normal clk APIs.

Risks: the enable path spins indefinitely if firmware or hardware never asserts the lock bit. Nested calls take and release the same lock only around individual reads, so callers must preserve the expected locking context. `pr_info()` on enable/disable can be noisy. `parent_rate * fbdiv` may overflow `unsigned long` on unusual inputs.

Test signals: boot on Zynq hardware, clock tree inspection, PLL rate changes near min/max dividers, lock-bit failure injection, and suspend/resume or peripheral enable tests that exercise gate users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Kconfig

Purpose: declares the `COMMON_CLK_ZYNQMP` configuration symbol for Xilinx ZynqMP UltraScale+ clock controller support.

Important APIs/types/functions: this is Kconfig metadata, not C code. The symbol is a boolean prompt that depends on `ZYNQMP_FIRMWARE || COMPILE_TEST` and defaults to `ZYNQMP_FIRMWARE`.

Control flow: during kernel configuration, enabling this option makes ZynqMP firmware-backed clock support selectable when the PMU firmware interface is present or compile testing is requested.

State and persistence: no runtime state; the selected symbol becomes part of the kernel configuration and influences compilation.

Dependencies and integration points: integrates with platform firmware support through `ZYNQMP_FIRMWARE`; paired with the local Makefile and the CCF drivers in this directory.

Risks: the local Makefile builds objects using `CONFIG_ARCH_ZYNQMP`, not `CONFIG_COMMON_CLK_ZYNQMP`, so configuration wiring should be reviewed if clocks are expected under compile-test-only builds.

Test signals: `menuconfig` visibility, `allyesconfig`/`COMPILE_TEST` builds, and ZynqMP platform builds confirming the clock controller object set is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Makefile

Purpose: lists the object files that implement the ZynqMP clock controller.

Important APIs/types/functions: this build file adds `pll.o`, `clk-gate-zynqmp.o`, `divider.o`, `clk-mux-zynqmp.o`, and `clkc.o` when `CONFIG_ARCH_ZYNQMP` is enabled.

Control flow: Kbuild consumes the `obj-$(CONFIG_ARCH_ZYNQMP)` assignment and links the complete clock implementation into the kernel for ZynqMP architecture builds.

State and persistence: no runtime state; it persists build graph membership only.

Dependencies and integration points: integrates with arch selection and the C files that export `zynqmp_clk_register_*()` helpers and the platform driver.

Risks: it does not reference `CONFIG_COMMON_CLK_ZYNQMP`, so the Kconfig symbol in the same directory may not be the direct build switch. Any future object added to the directory must be included here or it will silently not build.

Test signals: `make drivers/clk/zynqmp/`, ZynqMP defconfig builds, and compile-test matrix checks for missing object references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-gate-zynqmp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-gate-zynqmp.c

Purpose: implements firmware-controlled gate clocks for ZynqMP and Versal clock topologies.

Important APIs/types/functions: `struct zynqmp_clk_gate` wraps `clk_hw`, firmware flags, and `clk_id`. `zynqmp_clk_register_gate()` allocates and registers the gate. `zynqmp_clk_gate_enable()`, `zynqmp_clk_gate_disable()`, and `zynqmp_clk_gate_is_enabled()` call PM firmware clock enable/disable/getstate APIs.

Control flow: the main clock controller discovers a topology node of type `TYPE_GATE` and calls this registration helper. Runtime CCF operations translate directly to `zynqmp_pm_clock_enable()`, `zynqmp_pm_clock_disable()`, and `zynqmp_pm_clock_getstate()`.

State and persistence: gate state is owned by platform firmware and hardware. The driver keeps only the `clk_id` and flags in heap memory for the life of the registered clock.

Dependencies and integration points: depends on CCF, `clk-zynqmp.h`, and `linux/firmware/xlnx-zynqmp.h` PM calls. Integrated by `clkc.c` through the topology function table.

Risks: `num_parents` passed to the helper is ignored and `init.num_parents` is hardcoded to 1. Firmware errors are mostly debug-logged; disable failures cannot propagate through the void CCF callback. The `flags` member is stored but not used.

Test signals: enable/disable/is_enabled operations on gate clocks, firmware error-path tracing, clock summary validation, and peripheral probe tests that require gate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-gate-zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-mux-zynqmp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-mux-zynqmp.c

Purpose: implements firmware-controlled parent selection for ZynqMP mux clock nodes.

Important APIs/types/functions: `struct zynqmp_clk_mux` carries `clk_hw`, mapped mux flags, and firmware `clk_id`. `zynqmp_clk_register_mux()` registers either writable or read-only mux operations. `zynqmp_clk_mux_get_parent()` and `zynqmp_clk_mux_set_parent()` call PM firmware.

Control flow: CCF asks for the active parent or requests a parent switch; the driver forwards the request to `zynqmp_pm_clock_getparent()` or `zynqmp_pm_clock_setparent()`. Rate determination uses `__clk_mux_determine_rate_closest`.

State and persistence: parent selection persists in firmware-controlled clock state. The Linux object stores the firmware clock id and decoded flags.

Dependencies and integration points: used by `clkc.c` for `TYPE_MUX` topology nodes. Depends on CCF mux semantics and the ZynqMP PM clock parent APIs.

Risks: the read-only check tests `nodes->type_flag & CLK_MUX_READ_ONLY`, while type flags are decoded from ZynqMP-specific constants; this relies on bit compatibility with the generic flag. On get-parent failure, returning `num_parents` intentionally forces an invalid index. The mapped `mux->flags` are stored but not supplied to a generic mux helper.

Test signals: parent enumeration, `clk_set_parent()` success/failure, read-only mux behavior, and firmware-returned invalid parent indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-mux-zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-zynqmp.h -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-zynqmp.h

Purpose: defines shared ZynqMP clock topology types, firmware flag bits, and registration prototypes used by all clock subdrivers.

Important APIs/types/functions: `enum topology_type`, `struct clock_topology`, common flag macros such as `ZYNQMP_CLK_SET_RATE_PARENT`, divider/mux type flags, `zynqmp_clk_map_common_ccf_flags()`, and `zynqmp_clk_register_pll/gate/divider/mux/fixed_factor()`.

Control flow: `clkc.c` fills `struct clock_topology` entries from firmware query responses and dispatches to the registration functions declared here.

State and persistence: no state; it is a compile-time contract between the topology parser and the individual clock implementations.

Dependencies and integration points: includes `linux/firmware/xlnx-zynqmp.h` for PM APIs and `linux/spinlock.h`; consumed only by the ZynqMP clock directory.

Risks: flag definitions must stay synchronized with firmware ABI encoding. Reusing names similar to generic CCF flags can hide bit-number mismatches. `MAX_NODES` and topology type enum assumptions in `clkc.c` depend on these definitions remaining stable.

Test signals: successful build of all ZynqMP clock objects, firmware topology parsing across PLL/divider/mux/gate/fixed-factor nodes, and ABI compatibility tests with PM firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-zynqmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clkc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clkc.c

Purpose: probes the ZynqMP/Versal firmware clock database and registers a one-cell CCF provider containing all valid output clocks.

Important APIs/types/functions: `struct zynqmp_clock`, `struct clock_parent`, firmware response structs, `zynqmp_pm_clock_get_num_clocks()`, `_get_name()`, `_get_topology()`, `_get_parents()`, `_get_attributes()`, `zynqmp_clk_map_common_ccf_flags()`, `zynqmp_get_clock_info()`, `zynqmp_register_clocks()`, and the platform driver matching `xlnx,zynqmp-clk`/`xlnx,versal-clk`.

Control flow: probe calls `zynqmp_clk_setup()`, which queries the clock count, allocates `zynqmp_data` and the `clock` array, gathers attributes/names/topology/parents for each valid clock, registers output clocks by walking each topology node, and finally calls `of_clk_add_hw_provider()`.

State and persistence: global `clock`, `zynqmp_data`, and `clock_max_idx` persist for the driver lifetime. Runtime clock state remains in PM firmware; Linux stores discovered names, parent lists, topology nodes, and registered `clk_hw` pointers.

Dependencies and integration points: depends on ZynqMP PM query ABI, OF clock provider APIs, CCF, and the local PLL/divider/mux/gate/fixed-factor registration helpers.

Risks: firmware response parsing is tightly bound to bitfield layouts. Parent-name mutation uses `strcat()` into fixed buffers and assumes firmware names plus postfixes fit. `__zynqmp_clock_get_parents()` indexes the passed response slice, so caller offset handling must stay correct. Intermediate names allocated with `kasprintf()` are freed after registration, relying on CCF copying names as expected.

Test signals: boot-time clock registration count, `clk_summary`, firmware topology fuzz/compatibility, external parent resolution through `clock-names`, and probe failure tests for allocation or PM query errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clkc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/divider.c

Purpose: implements ZynqMP firmware-controlled adjustable divider clocks, including read-only, power-of-two, and fractional-parent cases.

Important APIs/types/functions: `struct zynqmp_clk_divider`, `zynqmp_clk_register_divider()`, `zynqmp_clk_divider_recalc_rate()`, `zynqmp_clk_divider_determine_rate()`, `zynqmp_clk_divider_set_rate()`, `zynqmp_clk_get_max_divisor()`, and divider flag mapping helpers.

Control flow: registration decodes topology flags, asks firmware for the maximum divisor, and registers either read-write or read-only CCF ops. Recalc reads packed DIV1/DIV2 values via `zynqmp_pm_clock_getdivider()`. Set-rate computes the closest divisor and writes it through `zynqmp_pm_clock_setdivider()`.

State and persistence: hardware divider state persists in firmware. The driver stores the clock id, divider type, max divisor, and decoded behavior flags.

Dependencies and integration points: used by `clkc.c` for `TYPE_DIV1` and `TYPE_DIV2` nodes. Depends on generic divider helpers, PM clock get/set divider APIs, and CCF rate request semantics.

Risks: read-only selection tests generic `CLK_DIVIDER_READ_ONLY` against firmware `type_flag`. Flag mapping maps `ZYNQMP_CLK_DIVIDER_POWER_OF_TWO` to `CLK_DIVIDER_HIWORD_MASK`, which should be reviewed against intended ABI. Zero divisor handling warns but returns parent rate. Fractional-parent logic mutates `best_parent_rate` when `CLK_SET_RATE_PARENT` is set.

Test signals: rate rounding across max divisor boundaries, DIV1/DIV2 packed writes, read-only divider behavior, power-of-two divider rates, and firmware failures from max-divisor or setdivider queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/pll.c

Purpose: implements ZynqMP PLL clocks controlled through PM firmware, including integer and fractional modes.

Important APIs/types/functions: `struct zynqmp_pll`, `enum pll_mode`, `zynqmp_clk_register_pll()`, `zynqmp_pll_get_mode()`, `zynqmp_pll_set_mode()`, `zynqmp_pll_determine_rate()`, `zynqmp_pll_recalc_rate()`, `zynqmp_pll_set_rate()`, and enable/disable/is_enabled callbacks.

Control flow: CCF rate selection keeps the VCO in the 1.5 GHz to 3.0 GHz range and clamps feedback divider values to 25..125. Recalc reads divider and optional fractional data. Set-rate chooses fractional mode when the requested rate cannot be represented by an integer feedback divider, writes divider and fractional data, and then enable handles any required PLL mode refresh.

State and persistence: PLL mode, divider, enable state, and fractional data live in firmware/hardware. `set_pll_mode` is a local latch used so enable is not skipped immediately after a fractional-mode IOCTL.

Dependencies and integration points: called from `clkc.c` for `TYPE_PLL` topology nodes. Depends on ZynqMP PM APIs for clock state, divider, fractional mode, and fractional data.

Risks: `zynqmp_pm_get_pll_frac_data()` and `zynqmp_pm_set_pll_frac_data()` return values are not checked. Rate arithmetic uses `long` intermediates and can be sensitive to large rates. A firmware `-EUSERS` set-divider result warns for shared PLL ownership but still continues fractional data handling.

Test signals: integer and fractional PLL rate programming, VCO boundary requests, shared-user firmware errors, enable after mode switch, and clock summaries comparing expected versus actual rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynqmp/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clocksource/Kconfig

Purpose: defines the configuration menu and symbols for Linux clocksource and clockevent drivers across many architectures and SoCs.

Important APIs/types/functions: Kconfig symbols include framework selectors (`TIMER_OF`, `TIMER_ACPI`, `TIMER_PROBE`, `CLKSRC_MMIO`), generic device options (`DW_APB_TIMER`, `ARM_ARCH_TIMER`, `ARM_GLOBAL_TIMER`, `CLKSRC_EXYNOS_MCT`), and many platform-specific timer drivers.

Control flow: configuration dependencies and `select` statements decide which timer infrastructure and driver objects can be built. Some options are hidden booleans selected by architecture code; many platform timers are visible only under `COMPILE_TEST`.

State and persistence: no runtime state; the selected symbols persist in `.config` and drive Kbuild.

Dependencies and integration points: integrates architecture symbols, OF/ACPI timer probing, MMIO clocksource helpers, CPU hotplug-related drivers, watchdog/MFD/clk dependencies, and per-SoC timer implementations.

Risks: hidden selects can produce surprising build inclusion. Some options depend on architecture-specific facilities such as `GENERIC_SCHED_CLOCK`, `HAS_IOMEM`, `COMMON_CLK`, or ACPI GTDT. A config symbol mismatch with the Makefile can silently omit a driver.

Test signals: `allmodconfig`, `allyesconfig`, `randconfig`, architecture defconfigs, and compile-test coverage for timer drivers selected by visible prompts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clocksource/Makefile

Purpose: maps clocksource Kconfig symbols to object files in `drivers/clocksource`.

Important APIs/types/functions: Kbuild entries include infrastructure (`timer-of.o`, `timer-probe.o`, `mmio.o`), legacy devices (`i8253.o`), ARM timers, DesignWare APB timers, Hyper-V, Exynos MCT, Ingenic timers, and numerous SoC-specific timer objects.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` assignment and links the selected objects into built-in kernel code or modules as dictated by configuration.

State and persistence: no runtime state; it persists the compile/link graph.

Dependencies and integration points: paired with `Kconfig` symbols and each driver’s `TIMER_OF_DECLARE`, platform driver, or arch initcall entry point.

Risks: missing or stale symbol/object mappings break driver inclusion. Some objects depend on headers and architecture facilities not evident from this file, so compile-test remains important.

Test signals: targeted `make drivers/clocksource/`, broad randconfig builds, and symbol-to-object audits against `Kconfig`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/acpi_pm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/acpi_pm.c

Purpose: registers the ACPI PM timer as a 24-bit continuous clocksource using an I/O port discovered by platform setup or overridden on the command line.

Important APIs/types/functions: exports `pmtmr_ioport`, `acpi_pm_read_verified()`, suspend/resume callback registration helpers, `clocksource_acpi_pm`, `init_acpi_pm_clocksource()`, and `parse_pmtmr()`.

Control flow: early PCI fixups may lower rating and switch reads to a verified multi-read workaround. `fs_initcall` validates monotonicity, optional PIT-rate sanity, and then registers the clocksource at `PMTMR_TICKS_PER_SEC`.

State and persistence: global I/O port, optional callback pointer/data, and mutable clocksource read/rating fields persist for runtime. The hardware counter is free-running and not reset here.

Dependencies and integration points: depends on ACPI PM timer definitions, x86 I/O port access, PCI chipset fixups, optional PIT calibration, and clocksource suspend/resume hooks.

Risks: broken chipsets require triple-read verification and lower performance. Invalid BIOS timer rates disable the source. Callback registration is unguarded and assumes controlled users. `pmtmr=` can override firmware-provided ports.

Test signals: PM timer monotonicity checks at boot, `acpi_pm_good`/`pmtmr=` command-line paths, suspend/resume callback invocation, and chipset blacklist/graylist coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/acpi_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arc_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/arc_timer.c

Purpose: supports ARC core timers as clocksources and per-CPU clockevents, including 32-bit TIMER0/TIMER1 and optional 64-bit RTC/GFRC counters.

Important APIs/types/functions: `arc_get_timer_clk()`, `arc_cs_setup_gfrc()`, `arc_cs_setup_rtc()`, `arc_cs_setup_timer1()`, `arc_clockevent_setup()`, per-CPU `arc_clockevent_device`, and `arc_of_timer_init()`.

Control flow: DT declarations initialize either a clockevent node or a clocksource node. Clockevents use TIMER0 with a per-CPU IRQ and CPU hotplug callbacks. Clocksources use TIMER1 for legacy UP or RTC/GFRC for ARCv2 depending on hardware capability and SMP suitability.

State and persistence: global timer frequency and IRQ persist; per-CPU clockevent devices are registered on CPU bring-up. Counter hardware state is programmed through ARC auxiliary registers.

Dependencies and integration points: depends on ARC auxiliary register helpers, MCIP/GFRC support, OF clock/IRQ parsing, sched_clock, and clockevents.

Risks: local TIMER1 and RTC are rejected for SMP. GFRC reads disable local IRQs around MCIP commands. Missing or disabled parent clocks abort initialization. Timer interrupt acknowledgement differs across ARC generations.

Test signals: DT compatible probing for `snps,arc-timer`, RTC/GFRC compatibles, CPU hotplug, SMP versus UP selection, and periodic/oneshot event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arc_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer.c

Purpose: implements the ARM architected system timer using CP15/system-register access for clocksource, sched_clock, per-CPU clockevents, vDSO time, and KVM timestamp support.

Important APIs/types/functions: `arch_timer_read_counter`, `clocksource_counter`, `cyclecounter`, `arch_timer_register()`, `arch_counter_register()`, `arch_timer_of_init()`, `arch_timer_acpi_init()`, erratum workaround tables, CPU hotplug callbacks, and exported helpers `arch_timer_get_rate()`, `arch_timer_get_kvm_info()`, `kvm_arch_ptp_get_crosststamp()`.

Control flow: DT or ACPI GTDT probing maps PPIs, validates frequency, applies errata, selects physical/virtual/hypervisor timer access, requests per-CPU IRQs, registers CPU hotplug setup, registers the counter clocksource and sched_clock, and exposes KVM timecounter metadata.

State and persistence: global rate, selected PPI, erratum state, event-stream cpumask, per-CPU `clock_event_device`, CPU PM saved control registers, and KVM timecounter persist after init.

Dependencies and integration points: integrates with OF, ACPI GTDT, CPU PM, CPU hotplug, vDSO clock modes, arm64 capability detection, SMCCC/KVM PTP, sched_clock, and clockevents.

Risks: firmware must provide correct interrupt and frequency data. Erratum workarounds can disable vDSO fast paths and alter counter reads. PPI trigger validation repairs bad firmware with warnings. Suspend-stop behavior depends on DT/ACPI data. Incorrect PPI selection affects guests and EL2 configurations.

Test signals: DT and ACPI boot paths, virtual versus physical timer selection, erratum-specific platforms, CPU hotplug, suspend/resume, event stream enablement, vDSO clock mode, and KVM PTP cross timestamp calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer_mmio.c

Purpose: supports memory-mapped ARM generic timer frames as clocksource and clockevent devices.

Important APIs/types/functions: `struct arch_timer`, `arch_timer_mmio_write()`, `arch_timer_mmio_read()`, `arch_counter_mmio_get_cnt()`, `find_best_frame()`, `arch_timer_mmio_frame_register()`, `of_populate_gt_block()`, and built-in platform drivers for OF and ACPI GTDT MMIO timers.

Control flow: probe obtains a generic timer block from DT or platform data, maps the control frame, chooses a virtual-capable frame when possible or physical frame otherwise, maps the selected frame, determines the rate, requests IRQ, registers a clockevent, then registers a 56-bit MMIO clocksource.

State and persistence: one `struct arch_timer` per platform device stores frame metadata, MMIO base, access mode, rate, clockevent, and clocksource.

Dependencies and integration points: integrates with `clocksource/arm_arch_timer.h`, OF child frame descriptions, ACPI GTDT platform data, MMIO accessors, and the sysreg arch timer rate as fallback.

Risks: CVAL writes are non-atomic and require disabling the timer first. Frame access is probed by writing `CNTACR`, so firmware permissions must allow it. No failure is allowed after IRQ request/setup. Rate fallback can mask incomplete firmware data.

Test signals: DT frame parsing, virtual-frame preference, physical fallback, IRQ delivery, clocksource monotonicity, and ACPI GTDT MMIO probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arm_arch_timer_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arm_global_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/arm_global_timer.c

Purpose: registers the ARM Cortex-A9 global timer as a 64-bit clocksource, sched_clock/delay timer, and per-CPU clockevent source.

Important APIs/types/functions: `_gt_counter_read()`, `gt_compare_set()`, `gt_clocksource_init()`, clockevent callbacks, clock-rate notifier `gt_clk_rate_change_cb()`, CPU hotplug callbacks, and `global_timer_of_register()`.

Control flow: DT init validates CPU revision, maps registers, enables the parent clock, computes a prescaler, registers a clock notifier, allocates per-CPU clockevents, requests PPI, initializes the clocksource, installs CPU hotplug state, and registers delay timer support.

State and persistence: global MMIO base, target rate, prescaler bookkeeping, PPI, clock notifier, and per-CPU clockevent objects persist. Hardware counter is reset and enabled during clocksource init.

Dependencies and integration points: depends on OF, CCF clock rate notifications, ARM CPU ID checks, per-CPU IRQs, sched_clock, delay timer registration, and clockevents.

Risks: older Cortex-A9 revisions are rejected. Clock-rate changes are accepted only if a prescaler can preserve target rate within error bounds. Erratum 740657 requires special oneshot interrupt handling. Resource cleanup exists only for init failures.

Test signals: Zynq and AM43 prescaler defaults, CPU hotplug, parent clock-rate transitions, oneshot duplicate-interrupt workaround, and sched_clock monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/arm_global_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/armv7m_systick.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/armv7m_systick.c

Purpose: exposes the ARMv7-M SysTick down-counter as a simple MMIO clocksource.

Important APIs/types/functions: `system_timer_of_register()` maps registers, obtains the rate from `clock-frequency` or a clock provider, programs reload/control registers, and calls `clocksource_mmio_init()`.

Control flow: DT `arm,armv7m-systick` probing maps the timer, resolves a nonzero rate, loads the 24-bit reload maximum, enables the counter, and registers a 24-bit down-counting clocksource.

State and persistence: MMIO counter state is configured once; optional clock is enabled and kept on after successful registration.

Dependencies and integration points: depends on OF address mapping, common clock APIs, and `clocksource_mmio_readl_down`.

Risks: no clockevent is provided. Error paths release the clock and unmap registers, but successful path keeps resources permanently. A missing or zero frequency prevents registration.

Test signals: DT probe with explicit frequency and with clk provider, 24-bit wrap handling, and clocksource registration logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/armv7m_systick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/asm9260_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/asm9260_timer.c

Purpose: supports the AlphaScale ASM9260 timer block as a clocksource and system clockevent.

Important APIs/types/functions: global `priv`, `asm9260_timer_set_next_event()`, state callbacks for oneshot/periodic/shutdown, interrupt handler, and `asm9260_timer_init()`.

Control flow: DT init maps registers, enables the clock, requests the IRQ, configures all counters for count-up timer mode, registers TC1 as a 32-bit MMIO clocksource, sets MR1 to max and starts TC1, then configures TC0 as a clockevent.

State and persistence: global MMIO base and `ticks_per_jiffy` persist. TC0 is used for events; TC1 is used for free-running clocksource.

Dependencies and integration points: depends on OF address/IRQ/clock helpers, clockevents, and `clocksource_mmio_init`.

Risks: some error paths after mapping/clock acquisition do not fully release earlier resources. The driver assumes TC1 cannot run without a match register and sets MR1 to max. Clockevent cpumask is CPU0 only.

Test signals: DT compatible probing, periodic and oneshot timer interrupts, TC1 monotonic reads, clock enable failure paths, and CPU0-only event behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/asm9260_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/bcm2835_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/bcm2835_timer.c

Purpose: supports the BCM2835 system timer as a 32-bit clocksource/sched_clock and one compare channel as a oneshot clockevent.

Important APIs/types/functions: `struct bcm2835_timer`, `bcm2835_sched_read()`, `bcm2835_time_set_next_event()`, `bcm2835_time_interrupt()`, and `bcm2835_timer_init()`.

Control flow: DT init maps registers, reads `clock-frequency`, registers sched_clock and a 32-bit MMIO clocksource from the low counter, maps the default timer IRQ, allocates a timer object, requests a shared IRQ, and registers a oneshot clockevent using compare channel 3.

State and persistence: `system_clock` global points to the counter low register; allocated timer object stores control/compare addresses and event device state.

Dependencies and integration points: depends on OF register/IRQ parsing, sched_clock, MMIO clocksource helpers, and shared interrupt handling.

Risks: only the low 32 bits are used despite a high counter register. Default channel 3 and IRQ index are hardcoded. Event handler is read with `READ_ONCE()` to tolerate early interrupts. Successful resources are permanent.

Test signals: Raspberry Pi DT boot, compare interrupt delivery, shared IRQ behavior, sched_clock monotonicity, and 32-bit wrap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/bcm2835_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/bcm_kona_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/bcm_kona_timer.c

Purpose: registers the Broadcom Kona peripheral timer as a oneshot clockevent source.

Important APIs/types/functions: `struct kona_bcm_timers`, `kona_timer_get_counter()`, `kona_timer_set_next_event()`, `kona_timer_shutdown()`, `kona_timer_interrupt()`, and `kona_timer_init()`.

Control flow: DT init gets rate from a clock or `clock-frequency`, maps IRQ and registers, disables pending compare state, registers a CPU0 oneshot clockevent, requests the timer IRQ, and arms the first event.

State and persistence: global `timers` holds IRQ and MMIO base; `arch_timer_rate` stores the event rate. Compare register 0 drives events.

Dependencies and integration points: depends on OF clocks/address/IRQ and clockevents.

Risks: `of_iomap()` and IRQ parse results are not checked before use. `clk_prepare_enable()` return is ignored. The 64-bit counter read retries only three times and returns `-ETIMEDOUT` on instability. The driver notes possible skew between interrupt and next-event programming.

Test signals: compatible strings `brcm,kona-timer` and deprecated `bcm,kona-timer`, IRQ delivery, counter-read retry failures, and clock-frequency fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/bcm_kona_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/clksrc-dbx500-prcmu.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/clksrc-dbx500-prcmu.c

Purpose: uses ST-Ericsson DBx500 PRCMU timer 4 in the always-on domain as a 32 kHz clocksource.

Important APIs/types/functions: `clksrc_dbx500_prcmu_read()`, `clocksource_dbx500_prcmu`, and `clksrc_dbx500_prcmu_init()`.

Control flow: DT init maps the timer, ensures it is configured as a continuous down-counter with max reload if firmware did not do so, and registers a 32-bit continuous suspend-nonstop clocksource at 32768 Hz.

State and persistence: a global MMIO base persists. Hardware timer mode/ref registers may be initialized once and then left running.

Dependencies and integration points: depends on OF mapping and the clocksource core; no clockevent or clock framework dependency appears in this file.

Risks: `of_iomap()` is not checked for failure. The fixed rate assumes the PRCMU timer always runs at 32 kHz. Read uses two consecutive reads to avoid unstable values, then bitwise-negates the decrementing counter.

Test signals: DB8500 DT probe, suspend/resume timekeeping, continuous-mode register state, and 32-bit wrap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/clksrc-dbx500-prcmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/clksrc_st_lpc.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/clksrc_st_lpc.c

Purpose: registers the ST Low Power Controller low-power timer as a clocksource when the LPC mode is configured for clocksource operation.

Important APIs/types/functions: global `ddata`, `st_clksrc_reset()`, `st_clksrc_sched_clock_read()`, `st_clksrc_setup_clk()`, `st_clksrc_init()`, and `st_clksrc_of_register()`.

Control flow: DT init reads `st,lpc-mode`, exits if not clocksource mode, maps registers, enables the LPC clock, resets and starts the low-power timer, registers sched_clock, and registers a 32-bit MMIO clocksource.

State and persistence: global clock pointer and MMIO base persist; timer registers are reset to zero and started on init.

Dependencies and integration points: depends on `dt-bindings/mfd/st-lpc.h`, OF mapping, CCF, sched_clock, and `clocksource_mmio_init`.

Risks: a shared LPC block can be configured for RTC/WDT instead, in which case this driver silently does nothing. Initialization failure after clock enable performs cleanup, but successful resources are permanent. Mode property is mandatory.

Test signals: DT mode selection, clock enable/rate failure paths, sched_clock registration, and monotonic clocksource reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/clksrc_st_lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/clps711x-timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/clps711x-timer.c

Purpose: supports Cirrus Logic CLPS711X timers as either a 16-bit down-counting clocksource or a periodic clockevent depending on DT alias id.

Important APIs/types/functions: `clps711x_clksrc_init()`, `_clps711x_clkevt_init()`, `clps711x_timer_interrupt()`, and `clps711x_timer_init()`.

Control flow: DT init maps the timer, resolves IRQ and clock, then switches on `of_alias_get_id(np, "timer")`. Alias 0 registers a 16-bit down-counting MMIO clocksource and sched_clock; alias 1 programs a prescaler and registers a periodic C3STOP clockevent.

State and persistence: global `tcd` stores the clocksource register for sched_clock. Clockevent device is heap-allocated and registered with its IRQ.

Dependencies and integration points: depends on OF aliases, OF IRQ/address, CCF, sched_clock, clocksource MMIO helpers, and clockevents.

Risks: the init function unmaps `base` even after successful registration, leaving registered clocksource/clockevent callbacks with unmapped MMIO. Clockevent only supports periodic mode. Alias configuration is required for correct role selection.

Test signals: DT alias role split, clocksource reads after init, periodic interrupt delivery, and memory mapping lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/clps711x-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/dummy_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/dummy_timer.c

Purpose: registers per-CPU dummy clockevent devices for systems that need tick broadcast infrastructure without a real local timer.

Important APIs/types/functions: per-CPU `dummy_timer_evt`, `dummy_timer_starting_cpu()`, and `dummy_timer_register()`.

Control flow: an `early_initcall` installs a CPU hotplug state. On each CPU start, the driver initializes a `CLOCK_EVT_FEAT_DUMMY` clockevent with periodic and oneshot feature bits and registers it.

State and persistence: per-CPU `clock_event_device` objects persist statically.

Dependencies and integration points: depends on clockevents and CPU hotplug; built when `ARCH_HAS_TICK_BROADCAST` selects the object.

Risks: this is not a hardware timer and cannot generate interrupts; it is only valid when another broadcast mechanism supplies real ticks. Misuse as a primary timer would stall time events.

Test signals: CPU hotplug registration, tick broadcast behavior on platforms without local timers, and clockevent framework listings showing dummy devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/dummy_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer.c

Purpose: provides reusable clockevent and clocksource support for Synopsys DesignWare APB timers.

Important APIs/types/functions: `dw_apb_clockevent_init()`, `dw_apb_clockevent_register()`, `dw_apb_clocksource_init()`, `dw_apb_clocksource_start()`, `dw_apb_clocksource_register()`, `dw_apb_clocksource_read()`, and internal APBT state callbacks.

Control flow: clockevent init allocates a `dw_apb_clock_event_device`, configures min/max deltas, requests the IRQ, and returns it for registration. Clockevent state callbacks program periodic/free-running oneshot modes and load deltas. Clocksource init starts a masked, free-running down-counter and exposes its inverted value as an up-counting source.

State and persistence: allocated wrapper structs store MMIO base, IRQ, frequency, and clockevent/clocksource objects. Hardware timer control/load/current registers persist state.

Dependencies and integration points: exported through `linux/dw_apb_timer.h` and used by `dw_apb_timer_of.c` and other platform code. Depends on IRQ, MMIO, clockevents, and clocksource core.

Risks: oneshot mode is emulated using free-running mode. Programming requires careful enable/load ordering and a small delay for periodic mode. IRQ is requested during init, so users must call cleanup elsewhere if registration is abandoned. Minimum delta is fixed conservatively.

Test signals: direct users of exported init/register APIs, IRQ EOI handling, oneshot/periodic transition tests, and clocksource wrap/monotonicity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer_of.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer_of.c

Purpose: Device Tree glue that instantiates DesignWare APB timers as one clockevent and one clocksource/sched_clock.

Important APIs/types/functions: `timer_get_base_and_rate()`, `add_clockevent()`, `add_clocksource()`, `init_sched_clock()`, `read_sched_clock()`, and `dw_apb_timer_init()`.

Control flow: each matching DT timer increments `num_called`. The first discovered timer becomes clockevent; the second becomes clocksource and sched_clock, unless a separate sched-clock compatible node is found. Base/rate setup maps registers, optionally resets hardware, enables optional `pclk`, and derives rate from properties or the `timer` clock.

State and persistence: global `sched_io_base`, `sched_rate`, and `num_called` persist after init. Mapped timer bases and clocks remain live on success.

Dependencies and integration points: consumes `dw_apb_timer.c` exported helpers, OF clock/reset/IRQ/address APIs, sched_clock, and ARM delay timer registration.

Risks: timer role depends on DT probe order. Some failures call `panic()` instead of returning errors. Optional `pclk` enable failures only warn. Successful clock references are intentionally retained.

Test signals: DTs with one/two APB timers, separate `picochip,pc3x2-rtc` sched-clock node, reset-control presence, and event/source role assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer_of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/em_sti.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/em_sti.c

Purpose: supports the Renesas Emma Mobile STI 48-bit timer as both a clocksource and a oneshot clockevent.

Important APIs/types/functions: `struct em_sti_priv`, `em_sti_enable()/disable()`, `em_sti_count()`, `em_sti_set_next()`, clocksource enable/disable callbacks, clockevent callbacks, `em_sti_probe()`, and module init/exit.

Control flow: platform probe allocates private state, maps MMIO, requests IRQ, prepares/enables the `sclk` to determine rate, initializes a raw spinlock, then registers clockevent and clocksource. The timer clock is enabled lazily while either user is active.

State and persistence: private device state tracks active users for clocksource and clockevent, clock rate, MMIO base, clock handle, and embedded CCF objects. Counter and compare state is in hardware.

Dependencies and integration points: platform driver with OF compatible `renesas,em-sti`; depends on devm resources, CCF, raw spinlocks, IRQ, clocksource, and clockevents.

Risks: `em_sti_enable()` resets the counter when first user starts, which can affect continuity if users transition unexpectedly. Next-event returns failure when the compare value is already too close. Interrupt handler does not explicitly clear status; compare programming clears sources.

Test signals: platform probe, clocksource enable/disable suspend/resume hooks, oneshot event latency, shared clocksource/clockevent active-user transitions, and 48-bit read ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/em_sti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/exynos_mct.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/exynos_mct.c

Purpose: implements Samsung Exynos Multi-Core Timer support with a global free-running clocksource, optional global comparator, and per-CPU local clockevents.

Important APIs/types/functions: `exynos4_mct_write()`, `exynos4_read_count_64/32()`, `exynos4_clocksource_init()`, global comparator callbacks, per-CPU tick callbacks, `exynos4_timer_resources()`, `exynos4_timer_interrupts()`, `mct_init_dt()`, `mct_init_spi()`, and `mct_init_ppi()`.

Control flow: DT init reads local timer mapping, maps resources and clocks, parses global and local IRQs as SPI or PPI, installs CPU hotplug callbacks for local timers, starts/registers the global clocksource and sched_clock, and registers a global comparator clockevent unless the FRC is shared.

State and persistence: global MMIO base, clock rate, IRQ array, interrupt type, and per-CPU `mct_clock_event_device` objects persist. Hardware write-status polling ensures register writes have landed.

Dependencies and integration points: depends on OF, CCF, per-CPU IRQs or SPI affinity, CPU hotplug, sched_clock, delay timer, and clockevents.

Risks: several fatal resource failures call `panic()`. Write completion polling can panic if hardware hangs. Interrupt topology and `samsung,local-timers` must match CPU layout. Shared FRC mode disables the global comparator path.

Test signals: Exynos4210 SPI and Exynos4412 PPI compatibles, CPU hotplug, local timer mapping property, global clocksource monotonicity, global comparator periodic/oneshot behavior, and write-status timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/exynos_mct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/hyperv_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/hyperv_timer.c

Purpose: provides Hyper-V synthetic timers as per-CPU clockevents and Hyper-V reference counters as clocksources/sched_clock for guest and root partitions.

Important APIs/types/functions: `hv_stimer_alloc()`, `hv_stimer0_isr()`, `hv_stimer_cleanup()`, legacy init/cleanup exports, `hv_stimer_global_cleanup()`, `read_hv_clock_msr()`, `read_hv_clock_tsc()`, `hv_init_clocksource()`, `hv_init_tsc_clocksource()`, and `hv_remap_tsc_clocksource()`.

Control flow: stimer allocation checks hypervisor features, allocates per-CPU clockevents, chooses direct mode or legacy VMbus-message mode, sets up IRQ/handler, and registers CPU hotplug callbacks. Clocksource init prefers the TSC reference page when available, with MSR fallback, and registers the MSR clocksource when supported.

State and persistence: per-CPU clockevent devices, direct-mode flag, stimer IRQ/message SINT, TSC reference page/PFN, sched_clock offset, and registered clocksources persist.

Dependencies and integration points: integrates with Hyper-V MSRs, VMbus legacy callbacks, ACPI GSI setup, CPU hotplug, paravirt or generic sched_clock, vDSO clock mode, TDX/paravisor feature checks, hibernation offset adjustment, and root-partition remapping.

Risks: direct versus legacy mode has different initialization timing. TSC page can be unavailable transiently and falls back to slow MSR reads. Ratings are adjusted for invariant TSC/root partition/TDX cases. Cleanup must coordinate CPU hotplug and VMbus paths.

Test signals: Hyper-V guests with and without direct mode, legacy VMbus stimer path, CPU online/offline, hibernation resume offset adjustment, root partition remap, invariant TSC rating behavior, and vDSO HVCLOCK exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/hyperv_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/i8253.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/i8253.c

Purpose: supports the legacy i8253/i8254 PIT as both a jiffies-extended clocksource and a clockevent device.

Important APIs/types/functions: exported `i8253_lock`, `clocksource_i8253_init()`, `clockevent_i8253_disable()`, `clockevent_i8253_init()`, `i8253_read()`, and PIT state callbacks.

Control flow: clocksource reads latch channel 0 under the raw spinlock, combine the down-counting PIT value with `jiffies`, and clamp apparent backward movement. Clockevent init programs periodic and optional oneshot modes through I/O ports and registers the device.

State and persistence: static `old_count` and `old_jifs` preserve monotonic read adjustments. The PIT hardware and global raw spinlock are shared with other legacy users such as speaker/NMI control.

Dependencies and integration points: depends on x86-style I/O ports, `linux/i8253.h`, `jiffies`, clocksource, clockevents, and SMP cpumask handling.

Risks: low rating and 32-bit mask reflect limited precision. Reads intentionally have side effects, so locking and retry semantics are delicate. Virtual PIT implementations require extra disable sequencing. One-shot support is optional and hardware-limited.

Test signals: PIT clocksource registration, periodic tick boot fallback, oneshot mode when requested, virtualization disable behavior on KVM/QEMU/Hyper-V, and monotonicity around PIT underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/i8253.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-ost.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-ost.c

Purpose: registers the Ingenic JZ operating system timer as a continuous clocksource and sched_clock.

Important APIs/types/functions: `struct ingenic_ost_soc_info`, `struct ingenic_ost`, low/high counter read helpers, `ingenic_ost_probe()`, suspend/resume PM ops, and the built-in platform driver probe.

Control flow: probe matches SoC data, allocates state, maps registers, obtains the parent TCU regmap, enables the `ost` clock, clears counter registers, configures non-reset-on-compare mode, enables TCU channel 15, registers the clocksource, and registers sched_clock using the appropriate counter half.

State and persistence: global `ingenic_ost` supplies lockless sched_clock reads; device state stores MMIO base, clock, and embedded clocksource. The TCU regmap controls shared timer registers.

Dependencies and integration points: depends on MFD Ingenic TCU definitions, syscon/regmap, platform device probing, CCF, PM sleep ops, clocksource, and sched_clock.

Risks: for 64-bit SoCs the driver still registers a 32-bit mask and reads the low half; for older SoCs it uses the high register. Global singleton design assumes one OST. `dev_get_drvdata()` in PM callbacks requires driver data to be set, but probe does not call `platform_set_drvdata()`.

Test signals: JZ4725B versus JZ4760B/JZ4770 compatibles, regmap access, suspend/resume clock gating, sched_clock monotonicity, and probe with missing parent regmap or clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-ost.c -->

# subset-b-000838 research

This grouped report covers SH4A and SH-Mobile kernel backend files from `sources/distributed-fs/ceph-client`. Each source file has a separate section delimited for deterministic split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-shx3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-shx3.c

Purpose: provides SH-X3 clock-framework registration for the legacy SuperH clock tree. It defines the external input clock, a fixed PLL clock, DIV4-derived clocks, MSTP gate clocks, and `clkdev` lookup aliases used by SH-X3 platform devices.

Important APIs, types, and functions: `arch_clk_init()` is the exported init entry point. `pll_recalc()` models PLL1 as `parent * 72`. Static `struct clk`, `struct sh_clk_ops`, `struct clk_div4_table`, `struct clk_div_mult_table`, and `struct clk_lookup` instances describe hardware clocks. The file uses `SH_CLK_DIV4`, `SH_CLK_MSTP32`, `CLKDEV_CON_ID`, and `CLKDEV_ICK_ID`.

Control flow: `arch_clk_init()` registers `extal_clk` and `pll_clk`, installs the lookup table, then registers DIV4 clocks and MSTP gate clocks if prior registration succeeded. Device drivers later acquire these clocks by connection id or by `(dev_id, con_id)` pairs such as `fck` for `sh-sci.*` and `sh-tmu.*`.

State and persistence: state is static kernel clock metadata plus MMIO-backed gate/divider state in `FRQMR1`, `MSTPCR0`, and `MSTPCR1`. The default EXTAL rate is `16666666` Hz and can be overridden by platform code through `clk_set_rate()`. Clocks marked `CLK_ENABLE_ON_INIT` stay enabled from boot.

Dependencies and integration points: depends on the SuperH clock core in `<asm/clock.h>`, frequency register definitions in `<asm/freq.h>`, `clkdev`, and MMIO helpers. It integrates with SH-X3 setup files that instantiate `sh-sci`, `sh-tmu`, H8, CSM, FE, HUDI, and DMAC devices.

Risks: register addresses and bit masks are hard-coded for SH-X3; wrong SoC selection can gate required clocks or expose invalid aliases. `ret |= clk_register()` collapses individual error codes and continues registering all root clocks. Some MSTP clocks have `NULL` parents, so consumers rely on gate control without rate derivation.

Test signals: boot log should show no clock registration failures; serial and TMU devices should probe and obtain `fck`; clock debugfs/sysfs, if enabled, should show expected rates derived from EXTAL and PLL; suspend/resume or module stop tests should verify MSTP gates do not disable essential clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-shx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/intc-shx3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/intc-shx3.c

Purpose: supplies shared SH-X3 interrupt-controller glue that is not tied to a single interrupt vector table. It registers the user interrupt mask register and, when balancing is enabled, provides acknowledge/finish helpers for the SH-X3 interrupt-distribution path.

Important APIs, types, and functions: `shx3_irq_setup()` calls `register_intc_userimask(INTC_USERIMASK)` at `arch_initcall`. Under `CONFIG_INTC_BALANCING`, `irq_lookup()` samples `INTACK` and returns either the IRQ or `NO_IRQ_IGNORE`, while `irq_finish()` writes `irq2evt(irq)` to `INTACKCLR`.

Control flow: early interrupt setup from SoC-specific `setup-shx3.c` registers the main descriptors; this file later registers the user mask at `0xfe411000`. Balanced interrupt handling calls the lookup and finish hooks around dispatched interrupts.

State and persistence: no heap state is kept. Persistent behavior is in MMIO registers `INTACK`, `INTACKCLR`, and `INTC_USERIMASK`.

Dependencies and integration points: depends on `<linux/irq.h>`, `<linux/io.h>`, and SuperH INTC helper APIs. It complements `setup-shx3.c`, `setup-sh7786.c`, and other INTC descriptors that use SMP balancing macros.

Risks: the balancing helpers assume the acknowledgement register protocol and event-code mapping match the active SH-X3 interrupt controller. Misordered ack/clear writes can lose interrupts. `irq_lookup()` masks on bit 0 only, so behavior depends on undocumented hardware semantics.

Test signals: with `CONFIG_INTC_BALANCING`, multi-CPU interrupt routing should deliver interrupts once and clear them; `/proc/interrupts` should increment on expected CPUs; boot should not warn about user-imask registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/intc-shx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/perf_event.c

Purpose: implements the SH-4A hardware performance-counter backend for Linux perf. It maps generic and cache perf events to SH-4A raw event codes and provides register operations for two hardware counters.

Important APIs, types, and functions: `sh4a_pmu_init()` registers `sh4a_pmu` with `register_sh_pmu()` during `early_initcall`. `sh4a_event_map()`, `sh4a_pmu_read()`, `sh4a_pmu_enable()`, `sh4a_pmu_disable()`, `sh4a_pmu_enable_all()`, and `sh4a_pmu_disable_all()` implement `struct sh_pmu`. The event tables are `sh4a_general_events` and `sh4a_cache_events`.

Control flow: init first checks `boot_cpu_data.flags & CPU_HAS_PERF_COUNTER`; unsupported CPUs get software events only. Perf event setup uses the generic map or cache matrix to select `hwc->config`; enabling a counter clears the corresponding PMCAT overflow/clear bit, writes the event code into `PPC_CCBR(idx)`, enables command/counting bits, then sets `CCBR_DUC`.

State and persistence: counter state lives in hardware registers `PPC_CCBR`, `PPC_PMCTR`, and `PPC_PMCAT`. `PPC_PMCAT` has a SH-X3-specific address under `CONFIG_CPU_SHX3`. The static PMU advertises two counters and a `raw_event_mask` of `0x3ff`.

Dependencies and integration points: integrates with Linux perf through SuperH `register_sh_pmu()`, `<linux/perf_event.h>`, and `<asm/processor.h>`. Raw MMIO helpers access fixed CPU counter registers.

Risks: comments note undocumented SH-X3 PMCAT relocation found by trial and error, so CPU revisions may differ. Unsupported generic events use `-1`, and several cache matrix entries use `0`, which must match generic SH PMU interpretation. Writes must preserve emulator-reserved PMCAT bits via `PMCAT_EMU_CLR_MASK`.

Test signals: `perf stat` for cycles, instructions, branch instructions, and L1 cache events should produce counts on CPUs with `CPU_HAS_PERF_COUNTER`; unsupported events should fail cleanly; SH-X3 testing should confirm counters clear and count using the alternate PMCAT address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7722.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7722.c

Purpose: registers the SH7722 pin function controller resource window with the SuperH PFC core.

Important APIs, types, and functions: `plat_pinmux_setup()` calls `sh_pfc_register("pfc-sh7722", sh7722_pfc_resources, ARRAY_SIZE(...))` at `arch_initcall`. The resource array exposes MMIO `0xa4050100-0xa405018f`.

Control flow: the initcall runs during architecture initialization and creates the PFC platform registration before most device consumers request GPIO or function pins.

State and persistence: no local mutable state beyond the static resource table; hardware state is in PFC registers and owned by the PFC driver after registration.

Dependencies and integration points: depends on `<cpu/pfc.h>` and the SoC-specific PFC driver named `pfc-sh7722`. Board files and serial setup rely on this registration for pin modes.

Risks: the file only registers one MMIO range, so incorrect range size or base prevents PFC probing. No validation is performed locally.

Test signals: boot should register/probe `pfc-sh7722`; GPIO/function requests for SH7722 board devices should succeed; pinmux debug output should show the expected resource span.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7723.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7723.c

Purpose: registers the SH7723 PFC MMIO block with the SuperH pin-control framework.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7723`; `sh7723_pfc_resources` describes `0xa4050100-0xa405016f`.

Control flow: an `arch_initcall` invokes the registration once during boot. The PFC core later binds the named driver and services GPIO/pin-function requests.

State and persistence: this file contains static immutable resource metadata only. Persistent pin state is maintained by the hardware and PFC core.

Dependencies and integration points: integrates with `<cpu/pfc.h>` and SH7723 board/platform setup, especially SCIF/SCIFA, I2C, USB, and multimedia pin assignments.

Risks: there is no runtime SoC detection; building or selecting this for the wrong CPU registers the wrong address range. Missing GPIO resource means all access is through the PFC range.

Test signals: `pfc-sh7723` should probe without MMIO conflicts, and platform devices requiring alternate pin functions should initialize correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7724.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7724.c

Purpose: registers the SH7724 PFC register window for the SuperH PFC driver.

Important APIs, types, and functions: `plat_pinmux_setup()` calls `sh_pfc_register("pfc-sh7724", ...)`; the sole resource maps `0xa4050100-0xa405016f`.

Control flow: the arch initcall provides PFC resources before board-level pin requests and before device drivers configure their pins.

State and persistence: no local runtime state; pinmux state is externalized to the PFC hardware and driver.

Dependencies and integration points: the registration names the SoC-specific PFC driver used by SH7724 setup paths for SCIF, DMA-capable peripherals, multimedia blocks, and sleep-state restoration.

Risks: resource range must match the PFC driver register model. Any mismatch can make pins unavailable or corrupt unrelated registers.

Test signals: PFC probe should succeed; SH7724 board devices should be able to request GPIO/function pins; suspend/resume should keep restored pins usable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7734.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7734.c

Purpose: registers SH7734 PFC and GPIO register windows with the PFC core.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7734`. `sh7734_pfc_resources` contains a PFC range `0xfffc0000-0xfffc011c` and GPIO range `0xffc40000-0xffc4502b`.

Control flow: the arch initcall publishes both resource ranges, allowing the PFC driver to manage function selection and GPIO controller registers.

State and persistence: local state is immutable resource metadata. Persistent state is hardware pin configuration and GPIO register contents.

Dependencies and integration points: integrates with `<cpu/pfc.h>` and SH7734 platform setup for SCIF, TMU, RTC, I2C, and external interrupt pin routing.

Risks: two distinct MMIO windows must remain in the expected order. The PFC driver likely assumes index 0 is PFC and index 1 is GPIO.

Test signals: probe should claim both ranges; GPIO and PFC debug output should expose SH7734 pins; external IRQ pin modes selected in `setup-sh7734.c` should work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7734.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7757.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7757.c

Purpose: registers the SH7757 B0-step pinmux resource with the PFC subsystem.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7757`; `sh7757_pfc_resources` maps `0xffec0000-0xffec008f`.

Control flow: boot-time `arch_initcall` registers the range before SH7757 devices such as SCIF, SPI, DMA, USB, and external IRQ modes need pin functions.

State and persistence: no local runtime state. PFC hardware and the PFC core own pin state after registration.

Dependencies and integration points: integrates with `<cpu/pfc.h>` and SH7757 setup code with multiple DMA engines and external interrupt-pin modes.

Risks: the comment identifies the B0 step; other silicon revisions may have incompatible pin registers. The file has no silicon-step check.

Test signals: `pfc-sh7757` should probe; SPI/SCIF/USB board pin requests should succeed; external IRQ mode selection should be reflected in PFC/GPIO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7757.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7785.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7785.c

Purpose: registers the SH7785 PFC MMIO block.

Important APIs, types, and functions: `plat_pinmux_setup()` calls `sh_pfc_register("pfc-sh7785", ...)`; resource 0 maps `0xffe70000-0xffe7008f`.

Control flow: `arch_initcall` registers the PFC resources during early platform initialization for later PFC driver binding.

State and persistence: local state is static resource metadata only.

Dependencies and integration points: integrates with the SH7785 PFC driver and setup code for SCIF, TMU, DMA, and external IRQ/IRL pin selection.

Risks: wrong resource address corrupts pin-function access. No fallback exists if the PFC driver is absent.

Test signals: `pfc-sh7785` probe success and working SCIF/TMU board pins are the main integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7785.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7786.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7786.c

Purpose: registers the SH7786 PFC resource range.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7786`; the resource covers `0xffcc0000-0xffcc008f`.

Control flow: the PFC registration runs as an `arch_initcall`; later SH7786 platform device setup and external interrupt pin setup use the PFC core.

State and persistence: no local mutable state; pin state persists in SoC PFC registers.

Dependencies and integration points: works with SH7786 setup for serial, timers, DMA, USB, SMP interrupt distribution, and optional SCIF1 demuxing.

Risks: SH7786 has many interrupt and peripheral mux paths; PFC range mistakes can break early console or USB/PCIe board wiring.

Test signals: PFC probe success, working serial pins, and successful board-specific pin requests validate this registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7786.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-shx3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-shx3.c

Purpose: registers the prototype SH-X3 PFC block with the SuperH PFC framework.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-shx3`; the resource maps `0xffc70000-0xffc7001f`.

Control flow: an `arch_initcall` publishes the pin-controller resource before `setup-shx3.c` requests GPIO function pins for IRQ mode.

State and persistence: local state is static metadata only; hardware PFC registers hold pin selection state.

Dependencies and integration points: used by SH-X3 serial/timer setup and `plat_irq_setup_pins()`, which requests `GPIO_FN_IRQ0` through `GPIO_FN_IRQ3` in IRQ mode.

Risks: the prototype CPU has a very small PFC window and likely limited validation; unsupported pin modes will fail at request time.

Test signals: `pfc-shx3` should probe, IRQ pin requests should succeed, and external IRQ/IRL board modes should produce interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-shx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/serial-sh7722.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/serial-sh7722.c

Purpose: provides SH7722-specific SCI pin initialization for the first SCIF port.

Important APIs, types, and functions: `sh7722_sci_init_pins()` implements `struct plat_sci_port_ops.init_pins`. `sh7722_sci_port_ops` is exported as a global platform ops structure. The function edits the PSCR register at `0xa405011e`.

Control flow: the SCI core calls `.init_pins` with a `uart_port` and termios `cflag`. If `port->mapbase == 0xffe00000`, the code clears PSCR bits `0x03cf`; when hardware flow control is not requested (`!(cflag & CRTSCTS)`), it sets `0x0340`, then writes PSCR.

State and persistence: no software state is stored; the persistent effect is a PFC/serial pin register write. Pin state may be overwritten by later PFC changes or resume restoration.

Dependencies and integration points: depends on `linux/serial_sci.h`, `linux/serial_core.h`, raw MMIO, and SH7722 serial platform data that attaches `sh7722_sci_port_ops` to the relevant port.

Risks: the hook only handles one mapbase and uses hard-coded PSCR bits. Incorrect `cflag` handling can disable RTS/CTS or select conflicting pins. It bypasses generic pinctrl abstractions.

Test signals: opening SCIF0 with and without `CRTSCTS` should drive correct pins; serial loopback and hardware-flow-control tests should pass on SH7722 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/serial-sh7722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7343.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7343.c

Purpose: describes SH7343 on-chip platform devices and interrupt controller data. It is the SoC setup file that turns fixed hardware blocks into Linux platform devices and INTC descriptors.

Important APIs, types, and functions: `sh7343_devices_setup()` allocates contiguous memory placeholders for VPU/VEU/JPU and calls `platform_add_devices()`. `plat_early_device_setup()` registers early SCIF, CMT, and TMU devices. `plat_irq_setup()` registers `intc_desc`. Data types include `plat_sci_port`, `uio_info`, `sh_timer_config`, `platform_device`, `resource`, `intc_vect`, `intc_group`, mask/prio/sense/ack registers, and `intc_desc`.

Control flow: static resources define SCIF0-3, IIC0-1, VPU4, VEU, JPU, CMT, and TMU0. Early setup exposes serial/timer devices for console and timekeeping; the arch initcall adds the full device list. Interrupt setup separately maps event codes for IRQ0-7, DMA, VIO, USB, MMC, SCIF, I2C, timers, JPU, LCDC, and related groups.

State and persistence: device and interrupt metadata are static `__initdata` or static structures. Runtime state lives in platform drivers and INTC MMIO registers. UIO multimedia devices receive reserved memory via `platform_resource_setup_memory()`.

Dependencies and integration points: integrates with `sh-sci`, `i2c-sh_mobile`, `uio_pdrv_genirq`, `sh-cmt-32`, `sh-tmu`, platform early devices, SuperH clock names, and the SH INTC core.

Risks: interrupt tables and resource addresses are hand-maintained and must match silicon. Multimedia UIO memory reservations can fail or conflict. `force_enable` and `force_disable` sentinel entries must align with mask table usage.

Test signals: boot should register all listed devices, early console/timekeeping should work, UIO devices should expose memory and IRQs, I2C transfers should use correct IRQ ranges, and `/proc/interrupts` should reflect mapped event codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7343.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7366.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7366.c

Purpose: provides SH7366 platform-device and interrupt setup, based on SH7722 but reduced to the peripherals present on this SoC.

Important APIs, types, and functions: `sh7366_devices_setup()` reserves VPU/VEU memory and registers SCIF0, CMT, TMU0, IIC, USB host, VPU, and two VEU UIO devices. `plat_early_device_setup()` exposes early SCIF/CMT/TMU; `plat_irq_setup()` registers `intc_desc`; `plat_mem_setup()` is a stub noting TODO for Node 1.

Control flow: the file constructs resources for SCIF0, IIC, on-chip `r8a66597_hcd`, VPU5, VEU instances, CMT, and TMU0. Boot first registers early serial/timers, then arch init adds the full device list. Interrupt vectors cover external IRQs, ICB, DMA, VIO, MFI, VPU, USB, MMC, SCIF/SCIFA, DENC/MSIOF, FLCTL, I2C, SDHI, CMT, TSIF, SIU, timers, VEU2, and LCDC.

State and persistence: static platform data describes resources. Reserved multimedia memory persists as platform resources. INTC register state is programmed by the generic INTC core using mask/prio/sense/ack descriptions.

Dependencies and integration points: integrates with `sh-sci`, `i2c-sh_mobile`, `r8a66597_hcd`, UIO generic IRQ driver, timer drivers, and SuperH INTC.

Risks: USB IRQ is marked `IRQF_TRIGGER_LOW` in the resource flags; platform code must agree with the IRQ core. `plat_mem_setup()` is incomplete for Node 1. Device ids are tied to clock lookup names such as `i2c0`.

Test signals: validate early console, CMT/TMU clocksource, USB host enumeration, I2C interrupt operation, multimedia UIO IRQ delivery, and correct interrupt priorities/masks under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7366.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7722.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7722.c

Purpose: registers SH7722 platform devices, DMA engine metadata, audio support, timers, multimedia UIO blocks, and the SH7722 interrupt controller.

Important APIs, types, and functions: `sh7722_devices_setup()` reserves VPU/VEU/JPU memory and calls `platform_add_devices()`. `plat_early_device_setup()` registers SCIF0-2, CMT, and TMU0 early. `plat_irq_setup()` registers `intc_desc`; `plat_mem_setup()` is empty. DMA configuration uses `sh_dmae_slave_config`, `sh_dmae_channel`, and `sh_dmae_pdata`.

Control flow: the full device array includes a DMA engine, SCIF0-2, RTC, USB function controller `m66592_udc`, IIC, VPU4, VEU, JPU, CMT, TMU0, and SIU PCM audio. Early setup exposes serial and timers. INTC tables map IRQ0-7 plus DMA, video, USB, MMC, SCIF, SIOF, FLCTL, I2C, CMT, SIU, TMU, JPU, and LCDC sources into mask/prio/sense/ack registers.

State and persistence: static platform resources persist as device metadata after registration. DMA slave/channel tables encode CHCR transfer-size and direction bits. UIO memory resources are filled dynamically by `platform_resource_setup_memory()`.

Dependencies and integration points: integrates with `sh-dma-engine`, `sh-sci`, `sh-rtc`, `m66592_udc`, `i2c-sh_mobile`, `uio_pdrv_genirq`, `sh-cmt-32`, `sh-tmu`, `siu-pcm-audio`, and SuperH INTC. It relies on clock aliases for `sh-sci`, timers, I2C, USBF, and SIU.

Risks: DMA slave IDs, CHCR bits, and DMARS resources must match the DMA engine driver. UIO contiguous-memory placeholders are fragile. Empty `plat_mem_setup()` means no extra memory nodes are registered.

Test signals: exercise DMA-backed SIU/audio, SCIF ports, USB gadget mode, RTC interrupts, I2C, timer tick, multimedia UIO IRQs, and interrupt masking/ack for external IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7723.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7723.c

Purpose: registers SH7723 platform devices and interrupt tables, including serial, multimedia, timers, RTC, USB host, and I2C.

Important APIs, types, and functions: `sh7723_devices_setup()` reserves memory for VPU and two VEU blocks and calls `platform_add_devices()`. `plat_early_device_setup()` registers SCIF/SCIFA, CMT, and TMU devices early. `l2_cache_init()` enables L2 cache by writing `L2_CACHE_ENABLE` to `RAMCR`. `plat_irq_setup()` registers `intc_desc`.

Control flow: static devices cover SCIF0-2, SCIFA3-5, VPU5, VEU2H0/1, CMT, TMU0/1, RTC, `r8a66597_hcd`, and IIC. Early device setup enables console/timekeeping before normal platform registration. Interrupt vectors include external IRQs, DMA, video, USB, MMC, SCIF/SCIFA, FLCTL, I2C, SDHI, CMT, SIU, TMU, VEU, LCDC, VPU, and JPU-style sources.

State and persistence: device metadata is static; reserved memory resources for UIO blocks are filled at init. `l2_cache_init()` persists by changing the RAM/cache control register.

Dependencies and integration points: depends on serial SCI, UIO, SH timer, USB `r8a66597`, I2C mobile, RTC, SuperH cache/MMIO, and INTC core.

Risks: L2 cache enable is a bare register write without runtime probing. SCIFA and SCIF resource ranges differ, so clock and pin mappings must agree. USB IRQ trigger flags must match board wiring.

Test signals: verify early serial on all configured ports, L2 cache enable behavior, USB host enumeration, VPU/VEU UIO memory and IRQ delivery, CMT/TMU operation, and I2C transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7724.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7724.c

Purpose: provides the large SH7724 SoC setup: DMA engines, serial ports, RTC, I2C, multimedia UIO blocks, timers, cache enable, interrupt controller, and reset-standby save/restore.

Important APIs, types, and functions: `sh7724_devices_setup()`, `plat_early_device_setup()`, `l2_cache_init()`, `plat_irq_setup()`, `sh7724_pre_sleep_notifier_call()`, `sh7724_post_sleep_notifier_call()`, and `sh7724_sleep_setup()` are the major functions. Data includes two DMA engine devices, extensive DMA slave/channel tables, platform devices, INTC descriptors, and sleep notifier blocks.

Control flow: boot registers early SCIF0-5, CMT, and TMU0/1, then the arch initcall reserves memory for VPU, VEU0/1, JPU, SPU0/1 and registers the full device array. The interrupt setup maps a broad multimedia-heavy vector set. `l2_cache_init()` writes cache-enable bits to RAMCR. The sleep init registers pre/post notifiers on SH-Mobile sleep notifier chains.

State and persistence: persistent hardware state includes DMA controller registers, interrupt mask/prio registers, cache-control bits, and reset-standby saved state. `sh7724_rstandby_state` snapshots BCR, INTC, RWDT, and CPG registers before `SUSP_SH_RSTANDBY`, then restores them afterward.

Dependencies and integration points: integrates with `sh-dma-engine`, `sh-sci`, `sh-rtc`, `i2c-sh_mobile`, UIO generic IRQ driver, CMT/TMU timers, SH-Mobile sleep notifier lists, and SuperH INTC. DMA slave IDs cover SCIF, USB, SDHI, SIU, FLCTL, and I2C-style requesters.

Risks: the sleep save/restore list is manual and easy to miss when adding hardware. RWDT writes require key bits and could disturb watchdog state. DMA tables and multimedia memory reservations have high board-specific risk. Cache enable is unconditional.

Test signals: suspend/reset-standby resume should restore interrupts, CPG, bus-control, and watchdog state; DMA clients should transfer correctly; multimedia UIO blocks should receive IRQs; early console/timers, I2C, RTC, and L2 cache behavior should be verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7734.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7734.c

Purpose: registers SH7734 serial, RTC, I2C, and timer devices and defines the SH7734 interrupt controller including selectable external IRQ/IRL pin modes.

Important APIs, types, and functions: `plat_early_device_setup()` adds SCIF0-5 and TMU0-2 as early devices. `plat_irq_setup()` programs default IRL/IRQ masking and registers `intc_desc`. `plat_irq_setup_pins()` selects `IRQ_MODE_IRQ3210`, `IRQ_MODE_IRL3210`, or `IRQ_MODE_IRL3210_MASK`. Interrupt descriptors are declared with `DECLARE_INTC_DESC` and `DECLARE_INTC_DESC_ACK`.

Control flow: unlike many setup files, platform devices are collected in arrays but this file has no visible normal `arch_initcall` for `sh7734_devices`; early devices are explicitly registered. Interrupt setup disables IRQ/IRL lines, selects IRL mode by default, then registers the main descriptor. Board code can call `plat_irq_setup_pins()` to enable external pin modes.

State and persistence: static platform data persists in registered devices. INTC state is set through MMIO registers such as ICR0, INTMSK/INTMSKCLR, and descriptor-driven mask/prio/sense/ack registers.

Dependencies and integration points: integrates with `sh-sci`, `sh-rtc`, `i2c-sh7734`, `sh-tmu`, PFC/GPIO for pin modes, and SuperH INTC. SCIF uses BRG register type and one port enables timeout interrupts.

Risks: SCIF5 resource appears to reuse the `0xffe43000` base while carrying a different interrupt, which may be intentional muxing or a collision risk. The lack of a normal device-registration initcall means non-early devices depend on other registration paths. Pin mode defaults can mask external interrupts until board code selects a mode.

Test signals: confirm all intended platform devices appear, SCIF ports do not conflict, TMU timers run, I2C probes as `i2c-sh7734`, and each supported IRQ/IRL pin mode generates and masks interrupts correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7734.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7757.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7757.c

Purpose: provides SH7757 platform setup for SCIF, TMU, SPI/RSPI, four DMA engines, USB host controllers, interrupt descriptors, and a small URAM memory node.

Important APIs, types, and functions: `sh7757_devices_setup()` registers all devices; `plat_early_device_setup()` registers SCIF2-4 and TMU0 early; `plat_irq_setup()` registers the main `intc_desc`; `plat_irq_setup_pins()` supports IRQ7654/3210 and IRL7654/3210 modes with optional masking; `plat_mem_setup()` registers URAM with `setup_bootmem_node()`.

Control flow: platform resources describe three SCIF ports, TMU0, SPI0/1, RSPI, EHCI/OHCI, and DMA0-3. DMA tables provide separate slave configs and pdata per engine. Default IRQ setup masks external IRQ/IRL lines and registers core vectors; board pin setup selects extra descriptors for external pins.

State and persistence: static DMA, device, and interrupt metadata persists after registration. `plat_mem_setup()` adds node 1 for `0xe55f0000-0xe5610000`. INTC mask/prio registers and DMA controller state are hardware-backed.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh_spi`, `rspi`, `sh-dma-engine`, `sh_ehci`, `ohci-platform`, SH PFC for pin modes, and the INTC core.

Risks: the four DMA engines share some IRQs and use `IORESOURCE_IRQ_SHAREABLE`, making interrupt routing sensitive. External IRQ mode selection writes ICR0 bits directly. URAM node bounds are fixed and must not overlap RAM maps.

Test signals: test DMA clients across each engine, SPI and RSPI transfers, EHCI/OHCI enumeration, early console/timers, all external IRQ/IRL pin modes, and memory node registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7757.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7763.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7763.c

Purpose: defines SH7763 platform devices and interrupt controllers for serial, RTC, USB host/function, and timers.

Important APIs, types, and functions: `sh7763_devices_setup()` registers SCIF0-2, RTC, OHCI, SH UDC, and TMU0/1. `plat_early_device_setup()` exposes serial and timers early. `plat_irq_setup()` registers the main descriptor. `plat_irq_setup_pins()` supports combined IRQ mode and IRL7654/3210 modes with optional mask descriptors.

Control flow: device arrays split normal and early registration. Interrupt setup initially disables IRQ and IRL groups, selects IRL mode, and registers the base descriptor. Board code can choose external pin mode later.

State and persistence: static platform resources include SCIF FIFO-data register type, RTC IRQs, USB MMIO/IRQ resources, and timer channels. INTC mask/prio/sense/ack state is hardware-backed.

Dependencies and integration points: integrates with `sh-sci`, `sh-rtc`, `ohci-platform`, `sh_udc`, `sh-tmu`, PFC-selected external IRQ pins, and SuperH INTC.

Risks: USB host and function controllers share SoC USB resources and need board-level power/PHY setup outside this file. Direct IRQ-mode writes assume specific ICR0 layout. No `plat_mem_setup()` is present for extra nodes.

Test signals: verify SCIF FIFO operation, USB OHCI and gadget modes, RTC interrupts, TMU clocksource/events, and external interrupt behavior in IRQ and IRL modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7763.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7770.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7770.c

Purpose: supplies SH7770 platform-device setup for ten SCIF ports, three TMU blocks, and interrupt descriptors with selectable external IRQ/IRL modes.

Important APIs, types, and functions: `sh7770_devices_setup()` registers SCIF0-9 and TMU0-2; `plat_early_device_setup()` registers the same early-capable serial/timer set; `plat_irq_setup()` and `plat_irq_setup_pins()` configure the main and external interrupt controllers.

Control flow: SCIF ports use adjacent MMIO blocks `0xff923000-0xff92c000` with event codes `0x9a0-0xac0`; TMU blocks cover `0xffd80000`, `0xffd81000`, and `0xffd82000`. Interrupt setup disables external groups, selects IRL mode by default, registers the main descriptor, then allows board-selected IRQ or IRL descriptors.

State and persistence: platform-device metadata is static. INTC state persists in mask/prio/sense/ack registers. No additional memory node state is registered.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, SH PFC/board pin selection, and SuperH INTC. The external IRL descriptor names include `sh7780-irl*`, likely copied from SH7780.

Risks: many similar SCIF resources increase copy/paste risk. The descriptor names for IRL modes referencing `sh7780` could confuse diagnostics. IRQ mode writes are hard-coded to ICR0 bits.

Test signals: boot should show ten usable serial devices and three timer blocks; external IRQ/IRL board modes should register with expected names and deliver interrupts; timer interrupts should map to correct event codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7780.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7780.c

Purpose: registers SH7780 serial, timer, RTC, and two DMA engine devices, plus interrupt setup for internal and external IRQ/IRL sources.

Important APIs, types, and functions: `sh7780_devices_setup()` registers SCIF0-1, TMU0-1, RTC, and DMA0-1. `plat_early_device_setup()` adjusts SCIF clock-enable bits when `CONFIG_SH_TIMER_TMU` is disabled, then registers early devices. `plat_irq_setup()` and `plat_irq_setup_pins()` configure INTC modes.

Control flow: static DMA channel/pdata/resources describe two DMA controllers, one with DMARS and one without. Early setup exposes serial/timer devices; normal init adds all platform devices. Interrupt setup defaults to IRL mode and optional board selection enables IRQ or maskable IRL descriptors.

State and persistence: static platform data persists. The early setup may mutate `scif0_platform_data.scscr` and `scif1_platform_data.scscr` by clearing `SCSCR_CKE1` when TMU is not selected. DMA and INTC state live in MMIO.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh-rtc`, `sh-dma-engine`, and SuperH INTC. Clocking behavior depends on timer configuration.

Risks: conditional SCIF clock-bit mutation can affect serial timing. Shared DMA IRQ resources require careful driver handling. External IRQ pin modes are board-selected and direct-register based.

Test signals: validate serial operation with and without TMU config, DMA transfers on both controllers, RTC interrupts, TMU events, and all external IRQ/IRL mode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7785.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7785.c

Purpose: provides SH7785 device and interrupt setup for six SCIF ports, two TMU blocks, two DMA engines, and an optional URAM node.

Important APIs, types, and functions: `sh7785_devices_setup()` registers SCIF0-5, TMU0-1, and DMA0-1. `plat_early_device_setup()` exposes serial/timers early. `plat_irq_setup()` and `plat_irq_setup_pins()` configure main and external interrupt descriptors. `plat_mem_setup()` registers URAM as Node 1.

Control flow: SCIF resources use `SCIx_SH4_SCIF_FIFODATA_REGTYPE` and `SCSCR_REIE | SCSCR_CKE1`. DMA0 has DMARS resources, while DMA1 does not. Interrupt setup supports separate IRQ0123/IRQ4567 and IRL0123/IRL4567 descriptors.

State and persistence: device metadata is static; `plat_mem_setup()` registers `0xe55f0000-0xe5610000` as bootmem node 1. INTC and DMA runtime state lives in hardware.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh-dma-engine`, PFC/board external pin setup, and SuperH INTC.

Risks: DMA1 lacking DMARS must match driver expectations. URAM registration must align with memory maps. External pin mode setup directly toggles ICR0 and mask registers.

Test signals: SCIF0-5 console/TTY tests, DMA transfer tests on both engines, timer interrupts, `/proc/iomem` node visibility for URAM, and external IRQ/IRL mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7785.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7786.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7786.c

Purpose: implements SH7786 platform setup for serial, timers, DMA, USB EHCI/OHCI, complex interrupt distribution, optional SCIF1 IRQ demux, and USB PHY initialization.

Important APIs, types, and functions: `sh7786_usb_setup()` performs USB register initialization and PHY/PLL polling. `sh7786_devices_setup()` runs USB setup, optionally replaces SCIF1 resources with demuxed IRQs using `intc_irq_lookup()`, registers early devices, then normal devices. `plat_early_device_setup()`, `plat_irq_setup()`, `plat_irq_setup_pins()`, and `plat_mem_setup()` provide platform hooks.

Control flow: early devices include SCIF0-5 and TMU0-3. Normal devices include DMA0 and USB host controllers. The main INTC descriptor maps internal sources including WDT, TMUs, DMAC, HUDI, HPB, SCIF, Ethernet, PCIe, USB, I2C, display, SSI, HAC, FLCTL, HSPI, GPIO, thermal, and inter-CPU interrupts. IRQ pin setup supports IRQ/IRL 3210 and 7654 modes. SCIF1 starts with a single IRQ, but after the main INTC is registered the device setup can install separate ERI/RXI/TXI/BRI IRQ resources.

State and persistence: USB setup writes persistent initial values to USBINIT registers and controls PHY/PLL bits. `sh7786_intc_desc` includes SMP balancing distribution registers. Platform device metadata can be mutated for SCIF1 demuxing. `plat_mem_setup()` is empty.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh-dma-engine`, `sh_ehci`, `ohci-platform`, INTC SMP balancing, PFC/board external pins, and USB PHY hardware.

Risks: USB setup has a busy wait without timeout reporting if PLL never locks. SCIF1 demux depends on `intc_irq_lookup()` after descriptor registration. SMP interrupt distribution register masks must match CPU count. Re-registering early devices in `sh7786_devices_setup()` can conflict if call ordering changes.

Test signals: USB EHCI/OHCI enumeration and PHY lock log, SCIF1 interrupt demux behavior, TMU0-3 interrupts, DMA transfer tests, Ethernet/PCIe/USB interrupt delivery, SMP IPI distribution, and external IRQ/IRL mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7786.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-shx3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-shx3.c

Purpose: supplies SH-X3 prototype CPU setup for SCIF, TMU, interrupt controllers, external IRQ/IRL pin modes, and extra memory nodes.

Important APIs, types, and functions: `shx3_devices_setup()` registers early devices as normal platform devices. `plat_early_device_setup()` adds SCIF0-2 and TMU0-1 for early use. `plat_irq_setup()` registers the main descriptor; `plat_irq_setup_pins()` configures GPIO-backed IRQ mode or IRL modes; `plat_mem_setup()` registers URAM/CSM bootmem nodes.

Control flow: static resources define SCIF0-2 with four IRQs each and TMU0-1. Interrupt tables cover TMU, SCIF, DMAC, CSM, H8EX, FE, HUDI, DMAC groups, and inter-CPU interrupt controller lines. `plat_irq_setup_pins()` requests GPIO function pins for IRQ mode before registering `intc_desc_irq`; IRL modes use mask registers and optional descriptors.

State and persistence: static platform data persists in devices. `plat_mem_setup()` registers CPU0 URAM `0x145f0000-0x14610000` and CSM `0x16000000-0x16020000`; additional CPU URAM nodes are present but disabled with `#if 0`. INTC distribution state uses `INT2DISTCR*` registers.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, PFC GPIO function requests, SH-X3 clock setup, SH-X3 SMP support, and SuperH INTC with SMP balancing.

Risks: prototype hardware and disabled CPU1-3 URAM nodes indicate incomplete SMP memory modeling. GPIO requests can fail, leaving IRQ mode unregistered. Early and normal registration use the same device list, requiring stable platform ordering.

Test signals: early console, TMU timekeeping, external IRQ mode GPIO requests, IRL modes, SMP IPI interrupts, `/proc/iomem` extra nodes, and interrupt balancing across CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-shx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/smp-shx3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/smp-shx3.c

Purpose: implements SH-X3 platform SMP operations: CPU discovery mapping, IPI request/handling, secondary CPU startup, CPU hotplug preparation, and CPU id lookup.

Important APIs, types, and functions: `shx3_smp_ops` exports `struct plat_smp_ops`. Key functions are `ipi_interrupt_handler()`, `shx3_smp_setup()`, `shx3_prepare_cpus()`, `shx3_start_cpu()`, `shx3_smp_processor_id()`, `shx3_send_ipi()`, `shx3_update_boot_vector()`, and `shx3_cpu_prepare()`. `register_shx3_cpu_notifier()` installs a CPU hotplug prepare state.

Control flow: SMP setup marks CPU0 possible and then naively marks CPUs up to `NR_CPUS` as possible. `prepare_cpus()` requests per-CPU IPI IRQs starting at 104 and marks CPUs present. Starting a CPU writes the reset vector to a per-CPU RESET register, stops the target via STBCR MSTP, then releases it with reset/light-sleep bits. IPIs write a message bit to per-CPU INTICI registers; the handler clears and dispatches the message to `smp_message_recv()`.

State and persistence: CPU maps `__cpu_number_map` and `__cpu_logical_map` are initialized. Hardware state lives in per-CPU STBCR/RESET registers and interrupt controller IPI registers. Hotplug prepare rewrites boot vectors before CPU bring-up.

Dependencies and integration points: integrates with Linux SMP, CPU hotplug (`cpuhp_setup_state_nocalls`), native SuperH CPU idle/death helpers, SH-X3 INTC vectors from setup files, and 29-bit vs physical address handling.

Risks: CPU count probing is intentionally absent; every `NR_CPUS` slot is marked possible, which can expose nonexistent CPUs. `BUG_ON(cpu >= 4)` in IPI send assumes hardware max 4. Startup loops can spin forever if STBCR bits do not update.

Test signals: boot should report expected secondary CPUs, CPU bring-up/hotplug should succeed, IPIs should deliver scheduler and TLB messages, `/proc/interrupts` should show IPI IRQs, and CPU id register reads should match logical maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/smp-shx3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/ubc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/ubc.c

Purpose: registers SH-4A on-chip User Break Controller support for hardware breakpoints.

Important APIs, types, and functions: `sh4a_ubc_init()` initializes hardware and calls `register_sh_ubc(&sh4a_ubc)` at `arch_initcall`. `sh4a_ubc_enable()`, `sh4a_ubc_disable()`, `sh4a_ubc_enable_all()`, `sh4a_ubc_disable_all()`, `sh4a_ubc_active_mask()`, `sh4a_ubc_triggered_mask()`, and `sh4a_ubc_clear_triggered_mask()` implement `struct sh_ubc`.

Control flow: init optionally obtains clock `ubc0`, enables it if present, clears the breakpoint control register, initializes each of two channels by clearing CAMR/CBR, programming CRR with break interrupt and PC break bits, performs dummy reads for posting, disables the clock, stores it in the UBC descriptor, and registers the backend.

State and persistence: `sh4a_ubc` advertises two events and trap number `0x1e0`. Breakpoint state persists in UBC channel registers CBR/CRR/CAR/CAMR and the common match flag register. The optional clock pointer is retained for later core use.

Dependencies and integration points: depends on Linux clock API, raw MMIO, and `<asm/hw_breakpoint.h>`. It integrates with ptrace/perf hardware breakpoint infrastructure through `register_sh_ubc()`.

Risks: `clk_enable(NULL)` and `clk_disable(NULL)` rely on clock API tolerance when no `ubc0` clock exists. Triggered-mask clearing writes `read & ~mask`, which must match hardware write semantics. Only two channels are exposed.

Test signals: hardware watchpoint/breakpoint tests through ptrace or perf should hit trap `0x1e0`, active and triggered masks should reflect channels, and platforms without `ubc0` should still boot without clock errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/ubc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/Makefile

Purpose: declares build objects for the Linux/SuperH SH-Mobile backend directory.

Important APIs, types, and functions: this is Kbuild metadata, not C code. `obj-$(CONFIG_PM) += pm.o sleep.o` includes power-management and sleep support when PM is enabled. `obj-$(CONFIG_CPU_IDLE) += cpuidle.o` includes CPU idle support when configured.

Control flow: during kernel build, Kbuild evaluates the configuration symbols and compiles/link these backend objects into the SH-Mobile CPU support area.

State and persistence: no runtime state. Build outputs persist as object files and linked kernel code depending on configuration.

Dependencies and integration points: integrates SH-Mobile PM, sleep, and cpuidle source files with the architecture build. Setup files such as SH7724 depend on SH-Mobile sleep notifier infrastructure when PM code is enabled.

Risks: missing `CONFIG_PM` omits sleep notifier support required by SoC-specific suspend paths. Missing `CONFIG_CPU_IDLE` excludes idle driver support. The Makefile intentionally has no per-SoC selection logic, so source files must guard their own dependencies.

Test signals: configuration/build tests should verify `pm.o` and `sleep.o` appear with PM and `cpuidle.o` appears with CPU idle; SH-Mobile suspend and cpuidle runtime tests validate the selected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/Makefile -->

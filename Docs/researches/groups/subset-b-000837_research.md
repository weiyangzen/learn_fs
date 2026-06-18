# subset-b-000837 research

This grouped report covers the requested SuperH SH2A, SH3, SH4, and SH4A CPU backend files from the Ceph client source snapshot. Each file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7206.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7206.c

## Purpose
`setup-sh7206.c` describes the SH7206 on-chip interrupt controller and early/normal platform devices for serial ports and timers. It is board-independent CPU setup glue that lets generic SH platform code discover SCIF, CMT, and MTU2 resources before and after normal driver init.

## Important APIs, Types, And Functions
The file defines INTC source enums, `vectors`, `groups`, `prio_registers`, `mask_registers`, and `DECLARE_INTC_DESC(intc_desc, "sh7206", ...)`. Platform resources include four `sh-sci` SCIF devices, an `sh-cmt-16` device with `channels_mask = 3`, and an `sh-mtu2s` device. Key functions are `sh7206_devices_setup()`, `plat_irq_setup()`, and `plat_early_device_setup()`.

## Control Flow
At `arch_initcall`, `platform_add_devices()` registers the full device list. During interrupt setup, `plat_irq_setup()` registers the SH7206 INTC descriptor. During early boot, `plat_early_device_setup()` clears clock-stopping bits in `STBCR4` for CMT and `STBCR3` for MTU2, then calls `sh_early_platform_add_devices()` for early console and timer availability.

## State And Persistence
Persistent state is hardware-facing: INTC priority/mask programming and standby-control register writes that enable timer clocks. Device state is static `__initdata` and platform-resource metadata consumed by drivers; no filesystem state exists.

## Dependencies And Integration Points
It depends on the SH intc layer, `platform_device`, `serial_sci`, `sh_timer`, raw MMIO access, and `asm/platform_early.h`. IRQ numbers and MMIO addresses are consumed by the `sh-sci`, `sh-cmt-16`, and `sh-mtu2s` drivers.

## Risks
Wrong vector numbers, priority-register bit positions, or standby bits can make interrupts or clocksource devices fail very early. The MTU device name differs from later SH726x files (`sh-mtu2s`), so driver binding must match that subtype.

## Test Signals
Useful signals are boot logs showing early console/timer registration, `/proc/interrupts` entries for SCIF/CMT/MTU events, and successful timer tick/serial interrupt operation on SH7206 hardware or emulator support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7206.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7264.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7264.c

## Purpose
`setup-sh7264.c` provides SH7264 interrupt routing and on-chip platform-device registration. It exposes eight SCIF ports, CMT, MTU2, RTC, and the on-chip R8A66597 USB host to generic Linux drivers.

## Important APIs, Types, And Functions
The file defines a large INTC map with grouped PINT and per-port SCIF interrupt groups, `DECLARE_INTC_DESC(intc_desc, "sh7264", ...)`, eight `plat_sci_port` objects using `SCIx_SH2_SCIF_FIFODATA_REGTYPE`, CMT/MTU/RTC resources, `r8a66597_platdata`, and `usb_port_power()`. Public setup hooks are `sh7264_devices_setup()`, `plat_irq_setup()`, and `plat_early_device_setup()`.

## Control Flow
Normal device registration happens through `arch_initcall(sh7264_devices_setup)`. `plat_irq_setup()` registers the INTC descriptor. Early boot registers SCIF0-7, CMT, and MTU2 only; RTC and USB host wait for normal platform init. `usb_port_power()` is handed to the USB host platform data and writes UACS25 when the HCD toggles port power.

## State And Persistence
State is static platform-resource description plus hardware configuration in INTC priority/mask registers and a USB control register. No persistent storage is used. The USB host advertises `dma_mask = NULL`, explicitly indicating no DMA use.

## Dependencies And Integration Points
The code integrates with `sh-sci`, `sh-cmt-16`, `sh-mtu2`, `sh-rtc`, and `r8a66597_hcd`. It relies on `linux/sh_intc` macros through the platform headers and raw I/O for USB power control.

## Risks
The dense interrupt table has high off-by-one risk, especially SCIF BRI/ERI/RXI/TXI ordering. The hard-coded USB power write is board/SoC specific and can break host bring-up if the address or bit differs. Early devices omit USB/RTC, so console and timer must not depend on them.

## Test Signals
Boot should show eight SCI ports and CMT/MTU timers registered, RTC appearing after platform init, and R8A66597 HCD probing on IRQ 170. Interrupt counters for grouped SCIF events and USB low-trigger IRQs are the main runtime evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7269.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7269.c

## Purpose
`setup-sh7269.c` is the SH7269 counterpart to SH7264 setup. It registers the SoC interrupt map and platform devices for eight SCIF ports, CMT, MTU2, RTC, and R8A66597 USB host using SH7269-specific MMIO addresses and event numbers.

## Important APIs, Types, And Functions
Important data includes `vectors`, SCIF/PINT `groups`, `prio_registers`, `mask_registers`, and `DECLARE_INTC_DESC(intc_desc, "sh7269", ...)`. Devices are SCIF0-7 using FIFO-data register layout, `sh-cmt-16`, `sh-mtu2`, `sh-rtc`, and `r8a66597_hcd`. Setup hooks are `sh7269_devices_setup()`, `plat_irq_setup()`, and `plat_early_device_setup()`.

## Control Flow
`arch_initcall` registers the full platform-device set. Early setup registers serial and timer devices for boot console and clockevent use. INTC registration is one call to `register_intc_controller(&intc_desc)`.

## State And Persistence
All state is hardware metadata and static init-time structures. The USB host uses on-chip, endian-aware platform data and no DMA mask. There is no runtime persistence beyond driver-owned device state after registration.

## Dependencies And Integration Points
The file connects the CPU backend with serial, timer, RTC, USB HCD, and interrupt-controller subsystems. It uses `DEFINE_RES_MEM`, `DEFINE_RES_IRQ`, named MTU IRQ resources, and raw platform IRQ numbers rather than `evt2irq()`.

## Risks
SH7269 moves SCIF MMIO to the `0xe800xxxx` range and shifts many interrupt numbers versus SH7264; copy/paste drift would produce silent driver misbinding or dead interrupts. The VDC4 vector table includes repeated event entries, so interrupt behavior should be checked against the hardware manual.

## Test Signals
Probe logs for `sh-sci.0` through `.7`, active CMT/MTU clocksource events, RTC IRQ 338, and USB HCD IRQ 170 are the practical validation points. Serial loopback and USB enumeration are strong integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7269.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/Makefile

## Purpose
The SH3 `Makefile` selects CPU-family core objects and subtype-specific setup, serial, clock, hibernation, and pinmux objects.

## Important APIs, Types, And Functions
It always builds `ex.o`, `probe.o`, `entry.o`, and `setup-sh3.o`. It conditionally adds `swsusp.o`, subtype setup and serial files for SH7705/7706/7707/7708/7709/7710/7712/7720/7721, clock implementations through `clock-y`, and `pinmux-sh7720.o` when `CONFIG_GPIOLIB` and `CONFIG_CPU_SUBTYPE_SH7720` are enabled.

## Control Flow
Kbuild expands `obj-*` and `clock-*` variables from Kconfig symbols. Later assignments to `clock-$(...) := ...` select exactly one primary clock file for the configured subtype, then `obj-y += $(clock-y)` links it into the CPU backend.

## State And Persistence
The file has no runtime state. Its build-state effect is the linked kernel image contents.

## Dependencies And Integration Points
It integrates SH3 Kconfig choices with architecture code. SH4 reuses SH3 `entry.o`, `ex.o`, and `swsusp.o`, so changes here can affect shared low-level code availability.

## Risks
Incorrect object selection can leave a configured CPU without setup or clock support. The SH7720 clock mapping deliberately reuses `clock-sh7710.o`, which is easy to misread as an omission.

## Test Signals
Build coverage for each `CONFIG_CPU_SUBTYPE_*` choice is the primary signal. Link errors for missing `plat_*` hooks, `arch_init_clk_ops`, or serial ops indicate selection regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh3.c

## Purpose
`clock-sh3.c` provides generic SH3 clock-ops for older SH3 parts by decoding the `FRQCR` frequency-control register into master, module/peripheral, bus, and CPU clock rates.

## Important APIs, Types, And Functions
It defines divisor/multiplier tables for STC, IFC, and PFC fields. Clock callbacks are `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `cpu_clk_recalc()`, and exported init hook `arch_init_clk_ops()`.

## Control Flow
Clock framework code calls `arch_init_clk_ops(ops, idx)`. If `idx` is in range, it receives one of the four `sh_clk_ops`. Each callback reads `FRQCR` with `__raw_readw()`, computes an index from scattered bitfields, and scales the parent or current rate.

## State And Persistence
No state is stored beyond initializing `clk->rate` in master init. The authoritative state is the hardware `FRQCR` register.

## Dependencies And Integration Points
It depends on `asm/clock.h`, `asm/freq.h`, and raw I/O. It plugs into the legacy SH clock framework used by `arch/sh/kernel/cpu/clock.c`.

## Risks
FRQCR bit extraction is SoC-sensitive; a wrong table or bit shift gives every timer, serial, and bus consumer wrong rates. Unsupported table entries are filled with `1`, which can hide invalid strap values.

## Test Signals
Boot-time clock prints, serial baud accuracy, timer calibration, and comparing `/sys/kernel/debug/clk` or equivalent SH clock dumps to board oscillator settings validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7705.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7705.c

## Purpose
`clock-sh7705.c` supplies SH7705-specific clock operations. It is structurally the generic SH3 implementation with SH7705 FRQCR multiplier/divisor tables.

## Important APIs, Types, And Functions
Key objects are `stc_multipliers`, `ifc_divisors`, `pfc_divisors`, four `sh7705_*_clk_ops`, and `arch_init_clk_ops()`.

## Control Flow
The callbacks read `FRQCR`, derive the same combined index fields as generic SH3, and scale master, module, bus, and CPU rates. `arch_init_clk_ops()` selects the requested callback by index for the common clock setup code.

## State And Persistence
Runtime state is only the calculated rate stored in `struct clk` by the clock framework. Hardware state stays in `FRQCR`.

## Dependencies And Integration Points
It integrates SH7705 with the legacy SH clock framework and feeds rates to serial, TMU, RTC, and peripheral drivers selected by `setup-sh7705.c`.

## Risks
SH7705-specific tables include non-linear ratios and reserved entries; using generic SH3 tables would produce incorrect baud/timer rates. There is no range validation beyond array bounds.

## Test Signals
Expected CPU/bus/peripheral rates from boot messages, correct SCIF baud generation, and stable TMU tick rate are the most direct validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7705.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7706.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7706.c

## Purpose
`clock-sh7706.c` defines clock operations for SH7706-class CPUs by decoding `FRQCR` with SH7706-specific divisor tables.

## Important APIs, Types, And Functions
It provides static ratio tables and `sh7706_master_clk_ops`, `sh7706_module_clk_ops`, `sh7706_bus_clk_ops`, `sh7706_cpu_clk_ops`, selected by `arch_init_clk_ops()`.

## Control Flow
The SH clock core asks for operations by index. Each callback reads `FRQCR`, extracts PFC/STC/IFC selection bits, and calculates child rates from the parent clock.

## State And Persistence
The implementation is stateless except for `struct clk` rate mutation during master init. Hardware register values remain the source of truth.

## Dependencies And Integration Points
It is selected by the SH3 Makefile for `CONFIG_CPU_SUBTYPE_SH7706`. Its outputs drive common timing and serial consumers configured by `setup-sh770x.c`.

## Risks
Reserved divisor entries are represented as fallback values, so invalid strap/register settings may look plausible. Any mismatch with setup code or board oscillator setup affects all timekeeping.

## Test Signals
Compile coverage for SH7706 plus boot-time clock rate checks, serial baud tests, and timer drift tests show whether the tables match the hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7706.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7709.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7709.c

## Purpose
`clock-sh7709.c` implements SH7709 clock decoding for CPU, bus, module, and master clocks.

## Important APIs, Types, And Functions
Important pieces are the SH7709 STC/IFC/PFC tables, the four `sh7709_*_clk_ops`, and `arch_init_clk_ops()`.

## Control Flow
Clock callbacks read `FRQCR`, combine high and low selector bits, and divide/multiply parent rates according to SH7709 ratios. The operation pointer array is exposed through `arch_init_clk_ops()`.

## State And Persistence
No persistent kernel state is introduced. Calculated rates live in the clock framework and depend on current `FRQCR`.

## Dependencies And Integration Points
The file is selected for `CONFIG_CPU_SUBTYPE_SH7709` and is paired with `setup-sh770x.c` and `serial-sh770x.c`.

## Risks
SH7709 allows ratios such as 3 and 6 that differ from neighboring SH3 parts. Timer and serial failures are likely if the wrong subtype clock object is linked.

## Test Signals
Clock rate logs, SCIF baud validation, and TMU tick accuracy on SH7709 boards provide coverage. Kbuild subtype matrix tests catch accidental selection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7709.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7710.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7710.c

## Purpose
`clock-sh7710.c` supplies SH7710 and SH7720-family clock operations based on mode/divider tables rather than the older SH770x scattered FRQCR selectors.

## Important APIs, Types, And Functions
It defines `md_table`, `master_clk_init()`, module/bus/CPU recalc callbacks, `sh7710_*_clk_ops`, and `arch_init_clk_ops()`.

## Control Flow
`master_clk_init()` reads the mode pins or frequency-control state through the SH frequency definitions and adjusts the root rate. The recalc callbacks use table lookups for module, bus, and CPU divisors. The common SH clock layer obtains callbacks through `arch_init_clk_ops()`.

## State And Persistence
State is limited to calculated `struct clk` rates. Hardware mode/frequency registers remain authoritative.

## Dependencies And Integration Points
It is selected for SH7710 and reused for SH7720 in the Makefile. Consumers include serial and timer devices from `setup-sh7710.c` and `setup-sh7720.c`.

## Risks
Because SH7720 also maps to this file, changes intended for SH7710 can regress SH7720 clocks. Table ordering must match hardware mode encodings.

## Test Signals
SH7710 and SH7720 build/boot coverage, timer calibration, and serial baud tests are the primary signals. Cross-check expected clock ratios from board manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7712.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7712.c

## Purpose
`clock-sh7712.c` provides SH7712-specific clock callbacks with compact multiplier and divisor tables.

## Important APIs, Types, And Functions
It defines `multipliers`, `divisors`, `master_clk_init()`, `module_clk_recalc()`, `cpu_clk_recalc()`, `sh7712_*_clk_ops`, and `arch_init_clk_ops()`. It does not define a separate bus clock callback.

## Control Flow
The SH clock framework requests ops by index. Master init and recalc callbacks read hardware frequency control fields and apply the SH7712 ratio tables. Missing indexes are ignored by the bounds check in `arch_init_clk_ops()`.

## State And Persistence
The file stores no runtime state; rates are derived from hardware registers and stored by the clock framework.

## Dependencies And Integration Points
It is selected for `CONFIG_CPU_SUBTYPE_SH7712` while setup/serial code reuses SH7710 files. It feeds clocks to those shared devices.

## Risks
The reduced operation set means callers must tolerate no bus-specific callback. Incorrect index mapping will miscompute CPU/module rates without immediate build failure.

## Test Signals
Boot rate output, serial baud, and timer drift on SH7712 hardware validate the implementation. Build coverage checks that shared setup still links with this clock file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/clock-sh7712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/entry.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/entry.S

## Purpose
`entry.S` is the SH3 low-level exception, TLB miss, syscall/interrupt return, and register save/restore path. It owns the VBR layout used when the CPU enters kernel mode from faults or interrupts.

## Important APIs, Types, And Functions
Exported entry labels include `tlb_miss_load`, `tlb_miss_store`, `initial_page_write`, `tlb_protection_violation_*`, `address_error_*`, `restore_regs`, `save_regs`, `save_low_regs`, `handle_interrupt`, `exception_none`, and `vbr_base`. It includes `../../entry-common.S` for common return/syscall logic.

## Control Flow
TLB miss entries set a fault code and call `handle_tlbmiss()`, falling back to `do_page_fault()` on failure. General exceptions enter at VBR offset `0x100`, call `prepare_stack()`, save registers, look up `exception_handling_table`, and jump to the handler with `ret_from_exception` as return. Interrupts enter at `0x600`, save state, derive IRQ from `INTEVT`, call `do_IRQ()` for valid hard IRQs, or dispatch special events like NMI through the exception table.

## State And Persistence
The code persists process-visible register state on the kernel stack in the layout expected by ptrace and signal code. It manipulates SR bank, BL/RB/IMASK bits, SSR/SPC, PR, GBR, MACH/MACL, and banked registers.

## Dependencies And Integration Points
It depends on `asm-offsets.h`, thread-info layout, MMU context definitions, `entry-macros.S`, C handlers such as `handle_tlbmiss`, `do_page_fault`, `do_address_error`, `do_IRQ`, and the exception table from `ex.S`.

## Risks
This code is extremely ABI-sensitive: stack layout changes must match ptrace/signal offsets. Delay-slot and bank switching errors can corrupt register state. Interrupt masking logic directly affects IRQ tracing and preemption behavior.

## Test Signals
Signals include successful boot to userspace, syscall tests, page-fault/COW tests, IRQ load tests, ptrace register validation, and hibernation or exception stress on SH3/SH4 paths that reuse this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/ex.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/ex.S

## Purpose
`ex.S` builds the SH3 exception dispatch table consumed by `entry.S`.

## Important APIs, Types, And Functions
It defines fallback aliases from many exception labels to `exception_error` when optional features are not present, aliases KGDB and FPU handlers conditionally, and exports `exception_handling_table`.

## Control Flow
`entry.S` converts the exception event code into an offset and indexes `exception_handling_table`. The table entries point to concrete handlers such as TLB miss handlers, address-error handlers, TRAPA/syscall logic from common entry code, optional FPU/KGDB handlers, or `exception_none`/`exception_error`.

## State And Persistence
There is no mutable state. The table is static dispatch data linked into the low-level exception path.

## Dependencies And Integration Points
It depends on symbols provided by `entry.S`, common SH exception code, KGDB, and FPU trap code depending on configuration. SH4 also reuses this table through its Makefile.

## Risks
Table order must match hardware exception vector encoding and `entry.S` indexing. Wrong fallback aliases can turn recoverable faults into fatal `exception_error` paths or mask unsupported features incorrectly.

## Test Signals
Exception-path smoke tests, syscall/TRAPA tests, KGDB trap tests when configured, and page-fault tests validate that the dispatch table points to the expected handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/ex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/pinmux-sh7720.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/pinmux-sh7720.c

## Purpose
`pinmux-sh7720.c` registers the SH7720 PFC/pinmux device when gpiolib support is enabled.

## Important APIs, Types, And Functions
It defines `sh7720_pfc_resources` for the PFC register window, and `plat_pinmux_setup()` which registers a `platform_device` named for the SH PFC driver.

## Control Flow
At `arch_initcall`, `plat_pinmux_setup()` creates the PFC platform device with its MMIO resource. The pinctrl/GPIO driver later binds and exposes pin configuration.

## State And Persistence
The file has no runtime state beyond static resources. Hardware pin function state is managed by the bound PFC driver.

## Dependencies And Integration Points
It is selected by the SH3 Makefile for SH7720 with `CONFIG_GPIOLIB`. It integrates with the SuperH PFC/pinmux subsystem and board-level pin requests.

## Risks
Wrong resource bounds prevent pinmux register access. If this object is omitted, device drivers may probe but fail to acquire required pin functions.

## Test Signals
Boot logs for PFC registration, GPIO enumeration, and successful pin configuration for SH7720 serial/USB/board peripherals provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/pinmux-sh7720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/probe.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/probe.c

## Purpose
`probe.c` identifies SH3 CPU subtypes and initializes `boot_cpu_data` cache geometry and feature flags.

## Important APIs, Types, And Functions
The file exports `cpu_probe()`. It reads CPU version registers, assigns `boot_cpu_data.type`, family, cache way/sets/line details, and flags such as MMU/FPU/DSP support according to detected subtype.

## Control Flow
During architecture CPU setup, `cpu_probe()` reads processor identification state, applies common SH3 defaults, switches on version/revision encodings, and updates per-CPU cache descriptors.

## State And Persistence
It mutates global boot CPU metadata used for cache management, feature checks, proc/cpuinfo, and architecture setup. No external persistence exists.

## Dependencies And Integration Points
It integrates with `asm/processor.h`, `asm/cache.h`, and the broader SH CPU initialization path. Cache and MMU code consume the populated fields.

## Risks
Misidentification causes wrong cache maintenance parameters and feature flags. Because many subtype IDs are old and close together, revision-specific handling is easy to regress.

## Test Signals
Boot CPU identification messages, correct `/proc/cpuinfo`, cache alias behavior, and successful boot on each SH3 subtype are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh770x.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh770x.c

## Purpose
`serial-sh770x.c` supplies SH770x-specific SCI/SCIF pin initialization callbacks for the `sh-sci` driver.

## Important APIs, Types, And Functions
The important export is `struct plat_sci_port_ops sh770x_sci_port_ops`, whose init hook configures serial pins according to UART port and termios flags.

## Control Flow
When a platform SCIF device from SH7705/SH770x setup is probed, `sh-sci` calls the port ops. The implementation chooses pin control behavior based on the port and requested line mode.

## State And Persistence
State is hardware pin function selection through SoC registers. The file itself has no independent storage.

## Dependencies And Integration Points
It is referenced by `setup-sh7705.c` and `setup-sh770x.c` via `plat_sci_port.ops`. It depends on `serial_core` structures and SH serial/pin helper definitions.

## Risks
Incorrect pin setup prevents console or UART operation even when MMIO/IRQ resources are correct. Control-line behavior can vary by board wiring.

## Test Signals
Early console output, runtime `ttySC*` transmit/receive tests, and hardware-flow-control tests where available validate the callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh770x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7710.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7710.c

## Purpose
`serial-sh7710.c` provides SH7710/SH7712 SCI port operations for the `sh-sci` platform data.

## Important APIs, Types, And Functions
It exports `sh7710_sci_port_ops` with a port pin-initialization routine used by the SH7710 setup file.

## Control Flow
The serial driver calls the ops during port initialization. The helper configures the SoC serial pins for the selected port and termios mode before normal UART operation.

## State And Persistence
Only pin-function hardware state is changed. There is no persistent software state.

## Dependencies And Integration Points
It is paired with `setup-sh7710.c` for both SH7710 and SH7712. It integrates with `linux/serial_core.h`, `linux/serial_sci.h`, and CPU pin definitions.

## Risks
Shared use for SH7710 and SH7712 means pin differences must be accurately represented. Incorrect pin setup can break console despite correct resource registration.

## Test Signals
Serial console boot, loopback, and flow-control tests on both SH7710 and SH7712 boards are the direct signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7720.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7720.c

## Purpose
`serial-sh7720.c` implements SH7720/SH7721 SCIF pin setup for serial ports used by the SH7720 setup file.

## Important APIs, Types, And Functions
It defines `sh7720_sci_init_pins()` and exports `struct plat_sci_port_ops sh7720_sci_port_ops`.

## Control Flow
`sh-sci` invokes `sh7720_sci_init_pins()` through platform data while initializing SCIF0 or SCIF1. The callback selects SoC pin functions appropriate to the port and `cflag`.

## State And Persistence
It changes pin-control hardware state but holds no software state. The serial driver owns runtime UART state.

## Dependencies And Integration Points
`setup-sh7720.c` assigns these ops in both SCIF platform-data structures. It depends on serial core data types and SH7720 pin definitions.

## Risks
SH7720 only exposes two SCIF devices here; wrong pin choices can collide with USB, MMC, or board functions. Termios-dependent hardware-control lines are a likely edge case.

## Test Signals
Boot console, `ttySC0`/`ttySC1` loopback, and board peripheral coexistence with configured pins validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/serial-sh7720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh3.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh3.c

## Purpose
`setup-sh3.c` contains common SH3 interrupt-pin setup shared by multiple SH3 subtypes. It handles external IRQ0-IRQ5 mode and priority setup that subtype files layer on top of.

## Important APIs, Types, And Functions
The key functions are `plat_irq_setup_sh3()` and `plat_irq_setup_pins()`. It defines common INTC vectors and priority/mask descriptors for IRQ pin handling.

## Control Flow
Subtype `plat_irq_setup()` functions register their SoC-specific controller and then call `plat_irq_setup_sh3()`. Board code can call `plat_irq_setup_pins(mode)` to configure IRQ pin mode and register additional external IRQ descriptors.

## State And Persistence
The file writes interrupt-control hardware registers for pin mode and registers static interrupt descriptors. There is no durable software state.

## Dependencies And Integration Points
It integrates with `linux/sh_intc.h`, IRQ mode constants, raw MMIO, and subtype setup files including SH7705, SH770x, SH7710, and SH7720.

## Risks
IRQ pin mode is board-sensitive. Unsupported modes intentionally `BUG()`, so bad board setup can halt boot. Shared use makes regressions broad across SH3 machines.

## Test Signals
External interrupt tests on IRQ0-IRQ5, boot without `BUG()`, and correct `/proc/interrupts` external IRQ entries validate this common setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7705.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7705.c

## Purpose
`setup-sh7705.c` registers SH7705 interrupt vectors and platform devices for two SCIF ports, TMU, and RTC.

## Important APIs, Types, And Functions
Important data includes `vectors`, `prio_registers`, `DECLARE_INTC_DESC(intc_desc, "sh7705", ...)`, `scif0_device`, `scif1_device`, `rtc_device`, `tmu0_device`, and setup hooks `sh7705_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
`arch_initcall` registers full platform devices. Early boot registers SCIF and TMU devices. `plat_irq_setup()` registers the subtype INTC descriptor and then calls common `plat_irq_setup_sh3()` for external IRQ pins.

## State And Persistence
The file contributes static resources and interrupt descriptors. Runtime hardware state is owned by the INTC, serial, TMU, and RTC drivers.

## Dependencies And Integration Points
It uses `sh770x_sci_port_ops`, `evt2irq()` event conversion, `sh-tmu-sh3`, `sh-rtc`, and the common SH3 interrupt-pin helper.

## Risks
SCIF device IDs and MMIO addresses are not numerically ordered by hardware naming, so driver aliases and console parameters must match. RTC resource bounds are small and IORESOURCE_IO-specific.

## Test Signals
Successful early console, TMU clockevent registration, RTC probe, and PINT/SCIF interrupt counts validate setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7705.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh770x.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh770x.c

## Purpose
`setup-sh770x.c` covers SH7706, SH7707, SH7708, and SH7709 platform setup. It conditionally describes subtype-specific vectors while registering SCI/SCIF, TMU, and RTC devices.

## Important APIs, Types, And Functions
It defines conditional INTC `vectors`/`prio_registers`, `intc_desc`, serial platform data using `sh770x_sci_port_ops`, `rtc_device`, `tmu0_device`, and hooks `sh770x_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
Compile-time `CONFIG_CPU_SUBTYPE_*` blocks select the right interrupt events and priority registers. Early setup registers serial and TMU. Normal init adds serial, TMU, and RTC. Interrupt setup registers subtype INTC and common SH3 pin handling.

## State And Persistence
No persistent storage is used. Static resource arrays become platform-device state; INTC registration programs interrupt metadata.

## Dependencies And Integration Points
The file ties `sh-sci`, `sh-tmu-sh3`, `sh-rtc`, `evt2irq()`, and common SH3 IRQ-pin setup to several closely related CPU subtypes.

## Risks
Heavy conditional compilation creates subtype coverage risk; a change may compile for one SH770x but not another. Event vectors for optional LCDC/PCC/PINT/SCIF blocks must match each subtype.

## Test Signals
Subtype build matrix coverage, boot probe logs, external IRQ/PINT testing, and serial/TMU runtime tests are required for confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh770x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7710.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7710.c

## Purpose
`setup-sh7710.c` supports SH7710 and SH7712 by registering interrupt mappings plus RTC, two SCIF ports, and TMU.

## Important APIs, Types, And Functions
The file defines `intc_desc`, `rtc_device`, `scif0_device`, `scif1_device`, `tmu0_device`, device arrays, and setup hooks `sh7710_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
Normal init adds all platform devices. Early init adds SCIF and TMU for console and clock use. IRQ setup registers SH7710 INTC and then common SH3 pin setup.

## State And Persistence
State is static device/interrupt description and hardware state in INTC and peripheral drivers. RTC capabilities include four-digit year through platform data.

## Dependencies And Integration Points
It depends on `sh7710_sci_port_ops`, `evt2irq()`, `sh-tmu-sh3`, `sh-rtc`, and common SH3 IRQ code. SH7712 reuses this setup through the Makefile.

## Risks
Shared setup for SH7710/SH7712 can miss subtype differences. SCIF IRQ ordering and register type must match the serial driver expectations.

## Test Signals
Boot on both subtypes, serial loopback, TMU tick stability, RTC probe, and IRQ-pin tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7720.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7720.c

## Purpose
`setup-sh7720.c` supports SH7720 and SH7721. It registers RTC, two SCIFs, OHCI USB host, SH UDC gadget, CMT, TMU, and a SoC-specific interrupt controller.

## Important APIs, Types, And Functions
Key devices are `rtc_device`, `scif0_device`, `scif1_device`, `usb_ohci_device`, `usbf_device`, `cmt_device`, and `tmu0_device`. INTC data includes `vectors`, `prio_registers`, and `DECLARE_INTC_DESC(intc_desc, "sh7720", ...)`. Hooks are `sh7720_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
Early boot registers SCIF, CMT, and TMU only. Normal `arch_initcall` registers the full list including RTC and USB devices. IRQ setup registers SH7720 INTC and then common SH3 external IRQ setup.

## State And Persistence
Static platform resources describe MMIO, IRQs, DMA masks, and RTC capabilities. Runtime state is held by bound USB, timer, RTC, and serial drivers.

## Dependencies And Integration Points
It uses `sh7720_sci_port_ops`, `usb_ohci_pdata`, `sh_timer_config`, `evt2irq()`, `sh_intc`, `asm/rtc.h`, and common SH3 IRQ setup. USB host/gadget drivers depend on the resources here.

## Risks
USB host/gadget share adjacent address space and separate IRQs; resource mistakes can cause probe conflicts. `CONFIG_CPU_SUBTYPE_SH7720` conditionally includes an SSL vector, so SH7721 builds need separate coverage. CMT uses an unusual low physical address resource.

## Test Signals
Early console and timer boot, OHCI enumeration, gadget controller probe, RTC operation, and `/proc/interrupts` entries for CMT/TMU/USB/SCIF validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/swsusp.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/swsusp.S

## Purpose
`swsusp.S` implements SH3/SH4 software suspend register save and resume restore paths.

## Important APIs, Types, And Functions
It exports `swsusp_arch_resume` and `swsusp_arch_suspend`, and uses global symbols `restore_pblist`, `swsusp_arch_regs_cpu0`, `swsusp_save`, `restore_regs`, `save_regs`, and `save_low_regs`.

## Control Flow
Resume sets the stack to saved architecture registers, walks `restore_pblist`, copies each saved page back to its original address, restores CPU registers with `restore_regs`, restores banked low registers, and returns with `rte`. Suspend sets up `spc` so resume returns through `swsusp_call_save`, saves banked and normal registers into `swsusp_arch_regs_cpu0`, restores the live stack/registers, and jumps to `swsusp_save()`.

## State And Persistence
It persists CPU register state in the hibernation architecture register block and copies image pages from restore buffers back into original physical pages. It manipulates SR/SSR/SPC, PR, banked registers, and stack pointers.

## Dependencies And Integration Points
It depends on hibernation core data structures, asm offsets for page backup entries, and the save/restore helpers from `entry.S`. SH4 builds include this file via the SH4 Makefile.

## Risks
Ordering is critical: restoring pages before registers and using the correct bank mode prevents corruption. Any mismatch with `SWSUSP_ARCH_REGS_SIZE` or PBE offsets can crash resume irrecoverably.

## Test Signals
The direct validation is successful hibernate/resume on SH3/SH4 hardware, with post-resume register, IRQ, timer, and userspace process state intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/swsusp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/Makefile

## Purpose
The SH4 `Makefile` selects common SH4 objects, reused SH3 low-level entry code, optional FPU/store-queue/perf support, subtype setup, and the generic SH4 clock file when not building SH4A.

## Important APIs, Types, And Functions
It always builds `probe.o` and `common.o`; `common-y` pulls `../sh3/entry.o` and `../sh3/ex.o`. Optional selections include `../sh3/swsusp.o`, `fpu.o`, `softfloat.o`, `sq.o`, `perf_event.o`, `setup-sh7750.o`, `setup-sh7760.o`, and `clock-sh4.o`.

## Control Flow
Kbuild expands objects from Kconfig symbols. Perf events are only selected for SH7750, SH7750S, and SH7091. `clock-sh4.o` is skipped when `CONFIG_CPU_SH4A` is set because SH4A has subtype clock files.

## State And Persistence
No runtime state; it controls linked kernel contents.

## Dependencies And Integration Points
It integrates SH4 Kconfig with shared SH3 assembly, SH4 FPU emulation, store queue module, PMU support, and platform setup files.

## Risks
Because SH4 reuses SH3 entry/exception/hibernate assembly, build changes here can affect both families. Conditional perf selection means some CPUs with counters may still use separate SH4A perf code.

## Test Signals
Build matrix coverage across SH7750 variants, SH7760, FPU on/off, hibernation, store queues, and perf events is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/clock-sh4.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/clock-sh4.c

## Purpose
`clock-sh4.c` implements generic SH4 clock operations for non-SH4A processors by decoding `FRQCR`.

## Important APIs, Types, And Functions
It defines IFC/BFC/PFC divisor tables, four `sh4_*_clk_ops`, and `arch_init_clk_ops()`.

## Control Flow
Clock callbacks read `FRQCR` and use low three-bit fields for module, bus, and CPU divisors. `master_clk_init()` multiplies the input rate by the peripheral divisor. `arch_init_clk_ops()` returns the callback set by index.

## State And Persistence
The file is stateless aside from clock rate updates in `struct clk`; `FRQCR` is the hardware source of truth.

## Dependencies And Integration Points
It integrates with the SH clock framework and setup files for SH7750/SH7760-class non-SH4A CPUs. Timer and serial drivers rely on the derived rates.

## Risks
Generic SH4 ratios do not apply to SH4A, which is why the Makefile excludes this file under `CONFIG_CPU_SH4A`. Wrong selection breaks baud and timekeeping globally.

## Test Signals
Boot clock logs, stable timer calibration, and serial baud tests on SH7750/SH7760 hardware validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/clock-sh4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/fpu.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/fpu.c

## Purpose
`fpu.c` saves/restores SH4 FPU context and handles FPU error traps for denormal/subnormal floating-point operations by emulating selected instructions.

## Important APIs, Types, And Functions
Important functions are `save_fpu()`, `restore_fpu()`, `denormal_to_double()`, `ieee_fpe_handler()`, `float_raise()`, `float_rounding_mode()`, and `BUILD_TRAP_HANDLER(fpu_error)`. It calls softfloat helpers such as `float64_mul`, `float32_div`, and `float64_to_float32`.

## Control Flow
Save/restore enables the FPU, moves FPUL/FPSCR and both FR banks through `frchg`, then disables the FPU. On an FPU trap, `fpu_error` unlazies current task FPU state, clears pending emulation flags, asks `ieee_fpe_handler()` to decode the faulting or delay-slot instruction, updates FPSCR cause/flag bits, restores FPU state, and returns unless enabled exceptions require `SIGFPE`.

## State And Persistence
Task FPU state persists in `tsk->thread.xstate->hardfpu`. Global `fpu_exception_flags` accumulates softfloat exception causes during one trap. The code manipulates hardware FPSCR/FPUL/FR registers.

## Dependencies And Integration Points
It integrates with lazy FPU ownership, SH trap handling, signal delivery, instruction decoding helpers, and `softfloat.c`.

## Risks
The file notes big-endian save/restore is untested. Delay-slot instruction decoding is subtle; wrong next-PC handling can skip or repeat instructions. FPSCR PR/FR bank handling must avoid undefined `frchg` behavior.

## Test Signals
FPU context-switch tests, signal-frame FP state tests, denormal add/sub/mul/div conversion tests, enabled-exception `SIGFPE` tests, and endian build coverage are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/perf_event.c

## Purpose
`perf_event.c` registers SH7750-style hardware performance counters with the generic SH perf infrastructure.

## Important APIs, Types, And Functions
It defines PMCR/PMCTR register macros, event maps `sh7750_general_events` and `sh7750_cache_events`, callbacks `sh7750_event_map()`, `sh7750_pmu_read()`, `sh7750_pmu_disable()`, `sh7750_pmu_enable()`, `*_all()`, `sh7750_pmu`, and `sh7750_pmu_init()`.

## Control Flow
At `early_initcall`, the file checks `boot_cpu_data.flags & CPU_HAS_PERF_COUNTER`. If present, it registers a two-counter `sh_pmu`. Perf core maps generic or cache events to PMCR PMM values, enables counters by clearing and programming PMCR, and reads a 48-bit count from high/low registers.

## State And Persistence
Hardware PMCR/PMCTR registers hold counter state. Software state is the static `sh_pmu` descriptor.

## Dependencies And Integration Points
It depends on `linux/perf_event.h`, raw MMIO, SH CPU feature probing, and `register_sh_pmu()`. The SH4 Makefile selects it for SH7750/SH7750S/SH7091 under perf events.

## Risks
Unsupported events use `-1` while zero-valued cache slots may mean unsupported or no event depending on core interpretation. Counter width composition and clear-on-enable behavior can affect sampling accuracy.

## Test Signals
`perf stat` for cycles/instructions/cache events, unsupported-event rejection, counter overflow behavior, and boot notice when counters are absent validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/probe.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/probe.c

## Purpose
`probe.c` identifies SH4 and SH4A CPU types, feature flags, cache geometry, and optional L2 cache properties.

## Important APIs, Types, And Functions
It exports `cpu_probe()`, reads `CCN_PVR`, `CCN_PRR`, and `CCN_CVR`, and populates `boot_cpu_data` fields including family, type, flags, cut version, icache/dcache/scache geometry, and special flags such as `CPU_HAS_PTEAEX`, `CPU_HAS_L2_CACHE`, `CPU_HAS_DSP`, and `CPU_HAS_PERF_COUNTER`.

## Control Flow
The function sets sane SH4 defaults, detects SH4A by PVR family, applies feature defaults, masks PVR to subtype ID, switches over PVR/PRR combinations, then refines cache geometry from CVR. Optional L2 is verified by CVR before scache fields are filled.

## State And Persistence
It mutates global boot CPU metadata used throughout architecture setup, cache maintenance, perf, FPU, and feature checks. There is no external persistence.

## Dependencies And Integration Points
It integrates with raw CCN register access, `asm/processor.h`, cache definitions, FPU/perf/store-queue users, and CPU subtype-specific setup.

## Risks
Misdetecting a CPU can select wrong cache maintenance, feature flags, or errata workarounds. The L2 size calculation comments note hardware/spec mismatch, so this path is hardware-sensitive.

## Test Signals
Boot CPU identification, `/proc/cpuinfo`, cache stress, FPU/perf availability, and L2 cache behavior on SH7785/SH7786/SH7723/SH7724 validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7750.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7750.c

## Purpose
`setup-sh7750.c` supports SH7091, SH7750, SH7750S, SH7750R, SH7751, and SH7751R platform devices and interrupt controllers.

## Important APIs, Types, And Functions
It defines RTC, SCI, SCIF, TMU0, optional TMU1 devices, multiple INTC descriptors (`intc_desc`, DMA4/DMA8, TMU34, IRLM, PCI), `sh7750_devices_setup()`, `plat_early_device_setup()`, `plat_irq_setup()` variants, and `plat_irq_setup_pins()`.

## Control Flow
Normal init registers SCI/SCIF depending on `mach_is_rts7751r2d()` and then adds timers/RTC. Early init similarly registers console serial devices and early timers. Compile-time subtype blocks select which interrupt descriptors `plat_irq_setup()` registers. `plat_irq_setup_pins(IRQ_MODE_IRQ)` enables IRLM on supported subtypes and registers IRL vectors.

## State And Persistence
Static platform data becomes driver state. Interrupt setup writes `INTC_ICR` for IRLM mode and registers descriptors for DMA, PCI, and timer interrupts. No disk state exists.

## Dependencies And Integration Points
It integrates with `sh-sci`, `sh-tmu`, `sh-rtc`, generated machine type helpers, SH INTC, and board-specific RTS7751R2D serial behavior.

## Risks
Many subtype conditionals make build and runtime coverage important. Calling IRQ pin setup on SH7750/SH7091 intentionally `BUG()`s because interrupts cannot be masked in that mode. Board-specific serial clock enable flags can affect early console.

## Test Signals
Subtype build tests, early console on RTS7751R2D and non-RTS boards, TMU/RTC probe, DMA/PCI IRQ delivery, and IRL pin-mode tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7760.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7760.c

## Purpose
`setup-sh7760.c` describes SH7760 interrupts and platform devices for four serial ports and TMU.

## Important APIs, Types, And Functions
Important data includes `vectors`, interrupt `groups`, `mask_registers`, `prio_registers`, `intc_desc`, `intc_desc_irq`, SCIF0-2 platform devices, a SIM-as-SCI port, `tmu0_device`, `sh7760_devices_setup()`, `plat_early_device_setup()`, `plat_irq_setup_pins()`, and `plat_irq_setup()`.

## Control Flow
`arch_initcall` adds serial and timer devices. Early setup registers the same set for console/timer availability. Base IRQ setup registers `intc_desc`; board IRQ pin setup can enable IRLM in `INTC_ICR` and register `intc_desc_irq`.

## State And Persistence
The file registers static resources and writes interrupt-control mode bits. Runtime device state is owned by serial and timer drivers.

## Dependencies And Integration Points
It uses SH INTC, `sh-sci`, `sh-tmu`, raw I/O, and `evt2irq()`. The SIM card module is intentionally exposed as `PORT_SCI` with only base registers because the serial driver lacks SIM-specific support.

## Risks
The comment that MFI vector differs from the data sheet is a red flag for hardware validation. SIM resource sizing is deliberate; expanding it could break `regshift` calculation. Unsupported IRQ pin modes `BUG()`.

## Test Signals
Serial probes for SCIF0-2 and SIM/SCI, TMU tick behavior, IRQ delivery for grouped SCIF/SIM/MMCIF/DMABRG interrupts, and IRQ pin mode tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7760.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/softfloat.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/softfloat.c

## Purpose
`softfloat.c` provides SH4-specific software floating-point helpers used by the FPU trap handler to emulate denormal/subnormal single- and double-precision operations.

## Important APIs, Types, And Functions
Exported helpers include `float64_sub`, `float32_sub`, `float32_add`, `float64_add`, `float64_div`, `float32_div`, `float32_mul`, `float64_mul`, `float64_to_float32`, `shift64RightJamming`, `shift32RightJamming`, `add128`, `sub128`, and `mul64To128`. It calls back to `float_raise()` and `float_rounding_mode()` in `fpu.c`.

## Control Flow
Public arithmetic functions unpack IEEE sign/exponent/fraction fields, normalize subnormal operands, choose add/sub paths based on signs, perform fixed-point significand arithmetic, round through `roundAndPackFloat32/64`, and raise FPSCR cause flags for overflow, underflow, inexact, or invalid operations.

## State And Persistence
The file has no global mutable state. It communicates exception state through `float_raise()` into `fpu.c` and consults current task FPSCR rounding mode.

## Dependencies And Integration Points
It is built with `fpu.o` under `CONFIG_SH_FPU`. It depends on SH FPSCR constants and `do_div()` for 64-bit division support.

## Risks
This is a modified SoftFloat subset, not a complete IEEE implementation. NaN handling is minimal in visible branches, and only SH4 rounding modes nearest/zero are supported. Arithmetic edge cases need direct tests.

## Test Signals
Denormal add/sub/mul/div tests, double-to-float conversion tests, FPSCR exception flag tests, divide-by-zero/invalid cases, and comparison with known IEEE results validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/softfloat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/sq.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/sq.c

## Purpose
`sq.c` implements the SH4 Store Queue mapping API, allowing physical I/O regions to be mapped into the store-queue address window and flushed efficiently.

## Important APIs, Types, And Functions
Public exports are `sq_flush_range()`, `sq_remap()`, and `sq_unmap()`. Internal state includes `struct sq_mapping`, `sq_mapping_list`, `sq_mapping_lock`, `sq_cache`, `sq_bitmap`, sysfs `mapping` attribute, CPU hotplug `sq_interface`, and module init/exit.

## Control Flow
`sq_api_init()` creates a slab cache, allocates a bitmap for the 64 MiB SQ window, and registers a CPU subsystem interface that creates per-CPU `sq` sysfs directories. `sq_remap()` validates non-RAM physical ranges, allocates a mapping, reserves bitmap pages, maps through `ioremap_page_range()` or QACR registers, logs the mapping, and links it. `sq_unmap()` finds the mapping, releases bitmap space, removes VM area on MMU builds, unlinks, and frees it. Sysfs writes map when length is nonzero and unmap when length is zero.

## State And Persistence
Mappings persist in kernel memory until explicit unmap or module exit. Hardware state includes QACR registers on no-MMU builds and store queue contents flushed by prefetch/barrier operations.

## Dependencies And Integration Points
It integrates with vmalloc/ioremap, bitmap allocation, slab, CPU sysfs, cache flush semantics, and `cpu/sq.h` address constants. Other drivers can call exported SQ APIs.

## Risks
`sq_unmap()` walks `sq_mapping_list` without taking the list lock until deletion, so concurrent sysfs/API access deserves scrutiny. Physical-address validation rejects normal RAM but relies on `high_memory`. Sysfs accepts raw hex input and can expose privileged footguns.

## Test Signals
Module init logs, sysfs mapping create/remove, driver SQ API use, concurrent map/unmap stress, no-MMU QACR behavior, and data-transfer flush correctness are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/sq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/Makefile

## Purpose
The SH4A `Makefile` selects subtype setup, clock, pinmux, SMP, perf, and hardware breakpoint support for SH4A CPUs.

## Important APIs, Types, And Functions
It maps CPU subtypes SH7757, SH7763, SH7770, SH7780, SH7785, SH7786, SH7343, SH7722, SH7723, SH7724, SH7734, SH7366, and SHX3 to setup objects. It maps the same family to clock objects, pinmux objects under `CONFIG_GPIOLIB`, `smp-shx3.o` under SMP, `perf_event.o`, and `ubc.o`.

## Control Flow
Kbuild selects exactly the objects matching Kconfig. Clock objects are always appended through `obj-y += $(clock-y)`, while pinmux/perf/ubc are gated by feature configs.

## State And Persistence
No runtime state; it controls link composition.

## Dependencies And Integration Points
It integrates SH4A Kconfig with setup, clock, pinmux, SMP, perf, and UBC subsystems. SH7786 and SHX3 also pull `intc-shx3.o`.

## Risks
Object selection errors are boot-critical because setup and clock files define required `plat_*` and `arch_clk_init` hooks. Pinmux gating by `CONFIG_GPIOLIB` can change board peripheral behavior.

## Test Signals
Subtype build matrix coverage, link checks for each CPU, and boot smoke tests per subtype validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7343.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7343.c

## Purpose
`clock-sh7343.c` registers the SH7343 clock tree, including root clocks, DLL/PLL, div4/div6 clocks, MSTP module-stop gates, and clkdev aliases.

## Important APIs, Types, And Functions
It defines `r_clk`, exported `extal_clk`, `dll_recalc()`, `pll_recalc()`, `dll_clk`, `pll_clk`, `main_clks`, div4/div6 tables, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
`arch_clk_init()` registers root/main clocks, adds clkdev lookups, registers div4 clocks, div6 video clock, and MSTP gates. Recalc callbacks read `DLLFRQ`/`PLLCR` and frequency-control registers to derive rates.

## State And Persistence
Clock rates and enable state live in the SH clock framework and MSTPCR hardware bits. Static lookup tables map names such as `cpu_clk`, `peripheral_clk`, `sh-sci.*`, CMT, I2C, SDHI, and LCDC to clocks.

## Dependencies And Integration Points
It depends on SH clk helpers `SH_CLK_DIV4`, `SH_CLK_DIV6`, `SH_CLK_MSTP32`, `clkdev_add_table`, and SoC device IDs used by setup/board files.

## Risks
MSTP gates marked `CLK_ENABLE_ON_INIT` keep CPU/internal blocks alive; changing flags can hang early boot. Lookup-name drift breaks driver clock acquisition silently.

## Test Signals
Boot clock registration, driver probe success for SCI/CMT/I2C/SDHI/LCDC, and rate checks against oscillator/PLL settings validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7343.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7366.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7366.c

## Purpose
`clock-sh7366.c` defines the SH7366 clock tree and module-stop gates.

## Important APIs, Types, And Functions
Important objects are `r_clk`, `extal_clk`, `dll_clk`, `pll_clk`, `div4_clks`, `div6_clks`, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
Init registers main clocks and clkdev aliases, then div4/div6 clocks and MSTP gates. DLL/PLL callbacks read `DLLFRQ` and `PLLCR`; dividers read FRQCR/SCLK/VCLK control registers through SH clock helpers.

## State And Persistence
Runtime clock enable/disable state is represented by MSTPCR hardware and `struct clk` data. No filesystem persistence exists.

## Dependencies And Integration Points
It supplies clocks to SCI, CMT, I2C, SDHI, USBF, display/video blocks, and other SH7366 platform devices via clkdev names.

## Risks
The SH7366 MSTP set differs subtly from SH7343 despite similar layout. Wrong parent selection for memory/video clocks can break display or DMA-heavy peripherals.

## Test Signals
Clock tree dumps, successful driver probes for SCI/CMT/I2C/SDHI/video blocks, and measured peripheral rates are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7366.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7722.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7722.c

## Purpose
`clock-sh7722.c` registers SH7722 clocks, including div4 enable/reparent clocks for IRDA and SIU audio clocks in addition to normal root/divider/MSTP clocks.

## Important APIs, Types, And Functions
It defines `r_clk`, `extal_clk`, `dll_clk`, `pll_clk`, `main_clks`, `div4_clks`, `div4_enable_clks`, `div4_reparent_clks`, `div6_clks`, `mstp_clks[HWBLK_NR]`, `lookups`, and `arch_clk_init()`.

## Control Flow
`arch_clk_init()` registers main clocks, installs lookups, registers div4 clocks, div4-enable clocks, div4-reparent clocks, div6 clocks, and MSTP gates in order. Drivers then acquire clocks by device IDs such as `sh-sci.0`, `sh-tmu.0`, `sh-cmt-32.0`, `sh_mobile_sdhi.0`, and LCDC.

## State And Persistence
Clock state lives in FRQCR, VCLKCR, SCLKACR/BCR, IRDACLKCR, PLL/DLL registers, and MSTPCR bits. The static lookup table is the software binding contract.

## Dependencies And Integration Points
It integrates with the SH mobile clock helpers, setup/board platform devices, and drivers for serial, timers, watchdog, flash, SDHI, USBF, audio, camera, video, and LCDC.

## Risks
Registration order matters because reparent clocks require parents to exist. HWBLK indexes must align with `clock-sh7722.h` style enumerations used by devices. Lookup-name drift breaks clock acquisition.

## Test Signals
Driver probe success across timers/serial/SDHI/USB/display/audio, clock tree inspection, and suspend/resume clock gating tests are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7723.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7723.c

## Purpose
`clock-sh7723.c` defines the richer SH7723 clock tree with L2/FPU/internal gates, six SCIF clocks, media clocks, and div4 enable/reparent support.

## Important APIs, Types, And Functions
Key data includes root `r_clk`/`extal_clk`, DLL/PLL callbacks, `div4_clks`, `div4_enable_clks`, `div4_reparent_clks`, `div6_clks`, extensive `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
The init path registers main clocks, clkdev lookups, div4 clocks, optional enable/reparent dividers, div6 video clock, and MSTP gates. Device drivers later enable gates through names such as `sh-sci.0` through `.5`, I2C, SDHI, USB, camera, VPU, and LCDC.

## State And Persistence
Hardware clock state is in FRQCR, IRDACLKCR, SCLKACR/BCR, VCLKCR, DLL/PLL registers, and MSTPCR0-2. Software state is static `struct clk` arrays and lookup mappings.

## Dependencies And Integration Points
It ties SH7723 setup/board devices to the SH clock framework and clkdev. Internal gates marked on-init protect TLB/cache/FPU/SHYWAY paths.

## Risks
The large MSTP table has index/name mismatch risk. On-init gates for core blocks must not be disabled. Media clocks use mixed parents and reparenting, so audio/video regressions can be subtle.

## Test Signals
Boot with cache/FPU enabled, serial and timer clocks, I2C/SDHI/USB/display/camera probes, and clock enable/disable debug traces validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7724.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7724.c

## Purpose
`clock-sh7724.c` registers SH7724 clocks, including FLL/PLL roots, div3/div4/div6 reparent clocks, media/audio external clocks, and a broad MSTP gate set.

## Important APIs, Types, And Functions
It defines `r_clk`, `extal_clk`, `fll_recalc()`, `pll_recalc()`, `div3_recalc()`, exported external clocks `sh7724_fsimcka_clk`, `sh7724_fsimckb_clk`, `sh7724_dv_clki`, `main_clks`, parent arrays, `div4_clks`, `div6_clks`, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
`arch_clk_init()` registers main clocks, installs lookup aliases, registers div4 clocks, div6 reparent clocks, and MSTP gates. PLL/FLL/div3 callbacks compute rates from FRQCRA/FRQCRB/FLLFRQ/LSTATS state.

## State And Persistence
Clock state persists in hardware clock registers and MSTP bits. Software state is `struct clk` arrays and clkdev lookup rows for DMA, serial, USB, Ethernet, MMC/SDHI, FSI, display, camera, and video devices.

## Dependencies And Integration Points
It integrates with SH clock div4/div6 reparent helpers and platform devices named by setup/board code, including `sh7724-ether.0`, `renesas_usbhs.*`, `sh_fsi.0`, and `sh_mobile_lcdc_fb.0`.

## Risks
This file has high complexity: multiple parent arrays, external clocks, and many media gates. Parent ordering or mask errors can break audio/video clocking without affecting simpler boot tests.

## Test Signals
Clock tree dumps, Ethernet/USB/SDHI/MMC/FSI/LCDC/camera probe tests, measured audio/video rates, and suspend/resume gate tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7734.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7734.c

## Purpose
`clock-sh7734.c` registers SH7734/SH7733 clocks using MODEMR-derived PLL selection, div4 clocks, and MSTP gates across MSTPCR0/1/3.

## Important APIs, Types, And Functions
Important pieces are `extal_clk`, `pll_recalc()`, `pll_clk`, `main_clks`, div4 ratio tables, `div4_clks`, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
`pll_recalc()` reads `MODEMR` and selects PLL behavior for 533 MHz mode or alternate mode. Init registers main clocks, clkdev lookups, div4 clocks, and MSTP gates.

## State And Persistence
Clock enable state is in MSTPCR hardware; rates derive from MODEMR and FRQMR1. Lookup table state binds clocks to I2C, SCI, TMU, SSI, USB, video, SDHI, Ethernet, RTC, and other devices.

## Dependencies And Integration Points
It depends on SH div4/MSTP helpers and device IDs such as `i2c-sh7734.*`, `sh-sci.*`, `sh7734-gether.0`, and timer IDs.

## Risks
MODEMR PLL selection is board strap dependent. MSTPCR3 adds many peripheral gates, increasing risk of missing or misnamed clocks. All div4 clocks are marked on-init, which may preserve required bus paths but reduce power gating.

## Test Signals
Boot frequency checks, serial/timer/I2C/Ethernet/SDHI/USB probe success, and comparing computed rates to MODEMR strap settings validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7734.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7757.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7757.c

## Purpose
`clock-sh7757.c` defines the smaller SH7757 clock tree with EXTAL/PLL roots, CPU/SHYWAY/peripheral div4 clocks, and MSTP gates.

## Important APIs, Types, And Functions
It defines `extal_clk`, `pll_recalc()`, `pll_clk`, `clks`, div4 table `div2`, `div4_clks`, MSTP gates, `lookups`, and `arch_clk_init()`.

## Control Flow
`arch_clk_init()` registers root clocks, adds clkdev lookups, registers div4 clocks, then registers MSTP gates. Drivers obtain clocks for SDHI, RIIC, TMU, SCI, USB, MMC, and RSPI.

## State And Persistence
State lives in FRQCR/FRQMR-style hardware registers and MSTPCR0/1/2 gate bits. Static clkdev aliases are the binding layer.

## Dependencies And Integration Points
It integrates with SH clock helpers and devices named `sh_mobile_sdhi.0`, `sh-tmu.*`, `sh-sci.*`, `renesas_usbhs.0`, and `rspi.2`.

## Risks
RIIC clocks all map to the same MSTP gate, so power gating affects multiple controllers together. PLL and divider masks are compact and subtype-specific.

## Test Signals
SCI/TMU/USB/SDHI/MMC/RSPI/I2C probe tests, clock rate inspection, and runtime clock gating tests validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7757.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7763.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7763.c

## Purpose
`clock-sh7763.c` provides legacy SH7763 clock ops and registers an on-chip SHYWAY clock.

## Important APIs, Types, And Functions
It defines bus/peripheral/CPU divisor tables, `module_clk_recalc()`, `bus_clk_recalc()`, `cpu_clk_recalc()`, `arch_init_clk_ops()`, `shyway_clk_recalc()`, `sh7763_shyway_clk`, `lookups`, and `arch_clk_init()`.

## Control Flow
The legacy SH clock core obtains clock ops through `arch_init_clk_ops()`. Separate `arch_clk_init()` registers the SHYWAY clock and its `shyway_clk` lookup. Recalc callbacks read `FRQCR`.

## State And Persistence
No persistent software state beyond `struct clk` registration. Hardware `FRQCR` determines derived rates.

## Dependencies And Integration Points
It bridges older SH4-style clock ops with an SH4A on-chip clock registration path. Consumers can request `shyway_clk` through clkdev.

## Risks
This hybrid style differs from newer SH4A full clock-tree files. Missing MSTP definitions here means peripheral gates may be managed elsewhere or not at all.

## Test Signals
Boot rate logs, `shyway_clk` lookup availability, serial/timer rate accuracy, and build coverage for SH7763 validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7763.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7770.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7770.c

## Purpose
`clock-sh7770.c` supplies SH7770 clock operation callbacks for the legacy SH clock framework.

## Important APIs, Types, And Functions
It defines IFC/BFC/PFC divisor tables, module/bus/CPU recalc callbacks, `sh7770_*_clk_ops`, and `arch_init_clk_ops()`.

## Control Flow
The clock core calls `arch_init_clk_ops()` by index, and each callback reads `FRQCR` to derive module, bus, or CPU clocks from the parent rate. Master clock ops are minimal compared with full SH4A tree files.

## State And Persistence
The file has no independent state; rate calculations depend on `FRQCR`.

## Dependencies And Integration Points
It is selected by the SH4A Makefile for `CONFIG_CPU_SUBTYPE_SH7770` and provides rates for the subtype setup file and generic peripherals.

## Risks
The divisor tables contain many reserved or fixed entries. Lack of clkdev/MSTP data means device gate coverage depends on other code paths.

## Test Signals
Build/boot on SH7770, timer calibration, serial baud, and clock debug output validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7780.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7780.c

## Purpose
`clock-sh7780.c` implements SH7780 clock ops and registers an additional SHYWAY on-chip clock.

## Important APIs, Types, And Functions
Important objects are IFC/BFC/PFC/CFC divisor tables, master/module/bus/CPU callbacks, `arch_init_clk_ops()`, `shyway_clk_recalc()`, `sh7780_shyway_clk`, `lookups`, and `arch_clk_init()`.

## Control Flow
Legacy ops decode `FRQCR` fields for core clocks. `arch_clk_init()` registers the SHYWAY clock and lookup after the common clock setup path.

## State And Persistence
State consists of calculated `struct clk` rates and hardware `FRQCR`; no software persistence exists.

## Dependencies And Integration Points
It is selected for SH7780 and feeds clock rates to the SH7780 platform setup and any driver requesting `shyway_clk`.

## Risks
SH7780 has distinct CFC/SHYWAY ratios; using generic SH4A assumptions can break bus/interconnect timing. Like SH7763, it lacks full MSTP mapping.

## Test Signals
Clock rate dumps, timer/serial accuracy, and successful SHYWAY lookup registration validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7785.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7785.c

## Purpose
`clock-sh7785.c` registers SH7785 clocks: EXTAL/PLL roots, div4 clocks for peripheral/display/DDR/bus/SHYWAY/UMEM/CPU domains, and MSTP gates.

## Important APIs, Types, And Functions
It defines `extal_clk`, `pll_recalc()`, `pll_clk`, `clks`, `div4_clks`, `mstp_clks`, `lookups`, and `arch_clk_init()`.

## Control Flow
Initialization registers root clocks, lookup aliases, div4 clocks, and MSTP gates. Lookups bind clocks to SCI, SSI/HAC, MMCIF, FLCTL, TMU, SIOF, HSPI, HUDI, UBC, DMAC, and GDTA-related consumers.

## State And Persistence
Clock rates come from PLL and FRQMR1 divider state. Enable state lives in MSTPCR0/1. Some MSTP clocks have `NULL` parents, indicating gate-only or externally parented usage.

## Dependencies And Integration Points
It uses SH div4/MSTP helpers and clkdev names consumed by SH7785 setup/board devices.

## Risks
`NULL`-parent MSTP gates require consumers not to assume a meaningful parent rate. Divider masks for display/graphics/bus domains are subtype-specific and easy to misconfigure.

## Test Signals
Serial, timer, MMCIF, SPI, DMA, audio/HAC/SSI, and display-related probe/rate tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7785.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7786.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7786.c

## Purpose
`clock-sh7786.c` defines SH7786 clocks and gates for serial, audio, timers, SDIF, HSPI, USB, PCIe, DMA, display, and Ethernet.

## Important APIs, Types, And Functions
It defines `extal_clk`, `pll_recalc()`, `pll_clk`, `clks`, div4 ratio table, `div4_clks`, MSTP gates, `lookups`, and `arch_clk_init()`.

## Control Flow
`arch_clk_init()` registers roots, installs clkdev aliases, registers div4 clocks, and registers MSTP gates. PLL rate is derived from PLL hardware state, and div4 clocks read FRQMR1 fields through SH clock helpers.

## State And Persistence
Rate state lives in `struct clk` and hardware FRQMR/PLL registers; enable state is in MSTPCR0/1. Static lookups bind device IDs and connection IDs to clock gates.

## Dependencies And Integration Points
It integrates with SH clock helpers and SH7786 devices including `sh-sci.*`, `sh-tmu.*`, SDIF, HSPI, USB, PCIe, DMA, DU, and Ethernet.

## Risks
Core display, PCIe, and Ethernet gates have no parent in the MSTP table, so rate propagation may be limited. Wrong gate indexes can disable essential bus-facing devices.

## Test Signals
Serial/timer boot, SDIF/USB/PCIe/Ethernet/display probe tests, clock tree inspection, and runtime gate toggling checks validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7786.c -->

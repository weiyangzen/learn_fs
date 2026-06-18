# Group Research: group_2_9front_sources_os_plan9_9front_sys_src_9_bcm_i2cbcm_c_sources_os_plan9_dd75e60f7627

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/i2cbcm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/i2cbcm.c

Broadcom Serial Controller I2C driver for Raspberry Pi BCM2835-family 32-bit kernels.

Key responsibilities:
- Registers an `I2Cbus` named `i2c1` with `addi2cbus()`.
- Maps BSC registers at `VIRTIO+0x804000`.
- Configures GPIO pins 2 and 3 for SDA/SCL alternate function with pull-ups.
- Sets the controller clock divider from `getclkrate(ClkCore)` for 100 kHz target timing.
- Handles I2C interrupts for RX, TX, and transfer-done conditions.
- Implements `i2cio()` for simple read/write transactions through the FIFO.

Important behavior:
- Rejects subaddressed and 10-bit-address transactions.
- Treats one-byte write probes specially to avoid controller NAK behavior.
- Uses `Rendez` sleep/wakeup around FIFO-ready and done bits.
- Clears controller state and returns `-1` on NAK or clock-stretch timeout.

Dependencies:
- Plan 9 I2C core, GPIO helpers, clock mailbox helpers, interrupt registration, and BCM IRQ numbers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/i2cbcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/i2cgpio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/i2cgpio.c

GPIO bit-banged I2C bus implementation for BCM platforms.

Key responsibilities:
- Drives SDA/SCL with GPIO direction changes, using input as released/high and output as pulled low.
- Implements start, restart, stop, bit read/write, byte read/write, ACK/NACK handling, and clock stretching.
- Registers the bit-banged bus through `addi2cbus()`.
- Uses `microdelay()` for bus timing.

Important behavior:
- Clock stretching waits for SCL to rise with a timeout.
- `io()` handles combined write/read packets, including repeated starts when both output and input lengths are present.
- NACK or stretch timeout terminates the transfer and sends stop.

Dependencies:
- GPIO direction/input/output helpers, Plan 9 I2C core, and kernel delay routines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/i2cgpio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/io.h

BCM 32-bit platform interrupt and bus constants.

Key contents:
- Defines interrupt numbers for basic IRQs, GPU IRQs, DMA channels, USB, GPIO, I2C, SPI, UART, timers, mailbox, SD/MMC, and ARM-local interrupts.
- Provides `IRQDMA(chan)` for DMA interrupt numbering.
- Defines `BUSUNKNOWN` as `-1`.

Role:
- Shared by low-level BCM drivers to coordinate IRQ registration and device selection.

Dependencies:
- Consumed by interrupt controller, UART, USB, I2C, SD/MMC, and platform initialization code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/irq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/irq.c

BCM2835-style interrupt controller support for 32-bit ARM kernels.

Key responsibilities:
- Maps interrupt registers at `VIRTIO+0xB200`.
- Tracks handlers as `Vctl` lists indexed by IRQ number.
- Disables CPU and controller interrupts during shutdown.
- Dispatches normal IRQs from pending basic/GPU registers.
- Dispatches FIQ through a separate handler slot.
- Enables IRQs by installing handlers and setting controller enable bits.

Important behavior:
- Returns whether an IRQ was a clock interrupt so trap handling can reschedule.
- Supports shared IRQ handler chains.
- `intrdisable()` is effectively a stub for this platform.

Dependencies:
- Trap entry code, `Ureg`, Plan 9 interrupt registration API, and BCM IRQ constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/irq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/l.s

Minimal 32-bit BCM bootstrap entry.

Key responsibilities:
- Provides `_start`.
- Sets the initial stack near `KTZERO`.
- Branches into `main`.

Role:
- Tiny architecture entry shim used with the rest of the BCM ARM assembly startup and exception code.

Dependencies:
- Memory layout constants from `mem.h` and the C `main()` entry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/lexception.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/lexception.s

32-bit ARM exception vector and trap-entry assembly for BCM.

Key responsibilities:
- Defines the vector table and branch table.
- Handles SVC/syscall, undefined instruction, prefetch abort, data abort, IRQ, and FIQ entries.
- Saves user/kernel register state into Plan 9 `Ureg` layout.
- Switches to the kernel `Mach`/`Proc` context before calling C `syscall()`, `trap()`, `irq()`, and `fiq()`.
- Restores user state for `noteret`, `forkret`, and normal trap return.
- Provides `setr13()` to set per-mode stack pointers.

Important behavior:
- Adjusts link-register offsets for abort types before building the saved PC.
- Distinguishes user exceptions from kernel exceptions.
- Uses FIQ stack handling and direct FIQ dispatch.

Dependencies:
- ARM CPSR modes, `mem.h` register conventions, C trap/syscall/interrupt handlers, and Plan 9 `Ureg` layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/lproc.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/lproc.s

Compatibility include for BCM process assembly.

Key contents:
- Includes `../omap/lproc.s`.

Role:
- Reuses shared ARM process-context assembly from the OMAP port rather than duplicating it locally.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/main.c

32-bit BCM kernel startup, memory sizing, initial user process setup, and reboot support.

Key responsibilities:
- Initializes `Mach` state for CPU0 and secondary CPUs.
- Parses boot arguments and `plan9.ini` data.
- Brings up memory, pools, printing, UART console, screen, traps, VFP, timers, pages, processes, devices, and scheduler.
- Builds initial `/boot/boot` argv and enters user mode in `init0()`.
- Computes kernel/user memory split and kernel pool sizes in `confinit()`.
- Implements reboot trampoline setup using embedded `rebootcode`.
- Provides platform stubs such as `isaconfig()` and `setupwatchpts()`.

Important behavior:
- Enforces minimum Raspberry Pi firmware revision/date.
- Uses mailbox/VideoCore information for RAM and device data.
- `exit()` reboots after stopping interrupts and devices.

Dependencies:
- Port kernel initialization APIs, BCM mailbox helpers, MMU/reboot assembly, scheduler, console, screen, and Plan 9 process bootstrap.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/mem.h

32-bit BCM memory map, page constants, register conventions, and PTE flags.

Key contents:
- Defines page size, stack sizes, max CPUs, `Mach` layout, and ARM register assignments.
- Defines kernel/user virtual layout: `KZERO`, `KTZERO`, `USTKTOP`, `FRAMEBUFFER`, `VIRTIO`, `ARMLOCAL`, and boot scratch addresses.
- Defines page table sizing and segment-map constants.
- Defines Plan 9 PTE abstraction bits: valid, writable, uncached, no-exec, and physical page mask.
- Defines `PHYSDRAM`, min/max macros, and alignment helpers.

Role:
- Central ABI contract for BCM C and assembly files.

Notable constraints:
- Low physical/virtual addresses are tightly reserved for vectors, `Mach`, page tables, mailbox buffer, FIQ stack, and reboot code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/mmu.c

32-bit ARM MMU setup and per-process user mapping management for BCM.

Key responsibilities:
- Initializes kernel L1/L2 mappings for DRAM, I/O, vectors, framebuffer, and device memory.
- Manages per-process L1 entries and L2 page-table allocation/release.
- Switches address spaces in `mmuswitch()` and flushes stale mappings.
- Installs user mappings through `putmmu()`.
- Handles cacheability changes with `mmuuncache()`.
- Provides physical-to-kernel mapping helpers: `cankaddr()`, `mmukmap()`, `kunmap()`, and `checkmmu()`.

Important behavior:
- Uses SoC-specific L1/L2 DRAM attributes from `soc`.
- Flushes TLB/cache state around page-table changes.
- Reuses Plan 9 `Page` refcounting for L2 page-table pages.

Dependencies:
- ARM page-table definitions, cache/TLB assembly helpers, `Proc`/`PMMU`, physical memory layout, and SoC configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/rebootcode.s

32-bit ARM reboot trampoline copied to low physical memory.

Key responsibilities:
- Runs with MMU/caches being torn down for reboot or kernel replacement.
- Copies new kernel/code payload to its destination.
- Cleans/invalidates caches and disables MMU-related state.
- Parks non-boot CPUs with wait-for-interrupt/event loops.
- Branches to the new entry on the boot CPU.

Important behavior:
- Uses physical addresses and explicit cache line maintenance.
- Contains shutdown paths for multicore synchronization.

Dependencies:
- Called by `rebootjump()` after copying to `REBOOTADDR`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/screen.c

BCM framebuffer console and draw attachment support.

Key responsibilities:
- Requests/configures framebuffer geometry through VideoCore mailbox helpers.
- Initializes Plan 9 draw screen state and software cursor support.
- Provides `attachscreen()` for `devdraw`.
- Flushes dirty framebuffer rectangles with cache maintenance.
- Implements console text rendering, scrolling, cursor positioning, and screen blanking.
- Provides color get/set stubs for true-color framebuffer usage.

Important behavior:
- Tracks window text area and cursor position manually for early console output.
- Uses `fbinit()`, `fbblank()`, and framebuffer physical/virtual mapping data from mailbox calls.
- Hardware acceleration is not implemented; `hwdraw()` returns failure.

Dependencies:
- `memdraw`, `devdraw`, framebuffer mailbox support, cache maintenance, and soft cursor routines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/screen.h

Screen, cursor, and mouse interface declarations for BCM display code.

Key contents:
- Declares mouse tracking, mouse acceleration, and mouse byte-input helpers.
- Declares screen blanking, framebuffer flush, `attachscreen()`, cursor on/off/load, and resize/redraw hooks.
- Defines `ishwimage(i)` as always true for `devdraw`.
- Declares software cursor functions.

Role:
- Shared interface between architecture screen code, draw device code, and mouse/cursor implementations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/trap.c

32-bit ARM trap, syscall exception, fault, and diagnostic handling for BCM.

Key responsibilities:
- Installs exception vectors in `trapinit()`.
- Converts ARM trap modes/status into printable names.
- Handles ARM data/prefetch faults through `faultarm()`.
- Detects write faults from instruction decoding with `writetomem()`.
- Dispatches IRQ/FIQ, syscall, undefined instruction, and abort cases in `trap()`.
- Produces user notes or exits for user-mode faults.
- Provides stack/register dumps and `callwithureg()` diagnostics.

Important behavior:
- Distinguishes user and kernel traps via PSR mode.
- Kernel faults panic unless handled by `waserror()`/fault recovery paths.
- Maintains interrupt nesting and scheduling behavior around clock IRQs.

Dependencies:
- Exception assembly, Plan 9 fault VM code, note delivery, scheduler, interrupt controller, and ARM fault-status registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/uartmini.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/uartmini.c

BCM auxiliary mini-UART driver.

Key responsibilities:
- Maps AUX registers at `VIRTIO+0x215000`.
- Configures GPIO pins 14/15 for TX/RX.
- Implements UART operations for enable/disable, interrupt receive/transmit, kick, break, baud, word bits, stop bits, parity, modem control, and polled get/put.
- Registers a `PhysUart` for Plan 9 serial core.

Important behavior:
- Baud divisor is computed from core clock.
- Only 7/8-bit modes are meaningful; parity/stop/modem functions are mostly constrained by hardware.
- Interrupt handler drains RX and fills TX while status bits allow.

Dependencies:
- UART core, GPIO setup, interrupt registration, and clock mailbox helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/uartmini.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/uartpl011.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/uartpl011.c

ARM PL011 UART driver for BCM platforms.

Key responsibilities:
- Implements Plan 9 `PhysUart` operations for PL011-compatible UARTs.
- Handles RX/TX interrupts, FIFO draining/filling, enable/disable, baud configuration, line control, break, parity, stop bits, and polled I/O.
- Controls UART enable state and interrupt masks safely while changing line settings.

Important behavior:
- Uses integer/fractional baud divisors.
- Updates line-control bits through helper masking.
- Supports common serial settings more fully than mini-UART.

Dependencies:
- Plan 9 UART layer, interrupt registration, PL011 register layout, and BCM clock data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/uartpl011.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/usbdwc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/usbdwc.c

USB host driver for the BCM2835 Synopsys DesignWare USB 2.0 OTG controller.

Key responsibilities:
- Registers HCI type `dwcotg`.
- Initializes controller FIFOs, DMA mode, host mode, power, and global interrupts.
- Allocates/releases host channels and configures endpoint channel state.
- Implements control, bulk, and interrupt endpoint read/write paths.
- Handles split transactions, SOF scheduling, NAK/NYET retries, stalls, channel halt, and DMA cache maintenance.
- Provides root-port enable, reset, power, and status methods.
- Uses FIQ-level interrupt handling for host-channel events and a timer IRQ to wake sleepers safely.

Important behavior:
- Isochronous pipes and bandwidth budgeting are explicitly unsupported.
- `Slowbulkin` works around a known bulk-IN DMA/channel lockup by reading packets individually.
- Control reads cache data in an endpoint-owned block until consumed by `ctldata()`.
- Endpoint open rejects unsupported transfer types.

Dependencies:
- `dwcotg.h`, Plan 9 USB core, DMA address/cache helpers, interrupt/timer infrastructure, VideoCore power control, and block allocator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/usbdwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/vcore.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/vcore.c

VideoCore mailbox/property interface and BCM board service helpers.

Key responsibilities:
- Sends/receives mailbox messages through `MAILBOX` registers.
- Builds property-tag requests in the shared mailbox buffer.
- Initializes framebuffer geometry and returns framebuffer address/stride/depth.
- Controls framebuffer blanking and device power state.
- Queries Ethernet MAC, board revision, firmware revision, RAM size, clock rates, and CPU temperature.
- Sets clock rates and controls virtual/external GPIO-style LEDs.
- Provides xHCI reset helper.

Important behavior:
- Serializes property calls through a lock.
- Uses `VCBUFFER` for mailbox payloads.
- Converts mailbox responses into Plan 9 configuration structures.

Dependencies:
- BCM mailbox hardware, SoC clock/device IDs, GPIO helpers, cache-coherent mailbox memory, and framebuffer code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/vcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/vfp3.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/vfp3.c

ARM VFPv3 floating-point detection, context management, and emulation glue.

Key responsibilities:
- Detects supported floating-point implementation/subarchitecture.
- Enables/disables VFP access and configures FPSCR/FPEXC.
- Allocates, saves, restores, forks, and releases per-process FP state.
- Saves FP state for note delivery and restores after notes.
- Handles floating-point unavailable/math traps and posts math notes.
- Provides limited emulation/condition handling for trapped FP instructions.

Important behavior:
- Uses lazy process FP ownership to avoid unnecessary save/restore.
- Kernel and user FP state transitions are carefully separated.
- `fpstuck()` detects repeated FP faults at the same PC.

Dependencies:
- ARM VFP system-register assembly helpers, `FPsave`, process note machinery, trap handling, and scheduler process hooks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/vfp3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/archbcm3.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/archbcm3.c

BCM2837/Raspberry Pi 3 architecture support for the ARM64 kernel.

Key responsibilities:
- Implements reset/reboot watchdog control.
- Feeds/disables the watchdog.
- Reports CPU type/name and prints CPUID information.
- Determines CPU count.
- Clears and writes per-CPU mailbox wake registers.
- Wakes secondary CPUs through mailbox plus event signaling.
- Registers the BCM3 architecture link hook.

Dependencies:
- Power/watchdog registers, ARM64 CPU ID helpers, mailbox layout, `sev()`, and architecture dispatch/link registration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/archbcm3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/archbcm4.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/archbcm4.c

BCM2711/Raspberry Pi 4 architecture support for the ARM64 kernel.

Key responsibilities:
- Implements reset/reboot watchdog control for the Pi 4 platform.
- Feeds/disables watchdog.
- Decodes CPU type/name and prints CPU identification.
- Determines CPU count.
- Clears/writes CPU wake mailboxes and sends events.
- Registers the BCM4 architecture link hook.

Important behavior:
- Similar structure to `archbcm3.c` but with BCM2711-specific register/layout assumptions.

Dependencies:
- Power/watchdog registers, ARM64 ID registers, wake mailbox layout, and platform link selection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/archbcm4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/clock.c

ARM64 BCM timer, cycle counter, and clock interrupt support.

Key responsibilities:
- Uses system timer 3 for CPU0 clock interrupts and `fastticks()`.
- Uses generic local timer interrupts for secondary CPUs.
- Initializes performance counter access and virtual counter access.
- Measures CPU frequency against the 1 MHz system timer.
- Programs next timer deadline in `timerset()`.
- Provides `fastticks()`, `perfticks()`, `microdelay()`, `delay()`, and `synccycles()`.

Important behavior:
- Treats `CNTFRQ_EL0` as unreliable on Raspberry Pi and sets cycle frequency to system timer frequency.
- Uses ARM timer for performance ticks and immediate wakeups.
- Panics on unexpected timer routing to the wrong CPU.

Dependencies:
- ARM64 system registers, interrupt registration, SoC oscillator frequency, timer core, and low-level cycle helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/dat.h

ARM64 BCM kernel data structure declarations and platform configuration types.

Key contents:
- Defines core typedefs for `Mach`, `Proc`, `PMMU`, `MMMU`, `Conf`, `FPsave`, `FPalloc`, `PFPU`, `Uart`, `Pcidev`, and `Soc`.
- Defines `Label`, FP state, memory-bank config, global configuration, process/MMU state, and `Mach`.
- Defines ISA config parsing structure and debug flags.
- Defines device config and SoC-dependent physical/virtual I/O, RAM, PCI, and page-table attributes.
- Provides timing constants and kernel ABI constants.

Role:
- Shared architecture data contract for ARM64 BCM C and assembly code.

Dependencies:
- `mem.h` address constants, Plan 9 port layer types, and ARM64-specific trap/MMU code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/devgen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/devgen.c

Architecture-local directory generation helper.

Key responsibilities:
- Implements `devgen()` wrapper behavior for directory table walking.
- Supports generated device directory entries using Plan 9 `Dirtab` metadata.

Role:
- Small compatibility helper for device file enumeration in this ARM64 port.

Dependencies:
- Plan 9 `Chan`, `Dirtab`, `Dir`, and device directory helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/devgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/ethergenet.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/ethergenet.c

Broadcom GENET Ethernet driver for BCM2711/Raspberry Pi 4.

Key responsibilities:
- Registers Ethernet card type `genet`.
- Maps GENET registers at `VIRTIO1+0x580000`.
- Manages RX/TX DMA descriptor rings and buffer pools.
- Runs kernel processes for receive, send, TX-free, and link-state monitoring.
- Handles GENET interrupt lines for DMA, MDIO, and link events.
- Implements MDIO read/write, MII setup, PHY reset/autonegotiation, and BCM PHY shadow-register tuning.
- Programs MAC address, multicast filters, promiscuous mode, and DMA/ring control.

Important behavior:
- Uses one main RX ring and one main TX ring with 256 descriptors each.
- RX replenishes buffers before handing completed packets to `etheriq()`.
- TX completion frees blocks asynchronously.
- `attach()` performs most hardware bring-up once and starts worker kprocs.
- MAC address comes from `getethermac()`.

Dependencies:
- Plan 9 Ethernet/MII core, DMA/cache helpers, interrupt controller, SoC address mapping, and mailbox MAC query.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/ethergenet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/fns.h

ARM64 BCM function declarations and architecture helper macros.

Key contents:
- Declares low-level assembly helpers for events, atomics, barriers, interrupt priority, user return, labels, FP register save/restore, TLB/cache maintenance, MMU setup, and physical/virtual mapping.
- Declares clock, FP, trap, interrupt, GPIO, UART, DMA, mailbox, framebuffer, PCI, and reboot/platform helpers.
- Defines `PADDR`, `KADDR`, `VA`, `cycles()`, and `getpgcolor()`.

Role:
- Central prototype header joining ARM64 assembly, platform drivers, and Plan 9 port code.

Dependencies:
- `dat.h`, `mem.h`, and all architecture subsystems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/gic.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/gic.c

ARM Generic Interrupt Controller support for BCM ARM64 kernels.

Key responsibilities:
- Maps distributor and CPU-interface registers using `CBAR_EL1`.
- Disables CPU interface and distributor during shutdown.
- Clears/enables interrupts and initializes priorities/targets.
- Dispatches IRQ handlers by GIC interrupt ID.
- Handles FIQ through a dedicated handler.
- Bridges PCI MSI interrupt enable/disable through PCI helpers.
- Translates legacy BCM IRQ numbers to GIC interrupt IDs.

Important behavior:
- Per-CPU private interrupts are stored by current CPU; shared interrupts target CPU0 unless otherwise selected.
- Clock interrupt detection includes system and generic timer IRQs.
- FIQ handler is restricted to CPU0.

Dependencies:
- ARM64 system registers, PCI interrupt helpers, Plan 9 interrupt API, trap code, and SoC local interrupt layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/gic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/gisb.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/gisb.c

BCM GISB arbiter bus-error reporting support.

Key responsibilities:
- Maps GISB arbiter registers at `VIRTIO2+0x400000`.
- Reads captured bus-error status, address, data, master, and interrupt state.
- Clears captured errors and interrupt bits.
- Prints detailed timeout/abort read/write diagnostics.
- Installs `arberror()` as the trap bus-error hook and periodically polls via clock callback.

Dependencies:
- Trap bus-error hook, clock callback registration, BCM GISB registers, and kernel diagnostic output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/gisb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/io.h

ARM64 BCM I/O include wrapper.

Key contents:
- Includes `../bcm/io.h`.

Role:
- Reuses the 32-bit BCM IRQ/bus constants for ARM64 BCM drivers that share the same peripheral naming.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/l.s

ARM64 BCM bootstrap, exception vectors, atomics, cache/TLB, FP register, and fault-safe copy assembly.

Key responsibilities:
- Boots from physical mode, selects EL1/EL2 setup, disables MMU, clears BSS/page tables, builds initial mappings, enables MMU/caches, and calls `main`.
- Computes CPU index from `MPIDR_EL1` and sets per-CPU `Mach` pointer in `TPIDR_EL1`.
- Provides `sev`, interrupt priority functions, idle wait, atomics, label save/restore, and return trampolines.
- Implements TTBR/TLB maintenance helpers and cache maintenance helpers.
- Provides FP/SIMD enable/disable and full V-register save/restore.
- Implements EL0/EL1 syscall/trap/IRQ/FIQ/SERR vector paths and return paths.
- Provides fault-proof `peek()` copy loop used by trap/fault probing.

Important behavior:
- Vector dispatch branches are patched to user/kernel-specific handlers.
- Uses `TRAPFRAMESIZE` layout from `mem.h`.
- Broadcast TLB operations use inner-shareable barriers where appropriate.

Dependencies:
- ARM64 system registers, `mem.h`, MMU C setup, trap/syscall C handlers, and Plan 9 calling conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/main.c

ARM64 BCM kernel entry, configuration, multiprocessor startup, and reboot handling.

Key responsibilities:
- Initializes first user process environment and enters `/boot/boot`.
- Computes memory allocation and kernel/user split.
- Initializes per-CPU `Mach` state.
- Wakes secondary CPUs through the spin table and events.
- Runs full kernel initialization sequence: bootargs, memory, pools, console, screen, traps, FPU, clocks, pages, processes, devices, user process, MMU, and scheduler.
- Sets ARM clock rate from firmware/config.
- Copies and invokes reboot trampoline with identity mapping restored.

Important behavior:
- Secondary CPUs take a shorter path into traps/FPU/clocks/MMU/scheduler.
- Sets `etherargs` from mailbox MAC address for boot networking.
- Uses `SPINTABLE` for ARM64 secondary boot coordination.

Dependencies:
- ARM64 MMU, mailbox/VideoCore helpers, platform arch hooks, scheduler, device/link initialization, and embedded reboot code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/mem.c

ARM64 BCM initial mapping and physical memory discovery.

Key responsibilities:
- Creates identity mappings for TTBR0 during early boot in `mmuidmap()`.
- Creates shared kernel mappings for KZERO, VIRTIO, and ARMLOCAL in `mmu0init()`.
- Handles mixed block/page mappings when I/O ranges are not block-aligned.
- Discovers RAM from mailbox or `*maxmem` overrides.
- Trims memory to SoC DRAM size and virtual KMAP limits.
- Removes oversized early mappings and remaps actual RAM through `kmapram()`.
- Counts pages per configured memory bank.

Important behavior:
- `INITMAP` ensures the kernel image plus one page is mapped during transition.
- Memory above actual RAM is explicitly unmapped after discovery.

Dependencies:
- ARM64 PTE macros, SoC physical I/O layout, mailbox RAM query, `conf.mem`, TLB flush, and kernel end symbol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/mem.h

ARM64 BCM memory layout, virtual address scheme, page-table constants, and PTE attributes.

Key contents:
- Defines 4 KiB pages, VA width, page-table levels, index macros, and block/page sizes.
- Defines `MAXMACH`, stack sizes, trap-frame size, and per-CPU `Mach` address layout.
- Defines high-half kernel ranges for KMAP, VMAP, VIRTIO2/VIRTIO1/VIRTIO, ARMLOCAL, VGPIO, VDRAM, KZERO, KTZERO, and user space.
- Defines memory attribute encodings, shareability, PTE validity/type/access/cache/execute bits.
- Defines segment-map sizing and Plan 9 PTE abstraction flags.

Role:
- Core ABI shared by ARM64 BCM assembly, MMU, drivers, and port code.

Notable constraints:
- User top is derived from the effective VA mask.
- Kernel layout leaves fixed low offsets for spin table, config, reboot code, and mailbox buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/pcibcm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/pcibcm.c

BCM2711 PCIe root complex and MSI support.

Key responsibilities:
- Implements Plan 9 PCI config-space read/write helpers.
- Programs root-complex memory windows and BAR mappings.
- Initializes MSI target address/data and dispatches MSI vectors.
- Provides `pciintrenable()`/`pciintrdisable()` for PCI devices using MSI.
- Scans and maps PCI bus resources.
- Brings PCIe PHY/root complex out of reset and forces Gen2 link settings.

Important behavior:
- Supports 32 MSI ISR slots.
- Allows `*pciwin` and `*pcidmawin` configuration overrides.
- Aborts PCI initialization if link status indicates PHY link down.

Dependencies:
- Plan 9 PCI core, GIC interrupt enable path, SoC PCI window settings, and BCMSTB PCIe registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/pcibcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/rebootcode.s

ARM64 reboot trampoline copied to low physical memory.

Key responsibilities:
- Copies replacement code/image to destination.
- Disables MMU and caches through system-register updates.
- Invalidates local TLB state.
- Branches to new entry or waits when no entry is provided.

Important behavior:
- Runs from physical low memory after `rebootjump()` copies it to `REBOOTADDR`.
- Uses raw system-register encodings for reboot-safe operation independent of normal kernel mappings.

Dependencies:
- ARM64 system register definitions and `main.c` reboot path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/sdhc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/sdhc.c

BCM2711 SDHCI/eMMC2 host-controller driver with ADMA2 support.

Key responsibilities:
- Registers `SDio` controller named `sdhc`.
- Maps SDHCI registers at `VIRTIO+0x340000`.
- Initializes/reset host controller and sets bus power/voltage.
- Sets SD clock and bus width.
- Builds ADMA2 descriptors for data transfers.
- Issues SD commands, parses response formats, handles busy responses, and waits for command/data completion.
- Handles data setup, DMA cache maintenance, and interrupt wakeups.

Important behavior:
- Uses mailbox `ClkEmmc2`, with a 100 MHz fallback if missing.
- Allows `*emmc2bus` override for bus-visible DRAM address base.
- Resets command/data circuits when inhibit bits get stuck.
- Masks card and DMA interrupts out of normal data wait handling.

Dependencies:
- Plan 9 SD core, cache/DMA helpers, BCM clock mailbox, interrupt controller, and SoC bus-DRAM mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/sdhc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/sdhost.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm64/sdhost.c

BCM2835 SDHOST controller driver using the platform DMA engine.

Key responsibilities:
- Registers `SDio` controller named `sdhost`.
- Maps SDHOST registers at `VIRTIO+0x202000`.
- Initializes power, command, status, clock divisor, block size/count, and host config.
- Sets bus width and SD clock.
- Sends SD commands and returns short/long responses.
- Transfers data through `dmastart()`/`dmawait()` using `DmaChanSdhost`.

Important behavior:
- Reports host status errors through generated error strings.
- Uses a 500 ms timeout counter derived from the selected clock.
- LED hook drives the platform `okay()` indicator.

Dependencies:
- Plan 9 SD core, BCM DMA helpers, clock mailbox, and GPIO/LED support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm64/sdhost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/boot.c -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/boot.c

Small boot program that expands embedded boot filesystem and executes `bootrc`.

Key responsibilities:
- Binds `/boot` after `/bin`.
- Forks `paqfs` to mount `/boot/bootfs.paq` at `/root`.
- Binds `/root` onto `/`.
- Adds architecture-specific `/root/$cputype/bin` and `/rc/bin` into `/bin`.
- Replaces `/rc` with `/root/rc`.
- Executes `/bin/bootrc`.

Important behavior:
- Reads `/env/cputype` to choose the architecture bin directory.
- On failure, exits with the current error string.

Dependencies:
- User-level Plan 9 namespace calls, `paqfs`, embedded boot filesystem, and `bootrc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/bootfs.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/bootfs.proto

Prototype file describing the base compressed boot filesystem.

Key contents:
- Includes architecture-specific binaries such as shell utilities, networking tools, authentication helpers, `cfs`, `mntgen`, and `tlsclient`.
- Installs rc support files, including `rcmain`, `reboot.rc`, `net.rc`, and `bootrc`.
- Creates basic directories: `tmp`, `sys/lib/kbmap`, and `lib/firmware`.

Role:
- Input manifest for building `/boot/bootfs.paq`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/bootfs.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/bootrc -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/bootrc

Main Plan 9 boot rc script for building the early namespace, selecting boot method, and starting init.

Key responsibilities:
- Creates `/n`, `/mnt`, and `/mnt/exportfs` mount generators.
- Binds core devices into `/dev` and network devices into `/net`.
- Imports RTC time and reparses selected environment variables.
- Prompts for `bootargs` unless suppressed.
- Starts factotum when needed and loads keys from secstore/auth.
- Runs boot method config/connect functions from `/rc/lib/*.rc`.
- Optionally inserts `cfs` into the boot service pipeline.
- Mounts root, overlays the selected root namespace, and execs architecture init.
- Starts keyboard and USB setup helpers.

Important behavior:
- Supports boot loop flattening through `#ec/bootloop`.
- Removes temporary boot environment and namespace pieces before `exec`.
- Loops after interrupted boot attempts, cleaning `/srv` state for retry.

Dependencies:
- Boot method rc libraries, factotum, secstore, cfs, mount services, namespace tools, `nusbrc`, and architecture `/init`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/bootrc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/devusb.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/devusb.proto

Prototype extension adding USB boot support tools.

Key contents:
- Includes `nusb/usbd`, `nusb/ether`, `nusb/disk`, and `nusb/kb`.
- Installs `nusbrc` into `rc/bin`.

Role:
- Adds USB enumeration, USB Ethernet, USB storage, and USB keyboard support to a boot image.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/devusb.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/disk.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/disk.proto

Prototype extension adding local disk filesystem support to boot images.

Key contents:
- Includes filesystem servers/tools: `9660srv`, `dossrv`, `cfs`, `cwfs64x`, `gefs`, `hjfs`.
- Includes disk tools: `cryptsetup`, `edisk`, `fdisk`, `prep`, `fstype`, and `diskparts`.
- Installs `local.rc` boot method.
- Creates `lib/firmware`.

Role:
- Enables local-disk discovery and mounting during boot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/disk.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/ether4330.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/ether4330.proto

Prototype extension for Broadcom SDIO Wi-Fi firmware.

Key contents:
- Includes calibration files and firmware for BCM40181/40183 and brcmfmac43430/43436/43455/43456 SDIO devices.
- Includes `.txt` NVRAM files and `.clm_blob` regulatory blobs where present.

Role:
- Supplies firmware assets needed by supported Broadcom wireless devices in boot environments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/ether4330.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/etheriwl.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/etheriwl.proto

Prototype extension for Intel Wi-Fi firmware.

Key contents:
- Includes iwm firmware for 3160, 3168, 7260, 7265, 8000C, 8265, and 9260 devices.
- Includes iwn firmware for 1000, 2000, 2030, 4965, 5000, 5150, 6000, 6005, 6030, and 6050 devices.

Role:
- Supplies firmware assets for Intel wireless adapters during boot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/etheriwl.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/etherrt2860.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/etherrt2860.proto

Prototype extension for Ralink RT2860 firmware.

Key contents:
- Installs `lib/firmware/ral-rt2860`.

Role:
- Adds firmware needed by the RT2860 wireless driver in boot images.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/etherrt2860.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/etherwpi.proto -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/etherwpi.proto

Prototype extension for Intel WPI firmware.

Key contents:
- Installs `lib/firmware/wpi-3945abg`.

Role:
- Adds firmware needed by the WPI wireless driver in boot images.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/etherwpi.proto -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/nusbrc -->
# File Research: sources/os/plan9/9front/sys/src/9/boot/nusbrc

Boot-time USB enumeration and auto-attach script.

Key responsibilities:
- Binds USB device namespace into `/dev`.
- Creates private USB state directories under shared memory.
- Starts `nusb/usbd`.
- Reads USB attach/detach events and starts appropriate helpers for Ethernet, keyboards, disks, and selected special devices.
- Detects common USB Ethernet chipsets and passes type-specific arguments.
- For USB disks, runs `diskparts`, detects DOS partitions, and starts `dossrv`.
- Cleans shared-memory state on detach.
- Waits for enumeration completion via `/env/usbbusy`, then binds USB device/net namespaces into `/dev` and `/net`.

Important behavior:
- Avoids attaching selected HID-like devices as keyboards.
- Special-cases Raspberry Pi USB Ethernet so it appears as `/net/etherU0`.

Dependencies:
- `nusb/usbd`, `nusb/ether`, `nusb/disk`, `nusb/kb`, `diskparts`, `fstype`, `dossrv`, shared-memory device `#σ`, and rc event handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/boot/nusbrc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/dat.h

Cyclone V ARM platform kernel data declarations.

Key contents:
- Defines core architecture typedefs for `Conf`, `Confmem`, `FPsave`, `PFPU`, `L1`, `MMMU`, `PMMU`, `Mach`, `Proc`, `Ureg`, `ISAConf`, and `DMAC`.
- Defines process label, FP state, memory configuration, process MMU state, L1 table wrapper, `Mach`, and ISA config structures.
- Defines DMA attribute bits `SRC_INC` and `DST_INC`.
- Provides memory-mapped register macros for MPCore, reset manager, system manager, L3, and DMA.

Role:
- Shared data ABI for Cyclone V C and assembly files.

Dependencies:
- `mem.h`, `io.h`, Plan 9 port kernel types, and platform MMU/trap code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/devarch.c

Cyclone V architecture device for FPGA configuration and arch control files.

Key responsibilities:
- Manages FPGA manager control/status/data registers.
- Waits for FPGA state transitions and interrupt completion.
- Streams FPGA bitstream data through a fixed buffer.
- Exposes arch device read/write/walk/stat/open/close operations.
- Initializes arch device directory entries and platform remap behavior.
- Provides attach support for the architecture device.

Important behavior:
- `fpgaconf()`, `fpgawrite()`, and `fpgafinish()` sequence FPGA configuration states.
- Uses timeout-based waits and an interrupt wake path.
- Write path is stateful across open/write/close.

Dependencies:
- Plan 9 device framework, FPGA manager registers, interrupt registration, reset/system manager registers, and kernel error handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/dma.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/dma.c

Cyclone V DMA controller microprogramming support.

Key responsibilities:
- Maps DMA controller registers.
- Defines DMA channel/status/control and instruction encodings.
- Builds compact DMA instruction streams for memory copies.
- Supports burst/beat sizing and source/destination increment attributes.
- Waits for transfer completion through interrupt wakeups.
- Provides DMA abort interrupt handling.
- Registers DMA interrupt handlers in `dmalink()`.

Important behavior:
- `compactify()` removes no-op spacing from generated instruction streams.
- `dmacopy()` uses controller microcode rather than CPU copy loops.
- DMA completion waits on controller state and interrupt paths.

Dependencies:
- Cyclone V DMA registers, interrupt controller, cache/coherence helpers, and `SRC_INC`/`DST_INC` attributes from `dat.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/ethercycv.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/ethercycv.c

Cyclone V Ethernet MAC driver.

Key responsibilities:
- Registers Ethernet card type for Cyclone V.
- Manages descriptor rings and RX buffer replenishment.
- Implements RX and TX packet paths.
- Handles Ethernet interrupts and wakes worker paths.
- Initializes MAC/DMA hardware and PHY/MII.
- Implements attach, promiscuous mode, multicast hash filtering, and interface statistics.
- Parses or assigns Ethernet MAC address during probe.

Important behavior:
- RX buffers are aligned and DMA-cache managed.
- Multicast filtering uses hash computation over Ethernet addresses.
- Link and descriptor state are exposed through `ifstat`.

Dependencies:
- Plan 9 Ethernet/MII core, DMA/cache helpers, EMAC registers, interrupt controller, and platform reset/system manager registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/ethercycv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/fns.h

Cyclone V architecture function declarations and macros.

Key contents:
- Declares atomics, address translation, process context, idle/event, MMU, interrupt, timer, UART, FP, cache, DMA, arch, and screen helpers.
- Defines `KADDR`, `PADDR`, `VA`, `PTR2UINT`, `userureg`, and `getpgcolor`.
- Declares cache-line and range maintenance routines plus physical-address cache helpers.
- Declares `dmacopy()` with DMA attribute arguments.

Role:
- Shared prototype layer connecting Cyclone V assembly, platform code, and Plan 9 port code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/init9.s -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/init9.s

Tiny Cyclone V user-init assembly stub.

Key responsibilities:
- Defines `_main`.
- Calls `main`.
- Calls `exits` if `main` returns.

Role:
- Minimal user/runtime entry glue for this architecture.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/intr.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/intr.c

Cyclone V interrupt controller support.

Key responsibilities:
- Initializes interrupt controller distributor/CPU interface state.
- Installs interrupt handlers by IRQ number.
- Enables interrupts with level/edge configuration.
- Dispatches pending interrupts to registered handlers.
- Tracks interrupt counts and clock interrupt behavior.

Important behavior:
- Uses GIC-like register layout through MPCore base.
- Maintains handler chains through `Vctl` records.
- `intr()` is the C dispatch target from trap assembly.

Dependencies:
- MPCore interrupt registers, `io.h` IRQ constants, trap assembly, and Plan 9 interrupt API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/io.h

Cyclone V physical I/O base addresses and IRQ constants.

Key contents:
- Defines UART, MPCore, L2 cache, clock manager, EMAC, reset manager, system manager, FPGA manager, OCRAM, DMA, and L3 base addresses.
- Defines reset-manager register offsets.
- Defines HPS clock value.
- Defines IRQ numbers for timer, UART0, EMAC1, FPGA manager, DMA channel 0, and DMA abort.
- Defines interrupt trigger constants `LEVEL` and `EDGE`.

Role:
- Shared hardware address/IRQ map for Cyclone V platform drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/l.s

Cyclone V ARM bootstrap and low-level assembly support.

Key responsibilities:
- Disables watchdog/L2/MMU early, clears low memory and BSS, builds initial section mappings, enables MMU, and enters `main`.
- Sets vector base and per-mode stacks.
- Provides user return, fork return, and stack setup helpers.
- Implements serial hex debug output.
- Provides interrupt priority functions, atomics, barriers, idle/event, TTBR/TLB/ASID helpers, fault address/status reads, performance counters, and VFP save/restore.
- Implements cache maintenance by range and line.
- Provides physical-address lookup helper `palookur()`.

Important behavior:
- Emits early boot characters through UART for progress.
- Maps KZERO to physical 0 and peripheral region as device/no-exec.
- Stores `Mach*` in `TPIDRPRW`.

Dependencies:
- `mem.h`, `io.h`, trap vector code, MMU setup, and ARMv7 CP15/VFP instructions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/ltrap.s -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/ltrap.s

Cyclone V ARM exception vector and syscall/trap entry assembly.

Key responsibilities:
- Defines ARM exception vectors.
- Handles instruction abort, generic exceptions, and SVC/syscall entry.
- Saves registers and status into `Ureg` layout.
- Restores `Mach`/`Proc` context from TPIDRPRW.
- Calls C `trap()` or `syscall()`.
- Restores user or kernel state and returns from exception.

Important behavior:
- Differentiates abort mode and general exception mode when saving PSR/type.
- Uses CPS mode switches and banked register restore for user returns.

Dependencies:
- `mem.h`, `io.h`, C trap/syscall handlers, and `Ureg` layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/ltrap.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/main.c

Cyclone V kernel startup, configuration parsing, and initial user process setup.

Key responsibilities:
- Implements reboot/exit stubs and address-alignment checks.
- Sets up process MMU state during fork/setup.
- Parses boot configuration options from the boot config area.
- Initializes memory configuration and kernel/user split.
- Creates initial process environment and enters user mode.
- Runs kernel initialization sequence: UART, memory, MMU, interrupts, timers, pools, pages, processes, devices, and scheduler.
- Provides `getconf()`, `isaconfig()`, CPUID print, sanity checks, and watchpoint stub.

Important behavior:
- Uses fixed config buffer sizing.
- Service mode and memory split are driven by parsed config variables.
- Starts from a relatively small platform-specific sequence compared with BCM.

Dependencies:
- Cyclone V MMU/trap/timer/interrupt code, Plan 9 port initialization, UART console, and user bootstrap.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/mem.h

Cyclone V memory layout, page-table flags, processor modes, and assembly constants.

Key contents:
- Defines page/cache-line sizes, stack sizes, timing constants, and max CPUs.
- Defines kernel/user virtual layout: `KZERO`, `KTZERO`, temporary maps, `KMAP`, `MACH`, `MACHL1`, `CONFADDR`, `PERIPH`, `UZERO`, `UTZERO`, and `USTKTOP`.
- Defines Plan 9 PTE abstraction flags and ARM L1/L2 descriptor flags.
- Defines ARM PSR mode/interrupt bits and assembly encodings for barriers, WFE/SEV, CPS, and VFP register access.
- Defines page-table index macros and TTBR attributes.

Role:
- Core memory/MMU ABI for Cyclone V C and assembly code.

Notable constraints:
- Peripheral space begins at `0xFF000000`.
- Temporary mapping sizes are section-sized and tied to L1/L2 layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/mem.h -->
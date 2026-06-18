# Group Research: group_1468_plan9_sources_os_plan9_plan9_sys_src_9_bcm_arch_c_sources_os_plan9__8f591a1de086

Scope checked against `Docs/research_subset_a.md`: all listed files are within `sources/os/plan9/plan9`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/arch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/arch.c

This file is a one-line architecture wrapper that includes `../omap/arch.c`.

It lets the BCM kernel reuse the OMAP ARM architecture implementation at compile time while keeping a BCM-local source path for the build. The real behavior is defined in the included OMAP file, so this file’s role is source-tree/build composition rather than standalone logic.

Integration points: compiled as part of the BCM ARM kernel; depends on the OMAP architecture source being compatible with BCM-specific headers and symbols.

Risk notes: any research or changes to behavior must inspect `sources/os/plan9/plan9/sys/src/9/omap/arch.c`; this file itself only redirects compilation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/archbcm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/archbcm.c

This file contains BCM2835/Raspberry Pi board glue for reset, reboot, watchdog service, CPU identification, and default Ethernet controller discovery.

Key behavior:
- `archreset()` enables floating point via `fpon()`.
- `archreboot()` programs the BCM watchdog/reset controller and spins forever.
- `wdogfeed()` refreshes the watchdog periodically; `wdogoff()` disables reset configuration.
- `cpuidprint()` reports the single ARM1176JZF-S CPU and measured MHz.
- `archbcmlink()` registers watchdog feeding with the clock callback list.
- `archether()` exposes controller 0 as USB Ethernet with 100 Mbps metadata.

Integration points: uses `POWERREGS` at `VIRTIO+0x100000`, `addclock0link`, `Ether`, and watchdog constants. It depends on `clock.c` for periodic callbacks and on USB Ethernet support for actual network I/O.

Risk notes: reboot and watchdog writes require the Broadcom password field. Incorrect register mapping or watchdog timing can hang reset/shutdown. `archether()` hard-codes only one USB-backed Ethernet controller.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/archbcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/arm.h

This header defines ARMv6 CPU, CP15, MMU, cache/TLB, status-register, and page-table constants shared by C and assembly.

Key content:
- Processor mode and CPSR flag constants such as `PsrMsvc`, `PsrMirq`, `PsrDirq`, `PsrDfiq`, `PsrN/Z/C/V`.
- Coprocessor IDs and CP15 register selectors for ID, control, TTB, DAC, FSR, FAR, cache, TLB, vector base, and performance counters.
- Main control register bits for MMU, caches, high vectors, branch prediction, alignment, and architecture-specific must-be-one/zero masks.
- Cache/TLB maintenance operation encodings used by assembly helpers.
- L1/L2 MMU descriptor constants: `Fault`, `Coarse`, `Section`, `Small`, `Cached`, `Buffered`, access permissions, domain access, and `HVECTORS`.

Integration points: included by `arm.s`, `l.s`, `lexception.s`, `mmu.c`, `trap.c`, and floating-point code. It is the common contract between assembly opcodes and C page-table code.

Risk notes: constants are hardware-sensitive. A wrong CP15 selector or descriptor bit breaks boot, cache maintenance, exception vectors, or user mappings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/arm.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/arm.s

This assembly include provides BCM ARMv6 helper macros and address translation constants.

Key content:
- `PADDR(va)` maps kernel virtual addresses to physical DRAM during early boot.
- `L1X(va)` computes L1 page table byte offsets.
- `PTEDRAM` defines cached/buffered kernel section PTE attributes.
- `ISB`, `DSB`, and `BARRIERS` encode ARMv6 cache/pipeline barrier operations via CP15.
- `MCRR` emits an MCRR instruction word for cache range operations.
- `OKAY` writes the GPIO OK LED register.

Integration points: included by `l.s`, `lexception.s`, and `rebootcode.s`. It centralizes low-level instruction sequences not directly supported by the Plan 9 assembler syntax.

Risk notes: barrier and cache maintenance macros clobber registers by convention. Callers must account for register use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/clock.c

This file implements BCM2835 timer support for kernel ticks, fast ticks, delays, performance ticks, and immediate ARM timer interrupts.

Key behavior:
- Uses system timer 3 at 1 MHz for `hzclock` interrupts and `fastticks()`.
- Uses the ARM timer for `perfticks()` and `armtimerset()`.
- `clockinit()` estimates CPU frequency by comparing system timer ticks with cycle counter values, then enables `IRQtimer3`.
- `clockintr()` acknowledges timer 3 and calls `timerintr`.
- `timerset()` bounds next timer deadlines between `MinPeriod` and `MaxPeriod`.
- `microdelay()` and `delay()` busy-wait on the 1 MHz system timer.
- `clockshutdown()` disables ARM timer and watchdog.

Integration points: uses interrupt registration, watchdog shutdown, `m->cpuhz/cpumhz/cyclefreq`, and the generic timer subsystem.

Risk notes: timing assumes system timer frequency is 1 MHz. `timerset()` calls `fastticks()` twice and computes from `now`; jitter is expected but bounded.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/coproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/coproc.c

This file is a one-line wrapper including `../teg2/coproc.c`.

It reuses Tegra ARM coprocessor support for the BCM build. The implementation details, including CP15/coprocessor access helpers, live in the included Tegra file.

Integration points: expected to satisfy prototypes in `fns.h` such as `cprd`, `cpwr`, `cprdsc`, and `cpwrsc`.

Risk notes: behavior depends entirely on ARM compatibility between BCM ARM1176 and the included Tegra code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/dat.h

This header defines BCM kernel machine data structures, timing constants, process/MMU state, floating-point save state, and device configuration types.

Key content:
- Time constants: `HZ`, `MS2HZ`, `TK2SEC`, `Mhz`.
- Core typedefs for `Mach`, `Proc`, `Conf`, `FPsave`, `Ureg`, `PMMU`, `MMMU`, etc.
- `FPsave` supports software emulation and VFP state with 32 registers and status/control metadata.
- `Conf` stores memory, process, swap, image, and CPU configuration.
- `Mach` contains scheduler state, interrupt statistics, MMU state, clock/cycle data, FPU state, and exception-mode save areas.
- Fake `kmap` macros map page physical addresses through `kseg0`.
- Global declarations for `m`, `up`, `machaddr`, `memsize`, `active`, debug flags, and ISA/device configuration.

Integration points: included by most BCM kernel C files and pulls in `../port/portdat.h`, so it bridges machine-specific and portable kernel structures.

Risk notes: register globals `m` and `up` assume assembly establishes R10/R9. `MAXMACH` is one in `mem.h`, and many fields assume a uniprocessor BCM target.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devarch.c

This file implements the Plan 9 `#P` architecture device for BCM.

Key behavior:
- Maintains a small `archdir` table with dynamic entries and per-file read/write callbacks.
- `addarchfile()` adds immutable named files, rejects duplicates, and returns the `Dirtab`.
- Implements standard device operations: attach, walk, stat, open, close, read, write.
- Exposes `cputype`, read-only, reporting `ARM11 <MHz>`.

Integration points: the `Dev archdevtab` is registered by the kernel device table. Other platform code can add architecture files through `addarchfile()`.

Risk notes: `Qmax` is 16, so additional architecture files are capacity-limited. `strcpy(d.name, name)` assumes names fit the `Dirtab` name buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devether.c

This file is a one-line wrapper including `../omap/devether.c`.

It reuses the OMAP generic Ethernet device implementation for the BCM kernel. BCM-specific controller discovery is supplied by `archbcm.c` and USB Ethernet support by `etherusb.c`.

Integration points: expected to provide `ether` device operations and interact with `etherif.h`.

Risk notes: actual behavior must be researched in the included OMAP `devether.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devfakertc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devfakertc.c

This file implements a fake `#r/rtc` device for Raspberry Pi systems without a hardware RTC.

Key behavior:
- Initializes `rtcsecs` from external `kerndate`.
- Registers `rtctick()` through `addclock0link` to increment once per second.
- Exposes a `rtc` file under device `#r`.
- `rtcread()` returns current seconds as a numeric string.
- `rtcwrite()` accepts a positive numeric time and updates `rtcsecs`.

Integration points: used by boot `settime.c` for local boot time initialization. Uses standard Plan 9 device operations through `fakertcdevtab`.

Risk notes: time starts from kernel build date and drifts with system ticks. `rtcwrite()` uses `strncpy` without explicit NUL termination before `strtol` when `n < sizeof(b)`, relying on stack residue risk; typical Plan 9 code often tolerates this pattern, but it is not robust.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devfakertc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devusb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devusb.c

This file implements the Plan 9 USB device framework exposed as `#u`.

Key behavior:
- Maintains registered HCI types, active HCIs, endpoint table `eps`, endpoint references, and USB device IDs.
- Provides namespace entries: `#u`, `#u/usb/ctl`, endpoint directories `epN.M`, and endpoint `data`/`ctl` files.
- `addhcitype()` registers host controller drivers such as `dwcotg`.
- `usbreset()` probes HCIs; `usbinit()` creates root hub endpoint 0 for each controller.
- `usbopen()` enforces endpoint existence, exclusive data-file use, mode compatibility, configuration state, and controller `epopen`.
- `usbread()`/`usbwrite()` dispatch endpoint I/O to HCI methods, with special toy root-hub emulation.
- `epctl()` implements commands: `new`, `newdev`, `hub`, `speed`, `maxpkt`, `ntds`, `pollival`, `samplesz`, `hz`, `info`, `detach`, `address`, `debug`, `clrhalt`, `name`, `timeout`, `reset`.
- `usbctl()` handles global debug and dump.

Integration points: HCI implementations fill `Hci` callbacks from `../port/usb.h`; `usbdwc.c` registers `dwcotg`. User-space `usbd` drives enumeration by writing endpoint control files.

Risk notes: endpoint lifecycle is reference-counted and subtle, especially `detach` releasing endpoint refs. Root hub emulation is intentionally minimal. Isochronous-related fields are present, but actual HCI support may be incomplete. Bandwidth/load estimates are rough.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/devusb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/dma.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/dma.c

This file implements a simple BCM2835 DMA controller driver.

Key behavior:
- Supports channels 0-6 with one lazily allocated aligned control block per channel.
- `dmastart()` initializes channel registers, sets source/destination bus addresses, performs cache maintenance, writes the control block, and starts DMA.
- Supports device-to-memory, memory-to-device, and memory-to-memory directions.
- `dmainterrupt()` acknowledges channel interrupt and wakes waiters.
- `dmawait()` sleeps up to 3 seconds, checks completion state, resets on timeout/error, and clears interrupt/end bits on success.

Integration points: used by `emmc.c` for SD/eMMC data transfers. Address conversion uses `DMAADDR()` and `DMAIO()` from `fns.h`.

Risk notes: one outstanding transfer per channel is assumed. Channel allocation is caller-managed; no global serialization protects concurrent starts on the same channel. Cache maintenance correctness is critical for DMA visibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/dwcotg.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/dwcotg.h

This header defines register layout and bit fields for the Synopsys DesignWare Core USB 2.0 OTG controller in host mode on BCM2835.

Key content:
- `Dwcregs` maps global, host, port, channel, and power/clock gating registers at their documented offsets.
- `Hostchan` maps per-channel registers: `hcchar`, `hcsplt`, `hcint`, `hcintmsk`, `hctsiz`, `hcdma`, `hcdmab`.
- Defines global interrupt/status bits, FIFO size fields, hardware config fields, host config fields, port status/control bits, channel characteristic bits, split transaction fields, channel interrupt bits, transfer-size/PID fields, and power gating bits.
- `Maxchans` is 16, matching the maximum channel register array.

Integration points: consumed by `usbdwc.c` to configure the controller, host channels, FIFOs, port reset/status, DMA transfers, and interrupt handling.

Risk notes: this is hardware-definition code; errors manifest as USB hangs or corrupted transfers. Comments note BCM-specific reinterpretation of some AHB config bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/dwcotg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/emmc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/emmc.c

This file implements the BCM2835 Arasan eMMC/SD host controller backend for Plan 9’s SD I/O layer.

Key behavior:
- Maps eMMC registers at `VIRTIO+0x300000`.
- Defines command response/data flags in `cmdinfo[64]`.
- `emmcinit()` queries the eMMC clock from VideoCore, resets the host controller, and records external clock.
- `emmcenable()` sets the initial 400 kHz clock, waits for stability, configures interrupt masks, and enables `IRQmmc`.
- `emmccmd()` issues SD/MMC commands, handles command/data inhibit reset, response extraction, busy wait completion, error handling, clock switch after card select, and host bus-width update after `Setbuswidth`.
- `emmciosetup()` programs block size/count.
- `emmcio()` performs DMA transfers via `dmastart()`/`dmawait()`, waits for data-done interrupts, and handles errors/timeouts.
- Exports `SDio sdio` with init/enable/inquiry/cmd/setup/io callbacks.

Integration points: uses `vcore.c` for clock rate, `dma.c` for data movement, and generic `../port/sd.h` stack.

Risk notes: timeout constants are guessed. Only selected DMA channels are known to work. Clock divider calculation assumes external clock availability or a 100 MHz fallback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/emmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/etherif.h

This file is a one-line wrapper including `../omap/etherif.h`.

It reuses the OMAP Ethernet interface declarations for the BCM build.

Integration points: included by `archbcm.c`, `devether.c`, and `etherusb.c`.

Risk notes: the actual interface definitions are in the OMAP header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/etherusb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/etherusb.c

This file implements a kernel Ethernet proxy over USB endpoint files.

Key behavior:
- Registers an `usb` Ethernet card through `etherusblink()`.
- `etherusbctl()` supports `bind type indev outdev mac bufsize maxpkt` and `unbind`.
- Supports CDC, ASIX, and SMSC framing with protocol-specific unpack/transmit functions.
- `etherusbproc()` continuously reads USB input blocks, unpacks one or more Ethernet frames, and injects them through `etheriq`.
- `etherusbtransmit()` drains the Ethernet output queue, wraps frames as needed, and writes through USB output channel.
- Tracks receive/transmit buffer and packet counters exposed by `ifstat`.

Integration points: binds to USB endpoint `Chan`s created by `devusb.c`/`usbd`; connects to generic Ethernet via `Ether` callbacks.

Risk notes: `unbind()` closes channels while the reader kproc may still be blocked/erroring; cleanup relies on process error exit. USB device-specific framing is hand-coded and validates only basic lengths/checksums.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/etherusb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/fns.h

This header declares BCM machine functions and maps common machine abstractions.

Key content:
- Includes `../port/portfns.h`.
- Declares architecture, clock, cache, MMU, DMA, framebuffer, VideoCore, interrupt, UART, trap, watchdog, process, syscall, and FPU functions.
- Defines `intrenable` as a three-argument wrapper around `irqenable`.
- Defines SD memory helpers and pointer/address conversion macros: `KADDR`, `PADDR`, `DMAADDR`, `DMAIO`.
- Defines Plan 9 `waserror()` macro in terms of `setlabel`.
- Provides no-op or simple macros for page color, kmap invalidation, and page ref counting.

Integration points: included broadly by BCM C files. It is the main declaration bridge between assembly routines and C code.

Risk notes: address conversion macros assume BCM memory layout from `mem.h`, especially `PHYSDRAM`, `BUSDRAM`, `BUSIO`, `KSEGM`, and `VIRTIO`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/fpiarm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/fpiarm.c

This file implements software emulation for old ARM FPA floating-point instructions.

Key behavior:
- Decodes trapped ARM FPA opcodes and emulates them using portable `fpi.h` internal floating-point helpers.
- Supports loads/stores, register transfers, compare, common unary operations, and binary arithmetic: add, subtract, multiply, divide, reverse forms, move, negate, absolute, round.
- Maintains emulated FP status/control in `Proc.fpsave`.
- Initializes FP emulation state on first use and rejects emulated opcodes when process state indicates VFP mode.
- `fpiarm()` loops over consecutive FPA instructions, checks condition codes, emulates matching instructions, and advances `ureg->pc`.

Integration points: called by FPU undefined-instruction handling through `fpuemu()` paths. Uses `Ureg`, `FPsave`, `arm.h` opcode predicates, and `../port/fpi.h`.

Risk notes: comments state it does not implement all ARM FP properties, does all arithmetic in double precision, and does not update FP trap status. Many deprecated/unimplemented FPA operations call `error()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/fpiarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/init9.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/init9.s

This file is a one-line wrapper including `../omap/init9.s`.

It reuses OMAP init assembly for the BCM build, likely for the initial user-mode bootstrap code or process entry glue.

Integration points: complements `main.c` user process creation and `touser()` path declared in `fns.h`.

Risk notes: actual behavior lives in the included OMAP file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/io.h

This header defines BCM interrupt numbers, DMA direction/device/channel IDs, power domain IDs, and clock IDs.

Key content:
- GPU interrupt IDs for system timers, USB, DMA, AUX UART, and MMC.
- ARM basic IRQ IDs for ARM timer.
- `IRQDMA(chan)` macro.
- `IRQfiq` set to USB, reflecting the single FIQ source policy.
- DMA direction constants and eMMC channel/device constants.
- VideoCore power IDs for SD, UART, USB, I2C, SPI, etc.
- VideoCore clock IDs for eMMC, UART, ARM, core, SDRAM, pixel, PWM, etc.

Integration points: used by `clock.c`, `dma.c`, `emmc.c`, `trap.c`, `uartmini.c`, `usbdwc.c`, and `vcore.c`.

Risk notes: IDs must match BCM2835 interrupt controller and mailbox property ABI.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/kbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/kbd.c

This file is a one-line wrapper including `../omap/kbd.c`.

It reuses OMAP keyboard support for the BCM build. On Raspberry Pi, keyboard input is generally USB-backed, but this wrapper supplies the kernel keyboard device code path.

Integration points: interacts with UART console input and USB keyboard setup through generic device layers.

Risk notes: real logic is in the included OMAP source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/kbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/l.s

This assembly file contains BCM2835 ARMv6 boot entry and low-level CPU helpers.

Key behavior:
- `_start` sets physical SB while MMU is off, enters SVC mode, disables MMU/caches, invalidates caches/TLBs, clears early memory, sets stack, calls `mmuinit()`, installs DAC/TTB, enables MMU/caches/high vectors, and jumps into kernel virtual space.
- `_startpg` enables the cycle counter and calls `main`.
- Provides CP15 readers for fault status/address and cycle counter.
- Implements interrupt priority helpers `splhi`, `splfhi`, `splflo`, `spllo`, `splx`, `islo`.
- Implements `tas`, `setlabel`, `gotolabel`, `getcallerpc`, `idlehands`, `coherence`.
- Provides TLB invalidation and cache maintenance functions, including range writeback/invalidate through MCRR.

Integration points: used by the entire kernel for boot, scheduling, locking, exception recovery, cache coherency, MMU management, and delay/timing.

Risk notes: register conventions are critical: `m` and `up` rely on fixed registers elsewhere. Cache range helpers rely on ARMv6 MCRR encodings from `arm.s`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/lexception.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/lexception.s

This assembly file implements ARM exception vectors and exception-mode transitions.

Key behavior:
- Defines vector stubs and vector table copied to high vectors by `trapinit()`.
- `_vsvc` saves user registers for SWI/syscall, calls `syscall`, restores state, and returns with `RFE`.
- `_vund`, `_vpabt`, `_vdabt`, `_virq` save scratch registers and branch to `_vswitch`.
- `_vswitch` switches from exception mode to SVC mode, builds `Ureg`, distinguishes user vs kernel exceptions, calls `trap`, and restores state.
- `_vfiq` saves FIQ state and calls `fiq`.
- `setr13()` installs mode-specific stacks.

Integration points: paired with `trap.c` and `syscall.c`; uses `Mach` fields for exception stacks and high-vector mapping from `mmu.c`.

Risk notes: precise PC adjustment is split between assembly and `trap.c`. Register save/restore ordering is delicate and comments mention Plan 9 assembler `MOVM.W` ambiguity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/lproc.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/lproc.s

This file is a one-line wrapper including `../omap/lproc.s`.

It reuses OMAP process/context-switch/user-entry assembly for the BCM build.

Integration points: expected to provide process save/restore, `touser`, and related routines declared in `fns.h`.

Risk notes: actual behavior is in the included OMAP assembly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/main.c

This file implements BCM kernel startup, configuration parsing, first user process creation, memory sizing, shutdown, and reboot.

Key behavior:
- Parses ATAGs or raw `plan9.ini`-style boot arguments into in-kernel config storage.
- Initializes `Mach`, MMU second phase, options, memory configuration, allocator, UART console, screen, firmware check, traps, clock, timers, CPU print, architecture reset, processes, segments, links, devices, pages, swap, first user process, and scheduler.
- `init0()` creates initial namespace, initializes devices, exports config into `#e` and `#ec`, starts alarm kproc, and enters user mode.
- `userinit()` creates the first process with kernel stack, user stack, boot args, and `initcode`.
- `confinit()` determines memory, page counts, process limits, swap/image sizes, and pool sizes.
- `exit()` and `reboot()` coordinate shutdown, device shutdown, clock shutdown, interrupt disable, reboot trampoline copy, and new-kernel transfer.
- `isaconfig()` is a stub used by reused OMAP Ethernet code.

Integration points: central orchestrator for all BCM platform subsystems and portable kernel init.

Risk notes: firmware revision is hard-gated. `memsize` has fallback and can be overridden by `*maxmem`. Reboot depends on copying `rebootcode` to `REBOOTADDR`, cache flushing, and physical addressing correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/mem.h

This header defines BCM memory layout, page sizes, kernel/user address spaces, cache line size, PTE flags, and physical/bus I/O regions.

Key content:
- Page size 4 KiB, `MAXMACH=1`, `MACHSIZE=BY2PG`, kernel stack 8 KiB.
- Kernel virtual layout: `KZERO`, `CONFADDR`, `MACHADDR`, `L2`, `VCBUFFER`, `FIQSTKTOP`, `L1`, `KTZERO`, `VIRTIO`, `FRAMEBUFFER`.
- User layout: `UZERO`, `UTZERO`, `USTKTOP`, `USTKSIZE`, temporary exec stack.
- Reboot code address at `KZERO+0x3400`.
- Cache line size 32 bytes, PTE map constants and Plan 9 PTE flags.
- Physical/bus regions: ARM DRAM physical base 0, GPU bus DRAM `0x40000000`, physical I/O `0x20000000`, bus I/O `0x7E000000`, 16 MiB I/O size.

Integration points: used by boot assembly, MMU code, DMA mapping, VideoCore mailbox buffer, framebuffer mapping, traps, and process setup.

Risk notes: layout aliases `VCBUFFER`, `FIQSTKTOP`, and `L1` near early low kernel memory. Changes must preserve alignment and boot-time assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/mmu.c

This file implements ARMv6 MMU setup and per-process user mappings for BCM.

Key behavior:
- `mmuinit()` builds initial physical L1/L2 tables: maps all RAM at `KZERO`, identity maps first MB for MMU enable, maps I/O at `VIRTIO`, and maps high vectors through L2.
- `mmuinit1()` switches to virtual L1 pointer, removes identity map, and invalidates TLB.
- Maintains per-process L2 page lists and caches via `PMMU`.
- `mmuswitch()` flushes caches, handles `newtlb`, clears user L1 range, installs process L2 tables, writes back L1, and invalidates TLB.
- `putmmu()` allocates/reuses L2 page tables, installs user small-page PTEs, flushes the changed entry, invalidates VA, and handles text-cache flush.
- `mmurelease()` clears mappings and returns L2 pages to allocator.
- `mmukmap()` adds section mappings for device/framebuffer regions.
- `cankaddr()` validates physical addresses for direct kernel mapping.

Integration points: called by boot assembly, fault handling, page fault resolution, process switching, and framebuffer setup.

Risk notes: user L1 cleanup has a disabled optimized path with a noted bug; active path clears the full user range. Cache/TLB maintenance is conservative and performance-costly but simpler.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/mouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/mouse.c

This file is a one-line wrapper including `../omap/mouse.c`.

It reuses OMAP mouse support for the BCM build, while BCM-specific display cursor drawing is implemented in `screen.c`.

Integration points: interacts with `screen.h` functions such as `mousexy`, `setcursor`, and `cursoron/off`.

Risk notes: actual mouse device behavior is in the included OMAP source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/rebootcode.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/rebootcode.s

This assembly file is copied to low kernel memory and executed during kernel reboot.

Key behavior:
- `main(PADDR(entry), PADDR(code), size)` saves arguments, enters SVC mode with interrupts disabled, calls `cachesoff`, disables the MMU, creates a small physical stack, copies the new kernel to its entry address with `memmove`, and jumps to entry.
- `cachesoff()` writes back/invalidates caches, disables caches and branch prediction, invalidates TLBs, restores a first-MB double map, and relocates SB/link to physical addressing.

Integration points: used by `main.c` `reboot()`, copied to `REBOOTADDR`.

Risk notes: must run without normal virtual mappings after MMU disable. Stack is placed just before the destination kernel entry, so overlap assumptions matter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/screen.c

This file implements BCM framebuffer console and software cursor support.

Key behavior:
- Initializes the framebuffer through `fbinit()` and Plan 9 `memimage` structures.
- Reads optional `vgasize` config as `widthxheightxdepth`; defaults to 1024x768x16.
- Supports RGB16, BGR24, and ARGB32 screen channels.
- Provides `attachscreen()`, `flushmemscreen()`, color stubs, and `blankscreen()`.
- Draws a simple console window and renders kernel text with memdraw fonts.
- Implements scrolling, tab/backspace/newline handling, and `screenputs`.
- Implements software cursor backing store, mask/image generation, movement via `mousexy()`, and periodic cursor refresh.

Integration points: uses VideoCore framebuffer from `vcore.c`, generic draw/memdraw, mouse device hooks, and kernel print path.

Risk notes: `flushmemscreen()` is empty, relying on direct framebuffer visibility. Software cursor races are mitigated with locks but comments acknowledge possible cursor artifacts during inopportune prints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/screen.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/screen.h

This header declares screen, cursor, mouse, and draw integration symbols.

Key content:
- `Cursorinfo` embeds `Cursor` and `Lock`.
- Declares mouse tracking/input functions from `devmouse.c` and mouse control functions.
- Declares `cursor`, `arrow`, screen blanking, framebuffer attach, flush, cursor control, and `setcursor`.
- Declares external `drawlock`.
- Defines `ishwimage(i)` as always true for `devdraw.c`.

Integration points: included by `screen.c` and reused mouse/draw code.

Risk notes: declaring all images as hardware images may affect generic draw assumptions; BCM `hwdraw()` mostly just avoids cursor overlap.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/softfpu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/softfpu.c

This file is a one-line wrapper including `../teg2/softfpu.c`.

It reuses Tegra soft-FPU management code for the BCM build.

Integration points: expected to provide functions declared in `fns.h` such as `fpuinit`, `fpuemu`, `fpuprocsave`, and related process/syscall FPU hooks.

Risk notes: actual FPU policy and trap integration are in the included Tegra source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/softfpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/syscall.c

This file is a one-line wrapper including `../kw/syscall.c`.

It reuses the `kw` syscall implementation for the BCM ARM kernel.

Integration points: called from `lexception.s` `_vsvc` and declared through standard kernel syscall interfaces.

Risk notes: actual syscall dispatch, argument handling, and tracing live in the included `kw` source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/trap.c

This file implements ARM exception, interrupt, fault, FIQ, debug dump, and stack trace handling.

Key behavior:
- `trapinit()` disables interrupts, copies vectors/vtable to high vectors, flushes caches, and sets stacks for FIQ/IRQ/abort/undefined/sys modes.
- `intrsoff()` disables all GPU/ARM interrupt sources and FIQ.
- `irqenable()` registers `Vctl` handlers and enables either GPU, ARM basic, or FIQ interrupt routing.
- `irq()` scans registered interrupts and calls handlers whose pending bits are set.
- `fiq()` dispatches the single FIQ handler.
- `trap()` adjusts PC for exception type, handles IRQ, prefetch abort, data abort, undefined instruction, user notification, and scheduler interaction.
- Data fault handling decodes ARM FSR status into translation, permission, alignment, external abort, and parity cases.
- User faults become notes; kernel faults panic.
- Provides `dumpregs`, `dumpstack`, and `callwithureg`.

Integration points: paired with `lexception.s`, MMU/fault subsystem, FPU emulation, timers, USB FIQ, and all device interrupts.

Risk notes: `irq()` uses a simple linked list and checks all handlers. FIQ is restricted to one source. `writetomem()` instruction decoding is simplified for fault read/write classification.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/uartmini.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/uartmini.c

This file implements the BCM2835 mini UART and basic GPIO helpers.

Key behavior:
- Defines GPIO and AUX register offsets and bits.
- Provides GPIO helpers for function select, pull-off, output set/clear, and input level.
- Defines `miniuart` and `miniphysuart`.
- `enable()` configures GPIO14/15 to ALT5, enables AUX UART, sets 8-bit mode, enables RX/TX, sets baud, and optionally enables interrupts.
- Interrupt handler drains RX and kicks TX.
- `kick()` transmits queued UART output and manages TX interrupt enable.
- Provides UART controls for baud, bits, stop, parity, RTS, status, polling `getc`/`putc`.
- `uartconsinit()` selects console from `console` config.
- `okay()` drives the OK LED GPIO.

Integration points: generic UART layer, console input/output, `clock.c` delays, and `main.c` early console init.

Risk notes: UART frequency defaults to 250 MHz. Flow control comments note CTS/RTS pins are not fully wired. `okay()` uses active-low LED semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/uartmini.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/usbdwc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/usbdwc.c

This file implements the BCM2835 Synopsys DWC OTG USB host controller driver.

Key behavior:
- Registers HCI type `dwcotg`.
- `reset()` validates Synopsys ID, initializes `Hci` callbacks, sets one high-speed port, and registers ARM timer IRQ for wakeups.
- `init()` powers USB, resets core, forces host mode, enables DMA, configures FIFOs, clears interrupts, and enables host channel interrupts.
- Allocates host channels with a bitmap and per-channel rendezvous.
- `chansetup()` programs endpoint address/type/speed/maxpkt and split transaction state.
- `chanio()` performs DMA-backed host channel transfers, handles SOF waits, split retries, ACK/NAK/NYET/stall/error cases, PID/toggle updates, and short packets.
- `ctltrans()` implements USB control setup/data/status phases and buffers IN data for subsequent reads.
- `epread()`/`epwrite()` implement control, bulk, and interrupt endpoint I/O with cache-aligned bounce buffers.
- FIQ handler processes host-channel and SOF interrupts, then schedules ARM timer wakeups for sleepers.
- Port methods implement root-port enable/reset/status mapping to hub status flags.

Integration points: registered through `devusb.c`; uses `dwcotg.h`, `trap.c` FIQ routing, `clock.c` ARM timer, `vcore.c` USB power, and cache maintenance.

Risk notes: comments state work-in-progress limitations: no isochronous pipes, no bandwidth budgeting, crude frame scheduling, optimistic error handling. Split transactions are serialized by a global lock.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/usbdwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/vcore.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/vcore.c

This file implements the mailbox interface to the Raspberry Pi VideoCore GPU.

Key behavior:
- Implements mailbox read/write for property channel and framebuffer channel.
- `vcreq()` builds property-tag messages in `VCBUFFER`, cache-flushes them, sends the bus address, handles a fallback from `BUSDRAM` to zero base, validates response, and copies response data back.
- Framebuffer helpers query defaults, allocate framebuffer, map it with `mmukmap()`, clear it, and blank/unblank display.
- Power helpers set/get device power state.
- Queries Ethernet MAC, firmware revision, ARM RAM size, and clock rates.

Integration points: used by `screen.c`, `main.c`, `emmc.c`, `usbdwc.c`, and network boot environment setup.

Risk notes: uses a single static mailbox buffer and is not reentrant. `getramsize()` assigns `limit = buf[1]`; this assumes firmware returns base/size or base/limit as expected by this port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/vcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/vfp3.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/bcm/vfp3.c

This file is a one-line wrapper including `../teg2/vfp3.c`.

It reuses Tegra VFPv3 support for the BCM build.

Integration points: provides hardware VFP functions declared in `fns.h`, working with `FPsave` in `dat.h` and undefined-instruction/FPU trap logic.

Risk notes: actual VFP register handling and CPU feature probing are in the included Tegra source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/bcm/vfp3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/aux.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/aux.c

This file provides small boot-program utility functions.

Key behavior:
- `warning()` and `fatal()` report errors with current `%r`; `fatal()` exits with an error string.
- `readfile()` and `writefile()` read/write small files.
- `setenv()` creates `#e/name` and writes a value.
- `srvcreate()` posts an fd into `#s` using the basename of the service.
- `catchint()` handles alarm notes for timed prompts.
- `outin()` prompts with a default value, optionally timing out in CPU boot mode.

Integration points: used broadly by boot method code and `boot.c`.

Risk notes: `fatal()` exits in boot context, which comments say triggers panic. `outin()` mutates default buffer only when input length is greater than one.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/aux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/boot.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/boot.c

This file is the main Plan 9 boot program that mounts root and executes init.

Key behavior:
- Reopens console, binds environment and service devices, parses `-k`, `-m`, `-f`.
- Reads debug flags and `cputype`.
- Optionally starts USB discovery and partition service.
- Selects boot method through `rootserver()`, using `nobootprompt`, `bootargs`, command arguments, or interactive prompt.
- Binds devices needed for disks/network/nvram, reads partitions if requested, runs authentication, restarts USB under new hostowner, connects root, mounts namespace, sets time, starts swap, and execs init.
- Supports old 9P compatibility through `/srvold9p`.
- Loads keyboard map from `kbmap` if configured.

Integration points: method table is generated by `mkboot`; method implementations live in local/network/paq/embed helpers.

Risk notes: boot is order-sensitive: USB/nvram/auth/root mount sequencing is deliberate. Some variables such as `PARTSRV` are chmodded after namespace setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/boot.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/boot.h

This header defines the boot-program interface shared by boot helpers.

Key content:
- `Method` struct with `name`, `config`, `connect`, and `arg`.
- Global boot state declarations: boot disk, root directory, cache function, flags, method table, host key, stat buffer, boot args.
- Utility prototypes for auth, cache, env, files, parts, USB, time, fatal/warning, old9p, and method implementations.
- Declares network/local/paq/embed config/connect functions.
- Declares `authaddr` for authentication server address passing.

Integration points: included by all boot helper C files.

Risk notes: declarations are broad and include some legacy/inactive prototypes, so method-specific build configurations determine which symbols must exist.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/boot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/bootauth.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/bootauth.c

This file starts boot-time authentication or falls back to setting hostowner.

Key behavior:
- `authentication()` checks for `/boot/factotum`.
- If present, forks factotum with `-S` for CPU mode or `-u` otherwise, optional debug/options/auth address, and waits for `/mnt/factotum`.
- If factotum is absent, `glenda()` sets `#c/hostowner` to `$user` or `glenda`.

Integration points: called by `boot.c` before root mount. Uses `authaddr` set by network boot configuration.

Risk notes: fallback creates an authentication discontinuity by setting hostowner without factotum.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/bootauth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/bootcache.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/bootcache.c

This file optionally wraps a root file-server fd with the boot cache file system `cfs`.

Key behavior:
- If `/boot/cfs` is absent, returns the original fd.
- Reads `#e/cfs`; `off` disables caching, otherwise an existing listed path can select the cache partition.
- Derives default cache partition from `bootdisk` or global `bootdisk`.
- Forks `/boot/cfs` with `-s -f partition`, plus `-r` when `fflag` is set, and returns pipe fd to cached service.

Integration points: `boot.c` uses global `cfs` function pointer generated by `mkboot` when cfs is included in bootdir.

Risk notes: partition derivation uses suffix stripping heuristics for `disk`, `fs`, and `fossil`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/bootcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/bootip.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/bootip.c

This file implements network configuration and TCP root connection for boot.

Key behavior:
- `configip()` binds IP and Ethernet interfaces into `/net` or `/netX`, forks `/boot/ipconfig`, waits for completion, and optionally prompts for filesystem/auth server IPs.
- Reads IP values from `/net/ndb`, `#e/fs`, and `#e/auth`, falling back to prompts.
- `configtcp()` configures IP and sets `authaddr` to TCP port 567.
- `connecttcp()` dials TCP port 564 on the filesystem server.

Integration points: network boot method uses these functions via the generated `Method` table.

Risk notes: only the first IP interface is configured by `/boot/ipconfig`. Prompting is used if fs/auth addresses are not discoverable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/bootip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/doauthenticate.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/doauthenticate.c

This file implements legacy ticket-based authentication/session support.

Key behavior:
- `readn()` reads an exact byte count or fails.
- `fromauth()` contacts a method-specific auth server, sends a ticket request, parses `AuthOK`/`AuthErr`, and returns tickets or error text.
- `doauthenticate()` performs `fsession`, obtains tickets from auth if needed, calls `fauth`, and falls back with a warning when auth server access fails.
- `checkkey()` checks a user/key pair by requesting and decrypting a ticket.

Integration points: intended for boot methods that provide an auth connection callback. Current `Method` in this `boot.h` lacks `auth`, so this appears legacy or configuration-dependent.

Risk notes: if authentication cannot be completed, it warns and uses the local key as server key, explicitly described as a security hole.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/doauthenticate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/embed.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/embed.c

This file implements booting from an embedded paqfs archive file.

Key behavior:
- `configembed()` selects `paqfile` from explicit `sys` path or method default argument.
- `connectembed()` verifies `/boot/paqfs` and target file, binds console/proc devices, forks `/boot/paqfs -iv paqfile`, passes extra boot args, waits, and returns the pipe fd.

Integration points: used as a boot method through the generated `Method` table.

Risk notes: returns `-1` if target is missing or directory. Child uses both pipe ends for stdin/stdout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/embed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/getpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/getpasswd.c

This file reads a boot-time password from console in raw mode.

Key behavior:
- Opens `#c/consctl`, writes `rawon`, prompts `password:`.
- Reads one byte at a time without echo.
- Handles newline, backspace, and control-U restart.
- NUL-terminates the output buffer.

Integration points: used by boot authentication/key routines.

Risk notes: fatal if console control or read fails. Does not restore raw mode explicitly before returning beyond closing the control fd.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/getpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/local.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/local.c

This file implements local disk boot methods for KFS and Fossil, plus helper process execution.

Key behavior:
- `configlocal()` chooses boot disk from prompt/sys path, MIPS argv convention, method arg, `bootdisk` env, or global fallback, then exports `bootdisk`.
- `connectlocalkfs()` starts `/boot/kfs -f partition -s` on a chosen `fs` partition or device.
- `runv()`/`run()` fork, exec, and wait for helper programs.
- `configloopback()` configures loopback IP for local Venti/Fossil.
- `connectlocalfossil()` detects Fossil config, optionally starts local or network Venti, starts Fossil, opens `#s/fboot`, removes it for reposting, and returns fd.
- `connectlocal()` binds console/proc/storage/USB/AoE devices, mounts USB parts, then tries Fossil before KFS.

Integration points: used by `boot.c` local boot method and by USB/partition discovery.

Risk notes: Fossil/Venti startup includes several heuristics and fixed memory percentages. Local boot depends on partition naming conventions like `<disk>fs` and `<disk>fossil`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/local.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/mkboot -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/mkboot

This rc script generates a boot program C source from a kernel configuration file.

Key behavior:
- Validates one input file argument.
- Emits C includes and a `Method method[]` initializer.
- Uses `../port/mkextract boot` and `awk` to generate method entries mapping method names to `config<name>` and `connect<name>`.
- Parses boot configuration to emit `cpuflag`, `rootdir`, `bootdisk`, selected boot entry function, and `main()`.
- Detects whether `bin/cfs` appears in `bootdir`; emits `int (*cfs)(int) = cache;` or zero.

Integration points: part of the Plan 9 kernel build pipeline for boot images.

Risk notes: parsing is text/awk-based and depends on config file structure and naming conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/mkboot -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/nopsession.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/nopsession.c

This file implements a simple 9P `Tnop` RPC probe.

Key behavior:
- Builds a `Fcall` with `NOTAG`, writes it to fd, reads enough response bytes, tolerates leading `OK`, decodes response, and validates tag/type.
- `nop()` prints progress and sends a `Tnop`.

Integration points: used by boot code variants needing to validate an open 9P connection.

Risk notes: response reading is minimal and assumes small header availability. Fatal on protocol mismatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/nopsession.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/paq.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/paq.c

This file implements a flash-backed paqfs boot method.

Key behavior:
- `configpaq()` binds flash and proc devices, opens flash control, and creates fixed partitions for bootloader, params, kernel, user, and ramdisk.
- `connectpaq()` forks `/boot/paqfs -v -i /dev/flash/ramdisk`, waits, and returns pipe fd.

Integration points: used by generated boot method table for paq systems.

Risk notes: partition offsets/sizes are hard-coded. `configpaq()` fatal message says `bind #c` even though it binds `#F`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/paq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/parts.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/parts.c

This file performs early disk partition discovery for boot, borrowed from 9load.

Key behavior:
- Models disks as `SDunit` with `ctl`, `data`, geometry, and up to 64 partitions.
- `sdaddpart()` validates and writes partition additions to devsd ctl as `part name start end`.
- Reads sectors through `sdread()`/`sdreadblk()`.
- Supports old Plan 9 partition tables on last or second-last sector.
- Supports new Plan 9 `part` tables inside a named partition.
- Parses MBR primary and extended partitions, adds first DOS partition as `dos`, and Plan 9 partitions as `plan9`, `plan9.N`.
- Detects El Torito boot floppy image on ISO9660 CDs and adds `cdboot`.
- `partition()` selects new/old parsing based on `$partition`.
- `readparts()` scans `/dev` for `sd*`, opens ctl/data, reads geometry, and sets partitions.

Integration points: called early by `boot.c` so nvram/factotum can see disk partitions.

Risk notes: buffers are sector-sized up to 2048. The code uses DOS partition structures from `/sys/src/boot/pc/dosfs.h`, an absolute include path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/parts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/printstub.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/printstub.c

This file provides small formatting stubs for boot builds.

Key behavior:
- `_fmtlock()`/`_fmtunlock()` guard formatting with a static `Lock`.
- `_efgfmt()` returns `-1`, likely stubbing floating-point format support.

Integration points: linked into constrained boot environments where full formatting support may not be present.

Risk notes: no functional float formatting; callers needing `%e/%f/%g` behavior would fail.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/printstub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/sac.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/sac.c

This file implements a special standalone boot path that takes over from boot.

Key behavior:
- `configsac()` replaces root namespace, binds `#C`, sets sysname and hostowner to `brick`, then execs `/<cputype>/init -c`.
- `connectsac()` is unreachable and returns `-1`.

Integration points: used as a boot method for a specific SAC/brick configuration.

Risk notes: fixed identity strings and namespace assumptions make this highly specialized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/sac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/settime.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/settime.c

This file sets system time during boot.

Key behavior:
- `settime()` runs once.
- For local boot, tries `#r/rtc`; if absent, prompts for `yymmddhhmm[ss]` and parses it.
- For non-local or unset time, mounts the root service temporarily at `/tmp` and uses root directory access time.
- Writes resulting seconds to `#c/time`.
- `lusertime()` converts compact date/time strings to Unix seconds with leap-year handling.

Integration points: called by `boot.c` after root mount setup and by local Fossil boot before starting Fossil.

Risk notes: manual input parser has minimal validation beyond length. Time fallback depends on mounted root stat data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/settime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/testboot.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/testboot.c

This file is a small test harness for boot commands.

Key behavior:
- Requires a command argument.
- Creates a pipe, forks with fresh fd/name groups, execs the command with pipe stdin/stdout, then mounts the pipe using `amount()` at `/n/kremvax`.

Integration points: used for testing boot file servers or boot command behavior.

Risk notes: hard-coded mount point `/n/kremvax`. Uses `amount`, likely legacy naming for authenticated mount.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/testboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/usb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/boot/usb.c

This file provides boot-time USB discovery and partition-service startup.

Key behavior:
- `start()` runs a helper and waits briefly for a target file to appear.
- `chmod()` changes mode on `/srv/partfs.sdXX`.
- `startpartfs()` starts `/boot/partfs` on `/dev/sdU0.0`, optionally posting `/srv/partfs.sdXX`, and passes 9load `sdB0part` partition data when available.
- `mountusb()` mounts `/srv/usb` into `/dev`.
- `mountusbparts()` mounts USB and starts posted partfs.
- `usbinit()` binds `#u`, starts `/boot/usbd`, waits for first USB disk, and starts partfs.

Integration points: called before and after authentication in `boot.c`, and by local boot to expose USB partitions.

Risk notes: assumes first USB disk is `/dev/sdU0.0`. Discovery waits are fixed polling loops.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/boot/usb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/arp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/arp.c

This file implements IPv4 ARP and IPv6 neighbor resolution cache management for the Plan 9 IP stack.

Key behavior:
- `arpinit()` allocates per-`Fs` ARP state and starts `rxmitproc`.
- Cache is fixed-size 256 entries with 64 hash buckets.
- `arpget()` looks up or creates entries, queues packets while awaiting resolution, and returns locked pending entries to caller.
- `arpenter()` installs resolved MAC addresses, removes IPv6 retransmit entries, and sends queued packets through the interface medium.
- `arpresolve()` marks an entry OK and returns held packets.
- `cleanarpent()` removes an entry from hash/retransmit lists.
- `arpwrite()` supports control commands: `flush`, `add`, and `del`.
- `arpread()` formats cache entries in fixed-width lines.
- `rxmitsols()` handles IPv6 neighbor solicitation retransmits and ICMP unreachable drops.
- `rxmitproc()` sleeps until retransmit/drop work is ready.

Integration points: used by IP interfaces and media implementations through `Medium` address-resolution callbacks; calls routing lookup, ICMPv6 neighbor solicitation, and medium `bwrite`.

Risk notes: cache eviction drops queued IPv4 packets immediately but queues IPv6 drops for ICMP unreachable. Several operations hold the ARP qlock and must avoid calling out until unlocked.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/arp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/chandial.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/chandial.c

This file implements kernel-channel dialing for Plan 9 network clone devices.

Key behavior:
- Parses dial strings of the form `[/net/]proto!dest`.
- Defaults network directory to `/net` and protocol to `net` when no `!` is present.
- Opens `<netdir>/<proto>/clone`, reads the allocated connection directory number, writes `connect dest [local]`, opens the `data` file, and optionally returns the ctl channel and directory path.

Integration points: used by kernel code needing a `Chan*` connection rather than libc `dial`.

Risk notes: parsing is bounded to 128 bytes and truncates longer dial strings. It mutates the clone path buffer to derive the data path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/chandial.c -->
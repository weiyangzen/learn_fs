# Group Research: group_1471_plan9_sources_os_plan9_plan9_sys_src_9_kw_flashkw_c_sources_os_plan_4351509dc55c

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/flashkw.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/flashkw.c

## Role

Kirkwood/SheevaPlug NAND flash driver for Plan 9. It exposes a NAND flash chip through the generic `Flash` interface, including chip identification, erase, page read/write, spare-area ECC handling, and partial-page read-modify-write.

This is directly storage-relevant: it is a raw flash block device implementation, not a filesystem.

## Main Interfaces

- `flashkwlink()`: registers the `"nand"` flash card driver.
- `flashat(Flash *f, uintptr pa)`: probes whether a flash chip exists at a physical address.
- `reset(Flash *f)`: installs `Flash` methods and identifies the chip.
- Internal low-level NAND bus helpers:
  - `nandcmd`, `nandaddr`, `nandread`, `nandreadn`, `nandwrite`, `nandwriten`
  - `nandclaim`, `nandunclaim`
- Flash operations:
  - `erasezone`
  - `read`
  - `write`

## Data Structures

- `Nandreg`: controller registers, including parameter registers and `ctl`.
- `Nandtab`: supported vendor/device table. Includes Hynix `HY27UF084G2M` and a Samsung ID variant.
- `Cache`: single-page software cache with owning `Flash`, page number, page size, and buffer.

## Important Behavior

- Assumes the SheevaPlug NAND interface at a data register address with command/address registers selected by ORing address bits `1` and `2`.
- Uses five-address-cycle NAND page reads and writes.
- Deduces page size, erase block size, and spare bytes from NAND ID byte 4.
- Supports unaligned higher-level reads/writes by reading whole pages into a cache, modifying fragments, then rewriting the page.
- Stores ECC in the last 24 bytes of the spare area: 3 ECC bytes per 256-byte data chunk.
- Reads verify and correct data via `nandecc`/`nandecccorrect`.
- Erase requires erase-block alignment.
- Cache is invalidated on erase and populated after successful reads/writes.

## Dependencies And Assumptions

- Uses Plan 9 flash abstractions from `../port/flashif.h`.
- Uses NAND ECC helpers from `../port/nandecc.h`.
- Depends on Kirkwood SoC mappings in `io.h` and physical constants in `mem.h`.
- Assumes page size and erase size are powers of two.

## Notable Risks

- Partial writes are implemented as read-modify-write on raw NAND; power loss can corrupt the whole page.
- Bad-block handling is mentioned in comments but not implemented here.
- ECC layout is fixed to this driver's convention and may not match all bootloader/Linux layouts.
- Global static page/OOB buffers are not obviously protected against concurrent users.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/flashkw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/fns.h

## Role

Machine-dependent function declaration header for the Kirkwood ARM Plan 9 port. It binds architecture assembly, MMU/cache operations, interrupt functions, PCI helpers, FPU hooks, UART console routines, and port-layer compatibility macros.

This is platform infrastructure used by storage and filesystem-adjacent drivers, but contains no filesystem logic itself.

## Main Interfaces

- Includes `../port/portfns.h`.
- Cache/MMU/CPU helpers:
  - `cachedwb`, `cachedwbinv`, `cachedinv`, `cacheiinv`
  - `l1cacheson`, `l1cachesoff`, `l2cache*`
  - `mmuidmap`, `mmuinvalidate`, `mmukmap`, `mmukunmap`, `vmap`, `vunmap`
- Coprocessor/register helpers:
  - `cpctget`, `cpidget`, `controlget`, `cprd`, `cpwr`, `fsrget`, `farget`
- Trap/interrupt entry points:
  - `vectors`, `vtable`, `intrenable`, `intrdisable`
- FPU emulation hooks:
  - `fpiarm`, `fpuemu`, `fpuprocsave`, `fpuprocrestore`
- PCI configuration helpers.
- Memory allocation aliases for SD and uncached allocation.

## Important Macros

- `coherence` maps to `barriers`.
- `cycles(ip)` stores `lcycles()` into the supplied pointer.
- `CASU`, `CASV`, `CASW` use `cas32`.
- `KADDR` and `PADDR` perform simple segment masking for kernel/physical conversion.
- `waserror()` expands to Plan 9 error-label stack setup.

## Dependencies And Assumptions

- Assumes ARM Kirkwood assembly symbols from `l.s`, `lexception.s`, and `lproc.s`.
- Assumes Plan 9 `Proc`, `Ureg`, `Pcidev`, `Block`, and allocation APIs exist.
- `KADDR`/`PADDR` are simple segment conversions, so callers must not pass arbitrary unmapped addresses.

## Notable Risks

- Header mixes public prototypes, macros, and low-level compatibility shims.
- Several macros hide architecture-specific behavior and are unsafe if reused outside this address-space model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/fpiarm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/fpiarm.c

## Role

ARM floating-point instruction emulator for the Kirkwood port. It decodes old ARM FPA-style floating-point instructions, emulates arithmetic through Plan 9's portable floating-point package, and also handles a few special atomic instruction encodings.

This is CPU trap support, not filesystem code.

## Main Interfaces

- `fpiarm(Ureg *ur)`: emulates consecutive FP/special instructions starting at the trapped PC.
- Special instruction helpers:
  - `casemu`
  - `ldrex`
  - `strex`
  - `clrex`
- Internal FP operation helpers:
  - binary: `fadd`, `fsub`, `fsubr`, `fmul`, `fdiv`, `fdivr`
  - unary: `fmov`, `fmovn`, `fabsf`, `frnd`
  - load/store: `fld`, `fst`
  - compare: `fcmp`

## Important Behavior

- Uses `FPsave` in the current `Proc` as the emulated FPU register state.
- Initializes FP state lazily when a process first executes an FP instruction.
- Decodes conditional execution with `condok`.
- Supports FPA load/store, register transfers, compare operations, and arithmetic operations.
- Unsupported FP instructions call `unimp`, which raises a Plan 9 error.
- `casemu` validates user memory and emulates a compare-and-swap-like operation.
- `ldrex`/`strex` use a global `ldrexvalid` flag, which models only a very coarse exclusive monitor.

## Dependencies And Assumptions

- Uses `../port/fpi.h` for the portable internal FP representation.
- Uses `Ureg` layout offsets to read and write general registers.
- Assumes `up` is non-nil and points to the current process.
- Relies on `validaddr`, `splhi`, and `spllo` for safe memory access and atomicity.

## Notable Risks

- Does not fully model ARM FP trap status or all FP exception semantics.
- Exclusive monitor emulation is global and simplified.
- Unsupported instruction paths raise process errors rather than providing complete architecture coverage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/fpiarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/init9.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/init9.s

## Role

Small ARM assembly startup wrapper for the user-level boot program. It sets the static base register and calls `startboot`.

This is boot/bootstrap glue, not filesystem code.

## Main Interface

- `TEXT main(SB), 1, $8`

## Important Behavior

- Loads `setR12(SB)` into `R12` to establish the Plan 9 static base.
- Places `boot(SB)` and an argument vector pointer on the stack.
- Calls `startboot(SB)`.
- Loops forever if `startboot` returns.

## Dependencies And Assumptions

- Assumes ARM Plan 9 calling conventions.
- Assumes `boot` and `startboot` symbols are linked into the boot image.

## Notable Risks

- Minimal bootstrap code with no error path; returning from `startboot` hangs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/io.h

## Role

Kirkwood platform I/O and bus definition header. It defines PCI bus IDs/config registers, Kirkwood SoC physical register addresses, interrupt controller layout, CPU control/status registers, PCIe register maps, and window target/attribute constants.

This is platform hardware description used by drivers, including storage/network/USB drivers.

## Main Contents

- Bus encoding macros:
  - `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`
- PCI config offsets and class/subclass constants.
- `Pcidev` and `Pcisiz` structures.
- Kirkwood address constants:
  - `AddrMpp`
  - `AddrSdio`
  - `Addrpci`
  - `Addrpcibase`
  - `AddrEfuse`
- Interrupt groups and IRQ bit numbers for low, high, and bridge interrupts.
- Register structures:
  - `IntrReg`
  - `CpucsReg`
  - `Pciex`
- MBUS target/attribute constants for DRAM, flash, NAND, SPI, boot ROM, and security SRAM windows.

## Important Behavior

- Provides the constants used by `trap.c`, `sdio.c`, `usbehcikw.c`, PCI code, and board setup.
- Encodes Kirkwood-specific interrupt numbering, including SDIO, USB, SATA, Ethernet, UART, GPIO, PCIe, and RTC interrupt bits.
- Defines cache/L2 and reset-control bit meanings used by platform initialization and reboot.

## Dependencies And Assumptions

- Assumes `PHYSIO` and address-space macros from `mem.h`.
- Assumes little-endian interrupt cause bit numbering as documented in comments.

## Notable Risks

- Hardware register layout definitions are brittle and must match the SoC manual.
- Some PCIe fields are partially modeled, with comments indicating incomplete coverage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/l.s

## Role

Core ARM assembly for the Kirkwood kernel: reset/startup, first page-table construction, cache and MMU control, coprocessor register access, interrupt priority primitives, atomic operations, labels, idle, and memory barriers.

This is low-level kernel architecture support, not filesystem code.

## Main Interfaces

- Boot/reset:
  - `_start`
  - `_reset`
  - `_r15warp`
  - `myputc`
- Cache control:
  - `l1cacheson`, `l1cachesoff`
  - `cachedwb`, `cachedwbse`
  - `cachedwbinv`, `cachedwbinvse`
  - `cachedinv`, `cachedinvse`
  - `cacheuwbinv`, `cacheiinv`
  - `l2cachecfgon`, `l2cachecfgoff`
  - `l2cacheuwb`, `l2cacheuwbse`, `l2cacheuwbinv`, `l2cacheuwbinvse`
  - `l2cacheuinv`, `l2cacheuinvse`
- MMU/register access:
  - `mmuenable`, `mmudisable`
  - `mmuinvalidate`, `mmuinvalidateaddr`
  - `cpidget`, `cpctget`, `controlget`, `ttbget`, `ttbput`
  - `dacget`, `dacput`, `fsrget`, `farget`, `pidget`, `pidput`
- Interrupt priority:
  - `splhi`, `spllo`, `splx`, `splxpc`, `spldone`, `islo`, `splfhi`
- Atomics/control:
  - `tas`, `_tas`, `clz`, `setlabel`, `gotolabel`, `getcallerpc`
  - `_idlehands`, `barriers`

## Important Behavior

- `_start` builds initial section mappings and L2 page tables before jumping into C `main`.
- Creates mappings for DRAM, IO registers, boot ROM, and kernel/user areas.
- Manages ARM control register bits for MMU, caches, branch prediction, alignment, and high vectors.
- Cache helpers use ARM CP15 operations and explicit wait/barrier loops.
- `tas` uses `LDREX`/`STREX` style exclusive access for atomic test-and-set.
- `spl*` manipulates IRQ/FIQ mask bits in CPSR.

## Dependencies And Assumptions

- Includes `arm.s`.
- Assumes the memory layout in `mem.h`, including `KZERO`, `L1`, and physical IO constants.
- Assumes single-core or simple exclusive access semantics matching this Kirkwood port.

## Notable Risks

- Startup page-table setup is tightly bound to physical address constants.
- Cache/MMU ordering errors here can corrupt all higher-level subsystems.
- Many routines are called from C via declarations in `fns.h`; signatures must stay synchronized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/lexception.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/lexception.s

## Role

ARM exception vector and trap-entry assembly for the Kirkwood kernel. It defines vector stubs, saves register state, switches stack modes, and calls C handlers for traps, syscalls, IRQs, and FIQs.

This is trap infrastructure, not filesystem code.

## Main Interfaces

- `vectors(SB)`: vector branch table.
- `vtable(SB)`: vector target table.
- Exception stubs:
  - `_vrst`
  - `_vsvc`
  - `_vund`
  - `_vpabt`
  - `_vdabt`
  - `_virq`
  - `_vfiq`
- `setr13(SB)`: sets mode-specific stack pointer.

## Important Behavior

- SWI/syscall entry saves user state, adjusts return PC, switches to supervisor mode, and calls `syscall`.
- Undefined instruction, prefetch abort, data abort, and IRQ paths build a `Ureg` frame and call `trap`.
- IRQ entry separately handles interrupt masking and stack switching.
- User exceptions restore user registers and resume via exception return semantics.
- FIQ path acknowledges with a minimal return sequence.

## Dependencies And Assumptions

- Includes `arm.s`.
- Assumes `Ureg` layout and PSR mode constants match `ureg.h`/`arm.h`.
- Calls C functions `syscall` and `trap`.

## Notable Risks

- Register save/restore layout must exactly match C `Ureg`.
- Any mismatch in mode-specific stack setup can corrupt kernel or user state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/lproc.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/lproc.s

## Role

Small ARM process transition assembly for entering user mode and returning from fork.

This is process-control infrastructure, not filesystem code.

## Main Interfaces

- `touser(SB)`: enters user mode at a supplied user entry PC.
- `forkret(SB)`: returns from a forked process into scheduler/user restore flow.

## Important Behavior

- `touser` sets up CPSR/SPSR state for user execution, loads the user stack pointer, and exception-returns into user mode.
- `forkret` loads the current process saved scheduler label, clears the process pointer in `m->proc`, and jumps through `gotolabel`.

## Dependencies And Assumptions

- Includes `mem.h` and `arm.h`.
- Assumes `Mach`/`Proc` offsets used in assembly match `dat.h`.
- Relies on Plan 9 ARM exception return conventions.

## Notable Risks

- Offset drift between assembly and C structs would break context switching.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/main.c

## Role

Kirkwood kernel C entry and board initialization. It parses boot configuration, initializes CPU/MMU/traps/devices, creates the first user process, configures memory, and implements reboot/shutdown support.

This is OS/platform bring-up. It indirectly supports filesystems by initializing device and memory infrastructure.

## Main Interfaces

- Kernel entry and setup:
  - `main(Mach *mach)`
  - `machinit`
  - `cpuidprint`
  - `confinit`
  - `userinit`
  - `init0`
- Boot configuration:
  - `getconf`
  - `addconf`
  - `getenv`
  - `plan9iniinit`
  - `optionsinit`
  - `bootargs`
- Shutdown/reboot:
  - `exit`
  - `reboot`
- Utility:
  - `cmpswap`
  - `spiprobe`
  - `probeaddr` is declared and used for probing memory.

## Important Behavior

- Reads boot arguments from `CONFADDR` into a parsed `confname`/`confval` table.
- Initializes UART console early, MMU, traps, clocks, links, page allocator, process subsystem, and device roots.
- Builds and starts the initial user process using `initcode`.
- `confinit` determines memory size using configured `memsize` or probing.
- `reboot` copies reboot code to low memory, turns off interrupts/caches, and jumps to supplied entry code.
- `spiprobe` reads SPI flash register bytes for diagnostic output.

## Dependencies And Assumptions

- Includes `init.h`, `arm.h`, `io.h`, `tos.h`, and pool definitions.
- Assumes Kirkwood memory layout from `mem.h`.
- Assumes one CPU (`MAXMACH` is 1 in `mem.h`).

## Notable Risks

- Boot configuration parsing is small and fixed-size (`MAXCONF`, `MAXCONFLINE`).
- Memory probing and reboot code operate near raw physical addresses.
- Early console and panic paths depend on hardware UART availability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/mem.h

## Role

Kirkwood ARM memory-layout and machine-constant header. It defines page size, kernel segments, user/kernel address bounds, timing constants, cache line size, PTE flags, and physical device addresses.

This is platform memory infrastructure used by MMU, drivers, and storage code.

## Main Contents

- Size units: `KiB`, `MiB`, `GiB`.
- Page and stack constants:
  - `BY2PG`, `PGSHIFT`, `KSTKSIZE`, `STACKALIGN`
- Kernel/user layout:
  - `KSEG0`, `KZERO`, `KTZERO`, `CONFADDR`, `L1`
  - `UZERO`, `UTZERO`, `USTKTOP`, `USTKSIZE`, `TSTKTOP`
- Time/cache constants:
  - `CLOCKFREQ`
  - `CACHELINESZ`
- PTE and color constants:
  - `PTEVALID`, `PTEWRITE`, `PTEKERNEL`, `PTEMAPMEM`
- Physical addresses:
  - `PHYSDRAM`
  - `PHYSIO`
  - `PHYSCONS`
  - `PHYSNAND1`
  - `PHYSNAND2`
  - `PHYSSPIFLASH`
  - `PHYSBOOTROM`
- `VIRTIO` maps IO virtually at the same base as physical IO.

## Important Behavior

- Establishes the kernel virtual segment at `0x60000000`.
- Uses a 4 KiB page size.
- Sets the Kirkwood TCLK clock frequency to 200 MHz.
- Defines direct physical constants consumed by NAND, UART, SDIO, USB, and MMU code.

## Dependencies And Assumptions

- Assumes single-machine build (`MAXMACH 1`).
- Assumes kernel physical/virtual mapping conventions used by `l.s` and `mmu.c`.

## Notable Risks

- Constants are global architectural contracts; changing one requires auditing assembly and C code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/mmu.c

## Role

Kirkwood ARM MMU management. It initializes kernel mappings, manages per-process L1/L2 page-table entries, switches address spaces, maps kernel IO windows, and supports uncached/vmapped memory.

This is virtual-memory infrastructure with direct impact on driver DMA and storage buffers.

## Main Interfaces

- Diagnostics/init:
  - `mmudump`
  - `mmuidmap`
  - `mmuinit`
- Process MMU:
  - `mmuswitch`
  - `flushmmu`
  - `mmurelease`
  - `putmmu`
- Kernel mappings:
  - `mmuuncache`
  - `mmukmap`
  - `mmukunmap`
  - `cankaddr`
  - `vmap`
  - `vunmap`

## Important Behavior

- `mmuinit` maps kernel segments, IO, boot ROM, and configured physical memory.
- Uses ARM L1 section mappings and L2 small page mappings.
- Maintains per-process L1/L2 tables through `Proc.pmmu`.
- `putmmu` allocates L2 tables as needed and installs user mappings with appropriate AP/cache bits.
- Flushes D/I caches and invalidates TLBs on mapping changes.
- `vmap` allocates kernel virtual space and maps physical pages for device access.
- `mmuuncache` clears cacheable/bufferable bits for a virtual address range.

## Dependencies And Assumptions

- Uses ARM PTE constants from `arm.h`.
- Uses `KMAP`, `KZERO`, `PTEMAPMEM`, and physical constants from `mem.h`.
- Relies on assembly helpers from `l.s`.

## Notable Risks

- TLB/cache ordering is critical and manually maintained.
- `mmuuncache` mutates page-table attributes in place and must be used carefully with live cached aliases.
- Kernel mapping functions assume ranges are page-aligned or roundable to pages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/plug.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/plug.c

## Role

Static kernel configuration for the Kirkwood Plan 9 build. It declares compiled-in device tables, link functions, SD interfaces, UART implementations, IP protocol initializers, boot settings, and the embedded textual config file.

This is configuration glue. It includes storage-relevant device selection through flash, SD, AoE, USB, and filesystem devices.

## Main Interfaces

- `devtab[]`: root/cons/env/pipe/proc/mnt/srv/rtc/arch/aoe/sd/fs/flash/twsi/ether/ip/uart/usb and other devices.
- `links()`: invokes compiled-in linker registration functions.
- `sdifc[]`: includes `sdaoeifc`.
- `physuart[]`: includes `kwphysuart`.
- `ipprotoinit[]`: TCP, UDP, IP interface, ICMP, ICMPv6, IP mux.
- Global config:
  - `cpuserver = 1`
  - `i8250freq = 3686000`
  - `conffile`
  - `kerndate`
  - `configfile[]`

## Important Behavior

- Registers Kirkwood Ethernet, architecture, flash, network medium, loopback, and EHCI USB support.
- Embeds the kernel configuration as a byte array terminated by zero.
- The embedded config comments identify target boards such as SheevaPlug, OpenRD client, GuruPlug, and DreamPlug.

## Dependencies And Assumptions

- Depends on each referenced `Dev`, link function, SD interface, UART, and IP initializer being linked.
- The byte-array config must match build-time expectations.

## Notable Risks

- Stale static device tables can include dead or missing devices.
- The embedded config is not human-editable in this generated C form.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/plug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/rebootcode.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/rebootcode.s

## Role

Standalone ARM reboot trampoline copied to low memory by `main.c:reboot`. It disables caches/MMU, sets temporary mappings, copies replacement code, and jumps to the new entry point.

This is reboot/bootstrap infrastructure, not filesystem code.

## Main Interfaces

- `main(SB)`: reboot trampoline entry.
- `cachesoff(SB)`: disables cache state.
- `_r15warp(SB)`: branch/jump helper.
- `mmudisable(SB)`
- `mmuinvalidate(SB)`
- `cacheuwbinv(SB)`

## Important Behavior

- Runs at a fixed copied location with arguments describing destination entry, source code pointer, and size.
- Copies the supplied code in words.
- Builds or reuses temporary page-table entries enough to execute during transition.
- Flushes and invalidates caches, disables MMU, invalidates TLBs, and jumps to the new entry.

## Dependencies And Assumptions

- Includes `arm.s`.
- Must stay position-safe enough for copying/execution as reboot code.
- Called by `reboot` in `main.c`.

## Notable Risks

- Any cache/MMU mistake can hang the machine during reboot.
- Source/destination size assumptions are raw and unchecked at this level.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/sdio.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/sdio.c

## Role

Kirkwood SDIO/MMC host driver implementing the Plan 9 `SDio` interface. It sends SD commands, manages responses, sets up DMA, handles read/write data transfers, and services SDIO interrupts.

This is directly storage-relevant: it is the SD/MMC block-device host controller backend.

## Main Interfaces

- `sdioinit`
- `sdioinquiry`
- `sdioenable`
- `sdiocmd`
- `sdioiosetup`
- `sdioread`
- `sdiowrite`
- `sdioio`
- `sdiointerrupt`

## Data Structures

- `Ctlr`: controller state including initialization, command buffer, interrupt status, wait rendezvous, and DMA bookkeeping.
- Register constants cover SDIO system address, block size/count, command, transfer mode, response registers, status, interrupt enables, clock, host control, and software reset.

## Important Behavior

- Uses `soc.sdio` as the controller register base.
- `WR` writes a register and reads it back for ordering.
- Sets SDIO clock divisors with `clkdiv`.
- Waits for command completion and transfer completion through interrupt status polling/wakeup.
- Handles 48-bit and 136-bit response formats.
- Sets up DMA by writing the physical address of the buffer.
- Read/write paths consume controller data availability and DMA done status.
- On errors, reports command/data timeout, CRC, index, end-bit, and DMA errors.

## Dependencies And Assumptions

- Implements an `SDio` backend consumed by the Plan 9 SD layer.
- Depends on `AddrSdio`/IRQ constants in `io.h`.
- Uses cache coherence helpers around DMA-relevant memory.

## Notable Risks

- DMA buffers must be physically addressable and coherent.
- Timeout constants and interrupt status handling are hardware-specific.
- Multi-block and error-recovery behavior is tightly coupled to controller status bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/sdio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/softfpu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/softfpu.c

## Role

Soft-FPU integration shim for the Kirkwood port. It provides the Plan 9 kernel FPU hook functions while delegating actual FP instruction emulation to `fpiarm`.

This is CPU emulation glue, not filesystem code.

## Main Interfaces

- `fpudevprocio`
- `fpunotify`
- `fpunoted`
- `fpusysrfork`
- `fpusysrforkchild`
- `fpuprocsave`
- `fpuprocrestore`
- `fpusysprocsetup`
- `fpuinit`
- `fpuemu`

## Important Behavior

- Most process lifecycle hooks are no-ops because FP state is stored in the `Proc`.
- `fpudevprocio` rejects access with `"no floating point status"`.
- `fpuemu` calls `fpiarm(ureg)`.

## Dependencies And Assumptions

- Assumes software FP emulation only; no hardware FPU context management is needed.
- Depends on `fpiarm.c`.

## Notable Risks

- Exposes no useful FPU status through device/proc IO.
- Hardware FPU support would require replacing these no-op hooks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/softfpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/syscall.c

## Role

ARM syscall and notify handling for the Kirkwood kernel. It dispatches system calls, manages user notification return, prepares exec/fork register state, and records syscall tracing/profiling metadata.

This is kernel process ABI code. It supports filesystem syscalls through the shared Plan 9 syscall table but does not implement filesystem operations itself.

## Main Interfaces

- `syscall(Ureg *ureg)`: main syscall dispatcher.
- `notify(Ureg *ureg)`: prepares user notification delivery.
- `noted(Ureg *cur, uintptr arg0)`: handles `noted` return modes.
- `execregs`
- `sysprocsetup`
- `forkchild`

## Important Behavior

- Extracts syscall number and arguments from user register/stack state.
- Validates user memory for syscall arguments.
- Calls `systab[scallnr]`.
- Handles Plan 9 error unwinding through `waserror`/`nexterror`.
- Supports syscall tracing through `syscallfmt`/`sysretfmt`.
- `notify` builds a user stack frame containing saved registers and note string.
- `noted` supports `NCONT`, `NRSTR`, `NSAVE`, and `NDFLT`.
- `execregs` initializes user stack, PC, and return registers for a new image.
- `forkchild` copies a parent `Ureg` and makes child return zero.

## Dependencies And Assumptions

- Depends on `../port/systab.h`, `tos.h`, and port process code.
- Assumes ARM `Ureg` layout and syscall ABI.
- Uses `validaddr`, `validalign`, and `evenaddr`.

## Notable Risks

- User stack/register manipulation is ABI-sensitive.
- Incorrect validation around user pointers would affect every syscall, including filesystem syscalls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/trap.c

## Role

Kirkwood ARM trap, fault, and interrupt controller handling. It routes hardware IRQs, initializes high-vector exception tables, handles page faults, invokes FP emulation for undefined instructions, and provides debugging dump helpers.

This is core kernel exception infrastructure, not filesystem code.

## Main Interfaces

- Interrupt management:
  - `intrenable`
  - `intrdisable`
  - `intrclear`
  - `intrmask`
  - `intrunmask`
  - `intrhi`
  - `intrbridge`
  - `intrfmtcounts`
- Trap/fault:
  - `trapinit`
  - `trap`
  - `faultarm`
  - `writetomem`
- Debug/utility:
  - `dumpregs`
  - `dumpstack`
  - `callwithureg`
  - `probeaddr`
  - `idlehands`

## Data Structures

- `Handler`: installed handler entry with function, arg, name, and counter.
- `Irq`: per-interrupt handler table with mask/cause register pointers.
- `Vctl`: local interrupt control structure.

## Important Behavior

- Supports low, high, and bridge interrupt groups.
- `trapinit` masks interrupts, copies vector code to high vectors, sets up stacks, and initializes interrupt tables.
- `intrs` scans pending interrupt bits and calls installed handlers.
- Fault handling distinguishes user/kernel faults and read/write status.
- Page faults call Plan 9 `fault`; unresolved kernel faults panic.
- Undefined instructions are first offered to `fpiarm` for emulation.
- `probeaddr` safely tests whether a physical/virtual address can be read.

## Dependencies And Assumptions

- Uses Kirkwood interrupt register layout from `io.h`.
- Uses ARM fault status/address register helpers from `l.s`.
- Calls VM fault handling and Plan 9 note delivery.

## Notable Risks

- Shared interrupt handler tables are fixed-size.
- Fault recursion/stuck fault detection is heuristic.
- Interrupt masking and clear semantics must match Kirkwood hardware exactly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/uartkw.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/uartkw.c

## Role

Kirkwood UART driver implementing Plan 9 `PhysUart`. It supports console registration, interrupt-driven input/output, baud/format configuration, and early serial output helpers.

This is console/serial hardware support, not filesystem code.

## Main Interfaces

- `kwphysuart`: physical UART operations table.
- `uartkirkwoodconsole`
- `serialputc`
- `serialputs`
- Internal operations:
  - `kw_pnp`
  - `kw_enable`
  - `kw_disable`
  - `kw_kick`
  - `kw_intr`
  - `kw_read`
  - `kw_getc`
  - `kw_putc`
  - `kw_baud`, `kw_bits`, `kw_stop`, `kw_parity`

## Data Structures

- `UartReg`: register layout for receiver/transmitter, interrupt enables, FIFO, line control, modem/status, scratch, and divisor registers.
- `Ctlr`: per-controller state with register pointer and enabled flag.
- Static `Uart` for the Kirkwood console.

## Important Behavior

- Uses `PHYSCONS` as the UART register base.
- Interrupt handler reads RX data and drains TX FIFO via Plan 9 UART helper callbacks.
- Baud changes program divisor latch registers.
- `serialputc` writes directly for early/last-resort output.

## Dependencies And Assumptions

- Depends on UART framework types and helpers.
- Uses interrupt `IRQ1uart0`.
- Assumes 16550-like register behavior.

## Notable Risks

- Early direct serial output bypasses normal locking.
- Hardware FIFO and modem control behavior is only minimally implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/uartkw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/uncached.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/uncached.h

## Role

Header that redirects allocation APIs to uncached allocation variants for code that includes it. It provides wrappers for zeroed uncached allocation.

This is memory-allocation support for DMA/device code, not filesystem logic.

## Main Interfaces

- Macro remaps:
  - `free` -> `ucfree`
  - `malloc` -> `myucalloc`
  - `mallocz` -> `ucallocz`
  - `smalloc` -> `myucalloc`
  - `xspanalloc` -> `ucallocalign`
  - `allocb` -> `ucallocb`
  - `iallocb` -> `uciallocb`
  - `freeb` -> `ucfreeb`
- Static helpers:
  - `ucallocz`
  - `myucalloc`

## Important Behavior

- Forces ordinary allocation calls in an including file to use uncached memory.
- `ucallocz` ignores the second argument and allocates zeroed uncached memory.
- `myucalloc` panics on allocation failure.

## Dependencies And Assumptions

- Requires uncached allocation functions declared in `fns.h`.
- Intended for inclusion in specific driver translation units, not globally.

## Notable Risks

- Macro replacement can surprise included code and change ownership/freeing expectations.
- The header creates static functions in each including file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/uncached.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/usbehci.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/usbehci.h

## Role

EHCI host-controller private header for the Kirkwood USB driver. It defines controller state, polling synchronization, operational register layout, debug macros, and linkage prototypes used by `usbehcikw.c` and generic EHCI code.

This is USB host infrastructure, indirectly storage-relevant for USB mass storage.

## Main Contents

- Debug macro overrides:
  - `dprint`, `ddprint`, `deprint`, `ddeprint`
- Opaque types:
  - `Ctlr`, `Eopio`, `Isoio`, `Poll`, `Qh`, `Qtree`
- `Poll`: lock/rendezvous state for polling.
- `Ctlr`: EHCI controller state, frame list, async queue heads, periodic tree, interrupt counters, and load accounting.
- `Eopio`: EHCI operational registers plus Kirkwood/Freescale-specific extension registers.
- Prototypes:
  - `ehcilinkage`
  - `ehcimeminit`
  - `ehcirun`

## Important Behavior

- Models standard EHCI operational registers and the Kirkwood-specific extra OTG/device-mode/Freescale registers.
- `Ctlr` embeds both synchronization and hardware list state.

## Dependencies And Assumptions

- Depends on `Hci`, `Ecapio`, endpoint debug fields, and USB types from port USB headers.
- Assumes one-port EHCI layout in `portsc[1]`.

## Notable Risks

- Register layout includes undocumented or semi-documented vendor extensions.
- Generic EHCI and Kirkwood-specific code must agree on structure layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/usbehcikw.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/usbehcikw.c

## Role

Kirkwood-specific EHCI USB host-controller driver glue. It configures address windows, resets the controller, wires generic EHCI methods into Plan 9's USB `Hci` interface, and registers the controller.

This is USB hardware support, indirectly storage-relevant for USB disks.

## Main Interfaces

- `usbehcilink()`: registers the EHCI controller type.
- HCI operations:
  - `reset`
  - `shutdown`
  - `setdebug`
- Internal setup:
  - `findehcis`
  - `ehcireset`
  - `ctlrreset`
  - `setaddrwin`
  - `addrmapdump`

## Data Structures

- `Kwusbtt`: target translation registers for USB address decode.
- `Kwusb`: Kirkwood USB register block including bridge, address windows, control, error status, and capability/control areas.
- `Usbwin`: decoded address window metadata.

## Important Behavior

- Configures up to four USB address decode windows for DRAM chip-select regions.
- Resets and halts EHCI, clears interrupts, configures all ports to host controller routing, and sets USB mode to host.
- Allocates a `Ctlr`, initializes generic EHCI memory, and runs the controller.
- Uses fixed Kirkwood addresses rather than PCI discovery.

## Dependencies And Assumptions

- Includes generic USB/EHCI headers and `usbehci.h`.
- Uses global `soc.ehci`.
- Assumes Kirkwood-style address windows and one EHCI controller.

## Notable Risks

- Address-window setup must match physical DRAM layout or DMA will fail.
- Fixed-address discovery limits portability to this SoC family.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/usbehcikw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/clock.c

## Role

Clock and delay implementation for the Plan 9 MTX PowerPC port. It configures the decrementer interrupt, tracks ticks, and supplies busy-wait delay and timestamp helpers.

This is platform timing infrastructure, not filesystem code.

## Main Interfaces

- `delayloopinit`
- `clockinit`
- `clockintr`
- `timerset`
- `delay`
- `microdelay`
- `fastticks`
- `µs`
- `perfticks`

## Important Behavior

- Computes `m->loopconst` from CPU frequency for busy-wait delay loops.
- Sets `m->dechz` to `m->bushz / 4`.
- Programs PowerPC decrementer through `putdec`.
- `clockintr` reloads the decrementer and calls `timerintr`.
- `fastticks` returns `m->ticks`; this is a low-resolution fallback.

## Dependencies And Assumptions

- Uses PowerPC decrementer accessors from assembly.
- Assumes `m->cpuhz` and `m->bushz` are initialized elsewhere.

## Notable Risks

- Busy-wait calibration is crude and CPU-frequency dependent.
- `fastticks` is tick-based, not true high-resolution cycle time.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/cycintr.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/cycintr.c

## Role

Stub timer scheduling hooks for the MTX port. It declares that no cycle timer is available and leaves timer add/delete/scheduler interrupt functions empty.

This is timing infrastructure placeholder code, not filesystem code.

## Main Interfaces

- `havetimer()`
- `timeradd(Timer *)`
- `timerdel(Timer *)`
- `clockintrsched()`

## Important Behavior

- `havetimer` returns `0`.
- The other functions are no-ops.

## Dependencies And Assumptions

- Included to satisfy shared kernel timer interfaces.
- Assumes the MTX port does not use the generic cycle-timer queue here.

## Notable Risks

- Any subsystem expecting high-resolution timer support will not get it from this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/cycintr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/dat.h

## Role

Machine-dependent data structure header for the MTX PowerPC Plan 9 port. It defines locks, labels, FPU state, memory configuration, MMU process state, machine state, ISA configuration, and global CPU/process registers.

This is kernel platform state, not filesystem logic.

## Main Contents

- Typedefs for core machine structures: `Conf`, `FPsave`, `Mach`, `Proc`, `Ureg`, `Vctl`, etc.
- `Lock`: includes key, saved status register, PC, owning proc/mach, and interrupt-lock flag.
- `Label`: stack and PC for context switching.
- FPU states: `FPinit`, `FPactive`, `FPinactive`, `FPillegal`.
- `FPsave`: 32 floating registers plus FPSCR.
- `Conf`/`Confmem`: memory and kernel sizing.
- `PMMU`: process MMU PID.
- Fake `kmap` macros for direct kernel mapping.
- `Mach`: per-CPU state including scheduler label, clocks, performance, MMU/TLB fields, and stack.
- `ISAConf`: parsed ISA configuration.
- `MACHP`, `mach0`, and register globals `m`/`up`.

## Important Behavior

- Includes shared `../port/portdat.h` after defining machine-dependent prerequisite structures.
- Defines Plan 9 AOUT magic as `Q_MAGIC`.
- `MACHP(n)` indexes CPUs by page-sized `Mach` areas.

## Dependencies And Assumptions

- Assembly in `mtx/l.s` depends on early `Mach` field offsets.
- Assumes PowerPC FPU save layout matches assembly `fpsave`/`fprestore`.

## Notable Risks

- Struct layout changes can break assembly.
- Fake `kmap` assumes direct physical-to-kernel address mapping.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/devarch.c

## Role

MTX architecture device implementation, exposing architecture-specific files and managing I/O port allocation. It implements the `#P/arch` device table used to inspect and mutate low-level machine state.

This is platform device support, not filesystem implementation, though it exposes a Plan 9 device namespace.

## Main Interfaces

- `addarchfile`
- `ioinit`
- `ioalloc`
- `iofree`
- `iounused`
- Device operations:
  - `archattach`
  - `archwalk`
  - `archstat`
  - `archopen`
  - `archclose`
  - `archread`
  - `archwrite`
- PCMCIA stubs:
  - `pcmspecial`
  - `pcmspecialclose`

## Data Structures

- `IOMap`: linked list node describing allocated or free I/O port ranges.
- `archdir[]`: dynamic architecture file directory entries.
- `readfn[]` and `writefn[]`: per-arch-file callbacks.

## Important Behavior

- Tracks I/O port ownership with a sorted linked list.
- `ioalloc` supports explicit port ranges or dynamic allocation with alignment.
- `iofree` releases exact ranges.
- Architecture files can be added dynamically with callbacks.
- Device read/write dispatches based on QID path and callback arrays.

## Dependencies And Assumptions

- Uses Plan 9 `Dev`/`Chan`/`Dirtab` conventions.
- Assumes x86-like I/O port concepts for this platform layer.

## Notable Risks

- I/O range allocation is manually managed and can fragment.
- `checkport` raises errors for invalid ranges, so callers must validate hardware claims.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/devether.c

## Role

Generic Ethernet network device frontend for the MTX port. It exposes Ethernet interfaces through Plan 9 device files and dispatches to registered hardware drivers such as `ether2114x`.

This is network device infrastructure, not filesystem code.

## Main Interfaces

- Device operations:
  - `etherattach`, `etherwalk`, `etherstat`, `etheropen`, `etherclose`
  - `etherread`, `etherbread`, `etherwrite`, `etherbwrite`
- Packet queues:
  - `etheriq`
  - `etheroq`
- Driver registration and setup:
  - `addethercard`
  - `etherreset`
- Utilities:
  - `parseether`
  - `ethercrc`

## Important Behavior

- Uses the Plan 9 `netif` framework for clone/data/control/stats files.
- `etheriq` dispatches received packets to matching network files, supports promiscuous taps, and handles bridge input.
- `etheroq` pads short frames, updates output counters, and calls the hardware transmit function.
- `etherwrite` handles control writes separately from raw packet writes.
- `etherreset` attempts each registered card reset routine.
- `ethercrc` computes Ethernet CRC using polynomial `0xedb88320`.

## Dependencies And Assumptions

- Includes `../port/netif.h` and `etherif.h`.
- Hardware drivers register through `addethercard`.

## Notable Risks

- Packet fanout and promiscuous handling are shared across all Ethernet devices.
- Hardware driver reset order depends on static registration order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/devrtc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/devrtc.c

## Role

MTX real-time clock and NVRAM device. It exposes `/dev/rtc` and `/dev/nvram`, supports BCD time conversion, checksum maintenance, and a watchdog reset hook.

This is time/NVRAM device support, not filesystem code.

## Main Interfaces

- Device operations:
  - `rtcattach`, `rtcwalk`, `rtcstat`, `rtcopen`, `rtcclose`
  - `rtcread`, `rtcwrite`, `rtcbwrite`
- NVRAM:
  - `nvput`
  - `nvget`
  - `nvcksum`
- Time:
  - `rtctime`
  - `setrtc`
  - `rtc2sec`
  - `sec2rtc`
- `watchreset`

## Data Structures

- RTC register constants and `Rtc` structure with second/minute/hour/day/month/year fields.
- `rtcdir[]` entries for `rtc` and `nvram`.

## Important Behavior

- Reads/writes RTC fields through CMOS-style address/data ports.
- Converts BCD encoded RTC fields to seconds since epoch and back.
- `rtcread` returns time as decimal seconds for `rtc` and raw bytes for `nvram`.
- `rtcwrite` accepts decimal time and updates RTC registers.
- `nvcksum` maintains checksum bytes over NVRAM contents.
- `watchreset` is a stub.

## Dependencies And Assumptions

- Uses port I/O helpers `inb`/`outb`.
- Assumes RTC/NVRAM layout compatible with the constants in this file.

## Notable Risks

- RTC century/year handling is manual and platform-specific.
- NVRAM checksum range assumptions must match firmware expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/ether2114x.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/ether2114x.c

## Role

DEC/Intel 2114x Tulip-family Ethernet driver for the MTX port. It handles PCI discovery, descriptor rings, transmit/receive, interrupts, EEPROM/SROM parsing, MII management, media selection, and registration with the generic Ethernet layer.

This is network device driver code, not filesystem code.

## Main Interfaces

- `ether2114xlink()`: registers the driver.
- Hardware operations:
  - `reset`
  - `attach`
  - `transmit`
  - `interrupt`
  - `ifstat`
  - `promiscuous`
- Controller setup:
  - `dec2114xpci`
  - `ctlrinit`
  - `softreset`
  - `srom`
  - `media`
  - `mediaxx`

## Data Structures

- `Des`: RX/TX DMA descriptor.
- `Ctlr`: controller state with PCI info, rings, SROM data, media state, and statistics.
- Enums define CSR bits, descriptor status/control bits, PHY registers, media variants, and SROM block types.

## Important Behavior

- Uses descriptor rings for RX and TX DMA.
- Interrupt handler processes receive packets, transmit completion, abnormal conditions, link changes, and fatal bus errors.
- MII bit-banging is implemented via CSR9 helpers.
- SROM parser interprets type 0/2/5 blocks and PHY/symbol media blocks.
- Media selection handles fixed, MII, SYM, and SIA-style 2114x variants.
- PCI discovery matches supported vendor/device IDs and configures IO port, IRQ, and bus mastering.
- `reset` allocates rings, reads MAC address, installs callbacks, and initializes controller state.

## Dependencies And Assumptions

- Depends on `devether.c`/`etherif.h`.
- Uses PCI config helpers and I/O port accessors.
- Assumes cache coherency or explicit descriptor visibility appropriate for this platform.

## Notable Risks

- Very hardware-specific media/SROM parsing with many fallback paths.
- DMA descriptor ownership bits must be maintained exactly.
- Error handling resets or reinitializes hardware in interrupt context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/ether2114x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/etherif.h

## Role

MTX Ethernet driver interface header. It defines the shared `Ether` structure and registration/helper prototypes used between generic Ethernet code and hardware drivers.

This is network interface glue, not filesystem code.

## Main Contents

- Queue/descriptor constants:
  - `Nrdre`
  - `Ntdre`
  - `Nrb`
- `Ether` structure:
  - hardware identity and bus fields
  - MAC address
  - interface name
  - receive/transmit callback hooks
  - multicast/promiscuous hooks
  - controller-private pointer
  - `Netif` embedded state
- Prototypes:
  - `etheriq`
  - `addethercard`
  - `ethercrc`
- Ring helpers:
  - `NEXT`
  - `PREV`

## Important Behavior

- Provides the contract consumed by `devether.c` and `ether2114x.c`.

## Dependencies And Assumptions

- Assumes `Netif`, `Block`, and Plan 9 network structures are visible to including files.

## Notable Risks

- Fixed RX/TX ring sizes are global defaults for drivers using this interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/fns.h

## Role

Machine-dependent function declaration header for the MTX PowerPC port. It declares assembly helpers, interrupt/timer/MMU routines, PCI and I/O port access, Ethernet/keyboard setup, and process transition hooks.

This is platform infrastructure used by drivers and kernel subsystems.

## Main Interfaces

- Includes `../port/portfns.h`.
- PowerPC helpers:
  - `getmsr`, `putmsr`, `getpvr`, `getdec`, `putdec`
  - `getdar`, `getdsisr`, `gethid0`, `puthid0`, `sync`, `eieio`
- I/O port helpers:
  - `inb`, `insb`, `ins`, `inss`, `inl`, `insl`
  - `outb`, `outsb`, `outs`, `outss`, `outl`, `outsl`
- Interrupt and timer:
  - `i8259init`, `i8259enable`, `i8259disable`, `intrenable`
  - `clockinit`, `clockintr`, `timeradd`, `timerdel`
- MMU/cache:
  - `mmuinit`, `mmusweep`, `tlbflush`, `tlbflushall`, `icflush`, `dcflush`
- PCI:
  - `pciscan`, `pcimatch`, `pcicfgr*`, `pcicfgw*`
- Process/control:
  - `touser`, `trapvec`, `forkret`, `procsetup`, `procsave`

## Important Macros

- `coherence()` maps to `eieio()`.
- `cycles(x)` is a no-op.
- `idlehands()` and `kexit(a)` are no-ops.
- `userureg(ur)` tests `MSR_PR`.
- `KADDR`/`PADDR` map through `KZERO`.

## Dependencies And Assumptions

- Assumes PowerPC assembly symbols from `mtx/l.s` and `inb.s`.
- Assumes MTX memory layout macros from `mem.h`.

## Notable Risks

- Several port hooks are stubbed/no-op for this architecture.
- Simple address conversion macros assume direct kernel mapping.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/i8259.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/i8259.c

## Role

Intel 8259A programmable interrupt controller support for the MTX port. It initializes master/slave PICs, enables/disables IRQs, acknowledges interrupts, and maps IRQs to vectors.

This is interrupt-controller infrastructure, not filesystem code.

## Main Interfaces

- `i8259init`
- `i8259isr`
- `i8259enable`
- `i8259intack`
- `i8259vecno`
- `i8259disable`

## Important Behavior

- Programs master and slave PIC initialization command words.
- Tracks interrupt masks in `int0mask` and `int1mask`.
- Handles cascaded slave interrupts through IRQ2.
- `i8259enable` attaches ISR/EOI callbacks into `Vctl`.
- `i8259intack` reads interrupt acknowledge port, handles spurious IRQ7/IRQ15, sends EOIs, and returns vector numbers.
- `i8259vecno` maps IRQ to `VectorPIC + irq`.

## Dependencies And Assumptions

- Uses I/O port helpers from `inb.s`.
- Assumes standard PC-compatible 8259 ports and vector base 32.

## Notable Risks

- Spurious interrupt handling is hardware-specific.
- Incorrect mask state can permanently lose or storm interrupts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/i8259.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/inb.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/inb.s

## Role

PowerPC assembly I/O port access routines for MTX. It implements byte/word/long input/output and repeated string I/O operations.

This is low-level bus I/O support, not filesystem code.

## Main Interfaces

- Input:
  - `inb`
  - `insb`
  - `ins`
  - `inss`
  - `inl`
  - `insl`
- Output:
  - `outb`
  - `outsb`
  - `outs`
  - `outss`
  - `outl`
  - `outsl`

## Important Behavior

- Uses PowerPC load/store byte/halfword/word instructions against I/O-mapped addresses.
- Repeated string operations loop with count registers and branch-on-count helpers.
- Calls `SYNC`/`EIEIO` around I/O operations for ordering.

## Dependencies And Assumptions

- Includes `mem.h`.
- Assumes port numbers are mapped into an addressable I/O region appropriate for `lbz`/`stb` style access.

## Notable Risks

- Endianness and ordering semantics are hardware-specific.
- Count and pointer arguments must match Plan 9 PowerPC calling conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/inb.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/io.h

## Role

MTX platform I/O definition header. It defines IRQ/vector numbers, interrupt control structures, bus encoding, EISA/PCI constants, PCI device structures, and PCI window address translation.

This is platform hardware description, not filesystem code.

## Main Contents

- IRQ and vector constants:
  - clock, keyboard, UART, PCMCIA, floppy, LPT, AUX, ATA IRQs
  - `VectorPIC`
- `Vctl`: interrupt handler descriptor with ISR/EOI hooks.
- Bus encoding macros:
  - `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSDF`, `BUSBDF`
- EISA constants.
- PCI config offsets and predefined header fields.
- `Pcisiz` and `Pcidev`.
- PCI translation:
  - `PCIWINDOW`
  - `PCIWADDR`

## Important Behavior

- Provides shared definitions for interrupt controller, PCI, Ethernet, and architecture code.
- Sets PCI window base to `0x80000000`.

## Dependencies And Assumptions

- Assumes `Pcidev` and interrupt vectors align with the MTX board's PC-compatible interrupt layout.
- Assumes PCI memory translation through `PADDR(va)+PCIWINDOW`.

## Notable Risks

- Header constants must match firmware/bridge configuration.
- `Pcidev` is a simplified PCI model compared with fuller ports.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/kbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/kbd.c

## Role

i8042 keyboard and auxiliary PS/2 controller driver for the MTX port. It initializes the controller, handles keyboard scan-code input, supports aux mouse command/enable paths, and registers keyboard interrupt handling.

This is input device support, not filesystem code.

## Main Interfaces

- `i8042reset`
- `i8042auxcmd`
- `i8042auxenable`
- `kbdinit`
- Internal helpers:
  - `outready`
  - `inready`
  - `i8042intr`

## Important Behavior

- Polls controller status for input/output readiness.
- Resets and configures the controller command byte.
- Handles key up/down prefixes and scan-code translation through keyboard tables.
- Calls Plan 9 keyboard queue helpers for decoded runes.
- Supports aux device command writes and installs an aux byte callback.
- `kbdinit` initializes keyboard state and enables keyboard/AUX interrupts.

## Dependencies And Assumptions

- Uses standard PC i8042 I/O ports.
- Depends on shared keyboard translation state/functions from the port layer.
- Uses `intrenable` with keyboard and aux IRQs.

## Notable Risks

- Polling timeouts are fixed.
- Scan-code state handling is global and sensitive to prefix/error bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/kbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/l.s

## Role

Core PowerPC assembly for the MTX port. It provides early MMU/BAT setup, interrupt priority primitives, context switch labels, cache/TLB operations, atomic primitives, special-register access, trap vector entry, user-mode transition, and FPU save/restore.

This is low-level kernel architecture support, not filesystem code.

## Main Interfaces

- Globals:
  - `mach0`
  - `memsize`
- MMU/bootstrap:
  - `mmuinit0`
  - `tlbflushall`
  - `tlbflush`
- FPU:
  - `kfpinit`
  - `fpsave`
  - `fprestore`
- Interrupt priority:
  - `splhi`
  - `splx`
  - `splxpc`
  - `spllo`
  - `spldone`
  - `islo`
- Context/process:
  - `setlabel`
  - `gotolabel`
  - `touser`
  - `forkret`
- Cache/atomic:
  - `icflush`
  - `dcflush`
  - `tas`
  - `_xinc`
  - `_xdec`
  - `cmpswap`
- Register access:
  - `getpvr`, `getdec`, `putdec`, `getdar`, `getdsisr`
  - `getmsr`, `putmsr`, `putsdr1`, `putsr`
  - `gethid0`, `gethid1`, `puthid0`, `puthid1`
  - `eieio`, `sync`
- Trap entry:
  - `trapvec`
  - `saveureg`
  - internal `ktrap` and `restoreureg`

## Important Behavior

- Initializes block address translation and segment registers for kernel mappings.
- Implements spin/atomic primitives with PowerPC reservation instructions.
- Saves complete trap frames into `Ureg` layout before calling C `trap`.
- Restores user state and returns with `RFI`.
- FPU save/restore covers 32 floating registers and FPSCR.
- Provides cache flush loops over address ranges.

## Dependencies And Assumptions

- Includes `mem.h`.
- Assembly uses fixed offsets in `Mach`, `Proc`, and `Ureg`; these must match C headers.
- Assumes PowerPC exception and MSR semantics.

## Notable Risks

- Struct offset drift breaks traps, scheduling, and user transitions.
- BAT/MMU setup is board-specific and fragile.
- FPU save/restore layout must match `FPsave` exactly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/l.s -->
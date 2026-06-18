# Group Research: group_1473_plan9_sources_os_plan9_plan9_sys_src_9_omap_kbd_c_sources_os_plan9__b0c4aa85bac4

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/kbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/kbd.c

OMAP keyboard scan-code translation for systems without a native keyboard controller, adapted from the PC PS/2 keyboard path.

Key responsibilities:
- Defines scan-code translation tables for normal, shifted, escaped, AltGr, control, control-escaped, and shifted-escaped states.
- Maintains independent internal and external `Kbscan` state machines.
- Converts scan codes to Plan 9 keyboard queue runes via `kbdputc(kbdq, ...)`.
- Tracks modifier state: shift, control, Alt/Latin compose, AltGr, caps lock, num lock, and mouse-button pseudo-keys.
- Supports Latin-1 compose collection through `latin1()`.
- Provides `kbdputmap()` and `kbdgetmap()` for runtime keyboard map mutation/query.
- Enables minimal keyboard state in `kbdenable()`.

Important behavior:
- `Ctl-Alt-Del` exits through `exit(0)`.
- `Latin` starts compose collection unless control is held, avoiding common VM focus-release behavior from `Ctl-Alt`.
- Shift updates the global `mouseshifted`, affecting mouse button mapping in `mouse.c`.
- F11 turns keyboard debug prints on; F12 turns them off.
- Mouse pseudo-key events can call `kbdmouse`.

Dependencies:
- Uses Plan 9 queue/global keyboard state from the port layer.
- Depends on `latin1`, `kbdputc`, `kbdq`, `error`, and Plan 9 error strings.

Notable risks:
- This is a scan-code table implementation, so behavior depends heavily on correct table entries.
- Some map arrays include mostly empty entries and special private-use rune encodings.
- The bounds check uses `sizeof kbtab`, which is byte size rather than `Nscan`; it is harmless here because entries are `Rune` and `c` is already masked to 7 bits, but it is semantically loose.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/kbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/l.s

ARMv7/OMAP3530 assembly assist for kernel entry, MMU/cache setup, reset, cache maintenance, interrupt priority primitives, atomic operations, labels, and CP15 accessors.

Key responsibilities:
- `_start` enters from U-Boot or another kernel with MMU disabled, sets SVC mode, prints early boot characters, applies Cortex/OMAP errata workarounds, clears `Mach`, builds first-level page tables, maps DRAM and MMIO, enables caches and MMU, then jumps into virtual-addressed C `main`.
- `_reset` disables caches, re-establishes temporary mappings, disables the MMU, and attempts a low-level reset path.
- Provides cache line operations: `cachedwbse`, `cachedwbinvse`, `cachedinvse`, plus full cache helpers via `cache.v7.s`.
- Provides MMU helpers: `mmuenable`, `mmudisable`, `mmuinvalidate`, `mmuinvalidateaddr`, `ttbget`, `ttbput`, `dacget`, `dacput`, `pidput`, `pidget`.
- Provides CP15/status helpers: CPU ID, cache type, control register, fault status/address, SCR.
- Implements `splhi`, `spllo`, `splx`, `islo`, `tas`, `clz`, `setlabel`, `gotolabel`, `getcallerpc`, `idlehands`, and `coherence`.

Important behavior:
- Sets up a double map for early physical and kernel virtual DRAM, then removes the physical alias after entering the virtual map.
- Maps up to 512 MiB of DRAM at `KZERO`, matching Beagle/IGEP comments.
- Uses high exception vectors later populated by `trapinit`.
- Uses `SWPW` for test-and-set even though it is deprecated on ARMv7.
- Uses barriers aggressively around CP15, MMU, cache, and interrupt state changes.

Dependencies:
- Depends on constants/macros from `arm.s`, `mem.h`, and MMU page-table macros such as `FILLPTE`, `ZEROPTE`, `PTEDRAM`, and `PTEIO`.
- Calls C/assembly routines including `cachedinv`, `cacheuwbinv`, `l2cacheuwbinv`, `main`, and `_div`.

Notable risks:
- Early startup has no normal stack until it creates one, so only very constrained calls are safe before that point.
- Low-level mapping mistakes can hang CP15/TLB operations.
- Reset path is incomplete for actual flash vector jump and falls into idle loop.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/lexception.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/lexception.s

ARM exception vector stubs and register-save/restore paths for OMAP Plan 9.

Key responsibilities:
- Defines `vectors` trampoline entries and `vtable` target table copied to high vectors by `trapinit()`.
- Handles SWI/syscall directly in `_vsvc`, building a `Ureg`, loading kernel `SB`, `m`, and `up`, calling `syscall()`, then returning via `RFE`.
- Handles undefined instruction, prefetch abort, data abort, IRQ, and FIQ through vector-specific stubs.
- `_vswitch` changes from exception modes to SVC mode, distinguishes kernel versus user exceptions, saves a full `Ureg`, calls `trap()`, and restores state.
- Provides `setr13()` to install per-mode stack pointers.

Important behavior:
- Adjusts banked registers carefully while switching processor modes.
- Uses separate user and kernel exception save paths because user register access uses `.S` forms.
- Avoids ambiguous writeback forms noted in `notes/movm.w`.
- FIQ currently returns immediately or is routed to IRQ in `vtable`.

Dependencies:
- Depends on `arm.s`, `trap()`, `syscall()`, `setR12`, `L1`, `MACHSIZE`, and ARM PSR mode constants.
- Matches `Ureg` layout expected by C trap/syscall code.

Notable risks:
- Correct `Ureg` stack layout is a hard ABI with `trap.c`, `syscall.c`, and `lproc.s`.
- Any mismatch in saved register order would break syscall/trap return.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/lproc.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/lproc.s

Small ARM process-transition assembly helpers.

Key responsibilities:
- `touser(SB)` performs the first transition from kernel to user mode, installing the user stack pointer in user `R13`, setting `SPSR` to user mode, pushing `UTZERO+0x20` as the initial PC, and returning through `RFE`.
- `forkret(SB)` restores a saved `Ureg` frame for a newly forked process and returns to user mode through `RFE`.

Important behavior:
- `touser` assumes the user entry point is always `UTZERO+0x20`.
- `forkret` mirrors the trap/syscall return frame layout produced in `lexception.s` and `syscall.c`.

Dependencies:
- Uses `mem.h`, `arm.h`, `UTZERO`, `PsrMusr`, and the expected ARM `Ureg` save layout.

Notable risks:
- These routines are tightly coupled to the assembly trap frame format; offsets are implicit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/main.c

OMAP kernel mainline and early system initialization for Plan 9.

Key responsibilities:
- Parses and stores boot arguments and `plan9.ini` configuration from `CONFADDR`.
- Initializes `Mach`, MMU, traps, memory sizing, pools, clocks, screen, devices, paging, swap, and the first user process.
- Provides configuration lookup/update helpers: `getconf`, `addconf`, `isaconfig`, `getenv`, and `writeconf`.
- Implements shutdown, `exit`, and in-memory kernel reboot through `rebootcode`.
- Creates the initial process, stack, argument vector, and `initcode` text mapping.
- Computes `Conf` memory/process/page/swap/image sizing.
- Probes physical memory size by temporarily identity-mapping candidate addresses and using `probeaddr()`.

Important behavior:
- Starts with conservative 256 MiB default memory, accepts `*maxmem`, and probes 256/128 MiB fallbacks.
- Clears BSS and verifies possible data-segment realignment after bootloader load quirks.
- Converts `plan9.ini` variables into both volatile and configuration environment entries in `init0`.
- Uses `touser(sp)` to enter the initial user process.
- Reboot copies trampoline code to `REBOOTADDR`, shuts down devices/clocks/interrupts, then calls it with physical addresses.

Dependencies:
- Depends on port kernel initialization routines, OMAP MMU/trap routines, `initcode`, `rebootcode`, pool allocator, device reset/init hooks, and ARM process entry assembly.

Notable risks:
- Many initialization calls have strict ordering comments, especially trap setup before memory probing and malloc/pool initialization before print/device paths.
- `getenv` searches only the local `oenv` buffer, which is initially empty except for any prior boot-argument population.
- `bootargs` notes its stack layout is not strictly the conventional argc/argv ABI but works with Plan 9 `startboot`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/mem.h

OMAP memory layout and machine constant header shared by C and assembly.

Key contents:
- Defines binary size units, bit-field helpers, page/stack/cache sizes, and max CPU count.
- Defines kernel/user virtual address layout:
  - `KZERO`/`KSEG0` at `0xC0000000`.
  - `L1` page table at `KZERO+16KiB`.
  - `CONFADDR` at `KZERO+0x300000`.
  - `KTZERO` at `KZERO+0x310000`.
  - user top at `0x20000000`.
- Defines reboot trampoline address `REBOOTADDR`.
- Defines Plan 9 PTE flags: valid, write, uncached, kernel.
- Enumerates OMAP35 physical peripheral addresses: system control, DSS/DISPC, DMA, USB, UARTs, MMC, INTC, PRM, watchdogs, timers, GPIO, L3/L4, GPMC, and DRAM.
- Defines `VIRTIO` as the same address as `PHYSIO`, relying on direct MMIO mapping.

Role:
- Provides the hardware contract for startup assembly, MMU setup, traps, screen, UART, USB, and other device drivers.
- Documents the low-memory boot layout used by `l.s`, `mmu.c`, `main.c`, and `rebootcode.s`.

Notable constraints:
- `MAXMACH` is 1.
- `KSEGM` mask assumes 512 MiB DRAM.
- Comments warn `KTZERO` must match the kernel mkfile load address.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/mmu.c

ARMv7 OMAP MMU management for kernel mappings, user page tables, TLB switching, and simple kernel mappings.

Key responsibilities:
- Dumps level-1 page-table ranges through `mmudump`.
- Adds section mappings with `mmumap` and identity mappings with `mmuidmap`.
- `mmuinit` completes static kernel mappings for I/O and high vectors, including a 4 KiB vector L2 table.
- Maintains per-process user L2 page-table pages in `Proc.mmul2` and `Proc.mmul2cache`.
- Switches process address spaces in `mmuswitch`, flushes stale mappings, and writes back page-table entries.
- Releases process MMU pages in `mmurelease`.
- Installs user mappings in `putmmu`.
- Provides section-level `mmuuncache`, `mmukmap`, `mmukunmap`, `cankaddr`, `vmap`, and `vunmap`.

Important behavior:
- User virtual space covered by `L1lo` through `L1hi` is cleared on switches.
- Allocates full pages for L2 tables even though each coarse ARM L2 table needs only 1 KiB.
- `putmmu` maps pages cached/buffered unless `PTEUNCACHED` is set, uses user RW or RO access bits, invalidates the specific TLB entry, and handles text-cache invalidation.
- `mmuuncache` only accepts already mapped 1 MiB sections.
- `mmukmap`/`mmukunmap` are section-size stubs.

Dependencies:
- Uses `ttbget`, cache/TLB assembly helpers, page allocator, process fields from `dat.h`, and ARM PTE constants from `arm.h`.

Notable risks:
- `mmul1empty` contains a disabled optimized path with a comment noting a bug; current code clears the entire user L1 range.
- `vmap` is a transitional implementation and comments call out multiple limitations.
- `mmukmap` asserts 1 MiB alignment and size, so sub-MiB users will fail.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/mouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/mouse.c

Mouse packet decoding and control handling, mainly for PS/2-format mouse streams.

Key responsibilities:
- Decodes 3-byte PS/2 mouse packets and 4-byte Intellimouse/AccuPoint packets.
- Maps button bits, including shift-right to middle-button behavior through `mouseshifted`.
- Handles packet resynchronization after long idle gaps.
- Sends movement/button events to `mousetrack`.
- Provides `mousectl()` command handling for acceleration, resolution, linear mode, Intellimouse mode, reset, and hardware acceleration flags.

Important behavior:
- `ps2mouseputc` signs-extends X/Y deltas from packet status bits and negates Y.
- Intellimouse packets can switch back to 3-byte packet mode if the fourth byte looks like a new first byte.
- Serial mouse command reports unsupported.

Dependencies:
- Uses devmouse functions from `screen.h`, Plan 9 command parsing, `MACHP(0)->ticks`, and the global keyboard shift state.

Notable risks:
- The actual PS/2 enable path is commented out, so this file provides decoding/control logic but not a complete OMAP hardware path.
- Several control settings record state but do not program hardware because the low-level controller hooks are absent/commented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/rebootcode.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/rebootcode.s

OMAP reboot trampoline copied to low memory and executed during kernel replacement.

Key responsibilities:
- `main(PADDR(entry), PADDR(code), size)` disables interrupts, slows speculative/cached behavior, turns caches off, switches from `KZERO` to physical DRAM addressing, disables MMU/caches, copies the new kernel image to its destination, flushes caches, and branches to the physical entry point.
- `cachesoff` writes back caches, disables I/D caches, re-establishes the physical/KZERO double map, invalidates TLBs, and adjusts SB/SP/LR into physical addressing.
- Provides local `_r15warp` and stubs for `panic` and `pczeroseg`.

Important behavior:
- Must fit in the low-memory space before page tables.
- Uses early `PUTC` progress characters to the serial console.
- Avoids `R11` because the loader uses it as a temporary.
- Jumps to the physical kernel entry; the new kernel later establishes virtual addressing in `l.s`.

Dependencies:
- Depends on `arm.s`, `cache.v7.s`, `memmove`, cache helpers, and the same page-table layout as `l.s`.

Notable risks:
- Runs while dismantling the current virtual-memory environment, so address-segment adjustment is central and fragile.
- Assumes the copied image and entry/destination arguments are sane physical addresses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/screen.c

OMAP35 Display Subsystem framebuffer driver, kernel text console, blanking, and software cursor support.

Key responsibilities:
- Defines DSS/DISPC register layouts and constants for display configuration.
- Provides fixed display mode settings, with default `Res1280x1024`.
- Allocates an aligned 16-bit RGB framebuffer and exposes it as a `Memimage`.
- Programs DSS/DISPC timing, divisor, framebuffer base, FIFO, and graphics attributes.
- Implements screen power/blanking through LCD enable/disable.
- Implements `flushmemscreen()` by writing back framebuffer cache lines.
- Exports framebuffer details to devdraw via `attachscreen()`.
- Provides a software cursor implementation: allocation, load, hide/draw, move, clock update, and `setcursor`.
- Provides an on-screen text console with border/title bar, tab/backspace/newline handling, and scrolling.

Important behavior:
- `screeninit()` shows a blue test screen for three seconds on first initialization, then sets up the console window and cursor.
- Cursor drawing saves/restores the underlying screen region in `swback`.
- Console output avoids deadlock by using `canlock` when called from high interrupt priority.
- `blankscreen(0)` reinitializes display registers before enabling the LCD.
- `attachscreen` reports `softscreen` based on `landscape == 0`.

Dependencies:
- Depends on Plan 9 draw/memdraw, clock callbacks, OMAP clock/GPIO functions, cache writeback, and constants from `screen.h`/`mem.h`.

Notable risks:
- Resolution is effectively fixed to compile-time `Wid`/`Ht`, despite a settings table.
- Several color values are magic 16-bit bytes.
- `flushmemscreen` computes a byte span but passes `end - start`, not including the final pixel fully; this is usually cache-line rounded but imprecise.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/screen.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/screen.h

Shared OMAP screen, cursor, devdraw, and mouse interface header.

Key contents:
- Forward declarations for `Cursorinfo`, `OScreen`, `Omap3fb`, and `Settings`.
- External declarations for mouse tracking, mouse position, acceleration, screen attach/flush/blank/cursor functions, devdraw hooks, draw lock, and screen image reset helpers.
- Defines `ishwimage(i)` as false for software-only drawing.
- Defines framebuffer maxima and format:
  - `Wid = 1280`
  - `Ht = 1024`
  - `Depth = 16`
  - palette constants and resolution indices.
- Defines `Settings` timing structure, `OScreen` state, and `Omap3fb` framebuffer pixel array.

Role:
- Connects `screen.c`, devdraw, devmouse, and possible DSS control code.
- Establishes the fixed framebuffer dimensions used by `screen.c`.

Notable constraints:
- `Omap3fb` is a statically shaped 1280x1024 16-bit framebuffer regardless of selected mode.
- `screenaperture`, `screensize`, `physgscreenr`, and `swcursorunhide` are declared but not implemented in `screen.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/softfpu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/softfpu.c

Soft-FPU placeholder and ARM floating-point instruction emulation hook.

Key responsibilities:
- Provides machine-dependent FPU lifecycle stubs expected by port code: `/proc` FPU I/O, notify/noted, rfork save/copy, process save/restore, exec setup, and init.
- Implements `fpuemu(Ureg*)`, which lowers priority, calls `fpiarm(ureg)` to emulate an ARM floating-point instruction, restores priority, and posts a debug note on error.

Important behavior:
- All FPU state-management routines are no-ops except `fpuemu`.
- `fpudevprocio` returns 0 and does not expose register state.

Dependencies:
- Depends on the soft-float emulator function `fpiarm`.
- Called by trap/syscall paths through machine-dependent hooks.

Notable risks:
- No real FPU context is saved/restored; this platform relies on software emulation or absence of hardware FPU use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/softfpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/syscall.c

ARM syscall, notify/noted, exec register setup, and fork-child register setup for OMAP Plan 9.

Key responsibilities:
- Defines the ARM user notification frame `NFrame`.
- `notify()` arranges delivery of pending Plan 9 notes by copying the current `Ureg` and note text onto the user stack and redirecting PC to `up->notify`.
- `noted()` validates and restores user state after a note handler calls `noted`, supporting `NCONT`, `NRSTR`, `NSAVE`, and default/debug termination paths.
- `syscall()` validates user origin, fetches syscall number/arguments, dispatches through `systab`, handles errors, traces syscall stops, handles `NOTED`, delivers notes, schedules delayed reschedules, and exits through `kexit`.
- `execregs()` sets a new process entry PC and user stack after exec.
- `forkchild()` builds the child `Ureg` frame so `forkret` returns to user mode with `r0 == 0`.

Important behavior:
- Syscall number is in `r0`; arguments are copied from the user stack after a return-PC word.
- `RFORK` triggers FPU state preparation before the syscall.
- `NOTED` calls `noted()` with the stack argument.
- User-altered PSR is masked so system flags cannot be changed across noted return.

Dependencies:
- Depends on `systab`, `sysctab`, Plan 9 process/note/procctl mechanisms, `okaddr`/`validaddr`, and ARM `Ureg` layout.

Notable risks:
- Notify frame ABI is architecture-specific and must match user runtime expectations.
- Syscall argument validation relies on stack range checks and `validaddr` for edge cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/trap.c

OMAP trap, interrupt-controller, exception, fault, register dump, and probe-address implementation.

Key responsibilities:
- Defines the OMAP35 MPU interrupt controller register map and interrupt handler chain `Vctl`.
- `trapinit()` installs high vectors, initializes per-mode stacks, masks all interrupts, and initializes interrupt priorities.
- Provides interrupt mask/unmask/save/restore helpers and `intrsoff`.
- `irqenable()`/`irqdisable()` manage chained handlers per IRQ and controller masking.
- `irq()` dispatches active IRQs, handles unexpected interrupts, tracks interrupt timing, and acknowledges the controller.
- `trap()` handles IRQ, prefetch abort, data abort, and undefined instruction exceptions.
- `faultarm()` dispatches VM faults to generic `fault()` and posts notes/panics on failure.
- Supports breakpoint handling, external abort decoding, alignment/access/permission fault handling, and soft-float emulation through `fpiarm`.
- Provides register/stack dumps and CP15 status dumps.
- `probeaddr()` safely attempts a kernel load, converting a fault into `-1` through the trap probing path.

Important behavior:
- Adjusts exception PC by `-4`, or `-8` for data aborts, before decoding.
- Clears `ldrexvalid` around interrupts/exceptions.
- Clock interrupt detection is IRQ number range 37-47.
- Unknown/unhandled interrupts are masked.
- Kernel faults generally panic; user faults become Plan 9 debug notes.
- Undefined user instructions first check the Plan 9 breakpoint encoding, then try floating-point emulation.

Dependencies:
- Depends on `lexception.s` vectors, interrupt controller physical address from `mem.h`, CP15 helpers from `l.s`, VM fault path, process note path, and `Ureg` layout.

Notable risks:
- Fault-status decoding is ARM-specific and panics on many external/parity cases.
- Probe handling depends on global `probing/trapped` state protected by a lock.
- IRQ handler invariants require handlers not to lower interrupt priority.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/uarti8250.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/uarti8250.c

OMAP35 8250-like UART driver for the console UART, integrated with Plan 9 `Uart`/`PhysUart`.

Key responsibilities:
- Defines 8250/OMAP UART registers and bit constants.
- Configures a single console UART at `PHYSCONS`, IRQ 74, exposed as `"COM3"`.
- Implements status, FIFO, DTR/RTS, modem control, parity, stop bits, data bits, baud, break, kick/transmit, interrupt handling, enable/disable, getc/putc, and console setup hooks.
- Provides early polled serial output before normal queues and interrupts are available.
- Connects `kbdq`, `serialoq`, and `consuart` in `i8250console`.
- Provides `_uartputs` and `_uartprint` early/debug output helpers.

Important behavior:
- Baud-rate programming is disabled under `#ifdef notdef`; requested baud is stored but hardware divisor is not changed.
- `i8250enable` refuses to do work when `up == nil`, preventing too-early interrupt setup.
- Early output path writes directly to `PHYSCONS` while holding high interrupt priority.
- Transmit interrupt is disabled when output queues drain and transmitter is empty.
- Receive interrupt consumes bytes unless break/framing/parity errors occurred.

Dependencies:
- Depends on Plan 9 generic UART layer, IRQ enable/disable, queue functions, and OMAP MMIO mapping.

Notable risks:
- Only one UART is declared, despite OMAP having multiple UARTs.
- FIFO enable changes flush hardware FIFOs, with comments noting possible receive data loss.
- Some PC 8250 workarounds/comments are retained even when not fully applicable to OMAP.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/uncached.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/uncached.h

Header-level allocator macro override for forcing USB/EHCI data structures into uncached memory.

Key contents:
- Documents spurious EHCI transaction errors when cached write-back memory is used for USB data.
- Redefines memory/block allocation/free names:
  - `free` to `ucfree`
  - `malloc`/`smalloc` to `myucalloc`
  - `mallocz` to `ucallocz`
  - `xspanalloc` to `ucallocalign`
  - block alloc/free functions to uncached equivalents.
- Implements `ucallocz()` and `myucalloc()` wrappers.

Role:
- Intended to be included before USB/EHCI code that assumes normal allocator names, redirecting allocations to uncached memory.

Notable risks:
- Macro substitution is broad and can surprise included code.
- `ucallocz` ignores its second argument and always zeroes.
- Allocation failure panics rather than returning nil.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/uncached.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/usbehci.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/usbehci.h

OMAP EHCI support header extending generic Plan 9 USB/EHCI definitions.

Key contents:
- Overrides EHCI debug print macros to use `ehcidebug` and endpoint debug flags.
- Forward-declares EHCI controller and queue structures.
- Defines `Poll` synchronization state.
- Defines `Ctlr`, the controller state used by generic EHCI code:
  - register pointers,
  - frame list,
  - async and periodic queue heads,
  - isochronous state,
  - interrupt/load counters,
  - poll rendezvous.
- Defines OMAP-specific `Eopio` operational register layout, including three ports and implementation-specific `insn[]` registers.
- Defines `Uhh` USB host subsystem register layout and `P1ulpi_bypass`.
- Declares EHCI globals and generic helper functions.

Role:
- Bridges the generic `portusbehci` driver and the OMAP-specific EHCI reset/register plumbing.

Notable details:
- `Eopio` includes OMAP implementation-specific registers beyond standard EHCI operational registers.
- Controller struct is shared with generic EHCI routines, so field layout matters across files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/usbehciomap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/usbehciomap.c

OMAP3-specific EHCI host-controller reset, setup, shutdown, and linkage code.

Key responsibilities:
- `ehcireset()` stops EHCI, clears 64-bit segment address, resets controller unless it is the debug controller, configures interrupt threshold, and records frame-list size.
- `shutdown()` resets/stops the controller and clears the frame-list base.
- Provides `setdebug()` to update global EHCI debug level.
- Implements OMAP-specific ULPI register writes through `wrulpi()`.
- `reset()` probes for EHCI presence, allocates `Ctlr`, maps capability/operational registers, initializes controller memory, configures OMAP implementation registers and ULPI/UTMI mode, links to generic HCI, and enables extra USB-related interrupts.
- `usbehcilink()` registers this HCI type as `"ehci"`.

Important behavior:
- Skips initialization when `*nousbehci` is set or `probeaddr(PHYSEHCI)` fails.
- Only allows one initialization through static `beenhere`.
- OMAP setup sets `insn[4]` bit 5 as required by the manual.
- For ULPI port 1, disables the integrated STP pull-up and forces PHY high-speed mode.
- Registers extra interrupts for USB TLL and OTG/OTG DMA.

Dependencies:
- Depends on generic USB HCI/EHCI port code, OMAP memory addresses, `probeaddr`, Plan 9 interrupt registration, and `usbehci.h`.

Notable risks:
- ULPI polling loop uses a counterintuitive condition documented as contrary to sparse documentation.
- GPIO PHY reset is noted as TODO.
- `hp->irq` is set to 77 but additional interrupt enables use 78, 92, and 93.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/usbehciomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ahci.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ahci.h

AHCI/SATA register, bit, and in-memory structure definitions.

Key contents:
- ATA error and status bit masks, including fatal error grouping.
- PCI AHCI BAR index.
- AHCI generic host control register layout `Ahba`.
- Host capability and global control flags.
- Port interrupt/status/error masks and fatal interrupt grouping.
- SATA SError bits and aggregate masks.
- Port command/control state bits and device-detection/interface-power states.
- AHCI port register layout `Aport`.
- Host memory structures:
  - `Afis` receive-FIS area descriptor,
  - `Alist` command list entry,
  - `Aprdt` PRD entry,
  - `Actab` command table,
  - `Aportm` software port state,
  - `Aportc` combined register/software pointer.

Role:
- Shared low-level hardware contract for an AHCI driver implementation.
- Contains no functions; it defines the symbolic interface to AHCI hardware and command memory.

Notable details:
- Some comments preserve AHCI spec section hints and note typo-like names from hardware docs.
- Command-table definition includes a single PRD entry, implying driver code may allocate/use one PRD per command table instance here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ahci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apbootstrap.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/apbootstrap.s

x86 application-processor bootstrap code for SMP startup.

Key responsibilities:
- Real-mode entry at `apbootstrap` far-jumps into `_apbootstrap`.
- Defines writable bootstrap data slots for AP entry vector, page directory base, and APIC value.
- Loads a minimal GDT, enables protected mode, installs segment registers, and far-jumps to 32-bit code.
- `_ap32` double-maps `KZERO` at virtual 0, loads CR3, enables paging/write-protect, and jumps into kernel virtual space.
- `_appg` removes the temporary zero mapping, flushes CR3, sets stack to `MACHADDR+MACHSIZE-4`, clears flags, pushes APIC argument, and calls the AP startup vector.
- Provides minimal GDT entries and pointer.

Important behavior:
- Must reside in low conventional memory on a 4 KiB boundary and effectively within the first 64 KiB due to shortcut addressing.
- The paging enable code must run from identity-mapped pages, hence the temporary double map.

Dependencies:
- Depends on x86 memory constants and descriptor macros from `mem.h`.
- Called by APIC/MP startup code after writing bootstrap data slots.

Notable risks:
- Very address-layout-sensitive; comments explicitly call out placement restrictions.
- Assumes page directory contains a valid kernel mapping at `KZERO`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apbootstrap.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apic.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/apic.c

Local APIC and I/O APIC support for PC SMP and timer interrupts.

Key responsibilities:
- Defines local APIC register offsets and bit masks.
- Provides `lapicr`/`lapicw` register access helpers.
- Initializes local APIC mode, spurious vector, error vector, LVT entries, timer, and arbitration synchronization in `lapicinit`.
- Calibrates local APIC timer against `fastticks` in `lapictimerinit`.
- Brings a CPU’s LAPIC online with periodic timer and lowered task priority.
- Starts application processors with INIT and STARTUP IPIs through `lapicstartap`.
- Handles APIC error/spurious interrupts and EOI.
- Provides IOAPIC redirection table read/write and initialization.
- Programs one-shot/periodic timer deadlines through `lapictimerset`.
- Bridges APIC clock interrupt to `timerintr`.
- Enables/disables LAPIC interrupt acceptance and NMI LVT.

Important behavior:
- APIC timer period is clamped between calibrated min/max.
- Some old Pentium steppings get an MSR workaround and suppress error reports.
- LAPIC timer reloads are staggered by CPU number to desynchronize processors.

Dependencies:
- Depends on MP/APIC structures from `mp.h`, x86 MSR helpers, `fastticks`, interrupt vectors, and generic timer/MTRR functions.

Notable risks:
- `lapictimerinit` panics if calibrated APIC clock appears faster than CPU clock outside tolerance.
- LAPIC access panics if `lapicbase` is not initialized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/apm.c

Advanced Power Management BIOS interface exposed through the PC arch device.

Key responsibilities:
- Parses APM register values from `plan9.ini` ISA configuration `apm0`.
- Builds three GDT descriptors required by the APM BIOS: 32-bit code, 16-bit code, and data.
- Adds `#P/apm` arch file for reading/writing a `Ureg`.
- `apmwrite` copies a user-provided `Ureg`, raises priority, calls BIOS through `apmfarcall`, then stores returned register state.
- `apmread` returns the last `Ureg` contents.

Important behavior:
- Forces both APM code segment lengths to 64 KiB due to a documented NEC Versa SX BIOS issue.
- Uses `KADDR(base)` when programming descriptors, meaning BIOS physical base addresses are mapped into kernel virtual space first.
- Prints configured APM code base and offset.

Dependencies:
- Depends on `apmfarcall` from `apmjump.s`, GDT layout in `Mach`, ISA configuration parsing, and `addarchfile`.

Notable risks:
- Comments call this a BIOS hack; it is tightly coupled to protected-mode descriptor details.
- The arch file write requires exactly a `Ureg` size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apmjump.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/apmjump.s

x86 assembly helper for protected-mode APM BIOS far calls.

Key responsibilities:
- Defines global `apmjumpstruct` containing the far-call offset and segment.
- Provides small `fortytwo` and `getcs` helpers.
- `apmfarcall(seg, off, Ureg*)` builds the far pointer, loads selected registers from `Ureg`, saves segment/general registers, installs `APMDSEG` in DS, performs an absolute far call through the jump structure, restores registers/segments, stores flags and selected returned registers back into `Ureg`, and returns carry flag status.

Important behavior:
- Explicitly warns it is not reentrant/thread-safe because it uses global jump parameters.
- Avoids using `FP` after manual stack manipulation starts.

Dependencies:
- Depends on `APMDSEG` and Ureg field offsets from PC kernel headers.

Notable risks:
- Ureg offsets are hard-coded numeric displacements.
- BIOS calls run with delicate segment state; incorrect GDT setup in `apm.c` would break this path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/apmjump.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/archmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/archmp.c

PC multiprocessor architecture selection and TSC-based clock support.

Key responsibilities:
- Defines `archmp`, a `PCArch` implementation for Intel MP Specification systems.
- `identify()` respects `*nomp`, searches for `_MP_`, validates the MP floating pointer and `PCMP` table checksum/version, and selects MP mode or uniprocessor fallback.
- Uses LAPIC/IOAPIC interrupt functions for MP systems.
- Uses `i8253read` or `tscticks` as fast clock depending on CPU server/TSC availability.
- `mpresetothers()` sends INIT to all CPUs except self.
- `syncclock()` synchronizes TSC values across processors.
- `tscticks()` reads the TSC and reports CPU Hz.

Important behavior:
- Does not accept default MP configurations with physical address 0.
- Prints a uniprocessor assumption message when no MP table is found.

Dependencies:
- Depends on MP structures, `sigsearch`, LAPIC/MP interrupt initialization, i8253, TSC/MSR helpers, and global `arch`.

Notable risks:
- ACPI is acknowledged but not used for interrupt routing here.
- TSC sync assumes CPU0 ticks progress and that writing MSR 0x10 is valid.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/archmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/audio.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/audio.h

Small PC audio compatibility header.

Key contents:
- Defines buffer size/count, DMA channel, audio IRQ, and byte-swap flag.
- Maps generic audio hooks to PC kernel helpers:
  - `seteisadma(a, b)` to `dmainit(a, Bufsize)`
  - `UNCACHED(type, v)` to a direct cast
  - `setvec(v, f, a)` to `intrenable(..., "audio")`
- Defines `Int0vec` empty.

Role:
- Supplies platform-specific constants/macros expected by shared or legacy audio code.

Notable details:
- `Bufsize` is documented as 5.8 ms and must be a power of two.
- `Nbuf` gives roughly 0.74 seconds total buffering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/audio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/bios32.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/bios32.c

BIOS32 service directory discovery and calling-interface setup.

Key responsibilities:
- Defines BIOS32 service directory and service interface structures.
- Scans BIOS memory for `_32_` on 16-byte boundaries and validates checksum.
- Maps the BIOS32 entry point with `vmap` and constructs a far pointer using `KESEL`.
- `bios32open(id)` calls the BIOS32 service directory for a four-character service ID, maps the returned service base, and builds a callable far pointer for the service entry.
- `bios32ci()` serializes BIOS32 service calls with `bios32lock`.
- `BIOS32close()` unmaps service memory and frees the descriptor.

Important behavior:
- Uses little-endian field extraction for the directory physical address.
- Lazily locates BIOS32 on first open.
- Uses a static debug flag macro, disabled by default.

Dependencies:
- Depends on low BIOS memory mapping macros, `vmap`/`vunmap`, `bios32call`, and `KESEL`.

Notable risks:
- BIOS32 calls are globally serialized, but service-specific behavior still depends on firmware correctness.
- `vmap(L32GET(...), 4096+1)` maps one page plus one byte, likely to cover potential page crossing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/bios32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/cga.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/cga.c

PC CGA/VGA text-mode console output.

Key responsibilities:
- Defines text colors, screen geometry, attributes, and CGA base address.
- Reads/writes CRT controller cursor registers.
- Implements `cgascreenputc` for newline, tab, backspace, ordinary characters, scroll, and cursor update.
- Implements interrupt-safe `cgascreenputs` using `canlock` at high priority.
- Provides `cgapost(code)` to display a two-hex-digit POST code near the bottom of the screen.
- `screeninit()` initializes `cgapos` from hardware cursor registers and installs `screenputs`.

Important behavior:
- Screen memory is `KADDR(0xB8000)`.
- Scrolling moves the 24 lower lines up and clears the final line.
- Cursor position is tracked in byte offsets because each cell is character+attribute.

Dependencies:
- Depends on port I/O functions `inb`/`outb`, `KADDR`, and Plan 9 screenputs hook.

Notable risks:
- Assumes VGA-compatible text mode and 80x25 layout.
- Drops console output if called during interrupt and lock is already held.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/cga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/dat.h

Core PC platform type definitions, process/MMU machine state, CPU feature flags, and architecture interface declarations.

Key contents:
- Forward declarations for BIOS32, configuration, PCMCIA, PCI, process/page/Mach, Ureg, and related types.
- Defines `Lock`, `Label`, x87/SSE FPU save structures, `FPsave`, `Confmem`, `Conf`, `PMMU`, and `Notsave`.
- Includes shared `../port/portdat.h`.
- Defines x86 `Tss`, GDT segment descriptor, and full `Mach` structure.
- Defines `KMap` aliases/macros and declares `kmap`/`kunmap`.
- Defines global `active` CPU/shutdown state.
- Defines `PCArch`, the architecture operations table for reset, power, interrupts, clocks, and peer CPU reset.
- Defines CPUID feature masks and parsed ISA configuration structure.
- Declares `arch`, `machp`, `m`, and `up`.

Role:
- The central machine-private ABI between PC assembly, MMU, traps, arch device, interrupt setup, process code, and port kernel code.

Important fields:
- `PMMU` stores page directory and page table-page lists per process.
- `Mach` contains per-CPU page directory/GDT/TSS, current process, performance counters, APIC timer lock, CPU ID/cache/TSC/MTRR state, and aligned FPU-save pointer.
- `PCArch` abstracts generic PC versus MP interrupt/clock implementations.

Notable risks:
- Many layouts are known to assembly or port code; structural changes require cross-file coordination.
- `up` is a macro through `MACHADDR`, not a normal global.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devarch.c

PC architecture device `#P`, I/O port allocator/accessor, CPU identification, architecture selection, and runtime architecture controls.

Key responsibilities:
- Maintains an I/O port allocation map with `ioinit`, `ioreserve`, `ioalloc`, `iofree`, and `iounused`.
- Implements `#P` files:
  - `ioalloc`
  - `iob`
  - `iow`
  - `iol`
  - dynamically added arch files.
- Provides `addarchfile()` for other code to extend `#P`.
- Allows raw I/O byte/word/long reads/writes after checking allocation conflicts, with VGA ranges exempted.
- Provides generic PC reset through i8042 reset and port `0xcf9`.
- Implements default `PCArch archgeneric`.
- Identifies CPU vendor/family/model via CPUID, selects CPU type names/timing constants, detects TSC/PSE/MCE/PGE/FXSR/SSE/SSE2, sets CR4 bits, calibrates CPU Hz, and selects FPU save routines.
- Exposes `cputype` and `archctl` files.
- `archctl` can toggle PGE, choose memory barrier implementation, enable/disable i8253 timer programming, and set MTRR cache ranges.
- Selects a concrete `PCArch` from `knownarch`, with fallback/default fields filled from `archgeneric`.
- Provides `pcmspecial` indirection, `fastticks`, microsecond conversion, and `timerset`.

Important behavior:
- Reserves a dummy I/O byte at `0x0fff` to support an IBM X20 boot quirk.
- `ioexclude` plan9.ini ranges are pre-allocated.
- Raw I/O access is denied for allocated ranges except VGA registers.
- Coherence defaults improve with CPU features: nop, `mb586`, or `mfence`.
- 386 systems switch to copy-on-reference mode and interrupt-disabled compare-and-swap.

Dependencies:
- Depends on x86 CPUID/MSR/CR helpers, i8259/i8253, MTRR code, Plan 9 devtab helpers, and known architecture list.

Notable risks:
- `#P/iob/iow/iol` are powerful privileged raw I/O interfaces.
- `archctl coherence nop` is only permitted on uniprocessors and is noted safe only under VMware.
- Some CPU type tables contain trial-and-error/guesswork timing constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devether.c

Generic PC Ethernet device multiplexer and card probing glue for Plan 9 `#l`.

Key responsibilities:
- Maintains discovered `Ether` controllers in `etherxx`.
- Implements devtab operations through the generic `netif` layer.
- Dispatches controller-specific attach, statistics, control, transmit, shutdown, and reset hooks.
- `etheriq()` demultiplexes received Ethernet packets to matching `Netfile`s by EtherType/promiscuous/multicast/address criteria.
- `etheroq()` handles outbound queueing, local loopback/promiscuous/broadcast feedback, and transmit kick.
- Supports packet header tracing for header-only listeners.
- Parses Ethernet addresses from hex strings.
- Registers card drivers through `addethercard()`.
- Probes configured `etherN` entries first, then auto-probes registered card types unless `*noetherprobe` is set.
- Sizes netif input/output queues based on interface Mbps, with memory caps.
- Provides a slow Ethernet CRC32 helper.

Important behavior:
- Outbound writes set the packet source address to the interface MAC.
- Multicast packets are dropped unless broadcast, promiscuous mode, or active multicast membership matches.
- Bridged packets are filtered from local feedback unless originated locally.
- IRQ2 is remapped to IRQ9.
- A negative `ether->irq` means no interrupt is used.

Dependencies:
- Depends on `etherif.h`, `../port/netif.h`, queue/block APIs, card-specific reset hooks, and Plan 9 devtab helpers.

Notable risks:
- Queue sizing is heuristic and tied to `mainmem->maxsize`.
- `etheriq` optimizes by passing the original received block to one recipient and copying for others; callers must respect ownership return semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devfloppy.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devfloppy.c

Intel 82077A/8272A-compatible floppy controller driver for Plan 9 `#f`.

Key responsibilities:
- Defines floppy device qids, supported disk formats, controller byte-per-sector encodings, and global controller state.
- `floppyreset()` probes platform setup, computes type capacities/track sizes, initializes DMA, allocates drive state/cache buffers, resets motors/controller, and runs platform setup.
- Exposes per-drive `fdNdisk` and `fdNctl`.
- Starts a kernel process to power down idle motors.
- Detects media changes and density by seeking/reading while cycling through compatible formats.
- Uses a per-track cache for reads.
- Validates sector-aligned I/O.
- Implements read/write data paths through seek, DMA setup, command issuance, wait, result validation, and retry.
- Handles control commands: `debug`, `nodebug`, `eject`, `format`, and `reset`.
- Implements controller command send/result receive, sense interrupt, recalibrate, seek, reset/revive, motor control, and interrupt handler.

Important behavior:
- Reads always come through a cached track; writes invalidate matching cached cylinder.
- Media change detection increments qid version and returns `Eio` when an open file sees changed media.
- Transfer retries are bounded by `dp->maxtries`, lower while probing.
- Controller “confused” state triggers full reset and per-drive recalibration.
- `floppywait` synthesizes interrupt handling after timeout for some portable power-management cases.
- Formatting writes per-sector ID records track by track using DMA.

Dependencies:
- Depends on platform-specific floppy hooks declared in comments: port I/O, DMA setup/end/init, `floppyexec`, `floppyeject`, and setup functions from `floppy.h`/platform code.

Notable risks:
- Timing and retries are highly hardware-dependent.
- DMA buffer allocation must satisfy low-memory/alignment constraints.
- Many errors mark controller or drive confused and retry/reset rather than giving detailed cause.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devfloppy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devi82365.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/devi82365.c

Intel 82365SL-compatible PCMCIA controller driver and `#y` PC card memory/attribute interface.

Key responsibilities:
- Defines 82365 register indices, Cirrus/Vadem extension registers, memory-window registers, and PC Card configuration-register offsets.
- Probes Intel, Cirrus CL-PD6710/6720, and Vadem VG-46x compatible controllers on standard index/data ports.
- Initializes PCMCIA slots, interrupt-on-card-change, slot power/reset state, and global `pcmspecial` hooks.
- Tracks slot presence, power, battery, write-protect, busy, and CIS/version data.
- Powers slots on/off with empirical delays and reads CIS through `pcmcisread`.
- Handles card-change interrupts and powers down removed cards.
- Maps card memory/attribute regions into ISA UMB space with 4 KiB granularity through `pcmmap`/`pcmunmap`.
- Exposes per-slot `pcmNmem`, `pcmNattr`, and `pcmNctl`.
- Implements byte-based memory/attribute reads/writes via mapped windows.
- Provides special-card lookup/configuration by version-string substring for drivers.
- `pcmio()` selects a CIS configuration table, configures interrupt routing, power, I/O windows, configuration register, I/O base, and I/O size.

Important behavior:
- Opening memory/attribute/control files increments slot reference and powers/enables the card; close decrements and may power it down.
- `pcmcia_pcmspecial` avoids powering cards too often by reusing cached CIS data for two minutes.
- `pcmio` remaps IRQ2 to IRQ9 and tries default, exact port/IRQ match, IRQ-capable, then any I/O config.
- Attribute-memory configuration-register bytes are spaced as even offsets (`<< 1`), matching PCMCIA attribute memory access conventions.

Dependencies:
- Depends on ISA I/O allocation, UMB allocation, CIS parsing structures/functions, Plan 9 devtab helpers, and interrupt registration.

Notable risks:
- Hardware probing writes magic sequences to detect Cirrus/Vadem chips.
- Mapping uses scarce ISA/UMB address space and returns failure when unavailable.
- Slot power/reset delays are empirical.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/devi82365.c -->
# Group Research: group_1479_plan9_sources_os_plan9_plan9_sys_src_9_pc_hcwAMC_h_sources_os_plan9_8b293127f650

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/hcwAMC.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/hcwAMC.h

- Size/hash: 2027 lines, 166004 bytes, SHA-256 `9fe944e6fed78605d6ebbbfda171ef1cb815edfefa52f994bd154f51cec8d670`.
- Purpose: Defines one static byte array, `static uchar hcwAMC[]`, containing 32385 hex byte literals. There are no functions, macros, structs, comments, or conditional sections.
- Integration: Included by `sources/os/plan9/plan9/sys/src/9/pc/devtv.c`, where `kfirloadu(tv, hcwAMC, sizeof hcwAMC)` loads the blob into the TV/video hardware path.
- Behavior: This is firmware or microcode-style data, not executable C control flow. The source file’s behavior is entirely determined by consumers that pass the byte buffer to a device loader.
- Dependencies: Relies on the including translation unit to have defined `uchar`.
- Research notes: Treat as a hardware payload asset for the Plan 9 PC TV driver. It is not filesystem-facing except as part of the broader kernel source tree inventory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/hcwAMC.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/i8253.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/i8253.c

- Size/hash: 365 lines, 7544 bytes, SHA-256 `52351080e181662cdc51bd2ba37cc1898429fa7cc1898429fa7ccedb77bc3a06d5858749b918`.
- Purpose: PC 8253/8254 programmable interval timer support: boot-time timer setup, clock interrupt enablement, CPU frequency estimation, fast tick reads, and calibrated delay loops.
- Main state: `I8253 i8253` tracks the programmed period, enabled flag, tick frequency, last counter-2 sample, cumulative ticks, and period-set count under a `Lock`.
- Key functions: `i8253init`, `guesscpuhz`, `i8253timerset`, `i8253enable`, `i8253read`, `delay`, `microdelay`, and `perfticks`.
- Control flow: `i8253init` allocates timer I/O ports, programs counter 0 for scheduler interrupts, counter 2 as a free-running clock source, and waits until counting begins. `i8253enable` registers `i8253clock` on `IrqCLOCK`; that handler calls `timerintr`.
- Timing model: `i8253read` latches counter 2, accounts for countdown/wrap behavior, updates cumulative ticks, and returns shifted ticks for extra precision. `i8253timerset` clamps one-shot periods between `MinPeriod` and `MaxPeriod`.
- Watchdog handling: `wdogpause`, `wdogresume`, `delay`, and `microdelay` avoid triggering the watchdog during long CPU-bound loops on CPU 0.
- Dependencies: Uses `io.h` IRQ constants, low-level `inb/outb`, `intrenable`, `cycles`, `aamloop`, `timerintr`, `watchdog`, and per-CPU `Mach` fields.
- Research notes: Core PC kernel timing substrate. Filesystem relevance is indirect: it drives scheduler and timer behavior used by all kernel work, including storage and VFS activity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/i8253.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/i8259.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/i8259.c

- Size/hash: 214 lines, 4586 bytes, SHA-256 `558807ad2c10f245a8085d7f4e033c5c639e08b72a92642c5e148702468ba980`.
- Purpose: Dual 8259 programmable interrupt controller setup and mask management for legacy PC IRQ routing.
- Main state: `i8259lock`, `i8259mask` initialized to all disabled, and exported `i8259elcr` recording level-triggered IRQs detected via ELCR ports.
- Key functions: `i8259init`, `i8259isr`, `i8259enable`, `i8259vecno`, `i8259disable`, `i8259on`, and `i8259off`.
- Control flow: `i8259init` programs master/slave PIC ICWs, maps IRQs to `VectorPIC` and `VectorPIC+8`, unmasks cascade IRQ2, sets ISR reads, probes ELCR, then restores masks.
- Interrupt handling: `i8259isr` validates vector range, reads ISR state, sends EOI to master and slave as needed, and reports whether the IRQ bit was in service.
- Enable semantics: `i8259enable` rejects out-of-range IRQs and shared non-level-triggered IRQs, unmasks the selected bit, and installs either `eoi` or `isr` callback behavior on the `Vctl`.
- Dependencies: Uses `io.h` vector and `Vctl` definitions plus `inb/outb`, Plan 9 locks, and arch tables in `devarch.c`.
- Research notes: Important for disk, network, keyboard, timer, and other interrupt-driven drivers. Filesystem relevance is through hardware interrupt delivery for storage devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/i8259.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/init9.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/init9.c

- Size/hash: 7 lines, 94 bytes, SHA-256 `103787d67b9a00d968d57f7ffe966d83f91281e4373c80f765269b83f0577a10`.
- Purpose: Tiny C entry shim for the first user-space boot program path.
- Contents: Declares `extern void startboot(char*, char**);` and defines `_main(char *argv0)` to call `startboot(argv0, &argv0)`.
- Integration: Bridges architecture-specific startup calling convention to the portable boot startup helper.
- Dependencies: Requires `startboot` from the boot/runtime side.
- Research notes: No filesystem implementation logic, but it participates in initial boot handoff toward `/boot`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/init9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/initcode.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/initcode.s

- Size/hash: 23 lines, 282 bytes, SHA-256 `5aad3ae5db916f7ab353b139cfe140ab830073c6fe3436a51650de505750914f`.
- Purpose: First user text copied by `main.c:userinit` into the initial process. It immediately executes `/boot`.
- Contents: Includes syscall numbers, defines `TEXT main(SB)`, builds arguments for `exec("/boot", bootv)`, invokes Plan 9 syscall trap `INT $64` with `EXEC`, then loops forever if exec returns.
- Data: Defines global `boot` string storage containing `"/boot"`.
- Integration: `main.c` copies `initcode` into the first user text page and builds the user stack with boot arguments; this assembly is the first user-mode instruction sequence.
- Dependencies: `/sys/src/libc/9syscall/sys.h`, kernel syscall vector `VectorSYSCALL = 64`.
- Research notes: Bootstraps the user-level root of the system. Filesystem relevance is early: `/boot` resolution begins the user-space boot and namespace setup path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/initcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/io.h

- Size/hash: 384 lines, 9722 bytes, SHA-256 `f53f636f658d94947b04646ddcaee323db3757e3f52a91233bcd29bc6a445dd1`.
- Purpose: Shared PC I/O, interrupt, bus, PCI, SMBus, and PCMCIA definitions for the Plan 9 x86 kernel.
- CPU macros: `X86STEPPING`, `X86MODEL`, and `X86FAMILY` extract CPUID family/model data including extended bits.
- Interrupt model: Defines exception vectors, PIC vectors, LAPIC offsets, syscall vector 64, APIC vector range, IRQ constants, and `Vctl` interrupt-handler records.
- Bus encoding: Defines bus type enum and `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`, and `BUSUNKNOWN` macros for TBDF addressing.
- PCI definitions: Contains standard PCI config offsets, base/subclass constants, header-specific offsets, `Pcisiz`, `Pcidev`, common vendor IDs, and ISA/PCI address-window macros.
- SMBus/PCMCIA definitions: Defines SMBus transaction enum and `SMBus`; defines `PCMmap`, `PCMconftab`, and `PCMslot` structures for PCMCIA slot/configuration state.
- Dependencies: References Plan 9 kernel types such as `Lock`, `QLock`, `Rendez`, `Pcidev`, `Ureg`, and `KNAMELEN`.
- Research notes: This is a hardware interface contract header. Storage drivers use these definitions for PCI discovery, IRQ registration, and bus/device addressing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/kbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/kbd.c

- Size/hash: 741 lines, 14969 bytes, SHA-256 `7841895089780d4f8199eb782dc59a7357b2c83331c91e98fe2c15e4cd8f41f5`.
- Purpose: i8042 PS/2 keyboard and auxiliary-port input driver, including scan-code translation tables and runtime keymap accessors.
- Data tables: Defines `kbtab`, `kbtabshift`, `kbtabesc1`, `kbtabaltgr`, and `kbtabctrl` for normal, shifted, escaped, AltGr, and control scan-code mappings.
- State: `Kbscan` tracks escape prefixes, modifier states, compose collection, mouse-button state, and collected runes separately for internal and external scan sources.
- Controller helpers: `outready` and `inready` poll status bits; `i8042a20` enables A20; `i8042reset` requests reset through the keyboard controller.
- Aux path: `i8042auxcmd`, `i8042auxcmds`, and `i8042auxenable` send mouse/aux commands through command `0xD4`, install an aux byte callback, and enable `IrqAUX`.
- Keyboard path: `kbdinit` drains and configures the controller command byte; `kbdenable` allocates `kbdq`, claims I/O ports, enables `IrqKBD`, and clears num-lock LED state.
- Interrupt flow: `i8042intr` reads status/data under lock, dispatches mouse bytes if `Minready` is set, otherwise passes keyboard scan codes to `kbdputsc`.
- Translation flow: `kbdputsc` handles E0/E1 escapes, key-up state, modifiers, compose sequences via `latin1`, Ctrl-Alt-Del exit, F11/F12 debug toggles, and queueing translated runes to `kbdq`.
- Keymap API: `kbdputmap` and `kbdgetmap` expose editable mapping tables used by the generic keyboard-map device.
- Dependencies: Uses `inb/outb`, `delay`, `intrenable`, `kbdputc`, `kbdq`, `latin1`, `qopen`, `qnoblock`, Plan 9 error handling, and `io.h` IRQ constants.
- Research notes: Not filesystem code, but part of the PC console/input substrate used during local boot, configuration, and interactive recovery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/kbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/l.s

- Size/hash: 1319 lines, 30391 bytes, SHA-256 `f677daa0a6bc72aca517f2cfa337b336aad91ed1938b94c45ef8e959987eb816`.
- Purpose: Core x86 assembly support for Plan 9 PC kernel startup, real-mode BIOS transitions, port I/O, control registers, CPU feature probes, floating point, spl/atomics, halt, and trap vectors.
- Boot path: `_startKADDR` jumps to physical `_startPADDR`; `_multibootheader` provides multiboot metadata; `_startPADDR` installs an initial GDT, enters 32-bit mode, builds bootstrap page tables, enables paging, clears BSS, initializes `m`, creates a stack, clears EFLAGS, and calls `main`.
- Initial memory setup: Uses `CPU0PDB`, `CPU0PTE`, `CPU0PTE1`, `CPU0GDT`, `CPU0MACH`, `MACHADDR`, and page-table macros from `mem.h`.
- Low-power path: `idle` loops with `STI; HLT`; `halt` conditionally halts only when `nrdy` indicates no ready process.
- Real-mode support: `realmode0`, `physcode`, `again16bit`, `now16real`, and return paths switch between paged protected mode and real mode to execute BIOS interrupts with register state stored in the real-mode Ureg area.
- BIOS32 support: `bios32call` loads register arguments, performs a far call through a supplied pointer, stores results, and returns carry status.
- Port I/O: Implements `inb/insb/ins/inss/inl/insl` and `outb/outsb/outs/outss/outl/outsl`.
- CPU registers/features: Implements `lgdt`, `lidt`, `ltr`, CR0/CR2/CR3/CR4 accessors, `invlpg`, `wbinvd`, `_cycles`, `lcycles`, `rdmsr`, `wrmsr`, `cpuid`, and `aamloop`.
- Floating point: Provides x87 and SSE enable/disable/save/restore/status/env/clear routines: `fpon`, `fpoff`, `fpinit`, `fpx87save`, `fpx87restore`, `fpstatus`, `fpenv`, `fpclear`, `fpssesave0`, `fpsserestore0`.
- Interrupt priority/atomic helpers: Defines `splhi`, `spllo`, `splx`, `islo`, `tas`, `_xinc`, `_xdec`, memory barriers, `xchgw`, `cmpswap486`, `mul64fract`, `gotolabel`, and `setlabel`.
- Trap path: `_strayintr` and `_strayintrx` build `Ureg` frames and call `trap`; `forkret` restores state; `vectortable` defines 256 vector stubs with syscall vector `0x40` routed to `_syscallintr`.
- Dependencies: Includes `mem.h` and `/sys/src/boot/pc/x16.h`; depends on C symbols including `main`, `trap`, `m`, `nrdy`, and kernel memory constants.
- Research notes: Foundational architecture code. It has broad indirect filesystem impact because it establishes the kernel execution environment, interrupt handling, TLB behavior, and syscall entry used by all OS services.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/main.c

- Size/hash: 982 lines, 19158 bytes, SHA-256 `632e80c024419ef6cbcf0b2c7764ae88b1b337095ec0b855e3ceb1573bb940ef`.
- Purpose: Main PC kernel bootstrap and machine-dependent process, FPU, reboot, configuration, and idle support.
- Global state: Defines `Mach *m`, `Conf conf`, boot/config arrays, `bootdisk`, initial user stack pointer `sp`, `delaylink`, and idle policy flags.
- Boot option parsing: `options` reads boot loader configuration from `BOOTARGS`, strips CR, normalizes tabs, splits `name=value` lines, ignores comments, and fills `confname/confval`.
- Main boot sequence: `main` performs early console/video setup, machine init, option parsing, I/O init, trap/MMU init, keyboard/timer/CPU/memory/config/arch setup, link loading, device reset, page/swap/user process init, then enters `schedinit`.
- Machine init: `mach0init` binds CPU0 `Mach`, PDB, and GDT addresses; `machinit` clears and reinitializes the current `Mach` with a temporary delay constant.
- First process: `userinit` creates `*init*`, allocates kernel/user stacks and text, calls `bootargs`, copies `initcode` into user text, and makes the process ready.
- User boot args: `bootargs` builds initial argv for `/386/9dos`, converts boot-line prefixes like `fd`, `sd`, and `ether`, and lays argc/argv onto the user stack.
- Configuration sizing: `confinit` computes process/image/swap counts, kernel/user page split, and pool sizes based on memory and `*kernelpercent`.
- FPU handling: `mathinit` installs handlers for coprocessor error, emulation fault, and segment overrun; helper routines save/restore x87/SSE state, post notes, and protect note handlers.
- Process machine state: `procsetup`, `procrestore`, and `procsave` manage lazy FPU state and process cycle accounting, flushing TLBs when saving.
- Shutdown/reboot: `shutdown` coordinates multi-CPU exit and panic delays; `reboot` writes config back, moves to CPU0, shuts down devices/interrupts, maps low memory, installs `rebootcode`, and jumps to the reboot trampoline; `exit` calls arch reset.
- Misc utilities: `isaconfig` parses ISA config entries; `cistrcmp` and `cistrncmp` provide case-insensitive matching; `idlehands` halts based on CPU count and idle policy.
- Dependencies: Touches nearly every PC and port subsystem: `ioinit`, `i8250console`, `trapinit`, `mmuinit`, `kbdinit`, `i8253init`, `cpuidentify`, `meminit`, `archinit`, `links`, `chandevreset`, `pageinit`, `swapinit`, scheduler, channels, pools, and reboot code.
- Research notes: This is the PC kernel orchestration point. Filesystem relevance is direct at boot: root channel initialization, device reset/link loading, swap init, and launch of `/boot`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mem.h

- Size/hash: 162 lines, 5569 bytes, SHA-256 `01e23fdd85c437f1ce555f38e6453fccaaa6fc450fad83ddcc7cbc141aa5c7d2`.
- Purpose: Shared x86 memory, address-space, segment, and page-table constants for C and assembly.
- Basic constants: Defines word/page sizes, page shift, cache-line size, block alignment, FPU save alignment, `MAXMACH`, and `KSTACK`.
- Time constants: Defines `HZ`, `MS2HZ`, and `TK2SEC`.
- Address layout: Defines `KZERO = 0xF0000000`, `KTZERO`, virtual page-table area `VPT`, `KMAP`, `VMAP`, user base/text/stack constants, `USTKSIZE`, and exec stack sizing.
- Reserved low/kernel addresses: Defines `CONFADDR`, `TMPADDR`, `APBOOTSTRAP`, `RMUADDR`, `RMCODE`, `RMBUF`, `IDTADDR`, `REBOOTADDR`, bootstrap CPU page directory/page tables/GDT/Mach addresses, and `CPU0END`.
- Segmentation: Defines GDT segment indices, selectors, descriptor type bits, privilege/present/granularity flags, and data/code readability/writability bits.
- MMU constants: Defines virtual segment-map sizes, PPN masking, PTE valid/write/user/cache/global/large-page bits, and `PDX`/`PTX` index macros.
- Dependencies: Used directly by `l.s`, MMU code, boot code, and machine-dependent C files. Values are ABI-like across boot, assembly, and C.
- Research notes: Critical to virtual memory and boot layout. Filesystem relevance is indirect but fundamental: page, kmap, and user/kernel layout constants constrain buffer, cache, process, and device-memory behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mem.h -->
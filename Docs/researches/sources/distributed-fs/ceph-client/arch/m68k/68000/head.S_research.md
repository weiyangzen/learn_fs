# sources/distributed-fs/ceph-client/arch/m68k/68000/head.S

Purpose: common early boot entry for 68000-core non-MMU systems, including DragonBall/68x328 boards. It establishes CPU state, optional board/LCD registers, RAM descriptors, BSS, stack, and then enters `start_kernel`.

Key exported symbols are `_start`, `_rambase`, `_ramvec`, `_ramstart`, and `_ramend`; `bootlogo_bits` is also exported for LCD-enabled builds. The file computes `RAMEND`, honoring `CONFIG_MEMORY_RESERVE`, and places RAM metadata in writable data for later architecture setup.

Control flow starts by disabling interrupts, optionally emitting the Palm/Pilot ROM signature, disabling watchdogs, and programming 68x328 PLL registers. Under `CONFIG_ROMKERNEL`, it applies uCsimm register setup, optional LCD setup, and copies init data from ROM to RAM. Under RAM-kernel plus ROMFS, it moves the embedded romfs above BSS and advances `_ramstart`. It then clears BSS, sets the initial kernel stack to the top of `init_thread_union`, and calls `start_kernel`.

State/persistence is early global boot state: RAM ranges, vector base, copied data, zeroed BSS, hardware chip-select/LCD/watchdog registers, and the final boot stack. The assembly does not return after `start_kernel`; the `_exit` loop is only a fail-safe.

Dependencies include linker symbols such as `_etext`, `_sdata`, `__bss_start`, `__bss_stop`, `init_thread_union`, Kconfig memory constants, DragonBall hardware addresses, and optional generated logo headers. It integrates with board setup in `m68328.c`, ROM vector setup in `romvec.S`, and generic setup code that consumes `_rambase` and related symbols.

Risks and test signals: incorrect memory ranges can destroy romfs, BSS, or reserved RAM; incorrect PLL/LCD writes can hang early boot with no console. Validate by building representative `CONFIG_ROMKERNEL`, `CONFIG_RAMKERNEL`, `CONFIG_UCSIMM`, `CONFIG_PILOT`, and `CONFIG_INIT_LCD` combinations, checking map symbols, and booting or emulating with early serial/debug output.

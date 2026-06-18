# sources/distributed-fs/ceph-client/arch/m68k/coldfire/head.S

Purpose: first ColdFire kernel entry code. It disables interrupts/cache, sets core base registers, discovers RAM, initializes cache/MMU basics, optionally relocates ROMFS, clears BSS, sets the initial stack/current task, then jumps to `start_kernel`.

Important symbols and macros: `_start`, `_rambase`, `_ramvec`, `_ramstart`, `_ramend`, optional `_init_sp`, `GET_MEM_SIZE`, and board-overridable `PLATFORM_SETUP`. The RAM-size macro has variants for fixed `CONFIG_RAMSIZE`, DMR-based parts, M5272, and M520x SDRAM registers.

Control flow and state: `_start` sets SR to mask interrupts, disables cache through CACR, saves U-Boot stack if enabled, programs MBAR when configured, runs platform setup, sets VBR to `CONFIG_VECTORBASE`, stores RAM base/vector/end globals, programs ACR cache regions, and enables cache. MMU builds set MMUBAR, clear TLBs, enable identity mapping, and jump to virtual space. ROMFS builds copy the ROM filesystem above BSS. It clears BSS, installs `init_thread_union` as stack, fills m68k CPU/MMU/FPU/machine globals for MMU builds, then calls `start_kernel`.

Dependencies and integration: linker symbols, ColdFire control registers, SoC memory-controller headers, Linux boot ABI, and later `vectors.c` trap setup. State stored before BSS clear is deliberately in `.data`.

Risks and test signals: RAM probing only works for supported SDRAM layouts and RAM at expected base. Cache/MMU register mistakes fail before console. Test with early boot on each config, RAM size reporting, ROMFS boot, U-Boot handoff, and MMU/no-MMU variants.

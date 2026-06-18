# sources/distributed-fs/ceph-client/arch/m68k/kernel/head.S

## Purpose

`head.S` is the MMU-enabled Linux/m68k bootstrap for classic 68020/030/040/060 and platform families such as Amiga, Atari, Macintosh, HP300, VME, Q40, Apollo, Sun3x, and the virtual platform. It runs before normal C setup, consumes bootinfo records placed after `_end`, builds the first kernel page tables, maps the kernel and early machine I/O windows, enables the MMU and caches, installs an initial stack, calls `base_trap_init()`, and finally enters `start_kernel()`.

## Important APIs, Types, and Functions

The exported entry symbols are `_stext`, `_start`, and `__start`. The file also defines `kernel_pg_dir` at `_stext`, and data symbols consumed by C code: `availmem`, `m68k_init_mapped_size`, `m68k_pgtable_cachemode`, `m68k_supervisor_cachemode`, plus VME/Q40 support symbols when configured. Its internal macro-callable routines include `get_bi_record`, `mmu_map`, `mmu_map_tt`, `mmu_fixup_page_mmu_cache`, `mmu_temp_map`, `mmu_engage`, `mmu_get_root_table_entry`, `mmu_get_ptr_table_entry`, `mmu_get_page_table_entry`, `get_new_page`, serial output helpers, and optional early console helpers.

## Control Flow

Boot starts by setting the temporary stack to `_stext`, reading `BI_MACHTYPE`, `BI_CPUTYPE`, `BI_FPUTYPE`, and `BI_MMUTYPE`, converting CPU bits into local `CPUTYPE_*` flags, choosing cache attributes, raising interrupt priority to `0x2700`, and collecting machine-specific bootinfo needed for very early serial/video debug. It then initializes serial and optional Mac framebuffer console output.

The core path maps the initial kernel memory window at `PAGE_OFFSET`, adds per-machine I/O mappings through either full page tables or transparent translation registers, fixes MMU table cache attributes on 040/060, optionally dumps mappings, and calls `mmu_engage`. After the MMU transition it rewrites early physical addresses to their final logical mappings, enables CPU caches, switches to `init_thread_union`, initializes the exception vector base through `base_trap_init`, and jumps to `start_kernel`.

## State and Persistence Behavior

The file persists early architecture state in global words used by later C setup: boot CPU/machine attributes, page-table cache modes, initial mapped size, `availmem`, platform debug pointers, and the kernel page directory. It allocates early page and pointer tables by bumping `L(memory_start)` until `availmem` is fixed. It also permanently programs MMU root pointers, transparent translation registers, cache control registers, and, for debug builds, early serial or framebuffer state.

## Dependencies and Integration Points

It depends on bootinfo record layout from `<asm/bootinfo*.h>`, m68k page flag definitions, platform machine constants, `init_task`, `init_thread_union`, `base_trap_init`, and `start_kernel`. It is paired with `setup_mm.c`, which rereads bootinfo and consumes `availmem`, `m68k_*` globals, and platform machine hooks. `vectors.c` relies on `base_trap_init()` being called before the kernel uses instructions that may trap on 68060/FPU support code.

## Risks and Edge Cases

This is CPU- and board-specific assembly with many hard-coded physical ranges. Wrong bootinfo, stale machine constants, or misdetected CPU type can leave the kernel without valid I/O mappings or cache attributes. The MMU transition is fragile because the program counter, stack, frame pointer, and return address are all adjusted while switching root tables. Early page-table allocation assumes the bootinfo block directly follows the kernel and that free memory is page aligned after `BI_LAST`. Debug serial and console paths directly touch hardware and can hang if selected for the wrong board. Cache-mode regressions are especially risky on 040/060 because page tables and writeback caches have CPU-specific coherency rules.

## Test Signals

Useful evidence is successful boot on representative 030, 040, 060, Sun3x, and platform-specific configs; early printk progress characters through `J`/`K`; correct `/proc/cpuinfo` values later from the same globals; valid `availmem` and `m68k_init_mapped_size`; no bus error during MMU enable; and a final map showing kernel text/data and expected I/O ranges. Debug builds can enable `MMU_PRINT` or `CONFIG_EARLY_PRINTK` to trace map construction.

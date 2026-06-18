# sources/distributed-fs/ceph-client/arch/arc/kernel/unwind.c

Purpose: implements ARC kernel stack unwinding from DWARF2 `.eh_frame` metadata, with a compact generated header table for fast FDE lookup and optional module unwind tables.

Important APIs/types/functions: key types are `struct unwind_table`, `struct unwind_state`, `struct unwind_item`, and CIE/FDE header entries. Public APIs are `arc_unwind_init()`, `unwind_add_table()`, `unwind_remove_table()`, and exported `arc_unwind()`. Helpers parse LEB128, encoded pointers, CIE/FDE relationships, FDE pointer type, and DWARF CFA instructions.

Control flow: boot initializes `root_table` from linker-provided `__start_unwind`/`__end_unwind`, then builds a sorted FDE header with `init_unwind_hdr()`. `arc_unwind()` finds the table covering the current PC, binary-searches the header for an FDE, validates its CIE, parses CIE/FDE CFI up to the target PC, computes CFA, and applies register recovery rules from memory/register/value sources. If DWARF lookup fails and frame pointers are configured, it attempts a frame-pointer fallback.

State and persistence: `root_table` persists for kernel text, while module tables are linked through `root_table.link` and `last_table`. Header storage is allocated with memblock at boot or kmalloc for modules. The active unwind modifies caller-provided `struct unwind_frame_info`.

Dependencies and integration: consumes linker sections emitted by `vmlinux.lds.S`, module memory metadata, stop-machine-era module synchronization assumptions, `__get_user()` for safe stack reads, `sort()`, and ARC unwind register metadata from `asm/unwind.h`. Used by `stacktrace.c`.

Risks: malformed or unsupported CFI panics during header construction or returns unwind errors at runtime. Module removal synchronization is marked `XXX: SMP`, so lifetime assumptions are important. Stack bounds and alignment checks protect memory reads but can truncate traces. Unsupported DWARF opcodes or expression-based CFA rules fail unwinding.

Test signals: oops and `dump_stack()` traces, module load/unload with stack traces through module text/init text, corrupted or absent `.eh_frame` handling, frame-pointer fallback builds, and deep-call unwinding through leaf and non-leaf functions.

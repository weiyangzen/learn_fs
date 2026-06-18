<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vec-copy-unaligned.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vec-copy-unaligned.S

Purpose: Provides vectorized helper routines for copying unaligned words and bytes during unaligned-access performance probing.

Important APIs/types/functions: Defines `__riscv_copy_vec_words_unaligned` and `__riscv_copy_vec_bytes_unaligned`.

Control flow: Each routine enables a vector loop, uses vector loads/stores with word or byte element widths, decrements length by processed vector length, and returns after all data is copied.

State and persistence: Mutates only caller-provided destination memory and vector registers; no persistent state.

Dependencies and integration points: Used by `unaligned_access_speed.c` to benchmark vector unaligned access.

Risks: Vector state use must be bracketed by callers so kernel/user vector state is not corrupted. Loop length and element width must handle tails correctly.

Test signals: Vector unaligned speed probe, data integrity comparison, and builds with vector enabled/disabled.

Source read size: 59 lines, 1444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vec-copy-unaligned.S -->

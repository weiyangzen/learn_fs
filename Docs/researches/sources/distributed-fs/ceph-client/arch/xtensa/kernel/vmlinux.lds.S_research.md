# sources/distributed-fs/ceph-client/arch/xtensa/kernel/vmlinux.lds.S

Purpose: Xtensa kernel linker script defining image entry, section layout, vector placement/relocation metadata, init/data/BSS layout, XIP layout, and Xtensa-specific metadata sections.

Important APIs, types, and functions: `OUTPUT_ARCH(xtensa)`, `ENTRY(_start)`, `jiffies` aliasing, `MERGED_VECTORS`, `RELOCATE_ENTRY`, `SECTION_VECTOR4`, `SECTION_VECTOR2`, vector section symbols, `__boot_reloc_table_start/end`, `__tagtable_begin/end`, and XIP symbols.

Control flow: Lays out text from `KERNELOFFSET`, optionally merges vectors into `.text` at vector virtual addresses, emits rodata/data/init/percpu sections, records relocation triples for vectors/XIP/secondary reset, emits separate output vector sections when relocation is needed, aligns init end and BSS, and preserves `.xt.prop/.xt.insn/.xt.lit`.

State and persistence: Defines the symbols consumed by boot code, setup memory reservation, vector relocation, KASAN/layout logging, init freeing, and XIP runtime relocation.

Dependencies and integration: Integrates with generic `asm-generic/vmlinux.lds.h`, Xtensa core/vector address macros, `setup.c` section reservations, `vectors.S` input sections, boot relocation code, and XIP configuration.

Risks: Vector address/alignment errors break exception dispatch before diagnostics; relocation table order must match boot copier expectations; XIP `LOAD_OFFSET` arithmetic is sensitive; `jiffies` offset differs by endian.

Test signals: Link successful kernels for merged and relocated vectors, inspect `System.map` vector symbols, boot XIP/non-XIP variants, verify section reservations, and confirm `.taglist` bootparam parser range.

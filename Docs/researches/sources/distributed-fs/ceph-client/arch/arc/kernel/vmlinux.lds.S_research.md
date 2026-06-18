# sources/distributed-fs/ceph-client/arch/arc/kernel/vmlinux.lds.S

Purpose: linker script for ARC kernel image layout.

Important sections/symbols: sets `OUTPUT_ARCH(arc)` and `ENTRY(res_service)`, defines endian-specific `jiffies`, places vector table at `CONFIG_LINUX_LINK_BASE`, handles optional ICCM/DCCM ARC fast sections, lays out init RAMFS/text/data/arch info/percpu, normal text/data/BSS/RO data, exception tables, unwind `.eh_frame`, debug/discard sections, and extension maps.

Control flow: not executable code, but controls boot-time and runtime address layout. Init sections precede main text to reduce relocation displacement. `.fixup` and exception tables are placed with text, while `.eh_frame` is either preserved with `__start_unwind`/`__end_unwind` or discarded depending on `CONFIG_ARC_DW2_UNWIND`.

State and persistence: defines persistent kernel image symbols such as `_text`, `_stext`, `_etext`, `_sdata`, `_edata`, `_end`, `__init_begin`, `__init_end`, `__arch_info_begin/end`, and optional DCCM/ICCM bounds.

Dependencies and integration: integrates with generic linker macros from `asm-generic/vmlinux.lds.h`, ARC cache/page/thread headers, unwind code, exception-table fixups, boot/init memory setup, and architecture-specific tightly coupled memory support.

Risks: layout mistakes can break vectors, relocation range, init freeing, unwind table discovery, exception fixups, or tightly coupled memory alignment. Discarding debug/unwind sections under the wrong configuration removes required runtime metadata.

Test signals: successful link/boot, correct vector base, exception-table fixup tests, `CONFIG_ARC_DW2_UNWIND` stack traces, init section freeing, and builds with ICCM/DCCM/endian variants.

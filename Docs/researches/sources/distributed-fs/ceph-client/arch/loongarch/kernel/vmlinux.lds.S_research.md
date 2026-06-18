# sources/distributed-fs/ceph-client/arch/loongarch/kernel/vmlinux.lds.S

Purpose: defines the LoongArch kernel linker script, including load address, text/init/data/BSS layout, EFI PE/COFF alignment metadata, ORC unwind tables, and discarded sections.

Important APIs, types, and symbols: establishes `OUTPUT_ARCH(loongarch)`, `ENTRY(kernel_entry)`, PHDRs, `_text`, `_stext`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_edata`, `_end`, relocation bounds, optional RELR bounds, optional EFI header symbols, and `jiffies = jiffies_64`.

Control flow: the script orders head text, executable text groups, fixups, init/exit text and data, alternatives, optional percpu, rodata, GOT/PLT, writable data, relocations, ORC tables, small data, BSS, debug metadata, modinfo, ELF details, and discard rules. It aligns major segments to `PECOFF_SEGMENT_ALIGN` and pads writable data to `PECOFF_FILE_ALIGN`.

State and persistence: the output binary layout is persistent build state consumed by boot loaders, runtime symbol ranges, exception tables, ORC unwinding, relocation code, and EFI stub metadata.

Dependencies and integration points: includes generic `vmlinux.lds.h`, architecture offsets, ORC lookup definitions, and `image-vars.h`. It integrates with build tools, EFI stub, relocation processing, objtool ORC emission, exception fixups, and module/debug metadata.

Risks: alignment or section ordering errors can break boot, early page tables, ORC lookup, alternatives, exception fixups, or EFI loading. Discarding the wrong metadata can hide needed runtime sections.

Test signals: successful kernel link, boot under EFI and non-EFI paths, ORC unwinder boot validation, relocation tests, section layout inspection with `readelf`, and early boot page table stability.

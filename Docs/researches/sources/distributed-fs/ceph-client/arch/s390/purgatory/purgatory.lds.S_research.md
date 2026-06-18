<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.lds.S -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.lds.S

Purpose: This linker script defines the layout of the standalone s390 purgatory ELF image.

Important APIs/types/functions: It sets `OUTPUT_FORMAT("elf64-s390")`, `OUTPUT_ARCH(s390:64-bit)`, entry `purgatory_start`, and section symbols `_head`, `_ehead`, `_text`, `_etext`, `_rodata`, `_erodata`, `_data`, `_edata`, `_bss`, `_ebss`, and `_end`.

Control flow: Link-time layout starts at address zero, places head text, text, rodata, data, aligns BSS to 256 bytes and then 8 bytes, and discards unwind/export CRC/ksymtab sections that have no purpose in purgatory.

State and persistence: The layout determines the embedded purgatory binary's offsets and symbols used by assembly for stack, end, and relocation calculations.

Dependencies and integration points: It depends on generic vmlinux linker macros, s390 ELF format, and symbols referenced by `head.S` and kexec loader code.

Risks and test signals: Section placement must match assumptions in self-relocation and BSS zeroing. Unexpected retained sections could bloat or break freestanding execution. Tests include link success, readelf section layout, absence of discarded metadata, and kexec boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.lds.S -->

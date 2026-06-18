# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/include/arch/elf.h

Purpose: declares LoongArch ELF machine and relocation constants for objtool, including fallback definitions when system headers lack them, and maps them to generic objtool relocation aliases.

Important APIs/types/functions: defines `R_LARCH_NONE`, `R_LARCH_32`, `R_LARCH_64`, `R_LARCH_32_PCREL`, `R_LARCH_64_PCREL`, `EM_LOONGARCH`, and generic aliases `R_NONE`, `R_ABS32`, `R_ABS64`, `R_DATA32`, `R_DATA64`, `R_TEXT32`, `R_TEXT64`.

Control flow: no runtime control flow; constants are consumed by relocation classification and creation code.

State and persistence behavior: generic relocation aliases determine what relocation types objtool creates in generated sections and writes back to ELF files.

Dependencies and integration points: used by LoongArch `decode.c`, shared ELF relocation helpers, and metadata section writers in `check.c`/ORC code.

Risks: `R_DATA64` and `R_TEXT64` map to a 32-bit PC-relative relocation alias here; that must match the kernel's intended compact metadata encoding. Header drift against LoongArch ABI constants can break host builds or generated metadata.

Test signals: generated `.orc_unwind*`, call-site, and other objtool sections should have relocations accepted by LoongArch linker and kernel runtime consumers.

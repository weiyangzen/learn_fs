<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/relocs.c -->
# sources/distributed-fs/ceph-client/arch/s390/tools/relocs.c

Purpose: This host utility scans a 64-bit big-endian s390 ELF executable/shared object and emits relocation offsets for absolute 64-bit relocations into a `.vmlinux.relocs_64` assembly section.

Important APIs/types/functions: Global ELF state is `ehdr`, `shnum`, `shstrndx`, `secs`, and `relocs64`. Core helpers are endian converters, `die`, `read_ehdr`, `read_shdrs`, `read_relocs`, `add_reloc`, `do_reloc`, `walk_relocs`, `sort_relocs`, `emit_relocs`, `process`, and `main`.

Control flow: `main` opens the input ELF, verifies the header class/endian/machine/type, reads section headers including extended section counts, reads all SHT_RELA relocation sections with endian conversion, walks relocations that apply to allocated sections, records offsets only for `R_390_64`, ignores known PC-relative/GOT/no-op relocations, errors on unsupported relocation types, sorts offsets, and prints `.long` directives in the reloc section.

State and persistence: The tool stores parsed section headers and relocation arrays in process memory. Persistent output is assembly text on stdout for later build stages.

Dependencies and integration points: It depends on libc, `<elf.h>`, host endian macros/bswap, and s390 relocation constants. It integrates with kernel relocation handling for s390 vmlinux images.

Risks and test signals: ELF validation and endian conversion must be exact because host endianness may differ from target. Unsupported relocation types intentionally fail the build. Offset truncation to 32-bit must match relocation-section consumer expectations. Tests include ET_EXEC and ET_DYN inputs, extended section counts, unsupported relocation injection, little-endian rejection, sorted output comparison, and build/link tests for relocatable s390 kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/relocs.c -->

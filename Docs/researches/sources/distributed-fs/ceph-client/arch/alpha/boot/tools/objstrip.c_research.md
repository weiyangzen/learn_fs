# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/objstrip.c

`objstrip.c` is a host utility that converts ELF or ECOFF Alpha executables into raw bootable binary payloads and can also generate an SRM primary boot block. It is the bridge between linked bootloader/header objects and the byte streams concatenated into boot images.

Important options are `-v` for diagnostics, `-b` for 512-byte padding/zero-filled BSS, and `-p` for primary bootblock generation. In primary mode it writes a 64-quadword block with the string `Linux SRM bootblock`, sector count, starting sector, flags, and checksum. In extraction mode it validates ELF `ET_EXEC`/`EM_ALPHA` or ECOFF executable/OMAGIC headers, computes file and memory sizes, handles an ELF entry-point/p_vaddr workaround, copies the loadable bytes, and zero-fills to BSS/padding length.

Persistent outputs are raw binary files or stdout. Risks include assuming one ELF program header, relying on Linux kernel header structs, host endianness/word-size expectations, and allowing extraction to continue after warning about multiple program headers. Tests should cover ELF and ECOFF fixtures, `-p` checksum generation, BSS zero-fill size, and failure paths for wrong architecture or malformed headers.

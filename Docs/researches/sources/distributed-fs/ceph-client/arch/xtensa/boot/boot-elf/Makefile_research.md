<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/Makefile

## Purpose
Builds the uncompressed Xtensa ELF boot image with reset-vector bootstrap code and an embedded raw kernel binary section.

## Important APIs, Types, And Functions
Key variables and targets are `OBJCOPY_ARGS`, `CPPFLAGS_boot.lds`, `boot-y := bootstrap.o`, `boot.lds`, `Image.o`, and `Image.elf`.

## Control Flow
The Makefile objcopies `vmlinux.bin` into a new `image` section attached to `bootstrap.o`, then links it with `boot.lds` using Xtensa linker flags and no build ID to produce `Image.elf`.

## State And Persistence
Persistent outputs are `Image.o`, generated `boot.lds`, and `../Image.elf`.

## Dependencies And Integration Points
Depends on endian-specific Xtensa ELF objcopy format, `bootstrap.S`, `boot.lds.S`, and the parent boot Makefile's `vmlinux.bin`.

## Risks And Edge Cases
The embedded section flags and linker placement must match the reset vector and kernel load address. Endianness mismatch produces an unusable image.

## Test Signals
Build `make Image`, inspect `Image.elf` sections and entry point, and boot on ISS or hardware using the ELF loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/Makefile -->

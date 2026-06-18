<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/Makefile

## Purpose
Builds the compressed RedBoot-style Xtensa `zImage.redboot` image from bootstrap code, the gzipped kernel image, and boot decompression libraries.

## Important APIs, Types, And Functions
Key variables and targets are `OBJCOPY_ARGS`, `boot-y := bootstrap.o`, `LIBS := arch/xtensa/boot/lib/lib.a arch/xtensa/lib/lib.a`, `zImage.o`, `zImage.elf`, and `zImage.redboot`.

## Control Flow
The Makefile embeds `vmlinux.bin.gz` as an `image` section in `bootstrap.o`, links it with `boot.ld` and decompression libraries into `zImage.elf`, then strips it to a raw binary `zImage.redboot`.

## State And Persistence
Build outputs are `zImage.o`, `zImage.elf`, and `../zImage.redboot`.

## Dependencies And Integration Points
Depends on RedBoot bootstrap assembly, parent boot gzip output, boot lib zlib objects, architecture lib helpers, and Xtensa endian-specific objcopy format.

## Risks And Edge Cases
Linker script, embedded section, and decompressor memory assumptions must agree. Endianness mismatch or missing zlib copy objects breaks the boot image.

## Test Signals
Build and boot `zImage.redboot`, inspect embedded image section and final binary size, and validate decompression path on target platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/boot/Makefile

## Purpose
This boot Makefile builds SPARC boot images, including raw images, compressed images, TFTP/install images, a.out images, and LEON U-Boot images.

## Important APIs, Types, and Functions
It declares host tool `piggyback`, targets `tftpboot.img`, `image`, `zImage`, `vmlinux.aout`, and optional `uImage`. Rules use `OBJCOPY`, `OBJDUMP`, `NM`, `ELFTOAOUT`, gzip, `piggyback`, and `mkimage` with `UIMAGE_LOADADDR` and `UIMAGE_ENTRYADDR`.

## Control Flow
The file strips or converts `vmlinux` into bootable forms. SPARC64 uses `elftoaout` for `vmlinux.aout`; SPARC32 copies a binary image. `zImage` compresses the raw image. `tftpboot.img` combines the a.out kernel, `System.map`, and optional initrd through `piggyback`. LEON builds `uImage` and `uImage.o` through U-Boot tooling.

## State and Persistence Behavior
It creates build artifacts under `arch/sparc/boot`. There is no runtime state in the Makefile itself.

## Dependencies and Integration Points
It integrates top-level `arch/sparc/Makefile` targets with PROM/a.out boot expectations, initrd embedding, U-Boot image creation, and the host `piggyback` utility.

## Risks
Boot image layout is sensitive to alignment, symbol addresses, and host tool availability. Incorrect `piggyback` input or U-Boot load/entry addresses can make an otherwise linked kernel unbootable.

## Test Signals
Build `image`, `zImage`, `tftpboot.img`, `vmlinux.aout`, and LEON `uImage` where configured. Verify file formats with `file`, expected headers, and bootloader acceptance under PROM/U-Boot/QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/Makefile -->

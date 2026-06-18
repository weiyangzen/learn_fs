# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/tools/mkbb.c

`mkbb.c` is a host utility that installs an SRM-compatible boot block while preserving the existing Alpha disklabel. It is used by the boot Makefile after concatenating `lxboot`, `bootlx`, and `vmlinux.nh`.

The key type is the local `bootblock` union, which overlays a 512-byte block as bytes, quadwords, a disklabel at offset 64, and a checksum at the last quadword. `main` opens the target device read/write, reads the 512-byte bootloader block, reads the current disk boot block, copies the disklabel from disk into the bootloader image, recomputes the first-63-quadword checksum, seeks to the start, and writes the full block.

Persistent state is the target block device/file. Risks are significant because this tool writes sector zero: argument reversal, short reads/writes, endian/word-size assumptions for `unsigned long`, and weak error exits can damage a target image. Test signals are host-tool compilation plus running against temporary files with known disklabel/checksum bytes rather than a real device.

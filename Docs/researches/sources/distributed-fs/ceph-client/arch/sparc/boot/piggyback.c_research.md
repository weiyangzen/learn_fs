<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/piggyback.c -->
# sources/distributed-fs/ceph-client/arch/sparc/boot/piggyback.c

## Purpose
`piggyback` is a host utility that modifies a SPARC a.out kernel image in place so it can carry an initial ramdisk for PROM/TFTP booting without NFS.

## Important APIs, Types, and Functions
Important helpers are `align()`, `ld2()`, `st4()`, `die()`, `usage()`, `start_line()`, `end_line()`, `get_start_end()`, and `get_hdrs_offset()`. `main()` accepts `bits vmlinux.aout System.map fs_img.gz`, verifies the a.out magic, finds `_start`/`_end`, locates the `HdrS` boot header, writes root/ramdisk metadata, updates SPARC64 a.out text/data/bss fields, and appends the initrd at an aligned offset.

## Control Flow
The tool parses the bitness, stats the ramdisk, scans `System.map` for `_start` and `_end`, opens the kernel image read-write, validates a.out magic, and locates the boot header either at the SPARC64 fixed offset or by decoding a branch target and searching backward for `HdrS`. It writes big-endian header fields, seeks to the aligned post-kernel payload offset, streams the ramdisk into the image, and closes both files.

## State and Persistence Behavior
The kernel image is modified in place. The utility stores no state outside the output image; all numeric fields are written big-endian because the image is SPARC-facing even when built on a little-endian host.

## Dependencies and Integration Points
It is built as a host program by `arch/sparc/boot/Makefile` and depends on a.out image layout, `System.map` symbol format, `HdrS` layout in SPARC boot assembly, page-size alignment conventions, and optional initrd images.

## Risks
Offset calculation is fragile: stale `System.map`, missing `HdrS`, wrong bitness, short reads, or older `elftoaout` output can corrupt the image. The tool modifies in place and only performs format sanity checks, so callers must provide a disposable boot artifact.

## Test Signals
Run on known SPARC32 and SPARC64 boot images with small initrd inputs. Verify a.out headers, embedded ramdisk size/address fields, appended payload offset, and successful PROM/TFTP boot or QEMU boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/piggyback.c -->

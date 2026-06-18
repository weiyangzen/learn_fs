# File Research: sources/block-storage/parted/libparted/arch/linux.h

This private Linux backend header defines `LinuxSpecific` and the `LINUX_SPECIFIC(dev)` cast helper.

Contents:
- Optionally includes `<blkid/blkid.h>` when available.
- Defines `LINUX_SPECIFIC(dev)` as a cast of `dev->arch_specific`.
- Declares and defines `struct _LinuxSpecific`.

Fields:
- `fd`: active Linux file descriptor for device I/O.
- `major` and `minor`: kernel device numbers captured from `stat()`.
- `dmtype`: device-mapper target type string.
- On s390/s390x:
  - `real_sector_size`: preserved sector size for DASD handling.
  - `devno`: DASD device number.
- With blkid:
  - `probe`: blkid probe handle.
  - `topology`: blkid topology handle.

Research notes:
- This header is intentionally private to the Linux backend and is listed in `EXTRA_libparted_la_SOURCES`, not installed as part of the public API.
- It carries the state required by Linux-specific probing, topology alignment, and device-mapper handling.

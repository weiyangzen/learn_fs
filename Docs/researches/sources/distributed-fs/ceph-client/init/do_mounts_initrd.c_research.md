# sources/distributed-fs/ceph-client/init/do_mounts_initrd.c

## Purpose
`do_mounts_initrd.c` handles deprecated block initrd loading support: it records physical initrd locations from early parameters, honors `noinitrd`, creates `/dev/ram`, asks the ramdisk loader to populate it, warns about deprecation, and removes `/initrd.image`.

## Important APIs, Types, and Functions
Important globals are `initrd_start`, `initrd_end`, `initrd_below_start_ok`, `mount_initrd`, `phys_initrd_start`, and `phys_initrd_size`. Key functions are `no_initrd()`, `early_initrdmem()`, `early_initrd()`, and `initrd_load()`.

## Control Flow
Early parameters `initrdmem=` and `initrd=` parse a physical start and size. The `noinitrd` setup parameter disables mounting. During namespace preparation, `initrd_load()` creates `/dev/ram`, calls `rd_load_image()` to copy/decompress `/initrd.image` into ramdisk, emits a deprecation warning on use, and unlinks `/initrd.image`.

## State and Persistence Behavior
Physical initrd location and size are `__initdata`; ramdisk contents persist only in memory as `/dev/ram0`. Temporary namespace paths `/dev/ram` and `/initrd.image` are removed during the load path.

## Dependencies and Integration Points
It depends on `do_mounts.h`, initrd globals used by architecture boot setup, `memparse`, early parameter registration, and ramdisk image loading in `do_mounts_rd.c`.

## Risks and Test Signals
Risks include malformed `initrdmem`, deprecated `noinitrd` behavior, missing ramdisk support, failure to remove temporary initrd image, and reliance on deprecated block initrd instead of initramfs. Test signals include boots with `initrd=`, `initrdmem=`, `noinitrd`, compressed and filesystem initrd images, and absence of `BLK_DEV_RAM`.

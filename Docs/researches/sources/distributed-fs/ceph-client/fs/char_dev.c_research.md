# sources/distributed-fs/ceph-client/fs/char_dev.c

## Purpose
`char_dev.c` implements Linux character-device number registration, dynamic major allocation, `struct cdev` lifetime, char-device open dispatch, and helper APIs for binding cdevs to devices.

## Important APIs, Types, And Functions
External APIs include `register_chrdev_region()`, `alloc_chrdev_region()`, `unregister_chrdev_region()`, `__register_chrdev()`, `__unregister_chrdev()`, `cdev_alloc()`, `cdev_init()`, `cdev_add()`, `cdev_del()`, `cdev_set_parent()`, `cdev_device_add()`, `cdev_device_del()`, `cdev_put()`, and `chrdev_init()`. Internal state uses `struct char_device_struct`, the `chrdevs` hash, `cdev_map`, and `cdev_lock`.

## Control Flow
Registration reserves major/minor ranges in `chrdevs`; dynamic allocation scans legacy and extended dynamic ranges. `__register_chrdev()` additionally allocates a `cdev`, installs fops, and adds it to `cdev_map`. Opening a char special inode uses `def_chr_fops.open`, resolves the cdev through `kobj_lookup()`, pins its module/kobject, replaces file operations, and calls the driver open method. Deletion unmaps future opens while existing open files keep callable fops.

## State, Persistence, And Dependencies
State is kernel-global and volatile: reserved ranges, kobject map entries, cdev kobjects, inode `i_cdev` links, and module references. It depends on VFS, kobjects, module refcounts, mutex/spinlock locking, device core helpers, and procfs display hooks.

## Integration Points
Every char driver registration path uses these APIs. `cdev_device_add()` bridges cdev lifetime with `struct device`, while `base_probe()` supports module autoload aliases for char majors.

## Risks
Risks include overlapping range detection, major exhaustion, lifetime after `cdev_del()`, module refcount failure during open, parent kobject references, and callers assuming failed `cdev_device_add()` means userspace never opened the cdev.

## Test Signals
Test fixed/dynamic registration, multi-major ranges, overlap failures and unwind, open while deleting, module autoload, cdev-device parent lifetime, proc `/proc/devices` output, and KASAN/KCSAN around inode cdev links.

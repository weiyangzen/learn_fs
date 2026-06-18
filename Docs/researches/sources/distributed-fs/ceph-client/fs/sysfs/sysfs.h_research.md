# sources/distributed-fs/ceph-client/fs/sysfs/sysfs.h

## Purpose
This internal header shares private sysfs declarations across the sysfs implementation files.

## Important APIs, Types, and Functions
It exposes `sysfs_root_kn` from mount code, `sysfs_symlink_target_lock` and `sysfs_warn_dup()` from directory code, file creation internals `sysfs_add_file_mode_ns()` and `sysfs_add_bin_file_mode_ns()`, and `sysfs_create_link_sd()` from symlink code.

## Control Flow and State
There is no runtime control flow. The header establishes internal coupling between sysfs components while keeping implementation helpers out of the public sysfs API header.

## Persistence, Dependencies, and Integration
It depends on `<linux/sysfs.h>` for public structures such as `attribute`, `bin_attribute`, and namespace types. The declarations coordinate kernfs root access, symlink race protection, and low-level file creation used by group code.

## Risks and Test Signals
Risk is interface drift: changing one implementation without updating this header causes build failures or mismatched helper semantics. Build coverage of `fs/sysfs/*.o` is the main signal.

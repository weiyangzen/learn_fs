# sources/distributed-fs/ceph-client/drivers/block/rnull/Kconfig

## Purpose
Adds the kernel configuration option for the Rust null block driver.

## Important APIs, types, and functions
- `config BLK_DEV_RUST_NULL` is a tristate option named "Rust null block driver (Experimental)".
- It depends on `RUST` and `CONFIGFS_FS`.
- Help text describes the driver as a Rust implementation of C `null_blk` with configfs-controlled virtual block devices.

## Control flow
Kconfig makes the module selectable only when Rust support and configfs are enabled. If selected as built-in or module, the corresponding Makefile builds `rnull_mod`.

## State and persistence behavior
No runtime state. Configuration choice persists in the kernel build config.

## Dependencies and integration points
Integrates with the kernel Kconfig system and the rnull Makefile. It signals that userspace control is through configfs.

## Risks and test signals
The help text contains a typo ("virutal"). Build tests should cover `n`, `m`, and `y` where Rust/configfs are available, plus dependency-hidden behavior when either dependency is disabled.

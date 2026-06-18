# sources/distributed-fs/ceph-client/drivers/block/rnull/Makefile

## Purpose
Builds the Rust null block driver object when `CONFIG_BLK_DEV_RUST_NULL` is enabled.

## Important APIs, types, and functions
- `obj-$(CONFIG_BLK_DEV_RUST_NULL) += rnull_mod.o`.
- `rnull_mod-y := rnull.o` makes `rnull.rs` the module's primary object; the Rust module imports `configfs.rs` as a Rust submodule.

## Control flow
The kbuild rule participates in normal kernel build selection. When enabled as a module, it produces `rnull_mod.ko`; when built-in, the object is linked into the kernel.

## State and persistence behavior
No runtime state. It affects build artifacts only.

## Dependencies and integration points
Depends on Kconfig selection and Rust kbuild support. `configfs.rs` is pulled by Rust module resolution rather than directly listed here.

## Risks and test signals
Build coverage should verify module and built-in configurations. Renaming `rnull.rs` or the Rust module name requires synchronized Makefile changes.

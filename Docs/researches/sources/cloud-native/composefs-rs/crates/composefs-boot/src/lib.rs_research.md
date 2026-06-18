# sources/cloud-native/composefs-rs/crates/composefs-boot/src/lib.rs

## Purpose
This is the public crate root for composefs boot integration. It exposes bootloader discovery, command-line handling, os-release parsing, SELinux labeling, UKI parsing, and boot writing modules. It also defines the boot transformation trait used to prepare filesystem images for bootable composefs workflows.

## Important APIs, types, and functions
`BootOps<ObjectID>` is the key trait. `transform_for_boot(&mut self, repo)` extracts boot entries, empties required top-level directories, compacts the filesystem, applies SELinux labels, and returns extracted `BootEntry` values. `transform_for_boot_from_dir(&mut self, rootfs)` applies the same filesystem mutation using policy files read from an on-disk root directory and does not extract boot entries.

`REQUIRED_TOPLEVEL_TO_EMPTY_DIRS` lists `boot` and `sysroot`. `empty_toplevel_dirs` clears those directories and sets their mtimes to match `/usr`.

## Control flow
The `FileSystem<ObjectID>` implementation for `BootOps` first calls `get_boot_resources` before clearing `/boot`; this preserves boot resources that would otherwise be removed from the transformed root. It then calls `empty_toplevel_dirs`, `compact`, and `selabel::selabel`. The directory-backed variant skips discovery and repository reads, then applies the same empty/compact/relabel sequence using `selabel_from_dir`.

## State and persistence behavior
The trait mutates the in-memory `FileSystem`. It clears the contents of `/boot` and `/sysroot`, copies `/usr` mtime to those now-empty directories, compacts unreachable leaves, and rewrites SELinux xattrs across the tree. It returns extracted boot resources but does not itself commit images or write boot partition files.

## Dependencies and integration points
The module depends on composefs `FileSystem`, `Repository`, and fs-verity traits; `rustix::fd::AsFd` supports the on-disk SELinux path. It integrates with `bootloader::get_boot_resources` and `selabel`. It is used from `composefs-ctl` when creating bootable images from OCI images or on-disk roots.

## Risks
`empty_toplevel_dirs` assumes `/usr`, `/boot`, and `/sysroot` exist and returns errors if required directories are missing. The ordering is important: extracting boot resources after clearing `/boot` would lose them, while labeling before clearing could label content that is intentionally removed. The from-dir variant cannot return boot resources, so callers that need to write a boot partition must use the repository-backed path.

## Test signals
There are no direct tests in this file. Behavior is exercised indirectly by SELinux tests and by CLI bootable paths. Direct integration tests should assert `/boot` and `/sysroot` clearing, mtime propagation from `/usr`, leaf compaction after clearing, and preservation of returned boot entries.

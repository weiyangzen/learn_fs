# sources/cloud-native/fuse-overlayfs/src/sys/mod.rs

## Purpose
`sys/mod.rs` is the module index for the crate's unsafe/syscall boundary.

## Important APIs, Types, And Functions
It publicly exports `dir`, `fs`, `handle`, `io`, `openat2`, `process`, `statx`, and `xattr`.

## Control Flow
There is no runtime control flow. The file defines the module tree consumed by higher-level overlay, datasource, copy-up, and mount code.

## State And Persistence
No state or persistence is defined here.

## Dependencies And Integration Points
All higher-level modules import syscall wrappers through this namespace. The organization supports the crate-level comment in `overlay.rs` that unsafe code lives in `src/sys`.

## Risks
Changing module visibility or names will break imports throughout the crate. Adding unsafe code outside this boundary would weaken the architectural contract.

## Test Signals
No direct tests. Successful compilation and the tests for individual submodules validate the module wiring.

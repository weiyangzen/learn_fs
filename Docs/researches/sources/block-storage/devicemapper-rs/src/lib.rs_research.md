# File Research: sources/block-storage/devicemapper-rs/src/lib.rs

## Purpose
Crate root for the devicemapper Rust library, documenting Linux device-mapper concepts and exposing the public API.

## Module Structure
Loads macros (`bitflags`, `nix`, `log`, range/id/shared macros), private modules for constants/core/cache/linear/result/shared/thin/thinpool/units, and test support under `cfg(test)`.

## Public API
Re-exports cache, core, linear/flakey, result, shared target traits/types, thin device, thin device ID, thin pool, and unit wrappers.

## Documentation
Explains DM lifecycle: create device, load inactive table, resume via suspend ioctl, active/inactive tables, and polling flow for DM minor version 37+.

## Notes
The crate surface is intentionally higher-level than raw ioctls while still exposing `DM` for direct control.

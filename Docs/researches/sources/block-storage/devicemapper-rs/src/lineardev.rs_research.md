# File Research: sources/block-storage/devicemapper-rs/src/lineardev.rs

## Purpose
Implements `dm-linear` and `dm-flakey` target parameter types, multi-line linear target tables, and `LinearDev`.

## Key Types
`LinearTargetParams`, `Direction`, `FlakeyFeatureArg`, `FlakeyTargetParams`, `LinearDevTargetParams`, `LinearDevTargetTable`, and `LinearDev`.

## Behavior
Linear params parse `linear <device> <offset>`. Flakey params parse device, offset, up/down intervals, and optional features: `drop_writes`, `error_writes`, and `corrupt_bio_byte <offset> <r|w> <value> <flags>`. `LinearDev::setup` creates or validates an existing device; equality requires exact table match and segment order. `set_table` loads a new inactive table and updates local state. `set_name` renames via DM and refreshes `DeviceInfo`.

## Tests/Notes
Loopback tests cover empty table failures, rename, duplicate segments, several segments, same-name validation, same-segment different-name creation, suspend/resume, and flakey parsing. Warnings note overlapping segments are not rejected and have undefined behavior.

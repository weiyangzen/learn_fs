# sources/cloud-native/composefs/tools/meson.build

## Purpose
This Meson file defines the composefs command-line tool build targets: `mkcomposefs`, `mount.composefs`, `composefs-info`, `composefs-dump`, and optionally `composefs-fuse`.

## Important APIs, Types, And Functions
It declares `libcomposefs_dep` from the in-tree library and `config_inc`, resolves `thread_dep`, and creates Meson `executable` targets. `composefs-info` also compiles `../libcomposefs/hash.c` with `composefs_hash_cflags`.

## Control Flow
Target creation is declarative. `mkcomposefs` links both public and internal composefs libraries plus threads and is installed. `mount.composefs` installs into `sbindir`. `composefs-info` installs as a user tool. `composefs-dump` and `composefs-fuse` are not installed. The FUSE target is gated by `fuse3_dep.found()`.

## State And Persistence
No runtime state exists. Build state is Meson target metadata and install decisions.

## Dependencies And Integration Points
This file integrates tools with `libcomposefs`, `libcomposefs_internal`, thread support, and optional fuse3. Install paths determine packaging and system mount-helper exposure.

## Risks
Changing `install` flags affects distribution surface. `composefs-fuse` is conditional and non-installed, so tests relying on it must account for missing fuse3. Internal library linkage means ABI changes in internal headers can break tools.

## Test Signals
Build tests should verify all targets with and without fuse3, installed file placement, and link correctness for threaded `mkcomposefs` and hash-backed `composefs-info`.

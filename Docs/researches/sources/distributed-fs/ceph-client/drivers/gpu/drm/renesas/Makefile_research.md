# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Makefile

## Purpose

This top-level Renesas DRM Makefile descends into Renesas display subdirectories and conditionally builds the shmobile driver directory.

## Important APIs, Types, and Functions

- Always includes `rcar-du/` and `rz-du/` through `obj-y`.
- Includes `shmobile/` only when `CONFIG_DRM_SHMOBILE` is enabled.

## Control Flow

Kbuild traverses the listed subdirectories during DRM driver compilation. Individual subdirectory Makefiles decide which objects are emitted based on their Kconfig symbols.

## State and Persistence Behavior

No runtime state. It affects build graph membership.

## Dependencies and Integration Points

Connected to Kbuild and the Kconfig symbols in this directory tree.

## Risks and Edge Cases

Because `rcar-du/` and `rz-du/` are always traversed, their Makefiles must keep object emission fully gated by config symbols.

## Test Signals

Build tests with Renesas options disabled should traverse these directories without producing unwanted modules or built-in objects.

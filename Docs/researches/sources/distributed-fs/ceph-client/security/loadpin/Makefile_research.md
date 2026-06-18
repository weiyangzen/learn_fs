<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Makefile -->
# sources/distributed-fs/ceph-client/security/loadpin/Makefile

## Purpose

The LoadPin Makefile connects `CONFIG_SECURITY_LOADPIN` to the `loadpin.o` object.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SECURITY_LOADPIN) += loadpin.o` includes the LoadPin implementation in the build when the Kconfig option is enabled.

## Control Flow

There is no runtime control flow. Kbuild evaluates the object list based on configuration.

## State and Persistence Behavior

No state is defined here. Runtime state such as pinned superblock and enforcement mode lives in `loadpin.c`.

## Dependencies and Integration Points

This file integrates the LoadPin source with the kernel security Makefile hierarchy.

## Risks and Edge Cases

The risk is build omission or stale object naming if `loadpin.c` is renamed or split. Verity support is conditional inside `loadpin.c`, so no extra object is listed here.

## Test Signals

`CONFIG_SECURITY_LOADPIN=y` should produce `security/loadpin/loadpin.o`; disabled builds should omit it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/Makefile -->

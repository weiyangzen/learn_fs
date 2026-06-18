<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Makefile -->
# sources/distributed-fs/ceph-client/security/lockdown/Makefile

## Purpose

The lockdown Makefile adds the lockdown implementation object when lockdown LSM support is enabled.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SECURITY_LOCKDOWN_LSM) += lockdown.o` connects Kconfig to Kbuild.

## Control Flow

There is no runtime flow. The build system includes or excludes `lockdown.c` based on `CONFIG_SECURITY_LOCKDOWN_LSM`.

## State and Persistence Behavior

No state is defined here. Runtime lockdown level and hooks are in `lockdown.c`.

## Dependencies and Integration Points

This file integrates with the kernel security directory build.

## Risks and Edge Cases

The primary risk is build drift if the implementation file changes name or is split into multiple objects.

## Test Signals

`CONFIG_SECURITY_LOCKDOWN_LSM=y` should build `security/lockdown/lockdown.o`; disabled builds should not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lockdown/Makefile -->

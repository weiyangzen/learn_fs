# sources/distributed-fs/ceph-client/security/landlock/Kconfig

## Purpose

This Kconfig file exposes Landlock LSM support and its KUnit test option. Landlock lets unprivileged processes impose restrictive sandbox policies on themselves and future children.

## Important APIs, Types, and Functions

`SECURITY_LANDLOCK` depends on `SECURITY` and selects `SECURITY_NETWORK` and `SECURITY_PATH`, because Landlock uses network, path, file, credential, and task LSM hooks. `SECURITY_LANDLOCK_KUNIT_TEST` depends on `KUNIT=y` and Landlock and defaults to `KUNIT_ALL_TESTS`.

## Control Flow

When enabled, Kbuild compiles the Landlock object and setup registers it as an LSM. The help text reminds users that Landlock must also appear in `CONFIG_LSM` at boot ordering time.

## State and Persistence Behavior

No runtime state is stored here. Build configuration persists in the kernel image and controls whether syscalls, hooks, and tests exist.

## Dependencies and Integration Points

This integrates with the Linux security framework, path hooks, network hooks, and KUnit. User-visible syscalls are implemented in adjacent Landlock files outside this work item.

## Risks and Test Signals

Configuration mistakes can build Landlock without required hook classes or tests. Build `SECURITY_LANDLOCK=y`, boot with Landlock in `CONFIG_LSM`, run `tools/testing/kunit/kunit.py run --kunitconfig security/landlock`, and run Landlock selftests.

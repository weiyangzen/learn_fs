# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/config

## Purpose
Kernel config fragment for exec selftests needing loop/block-device support.

## Important APIs, Types, And Functions
Sets `CONFIG_BLK_DEV=y` and `CONFIG_BLK_DEV_LOOP=y`.

## Control Flow
Consumed by config tooling, not executable.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Supports tests that create/check block device behavior, especially non-regular/check-exec paths using loop-device major/minor.

## Risks
Other exec tests require additional runtime features not expressed here, such as libcap, namespaces, and securebits support.

## Test Signals
Block-device test paths can create/use loop block device nodes when config and privileges allow.

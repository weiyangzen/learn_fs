# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/Makefile

## Purpose
Build/install metadata for virtio_net selftests. It registers `basic_features.sh` as the test program and `virtio_net_common.sh` plus net helper libraries as installed test files/includes.

## Important APIs, Types, And Functions
Defines `TEST_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, and includes `../../../lib.mk`. No functions are implemented.

## Control Flow
kselftest make infrastructure copies the script and dependencies to the output/install tree and runs `basic_features.sh`.

## State And Persistence
No runtime state. Build state is managed by kselftest output directories.

## Dependencies And Integration Points
Pairs with `config`, which requests BPF, IPv6, VRF, virtio debug, and virtio_net kernel support.

## Risks
If helper include paths change, installed tests can miss runtime libraries. This Makefile assumes the actual tests are shell-only and do not need compilation.

## Test Signals
Successful make/run should expose one test program and common helper file under the kselftest output.

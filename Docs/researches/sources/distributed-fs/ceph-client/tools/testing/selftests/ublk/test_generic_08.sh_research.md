# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_08.sh

## Purpose
This test validates `UBLK_F_AUTO_BUF_REG` with loop and stripe targets.

## Important APIs, Types, and Functions
It checks `_have_feature "AUTO_BUF_REG"`, creates two backing files, adds `-t loop --auto_zc`, then adds `-t stripe --auto_zc`, and runs `_mkfs_mount_test()` on both.

## Control Flow
The script skips without auto-buffer registration support, creates backing files, verifies a loop auto-zc device with a mount test, then verifies a stripe auto-zc device with a mount test.

## State and Persistence
Temporary files and ublk devices are removed by cleanup.

## Dependencies and Integration Points
It depends on kernel auto buffer registration, loop and stripe target auto-zc paths, and mount tooling.

## Risks
Auto-zc depends on buffer indexes from target helpers and kernel registration behavior. Stripe rejects fallback mode, so only normal auto-zc is covered.

## Test Signals
Pass means filesystem operations work on both loop and stripe devices with automatic buffer registration.

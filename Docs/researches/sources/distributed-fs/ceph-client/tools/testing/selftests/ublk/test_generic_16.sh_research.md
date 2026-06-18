# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_16.sh

## Purpose
This test validates `kublk stop --safe`, which should stop idle devices but reject devices with active openers.

## Important APIs, Types, and Functions
It checks `_have_feature "SAFE_STOP_DEV"`, creates null devices, invokes `${UBLK_PROG} stop -n <id> --safe`, opens a device with background `dd`, and deletes devices through `_ublk_del_dev()`.

## Control Flow
First it creates an idle null device and expects `stop --safe` to succeed, then deletes it. Second it creates another null device, starts a background direct read to keep it open, expects `stop --safe` to fail, kills `dd`, and deletes the device.

## State and Persistence
Temporary null ublk devices and a background `dd` process are cleaned up.

## Dependencies and Integration Points
It depends on kernel `UBLK_F_SAFE_STOP_DEV`, `kublk` try-stop command, and block device opener tracking.

## Risks
The busy test uses a short sleep for `dd` startup; slow systems could race if the opener is not established. Cleanup kills the background process best-effort.

## Test Signals
Pass means safe stop succeeds when idle and fails when the block device has an active opener.

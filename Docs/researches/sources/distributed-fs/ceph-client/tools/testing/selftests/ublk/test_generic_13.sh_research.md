# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_13.sh

## Purpose
This test ensures `kublk features` knows every feature bit exposed by the running kernel driver.

## Important APIs, Types, and Functions
It runs `${UBLK_PROG} features` and searches output for `unknown`.

## Control Flow
After standard prep, the script fails if any feature bit is printed as unknown, then cleans up.

## State and Persistence
No ublk device is created. A temporary test directory is created and removed by common setup/cleanup.

## Dependencies and Integration Points
It depends on `cmd_dev_get_features()` in `kublk.c` and its `feat_map`.

## Risks
Running an older selftest suite against a newer kernel with new ublk features will fail intentionally until the feature map is updated.

## Test Signals
Pass means every kernel-advertised ublk feature bit has a symbolic name in `kublk`.

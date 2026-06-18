# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_09.sh

## Purpose
This test covers auto buffer registration fallback on the null target.

## Important APIs, Types, and Functions
It checks `_have_feature "AUTO_BUF_REG"`, requires fio, creates a null device with `-z --auto_zc --auto_zc_fallback`, and runs fio read/write.

## Control Flow
The script adds the fallback-mode null device, runs a 256 MiB fio read/write workload, records exit status, cleans up, and reports.

## State and Persistence
Only a synthetic ublk null device is created and removed.

## Dependencies and Integration Points
It depends on null target invalid buffer-index fallback behavior and kernel `UBLK_IO_RES_NEED_REG_BUF` handling.

## Risks
The test relies on fallback being triggered by intentionally invalid buffer indexes. Fio availability and permissions are required.

## Test Signals
Pass means auto-zc fallback completes fio I/O successfully.

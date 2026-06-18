# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.c

## Purpose
This file implements debugfs reporting for compression CNV errors. It queries firmware for per-AE CNV error counts and latest error codes, decodes error fields, and exposes either a populated `cnv_errors` file or an explanatory no-compression message.

## Important APIs, Types, And Functions
Public functions are `adf_cnv_dbgfs_add()` and `adf_cnv_dbgfs_rm()`. Internal types include `struct ae_cnv_errors` and `struct cnv_err_stats`. Helpers include `get_err_info()`, seq operations `qat_cnv_errors_seq_*()`, `cnv_err_stats_alloc()`, file open/release handlers, and `no_comp_file_read()`.

## Control Flow
When added, if compression service is available, it creates a debugfs file backed by seq operations; otherwise it creates a read-only file saying compression is unavailable. Opening the file allocates stats, iterates service AEs, sends `adf_get_cnv_stats()` admin commands, stores error data, and then seq-show formats AE, count, latest error type, and decoded info. Release frees allocated stats.

## State And Persistence Behavior
Persistent per-device state is only `accel_dev->cnv_dbgfile`. Per-open stats are allocated and freed for each file read. Firmware counters live in firmware and are queried on demand.

## Dependencies And Integration Points
It depends on debugfs, seq_file, admin CNV stats, service/capability checks, and `adf_dbgfs_add()` for non-persistent debugfs entry creation.

## Risks
Admin query failures can make debugfs reads fail. Error decoding is tied to firmware bit layout and sign extension fields. Large or changing AE masks must be reflected in allocation and iteration.

## Test Signals
Reading `cnv_errors` on compression-enabled devices, no-compression text on crypto-only devices, injected CNV errors, admin unsupported status, open/release leak checks, and debugfs remove on device down validate behavior.

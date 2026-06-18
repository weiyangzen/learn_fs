# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.h

## Purpose
This header defines the anti-rollback data contract for QAT SVN enforcement. It provides SVN status constants, retry delay, status mask, command enum, per-generation hardware-data structure, and query/commit/check declarations.

## Important APIs, Types, And Functions
Important definitions are `enum anti_rb`, `struct adf_anti_rb_hw_data`, `GET_ANTI_RB_DATA()`, and APIs `adf_anti_rb_commit()`, `adf_anti_rb_query()`, and `adf_anti_rb_check()`. The hardware-data struct supplies an enablement callback, SVN status CSR offset, retry count, and sysfs state flag.

## Control Flow
No executable flow exists in the header. Implementations and sysfs code use the enum to select SVN query type and the hardware-data struct to read status.

## State And Persistence Behavior
The only state described is per-device volatile anti-rollback metadata inside `struct adf_hw_device_data`.

## Dependencies And Integration Points
It integrates Gen6 hardware data, admin SVN messaging, sysfs anti-rollback files, and PCI probe/init paths that initialize the struct.

## Risks
The status constants are hardware ABI. If status masks or retry timing change, `adf_anti_rb_check()` behavior changes across all users. The `sysfs_added` flag must be maintained consistently by sysfs code.

## Test Signals
Build coverage, anti-rollback sysfs presence on supported devices, correct pass/fail/retry status handling, and admin SVN query/commit tests validate the header.

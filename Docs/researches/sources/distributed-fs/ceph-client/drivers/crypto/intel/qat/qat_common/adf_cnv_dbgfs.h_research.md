# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.h

## Purpose
This header declares CNV compression-error debugfs add/remove hooks.

## Important APIs, Types, And Functions
It forward-declares `struct adf_accel_dev` and declares `adf_cnv_dbgfs_add()` and `adf_cnv_dbgfs_rm()`.

## Control Flow
No executable flow exists. The hooks are called by `adf_dbgfs_add()` and `adf_dbgfs_rm()` for PF devices when debugfs support is compiled.

## State And Persistence Behavior
The header defines no state. Runtime state is `accel_dev->cnv_dbgfile` in the implementation.

## Dependencies And Integration Points
It integrates CNV diagnostics with the broader QAT debugfs lifecycle.

## Risks
Prototype changes affect debugfs orchestration. Calls should only happen when debugfs is enabled and the device is in a suitable state for admin queries.

## Test Signals
Build coverage with `CONFIG_DEBUG_FS`, debugfs file creation/removal, and CNV stats reads validate the header.

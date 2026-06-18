# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.c

## Purpose
This file coordinates QAT debugfs directory and file creation. It separates persistent entries that survive device up/down transitions from non-persistent runtime diagnostics.

## Important APIs, Types, And Functions
Public functions are `adf_dbgfs_init()`, `adf_dbgfs_exit()`, `adf_dbgfs_add()`, and `adf_dbgfs_rm()`. Persistent init creates the device directory and config dump; non-persistent add/remove manages firmware counters, heartbeat, PM, CNV, and telemetry/debug files for PFs.

## Control Flow
`adf_dbgfs_init()` builds a directory name from `qat_`, device class name, and PCI name, creates the directory, and adds `dev_cfg`. `adf_dbgfs_exit()` removes config and directory. `adf_dbgfs_add()` skips VFs and adds runtime PF diagnostics. `adf_dbgfs_rm()` removes runtime diagnostics in reverse-ish dependency order.

## State And Persistence Behavior
Persistent state is `accel_dev->debugfs_dir` and config debugfs dentry. Runtime diagnostic file pointers are stored in feature-specific fields such as `fw_cntr_dbgfile` and `cnv_dbgfile`.

## Dependencies And Integration Points
It depends on Linux debugfs, config debugfs, firmware counters, heartbeat debugfs, PM debugfs, CNV debugfs, and telemetry debugfs.

## Risks
Debugfs calls can return error dentries but are generally non-fatal. Runtime diagnostics are PF-only; accidentally enabling on VFs can call unsupported admin paths. Removal order must tolerate partially created files.

## Test Signals
Debugfs tree creation/removal, `dev_cfg`, firmware counters, heartbeat, PM, CNV, TL files on PFs, absence on VFs, device up/down cycles, and debugfs-disabled build stubs.

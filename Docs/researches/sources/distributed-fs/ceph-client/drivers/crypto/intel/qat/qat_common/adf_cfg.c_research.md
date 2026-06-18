# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.c

## Purpose
This file implements the per-device QAT configuration database. It stores named sections and key/value pairs in kernel lists, exposes them through debugfs `dev_cfg`, and provides add/get/delete helpers for PCI probe defaults and user ioctl configuration.

## Important APIs, Types, And Functions
Public APIs are `adf_cfg_dev_add()`, `adf_cfg_dev_remove()`, `adf_cfg_dev_dbgfs_add()`, `adf_cfg_dev_dbgfs_rm()`, `adf_cfg_del_all()`, `adf_cfg_del_all_except()`, `adf_cfg_section_add()`, `adf_cfg_add_key_value_param()`, and `adf_cfg_get_param_value()`. Debugfs iteration uses `qat_dev_cfg_*()` seq operations.

## Control Flow
Device add allocates `adf_cfg_device_data`, initializes section list and lock. Section add creates or reuses a section. Key add formats decimal/string/hex values, then under the config write lock replaces an existing key if value differs or discards duplicate values. Get uses the read lock. Delete paths walk lists backwards and free section/key nodes. Debugfs seq operations lock a global read mutex while iterating the section list.

## State And Persistence Behavior
Config state is volatile in `accel_dev->cfg` and persists for the device lifetime or until reconfiguration/deletion. It stores strings, not parsed typed values. It does not persist to disk.

## Dependencies And Integration Points
It depends on Linux list/seq/debugfs/rwsem, QAT config strings/common definitions, and common driver status bits. It is used by PCI probes, control ioctl, Gen4/Gen6 service parsing, heartbeat config, and debugfs.

## Risks
Config stores fixed 64-byte strings, so truncation/length constraints matter. `ADF_HEX` treats `val` as an integer encoded through a pointer-shaped argument. Updates delete then append, changing list order. The debugfs reader uses a global mutex separate from per-device rwsem.

## Test Signals
Add/get/update/delete unit coverage, ioctl configuration, debugfs `dev_cfg` output, duplicate key behavior, invalid type rejection, config clearing on stop/reconfigure, and service parsing from stored values.

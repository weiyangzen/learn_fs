# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.h

## Purpose

`hns3_debugfs.h` defines the small set of structures used by `hns3_debugfs.c` to describe debugfs files, per-file private data, directory categories, command mappings, and capability display mappings.

## Important APIs and Types

- `HNS3_DBG_ITEM_NAME_LEN` and `HNS3_DBG_FILE_NAME_LEN` bound display item and generated file names.
- `struct hns3_dbg_item` stores a display name plus spacing interval for table-like debug output.
- `struct hns3_dbg_data` carries the handle, debug command, and queue id for per-queue BD files.
- `enum hns3_dbg_dentry_type` indexes debugfs directory categories.
- `struct hns3_dbg_dentry_info` stores a directory name and dentry pointer.
- `struct hns3_dbg_cmd_info` maps a debugfs file name to an HNAE3 debug command, directory, and initializer.
- `struct hns3_dbg_cap_info` maps display strings to capability bit numbers.

## Control Flow and Integration

The header provides data shapes only. `hns3_debugfs.c` fills arrays of these structures and uses them to create debugfs directories/files and route seq-file reads to local or backend-provided functions. `struct hns3_dbg_data` becomes seq private data for descriptor dump files.

## State and Persistence Behavior

Instances of these structures persist in static arrays or device-managed allocations in the implementation. Dentry pointers are valid only while debugfs entries exist. Per-file `hns3_dbg_data` persists for the PCI device lifetime because allocation is device-managed.

## Dependencies

The header includes `hnae3.h` for `struct hnae3_handle`, debug command enums, and capability bit enum values. It relies on Linux debugfs `struct dentry` declarations available through included kernel headers in consumers.

## Risks and Edge Cases

- Name length constants are small; generated queue file names must fit.
- Directory enum order must match the static dentry array in the implementation.
- Capability bit enum values must stay synchronized with `hnae3.h`.
- Per-file private data contains raw handle pointers, so debugfs teardown must happen before the handle becomes invalid.

## Test Signals

Compile coverage, debugfs file creation with long queue indices, directory mapping correctness, per-queue BD reads using the intended queue id, and teardown without stale private data are the key validation signals.

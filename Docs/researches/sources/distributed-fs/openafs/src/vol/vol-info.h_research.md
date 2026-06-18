# sources/distributed-fs/openafs/src/vol/vol-info.h

## Purpose

`vol-info.h` declares options, filters, output columns, and public helper APIs for OpenAFS volume inspection utilities implemented by `vol-info.c`.

## Important Types, Flags, and APIs

Scan-volume flags are `SCAN_RW`, `SCAN_RO`, and `SCAN_BK`. Vnode find flags are `FIND_FILE`, `FIND_DIR`, `FIND_MOUNT`, `FIND_SYMLINK`, and `FIND_ACL`.

`struct VolInfoOpt` is the caller-configurable scan state. It controls FSSYNC checkout, header/info/vnode dumping, inode numbers and times, file names, orphan reporting, size summaries, inode saving, header repair, hostname, column delimiter, headings, directory magic checks, mode masks, volume type filters, and vnode type filters.

`VOLSCAN_COLUMNS` is the canonical list of structured output columns. It is reused by `vol-info.c` to generate the column enum and name table, keeping CLI column names synchronized with switch handling.

Public APIs initialize the module/options, add vnode handlers, add output columns, scan partitions, and provide standard vnode handlers for size totals, saving inodes, raw/detail printing, and ACL scanning.

## Control Flow and Integration

A typical utility calls `volinfo_Init`, obtains defaults with `volinfo_Options`, modifies fields based on CLI options, registers output columns/handlers, and calls `volinfo_ScanPartitions`. `struct VnodeDetails` is forward-declared so callers can register callbacks without depending on its layout.

## State and Persistence Behavior

This header does not define persistence, but its options can enable persistent side effects in the implementation: `fixHeader` can rewrite bad special inode headers and `saveInodes` can create local copies of inode contents. All other flags primarily affect reads and output formatting.

## Risks and Test Signals

API risks include uninitialized option fields, unsupported column names, mode mask array overflow in callers, and handlers assuming `VnodeDetails` internals. Tests should verify default options, every `VOLSCAN_COLUMNS` value can be registered and printed, scan type filters combine correctly, find flags select expected handlers, and callback registration stays per vnode class.

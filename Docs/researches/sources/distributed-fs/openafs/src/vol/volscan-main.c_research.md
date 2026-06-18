# sources/distributed-fs/openafs/src/vol/volscan-main.c

## Purpose
Implements the `volscan` command-line entrypoint for machine-readable scans of volume vnode information using the shared `vol-info` backend.

## Important APIs, Types, and Functions
`ColumnNames` is generated from `VOLSCAN_COLUMNS` for command help. `VolScan` initializes `volinfo`, sets `VolInfoOpt` into volscan mode (`dumpInfo = 0`), parses filters and output settings, registers detail/ACL handlers, and invokes `volinfo_ScanPartitions`.

Supported parameters include `-checkout`, `-partition`, `-volumeid`, `-type`, `-find`, `-mask`, `-output`, `-delim`, `-noheading`, and `-ignore-magic`.

## Control Flow
`main` defines the cmd syntax and dispatches. `VolScan` parses partition and volume id, rejects zero volume ids, enables or disables headings, optionally disables directory magic checks, copies a delimiter with a 15-byte cap, and computes scan filters. With no `-type`, it scans RW, RO, and BK volumes; explicit values must be `rw`, `ro`, or `bk`. With no `-find`, it finds files, directories, mounts, and symlinks; explicit values may also include `acl`. Mode masks are parsed as octal and bounded by the option array. Output defaults to `host`, `desc`, `fid`, `dv`, optional ACL columns, and `path`; explicit columns are validated by `volinfo_AddOutputColumn`. Vnode handlers are registered for large vnodes, small vnodes, and ACL scanning according to the find mask.

## State and Persistence Behavior
The scanner is intended to be read-only, except that `-checkout` interacts with the running fileserver to safely inspect checked-out volumes. Output formatting state lives in `VolInfoOpt`, including delimiter, heading, filters, masks, and selected columns.

## Dependencies and Integration Points
Uses OpenAFS cmd parsing, rx queues, locks, ihandle/vnode definitions, and `vol-info.h` scanning/printing functions. It shares the same scanner backend as `volinfo-main.c`, making CLI behavior a thin configuration layer around reusable volume traversal logic.

## Risks
`strncpy` caps delimiters but silently truncates long delimiters. `strtoul`/`strtol` validation is minimal and treats zero masks as invalid, so users cannot search for mask `0000`. Unknown filter or column values fail early. `-ignore-magic` can trade path-lookup validation for resilience when directories are corrupt, so tests should cover both modes.

## Test Signals
CLI tests should cover default columns, ACL columns when `-find acl` is used, invalid `-type`, invalid `-find`, too many masks, invalid masks, unknown output columns, delimiter truncation, heading suppression, and partition/volume-specific scans.

## Source Notes
Read as C command entrypoint; 255 source lines; source-tree-aligned report generated for subset `subset-b-007819`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/lops.h

## Purpose
`lops.h` defines the dispatch interface for GFS2 log operation implementations and declares low-level journal write, pinning, journal-head discovery, and revoke-drain helpers.

## Important APIs, types, and functions
The main exported object is `extern const struct gfs2_log_operations *gfs2_log_ops[]`. Helper prototypes expose `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_write`, `gfs2_log_submit_write`, `gfs2_pin`, `gfs2_find_jhead`, and `gfs2_drain_revokes`. `buf_limit` and `databuf_limit` compute per-descriptor payload capacities from `sd_ldptrs`. Inline dispatchers are `lops_before_commit`, `lops_after_commit`, `lops_before_scan`, `lops_scan_elements`, and `lops_after_scan`.

## Control Flow
`log.c` calls the before/after commit dispatchers during a flush; each walks `gfs2_log_ops[]` and invokes implemented hooks. `recovery.c` calls the scan dispatchers around each replay pass and for each descriptor. `lops_scan_elements` stops on the first hook error. `lops_after_scan` is intended to call each `lo_after_scan` hook when scanning completes.

## State and Persistence
No state is declared in the header. It defines how operations act on transaction lists, journal descriptors, and replay state owned by `gfs2_sbd` and `gfs2_jdesc`. The limits encode persistent descriptor layout capacity.

## Dependencies and Integration Points
Includes `incore.h` for `struct gfs2_sbd`, `struct gfs2_jdesc`, and `struct gfs2_log_operations`. It is consumed by `log.c`, `lops.c`, and `recovery.c`, binding commit-time and recovery-time behavior together.

## Risks
The hook order is part of the journal format behavior: data, metadata, and revokes must remain coherent with recovery passes. `databuf_limit` halves descriptor capacity because each data buffer needs block number plus escape flag. The `lops_after_scan` inline checks `lo_before_scan` before calling `lo_after_scan`, which means a future operation that only has `lo_after_scan` would be skipped unless this condition changes.

## Test Signals
Build-time coverage of all hook users, recovery with all descriptor types, transactions that hit descriptor limits, and tests adding any new log operation without a complete hook set are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.h -->

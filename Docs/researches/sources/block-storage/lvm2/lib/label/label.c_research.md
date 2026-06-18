# File Research: sources/block-storage/lvm2/lib/label/label.c

## Purpose
Implements LVM2 label discovery, label writes/removal, scan-time bcache management, selected online/hints-based scan optimizations, and the public raw device byte I/O wrappers used by other LVM modules. It is the central bridge between block devices, format-specific labellers, `lvmcache`, filters, and the bcache-backed I/O layer.

## Main Responsibilities
- Maintains the registered labeller list and dispatches format-specific `can_handle`, `read`, `write`, label initialization, and destruction operations.
- Creates and owns the process-wide `scan_bcache`, sized from `io_memory_size`, using async I/O when configured and falling back to sync I/O.
- Opens devices for scans through validated dev-cache aliases, using `O_DIRECT`, `O_NOATIME`, read-only/read-write/exclusive modes, and bcache device indexes.
- Scans device headers, validates `LABELONE` headers, sector numbers, CRCs, and labeller compatibility, then calls labeller `read` to populate `lvmcache`.
- Runs normal full label scans, cached scans, read-write scans, exclusive scans, single-device rescans, and optimized `/run/lvm/pvs_online` VG scans.
- Uses hints and device ID validation to reduce unnecessary scans while falling back to complete scans if hints are stale.
- Provides `label_read_pvid` for quick PVID reads and `label_scan_for_pvid` for locating a PVID across filtered devices.
- Provides `dev_read_bytes`, `dev_write_bytes`, `dev_write_zeros`, `dev_set_bytes`, invalidation helpers, and last-byte helpers as bcache wrappers for metadata and signature I/O.

## Important Control Flow
`label_scan` sets up bcache, refreshes the DM UUID cache, builds an all-device list, applies nodata filters first, uses hints if possible, prepares the open-file limit, and calls `_scan_list`. After scan completion it warns if discovered metadata approaches bcache size, validates hints and devices-file entries, performs extra MD-component checks, and writes new hints when appropriate.

`_scan_list` batches bcache prefetches based on available cache blocks, opens devices as needed, reads the first bcache block, copies the first 4 KiB into a local header buffer, releases the bcache block, and calls `_process_block`. Non-LVM devices are invalidated and closed unless the caller explicitly wants to retain non-LVM devices for creation workflows.

`_process_block` reruns data-dependent filters after the header block is available, clears stale cache state for filtered or now-unlabelled devices, finds the label with `_find_lvm_header`, and invokes the format labeller. Duplicate PVIDs are treated differently from metadata summary failures: duplicate devices are logged without adding normal cache info, while metadata failures can still leave usable PV information in `lvmcache`.

`label_scan_vg_online` uses `/run/lvm` online PV files from `pvscan --cache` as startup hints. It maps dev_t values into dev-cache devices, temporarily relaxes device-id filtering for unstable devnames, reads PVIDs first, applies filters, scans the remaining devices, and falls back by reporting incomplete results when metadata says more PVs are required.

Write paths ensure bcache is writable or reopen devices read-write before writing. `dev_set_last_byte` chooses a 512-byte or 4096-byte boundary from direct block sizes so bcache writes respect the device's physical/logical block size.

## Dependencies
Depends on labeller implementations, `lvmcache`, device filters, dev-cache alias validation, bcache, command context configuration, DM UUID cache, hints, device ID matching, online PV files, activation helpers for LV-backed PV invalidation, and format text layout structures for PV headers.

## Risk Notes
- `scan_bcache` is global state; setup, invalidation, and destroy ordering affects all later metadata reads and writes in the process.
- `_scan_dev_open` mutates alias lists on failed opens and verifies major/minor after opening, so error handling must preserve dev-cache consistency.
- Header scanning intentionally scans only the first `LABEL_SCAN_SECTORS` sectors and treats extra labels as suspicious.
- The nodata filter and data-dependent filter split is subtle; stale persistent filter results must be wiped before full filtering.
- Hints and online PV optimizations are performance shortcuts, not authority. Their fallback behavior protects correctness.
- `dev_write_bytes` and `dev_set_bytes` flush bcache immediately and invalidate on failure; callers rely on this for metadata consistency.

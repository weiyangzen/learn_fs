<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.c

Purpose: Probes and stores LPAR hypervisor DIAG 204 data and exposes raw extended DIAG 204 snapshots through debugfs.

Important APIs/types/functions: Maintains `diag204_store_sc`, `diag204_info_type`, `diag204_buf`, and `diag204_buf_pages`. Public functions are `diag204_get_info_type()`, `diag204_get_buffer()`, `diag204_store()`, `hypfs_diag_init()`, and `hypfs_diag_exit()`. It defines packed debugfs header structs `dbfs_d204_hdr` and `dbfs_d204`.

Control flow: `diag204_probe()` first attempts extended DIAG 204 data with subcode 7, then subcode 6, and falls back to simple subcode 4. Extended mode uses DIAG 204 RSI to size the buffer, then vmallocs a page-aligned area. `diag204_store()` builds the selected subcode, adds BIF when available, and retries on `-EBUSY` unless a signal is pending. Debugfs creation allocates an aligned buffer with a 64-byte header and stores the raw DIAG 204 payload behind it.

State and persistence: Selected DIAG format/subcode and the reusable vmalloc buffer persist for all hypfs diag consumers. The debugfs raw snapshot is generated per read and freed afterward.

Dependencies and integration points: Integrates with `hypfs_diag_fs.c` for mounted filesystem formatting, `hypfs_dbfs.c` for raw debugfs exposure, DIAG 204/224 definitions, vmalloc, scheduling, signal handling, and EBCDIC conversion in consumers.

Risks: The buffer-size path trusts DIAG 204 RSI page counts. Busy retry can be interrupted by signals. Extended-only debugfs file creation means simple-mode machines still rely on filesystem formatting rather than raw debugfs.

Test signals: LPAR systems supporting DIAG 204 subcodes 7, 6, and 4; busy-retry behavior; raw diag_204 debugfs format validation; and mounted hypfs tree creation.

Source read size: 224 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.c -->

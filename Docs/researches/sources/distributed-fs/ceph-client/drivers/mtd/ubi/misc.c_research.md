# sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c

Purpose: this file collects small UBI-wide helpers for data-length trimming, static-volume verification, bad-eraseblock reserve accounting, byte-pattern checking, and standardized UBI log messages.

Important APIs, types, and functions: `ubi_calc_data_len()` trims trailing `0xFF` data and aligns the result to `ubi->min_io_size`. `ubi_check_volume()` fully reads a static volume through `ubi_eba_read_leb()` to verify per-LEB CRCs. `ubi_update_reserved()` and `ubi_calculate_reserved()` manage bad-eraseblock reserve targets. `ubi_check_pattern()` tests a buffer for one byte value. `ubi_msg()`, `ubi_warn()`, and `ubi_err()` format per-device kernel messages and include caller information for warnings/errors.

Control flow: data trimming scans backward to the last non-`0xFF` byte and rounds up. Static volume checking allocates one usable-LEB buffer, loops across `used_ebs`, uses `last_eb_bytes` for the final LEB, reads with CRC checking enabled, returns `1` for ECC/data corruption, and propagates negative errors. Reserve calculation derives the required reserve level from the configured bad PEB limit minus current bad count; reserve update moves available PEBs into reserved accounting under the caller's `volumes_lock`.

State and persistence behavior: reserve helpers update in-memory `ubi_device` accounting (`avail_pebs`, `rsvd_pebs`, `beb_rsvd_pebs`, `beb_rsvd_level`) but do not write flash directly. Static volume checking can cause callers to mark `vol->corrupted`, but the helper itself only reads. Logging has no persistence beyond kernel logs.

Dependencies and integration points: these helpers are used from API open paths, volume update/write code, wear-leveling bad-block handling, and IO/debug checks. They depend on EBA reads, vmalloc/vfree, MTD ECC classification helpers, alignment fields from `struct ubi_device`, and kernel printk formatting.

Risks: `ubi_calc_data_len()` assumes input length is min-I/O aligned. Static-volume checking can be slow for large volumes and allocates a full usable LEB. Reserve updates depend on callers holding `volumes_lock`; missing that lock would corrupt global accounting. Returning positive `1` for corruption is a special convention callers must not treat as success.

Test signals: check trimming of all-FF, partially written, and aligned buffers; static-volume CRC success and ECC failure handling; reserve accounting after new bad PEBs, over-limit bad PEB counts, and no available PEBs; and expected log prefixes for normal, warning, and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c -->

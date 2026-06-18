# sources/distributed-fs/ceph-client/fs/ubifs/scan.c

## Purpose
`scan.c` implements the generic UBIFS logical eraseblock scanner. It converts raw bytes from one LEB into a `struct ubifs_scan_leb` containing ordered `struct ubifs_scan_node` descriptors for valid nodes, while distinguishing valid padding, erased space, garbage, corrupt nodes, and corrupt empty space. Replay, recovery, garbage collection, LPT checks, master reading, orphan handling, authentication, debugging, and TNC in-the-gaps commit all depend on this scanner.

## Important APIs, Types, And Functions
`ubifs_scan_a_node()` classifies one candidate buffer position using common-header magic, node validation, padding-node validation, and raw padding-byte detection. Return values are the `SCANNED_*` enum values from `ubifs.h`, with positive values meaning padding bytes to skip. `ubifs_start_scan()` allocates and initializes `struct ubifs_scan_leb`, reads the LEB tail into the caller-provided scan buffer, and tolerates `-EBADMSG` because node CRCs are checked individually.

`ubifs_add_snod()` appends a `struct ubifs_scan_node` with sequence number, type, offset, length, raw node pointer, and key for keyed nodes. `ubifs_scan()` is the main scanner: it loops over nodes/padding, stops at erased space, enforces min-I/O alignment for the empty-space boundary, verifies that the remainder is all `0xff`, and returns either a scan list or `ERR_PTR(-EUCLEAN)` for recoverable corruption. `ubifs_scan_destroy()` frees only scan descriptors and the `sleb`; the raw buffer remains caller-owned.

## Control Flow
The scanner reads the target LEB once, then advances by either padding length or aligned node length. Valid node headers become scan nodes. Empty space stops node scanning and triggers strict tail verification. Garbage, corrupt nodes, and bad padding go through the corruption path, optionally dumping the first bytes of the corrupt region via `ubifs_scanned_corruption()`. Non-quiet callers get detailed diagnostics; quiet callers can probe during recovery without noisy logs.

## State And Persistence
The scanner does not mutate flash. It builds transient metadata over a caller-owned LEB-sized buffer. Each `snod->node` points into that buffer, so callers must consume or copy data before reusing/freeing the scan buffer. The `endpt` field records the min-I/O-aligned endpoint of valid content and is used by recovery and replay to decide where writes or cleanup can resume.

## Dependencies And Integration Points
Core dependencies are `ubifs_leb_read()`, `ubifs_check_node()`, key parsing helpers, UBIFS node layout definitions, kernel lists, and debug dump helpers. Callers include `replay.c`, `recovery.c`, `gc.c`, `log.c`, `master.c`, `orphan.c`, `auth.c`, `lprops.c`, `debug.c`, and `tnc_commit.c`. The scanner is therefore a shared correctness boundary between raw flash contents and higher-level recovery, commit, and GC decisions.

## Risks And Edge Cases
Padding handling is subtle: raw padding bytes must be non-zero and 8-byte aligned, while padding nodes must not run past LEB end and must align the combined node-plus-padding length. The empty-space start must align to `min_io_size`; otherwise the LEB is considered corrupt. `-EBADMSG` during the initial read is intentionally tolerated, but CRC/hash validation later must catch damaged nodes. Because scan nodes point into `sbuf`, stale pointers are possible if callers keep them after buffer reuse.

## Test Signals
Tests should cover valid mixed-node LEBs, raw padding bytes, padding nodes, empty LEBs, corrupt magic, bad CRC/hash, bad pad lengths, empty space starting at non-min-I/O offsets, non-`0xff` bytes in the tail, quiet versus non-quiet diagnostics, and callers that sort or replay scan lists. Recovery tests should confirm `-EUCLEAN` is produced for corruption that can be handled by recovery code.

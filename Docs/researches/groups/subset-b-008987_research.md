# Research: subset-b-008987 WiredTiger log subsystem

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log.c -->
# sources/storage-engines/wiredtiger/src/log/log.c

## Purpose
`log.c` is the physical transaction-log implementation for WiredTiger. It creates, opens, verifies, writes, scans, truncates, salvages, syncs, and removes numbered `WiredTigerLog.NNNNNNNNNN` files. It sits below transaction logging (`src/txn/txn_log.c`) and log manager lifecycle (`log_mgr.c`), and above the filesystem, compression, encryption, checksum, capacity throttling, and recovery subsystems.

The file turns caller-built `WT_LOG_RECORD` buffers into durable on-disk records with aligned padding, little-endian headers, checksums, optional compression/encryption, and LSN allocation through group-commit slots. It also implements the defensive scanner used by recovery, log cursors, printlog, and recovery probes.

## Important APIs and Functions
- `__wt_log_printf` / `__wt_log_vprintf`: build `WT_LOGREC_MESSAGE` records for internal diagnostic/system messages and write them through normal logging.
- `__wt_log_write`: public write entry point. Applies optional log compression and connection-level encryption, then delegates to `__log_write_internal`.
- `__log_write_internal`: fills the log record header, rounds to `WTI_LOG_ALIGN`, computes checksum, joins a `WTI_LOGSLOT`, writes/copies data, releases the slot, and waits for `WT_LOG_FLUSH` or `WT_LOG_FSYNC` guarantees when requested.
- `__wt_log_scan`: reads log files record by record, verifies headers and checksums, handles compression/encryption, detects holes/partial writes, invokes a caller callback, and truncates during recovery/salvage.
- `__wt_log_flush`, `__wt_log_flush_lsn`, `__wt_log_force_sync`: force buffered records out to OS or disk and return/advance write and sync LSNs.
- `__wt_log_get_backup_files`: computes log files needed for backup from allocation and checkpoint LSNs, forces a file switch, and filters directory listings.
- `__wt_log_needs_recovery`: opens a log cursor at checkpoint LSN and decides whether commit records exist after the checkpoint.
- `__wti_log_open`, `__wti_log_close`: open current/new log files at connection startup and close file handles at shutdown.
- `__wti_log_acquire`, `__wti_log_release`, `__wti_log_force_write`, `__wti_log_fill`: slot allocation/write/release primitives used by group commit and manager threads.
- `__wti_log_allocfile`, `__wti_log_remove`, `__wt_log_filename`, `__wti_log_extract_lognum`: file naming and filesystem operations for real, temporary, and preallocated log files.
- `__wti_log_set_version`, `__wt_log_compat_verify`: enforce compatibility-version log formats.

## Control Flow
Write path:
1. Caller passes a prebuilt `WT_LOG_RECORD` in a `WT_ITEM` to `__wt_log_write`.
2. The record may be compressed if the configured compressor produces a smaller aligned record, then encrypted if a keyed encryptor exists.
3. `__log_write_internal` pads to `WTI_LOG_ALIGN`, writes `len/checksum/flags/mem_len`, and computes the checksum over little-endian header bytes.
4. The writer joins the active slot with `__wti_log_slot_join`. Oversized, forced, or boundary-crossing records trigger `__wti_log_slot_switch`.
5. `__wti_log_fill` copies to the slot buffer or writes directly for forced/unbuffered records.
6. `__wti_log_slot_release` accounts for copied bytes. If the slot is done, `__wti_log_release` writes buffered bytes and either hands the slot to the write-LSN server or synchronously advances `write_lsn`/`sync_lsn`.

Read/recovery path:
1. `__wt_log_scan` derives `start_lsn` and `end_lsn` from explicit input, `WT_LOGSCAN_FIRST`, `WT_LOGSCAN_FROM_CKP`, or existing files when logging is disabled.
2. It opens/verifies the starting file with `__log_open_verify`, including descriptor magic/version and optional previous-LSN system record.
3. It reads at least one alignment unit, expands to the rounded record length, checks for zero-filled preallocation, holes, oversize lengths, checksum mismatches, partial writes, and backup-specific artifacts.
4. Valid records are byte-swapped, decrypted, decompressed, and passed to the callback unless they are file headers.
5. Recovery scans truncate at the discovered end and may salvage by truncating damaged logs when `WT_CONN_SALVAGE` is set.

File rollover path:
1. `__wti_log_acquire` checks whether the next allocation fits the current file or a forced new file flag is set.
2. `__log_newfile` waits for any prior file handle pending close, publishes `log_close_lsn/log_close_fh`, increments `fileid`, uses a preallocated file if available and safe, otherwise allocates a temporary file and renames it.
3. The new file receives a descriptor header and, for modern log versions, a system record containing the previous LSN.

## State and Persistence Behavior
- Persistent files are numbered log files under `log_mgr.log_path`, using `WT_LOG_FILENAME`, plus temporary/preallocated files using `WTI_LOG_TMPNAME` and `WTI_LOG_PREPNAME`.
- Each file begins with a fixed aligned descriptor containing magic, log version, and configured max file size.
- For `WTI_LOG_VERSION_SYSTEM` and later, the first real record stores the previous LSN so recovery can detect holes across file boundaries.
- `alloc_lsn` reserves future byte ranges, `write_lsn` tracks records written to the OS, `write_start_lsn` tracks the start of the last written record, `sync_lsn` tracks fsynced durability, `sync_dir_lsn` tracks parent-directory durability, and `trunc_lsn` records recovery truncation bounds.
- Log files are preallocated/zero-filled, so scanner logic treats zeroed ranges as EOF only after proving no later non-zero data exists.
- Truncation prefers filesystem truncate but falls back to zero-filling when truncate is unsupported or unsafe during backup.
- Compression and encryption flags are persisted in `WT_LOG_RECORD.flags`; `mem_len` persists uncompressed size for compressed/encrypted payload handling.

## Dependencies and Integration Points
- Uses `log_private.h` slot state, file prefixes, and private prototypes; uses public declarations and LSN macros from `log.h`.
- Consumed by transaction commit/checkpoint code (`__wti_txn_log_commit`, `__wt_checkpoint_log`) and log cursor/printlog paths.
- Coordinates with `log_mgr.c` background threads via `log_mgr.file.cond`, `log_mgr.server.cond`, and `log_mgr.wrlsn.cond`.
- Depends on filesystem wrappers (`__wt_open`, `__wt_write`, `__wt_read`, `__wt_fsync`, `__wt_ftruncate`, `__wt_fs_rename/remove/directory_list`), WiredTiger buffers/scratch allocation, checksums, endian helpers, capacity throttling, compressors, encryptors, hot backup locks, checkpoint signaling, and connection flags.

## Risks and Edge Cases
- Slot state ordering is concurrency-critical. Incorrect barriers around `slot_state`, `log_close_fh`, or LSN updates can produce holes, stuck waits, premature file close, or false durability.
- Scanner corruption rules are intentionally subtle: zero-fill, backup copies, partial writes, and bad checksums have different recovery consequences.
- File-size and preallocation behavior can create logs larger than `file_max` in edge races; code attempts to minimize but not entirely eliminate that.
- Version/downgrade handling must avoid writing newer-format files before compatibility verification completes.
- Compression/encryption require matching configuration during recovery; missing codecs fail recovery with explicit guidance.
- `__log_write_internal` currently asserts `ret == 0` after slot-fill errors, so any future changes to write-error propagation need care.
- Directory fsync and file fsync are separated; losing a directory entry after rename is mitigated only when `sync_dir_lsn` is advanced.

## Test Signals
- Crash-recovery tests should cover partial writes, checksum mismatch, zero-filled preallocation, hole detection, and salvage.
- Backup tests should cover hot backup cursor interactions, backup file filtering, no rename/truncate while backup is active, and backup-copy checksum anomalies.
- Compatibility tests should cover log versions 1-5, downgrade forced checkpoint/removal, and unsupported future versions.
- Sync tests should verify `WT_LOG_FLUSH`, `WT_LOG_FSYNC`, `transaction_sync` modes, directory fsync on file rollover, and no hangs waiting for inactive new files.
- Compression/encryption tests should verify records can be scanned only with matching configuration and that small/unhelpful compression falls back cleanly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log.h -->
# sources/storage-engines/wiredtiger/src/log/log.h

## Purpose
`log.h` is the public/internal logging interface header shared across WiredTiger. It defines log scan/write/sync flags, the `WT_LSN` representation, on-disk `WT_LOG_RECORD` header layout, log format version gates, log manager state, printlog arguments, thread wrappers, and prototypes for the log subsystem and generated log operation codecs.

## Important APIs, Types, and Constants
- `WT_LSN`: 64-bit atomic union of `(file, offset)` used as the transaction log position. Macros such as `WT_ASSIGN_LSN`, `WT_SET_LSN`, `WT_INIT_LSN`, `WT_ZERO_LSN`, `WT_IS_INIT_LSN`, `WT_IS_ZERO_LSN`, and `WT_IS_MAX_LSN` centralize atomic updates and comparisons.
- `WT_LOG_RECORD`: on-disk record header with `len`, `checksum`, `flags`, zero padding, `mem_len`, and flexible payload. Flags currently persist compression and encryption.
- `WT_LOG_FILENAME`: base prefix for real log files.
- `WT_LOG_FILE_MIN/MAX`: configured size bounds.
- `WT_LOGSCAN_*`: scan behavior flags for first record, checkpoint start, one-record lookup, recovery, and metadata recovery.
- `WT_LOG_*`: transaction sync/write flags for dsync, flush, fsync, and sync-enabled mode.
- `WT_LOG_V*_VERSION`: WiredTiger release thresholds that map compatibility versions to log file versions.
- `WT_TXN_PRINTLOG_ARGS`: carries printlog output stream and flags for hex, messages-only, and unredacted output.
- `WT_LOG_THREAD`: condition/session/thread bookkeeping for log manager threads.
- `WT_LOG_MANAGER`: connection-global logging configuration and runtime state, including compressor, file sizes, path, txn sync mode, cursor count, preallocation counts, compatibility requirements, thread handles, and global log flags.
- Prototypes expose log cursor open, scan, write, flush, backup file collection, truncation, reset, manager config/create/open/destroy, generated log operation pack/unpack/print helpers, and inline LSN helpers.

## Control Flow Role
This header does not implement control flow, but it defines the contracts used by all log control paths:
- Writers and recovery code pass `WT_LSN` pointers through `log.c`, `txn_log.c`, and cursor code.
- `WT_LOG_RECORD` layout is assumed by generated operation packing (`log_auto.c`), physical write/read (`log.c`), and transaction printlog.
- `WT_LOG_MANAGER.flags` determines whether logging is configured, enabled, removable, recovering dirty, downgraded, failed, or zero-filled.
- Scan flags gate `__wt_log_scan` behavior and determine how invalid LSNs are reported.

## State and Persistence Behavior
- `WT_LSN` is intentionally atomically assigned as a 64-bit `file_offset` because compilers/sanitizers may not perform safe atomic struct assignment.
- `WT_LOG_RECORD` flags are explicitly not auto-generated because they are written to disk and cannot change meaning.
- The unused padding in `WT_LOG_RECORD` is expected to be zero and is checked for corruption by `log.c`.
- Version constants preserve compatibility with historic log formats and determine first-record layout and system-record availability.

## Dependencies and Integration Points
- Included by core WiredTiger internals through `wt_internal.h` and by log implementation files.
- Tied to generated prototypes from `prototypes.py`; changes require regeneration.
- Uses WiredTiger atomics, version structures, stream types, sessions, cursors, compressors, condition variables, rwlocks, and thread abstractions.
- Generated log operation functions declared here are implemented in `log_auto.c` and consumed by transaction logging, recovery, cursors, and printlog.

## Risks and Edge Cases
- On-disk constants (`WT_LOG_RECORD_*`, log version mapping, file naming) are compatibility-sensitive.
- Endianness of `WT_LSN` fields is handled through union layout and atomic loads; direct non-macro updates can break portability or TSAN assumptions.
- `WT_IS_MAX_LSN` intentionally accepts both `INT32_MAX` and `UINT32_MAX` offsets for older releases.
- `WT_LOG_MANAGER` mixes configuration, persistent-version policy, thread state, and counters, so initialization/destruction ordering is important.

## Test Signals
- ABI/on-disk format tests should detect accidental changes to `WT_LOG_RECORD` layout and flag values.
- Compatibility tests should validate `WT_LOG_V*_VERSION` mappings and startup bounds.
- Thread/concurrency tests should exercise atomic LSN assignment under log write and scan load.
- Printlog and cursor tests implicitly verify key/value formats `WTI_LOGC_KEY_FORMAT` and `WTI_LOGC_VALUE_FORMAT`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_auto.c -->
# sources/storage-engines/wiredtiger/src/log/log_auto.c

## Purpose
`log_auto.c` is generated by `dist/log.py` and implements the binary codec and JSON-ish print helpers for individual log operations inside `WT_LOGREC_COMMIT` and system records. It provides size, pack, unpack, and print routines for row/column updates, truncates, checkpoint start markers, previous-LSN records, backup IDs, and transaction timestamps.

## Important APIs and Functions
- Low-level helpers: `__pack_encode_uintAny`, `__pack_encode_WT_ITEM`, `__pack_encode_WT_ITEM_last`, `__pack_encode_string`, and decode macros implement variable-length integer, sized item, last-item, and NUL string encoding.
- Record helpers: `__wt_logrec_alloc`, `__wt_logrec_free`, `__wt_logrec_read`, `__wt_logop_read`, `__wt_logop_unpack`, `__wt_logop_write`.
- Data operation codecs:
  - `__wt_logop_col_modify/put/remove/truncate_*`
  - `__wt_logop_row_modify/put/remove/truncate_*`
- System/metadata operation codecs:
  - `__wt_logop_checkpoint_start_*`
  - `__wt_logop_prev_lsn_*`
  - `__wt_logop_backup_id_*`
  - `__wt_logop_txn_timestamp_*`
- Print dispatch: `__wt_txn_op_printlog` peeks at operation type/size and dispatches to the correct print function.
- Escaping helpers: `__logrec_make_json_str` and `__logrec_make_hex_str` redact or display payloads for printlog.

## Control Flow
Packing pattern:
1. A generated `__wt_struct_size_*` computes payload size from varint sizes and item/string bytes.
2. The public `__wt_logop_*_pack` adds operation header size, applies `__wt_struct_size_adjust`, extends the caller's log record, writes operation type and total operation size, then writes payload fields.
3. `logrec->size` is advanced by the encoded operation size.

Unpacking pattern:
1. `__wt_logop_*_unpack` reads operation type and size with `__wt_logop_unpack`.
2. It decodes fields in the same order used by the packer.
3. Unless compatibility macros disable strictness, it verifies operation type and that consumed bytes exactly equal the encoded size.
4. In `PACKING_COMPATIBILITY_MODE`, corrupted binary data may advance by encoded size rather than fail immediately, matching older behavior.

Print pattern:
1. A print function calls its unpacker.
2. User data is redacted unless `WT_TXN_PRINTLOG_UNREDACT` is set or the file id is `WT_METAFILE_ID`.
3. Items are JSON escaped and optionally hex encoded when `WT_TXN_PRINTLOG_HEX` is set.

## State and Persistence Behavior
- Encoded operation type and operation size are persisted before each operation payload.
- Most numeric fields use WiredTiger variable-length unsigned integer encoding.
- `WT_ITEM_last` encodings omit an explicit length and consume the remaining operation body, so strict size validation is critical.
- Generated code defines the exact on-disk operation wire format; changing field order, sizes, or operation constants is a compatibility change.
- `__wt_logrec_alloc` creates aligned scratch buffers and initializes the `WT_LOG_RECORD` header area, leaving the physical header to `log.c`.

## Dependencies and Integration Points
- Included prototypes live in `log.h`; private constants and operation enum values come from WiredTiger internals.
- Transaction logging (`src/txn/txn_log.c`) uses the packers to append operations to transaction log records.
- Recovery and log cursors use unpackers to replay or expose operations.
- Printlog uses `__wt_txn_op_printlog` and per-operation print helpers.
- Relies on WiredTiger variable-length packing (`__wt_vpack_uint`, `__wt_vunpack_uint`), buffer management, JSON escaping, and formatting APIs.

## Risks and Edge Cases
- Because this file is generated, manual edits can be overwritten or can desynchronize from `dist/log.py`.
- `_last` item/string decoding depends on correct operation boundaries; size-mismatch checks catch many but not all corruptions depending on compatibility macros.
- Redaction policy is file-id based; incorrect file IDs or ignored operation flags can leak or hide data in printlog.
- The string decoder uses `strlen` before size validation, so it assumes the provided buffer is safely addressable up to a NUL within the mapped record.
- Operation size is cast to `uint32_t`; callers must avoid records exceeding supported log operation sizes.

## Test Signals
- Round-trip pack/unpack tests for every operation type, including empty keys/values and large varints.
- Corruption tests for wrong operation type, truncated payload, size mismatch, missing string NUL, and `PACKING_COMPATIBILITY_MODE`.
- Printlog tests for redaction, `WT_METAFILE_ID`, hex output, and messages-only behavior through transaction printlog.
- Recovery tests that replay row/column modify, put, remove, truncate, checkpoint start, prev-LSN, backup ID, and timestamp records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_auto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_cursor.c -->
# sources/storage-engines/wiredtiger/src/log/log_cursor.c

## Purpose
`log_cursor.c` exposes WiredTiger log records through a cursor interface opened with `log:`. It scans physical log records via `__wt_log_scan`, then presents each transaction operation as cursor key/value tuples for recovery helpers, diagnostic tools, and code such as `__wt_log_needs_recovery`.

## Important APIs and Functions
- `__wt_curlog_open`: allocates and initializes `WTI_CURSOR_LOG`, configures cursor methods, forces buffered records out, and takes a read lock preventing log removal while the cursor is open.
- `__curlog_logrec`: callback from `__wt_log_scan`; copies one physical log record, stores current/next LSN, reads record type, and initializes intra-record stepping for commit records.
- `__curlog_next`: advances within the current commit record or scans one more physical record with `WT_LOGSCAN_ONE`.
- `__curlog_search`: positions by LSN from the cursor key, ignoring the step counter for search.
- `__curlog_kv`: converts current record/operation into cursor key `(file, offset, step)` and value `(txnid, rectype, optype, fileid, opkey, opvalue)`.
- `__curlog_op_read`: unpacks supported row/column modify, put, and remove operations into operation key/value buffers; unknown operations return raw operation bytes in the value.
- `__curlog_compare`, `__curlog_reset`, `__curlog_close`: implement cursor comparison, reset, resource cleanup, lock release, and cursor counter decrement.

## Control Flow
1. Opening a log cursor allocates LSNs and scratch buffers, initializes key/value formats, calls generic cursor init, flushes active log slots if logging is live, and acquires `log_remove_lock` in read mode.
2. `next` uses existing `stepp` pointers while there are unconsumed operations in the current commit record. When exhausted, it calls `__wt_log_scan` from `next_lsn` for one physical record.
3. `__curlog_logrec` skips the physical log header, reads the record type, and for commit records reads the transaction id. Non-commit records are returned as whole-record payloads.
4. `__curlog_kv` increments `step_count`, peeks operation type/size, unpacks a logical operation when possible, and populates the cursor key/value.
5. Closing frees all scratch buffers and releases the removal read lock, allowing archived log files to be removed.

## State and Persistence Behavior
- Cursor state is in `WTI_CURSOR_LOG`: `cur_lsn`, `next_lsn`, copied `logrec`, operation buffers, stepping pointers, `step_count`, `rectype`, and `txnid`.
- The cursor does not persist state; it reads persistent log records and materializes copies into scratch buffers.
- A live cursor increments `conn->log_mgr.cursors` and holds `log->log_remove_lock`, preventing removal/truncation from deleting files being scanned.
- `search` treats the counter component as ignored and positions only by file/offset LSN.

## Dependencies and Integration Points
- Depends on `__wt_log_scan` from `log.c` and operation unpackers from `log_auto.c`.
- Uses key/value formats from `log_private.h` (`WTI_LOGC_KEY_FORMAT`, `WTI_LOGC_VALUE_FORMAT`).
- Used by recovery-adjacent logic, print/inspection paths, and `__wt_log_needs_recovery`.
- Integrates with generic WiredTiger cursor API macros and stats counters.

## Risks and Edge Cases
- The cursor only turns selected row/column put/modify/remove operations into logical keys/values; truncates and other operation types are returned as raw values.
- `next` treats a zero byte at `stepp` as zero-fill/end-of-record, matching padded record behavior.
- Holding the removal lock for long cursor scans can block log archival/removal.
- Search ignores step counter, so callers seeking a specific operation within one LSN must iterate after positioning.
- Raw-mode toggling around cursor get/set must restore cursor flags on all error paths.

## Test Signals
- Cursor tests should cover next/search/reset/compare/close and open cursor blocking log removal.
- Operation exposure tests should verify row and column put/modify/remove key/value formatting.
- Non-commit record tests should verify whole-record payload return with `WT_LOGOP_INVALID`.
- Boundary tests should cover end-of-log mapping from `ENOENT` to `WT_NOTFOUND`, padded zero bytes, and searching init/invalid/future LSNs through scan behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_inline.h -->
# sources/storage-engines/wiredtiger/src/log/log_inline.h

## Purpose
`log_inline.h` provides small inline helpers for endian conversion of log descriptors/records, atomic LSN access/comparison/stringification, and a race-avoiding preallocation-enabled check. These are hot-path or header-layout utilities shared by log implementation files.

## Important APIs and Functions
- `__wti_log_desc_byteswap`: byte-swaps `WTI_LOG_DESC` fields on big-endian hosts.
- `__wti_log_record_byteswap`: byte-swaps persisted `WT_LOG_RECORD` header fields on big-endian hosts.
- `__wt_log_cmp`: compares two `WT_LSN` values by reading each 64-bit atomic `file_offset` once.
- `__wt_lsn_string`: formats an LSN into `file,offset`.
- `__wt_lsn_file`, `__wt_lsn_offset`: atomically read individual file and offset components.
- `__wti_log_is_prealloc_enabled`: checks `log_mgr.prealloc_init_count` instead of the live adaptive `prealloc` counter to avoid concurrent read/write races.

## Control Flow Role
The inline functions are used throughout write, scan, sync, cursor, and manager code:
- Before checksumming/writing and after reading persisted headers, `log.c` calls the byteswap helpers to keep disk format little-endian.
- Slot release, scan range handling, sync waits, cursor comparison, and backup filtering call `__wt_log_cmp`.
- File and offset accessors are used wherever LSN components are reported or passed into cursor keys.
- Manager/server code uses `__wti_log_is_prealloc_enabled` to decide whether preallocation work is configured.

## State and Persistence Behavior
- Byteswap helpers define the endian boundary for persisted log descriptor and record headers.
- `__wt_log_cmp` deliberately snapshots each LSN once to avoid inconsistent comparisons when another thread updates an LSN concurrently.
- Preallocation enabled state is based on the initial configured count, not the adaptive count that changes while the log server runs.

## Dependencies and Integration Points
- Includes `log_private.h` for private structures and uses `WT_LOG_RECORD`, `WTI_LOG_DESC`, `WT_LSN`, session/connection macros, atomics, `WT_READ_ONCE`, and formatting helpers.
- Called by `log.c`, `log_mgr.c`, and `log_cursor.c`.

## Risks and Edge Cases
- Any new fields in `WTI_LOG_DESC` or `WT_LOG_RECORD` must update the corresponding byteswap helper.
- Direct LSN field reads elsewhere can bypass the one-read comparison discipline and introduce races.
- `__wt_lsn_string` asserts with a NULL session, so the assert mechanism must tolerate that use.
- Preallocation semantics depend on `prealloc_init_count` remaining immutable after configuration.

## Test Signals
- Big-endian or simulated endian tests should verify descriptor and record header round trips.
- Concurrency tests should exercise LSN comparison while writers advance `alloc_lsn`, `write_lsn`, and `sync_lsn`.
- Reconfiguration/preallocation tests should verify adaptive `prealloc` changes do not disable configured preallocation checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_mgr.c -->
# sources/storage-engines/wiredtiger/src/log/log_mgr.c

## Purpose
`log_mgr.c` owns lifecycle, configuration, compatibility-version policy, and background service threads for the WiredTiger log subsystem. It parses `log.*` and `transaction_sync.*` configuration, creates/destroys `WTI_LOG`, starts log server threads, drives idle force writes, file close/sync, write-LSN advancement, preallocation, and log removal.

## Important APIs and Functions
- `__wt_logmgr_config`: parse logging configuration, validate incompatibilities, set compressor/path/file size/prealloc/remove/zero-fill/recovery/sync options.
- `__wt_logmgr_create`: allocate and initialize `WTI_LOG`, locks, condition variables, version settings, open/create log files, initialize slots, and write a creation message before recovery.
- `__wt_logmgr_open`: start background log-close, write-LSN, and log-server threads after recovery.
- `__wt_logmgr_reconfig`: apply allowed runtime config and update log version policy.
- `__wt_logmgr_destroy`: stop threads, join them, destroy slots/handles/locks/conditions, and free manager-owned memory.
- `__wt_logmgr_compat_version`, `__logmgr_get_log_version`, `__logmgr_version`: map WiredTiger compatibility versions to log file versions and force live file rollover/removal for downgrade compatibility.
- `__wt_log_truncate_files`: public removal/truncation helper for manual or backup-driven removal.
- Background thread bodies:
  - `__log_file_server`: fsync/truncate/close old log file handles after rollover.
  - `__log_wrlsn_server`: calls `__wti_log_wrlsn` to advance `write_lsn` in contiguous slot order.
  - `__log_server`: forces idle buffers, preallocates future log files, and removes old logs.
- Removal/preallocation helpers: `__compute_min_lognum`, `__log_remove_once`, `__log_prealloc_once`, `__logmgr_force_remove`.

## Control Flow
Configuration:
1. `__wt_logmgr_config` reads `log.enabled`; rejects logging with `in_memory`.
2. On initial config, it resolves compressor and log path and fixed file size/extension settings.
3. If enabled, it parses removal/archive, dirty OS-cache percentage, preallocation, force-write wait, recovery mode, zero fill, and transaction sync mode.
4. Transaction sync flags are assembled locally and published with a release barrier.

Startup:
1. `__wt_logmgr_create` returns early if logging was not configured.
2. It sets `WT_LOG_ENABLED`, allocates `WTI_LOG`, initializes all LSNs/locks/conditions, applies version selection, opens/creates log files, initializes slots, and writes a system message.
3. `__wt_logmgr_open` sets the server flag, starts close/wrlsn/server sessions and threads, and writes a post-recovery startup message.

Runtime threads:
1. `__log_server` periodically forces buffered writes when idle, preallocates files under hot-backup constraints, and removes archived files when configured.
2. `__log_wrlsn_server` advances `write_lsn` by sorting written slots by release LSN and coalescing contiguous slots.
3. `__log_file_server` observes `log_close_fh`, waits for writes through `log_close_lsn`, fsyncs/truncates/closes the old file, then advances `sync_lsn` to the next file start.

Shutdown:
1. `__wt_logmgr_destroy` clears the log-server flag, signals/join threads, closes internal sessions, destroys slot buffers and file handles, destroys conditions/locks, and frees `log_path`/`log`.

## State and Persistence Behavior
- Manager flags distinguish configured, enabled, existing logs, removal, recovery dirty/done/error/failure, downgrade, forced downgrade, incremental backup requirements, and zero-fill policy.
- `req_min/req_max` store compatibility-required log versions and are checked before modifying files.
- Removal keeps all logs needed by checkpoint, sync, active/incremental backup, and debug retention.
- Preallocation adapts `log_mgr.prealloc`: missed files increase the target, surplus files gradually decrease it, while `prealloc_init_count` remains the configured baseline.
- The server writes log messages marking creation and thread startup, which become persistent message records.

## Dependencies and Integration Points
- Calls physical operations from `log.c` (`__wti_log_open`, `__wti_log_close`, `__wti_log_force_write`, `__wti_log_wrlsn`, `__wti_log_allocfile`, `__wti_log_remove`, `__wti_log_set_version`, `__wt_log_printf`, `__wt_log_truncate_files`).
- Interacts with connection open/close/reconfiguration, checkpoint sessions, hot backup locks, debug retention config, stats counters, internal sessions, and thread/condition APIs.
- Consumes compatibility version state from the connection and affects recovery/removal behavior through `WT_LOG_FORCE_DOWNGRADE`.

## Risks and Edge Cases
- Reconfiguration intentionally cannot enable/disable logging or change fixed settings like path/compressor/file size; accepting those changes would be unsafe.
- Thread shutdown ordering matters because checkpoint server may be gone while logging still tracks log-written thresholds.
- Removal must not race with open log cursors or hot backup; it uses `log_remove_lock`, cursor counts, and hot backup locks.
- Downgrade requires forcing a checkpoint and removal of newer-version logs; failures can leave logs incompatible with requested versions.
- Barrier semantics around `log_close_fh/log_close_lsn` are explicitly documented and TSAN-specific in places.
- `__logmgr_force_remove` opens an internal session and loops checkpoint/removal until old logs disappear; errors here can block compatibility downgrade.

## Test Signals
- Config tests for enabled mismatch on reconfigure, in-memory incompatibility, read-only plus zero-fill rejection, deprecated `log.archive`, and transaction sync mode flags.
- Lifecycle tests for create/open/destroy with logging enabled/disabled/read-only and for startup messages.
- Threaded stress tests for slot close, write-LSN advancement, file rollover, idle force writes, and shutdown with outstanding writes.
- Log archival tests for checkpoint/sync minima, backup cursor minima, debug retention, open log cursor blocking, and incremental backup removal.
- Compatibility tests for live downgrade, forced removal, and version bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_private.h -->
# sources/storage-engines/wiredtiger/src/log/log_private.h

## Purpose
`log_private.h` defines private logging subsystem structures, constants, state encodings, and prototypes shared among the log implementation files. It contains the group-commit slot state machine, private log runtime state (`WTI_LOG`), log descriptor format, and private log cursor structure.

## Important APIs, Types, and Constants
- File prefixes: `WTI_LOG_PREPNAME` for preallocated files and `WTI_LOG_TMPNAME` for temporary allocation files.
- `WTI_LOG_ALIGN`: 128-byte alignment for log headers and records.
- Cursor formats: `WTI_LOGC_KEY_FORMAT` and `WTI_LOGC_VALUE_FORMAT`.
- Slot sizing: `WTI_LOG_SLOT_BUF_SIZE`, `WTI_LOG_SLOT_BUF_MAX`, `WTI_LOG_SLOT_UNBUFFERED`.
- Slot state encodings:
  - `WTI_LOG_SLOT_FREE`
  - `WTI_LOG_SLOT_WRITTEN`
  - `WTI_LOG_SLOT_CLOSE`
  - `WTI_LOG_SLOT_RESERVED`
  - masks and extractors for joined/released byte counts.
- `WTI_LOGSLOT`: cache-line-padded group-commit slot with atomic state/error/flags, file offsets, LSN boundaries, file handle, and buffer.
- `WTI_MYSLOT`: per-writer view of slot membership, offsets, and close/release/unbuffered flags.
- `WTI_LOG`: runtime logging state with file ids, file handles, LSNs, spin/rw locks, condition variables, active slot pool, slot buffer size, and private flags.
- `WTI_LOG_DESC`: persisted file descriptor block with magic, version, and log size.
- `WTI_CURSOR_LOG`: private cursor state for `log:` cursors.
- Private prototypes for slot operations, file allocation/removal/open/close, version change, force-write, previous-LSN system records, and write-LSN advancement.

## Control Flow Role
This header is the contract for:
- Writer threads joining a shared active slot, recording joined/released byte counts, and deciding whether they close/release a slot.
- `log.c` switching slots, allocating LSN ranges, writing file headers, truncating, scanning, and releasing slots.
- `log_mgr.c` server threads walking `slot_pool`, advancing `write_lsn`, closing files, and forcing idle slots out.
- `log_cursor.c` maintaining cursor-local scan state.

## State and Persistence Behavior
- `WTI_LOGSLOT.slot_state` packs joined bytes in the high 32-bit region and released bytes in the low 32-bit region, with high bits reserved for close/special states.
- The active slot pool has 128 slots and is not represented as a conventional aligned array beyond this explicit layout because cache-line behavior is important.
- `WTI_LOG_DESC` is persisted at the start of each log file; magic/version/log_size values are validated on open.
- `WTI_LOG` LSN fields track allocation, checkpoint, dirty, first, directory-sync, file-sync, truncation, write-end, and write-start positions.
- `WTI_CURSOR_LOG` stores copied record data and intra-record operation pointers, not persistent state.

## Dependencies and Integration Points
- Included by `log.c`, `log_mgr.c`, `log_cursor.c`, `log_auto.c`, and `log_inline.h`.
- Relies on WiredTiger cache-line padding, atomics, flags macros, `WT_ITEM`, `WT_FH`, locks, condition variables, and session/connection structures.
- Private prototypes are generated by `prototypes.py`; implementations are distributed across `log.c` and `log_mgr.c`.

## Risks and Edge Cases
- Slot state uses signed integer encodings and comments note it should eventually be unsigned; mask logic is therefore fragile and must be kept consistent.
- Adding new slot states reduces maximum representable slot size because high bits are reserved.
- `WTI_LOG_SLOT_UNBUFFERED` is encoded into joined state and must stay compatible with buffer size/mask assumptions.
- Cache-line padding is enforced by `static_assert`; structure changes can affect performance or correctness under false sharing.
- `WTI_LOG` combines many locks with documented ownership expectations; calling private functions without the expected lock can corrupt state.
- On-disk `WTI_LOG_DESC` magic/version constants are compatibility-sensitive.

## Test Signals
- Slot unit/stress tests should cover join/release accounting, unbuffered records, close flag propagation, slot coalescing, and free/written transitions.
- Performance/concurrency tests should watch for regressions from padding or active slot count changes.
- Format tests should validate descriptor magic/version/log_size and endian handling.
- Cursor tests should verify `WTI_CURSOR_LOG` state transitions through commit and non-commit records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/log/log_private.h -->

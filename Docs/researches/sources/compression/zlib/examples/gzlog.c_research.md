# sources/compression/zlib/examples/gzlog.c

## Purpose
Implements the crash-recoverable gzipped log object declared in `gzlog.h`. It optimizes frequent short appends by writing them as uncompressed deflate stored blocks in a valid gzip file, then periodically recompressing accumulated stored data with a 32 KiB dictionary to preserve compression ratio. It also recovers interrupted append, compress, and dictionary-replacement operations.

## APIs, Types, And Functions
External APIs are `gzlog_open()`, `gzlog_write()`, `gzlog_compress()`, and `gzlog_close()`. Internal `struct log` stores the magic id, open `.gz` descriptor, path buffer, offsets to first/last stored blocks, bit-back offset, stored length, compressed and total CRC/lengths, and lock timestamp. Major helpers include lock management (`log_lock()`, `log_touch()`, `log_check()`, `log_unlock()`), gzip extra-field parsing and marking (`log_head()`, `log_mark()`), stored-block repair (`log_last()`), operations (`log_append()`, `log_compress()`, `log_replace()`), recovery logging (`log_log()`), `log_recover()`, `log_close()`, and `log_open()`.

## Control Flow
`gzlog_open()` allocates a log object, creates/acquires `path.lock`, initializes `path.gz` if empty, reads the custom gzip extra field, and recovers any marked operation. `gzlog_write()` writes the new payload to `path.add`, marks `APPEND_OP`, appends stored-block data, updates trailer and extra field to `NO_OP`, deletes `.add`, then triggers `gzlog_compress()` when stored data reaches `TRIGGER`. `gzlog_compress()` reads stored blocks into memory, writes `.add` and `.temp`, marks `COMPRESS_OP`, recompresses stored data over the previous stored region using `.dict` if available, writes a valid trailer, marks `REPLACE_OP`, replaces `.dict` with `.temp`, and finally marks `NO_OP`. `log_recover()` resumes based on the operation bits in the extra field.

## State And Persistence
Persistence spans several files sharing the path prefix: `path.gz` is always intended to be a valid gzip log after successful public calls; `path.add` stores append/compress payload for recovery; `path.dict` stores the previous 32 KiB dictionary; `path.temp` stores the next dictionary during compression; `path.lock` gates exclusive access and stale-lock handling; `path.repairs` records recovery events. The gzip extra field is the transaction marker and contains offsets, CRCs, lengths, stored-block length, bit-back position, and operation code. The code assumes the extra-field rewrite is effectively atomic due to its small fixed location near the file start.

## Dependencies And Integration
Depends on POSIX file APIs (`open`, `read`, `write`, `lseek`, `ftruncate`, `fsync`, `rename`, `unlink`, `stat`, `utimes`, `sleep`), libc time/reporting routines, and zlib `crc32`, raw `deflateInit2(-15)`, `deflateSetDictionary()`, `deflatePrime()`, `deflate()`, and `deflateEnd()`. The custom gzip header includes an `ap` extra subfield; non-gzlog gzip files are rejected by header comparison.

## Risks And Test Signals
Critical risks are transaction ordering, stale lock races, partial writes despite `fsync`, large in-memory compression of stored data, path suffix mutation through a shared buffer, and correctness of raw deflate bit priming/replacement. Missing `.add` during recovery can intentionally lose the interrupted append/compress data while restoring a valid gzip. Test signals include interruption injection via `GZLOG_DEBUG`, concurrent writer lock contention, stale lock expiry, disk-full behavior, recovery from each operation state, verification that `gunzip path.gz` succeeds after every public call, repeated compression thresholds, and dictionary replacement with missing `.temp` or `.dict`.

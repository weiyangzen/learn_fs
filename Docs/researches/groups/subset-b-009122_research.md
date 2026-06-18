# subset-b-009122 research

Grouped source-tree-aligned research report. Each section is delimited for reconciliation into per-file reports.


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/hashmap.h -->
# sources/sync-backup/casync/src/hashmap.h

Purpose: declares casync's imported systemd-style generic hash container API: plain `Hashmap`, insertion-ordered `OrderedHashmap`, and key-only `Set`, all backed by the opaque `HashmapBase` implementation in `hashmap.c`. It lets callers treat `NULL` maps as empty for reads, which reduces allocation noise across optional metadata paths.

Important APIs/types/functions: exposes `Iterator`, `ITERATOR_FIRST`, allocation/free/copy helpers, put/update/replace/get/get2/contains/remove variants, merge/move/reserve, size/bucket inspection, first/steal-first helpers, ordered next lookup, `*_get_strv`, and `HASHMAP_FOREACH*` macros. GCC type-checking macros (`HASHMAP_BASE`, `PLAIN_HASHMAP`) intentionally reject incompatible pointer families at compile time.

Control flow/state: the header is mostly inline wrappers around internal polymorphic functions. Iteration state is caller-owned in `Iterator`; debug builds add mutation counters and source location plumbing via `HASHMAP_DEBUG_*`.

Dependencies/integration: depends on `hash-funcs.h` for hash/equality operations and `util.h` for cleanup macros. `set.h` builds its public API directly on these calls.

Risks/test signals: misuse risk is iterator invalidation, freeing ownership confusion in `free_free` helpers, and mixing map types outside permitted merge cases. Coverage is indirect through match/origin/name-table code using maps/sets rather than a dedicated hashmap test here.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/hashmap.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/log.c -->
# sources/sync-backup/casync/src/log.c

Purpose: implements the small process-wide logging layer used by casync tools and tests. Messages go to `stderr` with a priority prefix and optional errno text.

Important APIs/types/functions: `set_log_level`, `set_log_level_from_string`, `log_info_errno`, `log_error_errno`, and `log_debug_errno`. `level_from_string` accepts emergency through debug plus numeric levels; `get_log_level` lazily reads `$SYSTEMD_LOG_LEVEL`.

Control flow/state: `log_max_level` is a static global initialized to `-1`. Each public logger funnels through `log_fullv`, which suppresses messages above the current max level, appends `strerror(abs(error))` when `error` is nonzero, and returns negative errno for error-carrying calls.

Dependencies/integration: uses syslog priority constants, stdio varargs, and `isempty` from `util.h`. `log.h` wraps it in ergonomic macros used by test helpers, notify-wait, and utility failures.

Risks/test signals: global log level is not synchronized, so concurrent reconfiguration would race. Environment parsing accepts numeric values that may not map to known syslog severities. Tests mostly exercise this indirectly through failing `assert_se` and helper diagnostics.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/log.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/log.h -->
# sources/sync-backup/casync/src/log.h

Purpose: public declaration layer for casync logging and assertion helpers.

Important APIs/types/functions: declares the three errno-aware log functions, macro aliases `log_info`, `log_error`, `log_debug`, `log_oom`, `assert_se`, `assert_not_reached`, `set_log_level`, and `set_log_level_from_string`. `_printf_` annotations let the compiler check format strings.

Control flow/state: no runtime state lives here, but `assert_se` evaluates an expression and logs a fatal-style error before calling `abort` on false. `assert_not_reached` always logs and aborts.

Dependencies/integration: includes `gcc-macro.h` for compiler annotations and errno types for `-ENOMEM` reporting. Many source and test files use `assert_se` as a hard test oracle.

Risks/test signals: `assert_se` remains active in release-style builds unlike standard `assert`, so callers must avoid expressions with unacceptable side effects in production paths. The header is heavily exercised by every C test binary.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/log.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/mempool.c -->
# sources/sync-backup/casync/src/mempool.c

Purpose: provides a simple fixed-size tile memory pool used through the `DEFINE_MEMPOOL` macro to amortize allocation overhead for many same-sized objects.

Important APIs/types/functions: internal `struct pool`, macro-generated `mempool_alloc_tile`, exported `mempool_free_tile`, and `mempool_drop`. A pool tracks a linked list of allocated blocks, tile size, first free tile, and allocation batch size.

Control flow/state: allocation first pops from `mp->first_free`; if empty, it allocates a new `struct pool` plus `at_least` tiles, chains all but one onto the freelist, and returns one tile. Freeing prepends the tile to the freelist. Dropping walks `first_pool` and frees every backing block.

Dependencies/integration: uses `malloc`, `free`, `offsetof`, and `util.h` helpers; consumers instantiate typed allocators in headers or C files.

Risks/test signals: tiles are not poisoned or checked for double-free, and all outstanding tile pointers become invalid after `mempool_drop`. The implementation is single-threaded and depends on correct macro-provided tile sizes.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/mempool.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/mempool.h -->
# sources/sync-backup/casync/src/mempool.h

Purpose: declares the shared pool state and the macro that generates type-specific allocation functions.

Important APIs/types/functions: `struct mempool` contains backing pools, freelist, tile size, and batch size. `DEFINE_MEMPOOL(pool_name, tile_type, alloc_at_least)` creates a static allocator that initializes size metadata and calls `mempool_alloc_tile`. `mempool_free_tile` and `mempool_drop` handle return and teardown.

Control flow/state: pool state is caller-owned and persists until `mempool_drop`; individual generated allocators lazily initialize `tile_size`/`at_least` on each call so zero-initialized structs are valid.

Dependencies/integration: intended for source-local object caches where callers can store `struct mempool` in a larger context.

Risks/test signals: the macro hides allocation failure paths and assumes the requested type is stable for the lifetime of the pool. There is no direct test in this subset; confidence comes from consumers that allocate parser/matcher nodes.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/mempool.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/meson.build -->
# sources/sync-backup/casync/src/meson.build

Purpose: defines the casync source grouping for Meson builds.

Important APIs/types/functions: creates `util_sources`, `libshared_sources`, `libshared` static library, `casync_sources`, conditional FUSE source inclusion, and `casync_http_sources`. The manifest lists core modules such as cache, chunking, compression, encoder/decoder, remoting, stores, hash maps, mempool, notification, parsing, quota, reflink, rm-rf, and siphash.

Control flow/state: build-time state comes from Meson configuration variables such as `HAVE_FUSE`. `libshared` combines common code used by tools and tests; executable-specific sources are separated from reusable modules.

Dependencies/integration: connects source files to top-level Meson targets and the test/fuzz Meson files. Conditional source inclusion must match configuration options and optional library detection.

Risks/test signals: source list drift can silently omit a new module from builds or tests. The tests in `test/meson.build` depend on this library being complete enough to link all helper binaries.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/meson.build -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/notify.c -->
# sources/sync-backup/casync/src/notify.c

Purpose: implements sd_notify-style readiness notification for helpers that need to tell a parent process they are ready.

Important APIs/types/functions: `send_notify(const char *text)` reads `$NOTIFY_SOCKET`, constructs an abstract or pathname UNIX datagram address, opens `AF_UNIX/SOCK_DGRAM|SOCK_CLOEXEC`, sends the text with `sendto`, and returns `1` on sent, `0` when no socket is configured, or negative errno.

Control flow/state: no persistent state beyond environment lookup. The leading `@` convention is translated to Linux abstract namespace by replacing it with a NUL byte in `sun_path`.

Dependencies/integration: used by services/tests coordinated by `notify-wait.c` and scripts that launch FUSE/NBD/HTTP helpers.

Risks/test signals: socket path length is bounded by `sockaddr_un`; too-long values return `-EINVAL`. Datagram send failures surface as negative errno. Readiness tests indirectly validate it via `notify-wait`.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/notify.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/notify.h -->
# sources/sync-backup/casync/src/notify.h

Purpose: tiny public header for readiness notification.

Important APIs/types/functions: declares `send_notify(const char *text)`. The include guard name is idiosyncratic but effective.

Control flow/state: none in the header; callers pass complete notification payloads such as `READY=1`.

Dependencies/integration: paired with `notify.c`; included by components that need to synchronize background helper startup with shell tests.

Risks/test signals: since only the declaration is here, ABI mismatch risk is low. Correctness depends on callers using newline-compatible sd_notify payload syntax and handling `0` when no notification socket exists.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/notify.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/parse-util.c -->
# sources/sync-backup/casync/src/parse-util.c

Purpose: parses and formats byte-size quantities for CLI/config-style input and output.

Important APIs/types/functions: `parse_size` recognizes numeric values with optional binary unit suffixes from bytes through exabytes, plus `K/M/G/T/P/E` aliases; `format_bytes` converts byte counts into a compact human-readable binary unit string.

Control flow/state: `parse_size` uses `strtoull`, checks suffixes against a local table, rejects fractional values that would not divide cleanly after scaling, and returns `-ERANGE`/`-EINVAL` on overflow or malformed input. `format_bytes` chooses the largest unit where the value is cleanly divisible, otherwise reports raw bytes.

Dependencies/integration: includes `time-util.h` only transitively for utility constants and `util.h` for helpers. Used by command-line parsing and status output.

Risks/test signals: decimal-looking fractional input is accepted only when exactly representable after binary scaling; unexpected whitespace/suffix combinations can be rejected. No direct test in this subset, so coverage is likely via CLI tests.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/parse-util.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/parse-util.h -->
# sources/sync-backup/casync/src/parse-util.h

Purpose: declaration header for byte-size parsing/formatting helpers.

Important APIs/types/functions: defines `FORMAT_BYTES_MAX`, declares `parse_size(const char*, uint64_t*)`, and `format_bytes(char*, size_t, uint64_t)`.

Control flow/state: stateless API; callers own the output buffer for formatting and receive parsed values through an out-parameter.

Dependencies/integration: includes `<inttypes.h>` for `uint64_t`. The functions are suitable for command-line option parsing and diagnostic output across casync.

Risks/test signals: callers must provide buffers at least `FORMAT_BYTES_MAX` for conservative formatting. Input validation behavior is defined in the C file rather than documented in detail here.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/parse-util.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/quota-projid.c -->
# sources/sync-backup/casync/src/quota-projid.c

Purpose: reads and writes Linux filesystem project quota IDs on an open file descriptor.

Important APIs/types/functions: `read_quota_projid` uses `FS_IOC_FSGETXATTR` and returns `fsx_projid`; `write_quota_projid` reads existing `fsxattr`, changes only `fsx_projid`, and writes it back with `FS_IOC_FSSETXATTR`.

Control flow/state: functions are stateless wrappers around `ioctl`. `write_quota_projid` preserves all other extended inode flags by round-tripping the current struct first.

Dependencies/integration: depends on Linux `<linux/fs.h>` and open file descriptors from higher-level archive/extract code that wants quota project inheritance.

Risks/test signals: only works on filesystems supporting these ioctls; failures return negative errno. Race potential exists if another process changes fsxattr between get and set. Tests are likely platform-dependent and not direct in this subset.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/quota-projid.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/quota-projid.h -->
# sources/sync-backup/casync/src/quota-projid.h

Purpose: public interface for Linux project quota ID helpers.

Important APIs/types/functions: declares `read_quota_projid(int fd, uint32_t *ret)` and `write_quota_projid(int fd, uint32_t id)`.

Control flow/state: no state in the header; all persistence is filesystem metadata addressed by fd.

Dependencies/integration: includes integer types and is compiled only where Linux quota ioctls are available through the implementation.

Risks/test signals: callers must be prepared for `-ENOTTY`, `-EOPNOTSUPP`, or permission failures. Extraction logic should treat unsupported project IDs according to feature flags rather than blindly failing portability cases.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/quota-projid.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/realloc-buffer.c -->
# sources/sync-backup/casync/src/realloc-buffer.c

Purpose: implements a growable byte buffer with efficient front consumption, append, fd read/write, formatted append, and ownership transfer.

Important APIs/types/functions: `realloc_buffer_acquire/acquire0`, `extend/extend0`, `append`, `advance`, `shorten`, `truncate`, `read_size`, `read_full`, `read_target`, `steal`, `donate`, `write`, `write_maybe`, `printf`, and `memchr`. It enforces `REALLOC_BUFFER_MAX` at 1 GiB.

Control flow/state: state is `data`, `allocated`, `start`, and `end`. Growth doubles allocation, aligns to page size, and compacts by copying live data when `start` is nonzero. Read functions append then shrink unused bytes; write drains from the front via `advance`.

Dependencies/integration: uses `page_size`, `mfree`, `memdup`, `BUFFER_SIZE`, and errno conventions from util/def. It is a core buffer primitive for chunk, compression, and protocol code.

Risks/test signals: `realloc_buffer_write` can busy-loop if `write` returns 0, though regular fds should not. Offset arithmetic is guarded, but callers must respect pointer invalidation after growth. `test-cachunk.c` exercises read/write paths indirectly.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/realloc-buffer.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/realloc-buffer.h -->
# sources/sync-backup/casync/src/realloc-buffer.h

Purpose: declares the growable buffer structure and inline accessors.

Important APIs/types/functions: `ReallocBuffer` stores backing pointer, allocation, start offset, and end offset. Inline helpers return current data, offset data, size, append-one-byte, empty, and read-default wrappers; exported functions cover allocation, trimming, fd I/O, printf append, donation/steal, and byte search.

Control flow/state: callers commonly zero-initialize the struct, pass it by address, and eventually call `realloc_buffer_free`. `realloc_buffer_data` deliberately returns the buffer object itself for empty unallocated buffers so zero-length acquisitions can produce a non-NULL sentinel.

Dependencies/integration: includes `util.h` for assertions, types, and printf annotations.

Risks/test signals: inline assertions catch internal invariant breaks in debug/test builds. Holding pointers across subsequent buffer mutation is unsafe and should be avoided.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/realloc-buffer.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/reflink.c -->
# sources/sync-backup/casync/src/reflink.c

Purpose: attempts copy-on-write reflinks between regions of two file descriptors, with block-aligned fallbacks and optional validation.

Important APIs/types/functions: `reflink_fd` is the public entry. Helpers include `pread_try_harder`, which reopens `/proc/self/fd/N` to pread from fds that may not support pread, and `validate`, which byte-compares copied ranges when enabled.

Control flow/state: the function aligns offsets to 4096-byte filesystem blocks, uses `FICLONERANGE`, tracks bytes reflinked in `ret_reflinked`, and returns negative errno on unsupported or invalid requests. It avoids partial unaligned regions that the kernel cannot clone.

Dependencies/integration: Linux `ioctl(FICLONERANGE)`, `struct file_clone_range`, fd utilities, and extraction/seed code that can optimize matching extents.

Risks/test signals: assumes 4096-byte block size, so filesystems with different clone granularity may underperform or fail. Validation is compile-time and expensive. Tests around seeded extraction and sparse/hardlink behavior provide indirect signals.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/reflink.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/reflink.h -->
# sources/sync-backup/casync/src/reflink.h

Purpose: public declaration for reflink cloning support.

Important APIs/types/functions: declares `reflink_fd(source_fd, source_offset, destination_fd, destination_offset, size, ret_reflinked)` using `uint64_t` offsets and sizes.

Control flow/state: no in-memory state; operation mutates destination file extents and optionally reports successfully cloned bytes.

Dependencies/integration: included by extraction or cache code that can use kernel COW clones as a fast path before falling back to copy.

Risks/test signals: callers must treat unsupported reflink as a recoverable condition and preserve correctness with normal writes. Alignment and filesystem behavior are handled in the implementation.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/reflink.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/rm-rf.c -->
# sources/sync-backup/casync/src/rm-rf.c

Purpose: recursively removes files/directories with guard rails for physical mount boundaries and immutable inode flags.

Important APIs/types/functions: `rm_rf_children`, `rm_rf_at`, `rm_rf`, plus `unlinkat_immutable`. `RemoveFlags` control root removal, recursive descent, physical filesystem restriction, and whether immutable attributes may be cleared.

Control flow/state: `rm_rf_at` opens/lstats the root and optionally unlinks it. `rm_rf_children` iterates directory entries, skips virtual filesystems when requested, descends into directories with `xopendirat`, and removes entries with `unlinkat_immutable`. Immutable handling can clear flags before unlinking.

Dependencies/integration: uses Linux statfs magic constants, `chattr.h`, openat/unlinkat patterns, and util directory helpers. Used by tests and cleanup paths for stores/trees.

Risks/test signals: destructive by design; flag interpretation is critical. Mount-boundary detection depends on `statfs` and root device state. `test-casync.c` uses `rm_rf` for cleanup, but no exhaustive deletion safety test appears here.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/rm-rf.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/rm-rf.h -->
# sources/sync-backup/casync/src/rm-rf.h

Purpose: declares recursive removal helpers and their flag contract.

Important APIs/types/functions: `RemoveFlags` includes `REMOVE_ROOT`, `REMOVE_RECURSIVE`, `REMOVE_PHYSICAL`, and `REMOVE_CHMOD`. Public functions are `rm_rf_children`, `rm_rf`, and `rm_rf_at`.

Control flow/state: no header state; flags define whether to remove just children or the root and whether cross-filesystem or immutable-flag behavior is allowed.

Dependencies/integration: includes `struct stat` because `rm_rf_children` can receive root device metadata for mount-boundary decisions.

Risks/test signals: callers must choose flags carefully. Passing `REMOVE_ROOT|REMOVE_PHYSICAL` to test cleanup is expected, but production deletion code should avoid overly broad roots.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/rm-rf.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/set.h -->
# sources/sync-backup/casync/src/set.h

Purpose: exposes a key-only set API implemented on top of the hashmap backend.

Important APIs/types/functions: `set_new`, free/free_free/copy, ensure-allocated, `set_put`, `set_get`, contains/remove, remove-and-put, merge, reserve, move/move_one, size/isempty/buckets, iteration, clear, first/steal-first, `SET_FOREACH`, and cleanup macros.

Control flow/state: all operations are thin wrappers around hashmap internals where the key is both identity and stored payload. `NULL` sets behave as empty for read paths through the hashmap base convention.

Dependencies/integration: includes `hashmap.h` and `util.h`; uses hash ops supplied by callers. Match trees, collections, and cache bookkeeping can use it for de-duplication.

Risks/test signals: ownership helpers such as `set_free_free` free stored keys, so callers must not mix borrowed and owned keys. Iteration ordering is undefined. Coverage is indirect through code that uses sets to deduplicate IDs or strings.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/set.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/signal-handler.c -->
# sources/sync-backup/casync/src/signal-handler.c

Purpose: centralizes signal blocking, exit handler installation, polling integration, and SIGPIPE suppression for the casync tool.

Important APIs/types/functions: `block_exit_handler`, `exit_signal_handler`, `install_exit_handler`, `sync_poll_sigset`, and `disable_sigpipe`. The file uses `CaSync` polling via `ca_sync_poll`.

Control flow/state: `block_exit_handler` changes the calling thread signal mask for SIGINT/SIGTERM. `install_exit_handler` installs a supplied handler for both. `sync_poll_sigset` temporarily unblocks exit signals around `ca_sync_poll` using `ppoll`-style semantics. `disable_sigpipe` ignores SIGPIPE process-wide.

Dependencies/integration: includes `casync.h`, `signal-handler.h`, and `util.h`; used by command-line transfer loops.

Risks/test signals: signal disposition and masks are process/thread global effects, so ordering matters when embedded. Tests likely cover behavior only through interruptible tool scenarios, not unit tests.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/signal-handler.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/signal-handler.h -->
# sources/sync-backup/casync/src/signal-handler.h

Purpose: declares helper functions for casync signal behavior.

Important APIs/types/functions: exports `block_exit_handler`, `exit_signal_handler`, `install_exit_handler`, `sync_poll_sigset`, and `disable_sigpipe`.

Control flow/state: API manipulates process signal handlers/masks and delegates polling to a `CaSync` instance.

Dependencies/integration: includes `<signal.h>` and `casync.h`, tying this header to the main transfer object rather than keeping it fully generic.

Risks/test signals: callers must restore old masks when appropriate and avoid conflicting handlers. The interface is narrow enough that regressions should show up as hung or uninterruptible command-line tests.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/signal-handler.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/siphash24.c -->
# sources/sync-backup/casync/src/siphash24.c

Purpose: implements SipHash-2-4, a keyed hash used for hash table seeding and stable keyed hashing of byte streams.

Important APIs/types/functions: provides state initialization, byte ingestion, finalization, compression rounds, and helper functions declared in `siphash24.h`. It maintains the standard four-word SipHash state and byte count/partial tail handling.

Control flow/state: callers initialize with a 128-bit key, write bytes in chunks, and finalize to a 64-bit result. The implementation processes complete 8-byte lanes and folds remaining bytes plus length during finalization.

Dependencies/integration: used by hash ops and any code needing collision-resistant keyed hashes. It depends on endian-safe utilities for little-endian reads.

Risks/test signals: cryptographic correctness hinges on exact rotation constants, endian packing, and finalization count. Hashmap behavior is an indirect integration test; dedicated known-vector tests would be stronger.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/siphash24.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/siphash24.h -->
# sources/sync-backup/casync/src/siphash24.h

Purpose: declares the SipHash state and public hashing helpers.

Important APIs/types/functions: defines `struct siphash` state fields and declares init/write/finalize-style functions for 64-bit keyed hash calculation.

Control flow/state: callers own mutable hash state until finalization. The API is incremental, so large keys/data do not need to be contiguous.

Dependencies/integration: includes integer types and is consumed by `hash-funcs`/hashmap code.

Risks/test signals: the state must not be reused after finalization unless reinitialized. Without visible test vectors in this subset, changes should be checked against standard SipHash-2-4 vectors.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/siphash24.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/time-util.c -->
# sources/sync-backup/casync/src/time-util.c

Purpose: implements time conversion/formatting helpers for monotonic and realtime values.

Important APIs/types/functions: includes functions for formatting timestamps or durations and for conversions used by polling timeouts. It complements inline conversions in `time-util.h`.

Control flow/state: stateless helpers convert between numeric nanoseconds and calendar/`timespec` representations, generally returning negative errno on invalid input or formatting failure.

Dependencies/integration: used by notify-wait timeout handling, progress/reporting paths, and utility code that needs monotonic deadline arithmetic.

Risks/test signals: overflow and clock-domain mixups are the main risks. `notify-wait.c` exercises `now`/`nsec_to_timespec` in a 30-second readiness timeout path.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/time-util.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/time-util.h -->
# sources/sync-backup/casync/src/time-util.h

Purpose: defines time constants and inline conversion helpers.

Important APIs/types/functions: declares nanosecond-per-unit constants, `timespec_to_nsec`, `nsec_to_timespec`, and `now(clockid_t)`. `now` wraps `clock_gettime` and returns nanoseconds.

Control flow/state: no persistent state. The conversion helpers are arithmetic-only and expect values that fit in `uint64_t`/`time_t` fields.

Dependencies/integration: included by utilities, notify-wait, and signal/poll code that computes deadlines.

Risks/test signals: overflow at extreme timestamps and platform `time_t` size are the main portability risks. Inline assertions make clock failures fatal in callers using `now`.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/time-util.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/udev-util.h -->
# sources/sync-backup/casync/src/udev-util.h

Purpose: provides a tiny cleanup integration point for libudev objects.

Important APIs/types/functions: defines cleanup functions/macros for `struct udev` or related udev references when udev support is compiled in.

Control flow/state: no runtime logic beyond cleanup wrappers; ownership follows libudev reference counting.

Dependencies/integration: used by device/NBD-related code that queries udev and wants `_cleanup_` style automatic unref.

Risks/test signals: header-only cleanup helpers are low risk, but conditional availability must match Meson feature detection. Device integration tests such as NBD paths are the likely signal.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/udev-util.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/util.c -->
# sources/sync-backup/casync/src/util.c

Purpose: implements broad low-level utilities for I/O, sparse writes, randomness, path/string handling, numeric parsing, fd/directory helpers, temporary directory selection, process waiting, and bounded line reading.

Important APIs/types/functions: key functions include `loop_write`, `loop_write_block`, `loop_read`, `write_zeroes`, `loop_write_with_holes`, `skip_bytes`, `dev_urandom`, hex helpers, `filename_is_valid`, `tempfn_random`, `hexdump`, `dirname_malloc`, `strjoin_real`, `ls_format_*`, `safe_atoi/atou/atollu/atollx`, `readlink*_malloc`, string-vector helpers, `xopendirat`, `progress`, `strextend`, `parse_uid`, `wait_for_terminate`, `page_size`, boolean parsing, `greedy_realloc*`, `skip_bytes_fd`, `rename_noreplace`, `path_startswith`, tmp dir lookup, `path_is_safe`, `is_dir`, `free_and_strdup`, `read_line`, `delete_trailing_chars`, and `strstrip`.

Control flow/state: most helpers are stateless. `dev_urandom` caches getrandom availability, `page_size` caches sysconf, and `progress` tracks spinner position/time. Sparse writing scans zero runs of at least 4096 bytes and uses hole punching when possible.

Dependencies/integration: central dependency for nearly every casync module and test. It wraps Linux features such as fallocate, renameat2, getrandom, statfs, and file attributes while preserving negative-errno style.

Risks/test signals: high blast radius; edge cases include short writes, nonblocking fds, sparse-file fallbacks, integer overflow, unsafe paths, and non-atomic `rename_noreplace` fallback. `test-util.c` directly verifies sparse write/read behavior; many other tests exercise paths indirectly.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/util.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/util.h -->
# sources/sync-backup/casync/src/util.h

Purpose: declares and defines casync's common utility API, macros, cleanup helpers, endian helpers, string/path predicates, numeric helpers, and allocation helpers.

Important APIs/types/functions: exposes allocation macros `new/new0/newa`, safe `MAX/MIN`, `IN_SET`, cleanup functions, safe close/fclose helpers, little-endian read/write, `memdup`, random helpers, string macros (`streq`, `startswith`, `strjoina`, STRV helpers), path predicates, fd I/O functions, formatting constants, `GREEDY_REALLOC`, and many prototypes implemented in `util.c`.

Control flow/state: header-only macros often evaluate arguments carefully with GCC extensions. Cleanup macros integrate with automatic variable cleanup attributes.

Dependencies/integration: includes libc, Linux fs headers, `gcc-macro.h`, and `log.h`; it is the common substrate for the whole C codebase.

Risks/test signals: macro complexity can hide type and lifetime mistakes, especially stack allocation via `strjoina/newa` and ownership transfer with cleanup attributes. Broad integration tests are the main regression signal.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/util.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test-files/test-files.sh -->
# sources/sync-backup/casync/test-files/test-files.sh

Purpose: creates the fixture tree used by casync integration tests.

Important APIs/types/functions: shell commands create regular files, sparse or random content, directories, links, device-like entries when permitted, and metadata combinations expected by archive/digest tests.

Control flow/state: mutates the current working directory by laying out deterministic test files. It is meant to be run from test setup, not sourced as a library.

Dependencies/integration: consumed by `test-script.sh.in`, FUSE/NBD variants, and source-tree fixture copying. It depends on standard Unix tools and root privileges for any privileged node/metadata cases.

Risks/test signals: environment-sensitive fixtures can differ when run unprivileged or on filesystems lacking special metadata support. The integration scripts compare list/mtree/digest output against this tree.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test-files/test-files.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/fuzz-compress.c -->
# sources/sync-backup/casync/test/fuzz/fuzz-compress.c

Purpose: libFuzzer target for compression/decompression handling.

Important APIs/types/functions: `LLVMFuzzerTestOneInput` accepts arbitrary bytes, feeds them through casync compression APIs, and validates that the code rejects or round-trips inputs without crashing or leaking under sanitizer builds.

Control flow/state: stateless per fuzz case except heap buffers allocated by compression helpers. The target returns 0 for all inputs so coverage-guided fuzzing can continue.

Dependencies/integration: linked by `test/fuzz/meson.build` and built for OSS-Fuzz via `tools/oss-fuzz.sh`.

Risks/test signals: fuzz value is strongest for malformed compressed streams and allocation edge cases. It is not a semantic corpus test for all compression algorithms unless build options enable them.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/fuzz-compress.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/fuzz-main.c -->
# sources/sync-backup/casync/test/fuzz/fuzz-main.c

Purpose: standalone runner for fuzz targets outside libFuzzer.

Important APIs/types/functions: `main` reads input files from argv, loads their bytes, and invokes the target entry point declared in `fuzz.h`.

Control flow/state: iterates over command-line paths, opens/reads each test case into memory, calls `LLVMFuzzerTestOneInput`, then exits nonzero on I/O/allocation failures.

Dependencies/integration: lets Meson tests or developers replay corpus entries without a fuzzing engine. Paired with `fuzz-compress.c` and optional generated corpora.

Risks/test signals: whole-file loading can be memory-heavy for very large inputs; replay coverage depends on passing representative corpus files.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/fuzz-main.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/fuzz.h -->
# sources/sync-backup/casync/test/fuzz/fuzz.h

Purpose: shared declaration for casync fuzz harnesses.

Important APIs/types/functions: declares the libFuzzer-compatible `LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)` entry point.

Control flow/state: no state. Provides a common interface so `fuzz-main.c` can call individual fuzz target objects.

Dependencies/integration: included by fuzz target files and the standalone runner.

Risks/test signals: API must remain ABI-compatible with libFuzzer. Any target-specific initialization must live outside this minimal header.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/fuzz.h -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/meson.build -->
# sources/sync-backup/casync/test/fuzz/meson.build

Purpose: registers fuzz targets with the Meson build.

Important APIs/types/functions: defines executable targets for fuzzers, including linking the common runner or libFuzzer engine depending on build options.

Control flow/state: build-time only; conditional options decide whether fuzzers are regular executables or sanitizer/fuzzer artifacts.

Dependencies/integration: used by `oss-fuzz.sh` and Meson `fuzzers` target.

Risks/test signals: missing source/link dependencies can make fuzzers build but not exercise the intended code. OSS-Fuzz script is the integration check.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/fuzz/meson.build -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/http-server.py -->
# sources/sync-backup/casync/test/http-server.py

Purpose: starts a small HTTP server rooted at a supplied directory for remoting integration tests.

Important APIs/types/functions: parses directory and port arguments, changes/serves the requested root, sends readiness notification, and runs Python's HTTP server loop.

Control flow/state: process-level current directory and socket listener are the main state. Once ready, it stays foreground until killed by the test script.

Dependencies/integration: launched through `notify-wait` by `test-script.sh.in` to serve `.caidx` and `.catar` files over `http://localhost:PORT`.

Risks/test signals: port collisions, Python version differences, and cwd mutation are the main risks. The HTTP remoting section of `test-script.sh.in` validates it.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/http-server.py -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/meson-check-help.sh -->
# sources/sync-backup/casync/test/meson-check-help.sh

Purpose: smoke-tests command help output under Meson.

Important APIs/types/functions: shell script invokes built binaries with help/version-like arguments and expects successful output.

Control flow/state: no persistent state; exits nonzero on command failure under `set -e` style behavior.

Dependencies/integration: wired from `test/meson.build` as a lightweight test that catches missing binaries or broken option parsing.

Risks/test signals: only validates shallow CLI availability, not full behavior. It can be sensitive to builddir substitutions and executable paths.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/meson-check-help.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/meson.build -->
# sources/sync-backup/casync/test/meson.build

Purpose: registers casync tests with Meson.

Important APIs/types/functions: defines test executables and shell-script tests, linking them against `libshared` and using configured `.sh.in` scripts.

Control flow/state: build-time orchestration only. The file determines which C tests and integration scripts run under `meson test`.

Dependencies/integration: depends on source targets from `src/meson.build`, optional feature flags, and generated config substitutions.

Risks/test signals: if a test is omitted here, regressions in that area may be invisible to CI. Keeping the list synchronized with test files is the primary maintenance concern.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/meson.build -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/notify-wait.c -->
# sources/sync-backup/casync/test/notify-wait.c

Purpose: helper executable that runs a child command and prints its PID only after the child sends `READY=1` to a temporary notify socket.

Important APIs/types/functions: sets up abstract UNIX datagram socket, exports `NOTIFY_SOCKET`, forks/execs child, polls for datagrams, watches `SIGCHLD`, `SIGINT`, `SIGTERM`, and enforces a 30-second timeout.

Control flow/state: parent owns notification socket and child pid; child resets signal mask, redirects stdout away from the parent pipe, sets environment, and execs. Parent peeks datagram size, reads complete messages, searches for `READY=1`, then prints pid and leaves the child running.

Dependencies/integration: used by FUSE, NBD, and HTTP tests to avoid racing service startup. Depends on `time-util`, `util`, and log helpers.

Risks/test signals: signal handling and abstract socket encoding are subtle. A child that exits early or never notifies fails the test deterministically with diagnostics.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/notify-wait.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/pseudo-ssh -->
# sources/sync-backup/casync/test/pseudo-ssh

Purpose: minimal SSH replacement for local remoting tests.

Important APIs/types/functions: shell script shifts away the hostname-style argument and `exec`s the remaining command locally.

Control flow/state: no persistent state; process is replaced with the requested command.

Dependencies/integration: `test-script.sh.in` sets `CASYNC_SSH_PATH` to this script and `CASYNC_REMOTE_PATH` to the built casync binary to exercise SSH locator logic without real SSH.

Risks/test signals: only models command execution, not authentication, quoting, network I/O, or remote environment differences. It is appropriate for protocol path plumbing tests.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/pseudo-ssh -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/report-holes.py -->
# sources/sync-backup/casync/test/report-holes.py

Purpose: diagnostic helper for reporting sparse-file holes/extents.

Important APIs/types/functions: Python script uses seek-style filesystem APIs to walk data/hole regions and print a compact report for a file.

Control flow/state: reads file metadata without mutating it. Output depends on filesystem support for sparse extent reporting.

Dependencies/integration: useful with tests around `loop_write_with_holes`, archive extraction, and sparse file preservation.

Risks/test signals: not portable to filesystems or platforms lacking `SEEK_DATA`/`SEEK_HOLE`. Best used as a manual or conditional diagnostic rather than a strict universal test.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/report-holes.py -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/semaphore-run -->
# sources/sync-backup/casync/test/semaphore-run

Purpose: CI helper script for Semaphore-style builds.

Important APIs/types/functions: installs Meson/Ninja when needed, configures builds, runs tests, and includes a 32-bit build/test lane with GCC flags.

Control flow/state: mutates build directories, package/user Python environment, and test artifacts. It exits on failures to signal CI status.

Dependencies/integration: complements Meson and shell test scripts for hosted CI coverage.

Risks/test signals: depends on specific distro package names, Python/pip behavior, compiler availability, and i386 toolchain support. It is valuable for environment coverage but brittle outside CI.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/semaphore-run -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-cache.sh.in -->
# sources/sync-backup/casync/test/test-cache.sh.in

Purpose: integration test for cache/store behavior.

Important APIs/types/functions: configured shell script drives the built `casync` binary against scratch directories, cache paths, and generated archives/indexes.

Control flow/state: creates a temporary workspace, runs make/extract/cache operations, compares expected outputs, and removes scratch state.

Dependencies/integration: relies on top build/source substitutions, compressor/digest defaults, and standard shell tools.

Risks/test signals: validates end-to-end cache reuse but can be sensitive to filesystem permissions and cleanup failures. Nonzero diff or command failure is the main oracle.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-cache.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-cachunk.c -->
# sources/sync-backup/casync/test/test-cachunk.c

Purpose: unit-style test for chunk file read/write helpers.

Important APIs/types/functions: `test_chunk_file` generates random bytes, writes them to a temp fd, reads via `ca_chunk_file`, validates `ReallocBuffer` contents, rewrites via `ca_chunk_write`, tests digest/id behavior, and compares bytes.

Control flow/state: uses a temporary unlinked file and two `ReallocBuffer` instances. State is fully local and cleaned by fd close/buffer free.

Dependencies/integration: exercises chunking, digest, realloc-buffer, random, and tmp-dir utilities.

Risks/test signals: random content increases coverage but can make failures harder to reproduce without captured data. It validates full-buffer equality rather than only return codes.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-cachunk.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-cachunker-histogram.c -->
# sources/sync-backup/casync/test/test-cachunker-histogram.c

Purpose: stress/diagnostic test for content-defined chunk size distribution.

Important APIs/types/functions: worker `process` threads feed random data through `CaChunker`, `draw` prints histogram bars, `run` computes average chunk size for a pick value, and `main` scans parameters.

Control flow/state: opens `/dev/urandom`, spawns threads, each records chunk-size counts in a histogram, then joins and aggregates. Assertions enforce min/max chunk bounds.

Dependencies/integration: depends on pthreads, chunker internals, random input, and terminal output for diagnostics.

Risks/test signals: statistical tests can be noisy and environment-dependent. The hard assertions check bounds; histogram/average output helps tune chunker parameters.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-cachunker-histogram.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-cachunker.c -->
# sources/sync-backup/casync/test/test-cachunker.c

Purpose: unit test for rolling hash and chunk-size configuration behavior.

Important APIs/types/functions: `test_rolling` verifies rolling hash add/remove symmetry over a window, `test_chunk` checks chunk boundaries on random data stay within min/max limits, and `test_set_size` validates size presets/parsing.

Control flow/state: initializes `CaChunker`, reads random buffers, feeds data in chunks, and asserts invariants.

Dependencies/integration: covers `cachunker.h`, util assertions, `/dev/urandom`, and size parsing behavior.

Risks/test signals: random-data chunking may not hit every boundary case but should catch broken rolling hash/window logic quickly.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-cachunker.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-cadigest.c -->
# sources/sync-backup/casync/test/test-cadigest.c

Purpose: verifies digest implementations and known output vectors.

Important APIs/types/functions: `test_speed` benchmarks or exercises each digest type; `main` checks SHA-256 and SHA-512/256 byte-for-byte outputs after specific writes.

Control flow/state: allocates `CaDigest`, writes data incrementally, reads final digest, and compares to embedded expected byte arrays.

Dependencies/integration: covers digest type selection, reset/write/read/finalization, and configured crypto backends.

Risks/test signals: strong regression signal for digest correctness, though performance output is diagnostic. Backend availability can affect which digest types are tested.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-cadigest.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-caencoder.c -->
# sources/sync-backup/casync/test/test-caencoder.c

Purpose: end-to-end smoke test for archive encoder and decoder streaming APIs.

Important APIs/types/functions: `encode` drives `CaEncoder` steps, writes emitted archive bytes to a temp file, logs file transitions, and validates archive offset against fd position. `decode` drives `CaDecoder`, feeds bytes on request, and logs decoded file transitions.

Control flow/state: creates a temp archive under `/var/tmp`-style directory, encodes a base directory (argv or `.`), reopens the archive, decodes it, and unlinks the temp file.

Dependencies/integration: exercises caencoder/cadecoder/caformat, feature flags, base fd handling, temp utilities, and low-level I/O.

Risks/test signals: it validates streaming state machines but does not compare reconstructed filesystem output. Failures surface as negative errno or assertion failures during state transitions.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-caencoder.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-caformat.c -->
# sources/sync-backup/casync/test/test-caformat.c

Purpose: tests archive format encoding/decoding helpers and constants.

Important APIs/types/functions: main constructs format structures, validates magic/feature/digest serialization, and checks expected values through `assert_se`.

Control flow/state: local-only test with no persistent files. It exercises conversion helpers rather than full archive traversal.

Dependencies/integration: includes `caformat.h` and util assertions, providing a low-level guard for on-disk format compatibility.

Risks/test signals: important because format regressions can break existing archives. Coverage is limited to cases hard-coded in the test.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-caformat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-caindex.c -->
# sources/sync-backup/casync/test/test-caindex.c

Purpose: test utility for reading and dumping casync index entries.

Important APIs/types/functions: opens a `CaIndex` from argv path, repeatedly reads entries/locations, and prints or validates each result.

Control flow/state: creates a read-mode index object, sets path, opens it, loops until EOF, then exits. State is in the index reader.

Dependencies/integration: used manually or by scripts to inspect `.caidx` behavior. Depends on `caindex` and origin/location code.

Risks/test signals: requires an input index file, so it is less self-contained than unit tests. It is useful for detecting parser failures on generated indexes.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-caindex.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-calc-digest.c -->
# sources/sync-backup/casync/test/test-calc-digest.c

Purpose: command-line helper that calculates a selected casync digest over files/stdin.

Important APIs/types/functions: parses digest type argument, streams file bytes through `CaDigest`, and prints the resulting hex digest.

Control flow/state: opens each requested file or stdin, reads in blocks, updates digest, finalizes once input is exhausted.

Dependencies/integration: used by NBD/script tests to compare casync CLI digest output against library digest calculation.

Risks/test signals: a bug here can mask or falsely report digest regressions in shell tests, but known-vector `test-cadigest.c` provides an independent check.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-calc-digest.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-calocation.c -->
# sources/sync-backup/casync/test/test-calocation.c

Purpose: exercises location parsing, formatting, patching, advancing, merging, opening, and ID generation.

Important APIs/types/functions: main builds `CaLocation` objects from strings, checks fields and formatted output, advances offsets, merges adjacent locations, opens referenced data, and validates chunk ID behavior.

Control flow/state: uses reference-counted location objects and temporary/local paths as needed. Assertions provide the oracle.

Dependencies/integration: covers `calocation`, file-root, digest, and util code central to archive origin tracking.

Risks/test signals: location syntax is user-facing and remote-sensitive; this test is a key guard against parser/formatter drift.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-calocation.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-camakebst.c -->
# sources/sync-backup/casync/test/test-camakebst.c

Purpose: verifies construction of array layouts suitable for binary-search-tree access.

Important APIs/types/functions: `find_bst` searches the generated layout, `test_makebst_size` builds arrays for sizes and checks ordering/search invariants, and `main` runs sizes across a range.

Control flow/state: allocates local arrays, calls `ca_make_bst`, then asserts each expected value is findable and out-of-range values are absent.

Dependencies/integration: covers `camakebst`, which is used for efficient sorted table layouts.

Risks/test signals: catches off-by-one and tree-shape regressions across small and medium sizes. It does not benchmark lookup performance.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-camakebst.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-camatch.c -->
# sources/sync-backup/casync/test/test-camatch.c

Purpose: thorough unit test for include/exclude match tree parsing, normalization, subtree inheritance, and matching.

Important APIs/types/functions: builds a match tree from string patterns, asserts child names/types/anchoring/directory flags, normalizes, tests files/directories, checks returned subtrees, and uses `ca_match_equal`.

Control flow/state: creates reference-counted match trees with nested child structures. The test checks both structural parse output and behavioral matching results.

Dependencies/integration: covers `camatch`, glob/path matching, string vectors, and util assertions. It is one of the stronger semantic tests in this subset.

Risks/test signals: pattern order and subtree propagation are subtle; this test guards many edge cases but remains limited to hard-coded patterns.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-camatch.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-caorigin.c -->
# sources/sync-backup/casync/test/test-caorigin.c

Purpose: tests origin range collection behavior.

Important APIs/types/functions: creates several `CaLocation` objects, pushes them into `CaOrigin`, dumps state, advances bytes, concatenates origins with full and bounded lengths, and validates calls succeed.

Control flow/state: mutable `CaOrigin` holds ordered location spans and byte counts. Operations coalesce/advance/append while preserving location semantics.

Dependencies/integration: covers origin tracking used to map chunks back to source locations.

Risks/test signals: mostly asserts success and dumps diagnostics; it does not compare every intermediate structure against explicit expected values, so semantic coverage is moderate.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-caorigin.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-casync.c -->
# sources/sync-backup/casync/test/test-casync.c

Purpose: high-level library API test for `CaSync` encode/decode workflows.

Important APIs/types/functions: creates temp tree/store/index paths, runs encode with feature flags, base fd, archive digest, store path, and index path; then runs decode with the same store/index and validates archive digest retrieval.

Control flow/state: drives `ca_sync_step` state machine until finished, handling archive digest states and cleaning temporary index/store/tree with `rm_rf`.

Dependencies/integration: exercises core casync orchestration, store/index interaction, feature flags, digest reporting, and cleanup utilities.

Risks/test signals: strong end-to-end API signal, though the generated source tree is small. Failures identify state machine, file setup, or digest regressions.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-casync.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-cautil.c -->
# sources/sync-backup/casync/test/test-cautil.c

Purpose: unit tests locator utility functions.

Important APIs/types/functions: tests `ca_locator_has_suffix`, `ca_strip_file_url`, `ca_classify_locator`, and `ca_locator_patch_last_component` across path, file URL, HTTP URL, and SSH-like locator examples.

Control flow/state: pure string tests allocate/free patched strings and compare exact expected outputs.

Dependencies/integration: covers `cautil` functions used by CLI and remoting locator handling.

Risks/test signals: good guard for parsing edge cases involving query strings, localhost file URLs, and SSH colon syntax. It does not cover every URL escaping case.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-cautil.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-feature-flags.c -->
# sources/sync-backup/casync/test/test-feature-flags.c

Purpose: verifies feature flag name/string conversion and compatibility logic.

Important APIs/types/functions: iterates feature flag bits, converts to names and back, checks known/default flags, and verifies unknown or combined behavior.

Control flow/state: local arithmetic over `uint64_t` flags with assertions.

Dependencies/integration: covers `caformat-util` and `caformat` constants used to negotiate archive capabilities.

Risks/test signals: important because feature flags gate privileged metadata and compatibility. It may need updates whenever new feature bits are added.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-feature-flags.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-fuse.sh.in -->
# sources/sync-backup/casync/test/test-fuse.sh.in

Purpose: integration test for FUSE mounting of a casync index.

Important APIs/types/functions: creates a scratch source copy, computes digest, makes `.caidx`, extracts it, optionally loads FUSE and launches `casync mount` via `notify-wait`, then compares mounted digest.

Control flow/state: mutates scratch directory and optionally creates a live mount that is killed/unmounted at the end.

Dependencies/integration: requires built casync/notify-wait, FUSE support, `/dev/fuse`, and root for module loading in some environments.

Risks/test signals: environment-sensitive but valuable for mounted read path correctness. Cleanup must handle failed mount/kill paths carefully.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-fuse.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-nbd.sh.in -->
# sources/sync-backup/casync/test/test-nbd.sh.in

Purpose: integration test for NBD device export of a casync block index.

Important APIs/types/functions: generates random blob, compares casync digest with `test-calc-digest`, creates `.caibx`, extracts with and without seed, and optionally runs `casync mkdev` through `notify-wait` to read from `/dev/nbd0`-style node.

Control flow/state: scratch files and optional kernel NBD device state are created; helper process is killed after digest comparison.

Dependencies/integration: requires NBD kernel support/root for the device portion and built helper binaries.

Risks/test signals: strong coverage for block archive extraction and device serving, but often skipped or partial in unprivileged CI.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-nbd.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-script-gzip.sh.in -->
# sources/sync-backup/casync/test/test-script-gzip.sh.in

Purpose: compression variant wrapper for the main integration script.

Important APIs/types/functions: `exec @top_builddir@/test-script.sh default gzip`.

Control flow/state: replaces itself with the configured main script using default digest and gzip compression.

Dependencies/integration: relies on Meson substitution and `test-script.sh.in` availability. The main script skips gzip when libz is disabled.

Risks/test signals: useful for catching gzip-specific archive/store regressions while avoiding duplicate test logic.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-script-gzip.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-script-sha256.sh.in -->
# sources/sync-backup/casync/test/test-script-sha256.sh.in

Purpose: digest variant wrapper for the main integration script.

Important APIs/types/functions: executes `test-script.sh sha256` to force SHA-256 instead of the default digest.

Control flow/state: no local state; all work is delegated to the main integration script.

Dependencies/integration: targets remoting and archive paths that might accidentally assume SHA-512/256 digest sizes.

Risks/test signals: concise but important compatibility lane for alternate digest algorithms.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-script-sha256.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-script-xz.sh.in -->
# sources/sync-backup/casync/test/test-script-xz.sh.in

Purpose: compression variant wrapper for xz.

Important APIs/types/functions: `exec @top_builddir@/test-script.sh default xz`.

Control flow/state: delegates completely to the main integration script, preserving exit status.

Dependencies/integration: requires liblzma-enabled build; the delegated script exits 77 when xz support is unavailable.

Risks/test signals: catches xz compressor/decompressor integration regressions without duplicating the large script.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-script-xz.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-script.sh.in -->
# sources/sync-backup/casync/test/test-script.sh.in

Purpose: comprehensive end-to-end CLI integration test for casync archives, indexes, extraction, seeking, SSH remoting, and HTTP remoting across digest/compression variants.

Important APIs/types/functions: invokes `casync list`, `mtree`, `digest`, `make`, `extract`, remote locators, `test-calc-digest`, `notify-wait`, `pseudo-ssh`, and `http-server.py`. It compares outputs with `diff -q` and filesystem trees with `diff -ur --no-dereference`.

Control flow/state: creates scratch source tree from `test-files` and `src`, generates `.catar` and `.caidx`, verifies list/mtree/digest equivalence, extracts with/without seeds and hardlinks, tests path seeking into archives, serves remote paths over pseudo SSH and HTTP, then cleans scratch state.

Dependencies/integration: central CLI regression lane; depends on configured compressor libraries, builddir substitutions, shell tools, Python HTTP helper, and local filesystem semantics.

Risks/test signals: broad but environment-sensitive. It can miss metadata unsupported by the current user/filesystem, but it is the strongest single signal for cross-module behavior.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-script.sh.in -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/test/test-util.c -->
# sources/sync-backup/casync/test/test-util.c

Purpose: directly tests low-level sparse write/read helpers.

Important APIs/types/functions: builds a buffer with zero and nonzero regions, writes it through `loop_write_with_holes`, checks punched byte counts, reads back with `loop_read`, tests an unaligned zero run, and verifies pipe behavior where hole punching must not occur.

Control flow/state: uses temp unlinked file and pipe fds; all assertions are local and deterministic except filesystem punch-hole support.

Dependencies/integration: covers `util.c` sparse I/O functions that archive extraction relies on for efficient sparse files.

Risks/test signals: expected punched count assumes hole punching succeeds for the temp filesystem; pipe subtest guards fallback behavior.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/test/test-util.c -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/tools/oss-fuzz.sh -->
# sources/sync-backup/casync/tools/oss-fuzz.sh

Purpose: build script for producing OSS-Fuzz-compatible casync fuzzing artifacts.

Important APIs/types/functions: configures clang/sanitizer flags, detects clang runtime library path, sets `WORK`/`OUT`, configures Meson with `oss-fuzz` or `llvm-fuzz`, disables some optional libs/manpages, runs `ninja fuzzers`, packages seed corpora, and moves `fuzz-*` executables to `$OUT`.

Control flow/state: deletes/recreates `$WORK/build`, writes artifacts under `$OUT`, and zips corpus directories named after fuzzers.

Dependencies/integration: used by OSS-Fuzz infrastructure and local sanitizer builds; depends on Meson, Ninja, clang, zip, and fuzz Meson targets.

Risks/test signals: sanitizer flag or clang library path drift can break fuzz builds. Disabling compression libraries narrows fuzz coverage unless separate jobs enable them.

<!-- END_FILE_RESEARCH: sources/sync-backup/casync/tools/oss-fuzz.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/.appveyor.yml -->
# sources/sync-backup/git-annex/.appveyor.yml

Purpose: AppVeyor CI configuration for git-annex across Windows and macOS, with optional Linux notes disabled.

Important APIs/types/functions: defines clone depth, build matrix, cache paths, RDP/SSH debug setup, Stack installation, dependency build with `-O0`, binary build/copy, platform-specific test commands, and finish hooks that can block for debugging via `BLOCK` files.

Control flow/state: CI phases mutate registry long-path setting on Windows, install Stack, create `stack.yaml.build`, cache Stack directories, build dependencies and binaries, symlink commands on Unix, then run `git-annex test`.

Dependencies/integration: integrates git-annex with AppVeyor images, Stack, PowerShell/cmd/sh steps, remote debug scripts, and project-level secrets for SSH/RDP.

Risks/test signals: downloads remote scripts during CI, relies on image names and Stack bootstrap behavior, and skips docs-only commits. It is a CI orchestration signal rather than runtime code.

<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/.appveyor.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Build/collect-ghc-options.sh -->
# sources/sync-backup/git-annex/Build/collect-ghc-options.sh

Purpose: translates conventional C toolchain flags into GHC option flags so Haskell builds pass them through to linker/compiler/preprocessor stages.

Important APIs/types/functions: loops over `$LDFLAGS` emitting `-optl...`, `$CFLAGS` emitting `-optc...`, and `$CPPFLAGS` emitting `-optc-Wp,...`.

Control flow/state: pure stdout generator; no files are mutated. Word splitting follows shell whitespace semantics.

Dependencies/integration: used by the git-annex Makefile during cabal configure as `--ghc-options="$(shell Build/collect-ghc-options.sh)"`.

Risks/test signals: flags containing spaces or shell-sensitive quoting can be split incorrectly. Build failures in environments with custom flags are the primary signal.

<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Build/collect-ghc-options.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Build/mdwn2man -->
# sources/sync-backup/git-annex/Build/mdwn2man

Purpose: quick Perl converter from ikiwiki-style markdown snippets to manpage roff.

Important APIs/types/functions: reads stdin, prints `.TH`, rewrites wiki links, inline backticks, headings, paragraphs, list items, hyphens, escaped dots, NAME section command names, and quote escapes.

Control flow/state: line-oriented filter with state flags for list context, paragraph skipping, and NAME section handling. It intentionally uses simple regex transformations rather than a full Markdown parser.

Dependencies/integration: part of git-annex documentation/manpage build tooling.

Risks/test signals: labeled as a hack; complex markdown can render incorrectly. Manpage generation and `lexgrog`-style NAME validation are the likely regression signals.

<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Build/mdwn2man -->


<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Makefile -->
# sources/sync-backup/git-annex/Makefile

Purpose: top-level git-annex build, install, test, documentation, clean, and packaging orchestration.

Important APIs/types/functions: targets include `build`, `install`, `install-home`, `build-dependencies`, `tmp/configure-stamp`, `dev`, `prof`, executable symlink targets, `install-*`, `test`, `retest`, `tags`, `mans`, `docs`, `clean`, standalone Linux packaging, Debian standalone packaging, OS X app packaging, and `distributionupdate`.

Control flow/state: chooses `cabal` by default or `stack` when requested, configures once into `tmp/configure-stamp`, builds `git-annex`, links related command names to the main binary, installs docs/completions, and generates platform packages under `tmp`. Several targets patch or reset packaging state using quilt/git commands.

Dependencies/integration: integrates Cabal/Stack/GHC, ikiwiki, rsync, hasktags, Debian packaging tools, hdiutil/install_name_tool on macOS, and helper Haskell builders under `Build/`.

Risks/test signals: large orchestration blast radius; environment differences in Cabal layouts, Stack dist dirs, docs tools, or packaging tools can break targets. `make test` and CI configs provide the main validation path.

<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Makefile -->

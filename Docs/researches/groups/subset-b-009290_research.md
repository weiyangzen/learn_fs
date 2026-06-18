# Research Report: subset-b-009290

This grouped report covers the LTP `fs/doio` sources assigned to `subset-b-009290`. Each section preserves the source path and is wrapped for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/doio.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/doio.c

Purpose: `doio.c` is the binary request consumer and I/O executor for the LTP/SGI doio filesystem stress tools. It reads fixed-size `struct io_req` records, validates their magic value, forks worker processes when requested, and dispatches each request to the selected file, vector, mmap, async, listio, sync, or platform-specific fcntl/SDS path. Its main testing value is that request generation can be separated from request execution while preserving detailed failure diagnostics and optional write logging.

Important APIs, types, and globals: the file depends on `doio.h` request types, `write_log.h` write-log records, `pattern.h` fill/check helpers, `string_to_tokens.h`, and `tso_random_range.h`. Internal state is centered on `struct memalloc`, `struct fd_cache`, `struct aio_info`, `struct status`, and `struct syscall_info`. Important globals include `Memalloc`, `Memptr`, `Memsize`, `Aio_Info`, `Wlog`, `Pattern`, `Pattern_Length`, `Reqno`, `Nprocs`, `Children`, option flags such as `v_opt`, `w_opt`, `k_opt`, and platform switches for CRAY, SGI, and generic Linux/POSIX builds.

Control flow: `main()` parses options, optionally initializes/truncates a write log, forks `Nprocs` children, and acts as a watchdog that folds child exit statuses into doio exit bits. Child execution enters `doio()`, installs cleanup and diagnostic signal handlers, opens the binary request input stream, then repeatedly reads exactly one `struct io_req`. Requests are rejected on short reads or bad magic, resource caches can be periodically released by `-r`, and dispatch is by `r_type`: simple `READ`/`WRITE`, extended `do_rw()` table-driven operations, CRAY listio/SDS, SGI fcntl reservations, or POSIX `fsync`/`fdatasync`.

Operation implementation: `do_read()` and `do_write()` handle legacy synchronous and CRAY async read/write. `do_rw()` generalizes dispatch through the `syscalls[]` table for `readv`, `writev`, mmap read/write, and SGI `pread`/`pwrite`/aio when enabled. Each write fills an aligned or deliberately unaligned buffer, optionally locks the target extent, optionally records a preliminary write-log entry with `w_done = 0`, performs the I/O, validates return counts or async completion status, optionally verifies file contents with `check_file()`, then records completion with `w_done = 1` and unlocks.

State and persistence behavior: memory allocation persists across requests and can rotate among heap, SysV shared memory, and mmap-backed allocations via `-M`; `alloc_mem(-1)` releases all tracked buffers. `alloc_fdcache()` persists open descriptors by file and open flags, closes the oldest cached descriptor on `EMFILE`, and keeps mmap mappings in cache slots for mmap I/O. Write logs persist to the file named by `-w` and are designed to support crash/interruption reconstruction. AIO slots persist while an operation is outstanding and carry signal/callback state until `aio_unregister()`.

Dependencies and integration points: the input contract is the exact C layout in `doio.h`, generally produced by companion generators such as `iogen`. `write_log` integration is shared with corruption checking tools. Pattern validation integrates through `pattern_fill()` and `pattern_check()`. Platform-specific branches preserve legacy CRAY/IRIX coverage while generic Linux builds primarily exercise `read`, `write`, `readv`, `writev`, `mmap`, `fsync`, `fdatasync`, memory allocation, locking, and signal cleanup paths.

Risks: the code is intentionally old and highly conditional, so some branches are compile-only on modern Linux. Static formatting buffers, many globals, and signal-handler cleanup make reentrancy poor. Request structs use `int` offsets and byte counts, which limits large-file precision in this executor despite some large-file-aware consumers elsewhere. `format_oflags()` allocates strings without freeing in diagnostic paths. `alloc_fdcache()` copies filenames into fixed `MAX_FNAME_LENGTH + 1` storage. The mmap path can fault on truncation, handled only by heuristic SIGBUS cleanup.

Test signals: passing behavior is mostly absence of setup, return-count, iosw/aio, data-compare, signal, or child-watchdog failures. Strong signals include correct `E_NORMAL` child exits, accurate write-log completion records, expected `E_COMPARE` on injected corruption, successful `-v` readback after writes, correct handling of descriptor pressure, and no leaked shared memory or mmap files after `SIGINT` cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/doio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/doio.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/doio.h

Purpose: `doio.h` defines the binary protocol consumed by `doio.c` and produced by companion I/O generators. It assigns numeric request IDs for legacy, platform-specific, and POSIX-like I/O operations and defines the packed request structures that are read directly from an input stream.

Important APIs and types: the header exports request type constants such as `READ`, `WRITE`, `READA`, `WRITEA`, `LISTIO`, listio variants, `PREAD`, `PWRITE`, `READV`, `WRITEV`, `AREAD`, `AWRITE`, `MMAPR`, `MMAPW`, `RESVSP`, `UNRESVSP`, `FSYNC2`, `FDATASYNC`, and `BIOSIZE`. It defines `DOIO_MAGIC`, user flag `F_WORD_ALIGNED`, exit-status bits `E_NORMAL` through `E_SIGNAL`, async completion strategies `A_POLL` through `A_CALLBACK`, `MAX_FNAME_LENGTH`, and the request structs `read_req`, `write_req`, `ssread_req`, `sswrite_req`, `listio_req`, and `io_req`.

Control flow role: the header has no runtime control flow, but its field layout drives the executor. `doio.c` relies on `r_file`, `r_oflags`, `r_offset`, and `r_nbytes` occupying matching positions in the read/write/list-compatible structures, and `r_pattern` matching between write-shaped requests. `struct io_req` wraps a `r_type`, `r_magic`, and union so the executor can switch by type while sharing field access through `r_data.io`.

State and persistence behavior: requests are intended to be serialized as raw C structs, so the ABI is persistent across producer and consumer processes rather than across heterogeneous machines. `r_magic` is the only embedded validation marker. File names are stored inline with a fixed 128-byte maximum, and offsets/counts are `int`, making the request format compact but not fully large-file neutral.

Dependencies and integration points: every tool that generates or consumes doio work must include or faithfully mirror this header. It integrates directly with `doio.c` dispatch tables and indirectly with write-log and corruption-checking tools through shared assumptions about file paths, offsets, lengths, and write patterns.

Risks: raw struct serialization is sensitive to compiler ABI, endian, padding, and field-size differences. The header has no include guard in the displayed source, so multiple inclusion relies on build discipline. Some constants are for CRAY/IRIX-only system calls and may be unsupported on modern Linux. The comment notes a critical layout invariant; changing any request field order can silently corrupt execution.

Test signals: useful validation is cross-tool round-trip generation of `struct io_req`, rejection of bad `DOIO_MAGIC`, and successful dispatch of each request type supported by the target build. Compile failures or request-size mismatches are strong indicators that producer and consumer are no longer ABI-compatible.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/doio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/file_lock.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/file_lock.c

Purpose: `file_lock.c` provides small retrying wrappers around `fcntl()` record locks for the doio and growfiles stress programs. It supports whole-file locks and explicit byte-range locks, normalizing the lock flag interface used by the legacy tests.

Important APIs and types: public functions are `file_lock(int fd, int flags, char **errormsg)` and `record_lock(int fd, int flags, int start, int len, char **errormsg)`. The module exports `Fl_syscall_str[128]`, a diagnostic string describing the most recent `fcntl()` call, and uses an internal static `errmsg[256]`. It consumes `LOCK_NB`, `LOCK_UN`, `LOCK_EX`, and `LOCK_SH` from `file_lock.h` or system headers.

Control flow: both functions zero a `struct flock`, choose `F_SETLK` for nonblocking locks or `F_SETLKW` for blocking locks, set `l_whence = 0`, and select `F_UNLCK`, `F_WRLCK`, or `F_RDLCK` from the caller flags. `file_lock()` uses `l_start = 0` and `l_len = 0` for the whole file; `record_lock()` uses caller-supplied `start` and `len`. Invalid lock mode flags set `errno = EINVAL`, populate `errormsg`, and return `-1`.

State and persistence behavior: locks persist in the kernel according to normal POSIX advisory-lock semantics and are released by unlock calls, descriptor close, or process exit. User-visible module state is limited to `Fl_syscall_str` and the static error buffer; both are overwritten by each call and are not thread-safe.

Dependencies and integration points: `growfiles.c` calls `file_lock()` through `lkfile()` for optional lock levels around write/read/truncate cycles or entire open/close windows. `doio.c` implements its own local region-lock helper rather than using this file. The wrappers depend on `fcntl` behavior and platform errno values, including optional legacy `EFILESH` and local fallback `EFSEXCLWR`.

Risks: retry behavior is surprising: for `F_SETLK`, several errors including `EACCES` and `EINTR` are retried indefinitely, which can spin rather than returning a nonblocking failure. The comment says it loops when `LOCK_NB` is not set, but the retry switch is under `cmd == F_SETLK`; that mismatch is a maintenance hazard. Error strings use fixed buffers and `sprintf`. The functions accept inconsistent flag combinations without checking for multiple lock mode bits beyond first-match ordering.

Test signals: useful checks include exclusive/shared/unlock success across cooperating processes, range-lock conflict behavior, invalid flag rejection with `EINVAL`, and interruption behavior. Stress tests should monitor for CPU spin when nonblocking locks encounter persistent `EACCES` or protected-file errors.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/file_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/forker.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/forker.c

Purpose: `forker.c` supplies process fan-out helpers used by filesystem stress programs. `background()` detaches the caller by forking and letting the parent exit. `forker()` creates a requested number of copies of the current process using either a flat parent-with-many-children shape or a chained child-of-child shape.

Important APIs and types: exported globals are `Forker_pids[FORKER_MAX_PIDS]` and `Forker_npids`. Public functions are `background(char *prefix)` and `forker(int ncopies, int mode, char *prefix)`. The file uses `fork()`, `getpid()`, `exit()`, and stderr diagnostics with `errno`/`strerror()`. A `UNIT_TEST` main can be compiled to exercise both helpers manually.

Control flow: `background()` calls `fork()`: failure prints an optional prefixed message and exits with `errno`; the parent exits zero; the child returns zero. `forker()` loops from one to `ncopies - 1`. In mode 1, each process forks one child; the parent returns immediately and only the child continues the loop. In default mode, the original parent keeps forking and each child returns immediately. Each successful fork increments `Forker_npids` and stores either the child pid or current child pid while capacity remains.

State and persistence behavior: pid state is process-local after forks. Different processes see different snapshots of `Forker_pids`; comments explicitly warn that only some processes know all child pids depending on mode. The fixed array stores at most `FORKER_MAX_PIDS` entries, while `Forker_npids` can continue to grow past the number of stored pids. `background()` intentionally orphans the continuing child.

Dependencies and integration points: `growfiles.c` uses `background()` for default asynchronous launch and `forker()` for `-n` multiple-copy stress. `notify_others()` in `growfiles.c` uses `Forker_pids` and `Forker_npids` to propagate `SIGUSR2` when synchronized stopping is requested. `forker.h` declares the shared interface.

Risks: there is no wait/reap logic here, so callers must own process lifecycle. The fixed pid array can truncate stored pids for very high copy counts. Return values differ by process and mode, so callers must not interpret them as a single global count without understanding the topology. Failure returns can be partial and do not clean up already-forked children.

Test signals: useful signals include expected process counts in flat and chained modes, parent exit after `background()`, correct pid array population for small `ncopies`, graceful failure on fork limits, and successful signal fan-out from callers that rely on `Forker_pids`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/forker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/growfiles.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/growfiles.c

Purpose: `growfiles.c` is a standalone LTP filesystem stress test that repeatedly opens one or more files, grows them by writes or lseek-created holes, verifies recent writes and optional whole-file contents, optionally truncates or unlinks them, and repeats until iteration, time, byte, error, or filesystem-space limits stop the run. It can fork multiple copies and coordinate failure shutdown across those copies.

Important APIs, types, and globals: the file integrates `dataascii`, `databin`, `datapid*`, `open_flags`, `forker`, `file_lock`, `tso_random_range`, `tso_lio`, and LTP `test.h`. Key functions are `main()`, `set_sig()`, `sig_handler()`, `notify_others()`, `handle_error()`, `cleanup()`, `growfile()`, `shrinkfile()`, `check_write()`, `check_file()`, `file_size()`, `lkfile()`, and non-Linux `pre_alloc()`. Global knobs track pattern type, random seeds, open flags, locking level, current write offset `Woffset`, last write size `Grow_incr`, mode bits, buffer alignment, filenames, byte consumption, iteration count, and LTP test identity.

Control flow: `main()` parses a large option set, chooses patterns and randomization, installs signal handlers, optionally backgrounds, forks copies, possibly re-execs children, builds command-line and auto-generated filename arrays, allocates the write buffer, calculates filesystem-space limits, and enters the iteration loop. Each file pass chooses open flags, opens the file, optionally locks at level 1, optionally preallocates, checks size against a per-file filesystem limit, calls `growfile()`, conditionally calls `check_write()` and `check_file()`, conditionally calls `shrinkfile()`, unlocks/closes, optionally unlinks, and applies busy-wait delay.

Write and validation behavior: `growfile()` detects FIFOs, chooses random size and/or offset when configured, handles `O_APPEND`, writes either a generated pattern buffer or a single `w` after seeking beyond EOF, updates `Woffset`, `Grow_incr`, current size, and `bytes_consumed`, and detects races that move the file offset. Patterns include ASCII, pid/offset words, fixed offset words, alternating bits, checkerboard, counting, all ones, zeros, and random data. `check_write()` validates the last write unless it was truncated away. `check_file()` validates the whole file in one read or `MAX_FC_READ` chunks when whole-file checking is meaningful.

State and persistence behavior: file contents, sizes, holes, truncations, and unlinks are the persistent state under test. Runtime state is global and process-local after forks. `Forker_pids` enables cross-process stop notification when `-y` is active. Random seeds can be shared or per-process. `remove_files` controls cleanup unlinking at exit, while `unlink_inter` can remove files during the test. `myexit()` maps process exit status into LTP `TPASS`/`TFAIL` before `tst_exit()`.

Dependencies and integration points: I/O is funneled through `lio_write_buffer()` and `lio_read_buffer()` when `NEWIO` is enabled, so the same test can stress sync, async, listio, and random I/O types. File locking delegates to `file_lock.c`; process creation delegates to `forker.c`; open-flag parsing/formatting delegates to open flag helpers; data generation and checking delegate to `dataascii`, `databin`, and datapid helpers. LTP harness integration occurs through `TCID`, `TST_TOTAL`, `tst_resm()`, and `tst_exit()`.

Risks: this program intentionally creates races with truncation, append, random offsets, and multiple writers, so some validation is disabled for modes where deterministic content cannot be inferred. Many counters and offsets are `int` even where `off_t` or `unsigned long` is also used, which is risky for large files. `filenames` cleanup loops through `ind <= num_files`, one past the allocated count. Buffer alignment adjusts the returned pointer and loses the original malloc pointer. Busy-wait delays can consume CPU. The global `Mode` keeps FIFO state once any file is a FIFO, potentially affecting later files.

Test signals: success is LTP `TPASS` with zero accumulated `Errors`. Failures show as write/read length mismatches, pattern mismatches, lock failures, open/stat/truncate failures, early `Maxerrs`, `ENOSPC` exit paths, or signal-driven cleanup. Strong coverage comes from running matrices over patterns, random size/offset, lock levels, multiple processes, open-flag sets, whole-file and last-write validation intervals, and unlink/truncate schedules.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/growfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/bytes_by_prefix.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/bytes_by_prefix.h

Purpose: `bytes_by_prefix.h` declares helpers that convert strings with byte-size prefixes into integer byte counts. The doio suite uses this style of helper for command-line size parsing across stress tools.

Important APIs and types: the header declares `bytes_by_prefix(char *)`, `lbytes_by_prefix(char *)`, and `llbytes_by_prefix(char *)`, returning `int`, `long`, and `long long` respectively. There are no structs or constants beyond the `_BYTES_BY_PREFIX_` include guard.

Control flow: no control flow is implemented here. Callers pass a mutable or immutable C string and receive a scaled byte count from the implementation in another source file.

State and persistence behavior: the interface suggests pure conversion with no persistent state. Any overflow behavior depends on the implementation and chosen return width.

Dependencies and integration points: this header is an integration point for utilities that accept human-sized byte arguments. It is independent of doio request structs but fits the same test-tool support layer.

Risks: the prototypes do not use `const char *`, so callers may assume the implementation mutates input. Width-specific return types can overflow silently if the implementation does not validate bounds. The header does not document accepted suffixes, base, or error signaling.

Test signals: coverage should include plain numbers, supported prefix suffixes, invalid suffixes, negative values if allowed, and boundary values for each return type.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/bytes_by_prefix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/dataascii.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/dataascii.h

Purpose: `dataascii.h` declares ASCII pattern generation and validation helpers used by growfiles-style tests. The pattern is offset-based so multiple writers can independently produce deterministic data for the same file position.

Important APIs and types: `dataasciigen(char *listofchars, char *buffer, int size, int offset)` fills a buffer and returns the number of characters written. `dataasciichk(char *listofchars, char *buffer, int size, int count, char **errmsg)` validates a buffer and returns a nonnegative error position or a negative success value. There are no exported data types.

Control flow: no implementation is present, but the documented algorithm chooses each character by taking a count or offset modulo the character list length. `listofchars == NULL` selects a default character array in the implementation.

State and persistence behavior: generated bytes are deterministic from character list, size, and starting offset. That makes file contents checkable after concurrent writers as long as all writers use the same pattern rules and write at known offsets.

Dependencies and integration points: `growfiles.c` uses these declarations for `PATTERN_ASCII` in `growfile()`, `check_write()`, and `check_file()`. ASCII patterns are the default on non-CRAY builds because they are readable and multi-writer friendly.

Risks: offsets and sizes are `int`, so very large files can exceed the documented arithmetic range. The checker reports through a caller-provided `char **errmsg`, whose lifetime depends on the implementation. If callers use different character lists for generation and checking, all comparisons fail.

Test signals: useful tests generate buffers at several offsets, validate matching and deliberately corrupted buffers, exercise custom character lists, and verify that adjacent writers produce the same expected byte for the same absolute file offset.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/dataascii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/databin.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/databin.h

Purpose: `databin.h` declares binary pattern generation and validation helpers for growfiles stress modes that are not simple ASCII or pid/offset word formats. These modes give the filesystem tests compact ways to fill buffers with deterministic bit patterns.

Important APIs and types: `databingen(int mode, char *buffer, int bsize, int offset)` fills a buffer. `databinchk(int mode, char *buffer, int bsize, int offset, char **errmsg)` validates a buffer and reports mismatch details. Documented modes are `'a'` alternating bits, `'c'` checkerboard, `'C'` counting, `'o'` all ones, `'z'` zeros, and `'r'` random integers.

Control flow: this header has declarations only. The comments state that every mode except random is file-offset based, allowing multiple writers to generate compatible content for the same byte ranges.

State and persistence behavior: deterministic modes persist in file data and can be verified later from mode plus offset. Random mode is explicitly not checkable by the same deterministic mechanism and causes `growfiles.c` to disable file checking.

Dependencies and integration points: `growfiles.c` calls `databingen()` for binary patterns in `growfile()` and `databinchk()` in both last-write and whole-file checks. It is part of the pattern abstraction beside `dataascii` and datapid helpers.

Risks: `mode` is an untyped integer/character with no enum, so invalid modes are possible. The API does not document return values for generation and only loosely documents checker error semantics. Offset/count width is `int`.

Test signals: tests should cover each deterministic mode at nonzero offsets, corruption reporting, random generation being excluded from validation, and boundary sizes that are not aligned to the implementation's natural word size.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/databin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/file_lock.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/file_lock.h

Purpose: `file_lock.h` declares the doio suite's file-lock wrapper API and provides fallback lock flag definitions on platforms that do not expose BSD-style `LOCK_*` constants in the expected headers.

Important APIs and types: it exports `extern char Fl_syscall_str[128]`, `file_lock(int, int, char **)`, and `record_lock(int, int, int, int, char **)`. On Sun and HP-UX builds it defines `LOCK_NB`, `LOCK_UN`, `LOCK_EX`, and `LOCK_SH`.

Control flow: the header has no implementation. It is consumed by callers that request whole-file or byte-range advisory locks and receive `0`/`-1` style status plus optional error text.

State and persistence behavior: `Fl_syscall_str` is shared process-global diagnostic state from the implementation. Actual lock persistence is kernel state tied to process/file descriptor semantics.

Dependencies and integration points: `file_lock.c` implements the declarations, and `growfiles.c` uses `file_lock()` through its `lkfile()` helper. The API abstracts the suite away from direct `struct flock` construction for common lock cases.

Risks: fallback constants are only defined for selected platforms; other systems must already provide compatible `LOCK_*` values. `char **` error output has no const qualifier or ownership annotation. `Fl_syscall_str` is mutable global state and not thread-safe.

Test signals: compile-time coverage should verify constants resolve on target platforms. Runtime coverage should check exclusive, shared, unlock, nonblocking, range, and invalid flag paths through the implementation.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/file_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/forker.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/forker.h

Purpose: `forker.h` declares process-backgrounding and process-copy helpers used by the doio filesystem stress programs. It also exposes the global pid table that callers can use for later coordination.

Important APIs and types: `FORKER_MAX_PIDS` is 4098. `Forker_pids` stores forked process ids and `Forker_npids` stores the number of pid entries known to the current process. Public functions are `background(char *)` and `forker(int, int, char *)`.

Control flow: no implementation is present, but comments define `background()` as parent-exits/child-continues detachment. `forker()` creates `ncopies - 1` additional processes; mode 0 creates first-generation children and mode 1 creates a descendant chain.

State and persistence behavior: pid arrays are copied by fork and then diverge per process. Consumers must account for incomplete pid knowledge in some process topologies. Process state persists outside the caller until normal process exit or explicit signaling by the test.

Dependencies and integration points: `forker.c` implements the API. `growfiles.c` uses it for `-b`/background default behavior, `-n` multiple workers, and optional synchronized stop notification.

Risks: exposed globals invite callers to depend on process-local snapshots. The fixed pid table can truncate for high fan-out. The API cannot express child reaping or cleanup responsibilities.

Test signals: callers should validate process counts, mode-specific parent/child return values, and whether enough pids are available for signal fan-out in the intended topology.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/forker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/open_flags.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/open_flags.h

Purpose: `open_flags.h` declares helpers that convert between numeric `open(2)` flag bitmasks and symbolic comma-separated names. The doio tools use these helpers for command-line parsing and diagnostics.

Important APIs and types: `openflags2symbols(int openflags, char *sep, int mode)` formats recognized flag bits into a caller-specified separator style and can append `UNKNOWN` when requested. `parse_open_flags(char *string, char **badname)` parses comma-separated symbols into an `open()` bitmask and reports the location of an invalid token.

Control flow: implementation is external. The documented parser leaves the input string unchanged and returns `-1` on invalid symbols. The formatter recognizes a finite table of known flags that must be updated as platforms add new flags.

State and persistence behavior: no persistent state is declared. Output string ownership is not documented in the header, so callers must inspect the implementation before freeing or reusing returned storage.

Dependencies and integration points: `growfiles.c` uses `parse_open_flags()` for `-o` and `openflags2symbols()` in debug and error messages. `doio.c` has its own local `format_oflags()` instead of using this header.

Risks: platform flag drift can cause valid modern flags to be reported as unknown or rejected. The parser's signal-safety warning notes that a signal during parsing could leave a null byte in the middle of the input string, which implies implementation-level tokenization risk. Lack of const qualifiers makes caller mutation concerns ambiguous.

Test signals: coverage should parse all documented open flags, reject bad tokens with a useful `badname`, format compound masks with several separators, and verify behavior for unknown high bits.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/open_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/pattern.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/pattern.h

Purpose: `pattern.h` declares efficient repeated-pattern fill and check primitives. `doio.c` uses them as the default data generator and corruption detector for write verification.

Important APIs and types: `pattern_check(char *buf, int buflen, char *pat, int patlen, int patshift)` validates that a buffer contains repeated copies of a pattern rotated by `patshift`. `pattern_fill(char *buf, int buflen, char *pat, int patlen, int patshift)` fills a buffer with that repeated, shifted pattern. No structs or globals are exported.

Control flow: implementation is external, but comments describe a doubling-style algorithm: seed the first pattern-length region, then compare or copy increasingly larger already-validated/generated regions rather than walking byte by byte. Partial trailing patterns are supported for fills.

State and persistence behavior: the functions are deterministic and stateless. Persistent state is the generated bytes in caller buffers or files. `patshift` allows callers to validate file slices that begin in the middle of a repeated pattern.

Dependencies and integration points: `doio.c` wraps these functions in `doio_pat_fill()` and `doio_pat_check()`. They are central to `-v` verification and detailed corruption reporting in `check_file()`.

Risks: the comment for `pattern_check()` says shifts greater than the pattern length rotate by `(patshift % patshift)`, which is likely a documentation typo for `% patlen`. The API performs no argument validation according to comments, so null pointers, zero pattern length, and negative lengths are caller bugs. Integer sizes limit very large buffers.

Test signals: tests should include exact multiples, partial trailing pattern, nonzero shifts, shifts greater than pattern length, one-byte patterns, mismatch position reporting, and invalid argument behavior if the implementation defines any.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/pattern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/string_to_tokens.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/string_to_tokens.h

Purpose: `string_to_tokens.h` declares a small tokenization helper used by doio command-line parsing for comma-separated and colon-separated option subfields.

Important APIs and types: `string_to_tokens(char *arg_string, char **arg_array, int max_args, char *separator)` parses a string, stores token pointers in `arg_array`, and null-terminates the array. There are no exported structs or globals.

Control flow: the implementation uses `strtok()` according to the comment. That means parsing walks separators, replaces them with `'\0'`, and returns pointers into the original buffer.

State and persistence behavior: token state is stored by mutating the caller's input string. Because `strtok()` has hidden process-global parsing state, the helper is not reentrant or thread-safe unless the implementation avoids nested calls.

Dependencies and integration points: `doio.c` uses it in `parse_cmdline()` for `-M` memory allocation lists, in `parse_memalloc()` for `:`-separated allocation descriptors, and in `parse_delay()` for delay descriptors.

Risks: callers must pass mutable storage, not string literals. Nested tokenization can be fragile because `strtok()` keeps static state; the current doio use tokenizes one sub-string at a time but future nested use could break. The header does not define truncation behavior when token count exceeds `max_args`.

Test signals: useful checks include empty fields, repeated separators, maximum-token boundaries, different separator strings, mutation of input, and null termination of the output array.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/string_to_tokens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/write_log.h -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/include/write_log.h

Purpose: `write_log.h` defines the write-log record format and API used by `doio.c` to persist enough metadata for later corruption reconstruction and backward scanning. It separates an in-memory user record from a compact on-disk bitfield record plus variable-length path, host, and pattern data.

Important APIs and types: constants include `WLOG_MAX_PATH`, `WLOG_MAX_PATTERN`, `WLOG_MAX_HOST`, `WLOG_REC_MAX_SIZE`, `WLOG_STOP_SCAN`, and `WLOG_CONTINUE_SCAN`. `struct wlog_rec` is the caller-facing record with pid, offset, byte count, open flags, completion flag, async flag, host, path, and pattern fields plus lengths. `struct wlog_rec_disk` is the packed on-disk header with bitfields. `struct wlog_file` carries append and random-access file descriptors plus the log path. Public functions are `wlog_open()`, `wlog_close()`, `wlog_record_write()`, and `wlog_scan_backward()`, with `Wlog_Error_String` exported for diagnostics.

Control flow role: the header has no implementation, but it defines the protocol used by `doio.c`: append a preliminary record before a write with `w_done = 0`, then rewrite or append completion information after the write with `w_done = 1` at the saved log offset. Backward scans use the two-byte record length stored at the end of each on-disk record.

State and persistence behavior: write logs are durable files. Each on-disk record stores fixed metadata, variable path/host/pattern bytes without null terminators, and a trailing two-byte total length to support reverse traversal. `struct wlog_file` persists open descriptors while logging or scanning. The path, host, and pattern maximums bound record size and must remain synchronized with bitfield widths.

Dependencies and integration points: `doio.c` uses the API when `-w` is enabled. Comments reference `doio_check`, which reconstructs file extents and distinguishes completed from uncertain writes by `w_done`. The format is also platform-sensitive through CRAY vs non-CRAY offset bit widths.

Risks: bitfield layout, width, and endian behavior are compiler/platform sensitive, so log files are not a robust cross-architecture interchange format. The non-CRAY disk offset bitfield is 32 bits, limiting logged offsets. `uint` is defined as a macro if absent, which can conflict with other headers. Size constants require manual synchronization with bit widths. Fixed host/path/pattern limits can truncate or reject long metadata depending on implementation.

Test signals: coverage should create/truncate/open logs, record incomplete and complete writes, scan backward across multiple records, validate maximum path/host/pattern lengths, and confirm `doio_check` can interpret both completed and interrupted write records.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/include/write_log.h -->

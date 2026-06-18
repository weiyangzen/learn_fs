# Research: subset-b-009801

Grouped research for selected s3fs-fuse utility, threading, unit-test, and integration-test files. Each source file has a marker-delimited section for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/string_util.cpp -->
# sources/user-network-fs/s3fs-fuse/src/string_util.cpp

## Purpose
Implements the string, date, encoding, masking, and xattr serialization helpers declared in `string_util.h`. These routines sit on hot integration paths for S3 request signing, HTTP header construction/logging, object-key encoding, XML-safe object listing, and metadata-backed extended attributes.

## Important APIs, Types, And Control Flow
`str(timespec)` formats timestamps and recognizes `UTIME_OMIT`/`UTIME_NOW`. `s3fs_strptime`, `s3fs_strtoofft`, and `cvt_strtoofft` wrap portable parsing with explicit failure behavior. `trim_*`, `lower`, `upper`, and `peeloff` are pass-by-value transformations. URL encoding is centralized in `rawUrlEncode`, with general, path, and query variants differing only by allowed character sets. Date helpers emit RFC850, `YYYYMMDD`, and SigV3/SigV4-style ISO8601 strings and parse ISO8601 into GMT `time_t`. Binary helpers produce lower/upper hex, base64, and base64 decode output. WTF8 helpers detect invalid UTF-8 and map bad bytes into the Unicode private range, then reverse that mapping. CR helpers encode `%` and carriage returns before libxml2 parsing. Masking helpers redact sensitive request headers and option arguments. `parse_xattrs` and `raw_build_xattrs` transform the URL-encoded JSON-ish xattr header into `xattrs_t`.

## State And Persistence
The file is mostly stateless. It reads current time and locale, uses process `errno`, logs parse failures through `s3fs_logger`, and returns serialized strings for persistence in S3 metadata. `parse_xattrs` mutates the output map by clearing and rebuilding it.

## Dependencies And Integration Points
Depends on libc time/string conversion, `<regex>`, `fcntl.h`/`sys/stat.h` constants, `s3fs_logger.h`, `types.h`, and the header contract. Integration points include S3 auth dates, URL/object key handling, list-response XML preprocessing, logging redaction, command-line option logging, and xattr metadata.

## Risks And Test Signals
Risks include non-validating URL/base64 decoders accepting malformed bytes, `lower`/`upper` passing signed `char` to ctype functions, xattr parsing as ad hoc JSON split on commas/colons, `timegm` portability, `s3fs_strptime` returning `s + tellg()` where `tellg()` can be streampos-sensitive, and sensitive-header patterns missing new credentials. `test_string_util.cpp` covers trim/peeloff, base64 round trips, off_t conversion, WTF8, CR encoding, redaction, and xattr serialization; integration tests cover CR filenames, xattrs, external metadata, object keys, and logging behavior indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/string_util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/string_util.h -->
# sources/user-network-fs/s3fs-fuse/src/string_util.h

## Purpose
Declares the common string utility interface used across s3fs-fuse for URL/path encoding, HTTP/date formatting, binary encodings, WTF8 conversion, redaction, and S3 metadata xattr parsing.

## Important APIs, Types, And Control Flow
The header exports `SPACES`, `CaseInsensitiveStringView`, `is_prefix`, `SAFESTRPTR`, and `WTF8_ENCODE`. Public functions include timestamp formatting/parsing, off_t conversion, trim/case/quote helpers, RFC850/SigV3/SigV4 date construction, URL encode/decode variants, keyword extraction, hex/base64 encode/decode, WTF8 encode/decode, CR encode/decode, sensitive-string/header/argument masking, and `parse_xattrs`/`raw_build_xattrs`.

## State And Persistence
It has no runtime state except references held by `CaseInsensitiveStringView`. `WTF8_ENCODE` creates a local buffer and pointer alias in the caller scope, so its state and lifetime are macro-local and must be used carefully.

## Dependencies And Integration Points
Includes `<cstring>`, `<ctime>`, `<string>`, `<strings.h>`, and `types.h`. It is integrated by network/auth, logging, option, metadata, and filesystem code that need consistent object-key, header, or metadata transformations.

## Risks And Test Signals
`CaseInsensitiveStringView` stores a raw `const char*`; constructing it from a temporary `std::string` leaves a dangling pointer. Macro expansion in `WTF8_ENCODE` requires an `_ARG` variable naming convention and can surprise scopes. Tests in `test_string_util.cpp` and helper assertions in `test_util.h` exercise the exported routines most directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/string_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/syncfiller.cpp -->
# sources/user-network-fs/s3fs-fuse/src/syncfiller.cpp

## Purpose
Implements `SyncFiller`, a small synchronization wrapper around FUSE `fuse_fill_dir_t` callbacks. It serializes concurrent directory-entry filling and suppresses duplicate names while s3fs builds `readdir` responses from multiple sources.

## Important APIs, Types, And Control Flow
The constructor stores the FUSE buffer and callback and aborts on null inputs. `Fill(name, stbuf, off)` locks the mutex, inserts `name` into the `filled` set, and calls `filler_func` only for the first occurrence. `SufficiencyFill(pathlist)` locks once, iterates a vector of names, fills missing entries with null stat and offset zero, and returns `1` if any callback invocation fails.

## State And Persistence
State is in-memory per `SyncFiller`: the FUSE buffer pointer, callback pointer, mutex, and `std::set<std::string>` of names already returned. It performs no persistence; output is written into the caller-owned FUSE readdir buffer.

## Dependencies And Integration Points
Depends on `s3fs_logger.h` and `syncfiller.h`, which pulls in FUSE types through `s3fs.h`. It integrates with directory listing code where object-derived, implicit, and sufficiency entries can arrive concurrently or with overlap.

## Risks And Test Signals
The constructor aborts rather than returning an error, so caller validation matters. Holding the lock while invoking the FUSE filler callback can serialize long callbacks and could deadlock if the callback re-enters the same `SyncFiller`. Duplicate suppression is by exact string only. Integration test list, implicit directory, non-existing directory object, and duplicate/missing readdir cases provide indirect signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/syncfiller.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/syncfiller.h -->
# sources/user-network-fs/s3fs-fuse/src/syncfiller.h

## Purpose
Defines `SyncFiller`, the thread-safe FUSE directory filler facade used to protect `fuse_fill_dir_t` calls and avoid repeated directory entries.

## Important APIs, Types, And Control Flow
`SyncFiller(void* buff, fuse_fill_dir_t filler)` establishes the callback target. `Fill` handles one named entry with optional stat and offset. `SufficiencyFill` handles a vector of fallback names. Copy and move operations are deleted because the class owns synchronization state tied to a FUSE buffer.

## State And Persistence
The class stores `filler_lock`, the opaque FUSE buffer, the filler callback, and a `filled` set. State is valid only for a directory-fill operation and should not persist beyond the owning readdir request.

## Dependencies And Integration Points
Includes STL mutex/vector/set/string and `s3fs.h` for FUSE definitions and `S3FS_FUSE_FILL_DIR_DEFAULTS`. It is a direct bridge between s3fs listing logic and libfuse.

## Risks And Test Signals
The header exposes no way to clear `filled`, so one object should be used per listing. Callback and buffer lifetime are external. Signals are mostly integration-level: directory listing, recursive removal, implicit directory discovery, and concurrent directory update tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/syncfiller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_curl_util.cpp -->
# sources/user-network-fs/s3fs-fuse/src/test_curl_util.cpp

## Purpose
Standalone unit test for `curl_util.cpp` list manipulation helpers, especially sorted insertion and removal of libcurl `curl_slist` headers.

## Important APIs, Types, And Control Flow
The file defines a minimal `S3fsCred` stub to satisfy linkage for `curl_util.cpp`. `assert_is_sorted` walks a `curl_slist` and is intended to compare adjacent header keys case-insensitively. `curl_slist_length` counts nodes. `test_sort_insert` inserts keys in head, tail, middle, and replacement positions and checks the head replacement and length. `test_slist_remove` removes absent, sole, head, tail, and middle entries.

## State And Persistence
State is transient in heap-allocated libcurl lists. Each test frees lists with `curl_slist_free_all`; no external state is persisted.

## Dependencies And Integration Points
Depends on `curl_util.h`, libcurl slist types, `test_util.h`, and the link-time stub for `S3fsCred::GetBucket`. It protects HTTP header canonicalization behavior used by signing and request construction.

## Risks And Test Signals
`assert_is_sorted` currently derives both `key1` and `key2` from the same node, so it does not actually compare adjacent nodes; insertion ordering is only partially checked by downstream expectations. Removal coverage is useful but does not assert remaining key order/content after every case. Build and `make check` compile/link behavior are important test signals because the file intentionally avoids linking full credential logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_curl_util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_page_list.cpp -->
# sources/user-network-fs/s3fs-fuse/src/test_page_list.cpp

## Purpose
Standalone unit test for `PageList` compression and unloaded-page discovery behavior in the file-cache page tracking layer.

## Important APIs, Types, And Control Flow
The file stubs `CacheFileStat::Open` and `CacheFileStat::OverWriteFile` to avoid full cache-stat persistence. `test_compress` initializes a 42-byte page list, marks ranges loaded, calls `Compress`, and verifies `IsPageLoaded` plus `FindUnloadedPage` start/size results as adjacent and separated ranges are added.

## State And Persistence
The test uses only in-memory `PageList` state. The `CacheFileStat` methods are stubbed to return false, so no cache stat file is opened or overwritten.

## Dependencies And Integration Points
Includes `fdcache_page.h`, `fdcache_stat.h`, and `test_util.h`. It targets cache coherency behavior used by partial downloads/uploads and sparse page tracking.

## Risks And Test Signals
Coverage is narrow: it checks a single size and loaded/unloaded transitions but not modified status, persistence, negative ranges, large page maps, or cache-stat writeback. Its direct signal is unit-level correctness for range compression; integration tests such as cache file stat, sparse upload, and non-boundary writes cover broader effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_page_list.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_string_util.cpp -->
# sources/user-network-fs/s3fs-fuse/src/test_string_util.cpp

## Purpose
Unit test driver for the string utility layer, including trimming, base64, numeric conversion, WTF8, CR encoding, sensitive-data masking, and xattr metadata parsing.

## Important APIs, Types, And Control Flow
Defines minimal globals expected by logging. `test_trim` checks left/right/full trim and quote peeling. `test_base64` validates empty and 1/2/3/4-byte base64 round trips. `test_strtoofft` checks decimal, invalid input, and hex conversions. `test_wtf8_encoding` compares ASCII, valid UTF-8, CP1252-like bytes, broken UTF-8, and mixed strings. `test_cr_encoding` round-trips CR, percent, CRLF, and mixed sequences. Masking tests verify AWS SigV4/SigV2 authorization, x-amz sensitive headers, proxy URLs, and client-cert password redaction. `test_parse_xattrs` checks build/parse for one, multiple, and colon-containing keys.

## State And Persistence
All state is local except construction of `S3fsLog` in `main`. No files or external services are touched.

## Dependencies And Integration Points
Includes `s3fs_logger.h`, `string_util.h`, `test_util.h`, and `types.h`. It is the main regression signal for utility functions that feed request signing, XML name handling, logging, and xattrs.

## Risks And Test Signals
The test leaves gaps for invalid base64, malformed URL escapes, malformed xattr JSON, invalid ISO8601, overflow in option duration parsing, and signed-char case conversion. It strongly signals intended round-trip behavior for WTF8 and CR encoding and intended redaction strings for logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_string_util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_util.h -->
# sources/user-network-fs/s3fs-fuse/src/test_util.h

## Purpose
Provides lightweight assertion helpers for s3fs C++ unit tests without depending on a test framework.

## Important APIs, Types, And Control Flow
Template `assert_equals` and `assert_nequals` compare generic values and abort with file/line diagnostics. `std::string` specializations also print hex encodings using `s3fs_hex_lower`. `assert_strequals` handles null C strings. `assert_bufequals` compares byte buffers by length and `memcmp`. Macros wrap these functions with `__FILE__` and `__LINE__`.

## State And Persistence
No persistent state. On failure it writes diagnostics to stderr and aborts the process.

## Dependencies And Integration Points
Includes C stdio/stdlib, iostream, string, and `string_util.h` for hex diagnostics. Used by `test_string_util.cpp`, `test_curl_util.cpp`, `test_page_list.cpp`, and likely other unit tests.

## Risks And Test Signals
Abort-based assertions are simple but prevent multiple failures from being reported in one run. Buffer diagnostics construct strings from possibly binary data and may be noisy. The macros are compile-time integration signals for tests that need no external framework.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/threadpoolman.cpp -->
# sources/user-network-fs/s3fs-fuse/src/threadpoolman.cpp

## Purpose
Implements the singleton `ThreadPoolMan` used to run S3fsCurl-backed worker functions on a fixed pool of threads. It centralizes parallel request execution and per-thread curl/share cleanup.

## Important APIs, Types, And Control Flow
`Initialize` creates the singleton, optionally updates `worker_count`, and starts workers. `Destroy` resets it. `SetWorkerCount` validates positive counts but does not resize a live pool. `Instruct` requires a non-null completion semaphore and enqueues work. `AwaitInstruct` wraps a work item in a local semaphore and blocks until completion. `Worker` creates one `S3fsCurl` object per thread, waits on `thpoolman_sem`, recreates the curl handle for each instruction, pops a `thpoolman_param`, runs `pfunc`, releases the instruction semaphore, and destroys thread-local curl share state on exit. `StopThreads` sets `is_exit`, releases workers, joins them, reads futures, clears lists, and drains the semaphore.

## State And Persistence
Global state is the singleton and static `worker_count`. Instance state includes an atomic exit flag, semaphore, vector of `(thread, future)`, and instruction list guarded by a mutex. There is no disk persistence, but worker functions can perform S3/cache mutations through their arguments.

## Dependencies And Integration Points
Depends on `threadpoolman.h`, `s3fs_logger.h`, `curl.h`, `curl_share.h`, std threads/futures, and `Semaphore`. It integrates with multipart uploads/downloads, parallel copy, and any code that submits `thpoolman_param` work.

## Risks And Test Signals
No explicit null check for `param.pfunc` exists before worker invocation. The queue can retain unprocessed instructions if `CreateCurlHandle` fails and breaks a worker. `StopThreads` holds `thread_list_lock` while joining, which is acceptable only because workers do not need that lock after exit is signaled. `reinterpret_cast<long>` of an `int` future value is suspicious in logging. Signals come from integration tests for multipart upload/copy/mix, concurrent reads/writes, skipped writes, and sanitizer runs, especially ThreadSanitizer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/threadpoolman.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/threadpoolman.h -->
# sources/user-network-fs/s3fs-fuse/src/threadpoolman.h

## Purpose
Declares the thread-pool manager interface and work-item contract for asynchronous S3fsCurl operations.

## Important APIs, Types, And Control Flow
`thpoolman_worker` is a function pointer taking `S3fsCurl&` and `void*`. `thpoolman_param` carries `args`, optional completion `Semaphore*`, and `pfunc`. `ThreadPoolMan` exposes singleton lifecycle (`Initialize`, `Destroy`), worker-count accessors, asynchronous `Instruct`, and synchronous `AwaitInstruct`. Private methods own worker startup/shutdown, queueing, exit flags, and the worker entry point.

## State And Persistence
The class stores singleton state, static default worker count, an instruction queue, semaphore, thread list, and futures. It is process-scoped and non-copyable/non-movable.

## Dependencies And Integration Points
Includes atomics, futures, lists, mutexes, vectors, `common.h` annotations, and `psemaphore.h`; forward-declares `S3fsCurl`. It is the public concurrency contract for parts of s3fs that need pooled curl work.

## Risks And Test Signals
Raw `void*` arguments and function pointers make type safety caller-owned. Completion semaphore lifetime must outlive execution. `SetWorkerCount` only affects future initialization. Integration and sanitizer scripts are the main signals; unit-level direct coverage is not present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/threadpoolman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/types.h -->
# sources/user-network-fs/s3fs-fuse/src/types.h

## Purpose
Defines shared lightweight types and enums for S3 metadata, ACLs, encryption/signature settings, multipart upload bookkeeping, directory rename bookkeeping, MIME maps, and object-kind classification.

## Important APIs, Types, And Control Flow
`xattrs_t` maps xattr names to values. `acl_t` plus `str(acl_t)`/`to_acl` converts S3 canned ACLs. `sse_type_t` and `signature_type_t` encode option choices. Multipart support uses `etagpair`, pointer-stable `etaglist_t`, `petagpool`, `filepart`, `filepart_list_t`, `untreatedpart`, `untreated_list_t`, `mp_part`, `mp_part_list_t`, and `total_mp_part_list`. `mvnode` describes rename operations. `mimes_t` is a case-insensitive map with transparent lookup. `objtype_t` models files, symlinks, several directory representations, and negative cache entries with helper predicates and `STR_OBJTYPE`.

## State And Persistence
Types are mostly value containers. Destructors call `clear`, which resets owned strings and pointers but does not close file descriptors in `filepart`; fd ownership is external. Pointer stability is explicitly required for etag lists/pools because `filepart` stores `etagpair*`.

## Dependencies And Integration Points
Includes standard containers and optional xattr system headers based on configure macros. This header is widely shared by metadata, cache, multipart upload, object classification, MIME, and rename code.

## Risks And Test Signals
`to_acl` assumes non-null input. `filepart` constructor ignores its `is_uploaded` argument and leaves `uploaded` default false, which may be intentional or a bug. Raw fd and pointer fields rely on external ownership. Object type equivalence treats all directory encodings as same, so callers needing exact representation must avoid `IS_SAME_OBJ`. Integration tests for ACL-like metadata, xattrs, multipart upload/copy/mix, implicit directories, and rename behavior exercise these contracts indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/test/Makefile.am

## Purpose
Automake test/build definition for the s3fs-fuse integration test directory.

## Important APIs, Types, And Control Flow
Declares `TESTS=small-integration-test.sh`, lists distributed helper scripts/configs in `EXTRA_DIST`, and builds no-install helper binaries: `junk_data`, `write_multiblock`, `mknod_test`, `truncate_read_file`, and `cr_filename`. The `clang-tidy` target runs static analysis over these helper C++ sources with configured C++ standard and dependency flags.

## State And Persistence
Build products are local test binaries. Running `make check` delegates to the shell test suite and its generated runtime state.

## Dependencies And Integration Points
Depends on Automake variables, configured `@CPP_VERSION@`, and project `DEPS_CFLAGS`/`CPPFLAGS`. Integrates helper binaries used by `integration-test-main.sh`.

## Risks And Test Signals
Only `small-integration-test.sh` is in `TESTS`; broader behavior depends on environment variable `ALL_TESTS`. Missing helper source declarations would break integration tests at runtime. `make check -C test/` is the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/chaos-http-proxy.conf -->
# sources/user-network-fs/s3fs-fuse/test/chaos-http-proxy.conf

## Purpose
Configuration for Chaos HTTP Proxy during proxy-failure integration tests.

## Important APIs, Types, And Control Flow
Defines a simple response distribution: one HTTP 503 response for every nine successes through `com.bouncestorage.chaoshttpproxy.http_503=1` and `success=9`.

## State And Persistence
No runtime state in the file itself. The Java proxy reads it at startup and injects transient failures into HTTP traffic.

## Dependencies And Integration Points
Used by `integration-test-common.sh` when `CHAOS_HTTP_PROXY` or `CHAOS_HTTP_PROXY_OPT` is set. It sits between s3fs and S3Proxy on HTTP-only test runs.

## Risks And Test Signals
The tiny config assumes Chaos HTTP Proxy property names and a fixed failure ratio. It does not configure ports here, so defaults or companion proxy behavior must match the script’s wait on port 1080. Test signal is successful retry behavior under injected 503s.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/chaos-http-proxy.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/compile_all_targets.sh -->
# sources/user-network-fs/s3fs-fuse/test/compile_all_targets.sh

## Purpose
Build matrix script that compiles s3fs-fuse under several TLS/crypto backends, language modes, word sizes, and compilers.

## Important APIs, Types, And Control Flow
The script enables `errexit`, `nounset`, and `pipefail`, sets `COMMON_FLAGS='-O -Wall -Werror'`, then repeatedly runs `make clean`, `./configure` with a variant, and parallel `make`. Variants cover GnuTLS, GnuTLS+Nettle, NSS, OpenSSL, C++23, `-m32`, and clang++ with `-Wshorten-64-to-32`.

## State And Persistence
Mutates the working tree build directory through configure outputs, object files, and clean/build cycles. No source files are edited.

## Dependencies And Integration Points
Depends on autotools/configure, make, nproc, backend development libraries, clang++, and 32-bit toolchain support. It complements runtime tests by checking optional compile targets.

## Risks And Test Signals
`-Werror` makes warning churn fail the matrix. `-m32` is environment-sensitive. The script is serial across configurations and can be expensive. A complete zero exit is strong build portability signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/compile_all_targets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/cr_filename.cc -->
# sources/user-network-fs/s3fs-fuse/test/cr_filename.cc

## Purpose
Helper program for testing object/file names containing a carriage return byte.

## Important APIs, Types, And Control Flow
`main` requires one base path argument, appends `\r` into a fixed buffer, creates the file with `open(O_CREAT|O_RDWR)`, closes it, verifies it with `stat`, and removes it with `unlink`.

## State And Persistence
Creates and deletes one filesystem object whose name ends in CR. It leaves no intended persistent state after success.

## Dependencies And Integration Points
Depends on POSIX `open`, `close`, `stat`, and `unlink`. Called by `integration-test-main.sh` in `test_cr_filename`, indirectly testing `string_util.cpp` CR encoding for S3 XML list parsing.

## Risks And Test Signals
Uses a 4096-byte fixed buffer and truncates silently if the base path is too long. It does not inspect contents or listing, only create/stat/delete. Success under the mounted filesystem is a direct signal that CR-named objects survive round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/cr_filename.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/filter-suite-log.sh -->
# sources/user-network-fs/s3fs-fuse/test/filter-suite-log.sh

## Purpose
Post-processes `test-suite.log` to reduce noisy s3fs informational output while preserving detailed logs around failed small integration tests.

## Important APIs, Types, And Control Flow
Parses optional log path, validates it, records line numbers for `test_*: "..."`, `test_* passed`, and `test_* failed` markers into `/tmp/.lineno.tmp`, then iterates marker ranges. Passed and normal ranges filter progress percentages and `s3fs: [INF]` lines; failed or unterminated test ranges print more complete output. Finally it prints the remaining tail and removes the temp file.

## State And Persistence
Reads a suite log and writes filtered stdout. Temporarily persists line metadata at a fixed `/tmp/.lineno.tmp` path.

## Dependencies And Integration Points
Uses grep, sed, head, tail, wc, basename, dirname, and shell arithmetic. It depends on marker text emitted by `integration-test-main.sh` and `test-utils.sh`.

## Risks And Test Signals
The fixed temp path can collide across concurrent runs. Range arithmetic around first/last lines is fragile. The grep expression mixes `-v`, `-a`, and multiple expressions in a way that depends on GNU grep behavior. Useful signal is human-readable CI failure logs with retained failure context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/filter-suite-log.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/integration-test-common.sh -->
# sources/user-network-fs/s3fs-fuse/test/integration-test-common.sh

## Purpose
Shared shell harness for starting/stopping S3Proxy, optional Chaos HTTP Proxy, pjdfstest, and an s3fs mount for integration tests.

## Important APIs, Types, And Control Flow
Sets defaults for `S3_URL`, `S3_ENDPOINT`, credentials, bucket, S3Proxy versions/hashes, and proxy settings. `retry` repeatedly evaluates commands. `start_s3proxy` downloads/verifies S3Proxy and Chaos HTTP Proxy if missing, generates a self-signed cert for HTTPS, starts Java services, waits for ports, and downloads/builds pjdfstest. `start_s3fs` selects auth mode, optional valgrind, proxy, macOS/FUSE-T, certificate, cache/stat options, starts s3fs in foreground with logging prefixing, captures PID, and waits for the mount. `stop_s3fs`, `stop_s3proxy`, and `common_exit_handler` tear down processes and mounts.

## State And Persistence
Creates credentials permissions, mount directories, downloaded binaries, `/tmp/keystore.*`, pjdfstest sources/build outputs, pid files, exported environment variables, background Java/s3fs processes, and mounted FUSE state.

## Dependencies And Integration Points
Depends on bash, curl, sha256sum, keytool, Java, S3Proxy, Chaos HTTP Proxy, pjdfstest autotools, FUSE/fusermount3 or macOS umount, awk, grep, `/proc/mounts`, and `test-utils.sh` helpers used by callers. It is sourced by `small-integration-test.sh`.

## Risks And Test Signals
Network downloads are pinned by hash but still depend on external availability. `eval` in `retry` is flexible but risky. Port waits assume fixed ports. Cleanup trap does not stack automatically. Successful mount/start/stop across Linux and macOS is the foundational signal for all integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/integration-test-common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/integration-test-main.sh -->
# sources/user-network-fs/s3fs-fuse/test/integration-test-main.sh

## Purpose
Main integration test suite for mounted s3fs behavior. It exercises POSIX-like file operations, S3 metadata mapping, multipart/cache behavior, implicit directory handling, xattrs/ACLs, concurrent access, sparse writes, statvfs, and selected pjdfstest cases.

## Important APIs, Types, And Control Flow
The script sources `test-utils.sh`, defines many `test_*` functions, calls `init_suite`, registers tests in `add_all_tests`, and runs them with `run_suite`. Tests cover create/append/truncate/shrink/read, rename of files/directories, shell redirects, mkdir/rmdir, chmod/chown, listing, non-empty rmdir errors, external S3 object creation/modification, metadata updates for small/large objects, rename before close, multipart upload/copy/mix, special characters, hardlink rejection, mknod, symlink, xattrs, timestamp update semantics, parent directory time updates, POSIX ACLs, recursive removal, copy/seek/overwrite, concurrent reads/writes/directory updates, second-fd reads, multioffset writes, content type, cache-stat files, zero-byte cache stats, sparse uploads, mixed upload entities, ensure-diskfree behavior, implicit directories, CR filenames, skipped writes, non-boundary writes, mountpoint time/statvfs, and pjdfstest subsets. `add_all_tests` selects tests based on mount options, OS, cache/ensure-diskfree settings, Alpine, Ubuntu version, and macOS FUSE-T caveats.

## State And Persistence
Creates and removes many files under the mounted bucket, `/tmp`, and cache directories. It mutates S3 objects through `s3_cp`, local cache/stat files, xattrs, ACLs, metadata timestamps, and mounted directory structures. Some tests intentionally delete cache files to force remote re-fetch.

## Dependencies And Integration Points
Depends heavily on `test-utils.sh`, helper binaries (`junk_data`, `write_multiblock`, `mknod_test`, `truncate_read_file`, `cr_filename`), AWS/S3 helper functions, GNU/coreutils behavior, xattr/ACL tools, pjdfstest, S3Proxy or a real S3 endpoint, and mounted s3fs options from `small-integration-test.sh`.

## Risks And Test Signals
The suite is environment-sensitive: macOS FUSE-T, Alpine, Ubuntu 25.10, noatime/relatime, root privileges, ACL/xattr tool availability, cache options, and disk space all affect coverage. It can consume significant disk and network resources. Strong signals include all registered tests passing under both default `sigv4` and `ALL_TESTS` option matrices, plus sanitizer/Valgrind wrapper scripts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/integration-test-main.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/junk_data.cc -->
# sources/user-network-fs/s3fs-fuse/test/junk_data.cc

## Purpose
Fast deterministic data generator used by integration tests instead of slower random data sources.

## Important APIs, Types, And Control Flow
`main` expects a byte count, allocates a 128 KiB stack buffer, fills it with incrementing `uint64_t` patterns based on output offset, and writes chunks to stdout until the requested byte count is produced.

## State And Persistence
No persistent state. It streams bytes to stdout for callers to redirect into local or mounted files.

## Dependencies And Integration Points
Depends on C stdio/stdlib and integer types. Called throughout `integration-test-main.sh` to produce large files for multipart, cache, sparse, and concurrency tests.

## Risks And Test Signals
No error checking on `fwrite`, no validation for invalid numeric input beyond `strtoull`, and reinterpret-casting a char buffer to `uint64_t*` may raise strict-aliasing/alignment concerns on unusual platforms. Its deterministic output makes `cmp`-based integration tests reliable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/junk_data.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/map-subscript-read.py -->
# sources/user-network-fs/s3fs-fuse/test/map-subscript-read.py

## Purpose
Cppcheck addon that flags read-side uses of `std::map::operator[]` and `std::unordered_map::operator[]`, where reads can accidentally insert default values.

## Important APIs, Types, And Control Flow
Imports `cppcheckdata`, defines `reportError`, `simpleMatch`, and `check_map_subscript`. The checker iterates configurations and token lists, finds `[` AST nodes with both operands, skips assignment LHS uses, resolves the container variable, and reports style diagnostics when the type token matches `std :: map <` or `std :: unordered_map <`. The script loads each dump argument and exits with cppcheck’s addon exit code.

## State And Persistence
Reads cppcheck dump files and emits diagnostics through cppcheck’s reporting API. No repository files are mutated.

## Dependencies And Integration Points
Depends on cppcheck addon Python APIs and dump generation (`cppcheck --dump`). It integrates with static analysis workflows to enforce safer map lookup patterns.

## Risks And Test Signals
Pattern matching is token-shape sensitive and may miss aliases, typedefs, namespace variations, references, or complex expressions. It can false-positive on deliberate insertion-through-read idioms not written as assignment LHS. Test signals are cppcheck addon runs over representative C++ snippets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/map-subscript-read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/mergedir.sh -->
# sources/user-network-fs/s3fs-fuse/test/mergedir.sh

## Purpose
Legacy utility script to merge directory objects created by old s3fs versions or other S3 clients into normal directory metadata.

## Important APIs, Types, And Control Flow
Parses `-h`, `-y`, `-all`, and a base directory. Warns if not root and prints a caution. Builds a dated log, finds directories, optionally filters to `d---------` permission directories, prompts per directory unless auto-yes, then attempts to restore permissions/ownership/timestamps from `ls -ld` output using `chmod`, `chown`, and `touch`.

## State And Persistence
Mutates directory metadata under the target tree and writes a timestamped log file. It can change ownership, mode, and mtime.

## Dependencies And Integration Points
Uses POSIX shell, find, grep, basename, whoami, date, ls, awk, chmod, chown, and touch. It is distributed as a helper/sample rather than invoked by the main automated tests in this subset.

## Risks And Test Signals
The implementation appears to pass extracted metadata variables incorrectly as path arguments (`chmod 755 "${CHMOD}"`, `chown "${CHOWN}"`, `touch -t "${TOUCH}"` without target directory), making it risky or broken. Parsing `ls` is locale/format fragile and fails with whitespace in names because `for DIR in $DIRLIST` word-splits. Requires careful manual testing before use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/mergedir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/mknod_test.cc -->
# sources/user-network-fs/s3fs-fuse/test/mknod_test.cc

## Purpose
Helper executable that validates mknod behavior for regular, character, FIFO, socket, and optionally block-special files on the mounted filesystem.

## Important APIs, Types, And Control Flow
`TestMknod` maps a mode to suffix, display name, and device number, creates the node with permissions, stats it, verifies `S_IFMT`, and unlinks it. `main` parses one base path or help, checks length, skips block-device testing unless effective uid is root, and fails if any required node type cannot be created/stat-verified.

## State And Persistence
Creates and removes several filesystem nodes named from the base path with `.reg`, `.chr`, `.fifo`, `.sock`, and optionally `.blk` suffixes. Failed cleanup can leave nodes behind.

## Dependencies And Integration Points
Depends on POSIX `mknod`, `stat`, `unlink`, `geteuid`, and `makedev`; macOS/FreeBSD include handling differs. Called by `integration-test-main.sh` from `test_mknod`.

## Risks And Test Signals
Some node types are unsupported or permission-sensitive on FUSE and host systems. The fixed path length cap is conservative. The integration signal is whether s3fs correctly rejects or represents special node creation according to expected FUSE semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/mknod_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/run_tests_using_sanitizers.sh -->
# sources/user-network-fs/s3fs-fuse/test/run_tests_using_sanitizers.sh

## Purpose
Runs the test suite under libstdc++ debug mode, multiple sanitizers, and Valgrind to expose memory, undefined behavior, thread, and container misuse issues.

## Important APIs, Types, And Control Flow
Uses strict bash options, sets debug-friendly `COMMON_FLAGS`, then cycles through clean/configure/build/check for `_GLIBCXX_DEBUG`, AddressSanitizer with leak/use-after-return options, ThreadSanitizer, UndefinedBehaviorSanitizer with extra conversion/bounds checks, and Valgrind with high retries and S3Proxy HTTP URL. MemorySanitizer is documented but disabled pending custom libc++.

## State And Persistence
Mutates build outputs repeatedly and runs integration tests that create mount, cache, and S3Proxy state. No source edits are made.

## Dependencies And Integration Points
Depends on GCC/libstdc++ debug mode, clang++, sanitizer runtimes, Valgrind, configure/make, and the test harness. Integrates as a heavyweight CI/local validation lane.

## Risks And Test Signals
Sanitizer availability is platform/toolchain-sensitive and ThreadSanitizer can be noisy with external libraries. Valgrind runs are slow and retry-heavy. Passing this script is a high-value signal for `ThreadPoolMan`, cache, and string/binary utilities.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/run_tests_using_sanitizers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/s3proxy.conf -->
# sources/user-network-fs/s3fs-fuse/test/s3proxy.conf

## Purpose
Default S3Proxy configuration for local integration tests with both HTTP and HTTPS endpoints.

## Important APIs, Types, And Control Flow
Sets HTTP endpoint `127.0.0.1:8081`, HTTPS endpoint `127.0.0.1:8080`, AWS v2/v4 auth, local identity/credential, keystore path/password, and transient-nio2 jclouds backend credentials.

## State And Persistence
No mutable state in the file. At runtime S3Proxy uses an in-memory/transient backend and the generated keystore.

## Dependencies And Integration Points
Read by Java S3Proxy in `integration-test-common.sh` unless public/noauth or chaos proxy variants are selected. Coordinates with credentials file and s3fs `-o url` defaults.

## Risks And Test Signals
Ports and credentials are fixed test defaults. HTTPS relies on generated `/tmp/keystore.jks`. Successful bucket creation/head/copy through S3Proxy validates this config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/s3proxy.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/s3proxy_http.conf -->
# sources/user-network-fs/s3fs-fuse/test/s3proxy_http.conf

## Purpose
S3Proxy configuration variant for HTTP-only proxy tests.

## Important APIs, Types, And Control Flow
Sets the HTTP endpoint on `127.0.0.1:8080`, AWS v2/v4 auth, local identity/credential, and transient jclouds backend identity/credential.

## State And Persistence
No local state; S3Proxy owns transient object data while running.

## Dependencies And Integration Points
Selected by `integration-test-common.sh` when Chaos HTTP Proxy is enabled. It avoids HTTPS because the chaos proxy path is HTTP-only.

## Risks And Test Signals
Port 8080 overlaps with the HTTPS port in the default config but is used in a mutually exclusive config path. Test signal is successful proxy-mediated S3 operations with injected failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/s3proxy_http.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/sample_ahbe.conf -->
# sources/user-network-fs/s3fs-fuse/test/sample_ahbe.conf

## Purpose
Sample additional-header-by-extension configuration file for s3fs startup.

## Important APIs, Types, And Control Flow
Documents line format as suffix or `reg:` regex, HTTP header name, and header values. Provides examples mapping compressed file suffixes such as `.gz`, `.Z`, `.bz2`, `.svgz`, `.tar.gz`, and `gz.js` to `Content-Encoding`, plus a regex example for paths under `/MYDIR`.

## State And Persistence
Static configuration only. When used by s3fs, matching upload/object operations receive additional HTTP metadata headers.

## Dependencies And Integration Points
Consumed by the s3fs AHBE option parser, not directly by automated scripts here. It integrates with content-encoding metadata behavior and S3 object upload headers.

## Risks And Test Signals
Order matters, so broad rules can shadow specific ones. The sample notes that `identity` should not be used as `Content-Encoding`. Test signals would be uploads with matching suffixes/regexes and subsequent metadata inspection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/sample_ahbe.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/sample_delcache.sh -->
# sources/user-network-fs/s3fs-fuse/test/sample_delcache.sh

## Purpose
Unsupported sample script for pruning s3fs local cache files by access time until a byte-size limit is met.

## Important APIs, Types, And Control Flow
Parses bucket, cache path, byte limit, and optional `-silent`. Computes file and stat cache directories, exits if under limit, then finds stat files with atime, sorts oldest first, maps stat-file paths to cache-file paths, validates unchanged atime, removes both files, and stops once current cache size is below limit.

## State And Persistence
Deletes files under `${cache}/${bucket}` and `${cache}/.${bucket}.stat`. It can permanently remove local cached object/stat data, though remote S3 data should remain.

## Dependencies And Integration Points
Uses POSIX shell plus GNU `du -sb`, `stat -c`, find, sort, cut, sed, and rm. It is a sample helper for installations using `use_cache`, not part of `make check`.

## Risks And Test Signals
Not safe for all platforms because GNU-specific `du`/`stat` options are used. It can race active s3fs cache users and does not lock. Path mapping via sed can fail for unusual bucket/cache names. Test on disposable cache directories before operational use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/sample_delcache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/small-integration-test.sh -->
# sources/user-network-fs/s3fs-fuse/test/small-integration-test.sh

## Purpose
Top-level Automake test script that prepares cache/SSE test state, starts S3Proxy, mounts s3fs with selected option sets, and invokes `integration-test-main.sh`.

## Important APIs, Types, And Control Flow
Uses strict bash options, sources `integration-test-common.sh` and `test-utils.sh`, creates `/tmp/s3fs-cache`, sets fake/ensure diskfree values, generates SSE key material, exports cache/diskfree variables, and builds `FLAGS`. With `ALL_TESTS`, it runs many option combinations: cache/diskfree/xattr/parent-stat, content-md5, noobj-cache disabled, small stat cache, no copy API, no multipart, SigV2, SigV4, small multipart copy threshold, and streamupload. Without `ALL_TESTS`, it runs only `sigv4`. It starts S3Proxy, creates the bucket if needed, loops mount/test/unmount for each flag, and stops S3Proxy.

## State And Persistence
Creates/removes cache directory, writes `/tmp/ssekey*`, creates or reuses a test bucket, mounts/unmounts s3fs repeatedly, and leaves downloaded S3Proxy/pjdfstest artifacts managed by the common harness.

## Dependencies And Integration Points
Depends on the common harness, OpenSSL, base64, S3 helper functions, helper binaries, and the full integration suite. It is the single `TESTS` entry in `Makefile.am`.

## Risks And Test Signals
Default coverage is intentionally small (`sigv4` only). `ALL_TESTS` is expensive and option-dependent. Some SSE options are present but disabled because S3Proxy lacks support. Passing this script is the main automated integration signal for a build.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/test/small-integration-test.sh -->

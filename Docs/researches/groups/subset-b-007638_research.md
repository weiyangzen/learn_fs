# Research: subset-b-007638

Grouped source-tree-aligned research for the requested LizardFS utility files and Lustre LNet headers. Each section preserves the source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/chunk_converter.cc -->
# sources/distributed-fs/lizardfs/utils/chunk_converter.cc

Purpose: command-line converter that rewrites one standard LizardFS/MooseFS chunk into XOR-coded part chunks plus a parity chunk. It accepts `xor_level`, `input_file`, and `output_dir`, validates the XOR level range 2..10, derives output names from the original chunk footer, and emits `chunk_xor_N_of_LEVEL...` plus `chunk_xor_parity_of_LEVEL...`.

Important APIs/functions: `saveBlockAndCrc()` calculates zlib `crc32()` for a 64 KiB parity block, stores the big-endian CRC bytes in a side buffer, writes the parity block, then resets the parity buffer. `main()` owns all parsing, stream setup, header validation, CRC distribution, block distribution, parity construction, and final status reporting.

Control flow: the program reads the 1 KiB header, accepts either `MFSC 1.0` or `LIZC 1.0`, rewrites the signature to `LIZC 1.0`, and sets header byte 20 to the LizardFS XOR chunk type encoding. It then round-robins 1024 4-byte CRC entries across data parts, seeks every part to the block area at 4 KiB, and streams full 64 KiB blocks from the source. Each block is written to its current data part and XORed into the parity accumulator; parity is flushed after every full stripe and once more for a partial final stripe.

State and persistence: persistent output is a set of chunk part files. Writes are direct `std::ofstream` operations with `failbit` exceptions enabled on outputs, but there is no cleanup on partial failure. The input is read sequentially.

Dependencies/integration: depends on `common/platform.h`, zlib, chunk on-disk header offsets, and `ChunkType::getXorChunkType()`-compatible encoding. It is an offline migration/repair utility, not part of the server runtime.

Risks and test signals: risks include assuming fixed 64 KiB block and 1024-block chunk geometry, writing output streams in text mode rather than explicitly binary mode, partial output files after exceptions, and relying on filename length/footer format. Test signals are conversion of old and new signatures, bad headers, xor levels outside 2..10, output-name collision, uneven stripe counts, and CRC/parity validation with the normal chunk verifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/chunk_converter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/chunk_operations_eio.c -->
# sources/distributed-fs/lizardfs/utils/chunk_operations_eio.c

Purpose: LD_PRELOAD-style fault injection library for chunk file I/O. It overrides `pread`, `pwrite`, `close`, and `fsync` and returns `-1/EIO` for selected file names, letting integration tests verify chunkserver behavior under I/O errors.

Important APIs/functions: `read_filename()` resolves an fd through `/proc/self/fd/<fd>`. `err_on_operation()` checks that the path contains `/chunk_`, then looks for operation-specific substrings such as `pread_EIO`, `pwrite_EIO`, `close_EIO`, `fsync_EIO`, or far-offset variants such as `pread_far_EIO`. The overridden libc symbols lazily resolve the real function with `dlsym(RTLD_NEXT, ...)`.

Control flow: every intercepted call first derives the filename. Non-chunk paths pass through unchanged. Matching chunk paths fail immediately when the always-fail token is present. For `pread` and `pwrite`, the `*_far_EIO` token only triggers when `offset > 102400`; `close` and `fsync` pass offset zero to the same helper.

State and persistence: no persistent state is written. Process-local static function pointers cache libc symbol lookups. Behavior is encoded entirely in the current fd target path, so renames or symlinks affect matching through `/proc/self/fd`.

Dependencies/integration: depends on glibc dynamic linking, `_GNU_SOURCE`, `/proc`, and POSIX file APIs. It is intended for test process environments via `LD_PRELOAD`.

Risks and test signals: `sprintf` into fixed 1024-byte buffers can truncate/overflow if unexpected fd strings or names are used, and `close` failure injection can leak descriptors in tests unless callers handle it. Concurrency is acceptable for static pointer initialization in normal tests but not formally synchronized. Test signals are successful pass-through for non-chunk files, exact EIO/error propagation for each trigger, far-offset threshold boundaries, and preserving original function behavior when no trigger matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/chunk_operations_eio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/configuration.h -->
# sources/distributed-fs/lizardfs/utils/configuration.h

Purpose: small utility configuration facade used by test binaries. `UtilsConfiguration` extends `devtools/configuration.h` and centralizes environment-driven values for generated file tests.

Important APIs/types: `blockSize()` reads `BLOCK_SIZE` with unit support and defaults to 64 KiB. `fileSize()` reads `FILE_SIZE` with unit support and defaults to 100 MiB. `repeatAfter_ms()` reads `REPEAT_AFTER_MS` and defaults to zero. `seed()` reads `SEED` and defaults to zero. The class publicly re-exports `Configuration::parseIntWithUnit` and `Configuration::parseInt` for command-line utilities.

Control flow: all methods are static wrappers over `getIntWithUnitOr()` or `getIntOr()`. There is no object state and no initialization order beyond the included configuration helper.

State and persistence: values are process-local reads from environment variables or explicit strings. Nothing is persisted.

Dependencies/integration: used by `data_generator.h` clients: `file_generate.cc`, `file_overwrite.cc`, `file_validate.cc`, and `file_validate_growing.cc`. It depends on the broader LizardFS devtools configuration parser, signal/system headers only indirectly, and standard C++ streams.

Risks and test signals: risks are inherited from environment parsing: invalid units, oversized values, or zero/small sizes that violate `DataGenerator` assumptions. Test signals are default behavior with no environment, unit parsing for sizes, `REPEAT_AFTER_MS` cache validation delay, and seeded deterministic generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/configuration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/coverage.sh -->
# sources/distributed-fs/lizardfs/utils/coverage.sh

Purpose: test coverage helper for LizardFS CMake builds. It prepares build directories for coverage data written by tests running under different UIDs and generates filtered HTML coverage reports.

Important commands/control flow: the script expects `prepare <build-dir>` or `generate-html <build-dir> <out-dir>`. It first verifies `<build-dir>/CMakeCache.txt`. `prepare` sets every directory in the build tree writable by all users and removes existing `*.gcda` files. `generate-html` creates the output directory, captures with `lcov --capture --directory .`, filters out system headers, `external`, `tests`, `utils`, and `devtools`, runs `genhtml`, then removes temporary `cov.raw` and `cov.info`.

State and persistence: mutates permissions under the build directory, deletes old coverage counters, and creates an HTML report in the requested output directory. Temporary coverage files are created in the caller's working directory, not necessarily inside `builddir`.

Dependencies/integration: depends on Bash, `find`, `xargs`, `lcov`, and `genhtml`; expects CMake/gcov-style artifacts. It is part of developer/test tooling rather than runtime.

Risks and test signals: `command=$1` and `builddir=$2` are read before argument validation, so `set -u` is not enabled until command branches. `xargs` without `-r` may invoke commands with empty input on some platforms. Coverage capture uses `--directory .`, so callers must run it from a meaningful build context. Test signals are prepare on populated and empty build trees, report generation with filtering, and permission handling when tests run under another UID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/coverage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/cpp-interpreter.sh -->
# sources/distributed-fs/lizardfs/utils/cpp-interpreter.sh

Purpose: Bash wrapper that treats a C++ source file as an interpreted test/program by compiling it on demand to a cached executable and then running it.

Important operations: it strips a leading shebang from the source via `grep -v '^#!'`, hashes the remaining source with `md5sum`, chooses `${TEMP_DIR:-/tmp}/cached_c_$hash`, compiles with `c++ -xc++ -o "$executable" - <<< "$source"` if the executable is missing or not executable, and finally executes it with forwarded arguments.

Control flow: the first argument is the source path; all remaining arguments are passed to the compiled binary. Empty source after shebang removal exits with status 1. Compilation failure aborts due to `set -e`.

State and persistence: persists cached binaries in `TEMP_DIR` or `/tmp`, keyed only by source content. It does not include compiler flags, compiler version, include paths, or linked libraries in the cache key.

Dependencies/integration: depends on Bash, GNU `md5sum`, `awk`, a working C++ compiler, and any includes required by the source. Useful for tests that embed small C++ programs with shebang lines.

Risks and test signals: cache collisions are unlikely but possible with MD5, and stale binaries may be reused when only compiler flags/environment changed. `grep -v '^#!'` removes all shebang-like lines, not just the first. Test signals are first compile, cached rerun, forwarding of arguments, failure on invalid C++, and honoring `TEMP_DIR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/cpp-interpreter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/crc_converter.cc -->
# sources/distributed-fs/lizardfs/utils/crc_converter.cc

Purpose: offline chunk utility that recalculates and rewrites CRC tables for standard or XOR chunk files. It accepts an input chunk and type selector `{ Std | Xor }`.

Important APIs/types/functions: `ChunkType` encodes file layout differences: standard chunks have data at 5 KiB, up to 1024 blocks, and 4 KiB CRC data; XOR chunks have data at 4 KiB, up to 512 blocks, and 2 KiB CRC data. `parseArguments()` validates CLI arguments. `calculateCrc()` seeks to the data region and fills a CRC buffer. `calculateCrcForBlock()` reads one full 64 KiB block and computes zlib CRC32. `writeCrc()` overwrites the CRC region at offset 1024.

Control flow: `main()` parses the type, allocates the exact CRC table size, computes CRCs block by block, and writes the table back to the same file. Short final blocks are considered incorrect chunk files and cause exit status 2.

State and persistence: mutates the input file in place. It opens the chunk first as input and later as read/write output. There is no backup or transactional rewrite.

Dependencies/integration: depends on zlib, `<arpa/inet.h>` for `htonl`, and fixed LizardFS chunk layout constants. It complements chunk conversion/repair workflows.

Risks and test signals: uses `reinterpret_cast<uint32_t*>` on a byte buffer, which can be alignment-sensitive on strict architectures. It does not verify chunk signature or file length before rewriting. Test signals are standard and XOR chunk fixtures, corrupted/short block behavior, endian correctness of CRC entries, and preservation of non-CRC regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/crc_converter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/data_generator.h -->
# sources/distributed-fs/lizardfs/utils/data_generator.h

Purpose: deterministic file generator and validator used by LizardFS tests. It creates files whose first 8 bytes store total size in big-endian form and whose body is a predictable sequence of big-endian 64-bit values derived from offset and optional seed.

Important APIs/types/functions: `DataGenerator(seed)` controls deterministic content. `createFile()` creates/truncates and fills a file. `overwriteFile()` preserves existing size and rewrites content. `validateFile(fd,name,file_size)` validates header, size, and body. `validateFile(name,repeat_after_ms)` optionally validates once, sleeps, and validates again to exercise caches. `validateGrowingFile()` validates only the requested current size. Protected helpers fill aligned and unaligned buffers with expected data.

Control flow: generation writes the serialized size, then loops with `UtilsConfiguration::blockSize()` buffers. Validation stats the file, optionally reads and compares the embedded expected size, then uses `pread` at successive offsets and `memcmp` for fast comparison. On mismatch it locates the first bad byte and reports expected/actual hex context.

State and persistence: file contents are the only persistent state. The seed is stored in the object; random seeded mode calls `std::srand(seed_)` inside buffer filling, making output deterministic for a given seed and offset but not thread-safe.

Dependencies/integration: depends on POSIX `open`, `write`, `pread`, `stat`, endian helpers, LizardFS assertion utilities, and `UtilsConfiguration`. It is shared by file generation, overwrite, and validation utilities.

Risks and test signals: files smaller than 8 bytes are invalid for generation. `validateFile(fd,name,file_size)` has subtle behavior when `file_size` is nonzero: it skips header size validation and allows short reads while decrementing by `bytes_read`, so EOF handling must be tested carefully for growing files. Test signals are seeded/unseeded generation, unaligned last blocks, mismatch diagnostics, repeated validation, and cache/race behavior for growing files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/data_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_generate.cc -->
# sources/distributed-fs/lizardfs/utils/file_generate.cc

Purpose: command-line wrapper around `DataGenerator::createFile()` for creating one or more deterministic test files.

Important APIs/functions: reads `FILE_SIZE` and `SEED` through `UtilsConfiguration`, constructs `DataGenerator`, and calls `createFile(argv[i], FILE_SIZE)` for each path. Usage text also advertises `BLOCK_SIZE`, which is used indirectly by the generator.

Control flow: if no file paths are provided it prints usage and exits 1. Otherwise all requested files are generated sequentially; assertion failures in lower-level file operations terminate the process.

State and persistence: creates or truncates each target with mode 0644 and writes deterministic content. No rollback exists if a later file fails.

Dependencies/integration: depends on `configuration.h` and `data_generator.h`. It is useful in integration tests needing known data on mounted LizardFS volumes.

Risks and test signals: large default size is 100 MiB, so test environments must budget disk space. Test signals are multi-file generation, explicit `FILE_SIZE` units, seeded body verification, and failure on unwritable targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_generate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_overwrite.cc -->
# sources/distributed-fs/lizardfs/utils/file_overwrite.cc

Purpose: command-line wrapper around `DataGenerator::overwriteFile()` for rewriting existing files with deterministic content while preserving their current size.

Important APIs/functions: reads `SEED` and `BLOCK_SIZE` through shared utilities, constructs a `DataGenerator`, and overwrites each file named on the command line.

Control flow: requires at least one path. For each file it stats the file to get size, opens it write-only, and writes the deterministic header/body pattern for that size. Lower-level assertions abort on stat/open/write/close failures.

State and persistence: mutates files in place and leaves their length unchanged because `overwriteFile()` opens without `O_TRUNC` and writes exactly `st_size` bytes. Existing content is fully replaced for regular files of at least eight bytes.

Dependencies/integration: paired with `file_generate` and `file_validate` in filesystem tests that want data churn without changing metadata size.

Risks and test signals: regular-file semantics are assumed; sparse files, concurrent writers, or files smaller than the 8-byte header can trigger assertion failures or partial writes. Test signals are preserving file size, validating overwritten content with the same seed, and expected failure on missing or read-only files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_overwrite.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_validate.cc -->
# sources/distributed-fs/lizardfs/utils/file_validate.cc

Purpose: command-line validator for files produced by `DataGenerator`.

Important APIs/functions: installs `SIGPIPE` ignore, reads `REPEAT_AFTER_MS` and `SEED`, then calls `DataGenerator::validateFile()` for each supplied path. Validation errors are caught per file and printed as `File <path>: <exception>`.

Control flow: no arguments prints usage and exits 1. Any validation failure sets aggregate return code 2, but later files are still checked. Repeat validation mode intentionally swallows an initial exception, sleeps, seeks back to start, and performs a decisive second validation.

State and persistence: read-only except for timing effects. It opens each file and closes it after validation.

Dependencies/integration: depends on `configuration.h`, `data_generator.h`, POSIX signal handling, and expected generated-file format. It is a test assertion binary for filesystem correctness.

Risks and test signals: first-pass errors are hidden when `REPEAT_AFTER_MS > 0`, so logs may not show transient corruption if the second pass succeeds. Test signals are clean files, corrupted header size, corrupted body byte, repeat-after cache behavior, multiple input aggregation, and SIGPIPE-safe use in pipelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_validate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_validate_growing.cc -->
# sources/distributed-fs/lizardfs/utils/file_validate_growing.cc

Purpose: validates a prefix/current length of a file that is still growing, using the same deterministic `DataGenerator` format.

Important APIs/functions: parses `<size>` with `UtilsConfiguration::parseIntWithUnit()`, ignores `SIGPIPE`, constructs `DataGenerator(seed)`, and calls `validateGrowingFile(path, FILE_SIZE)`.

Control flow: requires exactly `<file name> <size>`. On validation exception it prints the file name and exception text and exits 2; usage errors exit 1.

State and persistence: read-only. It opens the file and validates bytes through the requested size without requiring the embedded total-size header to match the current stat size.

Dependencies/integration: supports tests that read files while writers are still extending them, especially cache/coherency scenarios.

Risks and test signals: the underlying validator is sensitive to zero/too-small sizes and concurrent truncation. Because the requested size is trusted, tests should exercise sizes before and after block boundaries, partial final 8-byte words, and racing growth while validation is in progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/file_validate_growing.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/flockcmd.cc -->
# sources/distributed-fs/lizardfs/utils/flockcmd.cc

Purpose: interactive helper for testing BSD `flock()` behavior on a shared filesystem. It opens a file, takes a shared or exclusive advisory lock, prints state transitions, and waits for signals.

Important APIs/functions: global command maps translate `r` to `LOCK_SH` and `w` to `LOCK_EX`. Signal handlers: `SIGUSR1` unlocks, `SIGUSR2` reports interruption, and `SIGINT` closes the descriptor. `register_handler()` wraps `sigaction`.

Control flow: validates `path [r/w]`, opens the path read/write, prints `open`, calls blocking `flock(fd, cmd)`, prints `lock`, and then pauses. Signal handlers let tests orchestrate unlock/interrupt/close from another process.

State and persistence: holds a process-global fd and lock state. It does not write file data. Lock state is kernel/filesystem state and disappears on close/process exit.

Dependencies/integration: depends on `<sys/file.h>` and POSIX signals. It is used by shell/integration tests to observe flock semantics over LizardFS.

Risks and test signals: after an invalid command character it prints an error but does not immediately exit, so `commands[cmdno]` can default-insert zero. Signal handlers call non-async-signal-safe C++/stdio/string methods. Test signals are read/read compatibility, read/write and write/write exclusion, remote unlock via `SIGUSR1`, close via `SIGINT`, and behavior under signal interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/flockcmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/mfs_ping.cc -->
# sources/distributed-fs/lizardfs/utils/mfs_ping.cc

Purpose: simple network benchmark client that sends LizardFS/MooseFS `ANTOAN_PING` packets and measures round-trip latency.

Important APIs/functions: uses `tcpresolve`, `tcpsocket`, `tcpnodelay`, `tcpnumconnect`, `tcptowrite`, and `tcptoread` from LizardFS socket helpers. `serializeMooseFsPacket()` builds the ping packet with requested payload size.

Control flow: requires `host port bytes count usleep`. It resolves/connects, constructs one ping message, allocates a reply buffer of payload size plus 8-byte header, then loops `count` times measuring time around write/read with `gettimeofday()`. It prints each latency and an average.

State and persistence: no persistent state. Uses one TCP connection and in-memory buffers.

Dependencies/integration: integrates with `mfs_pingserv.cc` or any endpoint that responds with `ANTOAN_PING_REPLY` of matching size. It depends on protocol constants and serialization helpers.

Risks and test signals: `atoi` lacks robust range checking; `sassert(std::to_string(size) == argv[3])` rejects noncanonical numbers but not all invalid inputs gracefully. `count == 0` would divide by zero. Test signals are payload sizes including zero and large values, timeout behavior, average calculation, and interoperation with ping server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/mfs_ping.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/mfs_pingserv.cc -->
# sources/distributed-fs/lizardfs/utils/mfs_pingserv.cc

Purpose: simple LizardFS ping responder for use with `mfs_ping.cc`.

Important APIs/functions: opens a TCP listener on the requested port with `tcpsocket`, `tcpnodelay`, `tcpreuseaddr`, and `tcpstrlisten`. It parses 12-byte ping requests with `deserialize()` and emits replies with `serialize()`.

Control flow: accepts one client at a time. For each client, it reads exactly 12 bytes, expects `ANTOAN_PING` with 4-byte request payload length field, bounds requested reply payload below 2,000,000 bytes, builds an `ANTOAN_PING_REPLY` header, resizes the buffer to include zero-filled payload, and writes it. Read or write failure closes the client and returns to accept.

State and persistence: no persistence. Maintains per-client request/reply vectors and logs accepted connections to stderr.

Dependencies/integration: depends on LizardFS protocol and socket helpers. It is a benchmark/test peer, not production service code.

Risks and test signals: single-threaded accept loop can serve only one client at a time. Assertions abort on malformed input instead of returning protocol errors. Test signals are exact ping/reply framing, size bound enforcement, client disconnect handling, and repeated requests over one connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/mfs_pingserv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/mypy.ini -->
# sources/distributed-fs/lizardfs/utils/mypy.ini

Purpose: strict mypy configuration for Python utilities under this area, especially the Wireshark dissector generator.

Important settings: `disallow_untyped_defs = True` requires function annotations, `no_implicit_optional = True` keeps optional types explicit, `warn_return_any = True` surfaces imprecise return typing, and `warn_unused_configs = True` catches stale configuration.

Control flow/state: configuration-only; no runtime code or persistence.

Dependencies/integration: consumed by `mypy` when checking Python scripts. It applies a stricter policy than the legacy `make_dissector.py` style currently uses, so effective coverage depends on invocation scope and exclusions.

Risks and test signals: risk is drift between configured strictness and untyped historical scripts. Test signals are running `mypy` from this directory and confirming either intended failures or exclusions for generated/legacy scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/mypy.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/ping_pong.cc -->
# sources/distributed-fs/lizardfs/utils/ping_pong.cc

Purpose: byte-range lock latency/stress test inherited from Samba-style ping-pong locking. It repeatedly locks adjacent byte ranges in a shared file to measure lock manager throughput.

Important APIs/functions: `lock_range()` and `unlock_range()` use blocking `fcntl(F_SETLKW)`. `ping_pong()` truncates the file, optionally mmaps it, initializes per-byte state, locks byte 0, then loops up to `kLoopLimit` acquiring the next byte lock, optionally reading/writing one byte, unlocking the previous byte, and printing locks/sec once per second.

Control flow: CLI options `-r`, `-w`, and `-m` enable reads, writes, and mmap. Required arguments are `<file> <num_locks>`. The lock cursor advances modulo `num_locks`, so multiple processes running the same command contend over the same ring.

State and persistence: mutates the test file length to `num_locks + 1`; optional writes update one-byte counters. Lock state is advisory and process-held.

Dependencies/integration: tests filesystem lock manager behavior, especially distributed lock managers. Uses POSIX file locks, pread/pwrite, and mmap.

Risks and test signals: `num_locks <= 0` is not guarded and can cause modulo errors. mmap path does not call `msync` or `munmap`. Test signals are multiple concurrent instances, read/write/mmap modes, lock throughput output, and error paths for unsupported locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/ping_pong.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/posixlockcmd.cc -->
# sources/distributed-fs/lizardfs/utils/posixlockcmd.cc

Purpose: interactive helper for testing POSIX byte-range `fcntl()` locks.

Important APIs/functions: maps `r` to `F_RDLCK` and `w` to `F_WRLCK`; initializes a global `struct flock` with `SEEK_SET`. Signal handlers unlock (`SIGUSR1`), report interruption (`SIGUSR2`), or close (`SIGINT`). Optional start and length arguments set `l_start` and `l_len`.

Control flow: validates `path [r/w/u]` shape, opens the file read/write, fills lock metadata, calls blocking `fcntl(fd, F_SETLKW, &lock)`, prints state, and pauses for signal-driven orchestration.

State and persistence: no file data persistence; it holds a POSIX advisory lock over the requested byte range until unlock/close/exit. Global variables carry fd/path/lock state.

Dependencies/integration: complements `flockcmd.cc` for tests that need POSIX record-lock semantics rather than BSD whole-file locks.

Risks and test signals: usage mentions `u` but command validation only accepts `r`/`w`, and invalid command handling does not immediately exit. Signal handlers use non-async-signal-safe operations. Test signals are shared/exclusive record lock interactions, byte-range overlap/non-overlap, unlock signal behavior, and lock visibility across clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/posixlockcmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/readdir_unlink_test.cc -->
# sources/distributed-fs/lizardfs/utils/readdir_unlink_test.cc

Purpose: filesystem behavior test for interleaving `readdir()` with `unlink()` in the same directory. It validates that a directory iteration can still remove all previously created entries.

Important APIs/functions: `create_files()` creates numeric empty files. `unlink_files_in_readdir_loop()` opens `"."`, repeatedly calls `readdir()`, skips dot entries, and unlinks each returned file. `remove_empty_dir()` attempts `rmdir()` and treats `ENOTEMPTY` as a logical failure rather than infrastructure error.

Control flow: `main()` optionally accepts file count and workspace path, opens the workspace with `O_PATH|O_DIRECTORY`, `fchdir()`s into it, creates `test-dir`, changes into it, creates files, unlinks while reading, returns to the original directory, and removes `test-dir`. Exit 0 means created count equals unlinked count and `rmdir` succeeded; exit 1 means entries were missed; exit 2 means syscall error.

State and persistence: creates and deletes a temporary `test-dir` in the workspace. On failures, partial files/directories may remain for inspection.

Dependencies/integration: useful for FUSE/distributed directory consistency testing. Depends on Linux `O_PATH`, dirent APIs, and exception wrapping via `std::system_error`.

Risks and test signals: fixed directory name can collide with existing `test-dir`. `sync()` slows tests globally. Test signals are high file counts, workspace errors, ENOTEMPTY failure, and behavior under distributed metadata caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/readdir_unlink_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/redirect_bind.c -->
# sources/distributed-fs/lizardfs/utils/redirect_bind.c

Purpose: LD_PRELOAD library that intercepts `bind()` and shifts nonzero TCP stream ports by +1000. It lets tests transparently relocate services away from default ports.

Important APIs/functions: overridden `bind()` copies the supplied `sockaddr` as `sockaddr_in`, checks `SO_TYPE` with `getsockopt`, increments `sin_port` for `SOCK_STREAM` sockets with nonzero ports, lazily resolves the real `bind` with `dlsym(RTLD_NEXT, "bind")`, and calls it.

Control flow: all sockets pass through one wrapper. Only IPv4-shaped `sockaddr_in` and stream sockets are modified; zero port requests remain ephemeral.

State and persistence: no persistent state. A static function pointer caches the real symbol.

Dependencies/integration: intended for test environments using `LD_PRELOAD`. Depends on GNU dynamic linker and IPv4 socket layout.

Risks and test signals: casts every `sockaddr` to `sockaddr_in`, so IPv6 or Unix-domain bind calls can be misinterpreted before `getsockopt` determines type. Port addition can exceed 65535 and wrap through `htons`. Test signals are TCP port shift, UDP no-op, port zero no-op, and non-IPv4 socket safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/redirect_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/slow_chunk_scan.c -->
# sources/distributed-fs/lizardfs/utils/slow_chunk_scan.c

Purpose: LD_PRELOAD test shim that slows directory scans except for selected chunk storage directories. It exercises timeout and scheduling behavior during chunk scanning.

Important APIs/functions: overrides `opendir`, `readdir_r`, and `closedir`. `opendir()` records `DIR*` handles whose path contains one of `hdd_0_0` through `hdd_3_0` in a fixed `fast_dir` table. `readdir_r()` sleeps one second unless the handle is in the fast table. `closedir()` removes handles from the table.

Control flow: every opened directory is checked for fast path substrings. `readdir_r()` holds a mutex while scanning the handle table, then either sleeps or proceeds to the real `readdir_r`.

State and persistence: process-local static array of up to 5000 fast directory handles, protected by `pthread_mutex_t`. No persistent output.

Dependencies/integration: intended for Linux/glibc test processes via `LD_PRELOAD`. It targets code paths still using `readdir_r`.

Risks and test signals: `readdir_r` is deprecated in modern libc. The fixed table silently stops tracking fast dirs once full. If `opendir` fails and returns NULL, NULL may be recorded for matching paths. Test signals are slow scans for generic dirs, fast scans for named hdd paths, handle cleanup on `closedir`, and concurrent scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/slow_chunk_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/CMakeLists.txt

Purpose: Wireshark plugin build file for the generated LizardFS dissector.

Important declarations: includes `WiresharkPlugin`, sets module info `lizardfs 1.0.0.0`, declares `packet-lizardfs.c` as the dissector source, registers plugin files, builds `add_library(lizardfs ${LINK_MODE_MODULE} ...)`, removes the library prefix, applies Wireshark link flags, links against `epan`, and installs into Wireshark's plugin directory under package name/version.

Control flow: configure-time CMake logic optionally applies `-Werror` when `WERROR` is set, registers the plugin entry points, and emits a module suitable for Wireshark plugin loading.

State and persistence: generated build artifacts are outside this file. It assumes `plugin.c` and `packet-lizardfs.c` exist, with `packet-lizardfs.c` generated by `generate.sh`.

Dependencies/integration: tightly coupled to Wireshark's plugin CMake API, GLib/epan APIs, and the generated dissector source.

Risks and test signals: Wireshark plugin APIs change between versions, so build compatibility is the main risk. Test signals are CMake configure against supported Wireshark versions, plugin load, dissector registration for LizardFS TCP ports, and `WERROR` clean builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_chunktype-inl.h -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_chunktype-inl.h

Purpose: generated/static value-string include fragment for Wireshark display of LizardFS chunk type values.

Important data: maps `0` to `standard`, then encodes XOR parity and data-part chunk types for levels 2 through 10. Values follow the formula used elsewhere in LizardFS: parity at `(max_xor_level + 1) * level`, data parts immediately after parity.

Control flow/state: data-only include intended to be placed inside a `value_string` array. It does not include header guards because it is an inline initializer fragment.

Dependencies/integration: included by `make_dissector.py` generated code as `dict_chunktype-inl.h` for the external dictionary field `chunktype`.

Risks and test signals: risks are drift from core `ChunkType` numeric assignments and missing future erasure/replication formats. Test signals are generated dissector compile, correct display of standard and XOR chunk names in packet Info and tree columns, and alignment with `chunk_converter.cc` header byte 20 values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_chunktype-inl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_goal-inl.h -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_goal-inl.h

Purpose: value-string include fragment for LizardFS goal codes in Wireshark.

Important data: maps replication goals 1 through 9 to `goal1`..`goal9`, and XOR goals 255 down to 247 to `xor2`..`xor10`.

Control flow/state: data-only initializer fragment without guards. It is consumed inside generated C arrays.

Dependencies/integration: included by `make_dissector.py` generated code for `goal` fields, which are listed as externally-dictionaried fields.

Risks and test signals: risks are protocol drift if goal encodings change or new storage classes are added. Test signals are packet dissection for file attributes or set-goal messages containing normal and XOR goal values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_goal-inl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate.sh -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate.sh

Purpose: generator wrapper for the LizardFS Wireshark plugin sources.

Important operations: requires a path to `MFSCommunication.h`, canonicalizes it with `readlink -m`, changes to the plugin directory, writes `includes.h` with protocol constants and an include of the input header, then runs `python3 make_dissector.py < "$input_file" > packet-lizardfs.c`.

Control flow: usage validation requires exactly one argument. `set -eu` stops on missing variables and command failures. The generated `includes.h` defines `PROTO_BASE`, `MFSBLOCKSINCHUNK`, `MFSBLOCKSIZE`, and `LIZARDFS_WIRESHARK_PLUGIN` to make protocol macros parse/build outside the main tree.

State and persistence: overwrites `includes.h` and `packet-lizardfs.c` in the plugin directory.

Dependencies/integration: depends on Bash, GNU `readlink -m`, Python 3, the protocol header format, and `make_dissector.py`.

Risks and test signals: generated files are only as accurate as protocol comments/macros in `MFSCommunication.h`. Test signals are regeneration after protocol changes, generated C compilation, and stable diffs when input is unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate_sequence_diagram.sh -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate_sequence_diagram.sh

Purpose: Bash helper that extracts protocol command names from `MFSCommunication.h` and prints sequence-diagram text showing sender-to-receiver message flow.

Important data/functions: maps protocol tokens `AN`, `CL`, `CS`, `MA`, `ML`, and `TS` to participant names. `print_header()` emits title and participants. `get_search_pattern()` builds a sender/receiver regex from active tokens. `get_transformation_pattern()` converts command names like `CLTOMA_*` into `CLIENT->MASTER:...`. `extract_sequence()` greps `#define` names, filters by token pattern, and applies sed transformations.

Control flow: accepts `path/to/MFSCommunication.h` followed by optional `PARTICIPANTS=...` and `ACTIONS=...` filters. It filters participant tokens before generating the regex and optionally filters emitted actions.

State and persistence: no files are written; output goes to stdout.

Dependencies/integration: depends on Bash associative arrays, `egrep`, `awk`, and `sed -E`. Output format is suitable for text sequence diagram tools.

Risks and test signals: argument parsing treats the source path as an `ARGUMENT` too but ignores unrecognized keys; values containing `=` are not handled. `set -e` is not enabled, and `grep` failures inside participant filtering can be surprising. Test signals are full protocol extraction, participant-limited diagrams, action filters, and LIZ-prefixed command handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate_sequence_diagram.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/make_dissector.py -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/make_dissector.py

Purpose: Python source generator that parses annotated LizardFS protocol definitions and emits a Wireshark C dissector.

Important APIs/classes: `Types` maps internal integer/string/blob kinds to Wireshark field types, bases, and tvbuff getters. `PacketDissectionVariant` tracks one packet layout variant, with byte positions, variable-length expressions, optional variant condition, and field metadata. Methods such as `add_int_field`, `add_string8_field`, `add_string32_field`, `add_blob_field`, `condition`, `get_info()`, and `print_method()` drive generated C output.

Control flow: stdin is scanned line by line. Packet macros matching `(LIZ_)?(AN|CS|CL|MA|ML|TS)TO...` start new dissections and populate the `type` dictionary. `/// field values: name` blocks build dictionaries. Other `///` lines define packet variants with fields like `name:32`, `NAME`, `STDSTRING`, `STRING[n]`, `BYTES[n]`, and conditional selectors. LIZ messages default to `version == 0` when no condition is present. After parsing, the script prints includes, globals, dictionaries, one C method per variant, dispatch switches by message type, TCP PDU framing, preference registration for ports 9419-9422, and field registration.

State and persistence: no files are directly written; generated C is stdout. Internal dictionaries aggregate type and field metadata, and field type consistency is enforced.

Dependencies/integration: depends on protocol header comments following the expected annotation grammar and on Wireshark C APIs such as `tcp_dissect_pdus`, `proto_tree_add_item`, and preference ranges. External chunk type and goal dictionaries are included by name.

Risks and test signals: generated C is vulnerable to unsanitized field names from comments, and parser errors terminate generation. Some code contains historical typos but is functional. Variable-length fields and unknown variants are key risk areas. Test signals are generation from the current protocol header, C compiler warnings, dissector behavior for fixed/variable payloads, malformed length handling, dictionary display, and large/LIZ packet version dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/make_dissector.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/moduleinfo.h -->
# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/moduleinfo.h

Purpose: Wireshark plugin metadata header for the LizardFS dissector module.

Important content: defines package string as `lizardfs`, major/minor/micro version `1.0.0`, and empty `VERSION_FLAVOR`. It includes the standard Wireshark GPL header comments.

Control flow/state: metadata-only header. It does not declare functions or persistent state.

Dependencies/integration: consumed by Wireshark plugin build/registration conventions alongside `CMakeLists.txt` and generated `plugin.c`/`packet-lizardfs.c`.

Risks and test signals: version drift is the main risk; plugin packaging should match the CMake `set_module_info(lizardfs 1 0 0 0)`. Test signals are successful plugin build and Wireshark module metadata display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/moduleinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/api.h -->
# sources/distributed-fs/lustre-release/include/linux/lnet/api.h

Purpose: kernel-only public LNet API header. It exposes initialization, addressing, match-entry, memory-descriptor, data movement, and control operations for Lustre Networking.

Important APIs/types: initialization uses `LNetNIInit()` and `LNetNIFini()`. Addressing helpers include `LNetGetId`, `LNetDist`, primary/local NID helpers, peer-local/discovery checks, NID fetch callbacks, local-net checks, and NID update callback registration. Match and memory APIs include `LNetMEAttach`, `LNetMDAttach`, `LNetMDBind`, and `LNetMDUnlink`. Data movement uses asynchronous `LNetPut` and `LNetGet` over portals/match bits and MD handles. Misc APIs cover lazy portals, generic `LNetCtl`, peer debugging, peer discovery status, and peer insertion.

Control flow: this header is declarative; implementations manage LNet lifecycle, portal/match tables, MD ownership, and asynchronous completion events. API users must initialize LNet before calls and bind/attach memory before PUT/GET operations.

State and persistence: API calls operate on kernel-global LNet state and transient handles. No on-disk persistence is defined.

Dependencies/integration: includes `uapi/linux/lnet/lnet-types.h`, rejects non-kernel inclusion, and is consumed by Lustre kernel modules and LNDs.

Risks and test signals: risks are lifecycle misuse, stale MD handles, incorrect large-NID handling, and data movement without matching portals. Test signals are NI init/fini refcounting, NID enumeration, ME/MD attach/unlink events, PUT/GET success/failure paths, lazy portal behavior, and peer discovery callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lib-cpt.h -->
# sources/distributed-fs/lustre-release/include/linux/lnet/lib-cpt.h

Purpose: CPU partition table abstraction for Lustre/LNet. It maps CPUs/NUMA nodes into configurable CPU partitions and provides allocation, affinity, and iteration helpers.

Important APIs/types: under `CONFIG_SMP`, it declares `struct cfs_cpt_table *cfs_cpt_tab`, table allocation/free/print/distance APIs, CPU/node mask accessors, CPU/node-to-CPT mapping, bind functions, CPU/node set/unset operations, core include/exclude helpers, and CPU subsystem init/fini. Non-SMP builds provide inline single-partition stubs. Allocation helpers include `cfs_cpt_malloc`, `cfs_cpt_vzalloc`, `cfs_page_cpt_alloc`, and `cfs_mem_cache_cpt_alloc`. `cfs_cpt_bind_workqueue()` allocates an unbound workqueue and applies a CPT cpumask.

Control flow: modules use CPT tables to choose locality for locks, memory, workqueues, and network processing. Pattern/module parameters `cpu_npartitions` and `cpu_pattern` drive global layout outside this header.

State and persistence: runtime state is in CPT tables and module parameters; nothing persists across reboot/module unload.

Dependencies/integration: depends on Linux CPU, cpuset, topology, slab/vmalloc, NUMA node APIs, and Lustre compatibility workqueue wrappers. LNet uses it for `ln_cpt_table`, per-CPT locks, counters, and queues.

Risks and test signals: workqueue affinity must be updated under `cpus_read_lock`; allocation helpers rely on `cfs_cpt_spread_node()` returning valid NUMA nodes. Non-SMP stubs should preserve semantics. Test signals are pattern parsing, hotplug/online CPU behavior, NUMA distance output, per-CPT memory placement, and workqueue cpumask application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lib-cpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lib-lnet.h -->
# sources/distributed-fs/lustre-release/include/linux/lnet/lib-lnet.h

Purpose: top-level internal LNet library header. It ties together global state (`the_lnet`), locking, handle lookup, NI/peer/message lifecycle helpers, routing, portals, fault injection, sockets, discovery, recovery, and stats.

Important APIs/functions: inline helpers cover wire-handle validation, MD exhaustion/unlinkability, cookie-to-CPT mapping, resource/net locks, NI status get/set, MD wait/free, handle-to-MD lookup, refcount helpers for peers/NIs, message and response tracker allocation, NID hashing, network hash lookup, and header conversions for nid4/nid16 wire forms. Declarations cover `lnet_configure`, NI/net allocation/free, route add/delete/get, router buffer pools, dynamic net/NI add/delete, message attach/commit/send/receive/finalize, portal/match-table operations, fault rule management, counters, LND registration, acceptor/socket helpers, ping buffer/discovery, peer table operations, health adjustment, UDSP parsing, and notifier integration.

Control flow: LNet operations typically enter through public APIs, select CPT/locks, allocate messages/MDs, resolve local NI and peer/route, commit credits, call LND send/recv, and finalize events. Discovery and monitor threads handle peer push/ping, router checks, recovery queues, response timeouts, and resend queues.

State and persistence: all state is in kernel memory: `the_lnet`, per-CPT locks/containers/counters, peer tables, routes, queues, LND registrations, ping buffers, fault rules, and module parameters. No on-disk persistence.

Dependencies/integration: includes public and internal LNet/UAPI headers, Linux networking APIs, libcfs debug/private APIs, and Lustre lock compatibility. It is the central integration point for LND implementations and LNet core source files.

Risks and test signals: concurrency and lifetime are primary risks: resource locks, peer refcounts, MD handler races, response tracker zombies, route/health updates, and dynamic config changes. ABI risks exist around nid4/nid16 conversion and netlink/ioctl structures. Test signals are init/unconfigure cycles, concurrent PUT/GET/finalize, route failover, peer discovery push/ping, dynamic NI add/delete, fault injection, response timeout/resend, and lockdep coverage for documented lock nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lib-lnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lib-types.h -->
# sources/distributed-fs/lustre-release/include/linux/lnet/lib-types.h

Purpose: internal kernel-only type system for LNet core. It defines message, MD/ME, LND, NI, net, peer, route, portal, resource container, discovery, UDSP, netlink attribute, and global `struct lnet` state.

Important APIs/types: early helpers parse NID/net expression lists. `lnet_msg` carries target/source NIDs, deadlines, health status, retry state, TX/RX commitment flags, credit flags, peer/NI pointers, MD payload vectors, event, and header. `lnet_libmd` and `lnet_me` model memory descriptors and match entries, with flags for zombie, auto-unlink, aborted, handling, and GPU. `lnet_lnd` is the driver interface with startup/shutdown/control, send/recv/eager_recv, accept, tunables, netlink, device priority, and metadata callbacks. Network state is represented by `lnet_net`, `lnet_ni`, `lnet_peer`, `lnet_peer_net`, `lnet_peer_ni`, `lnet_route`, and `lnet_remotenet`. Portal matching uses `lnet_match_table`, `lnet_portal`, and rotor modes. `struct lnet` aggregates CPTs, locks, portals, MD containers, message containers, counters, peer tables, nets, routes, ping/push buffers, discovery and monitor queues, UDSP rules, update callbacks, and workqueues.

Control flow: types encode the core runtime graph. Messages flow through peers/NIs, consume credits, match portals/MDs, and finalize events. Discovery updates peer/ping data; recovery queues drive health repair; router buffer pools mediate forwarding.

State and persistence: entirely volatile kernel state. Atomic counters, krefs, spinlocks, lists, semaphores, completions, and workqueues define lifetime and concurrency boundaries.

Dependencies/integration: depends on Linux bvec/uio/kthread/kref/generic-radix-tree, Lustre netlink compatibility, UAPI LNet control headers, and `nidstr.h`. It must stay synchronized with user-space liblnetconfig for UDSP structures and netlink attributes.

Risks and test signals: high-risk areas are list/refcount ownership, lock ordering, peer discovery state bits, ping buffer size math for large NIDs, health transitions, route aliveness, response tracker zombies, and UAPI/netlink field drift. Test signals are struct layout assertions where exposed, large-NID ping validation, peer/route lifecycle stress, dynamic config with concurrent traffic, fault rules, portal matching, and teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lib-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lnet_crypto.h -->
# sources/distributed-fs/lustre-release/include/linux/lnet/lnet_crypto.h

Purpose: kernel internal crypto helper declarations for LNet/libcfs hashing.

Important APIs/functions: `cfs_crypto_hash_init()` creates an async hash request for an algorithm and optional key. `cfs_crypto_hash_update_page()` and `cfs_crypto_hash_update()` feed page or linear data. `cfs_crypto_hash_final()` completes the digest. `cfs_crypto_register()`/`cfs_crypto_unregister()` manage algorithm registration/lifecycle, and `cfs_crypto_hash_speed()` reports measured speed.

Control flow: callers select an algorithm from the UAPI enum, initialize a request, perform one or more updates, finalize into a hash buffer, and release/cleanup through implementation-specific behavior.

State and persistence: no persistent state in the header. Implementations maintain crypto API registrations and speed tables.

Dependencies/integration: includes `<asm/page.h>` and `uapi/linux/lnet/lnet-crypto.h`, integrating kernel crypto operations with the shared algorithm descriptors.

Risks and test signals: risks include unsupported algorithms, key length mismatch, page offset/length errors, async crypto failure, and digest buffer sizing. Test signals are each enum algorithm, page and linear updates, digest-size reporting, registration/unregistration, and speed table population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lnet_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lnet_rdma.h -->
# sources/distributed-fs/lustre-release/include/linux/lnet/lnet_rdma.h

Purpose: RDMA/GPU-direct integration header for LNet. It defines or imports NVFS DMA hooks and exposes LNet wrappers for device priority, scatterlist mapping, and GPU page detection.

Important APIs/types: when `WITH_EXTERNAL_GDS_HEADER` is not set, it defines `struct nvfs_dma_rw_ops` with callbacks for block request SG mapping, DMA map/unmap, GPU page detection, GPU index, and device priority. Feature bits and `NVIDIA_FS_CHECK_FT_*` macros advertise supported operations. Symbol-generation macros create versioned registration names `lustre_v1_register_nvfs_dma_ops` and `lustre_v1_unregister_nvfs_dma_ops`. LNet wrappers include `lnet_get_dev_prio`, `lnet_rdma_map_sg_attrs`, `lnet_rdma_unmap_sg`, `lnet_is_rdma_only_page`, and `lnet_get_dev_idx`.

Control flow: vendor/driver code registers an operations table; LNet checks feature bits and routes DMA mapping/unmapping or GPU page classification through registered callbacks, falling back to CPU paths when unavailable.

State and persistence: runtime registration state is external to this header and volatile.

Dependencies/integration: depends on Linux DMA, block, scatterlist, cpumask, and page APIs. It integrates Lustre networking with NVIDIA GPUDirect Storage style hooks.

Risks and test signals: risks include stale external header ABI, missing feature bits, wrong DMA direction, unbalanced map/unmap, and GPU-page misclassification. Test signals are registration/unregistration, CPU fallback, GPU page send/receive paths, DMA_ATTR_NO_WARN compatibility, and device priority selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/linux/lnet/lnet_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_debug.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_debug.h

Purpose: user/kernel ABI definitions for Lustre/libcfs debug records, subsystem bits, and debug mask bits.

Important APIs/types: `struct ptldebug_header` is a packed record header containing length, flags, subsystem, mask, CPU/type, timestamp seconds/usec, stack, PID fields, and source line. `PH_FLAG_FIRST_RECORD` marks first records. `enum libcfs_debug_subsys` defines 32 non-overlapping subsystem bits such as MDC, MDS, OSC, OST, LNET, LND, LDLM, LOV, OSD, MGS, FID, and FLD. `enum libcfs_debug_masks` defines trace/info/error/network/config/etc. mask bits. Name macros provide ordered string lists for display tools.

Control flow/state: no executable control flow. Log writers populate packed headers; readers interpret bitmasks and names consistently across kernel/user space.

Dependencies/integration: included by debug tools and kernel code; relies on fixed-width Linux types and packed layout.

Risks and test signals: ABI risk is high because changing enum bit positions or packed struct layout breaks log parsers. Timestamp comment notes 2106 overflow for 32-bit seconds. Test signals are binary log parse compatibility, default mask/subsystem expansion, and name-array ordering against bit positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_ioctl.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_ioctl.h

Purpose: low-level ioctl ABI for libcfs/LNet control operations.

Important APIs/types: `LNET_IOCTL_VERSION` and `LNET_IOCTL_VERSION2` version payload formats. `libcfs_ioctl_hdr` carries length/version. `libcfs_ioctl_data` is the legacy flexible container with NID, u32/u64 arrays, inline buffer lengths/pointers, userspace buffers, and trailing bulk data. Macros define ioctl command numbers for debug, NI queries, fail/discover/ping/fault operations, LND connection/peer/interface commands, and dynamic LNet configuration commands through `IOC_LIBCFS_MAX_NR`.

Control flow: user tools fill a versioned header/container and call ioctls; kernel dispatch uses command numbers and copies inline or userspace bulk buffers.

State and persistence: no persistence. Operations mutate/query kernel LNet state depending on command.

Dependencies/integration: includes Linux ioctl/types and defines `__user` for sparse compatibility. Later DLC structures referenced by command sizes are declared in `lnet-dlc.h`.

Risks and test signals: comments state older ioctl definitions are broken in their `_IOWR` type/size usage, so compatibility must be preserved. Pointer fields make 32/64-bit compatibility and copy bounds important. Test signals are version validation, max data size enforcement, compat ioctls, every command number remaining stable, and safe handling of user pointers/bulk lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-crypto.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-crypto.h

Purpose: shared crypto algorithm descriptors and helpers for LNet/libcfs.

Important APIs/types: `cfs_crypto_hash_type` maps hash algorithm names to default key and digest size. `cfs_crypto_crypt_type` maps cipher names to key sizes. Hash enum includes null, adler32, crc32, crc32c, md5, sha1, sha256, sha384, sha512, max, speed-test cutoff, and unknown. Crypt enum includes null and AES-256 CTR. Static descriptor arrays define names/sizes. Inline helpers return type, name, digest/key size, and enum lookup by name. `cfs_crypto_hash_digest()` declares a one-shot digest API.

Control flow: lookup helpers validate enum bounds and descriptor names, then return metadata or fallback values such as `"unknown"` and zero sizes.

State and persistence: static descriptor arrays are compiled into each including translation unit; `cfs_crypto_hash_speeds` is extern runtime state.

Dependencies/integration: included by kernel and possibly user ABI consumers; relies on Linux types and string functions.

Risks and test signals: static non-const arrays in a UAPI header can create duplicate mutable definitions in multiple translation units. Lookup functions call `strcmp(hash_types[hash_alg].cht_name, algname)` without checking null for all enum slots, though current loop excludes `CFS_HASH_ALG_MAX`. Test signals are name/enum round trips, digest-size max, speed-tested subset, unknown values, and one-shot digest behavior for each algorithm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-dlc.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-dlc.h

Purpose: Dynamic LNet Configuration UAPI for ioctl and generic netlink management of networks, NIs, routes, peers, buffers, health, UDSP, and fault controls.

Important APIs/types: defines generic netlink name/version and `enum lnet_commands` for configure, nets, peers, routes, conns, ping, CPT-of-NID, peer distance, UDSP, peer fail, debug recovery, fault, routing, buffers, and NUMA. Structures cover common and LND-specific tunables (`o2ib`, `sock`, `kfi`, `efa`, `gni`), NI/net config, router buffer pools, ping data, route/net/buffer config union, communication and message stats, local/peer health stats, NI config with CPT/interface/bulk, peer config and credit info, health reset, connection-per-peer reset, recovery lists, LNet stats, UDSP expression descriptors, UDSP rule/action payloads, and constructed UDSP info.

Control flow: user tools marshal these structs into ioctl or netlink requests; kernel code validates headers/version/counts, copies bulk arrays, and mutates/query LNet dynamic state.

State and persistence: structures represent runtime LNet state and configuration; persistence is external to user tooling, not in the ABI.

Dependencies/integration: includes `libcfs_ioctl.h` and `lnet-types.h`. Several comments require append-only structure evolution for backward compatibility with old `lnetctl`.

Risks and test signals: ABI layout, flexible arrays, user pointers, bitfields, fixed array limits, and append-only versioning are high-risk. Test signals are old/new lnetctl compatibility, per-LND tunable round trips, bulk length validation, UDSP marshal/unmarshal symmetry, peer/route/list pagination limits, and 32/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-dlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-idl.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-idl.h

Purpose: wire-format IDL for core LNet messages, NIDs, handles, protocol magic/version values, counters, NI status, metadata, and ping information.

Important APIs/types: `lnet_nid_t` is the legacy 64-bit NID. `struct lnet_nid` is the extended packed NID supporting up to 128-bit address and ANY wildcard. `lnet_process_id_packed`, `lnet_handle_wire`, message type enum, command structs (`lnet_ack`, `lnet_put`, `lnet_get`, `lnet_reply`, `lnet_hello`), `lnet_hdr`, and nid4 wrapper types define wire headers. Protocol magic constants cover IB, GNI, TCP, KFI, acceptor, ping, EFA, and placeholder unified protocol. Acceptor v1/v2 structs support legacy and large NIDs. Counter/status structs support LNet stats and ping replies. Ping feature bits advertise NI status, routing, multi-rail, discovery, large address, primary-large, and metadata support.

Control flow: LNDs exchange HELLO/acceptor messages, convert between network buffers and host-order `lnet_hdr`, and use ping info to discover peer NIs/features. `lnet_ping_info_size()` computes variable ping size based on large-address feature.

State and persistence: wire structs are transient network data, but ABI/wire layout is persistent protocol contract.

Dependencies/integration: included by UAPI type headers and internal conversion helpers in `lib-lnet.h`. Packed/fixed-width layout is central to interoperability.

Risks and test signals: changing field order, packing, endian expectations, or feature bits breaks wire compatibility. Large-NID size math and `pi_ni[0].ns_msg_size` validation are sensitive. Test signals are wire constant assertions, endian conversion tests, legacy nid4 interoperability, acceptor v1/v2 negotiation, ping feature validation, and malformed large-address ping buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-idl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-nl.h -->
# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-nl.h

Purpose: shared scalar-key netlink helper definitions for LNet.

Important APIs/types: `enum lnet_nl_key_format` flags describe whether a key is flow/block and mapping/sequence. `enum lnet_nl_scalar_attrs` defines generic nested scalar-list attributes: list, list size, index, nla type, string value, integer value, and key format. `ln_key_props` describes one scalar key with value string, key format, and data type. `ln_key_list` contains a max attribute and flexible array of key properties.

Control flow/state: declarative UAPI only. Internal code in `lib-types.h` defines `scalar_attr_policy` and `lnet_genl_send_scalar_list()` to serialize these definitions through generic netlink.

Dependencies/integration: used by LNet generic netlink code and user tools that need stable scalar lists for changing LNet netlink ABI.

Risks and test signals: flexible-array layout and string pointers are not directly wire-safe; kernel code must translate to netlink attributes rather than exposing raw pointers. Test signals are scalar list encoding/decoding, max attribute bounds, padding handling, and user-space compatibility across added keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-nl.h -->

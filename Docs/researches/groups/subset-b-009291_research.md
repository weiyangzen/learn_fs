# subset-b-009291 research

Grouped research report for LTP filesystem doio, fs_bind, and related filesystem stress files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/iogen.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/iogen.c

Purpose: random I/O request generator for the legacy LTP `doio` stress pipeline. It parses command-line ranges, creates or sizes target files, chooses syscall/open-flag/offset combinations, and emits binary `struct io_req` records with `DOIO_MAGIC` to stdout or a FIFO.

Important APIs/types/functions: `main`, `parse_cmdline`, `form_iorequest`, `get_file_info`, `create_file`, `init_output`, `startup_info`, `str_lookup`, `value_to_string`, `struct file_info`, `struct strmap`, `Syscall_Map`, `Flag_Map`, and `Omode_Map`. It integrates helpers from `doio.h`, `random_range.h`, `open_flags.h`, `string_to_tokens.h`, and byte-size parsing.

Control flow: startup clears umask, probes platform support, parses options, opens stdout/FIFO output, seeds `random_range`, prints configuration unless quiet, then loops by count, time, or forever. Each iteration chooses a syscall, file, open flag profile, transfer size, offset mode (`sequential`, `reverse`, `random`), optional overlap, and async completion strategy before writing one packed request structure.

State/persistence behavior: persistent state includes files created or resized from `[len:]file` arguments and FIFO output created by `-p`. In-memory state tracks per-file last offset/length so sequential, reverse, random, and overlap modes can generate related requests. On SGI/Cray paths it can request raw, realtime, reserve, or allocate behavior; Linux defaults to buffered and sync I/O with 512-byte raw alignment.

Dependencies/integration: intended to be piped into `${{LTPROOT}}/testcases/bin/doio`, and commonly launched by `rwtest`. It depends on platform `open(2)`, `stat(2)`, `fcntl(2)`, `lseek(2)`, `write(2)`, filesystem semantics, and the binary layout in `doio.h`.

Risks/test signals: binary protocol changes must stay synchronized with `doio`. Alignment and file-size validation are critical; too-small files are ignored, and all files being rejected is a fatal condition. Some platform options are disabled on Linux. Success is a stream of valid request records; failures are stderr diagnostics, nonzero exits, or downstream `doio` errors.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/iogen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/open_flags.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/open_flags.c

Purpose: converts symbolic `open(2)` flag lists to integer bitmasks and converts bitmasks back to symbolic text for diagnostics in the doio tools.

Important APIs/types/functions: `parse_open_flags`, `openflags2symbols`, static `Open_flags[]`, static return buffer `Open_symbols`, `UNKNOWN_SYMBOL`, and optional `UNIT_TEST` main. The table conditionally includes platform flags such as `O_DIRECT`, `O_LARGEFILE`, `O_RAW`, `O_SSD`, `O_PARALLEL`, and legacy SGI/Cray values when available.

Control flow: `parse_open_flags` walks comma-separated tokens in place, temporarily null-terminates each token, searches `Open_flags`, ORs matched bits, restores the separator, and returns `-1` plus the bad token pointer on an unknown symbol. `openflags2symbols` handles the implicit `O_RDONLY` case, consumes matching bits from the bitmask, joins names with the caller separator, and optionally appends `UNKNOWN`.

State/persistence behavior: no filesystem state is changed. The conversion-to-string path writes a process-global static buffer, so the result is overwritten by subsequent calls and is not thread-safe.

Dependencies/integration: used by `iogen` option parsing and by doio diagnostics that need readable open flags. It depends on `<fcntl.h>` feature macros so the symbol table varies by target platform.

Risks/test signals: adding new kernel open flags without updating this table yields `UNKNOWN` output or parse failures. `parse_open_flags` mutates the input buffer while parsing, even though it restores separators. Optional unit testing accepts either numeric bitmasks or symbolic lists and prints the conversion result.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/open_flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/pattern.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/pattern.c

Purpose: fills buffers with a repeating byte pattern and verifies that a buffer still matches that repeated pattern at a given shift. The routines are small data-integrity helpers for doio read/write validation.

Important APIs/types/functions: `pattern_fill`, `pattern_check`, `memcmp`, `memcpy`, `patlen`, and `patshift`.

Control flow: both functions normalize `patshift` modulo `patlen`, handle the split first pattern copy/compare when the shift is nonzero, then use a doubling-style copy/compare against the already-filled prefix to cover the rest of the buffer efficiently.

State/persistence behavior: all state is caller-owned memory. `pattern_fill` modifies `buf`; `pattern_check` reads `buf` and returns `0` on match or `-1` on mismatch. No global or persistent state is used.

Dependencies/integration: included through `pattern.h` by doio data paths that need deterministic write patterns and later verification.

Risks/test signals: callers must provide a nonzero pattern length for meaningful operation; a zero pattern length would make the first transfer length equal to zero and risk a non-progressing loop. The direct signal is `0` for valid data and `-1` for corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/pattern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/rwtest -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/rwtest

Purpose: shell wrapper that connects `iogen` to `doio`, handling option pass-through, generated test-file sizing, optional cleanup, named LTP reporting, and a few legacy scenarios.

Important APIs/types/functions: `usage`, `help`, `killkids`, `cleanup_and_exit`, shell arrays `F[]`, `df`, `dirname`, `${LTPROOT}/testcases/bin/iogen`, `${LTPROOT}/testcases/bin/doio`, and LTP `tst_resm` reporting.

Control flow: parses wrapper flags (`-c`, `-F`, `-S`, `-N`, `-n`) while separating iogen options from doio options, expands percentage file-size specifications using `df`, creates missing directories, and defaults doio flags to `-av`. With `-F` it only prints processed file specs; otherwise it runs `iogen ... files | doio ...`, forces `-k` locking for multi-process I/O, propagates iogen failures via `HUP`, and reports pass/fail from doio's exit status.

State/persistence behavior: can create directories and test files, and with `-c` removes those created by this invocation. Percentage sizing depends on current free space. It also manipulates process groups through traps to stop children on interrupt.

Dependencies/integration: expects LTP shell helpers, `LTPROOT`, installed `iogen` and `doio` binaries, `df`, `expr`, `dirname`, and optionally `mpprun` for MPP scenarios.

Risks/test signals: word-splitting of file names means paths with spaces are unsafe. The integer comparison `[[ $2 > 1 ]]` is shell-specific. Success is `TPASS` and exit 0; any iogen/doio nonzero result emits `TFAIL` and exits nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/rwtest -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/string_to_tokens.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/string_to_tokens.c

Purpose: tokenizes a separator-delimited string into a caller-provided pointer array for legacy option parsing.

Important APIs/types/functions: `string_to_tokens`, `strtok`, `arg_string`, `arg_array`, `array_size`, and `separator`.

Control flow: rejects invalid output array, size, or separator with `-1`; calls `strtok(arg_string, separator)` for the first token; then continues until the array is full or no token remains. The output array is null-terminated when capacity permits, and the return value is the number of tokens stored/found within the bounded array walk.

State/persistence behavior: mutates `arg_string` by replacing separators with NUL bytes and uses `strtok`'s process-global scan state. It creates no filesystem state.

Dependencies/integration: used by `iogen` to split composite open-creation options such as `-O` argument forms.

Risks/test signals: not reentrant or thread-safe because of `strtok`. Extra tokens beyond `array_size - 1` are ignored. Callers must pass a writable string, not a string literal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/string_to_tokens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/write_log.c -->
# sources/test-tools/ltp/testcases/kernel/fs/doio/write_log.c

Purpose: implements a compact appendable write-history log for doio-style writes, including support for later overlaying completion state for asynchronous operations and scanning records backward.

Important APIs/types/functions: `wlog_open`, `wlog_close`, `wlog_record_write`, `wlog_scan_backward`, `wlog_rec_pack`, `wlog_rec_unpack`, `struct wlog_file`, `struct wlog_rec`, `struct wlog_rec_disk`, `Wlog_Error_String`, `WLOG_REC_MAX_SIZE`, and `WLOG_STOP_SCAN`.

Control flow: `wlog_open` opens one append descriptor and one random-access descriptor. `wlog_record_write` packs fixed fields plus optional path/host/pattern strings; appends full records with a two-byte trailing length when `offset < 0`, or overlays only the fixed portion at a saved offset for completion updates. `wlog_scan_backward` reads blocks from EOF toward BOF, uses the trailing length field to locate complete records, unpacks into `wlog_rec`, and invokes a caller callback until count/EOF/stop.

State/persistence behavior: persists variable-length binary records in the log file named by `wfile->w_file`. Error state is a global static string. File descriptors remain owned by the `wlog_file` handle until `wlog_close`.

Dependencies/integration: consumed by doio write-verification paths that need to reason about which patterns should be present in a target file after a stress run. Depends on POSIX `open`, `write`, `lseek`, `read`, `close`, `umask`, and the disk layout declared in `write_log.h`.

Risks/test signals: record lengths are stored in two bytes, so layout and `WLOG_REC_MAX_SIZE` must stay bounded. Overlay callers must save valid offsets. Reverse scanning is sensitive to corrupt length trailers. Test signal is successful callback traversal; failures return `-1` and populate `Wlog_Error_String`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/doio/write_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_bind`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_bind_lib.sh fs_bind_regression.sh`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_trunk_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_bind*`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind01.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind01.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent2 share2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share2/child2/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check parent1/child1/b parent2/child2/b share2/child2/b`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent1/child1/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind02.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind02.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 share1`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 share1`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check parent1/child1/b parent2/child2/b share1/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent1/child1/b`
- `EXPECT_PASS umount parent1/child1`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind03.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind03.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 21 expected-success command assertions, 0 expected-failure assertions, 6 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `mkdir parent2`
- `EXPECT_PASS mount --bind parent1/child1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --bind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `fs_bind_check share2 parent2`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 share1`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 share1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share1/a`
Additional operations: 16 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind04.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind04.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to unclonable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to unclonable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 share1`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 share1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check parent1/child1/b parent2/child2/b share1/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/c`
- `fs_bind_check parent1/child1/c parent2/child2/c share1/c`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent1/child1/b`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind05.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind05.sh

Purpose: LTP `bind propagation` testcase for `bind: private child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: private child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --bind parent2 share2`
- `fs_bind_check -n parent1/child1 share1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2 share2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child2/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `fs_bind_check parent2/child2/b share2/child2/b`
Additional operations: 15 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind06.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind06.sh

Purpose: LTP `bind propagation` testcase for `bind: private child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: private child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child2/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind07-2.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind07-2.sh

Purpose: LTP `bind propagation` testcase for `bind: create slave then mount master - slave still propagates`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: create slave then mount master - slave still propagates"`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind share2 parent2`
- `EXPECT_PASS mount --make-slave parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share2`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/a`
- `fs_bind_check -n parent2/a share2/a`
- `EXPECT_PASS umount parent2/a`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind07-2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind07.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind07.sh

Purpose: LTP `bind propagation` testcase for `bind: private child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: private child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --bind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `mkdir parent2/child2`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `fs_bind_check -n parent2/child2 share2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
Additional operations: 16 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind08.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind08.sh

Purpose: LTP `bind propagation` testcase for `bind: private child to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: private child to uncloneable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `fs_bind_check -n parent1/child1 share1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child2/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `fs_bind_check -n parent1/child1 share1/child1`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child2/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind08.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind09.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind09.sh

Purpose: LTP `bind propagation` testcase for `bind: slave child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 8 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: slave child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `fs_bind_check parent1/child1 share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
Additional operations: 17 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind09.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind10.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind10.sh

Purpose: LTP `bind propagation` testcase for `bind: slave child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 17 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: slave child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `fs_bind_check parent1/child1 share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind11.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind11.sh

Purpose: LTP `bind propagation` testcase for `bind: slave child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 23 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: slave child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --make-rslave parent2`
- `mkdir parent2/child2`
- `fs_bind_check parent1/child1 share1`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent1/child1/a`
Additional operations: 21 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind11.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind12.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind12.sh

Purpose: LTP `bind propagation` testcase for `bind: slave child to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 17 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: slave child to uncloneable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `fs_bind_check parent1/child1 share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind12.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind13.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind13.sh

Purpose: LTP `bind propagation` testcase for `bind: uncloneable child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: uncloneable child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind parent2 share2`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1/x`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --bind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`
Additional operations: 2 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind13.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind14.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind14.sh

Purpose: LTP `bind propagation` testcase for `bind: uncloneable child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 8 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: uncloneable child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1/x`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --bind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind14.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind15.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind15.sh

Purpose: LTP `bind propagation` testcase for `bind: uncloneable child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 13 expected-success command assertions, 1 expected-failure assertions, 1 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: uncloneable child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1/x`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --bind --make-rslave share2 parent2`
- `fs_bind_check parent2 share2`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --bind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
Additional operations: 5 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind15.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind16.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind16.sh

Purpose: LTP `bind propagation` testcase for `bind: uncloneable child to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 8 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: uncloneable child to uncloneable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --bind parent1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1/x`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --bind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind16.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind17.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind17.sh

Purpose: LTP `bind propagation` testcase for `bind: shared subtree with shared child to shared subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared subtree with shared child to shared subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --bind share1 parent1`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
- `EXPECT_PASS umount share1/b`
- `EXPECT_PASS umount parent2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind17.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind18.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind18.sh

Purpose: LTP `bind propagation` testcase for `bind: shared subtree with shared child to private subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared subtree with shared child to private subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --bind share1 parent1`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
- `EXPECT_PASS umount share1/b`
- `EXPECT_PASS umount parent2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind18.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind19.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind19.sh

Purpose: LTP `bind propagation` testcase for `bind: shared subtree with shared child to slave subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared subtree with shared child to slave subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --bind share1 parent1`
- `EXPECT_PASS mount --bind --make-rslave share2 parent2`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind19.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind20.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind20.sh

Purpose: LTP `bind propagation` testcase for `bind: shared subtree with shared child to uncloneable subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared subtree with shared child to uncloneable subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --bind share1 parent1`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
- `EXPECT_PASS umount share1/b`
- `EXPECT_PASS umount parent2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind20.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind21.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind21.sh

Purpose: LTP `bind propagation` testcase for `bind: multi-level slave p-nodes`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: multi-level slave p-nodes"`
- `fs_bind_makedir rshared dir1`
- `mkdir dir1/x dir2 dir3 dir4`
- `EXPECT_PASS mount --bind dir1 dir2`
- `EXPECT_PASS mount --make-rslave dir2`
- `EXPECT_PASS mount --make-rshared dir2`
- `EXPECT_PASS mount --bind dir2 dir3`
- `EXPECT_PASS mount --make-rslave dir3`
- `EXPECT_PASS mount --make-rshared dir3`
- `EXPECT_PASS mount --bind dir3 dir4`
- `EXPECT_PASS mount --make-rslave dir4`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1/x`
- `fs_bind_check dir1/x dir2/x dir3/x dir4/x`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir2/x/a`
- `fs_bind_check -n dir1/x/a dir2/x/a`
- `fs_bind_check dir2/x/a dir3/x/a dir4/x/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" dir3/x/b`
- `fs_bind_check -n dir1/x/b dir3/x/b`
Additional operations: 14 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind21.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind22.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind22.sh

Purpose: LTP `bind propagation` testcase for `bind: bind within same tree - root to child`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 9 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: bind within same tree - root to child"`
- `fs_bind_makedir rshared parent`
- `fs_bind_makedir rshared parent/child1`
- `fs_bind_makedir rshared parent/child2`
- `EXPECT_PASS mount --bind parent parent/child2/`
- `fs_bind_check parent parent/child2/`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child1`
- `EXPECT_PASS umount parent/child2`
- `EXPECT_PASS umount parent/child2`
- `EXPECT_PASS umount parent`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind22.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind23.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind23.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to shared parent"`
- `fs_bind_makedir private mnt`
- `fs_bind_makedir rshared mnt/1`
- `mkdir mnt/2 mnt/1/abc`
- `EXPECT_PASS mount --bind mnt/1 mnt/2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" mnt/1/abc`
- `fs_bind_check mnt/1/abc mnt/2/abc "$FS_BIND_DISK1"`
- `mkdir tmp2`
- `fs_bind_makedir rshared tmp1`
- `EXPECT_PASS mount --bind tmp1 tmp2`
- `mkdir tmp1/3`
- `EXPECT_PASS mount --move mnt tmp1/3`
- `fs_bind_check tmp1/3/1/abc tmp2/3/1/abc tmp2/3/2/abc "$FS_BIND_DISK1"`
- `EXPECT_PASS umount tmp1/3/1/abc`
- `EXPECT_PASS umount tmp1/3/1`
- `EXPECT_PASS umount tmp1/3/2`
- `EXPECT_PASS umount tmp1/3`
- `EXPECT_PASS umount tmp1`
Additional operations: 1 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind23.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind24.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind24.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to shared parent"`
- `fs_bind_makedir rshared dir1`
- `mkdir dir1/1 dir1/1/2 dir1/1/2/3 dir1/1/2/fs_bind_check dir2 dir3 dir4`
- `EXPECT_PASS mount --bind dir1/1/2 dir2`
- `EXPECT_PASS mount --make-rslave dir1`
- `EXPECT_PASS mount --make-rshared dir1`
- `EXPECT_PASS mount --bind dir1/1/2/3 dir3`
- `EXPECT_PASS mount --make-rslave dir1`
- `EXPECT_PASS mount --bind dir4 dir2/fs_bind_check`
- `fs_bind_check dir1/1/2/fs_bind_check/ dir4`
- `EXPECT_PASS umount dir2/fs_bind_check`
- `EXPECT_PASS umount dir3`
- `EXPECT_PASS umount dir2`
- `EXPECT_PASS umount dir1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind24.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_bind*`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS01.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS01.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with shared dirs`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 9 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 2 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with shared dirs"`
- `fs_bind_makedir rshared dir1`
- `fs_bind_makedir rshared dir2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `EXPECT_PASS mount --bind dir1 dir2`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir2/a`
- `fs_bind_check dir1/a dir2/a`
- `fs_bind_check -s "$FS_BIND_DISK2" dir1/a dir2/a`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK3" $PWD/dir1/b`
- `fs_bind_check -s dir1/b dir2/b`
- `EXPECT_PASS umount dir1/b`
- `EXPECT_PASS umount dir2/a`
- `EXPECT_PASS umount dir2`
- `EXPECT_PASS umount dir1`
- `EXPECT_PASS umount dir2`
- `EXPECT_PASS umount dir1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS02.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS02.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespaces with parent-slave`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 3 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespaces with parent-slave"`
- `fs_bind_makedir rshared dir1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `mkdir dir2`
- `EXPECT_PASS mount --bind dir1 dir2`
- `EXPECT_PASS mount --make-slave dir2`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir1/a`
- `fs_bind_check dir1/a dir2/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" dir2/b`
- `fs_bind_check -n dir1/b dir2/b`
- `fs_bind_check -s "$FS_BIND_DISK2" dir1/a dir2/a`
- `fs_bind_check -s -n "$FS_BIND_DISK3" dir2/b`
- `fs_bind_check -s -n "$FS_BIND_DISK3" dir1/b`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK4" $PWD/dir1/c`
- `fs_bind_check -s dir1/c dir2/c`
- `fs_bind_exec_ns umount $PWD/dir2/a`
- `fs_bind_check -s -n dir1/a dir2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS03.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS03.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with unclonable mount`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 3 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 1 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with unclonable mount"`
- `fs_bind_makedir runbindable dir1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `fs_bind_check "$FS_BIND_DISK1" dir1`
- `fs_bind_create_ns`
- `fs_bind_check -s "$FS_BIND_DISK1" dir1`
- `EXPECT_PASS umount dir1`
- `EXPECT_PASS umount dir1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS04.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS04.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with private mount`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 5 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 2 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with private mount"`
- `fs_bind_makedir private dir1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir1/a`
- `fs_bind_check -s -n "$FS_BIND_DISK2" dir1/a`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK3" "$PWD/dir1/b"`
- `fs_bind_check -n "$FS_BIND_DISK3" dir1/b`
- `EXPECT_PASS umount dir1/a`
- `EXPECT_PASS umount dir1`
- `EXPECT_PASS umount dir1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS05.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS05.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with multi-level chain of slaves`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 3 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with multi-level chain of slaves"`
- `fs_bind_makedir rshared parent`
- `fs_bind_makedir rshared parent/child1`
- `fs_bind_makedir rshared parent/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent/child1`
- `EXPECT_PASS mount --rbind parent parent/child2`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent/child1/a`
- `fs_bind_check parent/child1/a parent/child2/child1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent/child2/child1/b`
- `fs_bind_check parent/child1/b parent/child2/child1/b`
- `fs_bind_check -s "$FS_BIND_DISK2" parent/child1/a parent/child2/child1/a`
- `fs_bind_check -s "$FS_BIND_DISK3" parent/child1/b parent/child2/child1/b`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK4" "$PWD/parent/child2/child1/c"`
- `fs_bind_check -scheck parent/child2/child1/c parent/child1/c`
- `fs_bind_exec_ns umount "$PWD/parent/child1/b"`
- `fs_bind_check -s parent/child2/child1/b parent/child1/b`
- `fs_bind_check "$FS_BIND_DISK4" parent/child2/child1/c parent/child1/c`
Additional operations: 9 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS06.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS06.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with shared point bind mounted within the same directory`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 18 propagation comparisons, and 3 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with shared point bind mounted within the same directory"`
- `fs_bind_makedir rshared dir1`
- `mkdir dir1/x dir2 dir3 dir4`
- `EXPECT_PASS mount --rbind dir1 dir2`
- `EXPECT_PASS mount --make-rslave dir2`
- `EXPECT_PASS mount --make-rshared dir2`
- `EXPECT_PASS mount --rbind dir2 dir3`
- `EXPECT_PASS mount --make-rslave dir3`
- `EXPECT_PASS mount --make-rshared dir3`
- `EXPECT_PASS mount --rbind dir3 dir4`
- `EXPECT_PASS mount --make-rslave dir4`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" dir1/x`
- `fs_bind_check dir1/x dir2/x dir3/x dir4/x`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" dir2/x/a`
- `fs_bind_check -n dir1/x/a dir2/x/a`
- `fs_bind_check dir2/x/a dir3/x/a dir4/x/a`
- `fs_bind_check -s dir1/x dir2/x dir3/x dir4/x`
Additional operations: 25 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS07.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS07.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: slave child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 9 expected-success command assertions, 0 expected-failure assertions, 11 propagation comparisons, and 2 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: slave child to slave parent"`
- `mkdir parent1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1`
- `EXPECT_PASS mount --make-rshared parent1`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `EXPECT_PASS mount --move parent1 parent2/a`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `fs_bind_create_ns`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/b`
- `fs_bind_check parent2/b parent2/a/b parent2/a/a/b`
- `fs_bind_check -s parent2 parent2/a parent2/a/a`
- `fs_bind_check -s parent2/b parent2/a/b parent2/a/a/b`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK3" "$PWD/parent2/a/c"`
- `fs_bind_check -s parent2/c parent2/a/c parent2/a/a/c`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `fs_bind_check parent2/c parent2/a/c parent2/a/a/c`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_lib.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_lib.sh

Purpose: shared LTP shell library for the `fs_bind` mount-propagation suites. It creates a private sandbox, test disk directories, mount namespaces, bind/move/rbind helpers, propagation comparisons, and cleanup around each test case.

Important APIs/types/functions: `fs_bind_makedir`, `fs_bind_check`, `fs_bind_setup`, `_fs_bind_unmount_all`, `fs_bind_cleanup`, `_fs_bind_setup_test`, `fs_bind_create_ns`, `fs_bind_exec_ns`, `fs_bind_destroy_ns`, `_fs_bind_cleanup_test`, `fs_bind_test`, and exported LTP variables `TST_NEEDS_TMPDIR`, `TST_NEEDS_ROOT`, `TST_TESTFUNC`, `TST_SETUP`, `TST_CLEANUP`, `TST_NEEDS_CMDS`.

Control flow: library setup bind-mounts a private `sandbox`, creates four disk directories with known subtrees, and wraps the real test function named by `FS_BIND_TESTFUNC`. Each test starts from a cleaned sandbox, runs either `test` or numbered `testN`, then checks for leaked mounts and unmounts everything in reverse `/proc/mounts` order.

State/persistence behavior: creates and removes temporary directories under `TST_TMPDIR`, makes and tears down many bind mounts, and optionally creates a persistent mount namespace process id in `FS_BIND_MNTNS_PID` until cleanup kills it.

Dependencies/integration: sources `tst_test.sh` and relies on LTP `EXPECT_PASS`, `EXPECT_FAIL`, `ROD`, `tst_res`, `tst_brk`, `tst_ns_create`, and `tst_ns_exec`. Requires root plus `mount`, `umount`, `awk`, `sed`, and `diff`.

Risks/test signals: cleanup is safety-critical because leaked mounts can affect later tests. `fs_bind_check -n` treats absence/difference as expected non-propagation. Success and failure are reported through LTP `TPASS`, `TFAIL`, and `TBROK` records.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_regression.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_regression.sh

Purpose: LTP `regression` testcase for `regression: bind unshared directory to unshare mountpoint | regression: rbind unshared directory to unshare mountpoint | regression: move unshared directory to unshare mountpoint`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "regression: bind unshared directory to unshare mountpoint"`
- `mkdir dir`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir`
- `fs_bind_check "$FS_BIND_DISK1" dir`
- `EXPECT_PASS umount dir`
- `tst_res TINFO "regression: rbind unshared directory to unshare mountpoint"`
- `mkdir dir1`
- `mkdir dir2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir1/a`
- `EXPECT_PASS mount --rbind dir1 dir2`
- `fs_bind_check dir1/a dir2/a`
- `EXPECT_PASS umount dir1/a`
- `EXPECT_PASS umount dir2/a`
- `EXPECT_PASS umount dir2`
- `EXPECT_PASS umount dir1`
- `tst_res TINFO "regression: move unshared directory to unshare mountpoint"`
- `mkdir dir1`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_regression.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_bind*`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move01.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move01.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 13 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared child to shared parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --bind parent2 share2`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild share2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share1/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share1/grandchild/a share2/child2/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/`
- `EXPECT_PASS umount parent2/child2`
Additional operations: 5 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move02.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move02.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared subtree to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 13 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared subtree to private parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share2/child2 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share1/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move03.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move03.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared subtree to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared subtree to slave parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --bind share2 parent2`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share2/child2 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share1/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/a`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move04.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move04.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared subtree to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared subtree to uncloneable parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share1/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
Additional operations: 1 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move05.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move05.sh

Purpose: LTP `mount --move propagation` testcase for `move: private subtree to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 13 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private subtree to shared parent"`
- `fs_bind_makedir private dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind parent2 share2`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share1/grandchild parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share2/child2/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share2/child2/grandchild/a`
- `EXPECT_PASS umount parent2/child2/grandchild/a`
- `EXPECT_PASS umount parent2/child2/grandchild`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move06.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move06.sh

Purpose: LTP `mount --move propagation` testcase for `move: private subtree to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private subtree to private parent"`
- `fs_bind_makedir private dir`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check -n parent2/child2/grandchild share2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share1/grandchild parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2/`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
Additional operations: 3 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move07.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move07.sh

Purpose: LTP `mount --move propagation` testcase for `move: private subtree to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 12 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private subtree to slave parent"`
- `fs_bind_makedir private dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check -n parent2/child2/grandchild share2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share1/grandchild parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share2`
Additional operations: 4 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move08.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move08.sh

Purpose: LTP `mount --move propagation` testcase for `move: private subtree to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 8 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private subtree to uncloneable parent"`
- `fs_bind_makedir private dir`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share1/grandchild parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move08.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move09.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move09.sh

Purpose: LTP `mount --move propagation` testcase for `move: slave subtree to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: slave subtree to shared parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind parent2 share2`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --make-rslave dir`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share1/grandchild parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share2/child2/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share2/child2/grandchild/a`
- `mkdir share1/test`
Additional operations: 9 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move09.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move10.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move10.sh

Purpose: LTP `mount --move propagation` testcase for `move: slave subtree to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: slave subtree to private parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --make-rslave dir`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `fs_bind_check -n parent2/child2 share2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild/ parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child2/grandchild/a`
- `fs_bind_check -n share1/grandchild/a parent2/child2/grandchild/a`
- `EXPECT_PASS umount parent2/child2/grandchild/a`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move11.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move11.sh

Purpose: LTP `mount --move propagation` testcase for `move: slave subtree to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 15 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: slave subtree to slave parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --make-rslave dir`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `fs_bind_check -n parent2/child2 share2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild/ parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child2/grandchild/a`
- `fs_bind_check -n share1/grandchild/a parent2/child2/grandchild/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move11.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move12.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move12.sh

Purpose: LTP `mount --move propagation` testcase for `move: slave subtree to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 12 expected-success command assertions, 1 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: slave subtree to uncloneable parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --make-rslave dir`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --bind parent2 share2 2> /dev/null`
- `EXPECT_PASS mount --move dir parent2/child2`
- `fs_bind_check -n parent2/child2 share2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild/ parent2/child2/grandchild`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child2/grandchild/a`
- `fs_bind_check -n share1/grandchild/a parent2/child2/grandchild/a`
- `EXPECT_PASS umount parent2/child2/grandchild/a`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move12.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move13.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move13.sh

Purpose: LTP `mount --move propagation` testcase for `move: uncloneable subtree to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 5 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: uncloneable subtree to shared parent"`
- `fs_bind_makedir runbindable dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind parent2 share2`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --move dir parent2/child2`
- `EXPECT_PASS umount dir`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move13.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move14.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move14.sh

Purpose: LTP `mount --move propagation` testcase for `move: uncloneable subtree to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 6 expected-success command assertions, 0 expected-failure assertions, 1 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: uncloneable subtree to private parent"`
- `fs_bind_makedir runbindable dir`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share2`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `fs_bind_check  -n parent2/child2/ share2/child2/`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move14.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move15.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move15.sh

Purpose: LTP `mount --move propagation` testcase for `move: uncloneable subtree to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 7 expected-success command assertions, 0 expected-failure assertions, 1 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: uncloneable subtree to slave parent"`
- `fs_bind_makedir runbindable dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind parent2 share2`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `fs_bind_check  -n parent2/child2/ share2/child2/`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move15.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move16.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move16.sh

Purpose: LTP `mount --move propagation` testcase for `move: uncloneable subtree to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 4 expected-success command assertions, 0 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: uncloneable subtree to uncloneable parent"`
- `fs_bind_makedir runbindable dir`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move16.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move17.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move17.sh

Purpose: LTP `mount --move propagation` testcase for `move: tree with shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 3 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: tree with shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_makedir rshared parent2`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --move parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move17.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move18.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move18.sh

Purpose: LTP `mount --move propagation` testcase for `move: private to private - with shared children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 13 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private to private - with shared children"`
- `fs_bind_makedir private parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --bind parent1/child1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --move parent1 parent2`
- `fs_bind_check parent2/child1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child1/a`
- `fs_bind_check parent2/child1/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" share1/b`
- `fs_bind_check parent2/child1/b share1/b`
- `EXPECT_PASS umount parent2/child1/a`
- `fs_bind_check parent2/child1/a share1/a`
- `EXPECT_PASS umount parent2/child1/b`
- `fs_bind_check parent2/child1/b share1/b`
- `EXPECT_PASS umount parent2/child1`
Additional operations: 5 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move18.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move19.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move19.sh

Purpose: LTP `mount --move propagation` testcase for `move: private to private - with slave children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private to private - with slave children"`
- `fs_bind_makedir private parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `mkdir parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --move parent1 parent2`
- `fs_bind_check parent2/child1 share1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child1/a`
- `fs_bind_check -n parent2/child1/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" share1/b`
- `fs_bind_check parent2/child1/b share1/b`
- `EXPECT_PASS umount parent2/child1/b`
- `fs_bind_check -n parent2/child1/b share1/b`
- `EXPECT_PASS umount parent2/child1/a`
- `EXPECT_PASS umount parent2/child1`
Additional operations: 5 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move19.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move20.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move20.sh

Purpose: LTP `mount --move propagation` testcase for `move: private to private - with unclonable children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 6 expected-success command assertions, 0 expected-failure assertions, 1 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private to private - with unclonable children"`
- `fs_bind_makedir private parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --move parent1 parent2`
- `fs_bind_check "$FS_BIND_DISK1" parent2/child1`
- `EXPECT_PASS umount parent2/child1`
- `EXPECT_PASS umount parent2/child1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move20.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move21.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move21.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared tree within a tree it is bound to`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared tree within a tree it is bound to"`
- `mkdir parent1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1`
- `EXPECT_PASS mount --make-rshared parent1`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `EXPECT_PASS mount --move parent1 parent2/a`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/b`
- `fs_bind_check parent2/b parent2/a/b parent2/a/a/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent2/a/c`
- `fs_bind_check parent2/c parent2/a/c parent2/a/a/c`
- `EXPECT_PASS umount parent2/a/a/c`
- `fs_bind_check parent2/c parent2/a/c parent2/a/a/c`
- `EXPECT_PASS umount parent2/b`
- `EXPECT_PASS umount parent2/a/a`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move21.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move22.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move22.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared tree within a tree it is bound to - and then move to another share subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 8 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared tree within a tree it is bound to - and then move to another share subtree"`
- `fs_bind_makedir rshared parent1`
- `mkdir parent1/a parent2`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `EXPECT_PASS mount --move parent1 parent2/a`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `fs_bind_makedir rshared tmp1`
- `mkdir tmp2 tmp1/1`
- `EXPECT_PASS mount --bind tmp1 tmp2`
- `EXPECT_PASS mount --move parent2  tmp1/1`
- `EXPECT_PASS umount tmp1/1/a/a`
- `EXPECT_PASS umount tmp1/1`
- `EXPECT_PASS umount tmp1`
- `EXPECT_PASS umount tmp2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move22.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_bind*`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind01.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind01.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent2 share2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent2 share2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share2/child2/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check parent1/child1/b parent2/child2/b share2/child2/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent1/child1/b`
- `EXPECT_PASS umount parent2/child2`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind02.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind02.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 share1`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 share1`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check parent1/child1/b parent2/child2/b share1/b`
- `EXPECT_PASS umount parent2/child2/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child2`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind03.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind03.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 21 expected-success command assertions, 0 expected-failure assertions, 6 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `mkdir parent2`
- `EXPECT_PASS mount --rbind parent1/child1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `fs_bind_check share2 parent2`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 share1`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 share1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share1/a`
Additional operations: 16 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind04.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind04.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared child to unclonable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared child to unclonable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 share1`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 share1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check parent1/child1/a parent2/child2/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check parent1/child1/b parent2/child2/b share1/b`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/c`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent1/child1/b`
- `EXPECT_PASS umount parent1/child1/c`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind04.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind05.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind05.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent2 share2`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2 share2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `fs_bind_check parent2/child2/c share2/child2/c`
Additional operations: 15 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind05.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind06.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind06.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child2/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07-2.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07-2.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: create slave then mount master - slave still propagates`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: create slave then mount master - slave still propagates"`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share2`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent2/a`
- `fs_bind_check -n parent2/a share2/a`
- `EXPECT_PASS umount parent2/a`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07-2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `mkdir parent2/child2`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `fs_bind_check -n parent2/child2 share2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
Additional operations: 16 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind08.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind08.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private child to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private child to uncloneable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `fs_bind_check -n  parent1/child1 share1/child1`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child2/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind08.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind09.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind09.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: slave child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 8 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: slave child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind parent2 share2`
- `EXPECT_PASS mount --rbind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `fs_bind_check parent1/child1 share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
Additional operations: 17 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind09.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind10.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind10.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: slave child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 17 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: slave child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `fs_bind_check parent1/child1 share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind11.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind11.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: slave child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 23 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: slave child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind parent2 share2`
- `EXPECT_PASS mount --rbind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --make-rslave parent2`
- `mkdir parent2/child2`
- `fs_bind_check parent1/child1 share1`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent1/child1/a`
Additional operations: 21 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind11.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind12.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind12.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: slave child to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 17 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: slave child to uncloneable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `fs_bind_check parent1/child1 share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --rbind parent1/child1 parent2/child2`
- `fs_bind_check parent1/child1 parent2/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n  parent1/child1/a parent2/child2/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child2/b`
- `fs_bind_check -n parent1/child1/b parent2/child2/b`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind12.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind13.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind13.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: uncloneable child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: uncloneable child to shared parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind parent2 share2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1/x`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --rbind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
Additional operations: 2 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind13.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind14.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind14.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: uncloneable child to private parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 8 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: uncloneable child to private parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1/x`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --rbind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind14.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind15.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind15.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: uncloneable child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 1 expected-failure assertions, 1 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: uncloneable child to slave parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1/x`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" share2`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `fs_bind_check parent2 share2`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --rbind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind15.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind16.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind16.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: uncloneable child to uncloneable parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 8 expected-success command assertions, 1 expected-failure assertions, 0 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: uncloneable child to uncloneable parent"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir runbindable parent1/child1`
- `mkdir parent1/child1/x`
- `EXPECT_PASS mount --rbind parent1 share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1/x`
- `mkdir parent2/child2`
- `EXPECT_FAIL mount --rbind parent1/child1 parent2/child2`
- `EXPECT_PASS umount parent1/child1/x`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind16.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind17.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind17.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with shared child to shared subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with shared child to shared subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --rbind share1 parent1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
- `EXPECT_PASS umount share1/b`
- `EXPECT_PASS umount parent2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind17.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind18.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind18.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with shared child to private subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with shared child to private subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --rbind share1 parent1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
- `EXPECT_PASS umount share1/b`
- `EXPECT_PASS umount parent2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind18.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind19.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind19.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with shared child to slave subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with shared child to slave subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --rbind share1 parent1`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/b`
Additional operations: 13 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind19.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind20.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind20.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with shared child to uncloneable subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with shared child to uncloneable subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --rbind share1 parent1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 share1 parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1`
- `fs_bind_check parent1/child1 parent2/child1`
- `fs_bind_check parent1/child1 share1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/a`
- `fs_bind_check parent1/a parent2/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/b`
- `fs_bind_check parent1/b parent2/b share1/b`
- `EXPECT_PASS umount share1/b`
- `EXPECT_PASS umount parent2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind20.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind21.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind21.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with  private child to shared subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 18 expected-success command assertions, 0 expected-failure assertions, 7 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with  private child to shared subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share1 parent1`
- `EXPECT_PASS mount --rbind share2 parent2`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 share1 parent2 share2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `fs_bind_check -n parent1/child1/a share1/child1/a`
- `fs_bind_check parent2/child1/a share2/child1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
Additional operations: 13 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind21.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind22.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind22.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with  private child to slave subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with  private child to slave subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `fs_bind_check -n parent2 share2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child1/b`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind22.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind23.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind23.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with  private child to private subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 15 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with  private child to private subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `EXPECT_PASS mount --rbind parent1 share1`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a share1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child1/b`
- `EXPECT_PASS umount parent2/child1`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind23.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind24.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind24.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with unclonable child to private subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 15 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with unclonable child to private subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir private parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `EXPECT_PASS mount --rbind parent1 share1`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a share1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child1/b`
- `EXPECT_PASS umount parent2/child1`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind24.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind25.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind25.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with slave child to shared subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 16 expected-success command assertions, 0 expected-failure assertions, 8 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with slave child to shared subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `mkdir parent1/child1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
- `fs_bind_check -n parent2/child1/b share1/b`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" share1/c`
Additional operations: 11 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind25.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind26.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind26.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with slave child to private subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 15 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with slave child to private subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child1/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind26.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind27.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind27.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with slave child to slave subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 6 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with slave child to slave subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --bind share2 parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `fs_bind_check -n parent2 share2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `fs_bind_check -n parent1/child1/a share1/a`
Additional operations: 13 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind27.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind28.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind28.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with slave child to unclone subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 15 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with slave child to unclone subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared parent1/child1`
- `EXPECT_PASS mount --bind share1 parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1/ parent2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent1/child1/a`
- `fs_bind_check -n parent1/child1/a parent2/child1/a`
- `fs_bind_check -n parent1/child1/a share1/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent2/child1/b`
- `fs_bind_check -n parent1/child1/b parent2/child1/b`
- `EXPECT_PASS umount parent1/child1/a`
- `EXPECT_PASS umount parent2/child1/b`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind28.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind29.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind29.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with uncloneable child to shared subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 13 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with uncloneable child to shared subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share1 parent1`
- `EXPECT_PASS mount --rbind share2 parent2`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check -n parent1/child1 share1/child1`
- `fs_bind_check -n parent1/child1 parent2/child1`
- `fs_bind_check parent2/child1 share2/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount parent2`
Additional operations: 4 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind29.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind30.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind30.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with uncloneable child to private subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with uncloneable child to private subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --rbind share1 parent1`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check -n parent1/child1 share1/child1`
- `fs_bind_check -n parent1/child1 parent2/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind30.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind31.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind31.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with uncloneable child to slave subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with uncloneable child to slave subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir private parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share1 parent1`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check -n parent1/child1 share1/child1`
- `fs_bind_check -n parent1/child1 parent2/child1`
- `fs_bind_check -n parent2 share2`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
Additional operations: 5 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind31.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind32.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind32.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: shared subtree with uncloneable child to uncloneable subtree`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: shared subtree with uncloneable child to uncloneable subtree"`
- `fs_bind_makedir rshared parent1`
- `fs_bind_makedir runbindable parent2`
- `fs_bind_makedir rshared share1`
- `EXPECT_PASS mount --rbind share1 parent1`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check -n parent1/child1 share1/child1`
- `fs_bind_check -n parent1/child1 parent2/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent1`
- `EXPECT_PASS umount share1`
- `EXPECT_PASS umount parent1`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind32.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind33.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind33.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: multi-level slave p-nodes`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 20 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: multi-level slave p-nodes"`
- `fs_bind_makedir rshared dir1`
- `mkdir dir1/x dir2 dir3 dir4`
- `EXPECT_PASS mount --rbind dir1 dir2`
- `EXPECT_PASS mount --make-rslave dir2`
- `EXPECT_PASS mount --make-shared dir2`
- `EXPECT_PASS mount --rbind dir2 dir3`
- `EXPECT_PASS mount --make-rslave dir3`
- `EXPECT_PASS mount --make-shared dir3`
- `EXPECT_PASS mount --rbind dir3 dir4`
- `EXPECT_PASS mount --make-rslave dir4`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" dir1/x`
- `fs_bind_check dir1/x dir2/x dir3/x dir4/x`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" dir2/x/a`
- `fs_bind_check -n dir1/x/a dir2/x/a`
- `fs_bind_check dir2/x/a dir3/x/a dir4/x/a`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" dir3/x/b`
- `fs_bind_check -n dir1/x/b dir3/x/b`
Additional operations: 14 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind33.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind34.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind34.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: rbind within same tree - root to child, child is shared `. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 9 expected-success command assertions, 0 expected-failure assertions, 6 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: rbind within same tree - root to child, child is shared "`
- `fs_bind_makedir rshared parent`
- `fs_bind_makedir rshared parent/child1`
- `fs_bind_makedir rshared parent/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent/child1`
- `EXPECT_PASS mount --rbind parent parent/child2/`
- `fs_bind_check parent parent/child2/`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child2`
- `EXPECT_PASS umount parent/child2`
Additional operations: 1 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind34.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind35.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind35.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: rbind within same tree - root to child, child is private `. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 0 expected-failure assertions, 6 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: rbind within same tree - root to child, child is private "`
- `fs_bind_makedir rshared parent`
- `fs_bind_makedir private parent/child1`
- `fs_bind_makedir rshared parent/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent/child1`
- `EXPECT_PASS mount --rbind parent parent/child2/`
- `fs_bind_check parent parent/child2/`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child1`
- `fs_bind_check -n parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" parent/child2/child1`
- `fs_bind_check -n parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child2`
- `EXPECT_PASS umount parent/child2/child1`
Additional operations: 3 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind35.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind36.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind36.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: rbind within same tree - root to child, child is uncloneable`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 9 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: rbind within same tree - root to child, child is uncloneable"`
- `fs_bind_makedir rshared parent`
- `fs_bind_makedir runbindable parent/child1`
- `fs_bind_makedir rshared parent/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK3" parent/child1`
- `EXPECT_PASS mount --rbind parent parent/child2/`
- `fs_bind_check parent parent/child2/`
- `fs_bind_check -n  parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK4" parent/child2/child1`
- `fs_bind_check -n  parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child1`
- `fs_bind_check parent/child1 parent/child2/child1`
- `EXPECT_PASS umount parent/child2/child2`
- `EXPECT_PASS umount parent/child1`
- `EXPECT_PASS umount parent/child2`
- `EXPECT_PASS umount parent`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind36.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind37.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind37.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private to private - with shared children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private to private - with shared children"`
- `mkdir parent1 parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_makedir rshared parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1/child1 share1`
- `EXPECT_PASS mount --rbind parent2/child2 share2`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1 parent2/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child1/a`
- `fs_bind_check parent1/child1/a parent2/child1/a share1//a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent1/child1/b`
- `fs_bind_check parent1/child1/b parent2/child1/b share1/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/c`
- `fs_bind_check parent1/child1/c parent2/child1/c share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind37.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind38.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind38.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private to private - with slave children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 21 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private to private - with slave children"`
- `mkdir parent1 parent2 parent1/child1 parent2/child2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share1 parent1/child1`
- `EXPECT_PASS mount --rbind share2 parent2/child2`
- `EXPECT_PASS mount --make-rslave parent1/child1`
- `EXPECT_PASS mount --make-rslave parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" share1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1 parent2/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share1/a`
- `fs_bind_check parent1/child1/a parent2/child1/a share1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent1/child1/b`
- `fs_bind_check -n parent1/child1/b share1/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" parent2/child1/c`
- `fs_bind_check -n parent2/child1/c share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind38.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind39.sh -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind39.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private to private - with unclonable children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 5 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private to private - with unclonable children"`
- `mkdir parent1 parent2`
- `fs_bind_makedir runbindable parent1/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check -n parent1/child1 parent2/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent1/child1`
- `EXPECT_PASS umount parent2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind39.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_di/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_di`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_di`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/create_datafile.c -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_di/create_datafile.c

Purpose: creates a deterministic data file of a requested number of 1 MiB buffers for filesystem data-integrity tests.

Important APIs/types/functions: `main`, `BSIZE` set to 1048576, `creat`, `write`, `fsync`, `close`, `strtol`, and a stack buffer initialized with an incrementing byte sequence ending in `Z`.

Control flow: validates two arguments, converts the buffer count, fills a 1 MiB buffer, creates the target with mode 0755, writes the buffer repeatedly, fsyncs after each write, prints progress dots, and exits 0 on success.

State/persistence behavior: creates or truncates the named file and persists `bufnum * 1MiB` bytes. The generated byte pattern is deterministic and later compared by `fs_di`.

Dependencies/integration: launched by the `fs_di` shell script to build source files for copy/readback and fragmentation checks.

Risks/test signals: `fd` is incorrectly typed as `off_t` rather than `int`, but used as a file descriptor. It does not abort immediately if `creat` fails, so later writes may fail. Success is exit 0 and the expected file size/content.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/create_datafile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/frag.c -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_di/frag.c

Purpose: creates two fragmented files from one input data file by repeatedly appending 1 KiB chunks, fsyncing, and closing both output files after each chunk.

Important APIs/types/functions: global `FILE *` handles, `main`, `fopen`, `fread`, `fwrite`, `fileno`, `fsync`, `fclose`, `strcpy`, and `strcat`.

Control flow: expects input file and output directory arguments, opens the data file, constructs `frag1` and `frag2` paths, repeatedly opens both outputs with `a+`, reads up to 1024 bytes, writes the same bytes to both outputs, fsyncs their descriptors, closes them, and stops at a short read.

State/persistence behavior: appends to `<dir>/frag1` and `<dir>/frag2`; repeated open/fsync/close cycles intentionally encourage fragmented allocation on the target filesystem.

Dependencies/integration: called by `fs_di` when the `-S` disk-size option enables fragmented-file validation.

Risks/test signals: fixed 100-byte path buffers can overflow for long directories. It treats `fread` byte count as signed even though `fread` returns `size_t`. Success is exit 0 and later `cmp` equality with the source data file.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/frag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/fs_di -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_di/fs_di

Purpose: shell-level filesystem data-integrity test. It writes generated data files into random-depth directory paths, copies them back, compares both directions, and optionally validates fragmented-file creation.

Important APIs/types/functions: `usage`, `end_testcase`, option parsing for `-d`, `-l`, `-s`, `-S`, `create_datafile`, `frag`, `cp`, `cmp`, `mkdir`, `chmod`, and LTP `tst_resm`.

Control flow: requires `-d` target directory, defaults to ten loops and a 30 MiB file, optionally chooses random sizes from 10-500 MiB, creates temp and test directories, then for each loop creates a data file, builds a random nested path, copies to the filesystem under test, compares after write, copies back, compares after read, and removes loop artifacts. If `-S` is given, it creates a half-partition-size file, runs `frag`, compares fragmented outputs, then cleans up.

State/persistence behavior: creates `$TCtmp`, `$TESTFS`, nested random directories, `testfile`, `testfile_copy`, and optional `frag1`/`frag2`; cleanup removes them when `CLEANUP=ON`.

Dependencies/integration: uses helper binaries built in the same directory and the legacy LTP shell library path. Intended for mounted filesystems supplied by the caller.

Risks/test signals: destructive cleanup removes `$TESTFS` and `$TMPBASE/*` paths, so `-d` must be isolated. The fragmented-file section contains a duplicated `retval` check and does not actually compare `frag2` before the second failure message. Pass/fail is entirely based on `cmp` and helper exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_di/fs_di -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_fill/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_fill/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_fill`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `default leaf targets from the LTP make include`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `-pthread`.

Control flow: make resolves `top_srcdir`, includes `include/mk/testcases.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_fill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_fill/fs_fill.c -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_fill/fs_fill.c

Purpose: multi-threaded filesystem fill stress test that repeatedly drives mounted filesystems to `ENOSPC` while unlinking one file per worker loop to keep pressure cycling.

Important APIs/types/functions: LTP `struct tst_test`, `tst_fill_fs`, `enum tst_fill_access_pattern`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_OPENDIR`, `SAFE_READDIR`, `SAFE_UNLINK`, `tst_atomic_t`, `worker`, `testrun`, `setup`, and `cleanup`.

Control flow: setup allocates `ncpus + 2` workers and per-thread directories below `mntpoint/subdir`. Each test iteration starts all worker threads with access pattern index `n`, waits until at least one `ENOSPC` after one second or more than 100 `ENOSPC` events, stops threads, joins them, and reports runtime. Workers fill their directory, increment the ENOSPC counter, then unlink one entry before looping.

State/persistence behavior: creates and deletes files on a mounted test filesystem. `workers`, `run`, and `enospc_cnt` are process state; filesystem state is discarded with the LTP mounted-device cleanup.

Dependencies/integration: requires root, a mountable device of at least 1024 MiB, all-filesystems iteration, pthreads, and LTP safe wrappers. The Makefile adds `-pthread`.

Risks/test signals: timing-based termination can vary by filesystem speed. Directory cleanup removes only one file per loop, so very large file counts can accumulate briefly. Success is a `TPASS` with observed `ENOSPC`; hangs are limited by the 300-second timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_fill/fs_fill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_inod/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_inod/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_inod`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `fs_inod`; explicit `MAKE_TARGETS` is `include $(top_srcdir)/include/mk/generic_leaf_target.mk`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/env_pre.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_inod/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_inod/fs_inod -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_inod/fs_inod

Purpose: inode allocation/deallocation stress script. It rapidly creates and removes many files from multiple background processes across two directory trees.

Important APIs/types/functions: `err_log`, `make_subdirs`, `touch_files`, `rm_files`, `step1`, shell redirection for file creation, `mkdir`, `rm`, `wait`, `date`, and exit status aggregation in `ERRORS`.

Control flow: requires volume, subdirectory count, files-per-subdirectory count, and loop count. It changes to the target volume, creates `dir1` and `dir2` with matching subdirectories, starts file creation in the background, then for each loop alternates create/remove phases between the two trees, waiting between phases to coordinate processes. After all loops it waits, removes `dir*`, prints timestamps, and exits with the accumulated error count.

State/persistence behavior: creates and deletes large numbers of `dirN/fileJK` entries under the target volume. Cleanup removes `$testvol/dir*`, so the target path must be a dedicated test area.

Dependencies/integration: legacy standalone shell test installed by the fs_inod Makefile. It depends on POSIX shell utilities and write permission on the tested filesystem.

Risks/test signals: unquoted variables and broad `rm -rf $testvol/dir*` are risky for unusual paths. Background sequencing stresses inode churn but can hide exact failing command context. Exit 0 means no logged step errors; nonzero means one or more create/remove operations failed.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_inod/fs_inod -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_maim/backbeat -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_maim/backbeat

Purpose: Perl helper that simulates an online backup across three mounted partitions by copying `/sbin`, archiving it, moving the archive, extracting it elsewhere, and diffing the result.

Important APIs/types/functions: Perl backticks for `cp -aL`, `tar`, `mv`, `diff`, `mkdir`, `chdir`, argument parsing by splitting `/dev/name` paths, and exit status 0/1.

Control flow: derives directory names from three device path arguments, creates `<part1>/sbin`, copies `/sbin` into it, tars from partition 1, moves the tarball to partition 2, extracts to partition 3, then compares partition 3's `sbin` tree to partition 1's original copy.

State/persistence behavior: writes directories, a tar archive, and extracted files inside the current working directory's partition-named mount points.

Dependencies/integration: called by `maimparts` after `partbeat` formats and mounts three partitions. Depends on Perl, `/sbin`, `cp`, `tar`, `mv`, and `diff`.

Risks/test signals: argument parsing assumes `/dev/name` paths with exactly three slash-separated fields. It follows symlinks with `cp -aL`, so backup content depends on host `/sbin`. Success is `Diff: PASS` and exit 0; any diff output produces exit 1.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_maim/backbeat -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_maim/maimparts -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_maim/maimparts

Purpose: destructive Perl orchestrator that repartitions a target disk into three partitions, runs mount/fsck cycling on each, and then runs the backup simulation.

Important APIs/types/functions: `sfdisk -g`, generated `/tmp/part.cfg`, `sfdisk --force`, `$parts`, `$fstype`, `partbeat`, `backbeat`, and Perl arrays for partition names.

Control flow: reads target disk name, iteration count, and filesystem type, queries disk geometry, divides cylinders by three, writes an sfdisk config, force-applies it to `/dev/$target`, runs `partbeat` for each partition, then calls `backbeat` using the three partition devices.

State/persistence behavior: rewrites the target disk partition table and creates `/tmp/part.cfg`. This is intentionally destructive and can remove all data from the specified disk.

Dependencies/integration: coordinates `partbeat` and `backbeat` helpers in the same directory. Depends on root privileges, `/sbin/sfdisk`, working block devices, filesystem tools, and mount permissions.

Risks/test signals: the prologue warning is accurate: passing the wrong device destroys data. Geometry parsing is fragile and assumes old sfdisk output. Test signals are printed helper output and nonzero helper failures, though the script itself does not consistently check every command status.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_maim/maimparts -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_maim/partbeat -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_maim/partbeat

Purpose: Perl helper that formats a partition, fscks it, repeatedly mounts/unmounts it while creating marker files, fscks again, and leaves it mounted with markers removed.

Important APIs/types/functions: filesystem-specific `mkfs` command selection, `fsck -t`, `mount -t`, `umount`, `touch`, target device parsing, and iteration loop.

Control flow: chooses `mkfs.jfs`, `mkfs`, `mkfs -t ext3`, or `mkreiserfs` based on the requested filesystem type, runs fsck, creates a mount directory named after the device basename, then for each iteration mounts the partition, touches `indicatorN`, and unmounts. Finally it fscks again, mounts once more, and removes indicators.

State/persistence behavior: destroys and recreates the filesystem on the target partition, creates a local mount directory, creates/removes indicator files, and leaves the filesystem mounted at the end for `backbeat`.

Dependencies/integration: invoked by `maimparts` for each generated partition. Depends on root, mkfs/fsck variants, mount/umount, and writable current directory.

Risks/test signals: command outputs are printed but exit statuses are not robustly enforced. Device basename directory conflicts can affect results. Success is inferred from clean command output and availability of the mounted partition for subsequent tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_maim/partbeat -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_perms/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_perms/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_perms`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `default leaf targets from the LTP make include`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `none`.

Control flow: make resolves `top_srcdir`, includes `include/mk/testcases.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_perms/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_perms/fs_perms.c -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_perms/fs_perms.c

Purpose: regression test for filesystem permission enforcement across read, write, and execute bits for a file with specified owner/group/mode and a tester uid/gid.

Important APIs/types/functions: `testsetup`, `testfperm`, `str_to_l`, `cleanup`, `tst_require_root`, `tst_tmpdir`, `tst_get_path`, `chmod`, `chown`, `fork`, `setgid`, `setuid`, `fopen`, `execl`, `execlp`, `wait`, and LTP `tst_resm`.

Control flow: validates seven arguments, parses file mode/owner/group/tester credentials/permission/expected result, creates an empty test file, and for execute tests also creates a shebang file. A child drops to the tester credentials and attempts either open mode `r`/`w` or execution. Parent compares child exit status with the expected result and reports one LTP pass/fail line.

State/persistence behavior: creates temporary files `test.file1` and optionally `test.file2` in an LTP temp directory, changes their ownership and modes, and removes the temp directory at completion.

Dependencies/integration: requires root to chown and switch credentials. Integrated with legacy LTP `test.h` rather than modern `tst_test.h`.

Risks/test signals: `wait(&status)` assumes normal child exit before `WEXITSTATUS`. Execute behavior differs for kernel shebang handling versus libc fallback, which is why two files are tested. Success is exact match between observed child result and expected result.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_perms/fs_perms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_readonly/Makefile -->
# sources/test-tools/ltp/testcases/kernel/fs/fs_readonly/Makefile

Purpose: build/install metadata for the read-only bind mount test. It installs `test_robind.sh`, which exercises normal, bind, and read-only bind mounts.

Important APIs/types/functions: `top_srcdir`, `INSTALL_TARGETS := test_robind.sh`, `env_pre.mk`, and `generic_leaf_target.mk`.

Control flow: the Makefile delegates all build and install behavior to the LTP generic leaf rules after declaring the script target.

State/persistence behavior: no runtime state; persistent effect is installing the shell test into the LTP testcase tree.

Dependencies/integration: depends on the LTP make framework. Runtime behavior lives in `test_robind.sh`, which expects a large block device and filesystem mkfs/mount tools.

Risks/test signals: if this Makefile omits the script target, the readonly bind test will not be installed or runnable from LTP. Build success and target installation are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/fs/fs_readonly/Makefile -->

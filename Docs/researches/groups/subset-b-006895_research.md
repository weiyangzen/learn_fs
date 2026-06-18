# subset-b-006895 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/main.c -->
# sources/distributed-fs/ceph-client/tools/testing/vma/main.c

Purpose: user-space test entry point for Linux VMA code. It includes the local shims, then directly includes `mm/vma_init.c`, `mm/vma_exec.c`, `mm/vma.c`, and the three local test files so tests can reach static kernel helpers. APIs: defines `merge_existing()` and `attach_vma()` wrappers around static VMA internals, plus `main()`. Control flow: initialize maple tree and VMA state, run merge, mmap, and flag/copy test runners, print pass/fail counts, and return success only on zero failures. State: exposes `sysctl_max_map_count` and asserts VMAs are attached after merge/link operations. Dependencies: `shared.h`, maple tree shims, kernel VMA sources. Integration: single binary harness for `tools/testing/vma`. Risks: direct source inclusion is sensitive to kernel internal symbol and macro drift. Test signals: aggregate count and process exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/shared.c -->
# sources/distributed-fs/ceph-client/tools/testing/vma/shared.c

Purpose: common allocation and state helpers for the user-space VMA tests. Important APIs: `alloc_vma()`, `detach_free_vma()`, `alloc_and_link_vma()`, `cleanup_mm()`, `vma_write_started()`, dummy anon-vma setup helpers, `get_current()`, `rlimit()`, and `vma_set_range()`. Control flow: tests allocate VMAs with explicit ranges/flags, attach them through the static wrapper in `main.c`, then clean the maple tree by iterating all VMAs and freeing them. State: owns harness globals such as `fail_prealloc`, `mmap_min_addr`, `stack_guard_gap`, `dummy_anon_vma`, and fake `current`. Persistence is in-memory only. Dependencies: kernel VMA allocation/link/free stubs and maple tree iterators. Integration: used by all included test cases. Risks: helper stubs simplify real kernel lifetime/locking, so failures may not expose every in-kernel race. Test signals: assertions inspect map counts, detached/attached markers, anon-vma clone/unlink flags, and write-start sequence changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/shared.h

Purpose: shared declarations and assertion macros for the VMA test harness. Important APIs/types: `TEST`, `ASSERT_*`, VMA flag assertion macros, extern harness globals, `vma_iter_prealloc` override, dummy close hook, and prototypes for allocation, cleanup, anon-vma, and range helpers. Control flow: test runners use `TEST(name)` to count tests and print failures while individual tests short-circuit with boolean assertions. State: declares globals implemented in `shared.c`, including the preallocation-failure switch used to drive ENOMEM paths. Dependencies: generated bit-length data, maple shared code, local `vma_internal.h`, and kernel `mm/vma.h`. Integration: included before imported kernel VMA code and by every test file. Risks: macro-heavy assertions hide cleanup on early failure and can leak test allocations during a failing path. Test signals: precise file/function/line assertion messages and failure counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/tests/merge.c -->
# sources/distributed-fs/ceph-client/tools/testing/vma/tests/merge.c

Purpose: comprehensive VMA merge, split, expand, shrink, and anon-vma behavior tests. Important helpers: `merge_new()`, `expand_existing()`, `vmg_set_range()`, `vmg_set_range_anon_vma()`, and `try_merge_new_vma()`. Test flow covers simple merge/modify/expand/shrink, new-VMA merge permutations, special flags, `vm_ops->close` restrictions, existing-VMA merge permutations, incompatible anon-vmas, anon-vma duplication, preallocation ENOMEM cleanup, `vma_merge_extend()`, and expand-only mode. State: constructs temporary `mm_struct`, `vma_iterator`, `vma_merge_struct`, VMAs, dummy anon-vma chains, sticky flags, and failure injection through `fail_prealloc`. Dependencies: kernel merge internals exposed through direct inclusion and harness wrappers. Integration: `run_merge_tests()` registers fourteen test groups into the main harness. Risks: assumes simplified single-threaded locking and dummy close behavior, but targets subtle metadata and lifetime regressions. Test signals: map counts, VMA ranges/pgoff, merge state enums, write-start markers, clone/unlink flags, and attached assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/tests/merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/tests/mmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/vma/tests/mmap.c

Purpose: focused test for `__mmap_region()` integration with VMA insertion and merge behavior. Important function: `test_mmap_region_basic()`, registered by `run_mmap_tests()`. Control flow: sets `current->mm`, maps two nonadjacent ranges, then maps adjacent ranges that should merge with each side, leaving two final VMAs. It iterates the maple tree and validates start/end/pgoff for both merged regions. State: uses a local `mm_struct`, iterator, and read/write/mayread/maywrite flags; cleanup destroys the tree. Dependencies: imported kernel mmap/VMA implementation and harness globals such as fake `current`. Integration: run after merge tests by `main.c`. Risks: validates deterministic fixed addresses only and does not cover permissions, files, or error paths. Test signals: returned addresses, `mm.map_count == 2`, final VMA layout, and harness assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/tests/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/tests/vma.c -->
# sources/distributed-fs/ceph-client/tools/testing/vma/tests/vma.c

Purpose: unit tests for typed VMA flag helpers and `copy_vma()`. Important functions: `compare_legacy_flags()`, `test_copy_vma()`, and tests for unchanged/cleared flags, word operations when flags exceed 64 bits, test/test-any/test-all, clear, empty, diff, and, append, and count operations. Control flow: builds known flag sets, applies macro helpers to raw `vma_flags_t`, `vm_area_struct`, and `vm_area_desc`, and compares against legacy `vm_flags_t` where applicable. State: all in-memory local flag bitmaps and temporary VMAs; `copy_vma()` uses an `mm_struct` and maple tree cleanup. Dependencies: kernel VMA flag macros, generated bit-length header, and shared assertions. Integration: `run_vma_tests()` is invoked by `main.c`. Risks: macro expansion and conditional high-bit cases depend on generated `NUM_VMA_FLAG_BITS`; lower-bit parity may pass while high-bit behavior is skipped on smaller builds. Test signals: bitmap equality, legacy conversion parity, map attachment, and flag count values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/tests/vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/vma_internal.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/vma_internal.h

Purpose: user-space replacement for kernel `mm/vma_internal.h` used by the VMA test harness. Important APIs/types: defines `CONFIG_MMU`, `CONFIG_PER_VMA_LOCK`, duplicate `mm_flags_t`, `vma_flags_t`, `vm_flags_t`, `pgoff_t`, `pgprot_t`, `vm_fault_t`, and maps VM warning/bug macros to generic stubs. Control flow: header guard intentionally matches the kernel internal header so the shim precludes including the real one. State: no runtime state, but compile-time type layout and macro definitions control how imported kernel sources build. Dependencies: many local Linux compatibility headers plus `include/stubs.h`, `include/dup.h`, and `include/custom.h`. Integration: included through `shared.h` before kernel VMA implementation files. Risks: highest drift surface in the VMA harness; any mismatch with kernel internal type expectations can create false positives or compile failures. Test signals: successful build and execution of imported VMA sources under the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/vma_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/Makefile

Purpose: build recipe for vsock selftests and benchmark. Targets: `all`, `test`, `vsock_test`, `vsock_diag_test`, `vsock_uring_test`, `vsock_perf`, `clean`, and `install`. Control flow: compiles object groups with shared helpers; links pthread for `vsock_test` and liburing for `vsock_uring_test`; includes generated dependency files. State/persistence: build artifacts are local binaries, objects, and `.d` files; install copies binaries to `VSOCK_INSTALL_PATH`. Dependencies: kernel selftest headers through `-I../../include` and `-I../../../usr/include`, plus host `liburing` and pthread when needed. Integration: developer entry point for host/guest vsock validation. Risks: `-Werror` makes toolchain/header drift fail builds; `install` errors unless `VSOCK_INSTALL_PATH` is set. Test signals: successful binary builds and `clean` removal coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/control.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/control.c

Purpose: TCP control channel used to synchronize host/guest vsock tests. Important APIs: `control_init()`, `control_cleanup()`, `control_writeln()`, `control_readln()`, `control_writeulong()`, `control_readulong()`, `control_expectln()`, and `control_cmpln()`. Control flow: server resolves/binds/listens/accepts; client resolves/connects. Tests exchange newline-delimited tokens and numeric values with `TIMEOUT` protection. State: single static `control_fd`; cleanup closes it. Dependencies: sockets, `getaddrinfo`, `timeout.h`, `util.h` for checked socket options. Integration: all coordinated vsock test binaries use this for barriers, hashes, and phase handshakes. Risks: one global connection, fatal exits on protocol mismatch, line reads grow by realloc and can be abused by a bad peer, and timeout state is process-global. Test signals: expected line matching and fatal mismatch messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/control.h -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/control.h

Purpose: public interface for the vsock control-channel helper. APIs: declares initialization/cleanup, line read/write, unsigned-long exchange, expected-line check, and optional comparison helper. Control flow: callers use it as a synchronous barrier protocol around AF_VSOCK actions. State: hides the underlying file descriptor in `control.c`; callers only pass strings/numbers. Dependencies: `<stdbool.h>` and the implementation’s timeout/socket stack. Integration: included by `util.c`, `vsock_test.c`, `vsock_diag_test.c`, `vsock_uring_test.c`, and zerocopy tests. Risks: no namespace scoping and no support for multiple independent control channels in one process. Test signals: compile-time declarations and runtime peer protocol correctness through `control_expectln()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/msg_zerocopy_common.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/msg_zerocopy_common.c

Purpose: shared MSG_ZEROCOPY completion validator. API: `vsock_recv_completion(int fd, const bool *zerocopied)`. Control flow: calls `recvmsg(MSG_ERRQUEUE)`, verifies a single control message from `SOL_VSOCK`/`VSOCK_RECVERR`, checks `SO_EE_ORIGIN_ZEROCOPY`, no error code, and optionally verifies copied-vs-zerocopy fallback state through `SO_EE_CODE_ZEROCOPY_COPIED`. State: no persistent state; completion is consumed from the socket error queue. Dependencies: Linux error queue structures, socket control-message macros, and local constants. Integration: used by `vsock_perf`, `vsock_test_zerocopy.c`, and io_uring zerocopy tests. Risks: assumes exactly the expected completion shape and exits on deviations; a kernel adding extra cmsgs may require updates. Test signals: pass/fail of error-queue metadata and copied/zerocopied expectation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/msg_zerocopy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/msg_zerocopy_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/msg_zerocopy_common.h

Purpose: header for shared MSG_ZEROCOPY completion handling. APIs/types: declares `vsock_recv_completion()` and provides fallback definitions for `SOL_VSOCK` and `VSOCK_RECVERR` when host headers are older. Control flow: consumers enable zerocopy, poll for `POLLERR`, then call this helper to drain and validate completion. State: none. Dependencies: `<stdbool.h>` and Linux socket error-queue semantics in the implementation. Integration: included by the benchmark, classic zerocopy tests, and io_uring tests. Risks: fallback constants must match kernel ABI; mismatches would make tests fail incorrectly. Test signals: compile compatibility with older userspace headers and correct completion validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/msg_zerocopy_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/timeout.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/timeout.c

Purpose: small timeout API for blocking single-threaded test syscalls. APIs: `sigalrm()`, `timeout_begin()`, `timeout_check()`, `timeout_end()`, and `timeout_usleep()`. Control flow: `timeout_begin()` arms `alarm(seconds)`, loops call `timeout_check(operation)`, and `timeout_end()` clears alarm and timeout flag. `timeout_usleep()` uses `nanosleep()` so it does not conflict with alarm semantics. State: static volatile boolean set by SIGALRM. Dependencies: POSIX signals, alarm, nanosleep. Integration: used by control-channel and vsock socket helpers around connect/accept/send/recv/ioctl. Risks: not nestable, process-global, and unsuitable for multithreaded tests using independent alarms. Test signals: fatal timeout messages naming the blocked operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/timeout.h -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/timeout.h

Purpose: declaration header for the vsock timeout helper. APIs: exposes `TIMEOUT` default of 10 seconds and function prototypes for alarm handling, begin/check/end, and microsecond sleep. Control flow: included by blocking helper code so loops can be bounded without duplicating signal logic. State: implementation owns the timeout flag. Dependencies: `useconds_t` availability from included system headers in consumers. Integration: common to control, util, diagnostic, and main vsock tests. Risks: header does not document non-nesting beyond implementation comments, so misuse can cause premature timeout clearing. Test signals: consistent timeout constant across test programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/timeout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/util.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/util.c

Purpose: shared vsock selftest utility layer. Important APIs: signal setup, CID/port parsing, bind/connect/listen/accept wrappers, send/recv expectation helpers, test-case runner/list/pick/skip, hash/iovec helpers, socket option checkers, zerocopy/linger setup, and transport detection from `/proc/kallsyms`. Control flow: wrappers add control-channel synchronization, timeout loops, address validation, and fatal error reporting. The runner exchanges `NEXT/SKIP/COMPLETED` barriers with the peer. State: cached transport bitmask and process signal configuration; all other state is socket/file/memory local. Dependencies: AF_VSOCK, epoll, ioctl `SIOCOUTQ/SIOCINQ`, mmap/munmap, kernel kallsyms, `control.h`, `timeout.h`. Integration: foundation for all vsock test binaries. Risks: exits on most errors, assumes host/guest clock and transport behavior, uses `/proc/kallsyms` visibility for transport classification, and pointer arithmetic on mmap bases is test-specific. Test signals: exact byte counts, errno checks, hashes, socket-option readback, and barrier completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/util.h -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/util.h

Purpose: public definitions for vsock selftest helpers. Important types: `enum transport`, `enum test_mode`, `struct test_opts`, and `struct test_case`. Constants define known transport symbols, G2H/H2G/local masks, and default peer port. APIs cover socket creation, synchronization-aware connect/accept, checked I/O, test selection, hashing, iovec allocation, socket option validation, zerocopy/linger enablement, and transport probing. Control flow: test programs populate `test_case` arrays and pass them to `run_tests()`. State: exposes transport symbol table as static const data in each translation unit. Dependencies: Linux bitops/kernel/vm_sockets headers. Integration: common ABI between `util.c` and every vsock test source. Risks: transport list must track kernel `vsock_core_register()` users; stale symbols make feature warnings misleading. Test signals: compile-time static assertions for table size/bit capacity and runtime helper outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_diag_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_diag_test.c

Purpose: validates `vsock_diag` netlink reporting. Important pieces: `struct vsock_stat`, socket state/type/shutdown printers, `send_req()`, `recv_resp()`, `read_vsock_stat()`, list/free helpers, and tests for no sockets, listening socket, and connected sockets. Control flow: opens `NETLINK_SOCK_DIAG`, dumps AF_VSOCK states, builds a list of `vsock_diag_msg`, finds entries by inode, and checks expected TCP-like states. State: transient linked list of socket stats; command-line options configure mode, control host/port, peer CID/port, list, and skip. Dependencies: netlink sock_diag, Linux list macros, control and util helpers. Integration: built by the vsock Makefile and run on both host and guest. Risks: requires `vsock_diag` support and assumes no unrelated vsock sockets for the no-sockets test. Test signals: list count, inode matching, state equality, and peer barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_diag_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_perf.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_perf.c

Purpose: AF_VSOCK throughput benchmark with optional MSG_ZEROCOPY. Important APIs: `memparse()`, local `vsock_connect()`, `run_receiver()`, `run_sender()`, `enable_so_zerocopy()`, and option parsing in `main()`. Control flow: receiver binds/listens/accepts, raises vsock buffer sizes, applies `SO_RCVLOWAT`, polls and reads until EOF, then prints throughput and read timing. Sender connects, allocates or mmaps a buffer, sends the requested byte count, optionally waits for zerocopy completions after each send, and reports TX metrics. State: global port, buffer sizes, socket buffer size, and zerocopy flag from CLI. Dependencies: AF_VSOCK, poll, mmap, `msg_zerocopy_common`. Integration: standalone benchmark built alongside tests. Risks: performance numbers depend on scheduling, buffer options, transport, and zerocopy completion behavior; no control channel synchronizes start. Test signals: total bytes, Gbit/s, syscall timing, POLLERR completions for zerocopy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test.c

Purpose: main AF_VSOCK functional and regression suite. Test families cover stream reset/bind/close/multiconnection, MSG_PEEK, seqpacket message bounds/truncation/timeouts/big messages/invalid buffers, `SO_RCVLOWAT`, invalid user buffers, virtio skb merge, shutdown SIGPIPE, double bind/connect, `SIOCOUTQ`/`SIOCINQ`, virtio credit updates, accept queue and zerocopy leak probes, transport UAF and transport-change races, connect retry, linger behavior, accepted-socket options, zerocopy coalescence corruption, TX credit bounds, and peek after partial receive. Control flow: command-line parser configures client/server mode, control channel, peer CID/port, skip/pick/list; `run_tests()` drives synchronized pairs from `test_cases`. State: local sockets, buffers, timers, signal handler for SIGPIPE and transport-change stress thread. Dependencies: `util`, `control`, `timeout`, zerocopy tests, pthread, AF_VSOCK ioctls/options. Integration: primary selftest binary. Risks: environment-sensitive tests may print skips/warnings; leak tests require external kmemleak scanning. Test signals: errno/byte/hash comparisons, poll flags, control barriers, and absence of kernel crashes/warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test_zerocopy.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test_zerocopy.c

Purpose: MSG_ZEROCOPY-specific test implementations used by `vsock_test.c`. Important types: `struct vsock_test_data` describing stream-only status, expected zerocopy/copy fallback, `SO_ZEROCOPY` enablement, expected `sendmsg` errno, and iovec patterns. Control flow: clients allocate test iovecs, optionally enable zerocopy, send with `MSG_ZEROCOPY`, validate error-queue completions when expected, send hashes to server, and close. Servers read expected bytes and compare hashes. Extra tests check empty error queue and virtio zerocopy skb coalescence corruption. State: static table of aligned, unaligned, large, unmapped, and fallback cases; transient mmap-backed iovecs. Dependencies: `util` iovec/hash helpers, `control`, `timeout`, and `msg_zerocopy_common`. Integration: functions exported through header and referenced in main test-case table. Risks: relies on kernel zerocopy ABI and transport support; mmap-unmapped cases are intentionally fault-oriented. Test signals: send errno, byte counts, POLLERR, zerocopy copied flag, and hash equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test_zerocopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test_zerocopy.h -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test_zerocopy.h

Purpose: declares zerocopy test entry points used by the main vsock test matrix. APIs: stream and seqpacket MSG_ZEROCOPY client/server pairs, empty error-queue stream pair, and stream coalescence-corruption pair. Control flow: `vsock_test.c` installs these functions directly in `struct test_case` entries. State: no header state. Dependencies: includes `util.h` for `struct test_opts`. Integration: separates zerocopy implementation from the already large main suite while preserving one executable. Risks: any signature drift from `struct test_case` callbacks breaks compile-time linkage. Test signals: successful linking and execution through named main-suite test cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_test_zerocopy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_uring_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_uring_test.c

Purpose: validates AF_VSOCK send/receive through io_uring, including zerocopy sendmsg. Important types/functions: `struct vsock_io_uring_test`, `vsock_io_uring_client()`, `vsock_io_uring_server()`, stream normal and MSG_ZEROCOPY wrappers, `test_cases`, and CLI `main()`. Control flow: client connects, optionally enables zerocopy, allocates/registers buffers, submits `io_uring_prep_sendmsg()` or `io_uring_prep_sendmsg_zc()`, waits for a CQE, sends a hash over the control channel, and cleans up. Server accepts and loops `io_uring_prep_readv()` until expected bytes arrive, then compares hash. State: static aligned and unaligned iovec patterns; transient io_uring rings. Dependencies: liburing, `util`, `control`, `msg_zerocopy_common` include, AF_VSOCK. Integration: separate binary linked with `-luring` and run like other host/guest tests. Risks: does not inspect send CQE result before trusting completion, and needs kernel/liburing support. Test signals: CQE progress, received length, hash equality, and control barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vsock/vsock_uring_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/Makefile -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/Makefile

Purpose: builds and installs `libthermal_tools` static/shared helper library. Targets: library object aggregation, `.a`, `.so` with versioned symlinks, pkg-config generation, install libs/headers/pkgconfig, clean. Control flow: derives `srctree`, imports kernel tools build includes, sets include paths for libthermal/tools/uapi headers, compiles PIC objects, links shared library, and generates `libthermal_tools.pc` from template. State/persistence: produces archives, shared libraries, symlinks, pkg-config file, and installed headers under `DESTDIR`/`prefix`. Dependencies: tools build framework, architecture include detection, libthermal headers, install utility. Integration: consumed by thermal-engine and thermometer Makefiles. Risks: apparent `CFGLAS` typo means intended linker flags may be inert; `-Werror` makes warning drift fatal. Test signals: successful `libs`, generated pkg-config, and install artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/log.c -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/log.c

Purpose: lightweight logging backend for thermal tools. APIs: `log_str2level()`, `logit()`, `log_init()`, and `log_exit()`. Control flow: level strings are matched against syslog levels, `log_init()` validates options/level/ident and opens syslog if requested, and `logit()` fans a formatted message to syslog, stderr, and/or stdout depending on option bits. State: static identity string and output option bitmask. Dependencies: stdio, syslog, varargs. Integration: macros in `log.h` call `logit()` throughout thermal tools. Risks: `logit()` reuses one `va_list` across multiple sinks without `va_copy`, which is undefined if more than one output option is set; `level > LOG_DEBUG` validation assumes syslog numeric ordering. Test signals: log output routing and return codes from `log_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/log.h -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/log.h

Purpose: logging interface and convenience macros for thermal tools. APIs/macros: output flags `TO_SYSLOG`, `TO_STDOUT`, `TO_STDERR`; `logit()`; severity macros `DEBUG`, `INFO`, `NOTICE`, `WARN`, `ERROR`, `CRITICAL`, `ALERT`, `EMERG`; and lifecycle/level conversion declarations. Control flow: callers use severity macros that map directly to syslog levels; `DEBUG` also adds function and line. State: no header state, implementation holds ident/options. Dependencies: `<syslog.h>` and `__maybe_unused` compatibility macro. Integration: included by `thermal-tools.h` and directly by library implementation. Risks: macros evaluate formatting arguments in logging calls regardless of output mask and do not provide compile-time format checking. Test signals: compilation and visible severity-prefixed/debug-location output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/mainloop.c -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/mainloop.c

Purpose: simple epoll-based event loop for thermal tools. APIs: `mainloop_init()`, `mainloop_add()`, `mainloop_del()`, `mainloop()`, `mainloop_exit()`, and `mainloop_fini()`. Control flow: create epoll fd, add file descriptors with callback/data wrappers, wait for up to ten events, invoke callbacks, and stop on timeout, explicit exit flag, or callback returning positive. State: static `epfd` and `exit_mainloop`; each add allocates a `mainloop_data`. Dependencies: epoll, malloc/free, signal-safe flag type, logging include. Integration: used by thermal-engine for netlink events and thermometer for timerfd/signalfd polling. Risks: `mainloop_del()` does not free `mainloop_data`, `mainloop_fini()` does not reset `epfd`, and callbacks are only registered for `EPOLLIN`. Test signals: callback invocation, loop exit behavior, and error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/mainloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/mainloop.h -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/mainloop.h

Purpose: declaration header for the thermal-tools event loop. Types/APIs: `mainloop_callback_t` and prototypes for loop, add/delete, exit, init, and fini. Control flow: applications initialize once, register fds with callbacks, run `mainloop(timeout)`, and request shutdown through `mainloop_exit()`. State: hidden in implementation. Dependencies: none beyond C function declarations. Integration: included through `thermal-tools.h` by thermal-engine and thermometer. Risks: callback contract only documents positive return ending the loop through implementation behavior, not comments; callers must manage fd lifetime carefully. Test signals: compile linkage and runtime epoll callback delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/mainloop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/thermal-tools.h -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/thermal-tools.h

Purpose: umbrella header for the small thermal tools support library. APIs: includes logging, mainloop, and uptime-of-day helpers. Control flow/state: no executable logic or state; it centralizes the common library surface for tools. Dependencies: `log.h`, `mainloop.h`, and `uptimeofday.h`. Integration: included by `uptimeofday.c`, `thermal-engine.c`, and `thermometer.c`, allowing tools to include one local header for shared helpers. Risks: broad inclusion can expose unrelated macros and names to consumers, but the file is intentionally small. Test signals: compile success for consumers using the combined helper API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/thermal-tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/uptimeofday.c -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/uptimeofday.c

Purpose: converts wall-clock time to an uptime-relative millisecond timestamp and provides millisecond-to-timespec conversion. APIs: `uptimeofday_init()`, `getuptimeofday_ms()`, and `msec_to_timespec()`. Control flow: initialization reads `sysinfo().uptime` and `gettimeofday()` to compute an offset; subsequent reads subtract the offset from current wall clock and convert to milliseconds. State: static offset and reusable timeval. Dependencies: sysinfo, gettimeofday, timespec. Integration: thermometer timestamps samples with uptime-like values and configures timerfd durations using `msec_to_timespec()`. Risks: uses wall-clock time rather than monotonic time after initialization, so clock adjustments can perturb reported uptime milliseconds. Test signals: init return code and plausible monotonic-ish timestamps in output files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/uptimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/uptimeofday.h -->
# sources/distributed-fs/ceph-client/tools/thermal/lib/uptimeofday.h

Purpose: public declarations for uptime-of-day helper functions. APIs: init, millisecond timestamp retrieval, and `msec_to_timespec()`. Control flow: consumers call init before first timestamp, then use conversions for output and timer setup. State: implementation keeps static offset/timeval. Dependencies: sysinfo/time headers for types. Integration: pulled in by `thermal-tools.h`, used mainly by thermometer. Risks: header exposes `struct timespec` while only including sysinfo/time headers; consumers rely on those headers providing the type on the target libc. Test signals: successful build and correct timer/timestamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/lib/uptimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermal-engine/Makefile -->
# sources/distributed-fs/ceph-client/tools/thermal/thermal-engine/Makefile

Purpose: builds the `thermal-engine` tool against libthermal and the local helper library. Control flow: derives `srctree`, sets include paths for `tools/thermal/lib` and `tools/lib/thermal/include`, links against `libthermal_tools`, `libthermal`, libconfig, and libnl, defines `VERSION`, and compiles `%: %.c` to a binary. State/persistence: creates `thermal-engine`; `clean` removes it. Dependencies: thermal helper library, kernel tools libthermal, libconfig, libnl-genl/libnl. Integration: consumer of `tools/thermal/lib`. Risks: generic pattern rule may build unexpected C files if invoked directly; link line requires prebuilt libraries and correct library search paths. Test signals: successful binary link and clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermal-engine/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermal-engine/thermal-engine.c -->
# sources/distributed-fs/ceph-client/tools/thermal/thermal-engine/thermal-engine.c

Purpose: thermal event monitor based on libthermal netlink notifications. Important pieces: option parsing, `thermal_data`, display callbacks for zones/trips/thresholds/temp/governor, threshold setup, event callbacks for zone/trip/cdev/governor/threshold changes, and `thermal_event()` mainloop adapter. Control flow: parse logging/daemon options, initialize logging and libthermal, discover zones, flush/add fixed thresholds, print current zones, initialize epoll loop, register the libthermal events fd, then process events indefinitely. State: discovered thermal zones and handler pointer; callbacks update in-memory trip and governor fields. Dependencies: libthermal, thermal-tools logging/mainloop, libnl via library link. Integration: example/utility consumer of libthermal event APIs. Risks: callbacks assume `thermal_zone_find_by_id()` succeeds, threshold values are hard-coded, and daemon mode plus stdout default require option care. Test signals: discovered zone output, threshold installation errors, event logs, and mainloop return code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermal-engine/thermal-engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermometer/Makefile -->
# sources/distributed-fs/ceph-client/tools/thermal/thermometer/Makefile

Purpose: builds the `thermometer` sampling tool. Control flow: derives `srctree`, includes `tools/thermal/lib`, links with `libthermal_tools` and libconfig, defines `VERSION`, and uses a generic `%: %.c` compile/link rule. State/persistence: creates the `thermometer` binary; `clean` removes it. Dependencies: local helper library and libconfig. Integration: sibling consumer of `tools/thermal/lib`. Risks: comment says cgroup tools despite being thermal; build requires the helper library already available in the specified search path. Test signals: successful build and clean target behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermometer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermometer/thermometer.c -->
# sources/distributed-fs/ceph-client/tools/thermal/thermometer/thermometer.c

Purpose: samples thermal zone temperatures to per-zone output files, optionally while running a child command. Important types: `options`, `tz_regex`, `configuration`, `tz`, and `thermometer`. Control flow: parse options, initialize logging/configuration/time/mainloop, scan `/sys/class/thermal/thermal_zone*/type`, match configured regexes, open `temp` fds, create output files, create timerfds per zone, write `timestamp(ms) temperature` rows on callbacks, optionally fork/exec a command, and exit on duration timer or signals. State: regex array, open sysfs fds, timer fds, FILE outputs, child pid, and output directory/postfix. Persistence: writes capture files named from thermal zone and postfix. Dependencies: libconfig, regex, signalfd, timerfd, sysfs thermal class, thermal-tools. Risks: uses `strcpy`/`sprintf` into PATH_MAX buffers, leaks some allocated paths/regex/name memory until exit, and `kill_process()` error logging uses `%p` for process errors. Test signals: created files with headers and samples, graceful close/flush, command termination, and runtime error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermometer/thermometer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermometer/thermometer.conf -->
# sources/distributed-fs/ceph-client/tools/thermal/thermometer/thermometer.conf

Purpose: sample libconfig configuration for `thermometer`. Content: a `thermal-zones` list with one entry matching `cpu[0-9]-thermal` and polling every 100 milliseconds. Control flow: consumed by `configuration_init()`, which compiles the `name` field as an extended regular expression and stores the polling interval. State/persistence: no runtime state, but determines which sysfs zones will be sampled and at what timer interval. Dependencies: libconfig syntax and thermal zone type names from `/sys/class/thermal`. Integration: example config for the thermometer CLI `--config` option. Risks: platform-specific zone names mean this sample may match nothing on non-CPU or differently named thermal zones. Test signals: parser accepts file, log reports one regex, and matching zones produce output files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/thermometer/thermometer.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/Makefile -->
# sources/distributed-fs/ceph-client/tools/thermal/tmon/Makefile

Purpose: builds, installs, and packages the `tmon` ncurses thermal monitor. Control flow: includes `../../build/Build.include` for `cc-option`, sets optimization and warning flags, probes stack protector support, discovers ncurses/panel flags through pkg-config with fallbacks, builds `tmon` from `tmon.o tui.o sysfs.o pid.o`, and provides valgrind/install/uninstall/clean/dist targets. State/persistence: creates binary and object files; install copies to `$(INSTALL_ROOT)/usr/bin/tmon`; dist tags and archives. Dependencies: math, pthread, ncurses/panel, pkg-config, build include. Integration: `pid.c` is one object in the monitor. Risks: `dist` creates a git tag as a side effect, and strict warnings may fail on newer compilers. Test signals: successful link against curses libs, valgrind target, clean removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/pid.c -->
# sources/distributed-fs/ceph-client/tools/thermal/tmon/pid.c

Purpose: PID controller for `tmon` cooling-device control tests. Important APIs/state: global `struct pid_params p_param`, cached previous inputs `xk_1`/`xk_2`, `init_thermal_controller()`, `controller_reset()`, and `controller_handler()`. Control flow: init seeds controller gains and target from global `ticktime`/`target_temp_user`; handler computes Type C PID terms from current temperature, target error, and previous samples, clamps output to cooling limits, stores `y_k`, and calls `set_ctrl_state()`. If temperature is sufficiently below setpoint, it resets and relaxes control. Dependencies: `tmon.h`, math `lround/fabs`, syslog, external globals and `set_ctrl_state()`. Integration: called periodically by tmon’s thermal data loop. Risks: `xk_2` is assigned after `xk_1 = xk`, losing the older sample and weakening derivative history; gains are hard-coded. Test signals: syslog debug messages and cooling state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/thermal/tmon/pid.c -->

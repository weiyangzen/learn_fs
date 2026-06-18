# Grouped Research Report: subset-b-009282

This grouped report covers the exact source files assigned to `subset-b-009282`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/xml2lcov/xml2lcov.sh -->
## sources/test-tools/lcov/tests/xml2lcov/xml2lcov.sh

Purpose: Bash regression test for lcov's `xml2lcov` converter. It exercises successful conversion of a bundled Cobertura-style `coverage.xml`, usage/help behavior, expected failures for missing source/version data and bad command lines, lcov aggregation syntax validation, and optional Python coverage reporting.

Important APIs/functions: the script is command-line orchestration rather than a library. It consumes variables and helper functions from `../common.tst`, including `clean_cover`, `PYCOVER`, `XML2LCOV_TOOL`, `LCOV_TOOL`, `PY2LCOV_TOOL`, `GENHTML_TOOL`, `KEEP_GOING`, `CLEAN_ONLY`, `USE_GIT`, `IS_GIT`, `IS_P4`, `PARALLEL`, `PROFILE`, and coverage-related paths. It dynamically selects version and annotate scripts for git or Perforce.

Control flow: cleanup is first, then an early `CLEAN_ONLY` exit. The test establishes VCS-specific `VERSION`/`ANNOTATE` options, requires `PY2LCOV_SCRIPT` to be executable, runs positive xml2lcov conversions, runs negative conversions that must fail, captures `--help` output and greps for usage text, aggregates generated lcov info with `--ignore inconsistent`, and optionally emits lcov/genhtml coverage for the Python converter.

State and persistence: creates and deletes local `*.info`, `*.json`, `help.txt`, `*.pyc`, `*.dat`, `__pycache__`, and generated coverage folders/files. It does not modify repository configuration.

Dependencies/integration: depends on lcov test harness conventions, bundled `coverage.xml`, VCS helper scripts, Python coverage tooling, and lcov/genhtml binaries. Integration point is the lcov test suite, where exit status determines pass/fail.

Risks: heavy use of `eval` around tool/options variables can misbehave if variables contain unexpected shell metacharacters. Negative tests assume version lookup fails without source. The disabled keep-going block is untested drift risk. Aggregation knowingly tolerates inconsistent coverage input.

Test signals: explicit failure messages and exits on unexpected status; final `Tests passed`; lcov aggregation validates generated syntax.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/xml2lcov/xml2lcov.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/.github/workflows/ci.yml -->
## sources/test-tools/liburing/.github/workflows/ci.yml

Purpose: GitHub Actions CI pipeline for liburing. It validates many compiler/architecture combinations, sanitizer variants, installability, out-of-source builds, Alpine/musl compatibility, spelling, and shell scripts.

Important APIs/types/functions: GitHub Actions jobs `get_commit_list`, `build`, `out-of-source-build`, `alpine-musl-build`, `codespell`, and `shellcheck`; matrix fields for architecture, compiler packages, compiler commands, sanitizer settings, and extra flags. It invokes `./configure`, `make`, `sudo make install`, and compiles `.github/workflows/test_build.c` against installed `-luring`.

Control flow: first job computes a reverse commit list from push commits or falls back to current SHA. All other jobs matrix over that list. Main build job installs appropriate cross or clang toolchains, runs configure/build in normal, ASAN/UBSAN, or TSAN mode, tests installation, then compiles a tiny C and C++ consumer. Separate jobs cover out-of-source build cleanliness, Alpine chroot build/install, codespell, and shellcheck.

State and persistence: CI creates build artifacts, installs into runner system paths with `sudo make install`, and writes summaries via `$GITHUB_OUTPUT`/`$GITHUB_STEP_SUMMARY`. Out-of-source job checks that ignored/untracked source-tree leakage, except `build`, is absent.

Dependencies/integration: integrates with Ubuntu 24.04, apt cross compilers, apt.llvm.org clang 22 installer, `jirutka/setup-alpine`, codespell, shellcheck, repo `configure`, top-level Makefile, and installed pkg/linker paths.

Risks: matrix is broad and expensive; commit-list expression can be fragile on non-push events with missing `github.event.commits[0]`. Clang install script is network-sensitive. The Alpine build uses `CFLAGS="$FLAGS"` but `FLAGS` is only defined in the main build job env, so Alpine may not receive intended warnings. Out-of-source final compile path references `.github/workflows/test_build.c` from inside build, relying on generated proxy Makefiles or working directory assumptions.

Test signals: successful multi-arch compilation with `-Werror`, sanitizer builds, install smoke tests, clean out-of-source tree, codespell clean run, and shellcheck success.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/.github/workflows/test_build.c -->
## sources/test-tools/liburing/.github/workflows/test_build.c

Purpose: Minimal installed-library smoke test used by CI to prove headers and linker artifacts from `make install` are usable by external C and C++ compilation commands.

Important APIs/functions: includes `<liburing.h>`, declares `struct io_uring`, calls `io_uring_queue_init(8, &ring, 0)`, then `io_uring_queue_exit(&ring)`.

Control flow: initialize ring, immediately tear it down, return zero. There is no error checking because the file is primarily a compile/link smoke test, not a runtime behavior test.

State and persistence: creates an io_uring instance at runtime if executed, but CI only needs successful compile/link into `a.out`.

Dependencies/integration: depends on installed liburing headers and `-luring`. CI compiles it once as C and once as C++ to catch header compatibility issues.

Risks: missing error handling means execution on kernels without io_uring could still return zero if the init failed, but the intended signal is build linkage. It does not test pkg-config or runtime library search paths.

Test signals: compiler and linker success in CI after install.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/.github/workflows/test_build.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/Makefile -->
## sources/test-tools/liburing/Makefile

Purpose: Top-level build orchestration for liburing. It delegates library, test, and example builds, generates pkg-config files, installs/uninstalls library/manpage/test artifacts, and supports source archives and SRPMs.

Important targets/APIs: `all`, `library`, `runtests`, `runtests-loop`, `runtests-parallel`, `config-host.mak`, `%.pc`, `install`, `uninstall`, `install-tests`, `clean`, `archive`, and `srpm`. It includes `Makefile.common`, `Makefile.quiet` indirectly through subdirs, and `config-host.mak` after auto-running `configure`.

Control flow: `all` recursively builds `src`, `test`, and `examples`. If not cleaning, `config-host.mak` is included and regenerated via `configure` when absent/out-of-date. Pkg-config files are generated from `.pc.in` templates using `sed`. Install recurses into `src`, writes pkg-config files, and installs manpages.

State and persistence: writes `config-host.mak`, `config-host.h`, `liburing.pc`, `liburing-ffi.pc`, build outputs, installed headers/libs, manpages, and archive/SRPM files. Clean removes local generated config and artifacts plus delegated subdir outputs.

Dependencies/integration: relies on `configure` for feature detection, recursive `make` in `src`, `test`, and `examples`, RPM tooling for `srpm`, git for archives/tags, and install paths from config.

Risks: recursive make hides some dependency edges. `config-host.mak` replays the old configure command by parsing a comment, which can break if quoting is complex. Install directly writes into configured paths and must be combined carefully with `DESTDIR`.

Test signals: `make all`, `make runtests*`, `make install`, CI out-of-source and install smoke tests.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/configure -->
## sources/test-tools/liburing/configure

Purpose: POSIX shell configure script that detects compiler/platform/kernel-header capabilities, writes `config-host.mak` and `config-host.h`, supports out-of-source build proxy Makefiles, and generates public compatibility/version headers.

Important functions/APIs: option parser for install dirs, compilers, `--use-libc`, `--enable-sanitizer`, `--enable-tsan`; helpers `fatal`, `print_config`, `do_cc`, `do_cxx`, `compile_prog`, `compile_prog_cxx`, `output_mak`, `output_sym`; generated symbols such as `CONFIG_NOLIBC`, `CONFIG_HAVE_KERNEL_RWF_T`, `CONFIG_HAVE_OPEN_HOW`, `CONFIG_HAVE_STATX`, `CONFIG_HAVE_UCONTEXT`, `CONFIG_HAVE_MEMFD_CREATE`, `CONFIG_HAVE_NVME_URING`, `CONFIG_HAVE_FUTEXV`, `CONFIG_HAVE_UBLK_HEADER`, sanitizer/TSAN flags.

Control flow: parse options and defaults, optionally print help, create out-of-source forwarding Makefiles, prepare temp compile files with cleanup trap, initialize config outputs, run a sequence of compile probes, write feature symbols, emit compiler/build variables, query `Makefile.common` for version, generate `src/include/liburing/io_uring_version.h`, and generate `src/include/liburing/compat.h` with fallback type/constant definitions.

State and persistence: removes and recreates `config-host.mak`, `config-host.h`, `config.log`, generated version and compatibility headers, and out-of-source stub Makefiles. Uses a temp directory cleaned on exit.

Dependencies/integration: invokes C/C++ compilers, `make`, kernel/uapi headers, pkg-config for libbpf, optional clang/bpftool for BPF, and architecture support for nolibc. Its outputs are included by top-level, src, examples, and tests.

Risks: compile probes depend on host headers and cross-compilers being runnable enough for compile/link checks. The script calls `clang -target bpf` even when `clang` may not exist, causing logged shell errors but nonfatal behavior. `--disable-werror` is mentioned in an error message but not parsed. Generated headers are source-tree state and must be cleaned for reproducibility.

Test signals: CI exercises native, cross, sanitizer, TSAN, out-of-source, and musl configure paths. Successful generated config enables all downstream builds.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/debian/rules -->
## sources/test-tools/liburing/debian/rules

Purpose: Debian package build rules for liburing using debhelper.

Important targets/APIs: default `%: dh $@ --parallel`, `override_dh_auto_configure`, and `override_dh_auto_test`. It includes dpkg defaults/buildtools and sets hardening and CFLAGS maintenance variables.

Control flow: debhelper owns most phases. Configure override passes Debian multiarch install paths, `/usr` prefix, man/data dirs, libdevdir, and `CC`. Test override runs `make runtests` only when `DEB_BUILD_OPTIONS` does not include `nocheck`; the file appends `nocheck`, so tests are skipped by default.

State and persistence: writes normal Debian build artifacts through debhelper and liburing build outputs. No custom persistent state outside package build.

Dependencies/integration: integrates with Debian `dh`, `dpkg` variables, `configure`, top-level Makefile, and package metadata.

Risks: default `DEB_BUILD_OPTIONS += nocheck` suppresses package-time tests unless overridden. Only `CC` is passed, not CXX. Multiarch libdir/libdevdir must align with package file lists.

Test signals: successful `dh_auto_configure`, build, install staging, and optionally `make runtests`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/Makefile -->
## sources/test-tools/liburing/examples/Makefile

Purpose: Builds liburing example programs against the in-tree static library.

Important targets/variables: `example_srcs`, `example_targets`, `helpers.o`, pattern target `%: %.c $(helpers) ../src/liburing.a`, `all`, `clean`, sanitizer/TSAN flag handling, conditional `CONFIG_HAVE_UCONTEXT`.

Control flow: include generated config unless cleaning, assemble source list, optionally add `ucontext-cp.c`, compile `helpers.o`, and link each example with `helpers.o`, `../src/liburing.a`, `-luring`, and pthread. Sanitizer options are appended when configured.

State and persistence: creates example binaries and `helpers.o`; clean removes all targets.

Dependencies/integration: depends on `config-host.mak`, `Makefile.quiet`, liburing headers from source, `../src/liburing.a`, pthread, and source files in `examples`.

Risks: `all_targets += ucontext-cp helpers.o` is outside the `CONFIG_HAVE_UCONTEXT` block, so clean may remove `ucontext-cp` even when not built. Pattern target links every C file with helpers, which is convenient but can mask unused helper coupling.

Test signals: CI `make examples` under many compilers and sanitizers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/echo-server.c -->
## sources/test-tools/liburing/examples/echo-server.c

Purpose: TCP echo server demonstrating modern io_uring networking with multishot accept, multishot receive, provided buffer rings, CQ ring sizing, and taskrun setup fallback.

Important APIs/types/functions: `struct conn`, `enum event_type`, global `ring`, `buf_ring`, `bufs`, `conns`; `encode_userdata`/decode helpers; `get_sqe`; `setup_buffer_ring`, `recycle_buffer`; `add_multishot_accept`, `add_recv`, `add_send`; handlers `handle_accept`, `handle_recv`, `handle_send`; `event_loop`; `setup_listening_socket` from helpers.

Control flow: main parses optional port, opens listening socket, initializes ring with `SUBMIT_ALL`, `CQSIZE`, `SINGLE_ISSUER`, `DEFER_TASKRUN` or fallback `COOP_TASKRUN`, registers provided buffers, arms accept, then loops over CQEs. Accept creates connection state and arms recv. Recv validates selected buffer, queues send, marks rearm when multishot stops or ENOBUFS occurs. Send recycles the buffer and rearms recv if needed.

State and persistence: persistent in-memory connection table indexed by fd, provided buffer ring, and heap buffer slab. Network sockets persist until closed; no files are written.

Dependencies/integration: requires liburing, helpers, kernel support for buffer rings and multishot recv, TCP sockets, and recent taskrun flags.

Risks: fd is packed into 16 bits and array-indexed; high fd values are rejected only above `MAX_CONNS`. Sends do not handle short positive sends for production. ENOBUFS recovery depends on send completions. No signal-driven shutdown path.

Test signals: manual `nc localhost 8000`; build coverage in examples; runtime kernel errors produce clear messages.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/echo-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/helpers.c -->
## sources/test-tools/liburing/examples/helpers.c

Purpose: Shared helper implementation for example programs.

Important APIs/functions: fallback `memfd_create` via `syscall(SYS_memfd_create)` when `CONFIG_HAVE_MEMFD_CREATE` is absent; `setup_listening_socket(int port, int ipv6)`; `t_aligned_alloc`; `t_error`.

Control flow: `setup_listening_socket` selects IPv4/IPv6 domain, creates stream socket, enables `SO_REUSEADDR`, binds to wildcard address, listens with backlog 1024, and returns fd. Allocation wrapper delegates to `posix_memalign`. Error helper prints formatted message plus optional errno string then exits.

State and persistence: creates listening sockets and heap allocations for callers. No global state.

Dependencies/integration: used by echo server, proxy, registered wait, zcrx, and other examples needing socket setup, aligned allocation, or test-style fatal errors.

Risks: on setsockopt/bind/listen failures, the socket fd is not closed before returning `-1`, causing minor leaks in failing examples. `t_error` exits directly, unsuitable for library contexts. Fallback `memfd_create` declaration may conflict if config detection is wrong.

Test signals: example builds and runtime paths that use socket setup/aligned allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/helpers.h -->
## sources/test-tools/liburing/examples/helpers.h

Purpose: Header exposing shared example helpers and compatibility declarations.

Important APIs/types: `T_ALIGN_UP(v, align)` macro; prototypes for `setup_listening_socket`, `t_aligned_alloc`, `t_error`, and `memfd_create`; conditional include of `<linux/memfd.h>` when config lacks memfd create.

Control flow: header-only declarations and macro expansion; no runtime flow.

State and persistence: none directly.

Dependencies/integration: included by examples that share socket setup, aligned allocation, and fatal error handling. Relies on generated `config-host.h` being force-included by build flags so `CONFIG_HAVE_MEMFD_CREATE` is meaningful.

Risks: `T_ALIGN_UP` assumes power-of-two alignment and can double-evaluate arguments. The unconditional `memfd_create` prototype under all configs must match libc signature.

Test signals: compile success across glibc, musl, Android-like configurations, and examples using these helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-close-test.c -->
## sources/test-tools/liburing/examples/io_uring-close-test.c

Purpose: Demonstrates registering the io_uring ring fd and closing the original ring fd while continuing to submit I/O via the registered ring fd.

Important APIs/functions: `io_uring_queue_init`, `io_uring_register_ring_fd`, `io_uring_close_ring_fd`, `io_uring_prep_readv`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_cqe_seen`.

Control flow: initialize ring, register and close ring fd, open input file, allocate four aligned 4 KiB buffers, queue readv requests up to file size, submit, wait for all completions, validate each is full-sized except final EOF chunk, print summary, close file and ring.

State and persistence: reads input file and allocates buffers. It leaks allocated iovec buffers and iovec array before exit, acceptable for short example but not reusable code.

Dependencies/integration: depends on liburing registered ring fd support and normal file I/O.

Risks: no cleanup on many early errors; no `O_DIRECT` but uses aligned buffers anyway; condition uses `offset > sb.st_size`, so exact-size boundary handling differs from `io_uring-test.c`. Demonstration assumes kernel supports ring fd registration.

Test signals: successful run prints submitted/completed/bytes and validates CQE byte counts.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-close-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-cp.c -->
## sources/test-tools/liburing/examples/io_uring-cp.c

Purpose: Asynchronous file/block-device copy example using separate read and write SQEs, bounded queue depth, and short I/O repair.

Important APIs/types/functions: `struct io_data` carries operation state, offsets, first length, and iovec; `get_file_size`; `queue_read`, `queue_write`, `queue_prepped`; `copy_file`; `io_uring_prep_readv`, `io_uring_prep_writev`.

Control flow: main opens input/output, initializes ring, determines input size, and calls `copy_file`. The copy loop fills queue with reads up to `QD`, submits, waits/peeks completions, retries `-EAGAIN`, adjusts short reads/writes by moving iov base/len and offset, turns completed reads into writes, frees data after write completion, then drains pending writes.

State and persistence: writes output file, uses heap allocation per chunk with payload after metadata. Global `infd/outfd` simplify callbacks.

Dependencies/integration: relies on regular or block-device input, `BLKGETSIZE64`, liburing, and POSIX file APIs.

Risks: pointer arithmetic on `void *` is GNU C extension. Error exits can leak queued buffers. Output file permissions fixed at 0644. Does not preserve metadata or sparse extents.

Test signals: output equality can be externally compared; internal errors print CQE failures or short submit failures.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-test.c -->
## sources/test-tools/liburing/examples/io_uring-test.c

Purpose: Minimal direct-I/O read demonstration for setting up a ring, submitting readv operations, consuming completions, and tearing down.

Important APIs/functions: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_prep_readv`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_cqe_seen`, `io_uring_queue_exit`.

Control flow: open file with `O_DIRECT`, stat size, allocate four 4096-byte aligned buffers, queue reads until queue or file exhausted, submit, wait for completions, validate full 4096-byte chunks except final file-sized remainder, print summary, free buffers and exit.

State and persistence: reads from input file only. Allocates and frees iovec buffers.

Dependencies/integration: depends on filesystem supporting `O_DIRECT`, aligned 4 KiB buffers, and liburing.

Risks: small or unaligned files/filesystems can produce direct-I/O errors. No handling for short non-final reads beyond failing. It does not check `calloc` return.

Test signals: successful summary output and zero exit; direct I/O failures expose environment limitations.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-udp.c -->
## sources/test-tools/liburing/examples/io_uring-udp.c

Purpose: UDP echo server using multishot `recvmsg`, provided buffer rings, fixed files, and sendmsg replies.

Important APIs/types/functions: `struct ctx`, `struct sendmsg_ctx`; `setup_buffer_pool`, `setup_context`, `setup_sock`, `add_recv`, `process_cqe_recv`, `process_cqe_send`, `process_cqe`; `io_uring_prep_recvmsg_multishot`, `io_uring_recvmsg_validate`, `io_uring_recvmsg_payload`, `io_uring_prep_sendmsg`, fixed file registration.

Control flow: parse IPv4/IPv6/port/buffer-size/verbose options, bind UDP socket, initialize ring with enlarged CQ, register buffer ring, register socket as fixed file, arm multishot recv, then submit-and-wait. Recv CQEs validate selected buffer and recvmsg metadata, optionally log peer, prepare a sendmsg back to source, and rearm if multishot ended. Send CQEs recycle buffers.

State and persistence: memory-mapped region stores both buffer ring descriptors and payload buffers. Socket is registered fixed file. No file persistence.

Dependencies/integration: kernel >= 6.0 for buffer rings/multishot recvmsg; liburing helpers for recvmsg parsing; UDP networking.

Risks: control length is zero, so ancillary data is ignored. Truncated names/payloads are dropped. Uses `cqe->flags >> 16` instead of named shift in one place. Infinite server loop lacks graceful shutdown cleanup except error path.

Test signals: binding log, verbose receive logs, echo behavior from UDP clients, build in examples.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/io_uring-udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/kdigest.c -->
## sources/test-tools/liburing/examples/kdigest.c

Purpose: Proof-of-concept file digest pipeline using Linux AF_ALG hash sockets and io_uring reads/sends, optionally with send bundle support.

Important APIs/types/functions: `enum req_state`, `struct req`, `struct kdigest`; `reap_completions`, `submit_sends_br`, `submit_sends_linked`, `digest_file`, `get_result`; AF_ALG `socket`, `bind`, `accept`; `io_uring_prep_read`, `io_uring_prep_send`, `io_uring_prep_send_bundle`, `io_uring_prep_recv`.

Control flow: main validates algorithm/input, opens file, creates and binds AF_ALG hash socket, accepts operation socket, allocates aligned buffers, initializes ring with preferred taskrun flags and fallback, conditionally sets up buffer ring if `IORING_FEAT_RECVSEND_BUNDLE` is present, copies file data through hash socket in ordered chunks, then receives and prints digest bytes.

State and persistence: reads input file, writes into kernel crypto operation socket, stores request state and buffers in memory, no files written.

Dependencies/integration: Linux crypto user API hash support, selected algorithm in `/proc/crypto`, liburing send bundle feature for optimized path, block-device size ioctl for block inputs.

Risks: comments acknowledge incomplete error handling. Ordering relies on either buffer-ring bundle serialization or linked sends. Many early returns skip fd/ring cleanup. Bundle support is feature-gated but still experimental.

Test signals: printed digest output; errors for missing AF_ALG or algorithm; compare digest to userspace hash tools.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/kdigest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/link-cp.c -->
## sources/test-tools/liburing/examples/link-cp.c

Purpose: Basic file copy proof-of-concept using linked read/write SQEs.

Important APIs/types/functions: `struct io_data`, global `infd/outfd/inflight`; `queue_rw_pair`, `handle_cqe`, `copy_file`; `IOSQE_IO_LINK`; `io_uring_prep_readv`, `io_uring_prep_writev`.

Control flow: main opens files and initializes ring. `copy_file` queues read/write pairs while `inflight < QD`, submits, then waits when queue pressure is high. Each pair stores one shared data object; read SQE is linked to write SQE. Completion handler increments pair completion count, retries canceled linked pairs on `-ECANCELED`, frees data after both CQEs complete, and decrements inflight.

State and persistence: writes output file; heap chunk per copy segment.

Dependencies/integration: liburing linked SQE semantics, regular/block input size discovery.

Risks: explicitly lacks short read handling. If read returns short but not error, linked write may write stale/extra bytes. Retry on canceled pairs can duplicate work if not carefully reasoned. Global `inflight` tracks SQEs, not logical chunks, which can be confusing.

Test signals: successful copy can be externally compared; runtime prints CQE errors.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/link-cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/napi-busy-poll-client.c -->
## sources/test-tools/liburing/examples/napi-busy-poll-client.c

Purpose: UDP ping client demonstrating io_uring NAPI busy-poll registration, optional SQPOLL/DEFER_TASKRUN/COOP_TASKRUN modes, and RTT measurement.

Important APIs/types/functions: `struct ctx`, `struct options`, `io_uring_napi`; `sendPing`, `receivePing`, `completion`, `recordRTT`, `printStats`, `reportNapi`; `io_uring_register_napi`, `io_uring_unregister_napi`, `io_uring_submit_and_wait_timeout`.

Control flow: parse address/port/ping count/busy options, connect UDP socket, configure ring flags, optionally register NAPI busy poll preferences, optionally use zero timeout pointer for busy looping, raise scheduler to SCHED_FIFO if permitted, send initial timestamp ping, then alternate send and receive completions until count is exhausted. First receive reports incoming NAPI id; later receives record RTT and queue next send.

State and persistence: uses socket connection state, in-memory RTT array, and ring registration state. No files.

Dependencies/integration: Linux NAPI socket options and liburing NAPI APIs, UDP peer server, optional realtime scheduler privilege.

Risks: uses `strcpy` into fixed-size option buffers without bounds checks. `-s` and `-d` parsing use `!!atoi(optarg)` even options are declared without obvious argument in usage. `optarg` is referenced in some error paths after `inet_pton`. RTT uses realtime clock, not monotonic.

Test signals: NAPI id print, RTT min/avg/max/mdev output, unregister verification of returned NAPI settings.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/napi-busy-poll-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/napi-busy-poll-server.c -->
## sources/test-tools/liburing/examples/napi-busy-poll-server.c

Purpose: UDP ping/pong server companion for the NAPI busy-poll client.

Important APIs/types/functions: `struct ctx`, global `opt`, `io_uring_napi`; `receivePing`, `sendPing`, `completion`, `reportNapi`; `io_uring_prep_recvmsg`, `io_uring_prep_sendmsg`, `io_uring_register_napi`.

Control flow: parse listen/address/port/count/NAPI options, bind UDP socket, initialize ring with taskrun mode, optionally register NAPI preferences, optionally set SCHED_FIFO, arm initial `recvmsg`, then loops on `io_uring_submit_and_wait_timeout`. Each recv stores peer address and received length then queues sendmsg echo; each send decrements remaining ping count and rearms receive.

State and persistence: socket bind state, current message/iovec buffers in `ctx`, NAPI registration. No persistent files.

Dependencies/integration: works with client example, liburing NAPI APIs, UDP IPv4/IPv6 sockets, optional realtime scheduling.

Risks: same fixed-buffer `strcpy` risk as client. `--listen` is parsed but mandatory server behavior does not require it. Some options declared as no-arg are parsed as needing optional data in code. Error handling often aborts.

Test signals: server logs listening address and NAPI id; paired client receives replies and reports RTT.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/napi-busy-poll-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/poll-bench.c -->
## sources/test-tools/liburing/examples/poll-bench.c

Purpose: Microbenchmark for io_uring poll operations on registered pipe file descriptors.

Important APIs/functions: `io_uring_queue_init`, `io_uring_register_files`, `io_uring_register_ring_fd`, `io_uring_prep_poll_add`, `io_uring_submit`, `io_uring_wait_cqe`.

Control flow: create pipe, initialize ring with `SINGLE_ISSUER` fallback, register pipe fds and ring fd, then for 10 seconds repeatedly queue 32 fixed-file poll requests for `POLLIN`, submit, write/read one byte through the pipe to satisfy polls, consume 32 CQEs, and count completions.

State and persistence: pipe buffers and ring registrations only. No files.

Dependencies/integration: liburing poll support, registered files, POSIX pipe.

Risks: returns on first submit mismatch; no cleanup on failures; benchmark can be distorted by pipe/read/write overhead and by arming multiple polls on same fd.

Test signals: stderr `requests/s` throughput line and zero exit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/poll-bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/proxy.c -->
## sources/test-tools/liburing/examples/proxy.c

Purpose: Advanced TCP sink/proxy example demonstrating multishot accept/receive, per-connection rings and threads, fixed files, provided receive and send buffer rings, send/receive bundles, zerocopy send, NAPI, SQPOLL/DEFER_TASKRUN/COOP_TASKRUN, bidirectional forwarding, statistics, and graceful shutdown.

Important APIs/types/functions: global option/state variables; `struct conn`, `conn_dir`, `conn_buf_ring`, `io_msg`, `msg_vec`; buffer setup `setup_recv_ring`, `setup_send_ring`, `setup_send_zc`, `setup_buffer_rings`; event encoding from `proxy.h`; handlers `handle_accept`, `handle_sock`, `handle_connect`, `handle_recv`, `handle_send`, `handle_cancel`, `handle_shutdown`, `handle_close`, `handle_fd_pass`, `handle_stop`; event loops `parent_loop`, `__event_loop`; initialization `init_ring`; thread entry `thread_main`.

Control flow: main parses options, validates incompatible modes, adjusts recvmsg multishot buffer size, creates listening socket, installs stats/signal hooks, initializes parent ring, arms multishot accept, and enters parent loop. Each accepted connection spawns a thread with its own ring and buffer rings. Fixed-file mode passes accepted fd via `io_uring_prep_msg_ring_fd`; non-fixed mode stores fd directly. Proxy mode opens/connects outbound socket, then arms one or two receives. Receive CQEs move selected buffers into outgoing queues or recycle in sink mode. Send CQEs recycle buffers back to receive ring and may rearm receives. Shutdown is coordinated through cancels, shutdown/close chains, and parent housekeeping.

State and persistence: long-lived global connection table, per-connection rings, pthreads, provided buffer rings, optional huge page mappings, stats buckets, open sockets, and counters. No file persistence.

Dependencies/integration: liburing latest networking APIs, `helpers.c` socket setup, pthreads, Linux TCP, optional kernel features for fixed files, NAPI, send buffer select, bundles, zerocopy, huge pages.

Risks: intentionally experimental with many interacting modes. Several feature macros are locally defined pending upstream headers. Per-connection thread model caps at `MAX_CONNS` and relies on shared globals with limited locking. Bidirectional mode has TODOs around bid sequencing checks. Error handling often terminates a connection or process. Buffer accounting invariants are enforced with asserts, which can abort under unexpected kernel behavior.

Test signals: manual proxy/sink traffic, bandwidth and per-connection stats, CQ overflow logs, CI build coverage. Good runtime signals are no asserts, stable buffer counts, matching in/out bytes, and clean close stats.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/proxy.h -->
## sources/test-tools/liburing/examples/proxy.h

Purpose: Shared helper header for `proxy.c` containing compact CQE/SQE user-data encoding and elapsed-time helpers.

Important APIs/types/functions: `struct userdata` union packs 4-bit op, 12-bit thread id, 16-bit buffer id, and 16-bit fd into a 64-bit value. `__encode_userdata`, `__raw_encode`, `cqe_to_op`, `cqe_to_bid`, `cqe_to_fd`, `mtime_since`, and `mtime_since_now`.

Control flow: inline pack/unpack functions are called when preparing SQEs and handling CQEs. Time helpers compute millisecond deltas with microsecond borrow handling.

State and persistence: none; pure encoding/time helpers.

Dependencies/integration: requires liburing types to be visible before inclusion. Used by proxy event dispatch and statistics.

Risks: fd and bid are truncated to 16 bits, op/tid share 16 bits with tid capped at 4095 even though proxy uses 1024. No endian issue inside a process, but bitfield layout in a union is compiler/ABI-sensitive; code is intended for local use, not serialization.

Test signals: proxy runtime dispatch correctness; bad user-data errors would reveal encoding mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/proxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/reg-wait.c -->
## sources/test-tools/liburing/examples/reg-wait.c

Purpose: Demonstrates registered wait arguments for `io_uring_submit_and_wait_reg`.

Important APIs/types/functions: `struct io_uring_reg_wait`, `struct io_uring_region_desc`, `struct io_uring_mem_region_reg`; `register_memory`; `io_uring_register_region`, `io_uring_enable_rings`, `io_uring_submit_and_wait_reg`.

Control flow: create pipe and ring disabled with `IORING_SETUP_R_DISABLED`, allocate page-aligned wait region, register it for wait args, enable rings, configure two wait entries. First wait expects `-ETIME` around one second with no completions. Then queue two pipe reads, satisfy one, and wait for two completions using min-wait usec; verifies submit count and approximate 10 ms wait behavior.

State and persistence: pipe fds, registered memory region, ring state. No files.

Dependencies/integration: new registered wait kernel/liburing support, page-aligned allocation helper, pipe I/O, wall-clock timing.

Risks: timing bounds are tight and may be noisy under load. Early returns leak pipe/ring/memory. Uses kernel feature detection via `-EINVAL`.

Test signals: timeout duration near expected ranges; successful registration; no unexpected wait return values.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/reg-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/rsrc-update-bench.c -->
## sources/test-tools/liburing/examples/rsrc-update-bench.c

Purpose: Microbenchmark for sparse registered-file-table updates via io_uring.

Important APIs/functions: `io_uring_queue_init` with `SINGLE_ISSUER|DEFER_TASKRUN`, `io_uring_register_ring_fd`, `io_uring_register_files_sparse`, `io_uring_register_files_update`, `io_uring_prep_files_update`, `io_uring_submit`, `io_uring_wait_cqe`.

Control flow: create pipe, initialize ring, register ring fd and sparse table, prepopulate table entries by updating each index, then for 10 seconds queue batches of 32 file update operations at pseudo-random offsets, submit, wait for all completions, and count operations.

State and persistence: registered file table and pipe descriptors; no files.

Dependencies/integration: liburing resource registration/update APIs and pipe fds.

Risks: does not inspect CQE result values for each update, only wait errors. Random offset uses unbounded `rand()` modulo table size. Benchmark measures kernel update throughput but not correctness beyond API survival.

Test signals: stderr `max updates/s` throughput; failures on registration or submit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/rsrc-update-bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/send-zerocopy.c -->
## sources/test-tools/liburing/examples/send-zerocopy.c

Purpose: Zerocopy send benchmark/test derived from Linux selftests. It can act as sender or receiver for TCP/UDP over IPv4/IPv6, supports fixed files, registered buffers, ring fd registration, huge pages, CPU affinity, multithreading, data verification, and defer-taskrun.

Important APIs/types/functions: `struct thread_data`; config globals; `setup_sockaddr`, `do_setup_rx`, `do_rx`, `do_tx`, `wait_cqe_fast`, `init_buffers`, `parse_opts`; `io_uring_prep_send_zc`, `IORING_RECVSEND_FIXED_BUF`, `IORING_CQE_F_NOTIF`, buffer/file/ring registration APIs.

Control flow: parse protocol/options and allocate patterned payload. Receiver mode binds/listens or binds UDP and flushes incoming data until timeout. Sender mode creates threads, connects sockets, initializes rings, registers files/ring/buffer, synchronizes via barrier, submits batches of send or send_zc SQEs until runtime/interrupt, consumes normal completions and zerocopy notification CQEs, then shuts down and prints aggregate throughput.

State and persistence: memory-mapped payload, socket connections, registered buffers/files, pthreads and barrier, counters. No file persistence.

Dependencies/integration: Linux networking, liburing zerocopy send support, optional huge pages, optional device binding, pthreads.

Risks: high-performance test with many privileged/environment-sensitive options. TCP batching can reorder data and disables verification. Signal handler uses `_exit` on second interrupt. Some error paths call fatal exit from worker threads. Receiver uses blocking `poll` and timeout assumptions.

Test signals: throughput line `packets=... rps=...`; verification failures detect payload mismatch; CQE notification accounting catches zerocopy completion semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/send-zerocopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/ucontext-cp.c -->
## sources/test-tools/liburing/examples/ucontext-cp.c

Purpose: Demonstrates coroutine-style asynchronous file copying using `ucontext` plus io_uring completions.

Important APIs/types/functions: `async_context`, `arguments_bundle`; generated `await_readv`/`await_writev` macros; `await_delay`; `setup_context`; `copy_file`; `copy_file_wrapper`; `swapcontext`, `makecontext`, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_prep_timeout`.

Control flow: main initializes a ring, creates one coroutine per input/output pair, starts each until it submits its first awaited operation, then enters an event loop. Await helpers prepare an SQE tagged with the coroutine context and swap back to main. Main waits for completions, retrieves context from CQE data, and resumes the coroutine. Completed coroutines update success/failure counters and main frees their stacks.

State and persistence: output files, per-coroutine heap stack, bundle, iovec buffer, and shared success/failure counters.

Dependencies/integration: `ucontext.h` availability detected by configure, liburing, POSIX files and timer operations.

Risks: `ucontext` is obsolete/nonportable and conditionally built. `makecontext` function-pointer cast is nonportable. Short writes fail rather than retry. The code mutates `piov->iov_len` after short reads and does not restore it to `BS` for the next loop, so subsequent reads may stay short.

Test signals: printed coroutine operation trace and final success/failure counts; output comparison can validate copies.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/ucontext-cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/examples/zcrx.c -->
## sources/test-tools/liburing/examples/zcrx.c

Purpose: Experimental zero-copy receive server for io_uring interface queues. It accepts TCP IPv6 connections and receives into registered zero-copy areas backed by normal memory, huge pages, or dmabuf.

Important APIs/types/functions: `struct zc_conn`; globals for queue/area config; `setup_zcrx`, `zcrx_populate_area`, `zcrx_populate_area_udmabuf`, `add_accept`, `add_recvzc`, `process_accept`, `process_recvzc`, `return_buffer`, `server_loop`; APIs `io_uring_register_ifq`, `IORING_OP_RECV_ZC`, `IORING_SETUP_CQE32`, `io_uring_zcrx_*` structures.

Control flow: parse interface, RX queue, sizes, area allocation mode, and affinity. Server creates IPv6 listener, initializes ring with CQE32 and enlarged CQ, registers zero-copy interface queue and refill ring/area, arms accept, and loops. Accepted connections allocate `zc_conn`, optionally set CPU affinity based on incoming CPU, arm multishot recvzc. Receive CQEs verify data if requested, update byte count, and return buffers through refill ring; final CQE handles completion or ENOSPC requeue.

State and persistence: listening and accepted sockets, registered interface queue, refill ring mapping, registered receive area, optional dmabuf/memfd fds, per-connection counters. No file output.

Dependencies/integration: very recent liburing/kernel zcrx APIs, network interface queue id, `/dev/udmabuf` for dmabuf mode, memfd, huge pages optionally, IPv6 TCP.

Risks: experimental kernel interface and direct CQE32 layout assumptions. `process_accept` sets `stop = false` on accept failure, likely preventing termination rather than stopping. Refill queue full drops buffers. Requires careful privileges and NIC queue setup. Cleanup is incomplete for mappings/fds on exit.

Test signals: accepted socket logs, connection termination byte/CQE/requeue stats, optional payload verification, fatal errors on setup mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/examples/zcrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/liburing-ffi.pc.in -->
## sources/test-tools/liburing/liburing-ffi.pc.in

Purpose: pkg-config template for the liburing FFI shared/static development package.

Important fields: `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Version`, `Description`, `URL`, `Libs: -L${libdir} -luring-ffi`, and `Cflags: -I${includedir}`.

Control flow: top-level Makefile transforms placeholders `@prefix@`, `@libdir@`, `@includedir@`, `@NAME@`, and `@VERSION@` via `sed` into `liburing-ffi.pc`.

State and persistence: template is static; generated `.pc` is installed to pkgconfig dir.

Dependencies/integration: consumed by pkg-config users linking `liburing-ffi`. Version/name come from Makefile/config metadata.

Risks: does not express dependency on base `liburing` even though FFI library build includes liburing objects; this may be intentional. No `Requires` or `Libs.private`.

Test signals: generated pc file during `make install`; downstream `pkg-config --libs --cflags`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/liburing-ffi.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/liburing.pc.in -->
## sources/test-tools/liburing/liburing.pc.in

Purpose: pkg-config template for the main liburing library.

Important fields: standard install variables, package metadata, `Libs: -L${libdir} -luring`, and `Cflags: -I${includedir}`.

Control flow: generated by top-level Makefile from configure/Makefile values and installed with `make install`.

State and persistence: template only; output `.pc` file is generated and installed.

Dependencies/integration: downstream build systems use it to find liburing headers and linker flags.

Risks: no `Libs.private` for static support; if future liburing gains external dependencies, template must be updated. Paths depend on correct configure prefix/libdir.

Test signals: install smoke tests can be extended with pkg-config; current CI indirectly validates installed headers/libs but not this file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/liburing.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/make-debs.sh -->
## sources/test-tools/liburing/make-debs.sh

Purpose: Helper script to create Debian source/build artifacts for a liburing release from the current git tree.

Important commands/flow: accepts optional base dir, computes release dir from `lsb_release`, finds own source dir, derives version from `git describe --match "lib*" | cut -d '-' -f 2`, copies the repo, runs `git clean -dxf`, updates Debian changelog with `dch` if needed, creates tarball and `.orig.tar.gz` symlink, then runs `debuild`.

State and persistence: destructively recreates `$base/<distro>/liburing`, copies source tree, edits copied `debian/changelog`, writes tarballs/symlink, and builds Debian artifacts.

Dependencies/integration: `bash`, git tags, `lsb_release`, `head`, `dch`, `debuild`, Debian packaging metadata.

Risks: `set -xe` exposes commands and aborts on failure. Version parsing assumes tag format matching `lib*` with hyphen-separated output. `readlink -e \`basename $0\`` depends on current working directory containing the script basename. `rm -rf $releasedir` is broad if variables are wrong, though base defaults to `/tmp/release`.

Test signals: successful debuild and generated tar/orig files; changelog version updated to `$version-1`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/make-debs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/Makefile -->
## sources/test-tools/liburing/src/Makefile

Purpose: Builds and installs liburing static/shared libraries plus FFI variants.

Important targets/variables: `liburing_srcs`, `liburing_objs`, `liburing_sobjs`, `liburing_ffi_objs`; targets `liburing.a`, `liburing-ffi.a`, shared `$(libname)`, `$(ffi_libname)`, `install`, `uninstall`, `clean`; config flags for `CONFIG_NOLIBC`, `CONFIG_USE_SANITIZER`, `CONFIG_USE_TSAN`.

Control flow: include common/config files, set CPPFLAGS/CFLAGS, build normal and PIC objects, archive static libraries, link shared libraries with version scripts and sonames, install public headers/static/shared libs/symlinks, and remove them on uninstall. Config toggles add `nolibc.c`, sanitizer support, or TSAN flags.

State and persistence: creates objects, dependency files, archives, shared libraries, generated installed files and symlinks. Clean removes local artifacts and generated compat/version headers.

Dependencies/integration: relies on `configure` outputs, `Makefile.common`, `Makefile.quiet`, version maps, liburing source files, compiler/linker/archive tools.

Risks: nolibc uses freestanding/no-default-libs flags and libgcc path, so architecture config must be correct. Shared link uses `-z defs` unless sanitizer, catching unresolved symbols. Install path symlink logic depends on `relativelibdir`.

Test signals: CI multi-arch build/install and test_build linkage; static/shared artifacts existence.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/aarch64/lib.h -->
## sources/test-tools/liburing/src/arch/aarch64/lib.h

Purpose: AArch64 page-size helper for liburing, including nolibc support.

Important APIs/functions: `__get_page_size` and cached `get_page_size`.

Control flow: with libc, call `sysconf(_SC_PAGESIZE)` and fallback to 4096. With nolibc, open `/proc/self/auxv`, read pairs of `Elf64_Off`, look for `AT_PAGESZ`, close fd, fallback to 4096. `get_page_size` caches first result in a static variable.

State and persistence: process-local static cache; reads procfs in nolibc mode.

Dependencies/integration: included by architecture-specific liburing internals; nolibc path depends on `__sys_open`, `__sys_read`, and `__sys_close`.

Risks: cache is unsynchronized but benign. Nolibc auxv parser assumes pair size and readable procfs. Fallback 4096 may be wrong on unusual systems if auxv/procfs unavailable.

Test signals: architecture CI build and runtime mapping behavior using page size.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/aarch64/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/aarch64/syscall.h -->
## sources/test-tools/liburing/src/arch/aarch64/syscall.h

Purpose: AArch64 raw syscall macro layer for nolibc/liburing internals, falling back to generic libc wrappers when not compiling for AArch64.

Important APIs/macros: `__do_syscall0` through `__do_syscall6`, using registers `x8` for syscall number and `x0`-`x5` for args, issuing `svc 0`; includes `../syscall-defs.h`.

Control flow: preprocessor selects native macros under `__aarch64__`, otherwise includes generic syscall implementation. Syscall wrappers in `syscall-defs.h` build on these macros.

State and persistence: none.

Dependencies/integration: depends on Linux AArch64 syscall ABI, syscall numbers, and compiler support for register variables/inline asm.

Risks: raw syscalls return negative errno values directly and callers must interpret consistently. Inline asm constraints must remain ABI-correct across compilers. Non-AArch64 cross include silently uses generic wrappers.

Test signals: aarch64 CI compilation and nolibc runtime tests where available.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/aarch64/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/generic/lib.h -->
## sources/test-tools/liburing/src/arch/generic/lib.h

Purpose: Generic libc-backed page-size helper.

Important APIs/functions: `get_page_size` calling `sysconf(_SC_PAGESIZE)` with 4096 fallback.

Control flow: simple call and fallback each invocation; no caching.

State and persistence: none.

Dependencies/integration: used on architectures/configurations without custom page-size helper; requires libc `sysconf`.

Risks: no cache means repeated sysconf calls, usually negligible. Fallback may be wrong on non-4K page systems if sysconf fails.

Test signals: generic architecture build/runtime behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/generic/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/generic/syscall.h -->
## sources/test-tools/liburing/src/arch/generic/syscall.h

Purpose: Libc-backed syscall wrapper layer for platforms without raw nolibc asm.

Important APIs/functions: `__sys_io_uring_register`, `__sys_io_uring_setup`, `__sys_io_uring_enter2`, `__sys_io_uring_enter`, `__sys_open`, `__sys_read`, `__sys_mmap`, `__sys_munmap`, `__sys_madvise`, `__sys_getrlimit`, `__sys_setrlimit`, `__sys_close`.

Control flow: each wrapper calls libc syscall or direct libc function and normalizes failures to `-errno`; mmap maps `MAP_FAILED` to `ERR_PTR(-errno)`.

State and persistence: invokes kernel syscalls; no internal state.

Dependencies/integration: used by liburing internals where libc is available. Requires syscall numbers for io_uring and standard POSIX headers.

Risks: `__sys_io_uring_enter` hardcodes `_NSIG / 8` signal mask size. Mixed direct libc and `syscall()` wrappers must preserve liburing's negative-error convention.

Test signals: non-nolibc builds across CI; runtime io_uring setup/enter/register behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/generic/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/riscv64/lib.h -->
## sources/test-tools/liburing/src/arch/riscv64/lib.h

Purpose: RISC-V 64 page-size helper with libc and nolibc paths.

Important APIs/functions: `__get_page_size` and cached `get_page_size`, equivalent in behavior to the AArch64 helper.

Control flow: libc mode uses `sysconf`; nolibc mode reads `/proc/self/auxv` looking for `AT_PAGESZ`; public helper caches result.

State and persistence: static page-size cache; procfs read in nolibc.

Dependencies/integration: included by RISC-V liburing internals; depends on raw syscall wrappers for nolibc.

Risks: includes `<sys/auxv.h>` even though nolibc path manually reads auxv; availability depends on headers. Fallback to 4096 may be wrong on systems with different page size.

Test signals: riscv64 CI compile and any nolibc runtime mapping tests.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/riscv64/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/riscv64/syscall.h -->
## sources/test-tools/liburing/src/arch/riscv64/syscall.h

Purpose: RISC-V 64 raw syscall macro layer for liburing nolibc operation.

Important APIs/macros: `__do_syscall0` through `__do_syscall6`; syscall number in `a7`, arguments in `a0`-`a5`, `ecall` instruction; includes `../syscall-defs.h` for typed wrappers.

Control flow: native raw asm selected when `__riscv && __riscv_xlen == 64`, otherwise generic libc syscall wrappers are used.

State and persistence: none.

Dependencies/integration: Linux RISC-V syscall ABI and compiler register variable support.

Risks: clobber lists differ for one-argument vs multi-argument macros to account for return registers; mistakes would corrupt syscall arguments/results. Raw negative errors must be handled by callers.

Test signals: riscv64 CI compilation and nolibc runtime where available.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/riscv64/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/syscall-defs.h -->
## sources/test-tools/liburing/src/arch/syscall-defs.h

Purpose: Architecture-independent typed wrappers built on raw `__do_syscallN` macros.

Important APIs/functions: `__sys_open`, `__sys_read`, `__sys_mmap`, `__sys_munmap`, `__sys_madvise`, `__sys_getrlimit`, `__sys_setrlimit`, `__sys_close`, `__sys_io_uring_register`, `__sys_io_uring_setup`, `__sys_io_uring_enter2`, `__sys_io_uring_enter`.

Control flow: `__sys_open` uses `open` or `openat` depending on syscall availability; `__sys_mmap` uses `mmap2` with page-shifted offset when present; rlimit wrappers use `prlimit64`; io_uring wrappers call the corresponding syscalls; `__sys_io_uring_enter` supplies `_NSIG/8` mask size.

State and persistence: performs direct kernel syscalls, returning raw integer/pointer results.

Dependencies/integration: included by architecture raw syscall headers; consumed by nolibc liburing code and page-size helpers.

Risks: unlike generic libc wrappers, raw syscall return values are not converted through `errno`; callers must expect negative kernel errno. Mmap returns a cast pointer without `ERR_PTR` normalization. `_NSIG` assumptions must match kernel ABI.

Test signals: nolibc builds and io_uring setup/register/enter functionality on supported architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/syscall-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/x86/lib.h -->
## sources/test-tools/liburing/src/arch/x86/lib.h

Purpose: x86 page-size helper.

Important APIs/functions: `get_page_size` returns constant 4096.

Control flow: no detection; always returns 4 KiB.

State and persistence: none.

Dependencies/integration: used by x86 liburing internals where 4 KiB page size is assumed for supported x86 Linux targets.

Risks: unsuitable for hypothetical x86 configurations with non-4K base pages. The simplicity avoids libc/procfs dependencies for nolibc.

Test signals: x86 and x86_64 CI builds and runtime memory mapping behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/x86/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/arch/x86/syscall.h -->
## sources/test-tools/liburing/src/arch/x86/syscall.h

Purpose: x86 raw syscall macro layer for x86_64 and i386 nolibc builds, with generic fallback when raw i386 is not enabled.

Important APIs/macros: x86_64 `__do_syscall0` through `__do_syscall6` using `syscall`, `rax/rdi/rsi/rdx/r10/r8/r9`; i386 nolibc variants using `int $0x80`, `eax/ebx/ecx/edx/esi/edi/ebp`; special six-argument i386 stack workaround for `%ebp`; includes `../syscall-defs.h`.

Control flow: preprocessor selects x86_64 raw syscalls, else i386 raw syscalls only under `CONFIG_NOLIBC`, else generic libc wrappers.

State and persistence: none.

Dependencies/integration: Linux x86 syscall ABIs, compiler inline asm constraints, and nolibc liburing internals.

Risks: i386 six-argument syscall workaround is delicate and documents a GCC bug avoidance. Raw asm clobber lists must remain correct. Return values are raw kernel negatives, not `errno`-translated.

Test signals: x86_64 and i686 CI compilation; nolibc runtime tests on supported x86 paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/arch/x86/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/ffi.c -->
## sources/test-tools/liburing/src/ffi.c

Purpose: Translation unit for producing an FFI-friendly liburing library variant by forcing non-inline definitions from liburing headers.

Important APIs/macros: defines `IOURINGINLINE` before including `liburing.h`; wraps Clang diagnostic suppression for `-Wmissing-prototypes`.

Control flow: compile-time only. Including `liburing.h` with `IOURINGINLINE` altered causes header functions intended for inline use to be emitted into the FFI object/library.

State and persistence: no runtime state. Produces `ffi.ol`/`ffi.os` objects and `liburing-ffi` archives/shared libraries via `src/Makefile`.

Dependencies/integration: depends on header implementation patterns in `liburing.h`, Clang/GCC warning behavior, and version map `liburing-ffi.map`.

Risks: tightly coupled to header inline semantics; changes in `liburing.h` can alter exported FFI surface. Clang warning suppression is local but masks missing prototypes in this inclusion.

Test signals: successful FFI library build/link; downstream FFI consumers linking `-luring-ffi`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/ffi.c -->

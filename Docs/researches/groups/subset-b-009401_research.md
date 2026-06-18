# subset-b-009401 research

Grouped research for the syzkaller executor and `pkg/aflow` files in work item `subset-b-009401`. Each section is source-tree-aligned and bounded for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb_netbsd.h -->
# sources/test-tools/syzkaller/executor/common_usb_netbsd.h

Purpose: NetBSD-specific implementation of syzkaller USB pseudo-syscalls. It adapts the Linux-oriented `common_usb.h` descriptor model to NetBSD VHCI device APIs so generated programs can attach and enumerate virtual USB devices.

Important APIs and types: the file redefines packed Linux-style USB descriptor structs and request constants, then exposes `vhci_open`, `vhci_setport`, `vhci_usb_attach`, `vhci_usb_recv`, `vhci_usb_send`, `syz_usb_connect_impl`, `syz_usb_connect`, and `syz_usb_disconnect`. `syz_usb_connect_impl` is the main control-flow hub: it builds a USB descriptor index with `add_usb_index`, selects port 1, attaches the device, receives VHCI control requests, resolves IN/OUT responses through `lookup_connect_response_in` or the supplied OUT resolver, and sends or receives endpoint-zero payloads until configuration completes.

State and dependencies: state is held in the VHCI file descriptor, the global `procid` path `/dev/vhci%llu`, and descriptor indexes owned by `common_usb.h`. The code depends on NetBSD headers, `ioctl` command contracts, `debug`, `debug_dump_data`, and `sleep_ms`.

Integration points: compiled when the executor or csource needs `syz_usb_connect`/`disconnect`; NetBSD coverage can attach remote VHCI coverage in `executor_bsd.h`.

Risks and tests: short reads/writes are looped, but `vhci_usb_recv` treats EOF as a zero-length progress bug that can spin if `read` returns 0 before completion. Control request behavior is strict and returns `-1` for unknown requests, making descriptor lookup correctness critical. Test coverage is indirect through USB feature setup and executor runtime; no dedicated NetBSD unit test appears in this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_usb_netbsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_windows.h -->
# sources/test-tools/syzkaller/executor/common_windows.h

Purpose: Windows implementation of executor/csource common primitives for exception-safe memory access, timing, threading, events, sandbox-none execution, and temporary directories.

Important APIs and control flow: `install_segv_handler` is a no-op because Windows structured exception handling is used directly. `NONFAILING` wraps arbitrary statements in `__try/__except` and returns false on access faults. `current_time_ms` and `sleep_ms` map to `GetTickCount64` and `Sleep`. `thread_start` creates a 128 KiB-stack Windows thread. `event_t` combines `CRITICAL_SECTION`, `CONDITION_VARIABLE`, and integer state; `event_set` rejects double-set events, `event_wait` blocks until state is set, and `event_timedwait` waits until timeout. `do_sandbox_none` calls the external `loop`. `use_temporary_dir` creates and enters a `./syzkaller.XXXXXX` temp directory using `mktemp`, `CreateDirectory`, and `_chdir`.

State and dependencies: event state is process-local and manually synchronized. The header depends on `windows.h`, `io.h`, `_chdir`, and executor helpers `exitf`.

Integration points: included through Windows common/executor builds and shared with generated C reproducers under feature macros.

Risks and tests: `event_reset` writes `state` without taking the critical section, so callers must preserve the executor's event ordering assumptions. `mktemp` is weaker than atomic temp creation. Coverage is not implemented here; Windows executor-specific syscall execution and read/write shims are in `executor_windows.h`. Test signals are mostly compile/build coverage for the Windows target.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_windows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_zlib.h -->
# sources/test-tools/syzkaller/executor/common_zlib.h

Purpose: Small in-tree deflate/zlib inflater used by executor/csource code to expand compressed blobs into files without linking an external zlib.

Important APIs and control flow: the puff-derived implementation centers on `puff_state`, `puff_bits`, `puff_stored`, `puff_huffman`, `puff_decode`, `puff_construct`, `puff_codes`, `puff_fixed`, `puff_dynamic`, and `puff`. `puff` reads final-block/type bits, dispatches stored/fixed/dynamic blocks, and returns positive errors for short input/output, zero for success, and negative errors for malformed streams. `puff_zlib_to_file` skips the two-byte zlib header, mmaps a 132 MiB destination buffer, inflates into it, writes it to `dest_fd`, and unmaps it.

State and dependencies: most temporary tables are stack allocations; fixed Huffman tables are static and lazily initialized by `puff_fixed`, which is not explicitly thread-safe. `setjmp`/`longjmp` handles input exhaustion from bit readers. The wrapper depends on `mmap`, `munmap`, `write`, and `errno`.

Integration points: used by syzkaller pseudo-syscalls that materialize compressed images/files. The 132 MiB maximum is shared with `pkg/image/compression.go`.

Risks and tests: this altered puff variant only writes nonzero literal/copy bytes, preserving sparse zero-filled output from the mmap. That is intentional for sparse payloads but would be surprising for a general inflater. Static initialization races are possible if multiple executor threads first enter fixed-code inflation concurrently. Error translation uses `errno = -err`, which creates synthetic errno values for deflate errors. Test coverage is primarily through generated image/file execution paths rather than local unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_zlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/conn.h -->
# sources/test-tools/syzkaller/executor/conn.h

Purpose: RPC and readiness primitives for the executor runner process.

Important APIs and control flow: `Connection` connects to a manager address/port or uses `stdin`, sends and receives size-prefixed flatbuffers, and retries partial `read`/`write` operations across `EINTR`/`EAGAIN`. `Connect` handles localhost IPv4/IPv6 fallback, numeric addresses, DNS via `gethostbyname`, and blocking connect interruption through `ConnectWait`. `Select` wraps `pselect`: `Arm` adds fds, `Wait` blocks with millisecond timeout, `Ready` tests readiness, and `Prepare` sets nonblocking mode.

State and dependencies: `Connection` owns an fd, a receive buffer, and a reusable `FlatBufferBuilder`. It assumes little-endian size prefixes via `le32toh`. `Select` owns a single fd set and max fd and is intended per-loop, not reusable after `Wait` without rearming.

Integration points: `executor_runner.h` uses `Connection` for host-manager messages and `Select` for multiplexing the manager socket plus subprocess response/stdout pipes.

Risks and tests: `Connection::Recv` trusts the remote size prefix and resizes memory accordingly, so manager/executor protocol trust is required. `stdin` mode returns fd 0 while `Send` writes back to the same fd, so it relies on an external bidirectional setup. Test signals are indirect through runner integration; this file is exempted from some fuzzer-only style checks in `style_test.go`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/cover_filter.h -->
# sources/test-tools/syzkaller/executor/cover_filter.h

Purpose: Shared-memory PC membership filter used to suppress already-known signal and restrict coverage to interesting code regions.

Important APIs and control flow: `CoverFilter()` allocates a new `ShmemFile`; `CoverFilter(fd, preferred)` maps an existing filter, usually in an executor child. `Insert` calls `FindByte(pc, true)` and sets a bit. `Contains` calls `FindByte(pc, false)`. `Seal` makes the shared mapping read-only and closes its fd. The table supports up to four 1 GiB regions, L1 entries per 1 MiB chunk, and L2 16 KiB bitmaps that drop the low three PC bits.

State and dependencies: the serialized `Table` lives entirely in shared memory, while `alloc_` is process-local allocation state for new L2 blocks. Filters passed to children are sealed or treated read-only, so only the creator should insert after construction. Depends on `ShmemFile`, `failmsg`, and executor integer typedefs.

Integration points: runner builds `max_signal_` and `cover_filter_`, passes their fds to child executors, and executor-side `coverage_filter` queries them while writing signal/coverage/comparisons.

Risks and tests: false positives are intentional from 8-byte granularity. Overflow is fatal when more than four regions or the bitmap budget is exceeded. `test_cover_filter` validates parent/child shared visibility, region boundaries, low-bit coalescing, and negative cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/cover_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/embed.go -->
# sources/test-tools/syzkaller/executor/embed.go

Purpose: Builds a single embedded common-header blob for `pkg/csource` so generated C reproducers can include executor support code without a source-tree include graph.

Important APIs and control flow: `src` embeds `common*.h`, `kvm*.h`, and `android/*.h`. `CommonHeader` reads `common.h`, discovers all other embedded headers except `common.h` and `common_ext_example.h`, then repeatedly replaces `#include "name.h"` and `#include "android/name.h"` with embedded contents until no more replacements occur. It panics if any embedded header was unused. Finally it removes ordinary `//` comments while preserving `//%` license/comment lines used by imported code.

State and dependencies: package-level initialization computes `CommonHeader` once. It uses `embed.FS`, `fs.Glob`, `maps.Clone`, `bytes.ReplaceAll`, `path.Base`, and regex cleanup.

Integration points: csource generation consumes `executor.CommonHeader`; `style_test.go` enforces source patterns that make this textual include/comment stripping safe.

Risks and tests: include replacement is basename-based, so duplicate basenames across directories would be ambiguous except for the special android path check. The variable name `relacedSomething` is misspelled but harmless. Comment stripping is regex-based and can break unusual string/comment patterns; style rules reduce that risk.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/embed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor.cc -->
# sources/test-tools/syzkaller/executor/executor.cc

Purpose: Main syzkaller executor binary. It implements command dispatch (`runner`, `exec`, `leak`, `test`), the child execution protocol, program decoding, syscall scheduling, coverage/comparison collection, and flatbuffer result construction.

Important APIs and control flow: `main` initializes OS state, maps input/output, sets control pipes, negotiates `handshake_req`, receives `execute_req`, opens coverage buffers, then enters the selected sandbox. `execute_one` decodes the varint program stream: copyin commands materialize constants, addresses, result references, data, and checksums; syscall commands are scheduled through `schedule_call`; copyouts are harvested in `copyout_call_results`. Threaded execution uses `thread_t` events, `worker_thread`, and per-call timeouts. Results are serialized through `write_output`, `write_call_output`, `write_extra_output`, and `finish_output`. `ShmemAllocator` and `ShmemBuilder` allow flatbuffers to be assembled directly inside shared memory.

State and persistence: global flags mirror RPC execution/environment options; `threads`, `results`, `extra_cov`, dedup tables, `output_data`, and optional `CoverFilter`s are reused across requests. With fork server enabled, output mappings are resized per request; snapshot mode reuses fixed ivshmem mappings.

Dependencies and integration: includes generated `syscalls.h`, `common.h`, OS-specific `executor_*.h`, `shmem.h`, `conn.h`, `files.h`, `snapshot.h`, `executor_runner.h`, and tests. It depends on flatrpc schemas and platform KCOV/KSANCOV/no-cover APIs.

Risks and tests: correctness hinges on shared-memory bounds, memory-ordering stores to `OutputData`, varint bounds checks, and matching constants with Go packages. Known risk areas include coverage buffer overflow/truncation, unfinished syscalls, thread-state races, and executor output corruption by fuzzed programs. `run_tests` covers checksum/copyin/filter/glob/KVM helpers; broader validation comes from syzkaller executor integration tests and machine checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_bsd.h -->
# sources/test-tools/syzkaller/executor/executor_bsd.h

Purpose: FreeBSD, NetBSD, and OpenBSD executor adapter for data mapping, syscall dispatch, and KCOV-style coverage.

Important APIs and control flow: `os_init` maps the executor data region with platform-specific W^X handling, raises `RLIMIT_NOFILE`, and installs a SIGCHLD handler. `execute_syscall` calls pseudo-syscalls directly or platform syscall entry points. `cover_open`, `cover_mmap`, `cover_protect`, `cover_unprotect`, `cover_enable`, `cover_reset`, and `cover_collect` adapt FreeBSD `/dev/kcov`, OpenBSD kcov ioctls, and NetBSD remote VHCI coverage. NetBSD declares `features` for USB emulation and fault injection plus no-op setup hooks.

State and dependencies: `cover_t` stores fd, mmap address, data size, offsets, and overflow state shared with `executor.cc`. The implementation depends on BSD kcov headers/ioctls, `MAP_FIXED_EXCLUSIVE`, and platform feature macros.

Integration points: included by `executor.cc` for `GOOS_freebsd`, `GOOS_netbsd`, and `GOOS_openbsd`; NetBSD USB integrates with `common_usb_netbsd.h`.

Risks and tests: OpenBSD does not support raw syscall fallback for missing call wrappers and fails instead. Protection is implemented only for FreeBSD/OpenBSD and not NetBSD. NetBSD extra coverage uses fixed VHCI remote IDs. Test signals are mostly cross-target executor builds plus runtime coverage/machine checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_bsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_common.h -->
# sources/test-tools/syzkaller/executor/executor_common.h

Purpose: Tiny executor utility header currently providing command-line option extraction shared by executor code and tests.

Important API and control flow: `get_last_opt(cmdline, key, out, out_len)` constructs `key=`, scans all occurrences in the command line, accepts only matches at the beginning or after whitespace, remembers the last valid value, then copies it into `out` truncated to `out_len - 1`.

State and dependencies: stateless helper depending on `snprintf`, `strstr`, `strlen`, `strcspn`, and `memcpy`. It does not clear `out` when no match is found, so callers should initialize defaults first.

Integration points: Linux kdump setup in `executor_linux.h` uses it to preserve `root` and `console` options when constructing a crash-kernel command line. `test.h` includes focused tests for whitespace, multiple occurrences, non-matches, and truncation.

Risks and tests: `key_eq` is limited to 128 bytes, so extremely long keys are truncated. The parser is intentionally simple and does not handle quoting. `test_get_last_opt` is the direct regression signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_darwin.h -->
# sources/test-tools/syzkaller/executor/executor_darwin.h

Purpose: Darwin/XNU executor adapter with KSANCOV coverage support.

Important APIs and control flow: `os_init` maps the data segment and forces `is_kernel_64_bit = false` because KSANCOV returns 32-bit PCs plus an offset. `execute_syscall` invokes pseudo-syscalls or `__syscall`. `cover_open` opens KSANCOV, configures trace mode before mapping, and computes max entries from `kCoverSize`. `cover_mmap` maps the KSANCOV trace region and records data bounds. `cover_enable` attaches coverage to the current thread and rejects comparison or extra coverage. `cover_reset` restarts tracing, and `cover_collect` updates size, PC array offset, and kernel offset.

State and dependencies: depends on XNU `ksancov.h` APIs and assumes trace-PC mode only. `cover_t::pc_offset` reconstructs full PCs from truncated trace entries.

Integration points: included for `GOOS_darwin` by `executor.cc`; result serialization remains the common executor path.

Risks and tests: comments note required C++ fixes in upstream XNU headers. Unsupported TRACE_CMP and extra coverage fail hard. Coverage size assumptions are checked at mmap time. Test signals are target build/runtime coverage rather than local unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_darwin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_fuchsia.h -->
# sources/test-tools/syzkaller/executor/executor_fuchsia.h

Purpose: Fuchsia executor adapter for Zircon/libc syscall execution without coverage support.

Important APIs and control flow: `os_init` maps the executor data segment through `syz_mmap`. `execute_syscall` invokes the generated call wrapper and converts Zircon status conventions for `zx_` calls into libc-style executor results: success returns 0, errors set `errno` to `(-res) & 0x7f` and return `-1`, while selected time/debug calls are treated as arbitrary-return helpers. Non-Zircon libc functions normalize 32-bit `-1` to pointer-width `-1`.

State and dependencies: includes `nocover.h`, so all coverage functions are no-ops. Depends on Zircon status/syscall headers, `strncmp`, and generated syscall wrappers.

Integration points: included by `executor.cc` for `GOOS_fuchsia`; shares common program decoding and output code.

Risks and tests: the errno mapping intentionally truncates Zircon statuses into a small range, which is enough for executor semantics but not a faithful status report. Because coverage is disabled, signal/coverage collection paths are unavailable on this target. Test signals are mainly target builds and executor machine checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_fuchsia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_linux.h -->
# sources/test-tools/syzkaller/executor/executor_linux.h

Purpose: Linux executor adapter for memory layout, syscall dispatch, KCOV/remote coverage, pkey protection, process exit, and feature probing.

Important APIs and control flow: `os_init` sets parent-death signal, maps guard/data pages, installs SIGCHLD handling, and probes reserved pkey availability. `execute_syscall` calls pseudo-syscalls or raw `syscall`. KCOV flow is `cover_open` -> `cover_mmap` -> `cover_enable` -> `cover_reset`/`cover_collect` -> optional `cover_close`; it supports 32/64-bit traces, comparison mode, delayed mmap, remote common/USB handles, read-only reset ioctl, and guard pages. `doexit` and `doexit_thread` use raw exit syscalls and then spin to survive blocked exits. Feature probes include KCSAN filtering, NIC VF/devlink PCI presence, delayed KCOV mmap, KCOV reset ioctl, kdump setup, fault/leak/USB/LRWPAN/binfmt/swap hooks.

State and dependencies: global `pkeys_enabled` affects coverage write protection. `cover_t` carries fd, mmap allocation, data pointers, offsets, and enabled state. The feature table maps `rpc::Feature` values to setup functions.

Integration points: included by `executor.cc` for Linux, consumed by runner handshake feature negotiation, snapshot pkey setup, and tests.

Risks and tests: KCOV ioctl behavior varies by kernel; setup functions return user-readable reasons for unsupported features. `setup_delay_kcov` deliberately tests for missing mappings via `clock_gettime` EFAULT. Kdump setup shells out to `kexec` and parses `/proc/cmdline`. Tests include Linux KVM/SYZOS helpers plus syzkaller machine checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_runner.h -->
# sources/test-tools/syzkaller/executor/executor_runner.h

Purpose: Long-lived manager-facing runner that multiplexes many child `syz-executor exec` subprocesses, performs host handshake, forwards requests, restarts unhealthy children, and returns flatbuffer results.

Important APIs and control flow: `ProcIDPool` allocates and recycles unique proc IDs. `Proc` owns one child process, request/response shared memory, pipes, current request, output buffer, and state machine (`Started`, `Handshaking`, `Idle`, `Executing`). `Proc::Execute` chooses restart conditions, sends `handshake_req` or `execute_req`, copies program data to shared memory, and reports `ExecutingMessage`. `Ready`, `ReadOutput`, `ReadResponse`, `Restart`, and `HandleCompletion` manage timeouts, stdout capture, failed/hanged requests, proc-id replacement, and `finish_output`. `Runner` receives manager messages, tracks request queue, builds feature info, handles signal updates/state requests/corpus triaged notifications, and runs optional leak checks. `runner` installs signal handlers, connects to the manager, pads fd numbers, and starts `Runner`.

State and dependencies: runner state persists across requests: proc freshness, queued requests, coverage filters, feature setup results, leak frames, and corpus triage status. Depends on `Connection`, `Subprocess`, `ShmemFile`, `CoverFilter`, flatrpc, and OS feature functions.

Integration points: selected by `main argv[1] == "runner"`; manager protocol implementation must match Go RPC server cookie hashing and message schemas.

Risks and tests: restart/hang behavior is subtle because killed top processes may leave descendant test processes alive. Shared-memory bounds rely on `kMaxInput`/`kMaxOutput` matching executor constants. Repeated failures escalate to `SYZFAIL`. Test signals are integration-heavy; `StateRequest` offers live diagnostic output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_runner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_test.h -->
# sources/test-tools/syzkaller/executor/executor_test.h

Purpose: Test-OS executor adapter used by syzkaller unit/integration tests to simulate coverage and syscall execution in userspace.

Important APIs and control flow: `os_init` sets parent-death signal on Linux, maps the data region, and derives kernel bitness from host word size. `__sanitizer_cov_trace_pc` records instrumented PCs into the current thread coverage buffer after converting return addresses into synthetic kernel-text PCs. `execute_syscall` injects a coverage PC and invokes the generated call wrapper. Coverage APIs allocate anonymous buffers, reset counts, collect sizes, and support comparison-mode bookkeeping without real KCOV. `inject_cover`, `syz_inject_cover`, and `syz_inject_remote_cover` copy caller-provided coverage data into local or extra coverage buffers. Feature setup reports fault support and leak unsupported.

State and dependencies: synthetic `kernel_text_start` and `kernel_text_mask` must align with `sys/targets` expectations. Coverage buffers live in executor memory rather than kernel mappings.

Integration points: included for `GOOS_test`; used by `test.h` and fuzzer tests to exercise executor result paths deterministically.

Risks and tests: the sanitizer hook must remain uninstru­mented to avoid recursion. Synthetic PC values do not represent real kernel layout. This file is itself part of the test target; test signals include coverage injection, cover-filter tests, and executor package tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_windows.h -->
# sources/test-tools/syzkaller/executor/executor_windows.h

Purpose: Windows executor adapter for data allocation, syscall wrapper invocation, and pipe I/O shims.

Important APIs and control flow: `os_init` reserves and commits the executor data region at the requested address with `PAGE_EXECUTE_READWRITE`. `execute_syscall` calls the generated wrapper under structured exception handling and returns `-1` on exception. The header includes `nocover.h`, so all coverage functions are stubs. It remaps `read` and `write` macros to `read_win` and `write_win`, which call `ReadFile`/`WriteFile` on `_get_osfhandle(pipe_id)` and return byte counts.

State and dependencies: depends on Windows handles and C runtime fd-to-handle conversion. No persistent coverage state is maintained.

Integration points: selected by `executor.cc` for `GOOS_windows`; complements `common_windows.h` threading/events/temp-dir support.

Risks and tests: `read_win`/`write_win` ignore API failure details and return zero bytes on failure, so protocol failures surface as short reads/writes in common executor code. Coverage and comparisons are unavailable. Test signals are target builds and Windows executor runtime checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/executor_windows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/files.h -->
# sources/test-tools/syzkaller/executor/files.h

Purpose: File discovery and file-content reporting helpers used during runner handshake and glob requests.

Important APIs and control flow: `Glob` wraps libc `glob` with alternate directory functions. Its custom `readdir` filters most symlinks to avoid recursion and escaping the target tree, while allowing selected symlink names such as `self`, `thread-self`, `kmalloc-64`, and cgroup links. It omits directory results and returns files. `ReadFile` opens a file, records existence/error/data in `rpc::FileInfoRawT`, and reads in 4 KiB chunks. `ReadTextFile` formats a path, reads it, and trims trailing newline/NUL. `ReadFiles` expands globs or reads explicit file paths.

State and dependencies: stateless apart from temporary buffers. Depends on POSIX file APIs, `glob`, `dirent`, and flatrpc file info types.

Integration points: runner `Handshake` sends requested host/VM files to the manager; executor `execute_glob` serializes glob results into output shared memory.

Risks and tests: symlink filtering is intentionally heuristic and name-based. `ReadFile` treats `EEXIST` and `ENOENT` as non-existing, while other open errors mark exists with an error string. `test_glob` builds a small directory tree to validate non-recursive file matching, hard-link inclusion, and controlled symlink handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/files.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/gen_linux_amd64.go -->
# sources/test-tools/syzkaller/executor/gen_linux_amd64.go

Purpose: Go generate hook for producing x86-64 KVM machine-code header data.

Important API and control flow: the `//go:generate` directive compiles `kvm_gen.cc` with `kvm_amd64.S`, defining `GOARCH_$GOARCH=1`, runs the resulting `kvm_gen` helper, redirects its output to `kvm_amd64.S.h`, and removes the temporary binary. The Go file has no runtime exports beyond belonging to package `executor`.

State and dependencies: generated output depends on GCC, assembler support, `kvm_gen.cc`, `kvm_amd64.S`, and the current `GOARCH` environment. `-Wa,--noexecstack` is passed for the assembly object.

Integration points: keeps generated byte-string blobs synchronized with assembly snippets used by KVM setup tests and executor KVM pseudo-syscalls.

Risks and tests: stale generated headers can diverge from assembly if `go generate` is not run. The generation command assumes GCC-compatible tooling. Validation comes from source review, generated-header diffs, and `test_kvm` on supported Linux amd64 hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/gen_linux_amd64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/gen_linux_ppc64le.go -->
# sources/test-tools/syzkaller/executor/gen_linux_ppc64le.go

Purpose: Go generate hook for producing ppc64le KVM machine-code header data.

Important API and control flow: the `//go:generate` directive compiles `kvm_gen.cc` with `kvm_ppc64le.S`, defining `GOARCH_$GOARCH=1`, runs `kvm_gen`, writes `kvm_ppc64le.S.h`, and removes the temporary generator. The file is runtime-empty package metadata.

State and dependencies: depends on GCC/assembler support for ppc64le assembly, `kvm_gen.cc`, `kvm_ppc64le.S`, and the `GOARCH` environment.

Integration points: generated blobs are included by KVM setup/test code for Linux ppc64le executor behavior.

Risks and tests: generated byte arrays must be refreshed when assembly changes. The test signal is `test_kvm` ppc64le cases that execute `kvm_ppc64_mr` and `kvm_ppc64_ld` under different setup flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/gen_linux_ppc64le.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm.h -->
# sources/test-tools/syzkaller/executor/kvm.h

Purpose: Shared KVM/SYZOS constant header defining guest memory layouts, architecture control bits, selectors, MSRs, VMCS/VMCB fields, and generic KVM sizing constants.

Important content: on amd64 it defines legacy x86 setup addresses, SYZOS memory map regions, per-L1-VCPU and per-L2-VM layout macros, segment selectors, CR0/CR4/EFER bits, page-table bits, EPT flags, selector indexes, MSR numbers, VMX/SVM access-rights constants, VMCS fields, VMCB offsets, and magic placeholders `X86_NEXT_INSN`/`X86_PREFIX_SIZE`. Generic constants include `KVM_MAX_VCPU`, `KVM_MAX_L2_VMS`, `KVM_PAGE_SIZE`, `KVM_GUEST_PAGES`, and `GENMASK_ULL`. Arm64 and riscv64 sections define interrupt-controller, exit, dirty-page, user-code, executor-code, scratch, stack, and table addresses.

State and dependencies: no runtime state; it is a compile-time contract shared by assembly, generated blobs, KVM pseudo-syscalls, and tests.

Integration points: included by `kvm_amd64.S`, `kvm_ppc64le.S`, generated KVM setup code, and Linux KVM tests. Constants must match guest memory initialization in common Linux KVM helpers outside this subset.

Risks and tests: address overlap or stale VMCS/VMCB fields can silently break guest setup. Architecture-specific sections are macro-guarded, so cross-arch compile coverage is important. `test_kvm` and `test_syzos` are the strongest signals.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_amd64.S -->
# sources/test-tools/syzkaller/executor/kvm_amd64.S

Purpose: x86 assembly snippets converted into byte arrays for KVM guest setup and mode-transition prefixes.

Important APIs and control flow: exported symbol pairs include `kvm_asm64_enable_long`, `kvm_asm32_paged`, `kvm_asm32_vm86`, `kvm_asm32_paged_vm86`, `kvm_asm16_cpl3`, `kvm_asm64_cpl3`, `kvm_asm64_init_vm`, and `kvm_asm64_vm_exit`, each with `_end` markers for `kvm_gen.cc`. Snippets enable paging/long mode, load TSS, transition to CPL3 through crafted far returns, enter VM86, initialize VMXON/VMCS state, write host/guest VMCS fields, launch a nested VM, and capture VM-exit diagnostics.

State and dependencies: uses constants from `kvm.h` as absolute guest physical/virtual addresses. The assembly assumes the KVM setup code has prepared GDT, IDT, page tables, VMXON/VMCS memory, TSS, and user code at matching addresses.

Integration points: `gen_linux_amd64.go` and `kvm_gen.cc` convert symbols to `kvm_amd64.S.h`; KVM setup code injects those byte strings into guest memory; `test_linux.h` validates mode combinations.

Risks and tests: VMX control setup is sensitive to CPU MSR allowed bits and selector/access-rights constants. Hardcoded absolute addresses must remain synchronized with `kvm.h`. Test signal is Linux amd64 `test_kvm`, gated by `/dev/kvm`, permissions, CPU VMX support, and kernel version for SMM.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_amd64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_amd64.S.h -->
# sources/test-tools/syzkaller/executor/kvm_amd64.S.h

Purpose: Generated C header containing byte-string encodings of the amd64 KVM assembly snippets.

Important API surface: defines `const char` arrays for `kvm_asm16_cpl3`, `kvm_asm32_paged`, `kvm_asm32_vm86`, `kvm_asm32_paged_vm86`, `kvm_asm64_enable_long`, `kvm_asm64_init_vm`, `kvm_asm64_vm_exit`, and `kvm_asm64_cpl3`.

State and dependencies: no runtime state. It is generated by compiling `kvm_gen.cc` with `kvm_amd64.S` and printing bytes between each symbol and its `_end` marker.

Integration points: included by KVM setup code/tests that need raw machine code rather than assembler sources at runtime.

Risks and tests: this file should not be hand-edited. Its only reliable validation is regenerating from assembly and running KVM tests. Divergence from `kvm_amd64.S` can produce opaque guest failures because byte strings have no symbolic checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_amd64.S.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_gen.cc -->
# sources/test-tools/syzkaller/executor/kvm_gen.cc

Purpose: Small build-time generator that emits C string byte arrays from linked assembly symbol ranges.

Important APIs and control flow: `PRINT(x)` declares external `x` and `x_end` byte symbols and calls `print`. `print` writes `const char name[] = "\x.."` for every byte in `[start, end)`. `main` prints a generated-file banner and selects amd64 or ppc64le symbol sets based on `GOARCH_amd64`/`GOARCH_ppc64le`.

State and dependencies: stateless command-line program using `stdio`. It relies on the linker preserving assembly symbol addresses and on architecture macros supplied by `go generate`.

Integration points: invoked by `gen_linux_amd64.go` and `gen_linux_ppc64le.go`; output is checked into `kvm_*.S.h`.

Risks and tests: missing `_end` symbols, wrong architecture macros, or assembler/linker changes can generate invalid or empty arrays. Tests are generated-header diffs and runtime KVM tests that consume the arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_gen.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_ppc64le.S -->
# sources/test-tools/syzkaller/executor/kvm_ppc64le.S

Purpose: ppc64le assembly snippets converted into byte arrays for KVM setup tests.

Important APIs and control flow: `LOAD64` materializes a 64-bit immediate into a register. `kvm_ppc64_mr` loads `0xbadc0de`, moves it through registers, and leaves it in GPR3. `kvm_ppc64_ld` stores `0xbadc0de` near the end of the executor's expected VM memory and reloads it into GPR3. `kvm_ppc64_recharge_dec` reloads the decrementer SPR and returns from interrupt with `rfid`.

State and dependencies: relies on guest memory sizing/layout assumptions from KVM setup code and `kvm.h`. Symbol `_end` markers are used by `kvm_gen.cc`.

Integration points: generated into `kvm_ppc64le.S.h` and exercised by Linux ppc64le `test_kvm`.

Risks and tests: hardcoded memory offsets must match the memory region used by tests. Instruction encoding correctness is validated only through generation and KVM execution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_ppc64le.S -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_ppc64le.S.h -->
# sources/test-tools/syzkaller/executor/kvm_ppc64le.S.h

Purpose: Generated C header containing byte-string encodings of ppc64le KVM assembly snippets.

Important API surface: defines `const char kvm_ppc64_mr[]`, `kvm_ppc64_ld[]`, and `kvm_ppc64_recharge_dec[]`.

State and dependencies: no runtime state; generated by `kvm_gen.cc` from `kvm_ppc64le.S`.

Integration points: consumed by Linux ppc64le KVM setup/test code.

Risks and tests: should not be manually edited. Staleness or generation under the wrong toolchain can cause guest register checks to fail. `test_kvm` validates `mr` and `ld` snippets across setup flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/kvm_ppc64le.S.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/nocover.h -->
# sources/test-tools/syzkaller/executor/nocover.h

Purpose: No-op coverage adapter for targets without executor coverage support.

Important APIs: defines empty `cover_open`, `cover_enable`, `cover_reset`, `cover_collect`, `cover_protect`, `cover_mmap`, and `cover_unprotect` functions with the same signatures expected by `executor.cc`.

State and dependencies: no state, no external dependencies beyond the common `cover_t` type.

Integration points: included by Fuchsia and Windows executor adapters.

Risks and tests: callers must not expect coverage buffers, signal collection, or comparisons when this header is active. Compile-time integration is the main test signal; runtime manager negotiation should avoid requesting unsupported coverage where appropriate.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/nocover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/shmem.h -->
# sources/test-tools/syzkaller/executor/shmem.h

Purpose: RAII wrapper for shared memory regions used by runner request/response buffers and coverage filters.

Important APIs and control flow: `ShmemFile(size)` creates a `mkstemp` file, `ftruncate`s it, mmaps it read/write, and unlinks the name. `ShmemFile(fd, preferred, size, write)` maps an existing fd at an optional preferred address with read-only or read/write protections. The destructor unmaps and closes owned fds. `Seal` mprotects the mapping read-only and closes the fd. `FD` and `Mem` expose the backing fd and mapped pointer.

State and dependencies: owns `mem_`, `size_`, and `fd_`. Uses POSIX `mkstemp`, `ftruncate`, `mmap`, `munmap`, `mprotect`, `unlink`, and `close`.

Integration points: `executor_runner.h` uses it for request/response shmem; `CoverFilter` stores its table in a `ShmemFile`.

Risks and tests: `Seal` closes the fd, so callers must duplicate/pass fds before sealing if needed. Mapping failures are fatal. OpenBSD lacks `fallocate`, hence `ftruncate` is the portable sizing method. Indirectly tested through runner and cover-filter tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/shmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/snapshot.h -->
# sources/test-tools/syzkaller/executor/snapshot.h

Purpose: Snapshot-mode executor support for qemu ivshmem based fast restore/execute cycles.

Important APIs and control flow: `FindIvshmemDevices` scans PCI devices for ivshmem vendor/device IDs, distinguishes doorbell and shared input/output regions by resource size, maps registers and shmem, and points `output_data` after `SnapshotHeaderT`. `SnapshotSetup` enables snapshot mode, reads a flatbuffer handshake from ivshmem input, parses normal executor flags, and performs requested feature setup. `SnapshotSetState` writes state and rings the doorbell. `SnapshotStart` pre-creates threads, prefaults output/input/globals/data/coverage memory, waits for parent prefaulting, marks `Ready`, handles first snapshot acknowledgement, then parses a `SnapshotRequest` after restore. `SnapshotDone` serializes final output and marks `Executed` or `Failed`.

State and dependencies: global `ivs` stores doorbell, header, and input pointers. State persists in the ivshmem header and executor globals across snapshot/restore. Linux pkeys can protect output memory.

Integration points: selected by `main exec snapshot`; shares `parse_handshake`, `parse_execute`, `finish_output`, and coverage/thread machinery with normal execution.

Risks and tests: relies on qemu ivshmem layout, resource sizes, busy-wait state transitions, and precise prefault sizes. Missing devices or feature setup failures are fatal. Test signals are snapshot-mode integration tests rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/style_test.go -->
# sources/test-tools/syzkaller/executor/style_test.go

Purpose: Go style/regression test enforcing executor source patterns that affect csource generation, reproducibility, and runtime safety.

Important APIs and control flow: `TestExecutorMistakes` defines regex checks with optional suppressions, example snippets that must match, and `commonOnly`/`fuzzerOnly` filters. It scans all `*.cc` and `*.h` files from `executorFiles`, reports line-local errors, and excludes runner helper files from allocation restrictions. `executorFiles` globs C++ and header files, requires both classes to exist, concatenates and sorts them.

State and dependencies: test-only state is the checks table. Depends on Go `testing`, regex, bytes, filepath globs, slices, and strings.

Integration points: protects assumptions in `embed.go` and executor design: debug calls in common headers need braces for csource stripping, block comments are banned, `SYZ_*` macros should use `#if`, malloc/new are discouraged in fuzzer paths, and exit APIs should go through executor wrappers.

Risks and tests: regex checks can have false positives/negatives, so suppressions are part of the contract. The test is itself the direct signal and should run in Go package tests for the executor.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/style_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/subprocess.h -->
# sources/test-tools/syzkaller/executor/subprocess.h

Purpose: POSIX subprocess wrapper used by the runner to launch executor children and binary test payloads with controlled fd mappings.

Important APIs and control flow: the constructor builds `posix_spawn_file_actions`, validates source fds do not overlap target fd range, adds requested dup/close actions, closes all other fds up to `kFdLimit`, creates a new process group, and starts the child with ASAN and glibc rseq environment overrides. `KillAndWait` sends `SIGKILL` to the child pid and waits. `WaitAndKill` polls with timeout, kills the process group and pid on timeout, then returns normalized status. `ExitStatus` maps exits, signals, and unusual wait states away from ambiguous `kFailStatus`/0 values.

State and dependencies: owns `pid_`; destructor kills any still-running child. Depends on `posix_spawn`, `waitpid`, `kill`, and executor timing helpers.

Integration points: `executor_runner.h` uses it for persistent `exec` subprocesses and temporary binary execution requests.

Risks and tests: fd remapping is intentionally single-pass and rejects overlapping source fds. `KillAndWait` kills only the top process, while `WaitAndKill` can kill the process group; runner comments acknowledge descendant processes can survive in some hang paths. Test signal is runner integration and timeout behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/subprocess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/test.h -->
# sources/test-tools/syzkaller/executor/test.h

Purpose: Built-in executor self-tests selected by `syz-executor test [name]`.

Important APIs and control flow: includes Linux KVM tests for supported architectures. `test_copyin` validates bitfield/endian store macros. `test_csum_inet` and `test_csum_inet_acc` validate Internet checksum fixed vectors and incremental update equivalence. `test_cover_filter` validates parent/child shared filter membership and false-positive granularity. `test_glob` builds a local tree and validates file/symlink behavior. `test_get_last_opt` checks command-line option parsing. `tests[]` registers test names and `run_tests` executes all or one named test with RUN/OK/FAIL/SKIP output.

State and dependencies: tests create files in cwd and use global executor helpers/macros. Some tests are arch/OS gated.

Integration points: invoked by `main` before normal `exec` mode. The tests cover helpers used by csource, runner handshakes, coverage filtering, and KVM setup.

Risks and tests: `test_glob` intentionally skips on 32-bit ARM under QEMU due to known `readdir` overflow. KVM tests require `/dev/kvm` and permissions. The file is both implementation and test signal for many helper contracts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/test_linux.h -->
# sources/test-tools/syzkaller/executor/test_linux.h

Purpose: Linux-specific executor self-tests for KVM setup and SYZOS installation.

Important APIs and control flow: `test_one` creates `/dev/kvm` VM/VCPU, maps `kvm_run`, allocates guest memory, calls `syz_kvm_setup_cpu`, runs `KVM_RUN`, checks exit reason, and optionally verifies result register (`rax` on amd64, `gpr[3]` on ppc64le). `test_kvm` chooses architecture-specific guest byte snippets and setup flags; amd64 gates VMX cases on supported CPUID and SMM cases on kernel version, while ppc64le loops flag combinations for generated snippets. `host_kernel_version`, `dump_cpu_state`, `dump_seg`, and `cpu_feature_enabled` support diagnostics. `test_syzos` on arm64 maps memory and calls `install_syzos_code`.

State and dependencies: uses real KVM fds, guest memory, generated KVM blobs, and setup helpers outside this subset. It prints detailed CPU state on failure.

Integration points: included by `test.h` for Linux amd64/ppc64/ppc64le/arm64. Validates `kvm.h`, generated assembly headers, and KVM pseudo-syscall setup.

Risks and tests: failures can be environmental (`/dev/kvm` absent, permissions, unsupported CPU feature) and return SKIP where appropriate. Hardcoded expected exit reasons vary by setup mode and architecture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/test_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action.go -->
# sources/test-tools/syzkaller/pkg/aflow/action.go

Purpose: Core action abstraction for the `aflow` package.

Important APIs and control flow: `Action` requires unexported `verify(*verifyContext)` and `execute(*Context) error` methods, restricting implementations to the package or types that can satisfy those unexported names in-package. `pipeline` stores ordered `Action`s. `Pipeline(actions ...Action)` constructs a pipeline. `(*pipeline).execute` runs actions sequentially and stops on the first error. `(*pipeline).verify` calls every action's verifier in order.

State and dependencies: `pipeline.actions` is immutable by convention after construction but not defensively copied. Execution state lives in the passed `Context`; validation state lives in `verifyContext`.

Integration points: other `aflow` actions compose through `Pipeline` to express ordered automation flows while allowing dataflow through shared context variables, args, instructions, or prompts.

Risks and tests: because verification visits all actions even if earlier verification records errors, `verifyContext` must aggregate/report consistently. Because execution short-circuits on errors, later actions may not run cleanup unless modeled separately. Test signals are package tests for concrete actions and pipeline composition.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action.go -->

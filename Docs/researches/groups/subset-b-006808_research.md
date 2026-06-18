# subset-b-006808 Research

Grouped source research for Linux BPF selftest harnesses and BPF programs under `tools/testing/selftests/bpf`. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/user_ringbuf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/user_ringbuf.c

## Purpose

Host-side selftest coverage for libbpf user ring buffer maps. It validates mmap protections, malformed producer records, reserve/submit/discard behavior, wraparound/overfill handling, blocking reserve wakeups, and a bidirectional message protocol between a userspace producer and BPF programs in `user_ringbuf_success`/`user_ringbuf_fail`. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`user_ring_buffer__new()`, `user_ring_buffer__reserve()`, `user_ring_buffer__reserve_blocking()`, `user_ring_buffer__submit()`, `user_ring_buffer__discard()`, `ring_buffer__new()`, `ring_buffer__consume()`, `bpf_map__set_max_entries()`, `mmap()`, `mprotect()`, `mremap()`, `pthread_create()`, and syscall triggers such as `getpgid`, `prctl`, and `prlimit64`. Key helpers are `write_samples()`, `open_load_ringbuf_skel()`, `load_skel_create_ringbufs()`, `manually_write_test_invalid_sample()`, `send_test_message()`, and `handle_kernel_msg()`.

## Control Flow

`test_user_ringbuf()` sets page-sized ring buffers, runs the success subtest table, then runs failure skeleton tests. Each success test loads a skeleton, scopes the BPF program to the current PID, attaches it, writes or corrupts ring data, triggers kernel consumption through syscalls, and asserts BSS counters/errors. The protocol test alternates user-to-kernel messages and kernel-to-user ring buffer consumption; the blocking test fills the ring, proves timeout behavior, then wakes a blocking reserve from another thread.

## State and Persistence Behavior

State is transient: libbpf ring buffer mappings, kernel/user ring buffer maps, skeleton BSS counters (`read`, `err`, `kern_mutated`, `user_mutated`), and a temporary pthread. There is no file persistence; mmaped producer/data pages are explicitly unmapped and skeleton/ring buffers are destroyed per subtest.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

The tests depend on page size, exact ring buffer header alignment, kernel memory-ordering semantics for producer position, and errno behavior for malformed samples. Missed cleanup can leave mappings or threads alive; log noise is intentionally minimized by asserting mostly on error paths.

## Test Signals

Expected signals include successful subtest table execution, `RUN_TESTS(user_ringbuf_fail)` verifier/load failures, exact BSS read/error counts, `-EINVAL`/`-E2BIG` for malformed records, no reads for discarded samples, and blocking reserve timeout-then-success behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/user_ringbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/varlen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/varlen.c

## Purpose

Selftest for variable-length reads and copied payload accounting in `test_varlen` BPF programs. It verifies that split input strings are captured into BSS/data buffers with correct lengths and that a deliberately bad read reports `-EFAULT` without corrupting sentinel bytes. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_varlen__open_and_load()`, `test_varlen__attach()`, skeleton BSS/data sections, `memcpy()`, `memcmp()`, `usleep()`, and `CHECK_VAL`/`CHECK` assertions.

## Control Flow

The test loads and attaches the skeleton, sets `test_pid`, writes `Hello, ` and `World!` into BSS input buffers, toggles `capture`, sleeps briefly to let attached programs run, then checks four copied payload variants and bad-read sentinel state.

## State and Persistence Behavior

All state is skeleton memory: BSS inputs/control flags and BSS/data output payloads. It is destroyed with the skeleton and has no persistence beyond the test process.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Timing is minimal (`usleep(1)`), so failures can expose attach/trigger timing or scheduler assumptions. Payload expectations include embedded NUL bytes, making length-aware comparisons required.

## Test Signals

Passing signals are exact length totals, exact concatenated payload bytes with embedded NULs, `ret_bad_read == -EFAULT`, and unchanged sentinel bytes around the bad read output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/varlen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verif_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verif_stats.c

## Purpose

Small selftest confirming that BPF program info exposes verifier statistics for a loaded program. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`trace_vprintk_lskel__open_and_load()`, `bpf_prog_get_info_by_fd()`, `struct bpf_prog_info`, and `verified_insns`.

## Control Flow

Load the lightweight skeleton, query the `sys_enter` program fd with `bpf_prog_get_info_by_fd()`, and assert that the kernel reported a positive verified instruction count.

## State and Persistence Behavior

No durable state; only a skeleton fd and stack-local `bpf_prog_info` are used.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

The test assumes the kernel populates `verified_insns` for the loaded program and that the queried `bpf_prog_info` length matches the running kernel ABI.

## Test Signals

The meaningful signal is `info.verified_insns > 0` after successful skeleton load and info query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verif_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier.c

## Purpose

Central dispatcher for a large set of verifier selftests generated as libbpf skeletons. It runs each verifier object through `test_loader`, generally without effective `CAP_SYS_ADMIN`, and provides pre-execution map initialization for array/value pointer arithmetic cases. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_loader__run_subtests()`, `test_loader__set_pre_execution_cb()`, `cap_disable_effective()`, `cap_enable_effective()`, `bpf_object__find_map_by_name()`, `bpf_map_update_elem()`, and the `RUN()` macro binding skeleton ELF-byte factories to exported `test_verifier_*()` functions.

## Control Flow

`run_tests_aux()` drops `CAP_SYS_ADMIN`, installs an optional callback, runs subtests for the named skeleton, finalizes the loader, then restores capabilities. Most `test_verifier_*` entry points are thin wrappers. `test_verifier_array_access()` and `test_verifier_value_ptr_arith()` prepopulate array maps with `struct test_val` before verifier execution.

## State and Persistence Behavior

Persistent state is limited to temporary effective capability changes and map contents inserted before individual verifier object loads. There is no storage outside process/kernel BPF objects created by the test loader.

## Dependencies and Integration Points

It depends on many generated verifier skeleton headers, `cap_helpers.h`, `test_loader`, libbpf object/map APIs, and kernel verifier behavior across helper, pointer, scalar, context, arena, tail-call, socket, XDP, LSM, and other program-type rules.

## Risks and Edge Cases

Because this file is a dispatcher, incorrect skeleton naming or ELF-byte factory wiring silently drops coverage. Capability drop/restore failures affect subsequent tests. Pre-execution callbacks must match map names and value layouts expected by the BPF object.

## Test Signals

Signals are per-skeleton loader subtest pass/fail records, expected verifier accept/reject diagnostics in paired BPF sources, successful CAP restoration, and successful prepopulation of `map_array_ro`/`map_array_48b`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_kfunc_prog_types.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_kfunc_prog_types.c

## Purpose

Minimal harness for verifier coverage of kfunc availability across BPF program types. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`RUN_TESTS(verifier_kfunc_prog_types)` and the generated skeleton `verifier_kfunc_prog_types.skel.h`.

## Control Flow

The exported test function delegates all load/attach/expectation handling to the common selftest `RUN_TESTS` macro.

## State and Persistence Behavior

No local state; skeleton and verifier expectation state are managed by the selftest framework.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Coverage depends entirely on annotations in the paired BPF source and kernel kfunc/BTF availability.

## Test Signals

Pass/fail is reported by `RUN_TESTS`, including expected verifier rejections for unsupported kfunc/program-type combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_kfunc_prog_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_log.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_log.c

## Purpose

Detailed verifier and BTF log buffer regression test. It checks fixed and rolling log modes, `log_true_size`, exact-size and too-short buffers, NULL log-size queries, load success/failure handling, and accidental writes past user-provided log buffers. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_load()`, `bpf_btf_load()`, `bpf_prog_load_opts`, `bpf_btf_load_opts`, `BPF_LOG_FIXED`, `btf__new_empty()`, `btf__add_int()`, `btf__raw_data()`, skeleton instruction accessors, and `ASSERT_STRNEQ`/`ASSERT_STREQ` checks over guarded buffers.

## Control Flow

`verif_log_subtest()` selects a good or bad skeleton program, captures a full reference log, then iterates every shorter buffer size in rolling and fixed modes to verify truncation contents and untouched tail bytes. It then validates `log_true_size` for real and NULL buffers and boundary cases. `verif_btf_log_subtest()` builds good or intentionally invalid BTF and repeats the same log-size/truncation logic. `test_verifier_log()` runs good/bad program and BTF subtests.

## State and Persistence Behavior

Global `logs` contains filler, active buffer, and reference buffer arranged to catch overrun/corruption. Global `insns`, `insn_cnt`, `btf_data`, and `btf_data_sz` point at the currently tested program/BTF. No state survives test exit.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It also depends on libbpf BTF construction APIs and kernel support for rolling verifier logs and `log_true_size`.

## Risks and Edge Cases

The test is sensitive to verifier log text length and mode semantics; kernel changes to emitted stats/log ordering can change expected sizes. It deliberately mutates a BTF type size through an internal pointer, so libbpf representation changes can affect the bad-BTF path.

## Test Signals

Important signals are `-ENOSPC` for too-short logs, exact prefix/suffix content for fixed/rolling modes, unchanged filler tails, equal fixed/rolling true sizes, valid NULL-buffer size queries, and expected good/bad load outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verify_pkcs7_sig.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verify_pkcs7_sig.c

## Purpose

Selftest for `bpf_verify_pkcs7_signature()` and signature verification from both map-updated data and fsverity xattrs. It exercises keyring selection, permission/expiration failures, corrupted data, module signature extraction, and file-open LSM enforcement. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_verify_pkcs7_sig` and `test_sig_in_xattr` skeletons, `bpf_map_update_elem()`, `request_key`, `keyctl`, `setxattr()`, `fsverity` setup script commands, `sign-file`, module signature parsing, `mkdtemp()`, `mkstemp()`, `mmap()`, and a custom libbpf print callback that detects missing kfunc BTF.

## Control Flow

The map test creates a temporary signing setup, loads the skeleton, skips if the kfunc is unavailable, attaches, then updates `data_input` through empty, valid session keyring, testing keyring, permission-denied, expired, corrupted-data, and optional system-keyring/module-signature cases. The fsverity test creates signed files through `verify_sig_setup.sh`, loads an xattr-checking skeleton, opens the file before/after fsverity enablement and with valid/invalid signatures.

## State and Persistence Behavior

Temporary directories and files under `/tmp`, session/testing keyrings, xattrs, skeleton BSS fields (`monitored_pid`, keyring serials, digest, signature size), and optional mapped module contents are used. Cleanup script runs at exit paths; there is no repository persistence.

## Dependencies and Integration Points

It depends on key retention, module signature, fsverity, xattr, `sign-file`, `verify_sig_setup.sh`, generated skeletons, and BPF kfunc availability in kernel/module BTF.

## Risks and Edge Cases

Environment variability is high: missing kfunc, missing fsverity support, missing `tcp_bic.ko`, filesystem xattr/fsverity limitations, keyring permission semantics, and external helper failures can skip or fail paths. Temporary cleanup and key permission restoration are important.

## Test Signals

Expected signals include skip on unsupported kfunc/fsverity setup, failed map updates for empty/corrupt/unauthorized/expired keys, successful updates for valid keyrings, platform keyring rejection in the tested case, and open success/failure transitions for fsverity+xattr cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verify_pkcs7_sig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vmlinux.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vmlinux.c

## Purpose

Smoke test that BPF programs compiled against `vmlinux.h` can attach to several tracing mechanisms and observe a nanosleep trigger. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_vmlinux__open_and_load()`, `test_vmlinux__attach()`, `syscall(__NR_nanosleep)`, and BSS flags for tracepoint, raw tracepoint, tp_btf, kprobe, and fentry handlers.

## Control Flow

Load and attach the skeleton, call `nanosleep()` with a distinctive nanosecond value, then assert each BSS flag was set by its corresponding BPF program.

## State and Persistence Behavior

Only skeleton BSS flags persist during the test; no file or kernel state is retained after skeleton destruction.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

The test depends on availability of all tracing attach mechanisms and the nanosleep path on the running kernel.

## Test Signals

All of `tp_called`, `raw_tp_called`, `tp_btf_called`, `kprobe_called`, and `fentry_called` must be true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vmlinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vrf_socket_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vrf_socket_lookup.c

## Purpose

Network namespace selftest proving TC/XDP socket lookup helpers are VRF-aware. It builds two veth paths between namespaces, places one path in a VRF, attaches lookup programs, opens servers inside/outside the VRF, and verifies lookup isolation. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`start_server()`, `make_sockaddr()`, `SO_BINDTODEVICE`, `bpf_tc_hook_create()`, `bpf_tc_attach()`, `bpf_xdp_attach()`, `open_netns()`, `if_nametoindex()`, `connect()`/`sendto()`, and skeleton BSS controls `test_xdp`, `tcp_skc`, `lookup_status`.

## Control Flow

Setup creates namespaces, veth pairs, VRF `vrf1`, routes, and attaches TC/XDP programs to NS0 devices. Each subtest opens non-VRF and VRF-bound servers in NS0, switches to NS1, sends traffic to each IP/port combination, and expects lookup success only when packet ingress VRF matches server scope.

## State and Persistence Behavior

State is network namespaces, veth/VRF devices, attached BPF programs, server sockets, and skeleton BSS flags. `cleanup()` deletes namespaces before and after the test.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires iproute2 VRF support, namespace privileges, and TCP/UDP socket lookup helper behavior.

## Risks and Edge Cases

The subtest names claim TCP/UDP and `bpf_skc_lookup_tcp()` variations, but all calls currently pass `SOCK_STREAM` and `tcp_skc=false`, which narrows actual coverage. Namespace cleanup failures can affect later runs.

## Test Signals

For each traffic direction, `lookup_status` must be 1 only for in-to-in and out-to-out cases and 0 for VRF-crossing cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vrf_socket_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/wq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/wq.c

## Purpose

Harness for BPF workqueue tests, including successful workqueue execution, expected verifier/load failures, and a custom negative case for maps lacking BTF. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`RUN_TESTS(wq)`, `RUN_TESTS(wq_failures)`, `wq__open_and_load()`, `bpf_prog_test_run_opts()`, `bpf_object__prepare()`, `bpf_map_create()`, `bpf_map__reuse_fd()`, raw `bpf_prog_load()`, and verifier log substring checks.

## Control Flow

`serial_test_wq()` runs common success tests, reloads the skeleton, attaches it, test-runs a sleepable syscall-array program, waits briefly, and checks that a timer/workqueue callback updated BSS. `serial_test_failures_wq()` delegates negative tests. `test_wq_custom()` loads instructions with a reused no-BTF map and asserts verifier log text.

## State and Persistence Behavior

Transient skeletons, one manually created array map fd, verifier log buffer, and BSS `ok_sleepable`. No durable state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires BPF workqueue support and BTF-bearing map validation.

## Risks and Edge Cases

The sleep is short and depends on async callback scheduling. The negative log check is string-sensitive. The reused fd path must close through skeleton destruction.

## Test Signals

`ok_sleepable == (1 << 1)`, expected failure skeleton results, failed raw program load for no-BTF map, and log substring `has to have BTF in order to use bpf_wq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp.c

## Purpose

Basic XDP tunnel rewrite test using shared IPv4/IPv6 packet fixtures. It verifies that `test_xdp.bpf.o` looks up VIP-to-tunnel map entries and rewrites packets for XDP_TX with the expected outer protocol. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_load()`, `bpf_find_map()`, `bpf_map_update_elem()` for `vip2tnl`, `bpf_prog_test_run_opts()`, `struct vip`, `struct iptnl_info`, packet fixtures `pkt_v4`/`pkt_v6`, and output header parsing via `struct iphdr`/`struct ipv6hdr`.

## Control Flow

The test loads `test_xdp.bpf.o`, populates the `vip2tnl` map with IPv4 and IPv6 TCP VIP keys, test-runs the program on an IPv4 packet and checks `XDP_TX`, output size 74, and `IPPROTO_IPIP`, then test-runs on an IPv6 packet and checks `XDP_TX`, output size 114, and `IPPROTO_IPV6`.

## State and Persistence Behavior

State is the loaded object, `vip2tnl` map entries, stack output buffer, and parsed output headers. The object close releases all test state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Coverage is intentionally small; regressions outside basic test-run behavior may be caught by the more specialized XDP files in this subset.

## Test Signals

Successful XDP program load and expected `bpf_prog_test_run_opts()` return/action values are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_frags.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_frags.c

## Purpose

Selftest for XDP multi-buffer fragment updates through test-run. It checks that a BPF program can modify bytes in the linear head, in fragments, across the head/fragment boundary, and across fragment boundaries, and rejects unsupported oversized buffers. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_object__open()`, `bpf_object__load()`, `bpf_program__fd()`, `bpf_prog_test_run_opts()`, `/proc/sys/net/core/max_skb_frags`, `sysconf(_SC_PAGE_SIZE)`, and packet buffers carrying an offset marker.

## Control Flow

The test loads `test_xdp_update_frags.bpf.o`, allocates buffers of 128 bytes, 9000 bytes, and an oversized max-frags-plus-one size, writes an offset in the first word and marker bytes at target positions, runs the XDP program, and checks markers changed from `0xaa` to `0xbb` where supported or `-ENOMEM` for unsupported size.

## State and Persistence Behavior

Heap packet buffers and the loaded BPF object are transient. It reads but does not modify `/proc/sys/net/core/max_skb_frags`.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP multi-buffer test-run emulation and system page/max-frag settings.

## Risks and Edge Cases

Expected offsets assume the kernel test-run linear area and fragment layout. Non-default max-frag settings are called out in the assertion label and can affect the oversized-buffer case.

## Test Signals

Signals are `XDP_PASS`, exact marker mutation at 16/31, 5000/5015, 3510/3525, 7606/7621, and `-ENOMEM` for an unsupported buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_frags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_tail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_tail.c

## Purpose

XDP tail adjustment regression suite for shrinking and growing linear and fragmented packets, including page-size-specific behavior and data zeroing/untouched-region checks. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_load()`, `bpf_prog_test_run_opts()`, `bpf_object__open/load`, `getpagesize()`, XDP return codes, packet fixtures, and BPF objects `test_xdp_adjust_tail_shrink.bpf.o`/`test_xdp_adjust_tail_grow.bpf.o`.

## Control Flow

Subtests load shrink/grow programs, run IPv4/IPv6 fixture cases, validate `data_size_out`, then run synthetic packet-size cases for maximum grow and ENOSPC copy limits. Fragment subtests allocate 9KB/16KB/256KB buffers and check shrinking pages, growing last fragments, zero-filled new bytes, untouched tail bytes, and too-large grow drops. `test_xdp_adjust_tail()` dispatches page-size-specific variants.

## State and Persistence Behavior

State is only heap buffers, stack buffers, and loaded BPF objects. Page size influences expected paths but is not changed.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP test-run packet allocator layout, `skb_shared_info` tailroom assumptions, and architecture cacheline/page details.

## Risks and Edge Cases

Expected max grow/tailroom is architecture-sensitive; 64K page systems use different paths. Buffer aliasing via `data_in == data_out` makes size reset between calls important.

## Test Signals

Expected `XDP_DROP`/`XDP_TX`, exact output sizes such as IPv6 shrink/grow, ENOSPC with reported output size, zero-filled grown regions, and drop on too-large multi-buffer grow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_tail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_attach.c

## Purpose

Tests XDP attach/replace/detach semantics on loopback and validates failure diagnostics for invalid XDP link attachment flags. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_load()`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach()`, `bpf_xdp_query_id()`, `bpf_xdp_detach()`, `bpf_xdp_attach_opts.old_prog_fd`, perf-buffer error callback, and `test_xdp_attach_fail` skeleton.

## Control Flow

The main attach test loads three XDP programs, attaches the first with replace semantics, verifies program id, attempts invalid replacement, replaces with a valid old fd, checks id again, then verifies invalid detach and valid detach behavior. The failure path captures expected error text from a skeleton/perf event.

## State and Persistence Behavior

State is current XDP program on ifindex 1 and loaded object fds; detach paths clean up loopback attachment.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It assumes ifindex 1 is loopback and XDP generic attach is available.

## Risks and Edge Cases

Failure to detach leaves loopback modified for later tests. Program id checks are sensitive to querying the same attach mode as used for attach.

## Test Signals

Signals include exact program-id transitions, failed replacement with wrong expected fd, failed detach with wrong old fd, successful detach with correct old fd, and expected invalid-link-flag error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bonding.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bonding.c

## Purpose

Comprehensive XDP bonding integration test. It validates XDP attach rules for bond masters/slaves, packet balancing across bond modes and xmit policies, multi-redirect behavior, nested bond safety, feature aggregation, no-up round-robin redirect safety, and xmit policy compatibility with native XDP. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_program__attach_xdp()`, `bpf_xdp_attach/detach/query()`, BPF links, raw AF_PACKET `sendto()`, `/proc/net/dev` parsing, `setns()`, iproute2 bond/veth/netns commands, `xdp_dummy`, `xdp_tx`, and `xdp_redirect_multi_kern` skeletons.

## Control Flow

`serial_test_xdp_bonding()` opens root netns, loads skeletons, runs attach/nested/features subtests, iterates bond mode cases, then runs xmit-policy, redirect-multi, and no-up tests. Setup creates paired namespaces and bonds, enslaves veths, attaches XDP programs, sends synthetic UDP frames, reads rx counters, and tears down links/namespaces after each case.

## State and Persistence Behavior

Large transient network state is created: namespaces, bonds, veths, BPF links, bond feature state, and packet counters. `root_netns_fd` anchors namespace restoration; `struct skeletons` tracks links for cleanup.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires bonding driver support, veth native/generic XDP, netdev feature reporting, namespace privileges, and iproute2 support for bond options.

## Risks and Edge Cases

Environment-sensitive and cleanup-sensitive. Counter assertions can be affected by background traffic on test interfaces if names collide. Some modes/policies are intentionally selected; unsupported xmit policies are reported as unimplemented. Failing namespace restoration can cascade.

## Test Signals

Signals include expected attach accept/reject combinations, packet distribution by mode/policy, redirect-multi excluding ingress bond/slave, feature flag changes as slaves/programs change, no crash for inactive RR bond redirect, and rejection of `vlan+srcmac` while native XDP is attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bonding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bpf2bpf.c

## Purpose

Selftest for XDP BPF-to-BPF calls and perf-event metadata reporting across packet sizes. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp`/`test_xdp_bpf2bpf` skeletons, `perf_buffer`, `bpf_prog_test_run_opts()`, a `struct meta` sample callback, and packet buffer sizing around `BUF_SZ`.

## Control Flow

The test opens XDP programs, configures perf-buffer callbacks, runs packet-size cases through an XDP program that calls into other BPF functions, and validates returned metadata/sample state in `test_ctx`.

## State and Persistence Behavior

State is `test_ctx`, perf-buffer samples, packet buffers, and skeleton maps/BSS. No durable state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on BPF-to-BPF call support for XDP programs and perf-event delivery.

## Risks and Edge Cases

Perf-buffer polling/ordering can make failures look like missing samples. Packet-size boundaries must match the paired BPF program expectations.

## Test Signals

Expected signals are successful test-run returns, perf sample callback invocation, and metadata fields matching the packet size/action under test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bpf2bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_context_test_run.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_context_test_run.c

## Purpose

XDP context and metadata test-run suite. It validates `bpf_prog_test_run_opts()` context validation, XDP metadata propagation into TC, TAP/TUN and mirred paths, dynptr access to metadata, and helper behavior that mutates skb headroom. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_run_opts()`, `struct xdp_md`, `bpf_tc_hook_create/attach()`, `bpf_xdp_attach()`, `open_tuntap()`, raw AF_PACKET `sendto()`, `tc mirred`, `bpf_prog_stream_read()`, and `test_xdp_context_test_run`/`test_xdp_meta` skeletons.

## Control Flow

`test_xdp_context_test_run()` runs valid and invalid context layouts, checking errno and normalized output context. `test_xdp_context_veth()` builds TX/RX namespaces with veth, attaches XDP and TC, sends a marker packet, and checks BSS. `test_xdp_context_tuntap()` runs TAP subtests for data_meta, dynptr read/write/slice/offset, cloned metadata survival, and helpers that adjust VLAN/head/tail/proto.

## State and Persistence Behavior

Transient namespaces, veth/TAP/dummy interfaces, TC hooks, XDP attachments, skeleton BSS `test_pass`, and stderr streams. Cleanup frees namespaces and skeletons.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires tuntap, clsact/mirred, TC, XDP generic attach, and dynptr/helper support.

## Risks and Edge Cases

Many subtests depend on network privileges and kernel helper semantics. Invalid context tests rely on precise errno (`EINVAL`, `E2BIG`). Diagnostic output comes from BPF program stderr streams.

## Test Signals

Signals include expected context rejection cases, normalized valid context/data sizes, `test_pass` from veth/TAP/mirred paths, and readable stderr on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_context_test_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_cpumap_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_cpumap_attach.c

## Purpose

Selftest for attaching programs to CPUMAP entries, including frags compatibility and negative fd/program-type cases. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_cpumap_val`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach/detach()`, live-frame `bpf_prog_test_run_opts()`, `kern_sync_rcu()`, and skeletons for normal/frags CPUMAP helpers.

## Control Flow

The normal test creates a namespace, attaches a redirect program to loopback, stores a `BPF_XDP_CPUMAP` program fd in a cpumap entry, verifies stored program id, sends a live-frame packet, waits for flush, checks redirect count, and then tests invalid direct attach, non-CPUMAP program, non-BPF fd, closed fd, and frags/non-frags incompatibility. The frags test performs the inverse compatibility check.

## State and Persistence Behavior

Transient namespace, loopback XDP attachment, cpumap entries, BSS redirect count, and one `/dev/null` fd for negative checks.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires CPUMAP entry program support and XDP live-frame test run.

## Risks and Edge Cases

Map-entry program compatibility rules are strict; mixing frags and non-frags programs must remain rejected. The namespace cleanup path must detach XDP to avoid leakage.

## Test Signals

Program id in map entry must match, redirect count must become nonzero, and invalid map updates/attaches must return `-EINVAL`, `-EBADF`, or nonzero as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_cpumap_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_dev_bound_only.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_dev_bound_only.c

## Purpose

Regression test for device-bound XDP program loading on a non-offload veth device. It distinguishes `BPF_F_XDP_DEV_BOUND_ONLY` from an ifindex-bound program that would be treated as offloaded. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Raw `bpf_prog_load()` with `prog_ifindex` and `prog_flags`, simple inline BPF instructions, `if_nametoindex()`, namespace/veth setup helpers, and `BPF_F_XDP_DEV_BOUND_ONLY`.

## Control Flow

The test creates a namespace and veth, loads a dummy XDP program bound to the veth with `BPF_F_XDP_DEV_BOUND_ONLY` and expects success, then loads a second ifindex-bound program without the flag and expects `-EINVAL` because veth does not support offload.

## State and Persistence Behavior

Transient namespace, veth, and two program fds. Namespace deletion removes the veth.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP offload/dev-bound loader semantics.

## Risks and Edge Cases

If device offload classification changes, the expected `-EINVAL` may change. The test is meant to catch a NULL dereference class in offload handling.

## Test Signals

First program fd is nonnegative; second load returns `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_dev_bound_only.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_devmap_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_devmap_attach.c

## Purpose

Selftest for DEVMAP entry-attached XDP programs, attach-type verifier checks, frags compatibility, tail-call attach typing, and veth live-frame redirection. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_devmap_val`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_prog_get_info_by_fd()`, `bpf_program__set_expected_attach_type()`, `bpf_xdp_attach/detach()`, live-frame `bpf_prog_test_run_opts()`, and DEVMAP helper skeletons.

## Control Flow

Normal DEVMAP tests attach a redirect program, insert a `BPF_XDP_DEVMAP` program into a devmap entry, verify id, trigger a packet, reject direct device attach of a DEVMAP program, and reject incompatible program types/frags. Tail-call tests load combinations of expected attach types and assert accept/reject. The veth case attaches redirect and receiver programs to a veth pair and runs a live-frame packet.

## State and Persistence Behavior

Transient namespace, loopback/veth XDP attachments, devmap entries, BPF objects, and program links. Cleanup deletes namespace and detaches programs.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires DEVMAP entry programs, XDP frags support, and veth native mode for the veth subtest.

## Risks and Edge Cases

Program attach type and frags compatibility rules are intentionally strict. Native XDP on veth may be unavailable in constrained environments.

## Test Signals

Stored devmap program id must match, live-frame test run must succeed, invalid attach/map update combinations must fail, and expected attach-type combinations must match verifier outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_devmap_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_do_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_do_redirect.c

## Purpose

XDP redirect integration tests. It validates live-frame XDP test-run interactions with XDP_PASS/TX/REDIRECT, veth feature flags, TC counting, maximum packet size limits, and index-based XDP forwarding across namespaces. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_run_opts()` with `BPF_F_TEST_XDP_LIVE_FRAMES`, `bpf_xdp_query()`, `bpf_program__attach_xdp()`, TC hook APIs, veth/netns/ip/sysctl/ethtool commands, `kern_sync_rcu()`, and `test_xdp_do_redirect`/`xdp_dummy` skeletons.

## Control Flow

The first test creates a veth namespace, enables IPv6 forwarding/GRO, queries XDP feature flags before and after GRO, loads a redirect skeleton, attaches an XDP counter and TC counter, runs `NUM_PKTS` live-frame test-run iterations, waits for flush, asserts XDP/TC counts, then checks max packet size. `test_xdp_index_redirect()` builds three namespaces and two fixed-index veths, attaches redirect programs on both sides, and verifies ping through noflag, drv, and skb modes.

## State and Persistence Behavior

Transient namespaces, veths, TC hooks, XDP attachments, BSS packet counters, neighbor entries, and sysctl/GRO state inside the namespace.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires veth feature reporting, ethtool, IPv6 forwarding, TC, and live-frame XDP test-run support.

## Risks and Edge Cases

Feature flags vary by kernel/device; GRO changes alter expected flags. Batch/live-frame paths can deadlock if kernel regressions reappear. Fixed ifindexes 111/222 are assumed free in NS0.

## Test Signals

Expected feature flag masks, `pkts_seen_xdp == 2`, `pkts_seen_zero == 2`, `pkts_seen_tc == NUM_PKTS - 2`, max-size success/too-big `-EINVAL`, and successful ping for each attach mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_do_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_flowtable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_flowtable.c

## Purpose

Integration test for XDP interaction with nftables flowtable forwarding. It builds a routed namespace topology, configures nft flowtable offload, attaches an XDP program, sends UDP traffic, and checks BPF stats. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`nft` command availability, iproute2 namespace/veth/dummy setup, `bpf_program__attach_xdp()`, `bpf_map_lookup_elem()`, UDP `sendto()`, and `xdp_flowtable` skeleton stats map.

## Control Flow

The test skips if `nft` is missing, creates TX/RX namespaces and forwarding/dummy devices, configures forwarding and nft flowtable rules, attaches the XDP program to the forwarding interface, sends repeated UDP packets to a routed destination, then reads a stats map key to validate flowtable/XDP observation.

## State and Persistence Behavior

Temporary namespaces, nft table/flowtable/rules, veth/dummy devices, XDP link, and stats map entries. Cleanup deletes namespaces and destroys skeleton/link.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires nftables, flowtable support, namespace privileges, and UDP routing between the constructed devices.

## Risks and Edge Cases

Highly environment-sensitive: nft missing, flowtable unsupported, or route/neigh differences can skip/fail. Traffic timing uses short sleeps to give flowtable state time to update.

## Test Signals

Signals are successful nft setup, UDP send completion, XDP attach success, and nonzero/expected stats map values after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_flowtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_info.c

## Purpose

Serial XDP info/query test on loopback. It validates `bpf_xdp_query_id()` before and after generic XDP attach and checks that loopback reports no driver-mode feature flags. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_xdp_query_id()`, `bpf_xdp_query()`, `bpf_prog_test_load()` for `xdp_dummy.bpf.o`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach()`, `bpf_xdp_detach()`, `bpf_xdp_query_opts`, and loopback ifindex 1.

## Control Flow

The test first confirms no XDP program id is reported for default or SKB mode. It loads `xdp_dummy.bpf.o`, records the program id, attaches it to loopback in SKB mode, verifies default and SKB queries return that id while DRV mode returns zero, then queries feature flags and detaches.

## State and Persistence Behavior

Transient loopback XDP state only; cleanup must detach any program installed by the test.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Assumes loopback is ifindex 1 and that no unrelated XDP program is attached by the environment.

## Test Signals

Expected query success and expected program id/zero-id values for the tested state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_link.c

## Purpose

Serial regression test for coexistence rules between legacy netlink-style XDP program attachment and BPF link-based XDP attachment on loopback. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_link` skeletons, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach()`, `bpf_xdp_detach()`, `bpf_xdp_query_id()`, `bpf_program__attach_xdp()`, `bpf_link_update()`, `bpf_link_get_info_by_fd()`, `bpf_link__fd()`, and loopback ifindex 1.

## Control Flow

The test loads two skeleton instances and obtains program ids. It attaches the first program through `bpf_xdp_attach()`, proves a BPF link cannot replace that legacy attachment, detaches it, attaches via BPF link, proves legacy attach/update cannot replace the active link, then exercises valid and invalid `bpf_link_update()` replacement using expected old program fds before checking link info and cleanup semantics.

## State and Persistence Behavior

State is the active loopback XDP program, one BPF link owned by `skel1`, and temporary legacy attach options. Destroying the skeleton/link should remove the attachment.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Loopback state conflicts can cause false failures. Link lifetime semantics are the core behavior under test, so premature fd/link close changes outcomes.

## Test Signals

Expected attach/query results while the link is live and automatic detach/cleanup after link destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_metadata.c

## Purpose

End-to-end XDP metadata and AF_XDP test. It verifies RX timestamp/hash/VLAN metadata, TX timestamp/checksum metadata, dev-bound XDP restrictions, AF_XDP UMEM metadata layout, and freplace attachment to a dev-bound program. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

AF_XDP APIs (`xsk_umem__create`, `xsk_socket__create`, ring reserve/submit/peek/release helpers), `bpf_xdp_attach()`, `bpf_map_update_elem()`, devmap/prog-array update checks, BPF program ifindex/flags setters, VLAN/veth namespace setup, UDP generation, `poll()`, and `xdp_metadata`/`xdp_metadata2` skeletons.

## Control Flow

The test creates TX/RX namespaces with a VLAN over veth, opens RX and TX AF_XDP sockets with metadata-enabled UMEM, loads dev-bound RX/redirect programs, verifies dev-bound programs cannot be inserted into prog arrays/devmaps, attaches RX XDP, sends an AF_XDP packet and validates TX/RX metadata, sends a normal UDP packet and validates RSS/VLAN metadata, then loads and attaches a freplace program targeting RX and sends another packet to prove invocation.

## State and Persistence Behavior

State includes namespaces, VLAN/veth devices, AF_XDP UMEM mappings/rings/sockets, XSK map entry, skeleton maps/BSS, dev-bound program fds, and freplace link state. Cleanup closes XSKs, destroys skeletons, closes namespace token, and deletes namespaces.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires AF_XDP, XDP metadata kfunc/support, VLAN, veth, dev-bound XDP, and freplace support.

## Risks and Edge Cases

Very environment-sensitive. Metadata availability depends on driver/veth support; ring index/address arithmetic must preserve metadata headroom; the retry loop for freplace has a likely inverted condition (`while (!retries--)`) that may not wait as intended.

## Test Signals

Expected metadata includes nonzero RX/TX timestamps, nonzero RX hash, L4 RSS type and VLAN id/proto for stack-generated packets, zero hash type and expected UDP checksum for AF_XDP-generated packets, rejected dev-bound program map insertions, and freplace `called > 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_noinline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_noinline.c

## Purpose

Harness for XDP program tests with noinline BPF helper/subprogram structure. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_noinline` skeleton, `bpf_prog_test_run_opts()` through the selftest helpers, and packet fixtures from `network_helpers.h`.

## Control Flow

The test loads the noinline skeleton and runs packet test cases to ensure XDP behavior remains correct when logic is split into non-inlined BPF subprograms.

## State and Persistence Behavior

Only skeleton state and packet buffers exist during the test.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on BPF subprogram call support in XDP programs.

## Risks and Edge Cases

Failures can indicate verifier/JIT subprogram issues rather than packet parser logic alone.

## Test Signals

Expected XDP return values and packet/result state from the noinline skeleton test run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_noinline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_perf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_perf.c

## Purpose

Small dispatcher for XDP performance-oriented selftests. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_progs.h` selftest entry point and the paired XDP performance BPF object invoked by the harness.

## Control Flow

The function delegates to the selftest framework for the XDP performance case; local control flow is intentionally minimal.

## State and Persistence Behavior

No local persistent state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Because this is a thin wrapper, all substantive behavior is in the paired BPF object and framework registration.

## Test Signals

Pass/fail is the selftest framework result for the XDP performance subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_pull_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_pull_data.c

## Purpose

Tests XDP pull-data behavior across frame sizes and return values, including large pull constants and packet data preservation. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_pull_data` skeleton, `bpf_prog_test_run_opts()`, frame-size probing in `find_xdp_sizes()`, `run_test()`, and constants `PULL_MAX`, `PULL_PLUS_ONE`, `XDP_PACKET_HEADROOM`.

## Control Flow

The basic test loads the skeleton, discovers acceptable XDP frame sizes, runs cases with different return values and pull sizes, and validates output packet sizes/contents and error behavior for too-large or boundary pulls.

## State and Persistence Behavior

State is skeleton maps/BSS, packet buffers, and computed frame-size limits. No durable state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP test-run frame allocation and headroom/tailroom limits.

## Risks and Edge Cases

Boundary constants are large and can expose integer overflow or frame-size assumptions. Architecture/page-size differences may affect computed limits.

## Test Signals

Expected return values, accepted/rejected pull sizes, and preserved packet data/size across run cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_pull_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_synproxy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_synproxy.c

## Purpose

Integration test for XDP and TC SYN proxy sample behavior using namespaces, iptables/nft-like control commands, and TCP handshake observation. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SYS()`/`SYS_OUT()` command helpers, `popen()`, `escape_str()`, `expect_str()`, veth/netns setup, `ethtool` checksum offload control, TCP sockets, and command output parsing.

## Control Flow

`test_synproxy()` creates a `synproxy` namespace and veth pair, disables checksum offload where needed, configures addresses and BPF SYN proxy path for XDP or TC mode, opens server/client sockets, reads control output, and compares expected strings. `test_xdp_synproxy()` runs XDP and likely TC variants through subtests.

## State and Persistence Behavior

Transient namespace, veth devices, sysctl/ethtool state inside the test topology, sockets, popen streams, and output buffers. Cleanup deletes the namespace.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires network namespaces, veth, TCP stack behavior, command-line networking tools, and SYN proxy BPF sample support.

## Risks and Edge Cases

String comparisons are exact after escaping, so command output changes are brittle. Checksum offload must be disabled because the XDP program sees pre-offload checksums.

## Test Signals

Expected command output strings, successful TCP connection/accept path, and no unexpected packet drops in XDP/TC SYN proxy modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_synproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_vlan.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_vlan.c

## Purpose

Network namespace selftest for XDP VLAN tag change/removal behavior with a TC companion program. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_vlan` skeleton, `bpf_xdp_attach()`, TC attach helpers through network commands, namespace/veth setup, `ping`, VLAN id/proto constants, and XDP attach flags.

## Control Flow

Setup creates two namespaces connected by veth, assigns IP addresses, and brings links up. `xdp_vlan()` attaches XDP and TC programs, sends traffic, and validates either VLAN change or removal behavior. Exported tests run change and remove variants.

## State and Persistence Behavior

Temporary namespaces, veth, XDP/TC attachments, and skeleton state. Cleanup deletes namespaces.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires namespace, veth, VLAN handling, XDP, TC, and ping.

## Risks and Edge Cases

Traffic and VLAN behavior depend on correct namespace cleanup and no interface-name collisions. Offload or kernel VLAN parsing changes can affect expectations.

## Test Signals

Successful ping/traffic with expected XDP VLAN transformation, and no assertion failures in change/remove subtests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdpwall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdpwall.c

## Purpose

Thin selftest entry for the `xdpwall` sample-style XDP program. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`xdpwall` skeleton and the selftest harness macros.

## Control Flow

The test loads/runs the skeleton through the shared framework; substantive packet/firewall logic is in the paired BPF program.

## State and Persistence Behavior

No local state beyond skeleton lifetime.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

This file gives little local context; test coverage quality depends on the generated skeleton and paired BPF object annotations.

## Test Signals

Pass/fail is reported by the selftest framework for `xdpwall`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdpwall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xfrm_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xfrm_info.c

## Purpose

Integration test for BPF TC helpers that set and get XFRM interface metadata. It builds a three-namespace IPsec/XFRM topology and verifies ping responses use the requested if_id. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

TC hook attach APIs, iproute2 XFRM state/policy commands, raw NETLINK_ROUTE message construction for external xfrm interface creation, namespace helpers, `ping`, and `xfrm_info` skeleton BSS fields `req_if_id`/`resp_if_id`.

## Control Flow

The test deletes stale namespaces, creates underlay veth networks, configures XFRM states/policies and ipsec0 interfaces, creates an external-mode xfrm device through netlink, loads TC ingress/egress BPF programs on NS0 ipsec0, then pings two overlay destinations by setting different requested if_ids and checking the response if_id recorded by ingress BPF.

## State and Persistence Behavior

Temporary namespaces, veths, XFRM state/policy database entries, ipsec0 devices, TC hooks, and skeleton BSS if_id state. Cleanup deletes all namespaces.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires XFRM/IPsec support, route netlink, iproute2 xfrm commands, TC, ping, and namespace privileges.

## Risks and Edge Cases

XFRM command syntax and external-device support vary by kernel/iproute2. The raw netlink request uses a fixed-size buffer. Cleanup is essential because XFRM state lives in namespaces.

## Test Signals

Successful underlay/overlay setup, TC attach success, ping success to each destination, and `resp_if_id` exactly matching `IF_ID_0_TO_1` and `IF_ID_0_TO_2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xfrm_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xsk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xsk.c

## Purpose

AF_XDP namespace test harness. It creates a veth pair, configures TX/RX interface objects, initializes packet streams and UMEM parameters, and runs each `test_xsk` scenario in SKB and DRV modes. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`setup_veth()`, `delete_veth()`, `configure_ifobj()`, `ifobject_create/delete()`, `init_iface()`, `test_init()`, `pkt_stream_generate/delete/restore_default()`, hardware ring-size helpers, procfs reads for cacheline/max frags, and `xsk_xdp_progs` skeleton cleanup.

## Control Flow

`test_ns_xsk_skb()` and `test_ns_xsk_drv()` create veths, iterate the global `tests[]` table, and call `test_xsk()` per subtest. `test_xsk()` creates ifobjects, populates ifindexes and tailroom, initializes RX/TX interfaces, creates default packet streams, runs the selected test function in the requested mode, restores defaults and hardware ring sizes, then destroys resources.

## State and Persistence Behavior

Transient veth pair, optional busy-poll sysfs values, ifobject/UMEM/socket state managed by the shared XSK helpers, packet streams, and XDP skeletons. `delete_veth()` removes interfaces after each mode suite.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends heavily on `test_xsk.h` shared helpers, AF_XDP, veth, procfs/sysfs tunables, and optional ethtool ring-size support.

## Risks and Edge Cases

Many behaviors are delegated to shared XSK helpers. Hardware ring-size and busy-poll support are environment-dependent. Cleanup must reset ring size when supported and delete both veth names.

## Test Signals

Each `tests[]` entry either returns `TEST_SKIP` or `0`; assertion coverage includes veth setup, ifobject initialization, packet stream generation, and cleanup without leaked XDP programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/access_map_in_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/access_map_in_map.c

## Purpose

BPF program object that stresses access to inner maps stored in array-of-maps and hash-of-maps containers from kprobe and sleepable fentry contexts. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Map definitions for `inner_map`, `outer_array_map`, `outer_htab_map`; `bpf_map_lookup_elem()`, `bpf_map_update_elem()`, `bpf_get_current_pid_tgid()`, and SEC programs `access_map_in_array`, `sleepable_access_map_in_array`, `access_map_in_htab`, `sleepable_access_map_in_htab`.

## Control Flow

Each entry calls `acc_map_in_map()`, filters by configured `tgid`, verifies a missing key returns no inner map, retrieves key 0, then repeatedly updates the inner map while userspace may replace map-in-map entries.

## State and Persistence Behavior

Persistent BPF maps are the inner array and two outer map-in-map containers. Global `tgid` controls activation; updates are kernel map state only.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here.

## Risks and Edge Cases

This is concurrency-oriented: repeated updates while userspace replaces inner maps can expose lifetime/refcount bugs. Sleepable and non-sleepable attach contexts must both be legal for map access.

## Test Signals

Verifier/load success for all attach sections and absence of crashes/refcount issues while userspace replacement tests run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/access_map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_atomics.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_atomics.c

## Purpose

BPF arena atomic operation test program. It exercises add/sub/bitwise/cmpxchg/xchg atomics, optional use-after-free recovery paths, and load-acquire/store-release instructions on arena globals. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `__arena_global`, GCC/C11 atomic builtins, inline encoded `BPF_LOAD_ACQ`/`BPF_STORE_REL`, `bpf_arena_alloc_pages()`, `bpf_arena_free_pages()`, `bpf_get_current_pid_tgid()`, raw tracepoint/syscall sections, and feature macros such as `ENABLE_ATOMICS_TESTS` and `__BPF_FEATURE_ADDR_SPACE_CAST`.

## Control Flow

Raw tracepoint programs filter by `pid`, perform one class of atomic operation, and store old/new values into arena globals for userspace assertions. Unsupported compiler/arch combinations set skip flags. The UAF path allocates and frees an arena page, then tries many atomic operations to verify recovery/fault accounting. Load/store acquire/release paths emit raw instructions when supported.

## State and Persistence Behavior

Arena map pages and many arena global variables carry expected values/results. `skip_all_tests` and `skip_lacq_srel_tests` communicate feature availability to userspace.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It also depends on compiler BPF feature macros and architecture support for arena atomics.

## Risks and Edge Cases

Highly feature-gated; clang version, target architecture, and kernel verifier/JIT atomic support determine coverage. Raw instruction encoding must match kernel opcode definitions.

## Test Signals

Userspace should observe skip flags when unsupported and exact result globals for each atomic operation when enabled; UAF recovery counter behavior is a key safety signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_atomics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab.c

## Purpose

BPF arena hash table exercise using helpers from `bpf_arena_htab.h`. It allocates an arena hash table, updates many elements, touches arena and non-arena arrays, and exposes the table pointer to userspace. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `bpf_alloc()`, `htab_init()`, `htab_update_elem()`, `cast_kern()`, `cast_user()`, arena globals, and `SEC("syscall") arena_htab_llvm`.

## Control Flow

When address-space casts are supported, the program allocates a hash table in arena memory, initializes it, loops up to 100000 updates while writing `arr1`, then does replacement updates for 1000 entries while touching `arr2`, casts the table pointer to user address space, and stores it in `htab_for_user`. Unsupported builds set `skip`.

## State and Persistence Behavior

Arena map pages hold the hash table and `arr1`; normal BSS holds `arr2`, `zero`, `skip`, and exported user pointer. State persists until map/skeleton teardown.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on `bpf_arena_htab.h` and arena address-space cast support.

## Risks and Edge Cases

Long bounded loops stress verifier loop handling and arena pointer casts. Userspace pointer exposure must use the correct cast direction.

## Test Signals

Expected signals are `skip=false` on supported targets, successful syscall program run, populated arena hash table, and usable `htab_for_user` pointer for harness validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab_asm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab_asm.c

## Purpose

Assembly-forced variant of `arena_htab.c`, reusing the same implementation while defining `BPF_ARENA_FORCE_ASM` and renaming the entry to `arena_htab_asm`. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Preprocessor aliases `BPF_ARENA_FORCE_ASM` and `arena_htab_llvm arena_htab_asm`, plus all APIs inherited from `arena_htab.c`.

## Control Flow

Compilation includes `arena_htab.c` with assembly forcing enabled, so runtime flow mirrors the hash-table arena test but exercises alternate code generation paths.

## State and Persistence Behavior

Same arena/hash-table state as `arena_htab.c` under renamed symbols.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on the included C file and assembler-compatible arena helper implementation.

## Risks and Edge Cases

Because this file includes another `.c`, source-level changes to `arena_htab.c` affect both variants. Macro aliasing must occur before include.

## Test Signals

Harness should see the same functional results as the LLVM variant while covering the forced-assembly path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_htab_asm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_list.c

## Purpose

BPF arena linked-list test. It allocates arena list nodes, pushes them into an arena list head, iterates/deletes them, and optionally tests behavior under RCU read lock. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `bpf_arena_alloc.h`, `bpf_arena_list.h`, `bpf_alloc()`, `list_add_head()`, `list_for_each_entry()`, `list_del()`, `bpf_rcu_read_lock/unlock` ksyms, arena globals, and syscall sections `arena_list_add`/`arena_list_del`.

## Control Flow

`arena_list_add()` sets `list_head` to `global_head`, allocates `cnt` nodes, increments globals, accumulates `arena_sum`, and inserts at head. `arena_list_del()` optionally enters RCU read-side critical section, iterates the list, sums values, deletes nodes, and updates counters/sums for userspace validation. Unsupported builds set `skip`.

## State and Persistence Behavior

Arena state includes nodes, list head, `arena_sum`, and `test_val`; BSS state includes `list_head`, `list_sum`, `cnt`, `skip`, `nonsleepable`, and `zero`.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on arena allocation/list helper headers and RCU kfunc availability.

## Risks and Edge Cases

Pointer address-space correctness and list mutation under optional non-sleepable/RCU context are the main risks. Missing address-space cast support turns the test into a skip.

## Test Signals

Expected userspace signals include skip gating, correct sums/counts after add/delete, and verifier acceptance of arena list operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_spin_lock.c

## Purpose

BPF arena spin-lock test program for TC context. It validates lock-protected critical section behavior and feature-gated skip values. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `bpf_arena_spin_lock.h`, TC section `prog`, globals `cs_count`, `test_skip`, `counter`, and `limit`.

## Control Flow

The TC program enters an arena spin-lock protected region when supported, increments counters up to the configured limit, and records critical-section activity. Compile-time/target feature checks set `test_skip` to communicate unsupported cases.

## State and Persistence Behavior

Arena map plus BSS globals carry counter/limit/skip state for harness checks. No durable state.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on arena spin lock helper definitions and TC program verifier support.

## Risks and Edge Cases

Lock semantics in BPF are verifier-sensitive. Unsupported compiler/architecture paths must skip rather than fail unexpectedly.

## Test Signals

Harness should see expected skip value or increasing `counter`/`cs_count` without verifier rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_strsearch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_strsearch.c

## Purpose

BPF arena string-search selftest using arena-resident patterns/test strings. It validates glob/string search helpers over a compact table of expected matches. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `bpf_arena_strsearch.h`, arena string constants, helper `test()`, syscall program `arena_strsearch`, and global `skip`.

## Control Flow

The program iterates encoded test cases, invokes the arena string-search helper for pattern/string pairs, compares against expected results, and records pass/fail state for userspace. Unsupported feature paths set `skip`.

## State and Persistence Behavior

Arena constants and BSS `skip`/result counters are transient skeleton state. The arena map holds searchable data.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on arena string-search helper macros and address-space support.

## Risks and Edge Cases

Glob escaping, NUL-terminated arena strings, and address-space casts are easy to break. The compact encoded table must remain aligned with parser expectations.

## Test Signals

Expected signal is no mismatch across the glob table, or `skip=true` if arena string search is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_strsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/async_stack_depth.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/async_stack_depth.c

## Purpose

Negative verifier tests for combined stack depth across normal pseudo-calls and asynchronous timer callbacks. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_HASH` holding `struct bpf_timer`, `bpf_timer_set_callback()`, noinline `timer_cb()`/`bad_timer_cb()`, TC sections annotated `__failure` and `__msg("combined stack size of 2 calls is")`.

## Control Flow

Both TC programs allocate a 256-byte stack buffer and look up a timer element. One calls a 256-byte callback directly and sets it as timer callback; the other sets a callback that uses 300 bytes and calls the first callback. Both are expected to fail verifier combined-stack checks.

## State and Persistence Behavior

Only the hash map/timer value and stack buffers are involved; programs should not load successfully.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on verifier support for async callback stack accounting and selftest expected-failure annotations.

## Risks and Edge Cases

Verifier diagnostic text is part of the contract. Stack-size calculations can shift if callback accounting changes.

## Test Signals

Expected verifier rejection with message containing `combined stack size of 2 calls is` for both programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/async_stack_depth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomic_bounds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomic_bounds.c

## Purpose

Verifier scalar-bounds regression for atomic fetch-add results. It checks whether the verifier can infer that a stack-local atomic fetch-add returns zero and therefore a `while (b)` loop is unreachable. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SEC("fentry/bpf_fentry_test1")`, `BPF_PROG(sub, int x)`, `__sync_fetch_and_add()` on a stack local, compile-time `ENABLE_ATOMICS_TESTS`, and global `skip_tests`.

## Control Flow

When atomics tests are enabled, the fentry program initializes `a` to zero, assigns `b = __sync_fetch_and_add(&a, 1)`, and contains a loop guarded by `b`. Correct verifier reasoning treats `b` as certainly zero, so the program loads. Without atomics support the harness sees `skip_tests=true`.

## State and Persistence Behavior

Only BSS skip/result globals are used. No maps are declared.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here.

## Risks and Edge Cases

Feature gating must match compiler/kernel atomic support; otherwise expected verifier behavior can become architecture-dependent.

## Test Signals

Harness observes `skip_tests` or successful load/run with expected atomic bounds behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomic_bounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomics.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomics.c

## Purpose

Non-arena BPF atomic operation test program. It exercises add/sub/and/or/xor/cmpxchg/xchg over global and stack values from raw tracepoint programs filtered by PID. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Raw tracepoint sections `add`, `sub`, `and`, `or`, `xor`, `cmpxchg`, `xchg`; GCC/C11 atomic builtins; globals such as `add64_value`, `cmpxchg64_result_succeed`, `process pid`; and `skip_tests` feature gating.

## Control Flow

Each raw tracepoint program returns unless current TGID matches `pid`. Enabled paths perform one atomic family and store old/new values in globals for userspace validation. Unsupported builds set `skip_tests`.

## State and Persistence Behavior

Global BSS/data variables hold operands and results. Stack-local atomic tests copy stack values into globals to verify side effects.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on raw tracepoint attach and BPF atomic instruction support.

## Risks and Edge Cases

Atomic codegen differs by compiler features; stack atomic operations and no-return atomic variants are verifier/JIT-sensitive.

## Test Signals

Expected old values, updated values, and stack copies for each atomic family, or a skip flag on unsupported builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/atomics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops.c

## Purpose

Negative/edge struct_ops object defining callbacks for two different test module ops structures, used to validate struct_ops attachment/type checking. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SEC("struct_ops/test_1")`, `SEC("struct_ops/test_2")`, `BPF_PROG()` callbacks, `.struct_ops.link` maps `testmod_1` and `testmod_2`, and test module headers.

## Control Flow

Two callbacks return 0. The object declares two struct_ops link instances referencing those callbacks, intentionally mixing different ops structures for loader/verifier validation.

## State and Persistence Behavior

Struct_ops link map definitions are the relevant state; there is no runtime mutable state.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on the BPF test module's struct_ops BTF types.

## Risks and Edge Cases

Availability of `bpf_testmod` and exact struct_ops type definitions controls load behavior. The file is intentionally named bad, so success/failure expectations live in the harness.

## Test Signals

Expected loader/verifier behavior for invalid or mixed struct_ops link definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops2.c

## Purpose

Minimal bad struct_ops program with no corresponding struct_ops map, used to ensure bare `struct_ops/foo` sections are rejected without attachment metadata. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SEC("struct_ops/foo") void foo(void)` and GPL license section.

## Control Flow

There is no meaningful runtime flow; the object is intended to fail at load/configuration because no struct_ops map provides attachment information.

## State and Persistence Behavior

No mutable state.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here.

## Risks and Edge Cases

If loader policy for unused struct_ops programs changes, expected failure text/status may need updates.

## Test Signals

Expected object load failure due to missing struct_ops map/attachment information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_local_storage_create.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_local_storage_create.c

## Purpose

Benchmark BPF program for local storage creation on task fork and socket creation paths. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_SK_STORAGE`, `BPF_MAP_TYPE_TASK_STORAGE`, `bpf_task_storage_get()`, `bpf_sk_storage_get()`, `BPF_LOCAL_STORAGE_GET_F_CREATE`, tracepoint BTF `sched_process_fork`, sleepable LSM `socket_post_create`, and counters `create_cnts`/`create_errs` gated by `bench_pid`.

## Control Flow

On fork, if parent TGID matches `bench_pid`, create task storage for the child and atomically increment success/error counters. On socket post-create, if current PID matches and `sock->sk` exists, create socket storage and update counters.

## State and Persistence Behavior

Persistent BPF local storage maps attach data to tasks/sockets for the life of those kernel objects. Global counters report benchmark outcomes.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It requires task and socket local storage support, tp_btf, and sleepable LSM attachment.

## Risks and Edge Cases

Benchmark results depend on workload PID filtering and object lifetime. Missing `sock->sk` is handled as a no-op.

## Test Signals

Counters should show storage creation counts/errors corresponding to benchmark-generated forks or sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_local_storage_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_sockmap_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_sockmap_prog.c

## Purpose

Benchmark/helper BPF programs for sockmap and sk_msg redirection throughput tests. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_SOCKMAP` maps `sock_map_rx`/`sock_map_tx`, `bpf_sk_redirect_map()`, `bpf_msg_redirect_map()`, SK_SKB parser/verdict sections, SK_MSG verdict sections, and globals `process_byte`, `verdict_dir`, `dropped`, `pkt_size`.

## Control Flow

The stream parser returns configured `pkt_size`. Verdict programs redirect to map index 1 using `verdict_dir`, count bytes processed, and increment `dropped` on `SK_DROP`. Pass variants only count bytes and return `SK_PASS`.

## State and Persistence Behavior

Sockmap contents are managed by userspace benchmark code. Global counters and configuration variables persist in BSS while the benchmark runs.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on sockmap/sk_skb/sk_msg program support and userspace populating maps/configuration.

## Risks and Edge Cases

Incorrect `verdict_dir` or missing map entries cause drops and skew benchmark results. Parser `pkt_size` controls stream framing and must match benchmark payloads.

## Test Signals

Benchmark harness observes byte counters, drop counter, and redirect/pass behavior under selected parser/verdict modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_sockmap_prog.c -->

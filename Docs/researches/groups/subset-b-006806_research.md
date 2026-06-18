# subset-b-006806 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_csum_diff.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_csum_diff.c

Purpose: table-driven verifier/runtime coverage for the `bpf_csum_diff()` helper through the `csum_diff_test` skeleton. It checks push, pull, replace/diff, and edge cases over 0, odd, aligned, and full 512-byte buffers with endian-specific expected values.

Important APIs/types/functions: `struct testcase` holds `to_buff`, `from_buff`, byte lengths, seed, and expected checksum. `trigger_csum_diff()` runs `compute_checksum` with `bpf_prog_test_run_opts()`. `test_csum_diff()` mutates skeleton rodata before load, populates BSS buffers after load, and validates `skel->bss->result`. `test_test_csum_diff()` exposes four subtests.

Control flow: each testcase opens a fresh skeleton, writes length constants into rodata, loads the program, copies test data to BSS, sets seed, invokes the BPF program once, and compares the helper result. Fresh skeletons are needed because rodata lengths are load-time constants.

State and persistence: no persistent external state. BSS and rodata are per-skeleton; checksum expectations are static in the C file.

Dependencies and integration: depends on `test_progs.h`, generated `csum_diff_test.skel.h`, libbpf test-run support, and byte-order macros. It integrates with the BPF selftest harness as `test_test_csum_diff`.

Risks: expected values are tightly coupled to helper folding semantics and host endian handling for odd lengths. A failed load short-circuits the current table and destroys only the current skeleton. Edge case with 512 bytes of zero `from_buff` and full length validates kernel behavior on large zero input.

Test signals: `ASSERT_OK_PTR`, `ASSERT_EQ(err, 0)`, and `ASSERT_EQ(got, result)` report load and checksum regressions per subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_csum_diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_dst_clear.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_dst_clear.c

Purpose: validates that a TCX-attached BPF program can observe and clear skb destination cache state on loopback UDP traffic.

Important APIs/types/functions: `test_dst_clear__open_and_load()`, `bpf_program__attach_tcx()`, `make_sockaddr()`, `sendto()`, and BSS flags `had_dst` and `dst_cleared`. Constants define loopback IPv4 address `1.0.0.1` and UDP port `7777`.

Control flow: load the skeleton, add the IPv4 address to `lo`, attach `dst_clear` to TCX on loopback, build a sockaddr, send one UDP datagram, then assert that BPF saw an existing dst and cleared it.

State and persistence: mutates the loopback address in the current network namespace and leaves cleanup to the wider namespace harness if any. Skeleton link ownership is stored in `skel->links.dst_clear` and destroyed with the skeleton.

Dependencies and integration: depends on TCX support, `if_nametoindex("lo")`, iproute2 via `SYS`, UDP sockets, and generated `test_dst_clear.skel.h`. The function name `test_ns_dst_clear` implies it is intended to run in an isolated netns selftest variant.

Risks: failure before namespace cleanup can leave the loopback alias. TCX availability and route-cache behavior are kernel-version sensitive. Requires sufficient privilege to modify addresses and attach TCX.

Test signals: asserts skeleton load, address setup, TCX link creation, sockaddr construction, exact send length, and final BSS booleans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_dst_clear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_global_funcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_global_funcs.c

Purpose: exercises global BPF function verification across many generated skeletons and verifies libbpf rewriting of `__arg_ctx`-annotated global-function arguments on kernels without native argument-context metadata.

Important APIs/types/functions: `RUN_TESTS(test_global_func*)` dispatches generated positive/negative skeleton tests. `subtest_ctx_arg_rewrite()` uses `btf__load_vmlinux_btf()`, `btf__find_by_name_kind()`, `bpf_prog_get_info_by_fd()`, `btf__load_from_kernel_by_id()`, and `check_ctx_arg_type()`.

Control flow: run the numbered global-function skeleton suites, then optionally run `ctx_arg_rewrite`. The rewrite subtest skips on kernels with native `bpf_subprog_arg_info`, enables only `arg_tag_ctx_perf`, loads the skeleton, retrieves function-info records, loads the program BTF by id, and validates that subprogram arguments tagged as context were rewritten to pointers to `struct bpf_perf_event_data`.

State and persistence: no durable state. It allocates kernel and program BTF handles and frees them. It reads program metadata from the loaded BPF object.

Dependencies and integration: depends on generated `test_global_func*.skel.h`, `test_global_func_ctx_args.skel.h`, libbpf internal helpers, BTF helpers, and kernel BTF availability. Integrated through `test_test_global_funcs`.

Risks: the ctx rewrite subtest intentionally skips once the kernel exposes native argument metadata, so coverage shifts with kernel capability. It assumes three function-info records and exact subprogram names. BTF dump string matching can be brittle if formatting changes.

Test signals: generated suites report through `RUN_TESTS`; rewrite checks kernel BTF load, skeleton load, program info count, BTF kinds, subprogram names, argument count, and context struct type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_global_funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ima.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ima.c

Purpose: validates BPF IMA helpers and LSM hook behavior by measuring files under a temporary IMA setup, consuming hashes from a ring buffer, and checking fresh versus stale digest behavior plus deny behavior.

Important APIs/types/functions: `_run_measured_process()` forks and execs `./ima_setup.sh` commands; `process_sample()` collects up to `MAX_SAMPLES` 64-bit hashes from ringbuf records; `test_init()` resets BSS feature flags; `test_test_ima()` orchestrates six scenarios. It uses `ima__open_and_load()`, `ring_buffer__new()`, `ima__attach()`, `ring_buffer__consume()`, `mkdtemp()`, and `system()`.

Control flow: create and attach the IMA skeleton, prepare a measured directory with `ima_setup.sh setup`, then run tests for `bpf_ima_inode_hash`, `bpf_ima_file_hash`, stale inode hash after binary modification, fresh file hash after exec hook, kernel-read-file policy loading, and kernel-read-file denial. Cleanup invokes `ima_setup.sh cleanup`.

State and persistence: creates `/tmp/ima_measuredXXXXXX`, mutates test binaries/policies through the setup script, stores monitored child pid and enable flags in BSS, and uses process-global sample arrays. Cleanup is best-effort via shell script and skeleton/ringbuf destruction.

Dependencies and integration: depends on IMA kernel configuration, BPF LSM hooks, ring buffer map, `ima_setup.sh`, `/bin/true`, fork/exec/wait, and generated `ima.skel.h`. Integrated as `test_test_ima`.

Risks: highly environment-sensitive: IMA policy, helper availability, privileges, script behavior, and commit-dependent stale digest semantics can affect sample counts. Ring buffer capacity is only four samples, matching current scenarios. Early failures before `close_clean` may leave temporary measurement artifacts.

Test signals: asserts exact or minimum sample counts, nonzero hashes, equality/inequality against the saved `/bin/true` sample, expected command failures for deny mode, and zero samples after denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ima.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ldsx_insn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ldsx_insn.c

Purpose: verifies signed load-extension BPF instructions for map values, probed memory, cgroup socket context members, and narrow skb context fields.

Important APIs/types/functions: `test_map_val_and_probed_memory()`, `test_ctx_member_sign_ext()`, `test_ctx_member_narrow_sign_ext()`, `test__join_cgroup()`, `trigger_module_test_read()`, `bpf_program__attach_cgroup()`, and `bpf_prog_test_run_opts()`. It uses generated `test_ldsx_insn.skel.h`.

Control flow: each subtest opens a skeleton, skips if `skel->rodata->skip` is set, enables only the relevant programs, loads, and triggers execution through either bpf_testmod read, `getsockopt()` on a socket in a cgroup, or TC program test-run over `pkt_v4`. BSS fields record sign-extended results.

State and persistence: transient cgroup `/ldsx_test`, a socket fd, skeleton links, and BSS result fields. All handles are closed/destroyed in local cleanup paths.

Dependencies and integration: depends on BPF test module trigger support, cgroup setup helpers, networking helpers for `pkt_v4`, and kernel support for LDXSX instructions. Integrated as `test_ldsx_insn`.

Risks: skip gating hides unsupported-kernel failures. The module-read path requires bpf_testmod. Sign-extension assertions are sensitive to verifier/JIT codegen and context field widths.

Test signals: checks BSS `done*`, return flags, `int_member == -1`, cgroup `optlen`/`retval == -1`, and TC `set_mark == -2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ldsx_insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_local_storage.c

Purpose: validates task, inode, and socket local-storage maps through both direct syscalls and BPF LSM-triggered runtime behavior.

Important APIs/types/functions: `run_self_unlink()` forks a copied `rm` binary that attempts to delete itself; `check_syscall_operations()` performs lookup/update/lookup/delete/lookup on a local-storage map keyed by fd; `test_test_local_storage()` loads and attaches `local_storage`.

Control flow: load/attach skeleton, open current pidfd and validate task storage syscalls, create a temp directory and copy `/bin/rm`, validate inode storage syscalls on the copied executable, execute self-unlink and expect `EPERM`, rename the file to exercise null-inode LSM path, start an IPv6 server socket, validate socket storage syscalls, then cleanup.

State and persistence: creates `/tmp/local_storageXXXXXX`, copies/removes an executable, opens task/inode/socket fds, sets `skel->bss->monitored_pid`, and observes result fields in skeleton data. Temp directory removal is best-effort.

Dependencies and integration: depends on generated `local_storage.skel.h`, task local storage helpers, `pidfd_open`, LSM attachment, `/bin/rm`, shell `cp`/`mv`/`rm`, and network helper `start_server`.

Risks: requires privileges and kernel support for local-storage maps and BPF LSM. Shell commands and hard-coded `/bin/rm` path are environment-sensitive. Early failures may leave temp files until the cleanup label is reached.

Test signals: syscall operation assertions check `-ENOENT`, update success, value round-trip, delete success, and post-delete miss; runtime signals check task/inode/socket BPF result fields and expected self-unlink `EPERM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_lsm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_lsm.c

Purpose: tests BPF LSM attachment, enforcement, repeated detach/attach, copy-from-user edge handling, and tail-call program-array behavior for LSM programs.

Important APIs/types/functions: `stack_mprotect()`, `exec_cmd()`, `test_lsm()`, `test_lsm_basic()`, `test_lsm_tailcall()`, `lsm__attach()`, `lsm__detach()`, `bpf_program__attach()`, and program-array updates on `jmp_table`.

Control flow: the basic subtest loads `lsm`, attaches all links, verifies a second direct attach of an already linked program fails, forks/execs `true` and checks `bprm_count`, sets monitored pid and attempts executable stack `mprotect()` expecting `EPERM`, triggers `setdomainname` calls with invalid pointers/lengths to exercise copy paths, detaches, resets counters, and repeats. Tailcall subtest loads `lsm_tailcall`, stores two LSM program fds into the same jump-table slot to validate update behavior.

State and persistence: transient child process, stack memory protection attempt, BSS counters and monitored pid. No durable state.

Dependencies and integration: depends on BPF LSM support, generated skeletons, `true` executable, syscall availability, and program-array support. Integrated as `test_test_lsm`.

Risks: LSM stacking/configuration and process privilege can change attach or enforcement behavior. `errno` after `mprotect` is part of the expected signal. Tailcall subtest uses `CHECK_FAIL(!err)` for the first update, meaning it expects that update to fail; that is intentional coverage but easy to misread.

Test signals: validates attach success, duplicate attach rejection, `bprm_count`, `mprotect_count`, `copy_test == 3`, second attach cycle, and jump-table update outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_mmap_inner_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_mmap_inner_array.c

Purpose: verifies that an inner array map can be mmaped from user space and later referenced through an outer map by a BPF program.

Important APIs/types/functions: generated `mmap_inner_array` skeleton, `mmap()` on `inner_array` fd, `mmap_inner_array__attach()`, `bpf_map__update_elem()` on `outer_map`, BSS flags `pid_match`, `outer_map_match`, `done`, and data `match_value`.

Control flow: load skeleton, mmap one page from the inner array map, attach BPF, set target pid, wait briefly and confirm pid matched but outer map not yet configured and mmaped value remains zero. Then insert the inner-map fd into the outer map keyed by pid, wait again, and confirm the program matched the outer map and wrote the expected value.

State and persistence: one shared mmap region and skeleton BSS/data fields. The mmap is unmapped and skeleton destroyed.

Dependencies and integration: requires mmapable BPF array map semantics, map-in-map update support, and generated skeleton. Integrated as `test_mmap_inner_array`.

Risks: timing uses `usleep(1)` and assumes the attached program is triggered often enough. Map-in-map fd lifetime and mmap visibility are the main kernel contracts under test.

Test signals: before and after assertions distinguish pid match, outer map match, completion, and exact mmaped value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_mmap_inner_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_overhead.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_overhead.c

Purpose: measures relative event-processing overhead for kprobe, kretprobe, raw tracepoint, fentry, and fexit BPF hooks on task rename events.

Important APIs/types/functions: `test_task_rename()` repeatedly writes to `/proc/self/comm`, `setaffinity()` pins CPU 0, `bpf_object__open_file("./test_overhead.bpf.o")`, program lookup by names `prog1` through `prog5`, and attach helpers for kprobe/raw tracepoint/fentry/fexit.

Control flow: preserve current task comm, open and load the BPF object, find all programs, pin affinity, run a baseline loop, attach each hook type one at a time, run the same rename loop, print K events/sec, destroy the link, restore comm, and close object.

State and persistence: mutates process comm many times and restores the original 16-byte comm at cleanup. No BPF map state is inspected.

Dependencies and integration: depends on `test_overhead.bpf.o` in the working directory, kernel symbol `__set_task_comm`, raw tracepoint `task_rename`, fentry/fexit BTF support, `/proc/self/comm`, and scheduling affinity APIs.

Risks: this is a performance signal, not a deterministic correctness test. CPU frequency, scheduler noise, missing BTF, or symbol naming can alter results. A cleanup path restores comm but does not restore CPU affinity.

Test signals: load/attach assertions catch functional regressions; printed throughput lines are the primary measurement output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_overhead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_profiler.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_profiler.c

Purpose: smoke-tests three profiler skeleton variants by attaching them and invoking their raw tracepoint program through `bpf_prog_test_run_opts()`.

Important APIs/types/functions: `sanity_run()` supplies a three-element `__u64` context, runs a BPF program fd, and expects both syscall success and nonzero test-run retval. The main function loads/attaches `profiler1`, `profiler2`, and `profiler3`.

Control flow: open/load profiler1, attach, sanity-run `raw_tracepoint__sched_process_exec`; repeat for profiler2 and profiler3; destroy all skeletons in cleanup.

State and persistence: no durable state. Each skeleton may install tracepoint links until destroyed.

Dependencies and integration: depends on `progs/profiler.h`, generated profiler skeletons, raw tracepoint test-run support, and sched process exec tracepoint compatibility.

Risks: test-run context shape must match the BPF program expectations. Failures in the first profiler skip later variants through shared cleanup.

Test signals: skeleton load, attach status, test-run syscall status, and retval validation for each profiler variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_profiler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_skb_pkt_end.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_skb_pkt_end.c

Purpose: verifies skb packet-end handling when `bpf_prog_test_run_opts()` is run with checksum-complete skb test flags.

Important APIs/types/functions: generated `skb_pkt_end` skeleton, `sanity_run()`, `pkt_v4` from network helpers, `BPF_F_TEST_SKB_CHECKSUM_COMPLETE`, and expected retval `123`.

Control flow: load and attach skeleton, test-run `main_prog` with IPv4 packet bytes and checksum-complete flag, assert syscall success and retval.

State and persistence: no persistent state; skeleton link is destroyed at cleanup.

Dependencies and integration: depends on network helper packet fixture, generated skeleton, and kernel support for skb checksum-complete test-run mode. Integrated as `test_test_skb_pkt_end`.

Risks: primarily sensitive to verifier/JIT packet-boundary logic and test-run flag semantics. Attach is performed even though the substantive signal comes from direct test-run.

Test signals: skeleton load/attach and exact test-run retval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_skb_pkt_end.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_strncmp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_strncmp.c

Purpose: validates accepted and rejected uses of the BPF `bpf_strncmp()` helper, including return ordering semantics and verifier constraints around constant size and read-only null-terminated target strings.

Important APIs/types/functions: `trigger_strncmp()` waits for the attached program to update `cmp_ret` and normalizes sign; `strncmp_full_str_cmp()` mutates every character against rodata `target`; `test_strncmp_ret()` runs positive comparisons; three negative subtests enable bad programs and expect load failure.

Control flow: positive path opens skeleton, autoloads `do_strncmp`, loads/attaches, sets `target_pid`, checks empty string, equal string, non-null-terminated local string, and per-position less/greater comparisons. Negative paths open new skeletons, autoload one invalid program each, load, and expect an error.

State and persistence: BSS string buffer, target pid, and comparison result are transient per skeleton. Uses rodata target as immutable comparison string.

Dependencies and integration: depends on generated `strncmp_test.skel.h`, helper availability, and the attach trigger used by the BPF program. Integrated as `test_test_strncmp`.

Risks: `usleep(1)` assumes the program has run after BSS mutation. Negative verifier diagnostics are not checked, only load failure. String array sizes and null termination are central to correctness.

Test signals: comparison result assertions for many character positions and `ASSERT_ERR` load failures for non-constant size, writable target, and non-null-terminated target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_strncmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_assoc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_assoc.c

Purpose: tests explicit association between BPF programs and struct_ops maps, reuse of operator programs, and struct_ops calls from timer callbacks with and without a user reference.

Important APIs/types/functions: `bpf_program__assoc_struct_ops()`, skeleton attach helpers, `bpf_prog_test_run_opts()`, `bpf_map__attach_struct_ops()`, `sched_yield()`, and BSS fields such as `test_err_a`, `test_err_b`, `timer_cb_run`, `timer_test_1_ret`, and `timer_ns`.

Control flow: `test_st_ops_assoc()` verifies direct struct_ops callback association is rejected, associates syscall/tracing programs with maps A/B, rejects reassociation, attaches, triggers tracing through `sys_gettid()`, then test-runs syscall programs. Reuse subtest associates two syscall programs and checks both. Timer subtests run a syscall program that calls a kfunc and schedules a timer callback; the no-user-reference variant destroys link and closes fds before the delayed callback runs.

State and persistence: struct_ops links, map/program fds, timer callback state, and BSS error/result fields. No durable state beyond loaded BPF objects.

Dependencies and integration: depends on generated struct_ops skeletons, kernel kfuncs for multi struct_ops testing, timers, and bpf_testmod-style struct_ops support. Integrated as `test_struct_ops_assoc`.

Risks: busy-wait loops rely on timer callback completion. Closing fds intentionally tests lifetime/refcount behavior and could expose use-after-free regressions. Association APIs are libbpf-sensitive.

Test signals: expected success/error from association calls, attach success, zero error fields, syscall test-run success, timer return `1234` with reference and `-1` after dropped user reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_assoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_id_ops_mapping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_id_ops_mapping.c

Purpose: verifies mapping from struct_ops map ids to the correct operations implementation across two independently loaded skeletons.

Important APIs/types/functions: generated `struct_ops_id_ops_mapping1` and `struct_ops_id_ops_mapping2`, `bpf_map_get_info_by_fd()`, `bpf_prog_test_run_opts()`, and BSS fields `st_ops_id`, `test_pid`, and `test_err`.

Control flow: load both skeletons, query each struct_ops map id, store each id in its own BSS, attach both skeletons, trigger tracing programs through `sys_gettid()`, run each syscall program directly, then require both `test_err` fields to be zero.

State and persistence: transient map ids and BSS pid/error fields. Skeleton destruction releases links and maps.

Dependencies and integration: depends on struct_ops map id reporting and generated skeletons. Integrated as `test_struct_ops_id_ops_mapping`.

Risks: assumes map info ids are stable while skeletons are alive and that simultaneous attachments do not interfere. Failures could indicate wrong id-to-ops lookup or cross-object confusion.

Test signals: map info query success, attach success for both objects, syscall test-run success, and zero error fields in both skeletons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_id_ops_mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_kptr_return.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_kptr_return.c

Purpose: dispatches positive and negative verifier coverage for struct_ops callbacks returning kernel pointers.

Important APIs/types/functions: `RUN_TESTS()` over `struct_ops_kptr_return` plus failure skeletons for wrong type, invalid scalar, nonzero offset, and local kptr return.

Control flow: the selftest harness opens/loads/runs each generated skeleton according to its embedded expectations. This C file acts as the manifest tying those skeletons into the suite.

State and persistence: no state in the harness file; all test state is inside generated skeletons and their BPF objects.

Dependencies and integration: depends on generated skeletons and struct_ops kptr verifier support. Integrated as `test_struct_ops_kptr_return`.

Risks: because this file delegates entirely to `RUN_TESTS`, detailed semantics live in the BPF program sources. Missing or misnamed skeletons break build/runtime registration.

Test signals: pass/fail comes from the generated skeleton test macro, especially expected load rejection for invalid kptr return shapes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_kptr_return.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_maybe_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_maybe_null.c

Purpose: validates verifier handling of nullable struct_ops pointer arguments: checked access is accepted and unchecked access is rejected.

Important APIs/types/functions: generated `struct_ops_maybe_null` and `struct_ops_maybe_null_fail` skeletons, `open_and_load()` helpers, `ASSERT_OK_PTR`, and `ASSERT_ERR_PTR`.

Control flow: subtest `maybe_null` loads the valid object and destroys it. Subtest `maybe_null_fail` attempts to load the invalid object and returns successfully only if load produces an error pointer.

State and persistence: none beyond transient skeleton handles.

Dependencies and integration: depends on struct_ops maybe-null verifier annotations and separate BPF objects to isolate load-time verification. Integrated as `test_struct_ops_maybe_null`.

Risks: does not attach or execute programs; all signal is verifier load behavior. If verifier diagnostics change but accept/reject remains stable, test still passes.

Test signals: load success for the checked program and load failure for unchecked nullable access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_maybe_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_module.c

Purpose: comprehensive module-backed struct_ops coverage using bpf_testmod: map BTF ownership, callback replacement, zeroed-field compatibility, incompatible signatures, nulling callbacks, forgotten callback diagnostics, link detach notification, and unsupported-ops delegation.

Important APIs/types/functions: `check_map_info()` verifies `btf_vmlinux_id` points to BTF object named `bpf_testmod`; `attach_ops_and_check()` attaches a struct_ops map and checks BSS callback results; `bpf_map__attach_struct_ops()`, `bpf_map_get_info_by_fd()`, `bpf_btf_get_fd_by_id()`, `bpf_btf_get_info_by_fd()`, libbpf log capture, `bpf_link__detach()`, and `epoll_wait()` are central.

Control flow: `test_struct_ops_load()` customizes struct_ops fields, disables unused autoload, loads, checks map info, and attaches two maps with expected results. `test_struct_ops_not_zeroed()` verifies zero-valued unknown fields are accepted while nonzero unknown values or non-null unknown ops are rejected. `test_struct_ops_incompatible()` loads and attaches a map whose program signature is intentionally left for kernel verifier enforcement. Other subtests null out supported callbacks, validate a useful libbpf error for an unreferenced struct_ops program then programmatically reference it, and detach a link while waiting for `EPOLLHUP`. `serial_test_struct_ops_module()` runs these serially and also runs `unsupported_ops`.

State and persistence: attaches struct_ops links to bpf_testmod and inspects skeleton BSS results. Epoll monitors a link fd. Log capture allocates a string that is freed. All skeletons/links/fds are destroyed or closed in cleanup.

Dependencies and integration: depends on bpf_testmod being loaded with BTF, generated skeletons, struct_ops link fds, epoll, libbpf log capture, and serial execution to avoid module-global interference. Entry point is `serial_test_struct_ops_module`, not a plain `test_` function.

Risks: kernel module availability and BTF naming are hard requirements. Unknown-field compatibility behavior is libbpf-version sensitive. Link-detach notification depends on fd lifetime and epoll semantics.

Test signals: map BTF name equality, callback result values (`0xdeadbeef`, `20`, `12`), accepted/rejected loads, libbpf diagnostic substring, detach success, single `EPOLLHUP`, and `RUN_TESTS(unsupported_ops)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_args.c

Purpose: registers the generated struct_ops multi-argument callback selftest with the harness.

Important APIs/types/functions: includes `struct_ops_multi_args.skel.h` and calls `RUN_TESTS(struct_ops_multi_args)`.

Control flow: all open/load/attach/run expectations are delegated to the generated skeleton test macro.

State and persistence: none in this wrapper.

Dependencies and integration: depends on generated skeleton and struct_ops support for callbacks with multiple arguments. Integrated as `test_struct_ops_multi_args`.

Risks: the wrapper provides no local diagnostics beyond the generated test macro; behavioral details must be read from the paired BPF source.

Test signals: `RUN_TESTS` result for the skeleton.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_pages.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_pages.c

Purpose: verifies struct_ops trampoline allocation/attachment when callbacks span more than one page of generated trampoline code.

Important APIs/types/functions: generated `struct_ops_multi_pages` skeleton, `bpf_map__attach_struct_ops()`, and `bpf_link__destroy()`.

Control flow: open/load skeleton, attach `skel->maps.multi_pages`, assert link creation, destroy link and skeleton.

State and persistence: transient struct_ops link only.

Dependencies and integration: depends on architecture/kernel trampoline allocation behavior and generated large callback set. Integrated as subtest `multi_pages`.

Risks: comment notes the page-size condition is at least true for x86; coverage may be weaker or different on other architectures. It tests attach success, not callback execution results.

Test signals: skeleton load and struct_ops attach success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_multi_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_no_cfi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_no_cfi.c

Purpose: loads a kernel module that self-tests struct_ops registration with and without CFI stubs, ensuring unsupported no-CFI registration fails while the module as a whole succeeds only if expected outcomes occur.

Important APIs/types/functions: `open("bpf_test_no_cfi.ko")`, `finit_module()`, `delete_module("bpf_test_no_cfi")`, and `testing_helpers.h`.

Control flow: open module file, call `finit_module`, close fd, then delete the module. The module's init path performs the actual registration checks.

State and persistence: temporarily loads kernel module `bpf_test_no_cfi`; removes it at end if load succeeded.

Dependencies and integration: requires module file in working directory, CAP_SYS_MODULE, loadable module support, and struct_ops CFI registration code. Integrated as subtest `load_bpf_test_no_cfi`.

Risks: can leave a module loaded if `delete_module` fails. Will fail in lockdown or module-disabled environments. Most logic lives inside the module, not visible here.

Test signals: successful module open, `finit_module`, and `delete_module`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_no_cfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_refcounted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_refcounted.c

Purpose: dispatches struct_ops refcounted-object verifier coverage, including valid handling and expected failures for reference leaks, global subprogram use, and tail-call use.

Important APIs/types/functions: `RUN_TESTS()` over `struct_ops_refcounted` and three failure skeletons.

Control flow: sequentially runs generated skeleton tests; expected accept/reject behavior is encoded in those skeletons/BPF programs.

State and persistence: none in wrapper.

Dependencies and integration: depends on generated skeletons and kernel verifier support for refcounted kptr semantics in struct_ops. Integrated as `test_struct_ops_refcounted`.

Risks: wrapper has no additional environment setup; all detail is in paired BPF sources. Missing negative coverage would surface as unexpected `RUN_TESTS` failure.

Test signals: generated tests for successful load and rejected invalid refcount patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_struct_ops_refcounted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_sysctl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_sysctl.c

Purpose: table-driven cgroup/sysctl BPF verifier and runtime suite covering attach-type validation, read/write allow/deny, context field access, helper behavior, file-position changes, value reads/writes, and object-file based programs.

Important APIs/types/functions: `struct sysctl_test` describes inline instructions or `prog_file`, attach type, `/proc/sys` target, open mode, expected operation result, and optional fixup. `probe_prog_length()`, `fixup_sysctl_value()`, `load_sysctl_prog_insns()`, `load_sysctl_prog_file()`, `access_sysctl()`, `run_test_case()`, and `run_tests()` implement execution. It uses `bpf_prog_load()`, `bpf_prog_test_load()`, `bpf_prog_attach()`, `bpf_prog_detach()`, and cgroup helpers.

Control flow: `test_sysctl()` creates and joins cgroup `/foo`, then iterates the large static `tests[]` array. Each case builds `/proc/sys/<sysctl>`, loads either raw BPF instructions or a BPF object, optionally patches a `BPF_LD_IMM64` with the live sysctl value, attaches to the cgroup, reads or writes the sysctl, and compares the observed result with `LOAD_REJECT`, `ATTACH_REJECT`, `OP_EPERM`, or `SUCCESS`.

State and persistence: creates a cgroup test environment, attaches one program at a time, opens and may write selected sysctls such as `kernel/domainname`, closes BPF objects and fds per case, and cleans the cgroup environment at end. Some tests rely on default or current sysctl values.

Dependencies and integration: depends on `test_progs.h`, `cgroup_helpers.h`, raw BPF instruction macros, cgroup sysctl program type, procfs sysctls, and object files referenced by `prog_file` cases. Integrated as `test_sysctl`.

Risks: large inline instruction table is brittle to helper ABI/verifier changes. Some sysctls may be absent, read-only, or policy-restricted in unusual environments. `FIXUP_SYSCTL_VALUE` cases depend on live procfs contents and BPF instruction position. Cleanup detaches best-effort without checking detach return.

Test signals: per-case `[PASS]/[FAIL]` printing, detailed verifier log on unexpected load failure, expected errno `EPERM` for operation denial, old-value string comparisons, and final summary requiring zero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_local_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_local_data.c

Purpose: tests the userspace task-local-data helper library and BPF-side reads under multithreaded isolation, concurrent key creation, and variable dynamic-data capacity.

Important APIs/types/functions: `TLD_DEFINE_KEY`, `tld_create_key()`, `tld_get_data()`, `tld_free()`, internal `tld_meta_p`, `reset_tld()`, generated `test_task_local_data` skeleton, and BPF program `task_main`.

Control flow: basic subtest resets metadata, creates static/dynamic keys, verifies `E2BIG`, `EEXIST`, and `ENOSPC`, then starts 32 threads. Each thread writes thread-specific values, serializes BPF program test-run through `global_mutex`, checks BPF-observed globals, mutates values, and repeats. Race subtest repeatedly starts many threads that create valid and invalid keys concurrently, writes unique values to all keys, checks no overlap, and runs BPF. Dynamic-size subtests reset available size to 64 or 0, fill as many int keys as allowed, expect overflow, verify values, and ensure static key remains readable by BPF.

State and persistence: intentionally mutates library-global metadata `tld_meta_p`, process thread-local data, and skeleton BSS. `reset_tld()` is safe only because subtests are sequential. Allocated key arrays are freed, and `tld_free()` clears library state.

Dependencies and integration: depends on `task_local_data.h`, pthreads, BTF headers, generated skeleton, page size, and BPF map test-run support. Integrated as `test_task_local_data`.

Risks: directly modifying library internals is test-only and fragile. Thread array joins can join uninitialized entries if thread creation fails early. Race loops are timing-sensitive but repeated 100 times to amplify bugs.

Test signals: key-creation errno assertions, per-thread BPF/global value equality, no overlap checks, race return codes, `task_main` retval, dynamic overflow `-E2BIG`, and static-key readback `0xdeadbeef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_local_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_work.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_work.c

Purpose: validates BPF task-work scheduling from perf-event programs across hash, array, and LRU maps, and dispatches negative verifier tests.

Important APIs/types/functions: `perf_event_open()`, `struct elem` with `struct bpf_task_work`, `verify_map()`, `task_work_run()`, generated `task_work` and `task_work_fail` skeletons, `bpf_program__attach_perf_event()`, and map iteration via `bpf_map__lookup_elem()`.

Control flow: `task_work_run()` creates a pipe and child process, blocks the child until BPF is attached, opens skeleton with only one target program autoloaded, stores a userspace string pointer in BSS, loads, opens a hardware CPU-cycles perf event for the child, attaches, releases the child, waits for samples/exit, finds the target map, and verifies at least one map value contains `"hello world"`. Main runs hash/array/LRU variants and `RUN_TESTS(task_work_fail)`.

State and persistence: transient child process, pipe fds, perf event/link ownership, BPF maps with task-work entries, and userspace pointer in BSS. Cleanup unblocks/waits for child if needed.

Dependencies and integration: depends on perf hardware event support, task-work kfunc/helper support, generated skeletons, and ptr-to-user string handling in the BPF program. Integrated as `test_task_work`.

Risks: skips when `PERF_COUNT_HW_CPU_CYCLES` is unsupported. Sampling can be nondeterministic; child loop attempts to generate enough cycles. User pointer lifetime must outlive BPF use.

Test signals: pipe/fork/load/attach assertions, optional skip on unsupported perf, map verification that processed entries have expected data and at least one value was processed, plus negative `task_work_fail` skeleton results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_task_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_edt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_edt.c

Purpose: end-to-end test for BPF-based Earliest Departure Time flow shaping by measuring TCP transfer rate through a TC program.

Important APIs/types/functions: netns helpers, `tc_prog_attach()`, `test_tc_edt` skeleton, `start_server()`, `connect_to_fd()`, `send_recv_data()`, `get_time_ns()`, and BSS `target_rate`. Constants set 5 Mbps target, 1 MB transfer, and 2 percent acceptable error.

Control flow: load skeleton, create client/server namespaces with veth pair, configure IPv4 addresses, add `fq` qdisc on server veth, attach TC program to server veth, write target rate into BSS, start a server in server namespace, connect from client namespace, transfer bytes, compute Mbps from elapsed time, and assert error threshold.

State and persistence: creates two named netns, veth pair, qdisc, TC attachment, sockets, and BSS rate. Cleanup removes namespaces after run; early setup failures remove partial namespaces.

Dependencies and integration: requires iproute2, fq qdisc, TC attach helpers, network privileges, and timing stability. Integrated as `test_tc_edt`.

Risks: performance/timing tests are noisy under CPU contention or virtualized networking. Cleanup is skipped if setup fails after skeleton load because `test_tc_edt()` returns early without destroying the skeleton in that path. Rate computation assumes byte/usec conversion matches `TARGET_RATE_MBPS`.

Test signals: namespace/network setup assertions, server/client fd assertions, transfer success, and `ASSERT_LE(rate_error, RATE_ERROR_PERCENT)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_edt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_tunnel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_tunnel.c

Purpose: end-to-end TC tunnel suite comparing BPF encapsulation and decapsulation against kernel tunnel decapsulation for many IPv4/IPv6, Ethernet, MPLS, GRE, VXLAN, IPIP, SIT, UDP/FOU, and GSO variants.

Important APIs/types/functions: `struct subtest_cfg` describes tunnel type, iproute type, MAC mode, IP protocol, FOU/MPLS/GSO flags, addresses, program fds, and server fd. Helpers include `set_subtest_progs()`, `run_server()`, `send_and_test_data()`, `configure_kernel_decapsulation()`, `configure_ebpf_decapsulation()`, `setup()`, `subtest_setup()`, and `subtest_cleanup()`. Uses generated `test_tc_tunnel.skel.h` and `tc_prog_attach()`.

Control flow: global setup creates client/server netns, veth pair, and random tx buffer. Each config builds a subtest name, resolves BPF encap/decap program fds, configures veth addresses/routes, starts a TCP server, verifies plain connectivity, attaches BPF encap to client egress and expects connectivity to require decap, optionally configures a kernel tunnel device for decap and verifies traffic, then replaces/removes it with BPF decap on server ingress and verifies traffic again. Cleanup removes qdiscs, addresses, kernel tunnels, FOU ports, MPLS routes, and namespaces.

State and persistence: creates two netns, veth devices, `testtun0`, FOU ports, MPLS sysctls/routes, qdiscs, sockets, and BPF TC links. Random tx data is process-global. Cleanup is substantial and mostly best-effort.

Dependencies and integration: requires iproute2 tunnel support, ethtool, TC, TCP sockets, network privileges, BPF TC programs, optional MPLS and FOU kernel support, and generated skeleton. Integrated as `test_tc_tunnel`.

Risks: broad environment surface and many kernel modules/features. Some configs set `expect_kern_decap_failure` and skip kernel decap assertions. GSO path sends 2000 bytes but checks only default receive size, matching current helper behavior. Failures can leave netns/tunnel state if cleanup is bypassed before global cleanup.

Test signals: per-subtest connectivity assertions for plain, kernel-decap, and BPF-decap paths; exact received data comparisons; setup/attach command assertions; and cleanup after each subtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tc_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tunnel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tunnel.c

Purpose: broad end-to-end tunnel metadata selftest for BPF tunnel helpers over VXLAN, IPv6 VXLAN, IPIP/FOU/GUE, XFRM, GRE/GRETAP, IP6GRE/IP6GRETAP, ERSPAN/IP6ERSPAN, Geneve/IP6Geneve, and IP6TNL.

Important APIs/types/functions: topology helpers `config_device()` and `cleanup()`, tunnel add/delete helpers, `tc_prog_attach()`, `bpf_xdp_attach()` for XFRM, map `local_ip_map`, ping helpers, and generated `test_tunnel_kern.skel.h`. `RUN_TEST` wraps per-subtest network setup/test/cleanup. `test_tunnel()` runs all tests in a pthread to isolate namespace mount changes from `open_netns()`.

Control flow: each subtest creates base netns/veth topology, adds a specific tunnel pair with one native tunnel in `at_ns0` and one metadata/external tunnel in root, loads BPF programs that set/get tunnel metadata, attaches them to tunnel or veth TC/XDP hooks, optionally updates maps or XFRM state, then pings overlay/underlay addresses to validate encapsulation and decapsulation. Cleanup deletes tunnel devices and netns for each subtest.

State and persistence: creates namespace `at_ns0`, veth pair, many named tunnel devices, FOU ports, XFRM states/policies, IPv4/IPv6 addresses, routes, neighbor entries, and BPF links. Cleanup is repeated per subtest and uses `SYS_NOFAIL`.

Dependencies and integration: depends on many kernel tunnel drivers, XFRM, XDP attach, TC, iproute2, ping commands, generated skeleton, and privilege to modify network namespaces. Integrated as `test_tunnel`.

Risks: very environment-sensitive, especially module availability and IPv6/DAD timing. Cleanup is best-effort and may leave XFRM or tunnel state if command behavior changes. `ping6_dev1()` calls `test_ping(AF_INET, IP6_ADDR_TUNL_DEV1)`, which appears suspicious because it passes an IPv6 address with `AF_INET`.

Test signals: setup command assertions, BPF attach assertions, ping command success, XFRM BSS fields (`reqid`, `spi`, `remote_ip`, `replay_window`), and per-subtest harness assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_veristat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_veristat.c

Purpose: black-box tests for the `veristat` command-line tool's `-G` global-variable override parser over scalar, enum, nested struct/union, array, matrix, file-based, and error cases.

Important APIs/types/functions: `struct fixture` holds temp output file, buffer, and veristat path; `init_fixture()` locates `./veristat` or `../veristat`, creates a temp file, and allocates a 1 MB output buffer; `__CHECK_STR` validates expected substrings. Tests invoke `SYS` or `SYS_FAIL`.

Control flow: success test runs `veristat set_global_vars.bpf.o` with many `-G` assignments and checks verbose output for resolved values. File-based test writes assignments to a temp file and passes `-G @file`. Failure tests check out-of-range scalar, pointer array unsupported, array index out-of-bounds, enum index resolution failure, array index on non-array, and missing array index for array/composite traversal.

State and persistence: creates temp files in `/tmp`, reads command output into fixture buffers, and removes temp files during teardown. Does not load BPF into kernel directly; invokes external binary.

Dependencies and integration: depends on `veristat` binary, `set_global_vars.bpf.o`, shell redirection, and exact diagnostic/output strings. Integrated as `test_veristat`.

Risks: strongly coupled to veristat output formatting and working directory layout. `init_fixture()` prints failure if binary is missing but still proceeds with an uninitialized path risk if not caught by harness semantics. Large output buffer is fixed at 1 MB.

Test signals: expected output substrings for successful assignments and expected stderr substrings for parser/type/range failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_veristat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xdp_veth.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xdp_veth.c

Purpose: end-to-end XDP redirect suite over three veth pairs and four namespaces, covering chained redirect, broadcast/multicast redirect flags, and devmap egress programs.

Important APIs/types/functions: `struct veth_configuration`, `struct net_configuration`, `struct prog_configuration`, `create_network()`, `cleanup_network()`, `attach_programs_to_veth_pair()`, `xdp_veth_redirect()`, `xdp_veth_broadcast_redirect()`, and `xdp_veth_egress()`. Uses skeletons `xdp_dummy`, `xdp_redirect_map`, `xdp_redirect_multi_kern`, and `xdp_tx`, plus `bpf_xdp_attach()`, devmap updates, and ping.

Control flow: network creation copies a default topology, appends tid suffixes to namespace names, creates one ns0 namespace plus three remote namespaces and veth pairs. Redirect test loads dummy/tx/redirect-map programs, populates a tx-port map with next local ifindexes, attaches local and remote XDP programs, and pings destination. Broadcast test loads multi-redirect programs, configures redirect flags and devmap entries, pings a neighbor address, and checks per-interface receive counts with and without `BPF_F_EXCLUDE_INGRESS`. Egress test configures devmap egress program and magic MAC map, pings, then checks stored rx MACs.

State and persistence: creates multiple netns and veths, attaches XDP programs in ns0 and remote namespaces, updates BPF maps with ifindexes, flags, counters, and MACs. Cleanup removes namespaces and destroys skeletons; close_netns is used around namespace switches.

Dependencies and integration: requires XDP attach in generic/driver/SKB modes, devmap and devmap egress support, iproute2, ping, network namespaces, generated skeletons, and root privileges. Exposes three entry points: `test_xdp_veth_redirect`, `test_xdp_veth_broadcast_redirect`, and `test_xdp_veth_egress`.

Risks: driver mode can be unsupported on veth depending on kernel/config. A failure before `create_network()` initializes `net_config` can still call cleanup with uninitialized names in some paths. Egress test calls `attach_programs_to_veth_pair()` with `VETH_REDIRECT_SKEL_NB` instead of `VETH_EGRESS_SKEL_NB`; values are both 3 today, but the coupling is fragile.

Test signals: XDP attach success, redirect/devmap update success, ping success, exact receive counts (`4` or `0` for excluded ingress), and magic MAC comparisons for egress results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xdp_veth.c -->

# subset-b-006800 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fill_link_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fill_link_info.c

## Purpose

`fill_link_info.c` validates that `bpf_link_get_info_by_fd()` fills complete, type-specific metadata for perf-event links, kprobe-multi links, and uprobe-multi links. It is a user-space BPF selftest harness around `test_fill_link_info.skel.h`; the BPF programs are mostly inert trigger/attachment targets while the host test stresses link-info ABI behavior.

## Important APIs, Types, and Functions

The test centers on `struct bpf_link_info`, `bpf_link_get_info_by_fd()`, `bpf_program__attach_kprobe_opts()`, `bpf_program__attach_tracepoint_opts()`, `bpf_program__attach_perf_event_opts()`, `bpf_program__attach_uprobe_opts()`, `bpf_program__attach_kprobe_multi_opts()`, and `bpf_program__attach_uprobe_multi()`. It uses `bpf_kprobe_opts`, `bpf_tracepoint_opts`, `bpf_perf_event_opts`, `bpf_uprobe_opts`, `bpf_kprobe_multi_opts`, and `bpf_uprobe_multi_opts` with cookies, return-probe flags, symbol arrays, address arrays, and ref-counter offsets. `trace_helpers.h` supplies kallsyms and ELF symbol resolution helpers.

## Control Flow and Data Flow

`test_fill_link_info()` loads the skeleton, loads kallsyms, resolves `bpf_fentry_test1`, resolves local uprobe offsets, sorts kprobe-multi symbols, and runs subtests. Verification helpers first query only fixed-size fields, then repeat with user buffers for variable-length strings, address arrays, cookie arrays, path buffers, and ref-counter offsets. Negative helpers deliberately pass bad user pointers, missing counts, undersized arrays, and invalid lengths to assert `-EINVAL`, `-EFAULT`, or `-ENOSPC`.

## State, Dependencies, Integration Points, Risks, and Test Signals

The only persistent state is live link lifetime and the pinned kernel-side link metadata reachable through the FD; all links are destroyed before return. The test depends on perf events, tracepoints, kprobes, uprobes, kprobe-multi, uprobe-multi, kallsyms visibility, executable ELF symbols, and architecture-specific kprobe entry offsets for x86 IBT and PPC64 ftrace. Integration is the libbpf/kernel link-info ABI. Risks are kptr restrictions hiding addresses, architecture entry offset drift, missing perf/kprobe features, and exact errno regressions. Strong test signals are successful metadata round-trips for kprobe/kretprobe/tracepoint/uprobe/uretprobe/perf-event/kprobe-multi/uprobe-multi plus failure of invalid-buffer probes without corrupting zeroed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fill_link_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/find_vma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/find_vma.c

## Purpose

`find_vma.c` verifies the `bpf_find_vma()` helper from both perf-event and kprobe contexts and checks verifier rejection for illegal writes through returned VMA/task pointers.

## Important APIs, Types, and Functions

The file uses `find_vma.skel.h`, `find_vma_fail1.skel.h`, and `find_vma_fail2.skel.h`. Core functions are `open_pe()`, `find_vma_pe_condition()`, `test_find_vma_pe()`, `test_find_vma_kprobe()`, `test_illegal_write_vma()`, and `test_illegal_write_task()`. It uses `perf_event_open`, `bpf_program__attach_perf_event()`, skeleton attach, and BSS/data fields such as `found_vm_exec`, `find_addr_ret`, `find_zero_ret`, and `d_iname`.

## Control Flow and Data Flow

`serial_test_find_vma()` loads the valid skeleton, conditionally runs perf-event coverage when hardware CPU-cycle events work, always runs the kprobe path, then loads two expected-fail skeletons. Each positive path triggers a BPF program and calls `test_and_reset_skel()` to assert successful VMA lookup for the test binary and expected failure or success for zero address.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS/data counters in the skeleton and transient perf links. Dependencies include perf hardware events, kprobes, process VMAs, `/proc` executable naming, and the verifier's pointer write protections. Integration points are helper semantics and verifier enforcement around VMA/task pointers. Risks include unsupported PMU events, naming assumptions around `test_progs`, and kernel changes in zero-address lookup behavior. Test signals are positive VMA discovery, reset BSS state between triggers, and load rejection for both illegal write variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/find_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector.c

## Purpose

`flow_dissector.c` validates BPF flow dissector behavior in three modes: namespace attachment exclusivity, direct/indirect skb-less attach through a TAP interface, and skb-mode `bpf_prog_test_run_opts()` packet parsing. It exercises IPv4, IPv6, VLAN, fragments, flow labels, IPIP, GRE, encapsulation stop flags, and `BPF_FLOW_DISSECTOR_CONTINUE`.

## Important APIs, Types, and Functions

The file defines packed packet layouts (`ipv4_pkt`, `ipv6_pkt`, VLAN, fragment, IPIP, GRE) and a `struct test` table with expected `struct bpf_flow_keys`. It uses `bpf_flow.skel.h`, `bpf_prog_attach()`, `bpf_prog_detach2()`, `bpf_program__attach_netns()`, `bpf_prog_test_run_opts()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, TAP ioctls, and network namespace helpers. Key helpers are `init_prog_array()`, `create_tap()`, `ifup()`, `run_tests_skb_less()`, and the three public test entry points.

## Control Flow and Data Flow

The namespace test proves root and non-root netns flow dissector attach mutual exclusion. The skb-less tests create a private netns, load the dissector, populate the program array jump table, attach directly or via a netns link, send crafted frames through `tap0`, and read stored flow keys from `last_dissection`. The skb test runs each packet fixture directly against the dissector and compares returned flow keys.

## State, Dependencies, Integration Points, Risks, and Test Signals

State lives in the kernel flow-dissector attachment slot, the skeleton jump-table map, the `last_dissection` map, and temporary netns/TAP devices. Dependencies include `/dev/net/tun`, CAP_NET_ADMIN, namespace support, libbpf netns links, and packet layout definitions from kernel headers. Integration points are BPF flow dissector attach semantics, map-in-map tail calls, and flow key ABI. Risks are namespace cleanup leaks, TAP availability, endianness/packed layout mistakes, and skipped skb-less cases whose flags cannot be supplied. Test signals are correct `bpf_flow_keys`, attach rejection with `EEXIST`, clean detach, and exact `BPF_OK`/`BPF_FLOW_DISSECTOR_CONTINUE` return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_classification.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_classification.c

## Purpose

`flow_dissector_classification.c` performs end-to-end classification checks showing that a BPF flow dissector feeds kernel packet classification consistently for plain IPv4/IPv6 UDP, `BPF_FLOW_DISSECTOR_CONTINUE`, IPIP, GRE, and port-range flower filters.

## Important APIs, Types, and Functions

The harness builds packets with IPv4, IPv6, UDP, GUE, GRE, and optional extra encapsulation headers. It uses `bpf_flow.skel.h`, `bpf_prog_attach()`, program-array setup, raw and UDP sockets, `tc qdisc/filter` commands through `SYS`, network namespace helpers, checksum helpers, and `write_sysctl()`. `struct test_configuration` captures setup/teardown callbacks, source ports, address families, inner/outer addresses, encapsulation protocol, and DS fields.

## Control Flow and Data Flow

`test_global_init()` loads the dissector, enters an isolated netns, disables rp_filter, attaches and populates the program array. Each table entry sets qdisc/filter and tunnel state, sends ten packets from three source ports, receives UDP payloads, and expects pass/drop/pass behavior. Packet data is built from inside out so UDP checksums cover correct pseudo headers.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes netns configuration, loopback addresses, qdiscs, flower filters, IPIP/GRE devices, sockets, and the attached dissector. Dependencies are CAP_NET_ADMIN, `ip`/`tc`, raw sockets, loopback tunnel support, sysctl write access, and BPF flow dissector support. Integration points are dissector-to-flower classification and tunnel decapsulation. Risks include cleanup failures leaving qdiscs/tunnels, timing in receive polling, checksum mistakes, and environmental lack of modules or privileges. Test signals are `TEST_PACKETS_COUNT, 0, TEST_PACKETS_COUNT` receive counts for the three source-port cases across all configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_classification.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_load_bytes.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_load_bytes.c

## Purpose

`flow_dissector_load_bytes.c` checks helper availability/behavior for `bpf_skb_load_bytes()` in a flow dissector program run through the skb-style test-run path.

## Important APIs, Types, and Functions

The test hand-builds raw BPF instructions, loads them as `BPF_PROG_TYPE_FLOW_DISSECTOR` with `bpf_test_load_program()`, and executes with `bpf_prog_test_run_opts()`. It uses `pkt_v4`, `struct bpf_flow_keys`, and return codes `BPF_DROP`/`BPF_OK`.

## Control Flow and Data Flow

The BPF program tries to copy one byte from offset zero into stack memory. If helper execution succeeds it returns `BPF_DROP`; otherwise it returns `BPF_OK`. The host runs the program with packet input and flow-key output buffer, then asserts the program loaded, test-run succeeded, output size is the flow-key size, and retval is `BPF_OK`.

## State, Dependencies, Integration Points, Risks, and Test Signals

There is no persistent state beyond the loaded program FD. The test depends on flow dissector test-run support and helper restrictions for this program type/context. It integrates with verifier/helper availability and skb-less-vs-skb flow dissector semantics. The main risk is interpreting a helper policy change as a behavior regression; comments and expected retval encode the current contract. Test signals are successful load, successful run, preserved data-out size, and `BPF_OK` rather than helper-success `BPF_DROP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_load_bytes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_reattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_reattach.c

## Purpose

`flow_dissector_reattach.c` exhaustively tests attach, detach, query, link creation, link update, and link-info behavior for `BPF_FLOW_DISSECTOR` in init and non-root network namespaces.

## Important APIs, Types, and Functions

The file uses low-level BPF syscalls via libbpf wrappers: `bpf_prog_attach()`, `bpf_prog_detach2()`, `bpf_prog_query()`, `bpf_link_create()`, `bpf_link_update()`, `bpf_link_get_info_by_fd()`, and `bpf_prog_get_info_by_fd()`. It loads minimal flow-dissector programs with `bpf_test_load_program()`, switches namespaces with `setns()`/`unshare(CLONE_NEWNET)`, and checks `struct bpf_link_info.netns`.

## Control Flow and Data Flow

`serial_test_flow_dissector_reattach()` saves the starting netns, moves to `/proc/1/ns/net`, skips if init_net already has a dissector, runs a table of subtests there, then creates a new netns and repeats. Subtests cover prog/prog replacement, link/link exclusivity, prog-vs-link exclusivity, detach/query, link close, update with/without `BPF_F_REPLACE`, invalid opts, invalid program type, destroyed netns, and link info stability across updates.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the per-netns flow dissector attachment and link FD lifetime. Dependencies include namespace privileges, no preexisting init_net dissector, low-level BPF syscall support, and correct errno reporting. Integration points are kernel netns attachment ownership and libbpf link APIs. Risks are leaked namespace state on early failure, global init_net interference, and exact errno drift (`EEXIST`, `E2BIG`, `EINVAL`, `EPERM`, `EBADF`, `ENOLINK`). Test signals are queried program IDs matching expected FDs, no attachment after detach/close, and link info matching program id, link id, attach type, and netns inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_reattach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/for_each.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/for_each.c

## Purpose

`for_each.c` validates `bpf_for_each_map_elem()` behavior over hash, array, percpu, and multiple-map cases, plus verifier rejection when callbacks try to mutate map keys.

## Important APIs, Types, and Functions

The harness uses skeletons for hash map iteration, array map iteration, key-write failure, multi-map iteration, and hash modification. It uses `bpf_map__update_elem()`, `bpf_map__lookup_elem()`, `bpf_prog_test_run_opts()`, `bpf_num_possible_cpus()`, and packet input from `network_helpers.h`.

## Control Flow and Data Flow

Each subtest populates maps, runs `test_pkt_access`, and validates BSS counters and map side effects. Hash iteration checks element count, callback return/output, deletion of key 1, and percpu value selection for current CPU. Array iteration sums entries except the last to validate early stop behavior. Multi-map iteration toggles `use_array` to drive array versus hash traversal. Hash-modify exercises iteration while updating/deleting map elements according to the BPF-side program.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is limited to BPF maps and skeleton BSS fields. Dependencies are verifier support for map iteration callbacks, percpu map layout, and test-run support. Integration is the helper contract for callback invocation, early termination, key immutability, and map mutation safety. Risks include CPU-count dependent percpu expectations and verifier message/behavior drift. Test signals are expected sums/counters, failed lookup for deleted hash key, valid current-CPU percpu value, expected load failure for key writes, and correct outputs for array/hash selected paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/for_each.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/free_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/free_timer.c

## Purpose

`free_timer.c` stress-tests BPF timer freeing/overwriting races by concurrently running one BPF program that starts timers and another that overwrites/free-replaces them.

## Important APIs, Types, and Functions

The file uses `free_timer.skel.h`, `bpf_object__find_program_by_name()`, `bpf_prog_test_run_opts()`, pthreads, barriers, CPU affinity, and acquire/release atomics around the `start` flag. `run_ctx` carries program handles, a barrier, loop count, and stop/start flags.

## Control Flow and Data Flow

After skeleton load, the harness resolves `start_timer` and `overwrite_timer`, starts two CPU-pinned threads, releases them, and runs ten synchronized iterations. The start thread runs the timer-start program, signals overwrite, waits, and repeats. The overwrite thread waits for the signal, runs the overwrite program, then releases the start thread.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BPF timer/map state inside the skeleton and user-space synchronization state. Dependencies include BPF timer support, at least two CPUs for intended affinity, pthread barriers, and `bpf_prog_test_run_opts()`. Integration is the kernel timer lifetime path under concurrent replacement. Risks are scheduling/affinity limitations, races masked by low iteration count, and `EOPNOTSUPP` feature skips. Test signals are zero thread return bitmasks and no test-run errors or nonzero BPF retvals from either thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/free_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fs_kfuncs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fs_kfuncs.c

## Purpose

`fs_kfuncs.c` validates filesystem-related BPF kfuncs for reading, setting/removing xattrs, and fs-verity operations through LSM hooks.

## Important APIs, Types, and Functions

The test uses `test_get_xattr.skel.h`, `test_set_remove_xattr.skel.h`, and `test_fsverity.skel.h`, plus Linux xattr syscalls and `linux/fsverity.h`. It creates `/tmp/test_progs_fs_kfuncs`, triggers `security_inode_getxattr`, validates `security.bpf.*` xattrs, and exercises fs-verity ioctls through skeleton-controlled BSS/data/rodata fields.

## Control Flow and Data Flow

`test_get_xattr()` creates a file, sets a named xattr, attaches an LSM BPF program for the current PID, calls `getxattr()`, and checks whether BPF observed file/dentry xattr values and optionally denied access. The set/remove path creates a file, seeds `security.bpf.foo`, attaches programs that modify `security.bpf.bar`, and validates set, replacement, and removal from user space. Fs-verity subtests create file content, attach the skeleton, invoke fs-verity operations, and compare BPF-observed digest/signature behavior.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is temporary file metadata, xattrs, fs-verity state, and skeleton BSS counters. Dependencies include `/tmp` filesystem xattr support, LSM BPF, fs-verity kernel/filesystem support for relevant paths, and permission to manipulate security xattrs. Integration points are VFS/LSM hooks and filesystem kfunc ABI. Risks are filesystem-specific unsupported features, cleanup after partial xattr setup, and errno differences. Test signals are skip on `EOPNOTSUPP`, expected `getxattr()` return/errno, BSS flags for file/dentry discovery, and matching/removal of xattr values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fs_kfuncs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fsession_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fsession_test.c

## Purpose

`fsession_test.c` tests fentry/fexit session attachment behavior, including basic operation, detach/reattach, and session-cookie handling.

## Important APIs, Types, and Functions

The harness uses `fsession_test.skel.h`, skeleton `open/load/attach/detach/destroy`, and `bpf_prog_test_run_opts()` against `skel->progs.test1`. `check_result()` treats the BSS as an array of `__u64` result slots and requires every slot to be set to one.

## Control Flow and Data Flow

The basic subtest loads and attaches the skeleton, then runs `test1` to trigger function calls. The reattach subtest runs once, detaches, zeroes BSS, reattaches, and runs again. The cookie subtest disables `test6` autoload, compensates by setting its expected BSS fields, then verifies the remaining session-cookie paths.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is skeleton BSS result counters and link attachment state. Dependencies include kernel fprobe/session support; `-EOPNOTSUPP` causes skip. Integration is fentry/fexit session attachment, detachment, and cookie propagation. Risks are treating all BSS fields uniformly as `__u64` and feature availability on older kernels. Test signals are zero test-run error/retval and every expected result field equal to one across first attach, second attach, and cookie variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fsession_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_branch_snapshot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_branch_snapshot.c

## Purpose

`get_branch_snapshot.c` verifies `bpf_get_branch_snapshot()`/LBR snapshot behavior for a module function and tracks wasted branch entries.

## Important APIs, Types, and Functions

The file uses `get_branch_snapshot.skel.h`, `perf_event_open` with `PERF_SAMPLE_BRANCH_STACK`, kallsyms lookup for `bpf_testmod_loop_test`, `trigger_module_test_read()`, and helper routines to detect hypervisors and open per-CPU perf events.

## Control Flow and Data Flow

The serial test skips under hypervisors and when no LBR-capable perf event can be opened. It loads the skeleton, sets low/high address bounds around `bpf_testmod_loop_test`, attaches, triggers the module read path, and checks BSS counters for branch entries, hits, and wasted entries.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is per-CPU perf event FDs and BSS counters. Dependencies are LBR branch sampling, non-hypervisor environment, `bpf_testmod`, kallsyms visibility, and perf permissions. Integration is the perf branch stack with BPF branch snapshot helper. Risks include address-range guesswork, module symbol ordering, and variable branch-stack depth. Test signals are at least sixteen entries, more than six hits within the module function range, and fewer than ten wasted entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_branch_snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_args_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_args_test.c

## Purpose

`get_func_args_test.c` validates BPF helpers for reading traced function arguments in normal fentry/fexit/fmod_ret programs and fprobe session programs.

## Important APIs, Types, and Functions

The harness uses `get_func_args_test.skel.h` and `get_func_args_fsession_test.skel.h`, `bpf_prog_test_run_opts()`, skeleton attach, and `trigger_module_test_read()`. It drives `test1` and `fmod_ret_test` BPF programs and checks BSS result slots.

## Control Flow and Data Flow

The main test attaches all probes, runs `test1` to trigger `bpf_fentry_test*`, runs `fmod_ret_test` to trigger modify-return and fexit paths, triggers testmod read, and asserts six result flags. The fsession variant loads/attaches the session skeleton, runs `test1`, and checks its session argument result.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is only skeleton BSS result flags and link state. Dependencies include fentry/fexit/fmod_ret, fprobe sessions, and `bpf_testmod`. Integration is helper argument extraction across probe families. Risks are changed test function prototypes or missing module support. Test signals are zero test-run errors, expected packed retval from fmod_ret, successful module trigger, and all result flags equal to one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_args_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_ip_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_ip_test.c

## Purpose

`get_func_ip_test.c` validates `bpf_get_func_ip()` for function entry, function body offsets, uprobes, kprobes, and fprobe sessions.

## Important APIs, Types, and Functions

The file uses `get_func_ip_test.skel.h`, `get_func_ip_uprobe_test.skel.h`, and `get_func_ip_fsession_test.skel.h`. It attaches skeleton probes, manually attaches an x86_64 kprobe with `bpf_kprobe_opts.offset`, defines an assembly `uprobe_trigger_body`, and runs trigger programs with `bpf_prog_test_run_opts()`.

## Control Flow and Data Flow

Entry tests load/attach the skeleton, store the address of a local noinline trigger, run BPF trigger programs, call the local uprobe trigger, and assert result flags. On x86_64, body tests enable a disabled program, choose an offset adjusted for IBT, attach a kprobe to `bpf_fentry_test6`, run trigger code, then run the uprobe-body skeleton and call the assembly function. The fsession test checks entry and exit results.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS fields holding trigger addresses and result flags. Dependencies include fentry, fexit, kprobe, uprobe, fprobe sessions, x86_64-specific body tests, and kconfig `CONFIG_X86_KERNEL_IBT`. Integration is IP reporting across probe types and offsets. Risks are instruction offset drift, compiler treatment of noinline triggers, and architecture skips. Test signals are all expected result fields equal to one and clean attach/run across entry, body, and session paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_ip_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stack_raw_tp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stack_raw_tp.c

## Purpose

`get_stack_raw_tp.c` validates stack collection helpers from a raw tracepoint program, including raw address stacks and build-id stack data.

## Important APIs, Types, and Functions

The test loads `test_get_stack_rawtp.bpf.o` and expected-fail `test_get_stack_rawtp_err.bpf.o`, attaches to raw tracepoint `sys_enter`, uses a perf buffer map, and decodes `struct get_stack_trace_t`. It uses `load_kallsyms()`, `ksym_search()`, CPU affinity, `nanosleep()` triggers, and `perf_buffer__poll()`.

## Control Flow and Data Flow

The harness first asserts the erroneous object cannot load, then loads the valid raw tracepoint object, finds program and perf map, pins itself to CPU 0, attaches to `sys_enter`, creates a perf buffer, triggers ten syscalls, and polls until expected events arrive. The callback checks kernel stack sanity by symbol name when JIT is disabled or non-empty stacks when JIT is enabled, and validates user stack/build-id sizes.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes a raw tracepoint link, perf buffer events, and kallsyms cache. Dependencies are raw tracepoints, stack walking, build-id support, perf buffer delivery, and CPU affinity. Integration is BPF stack helper output format and perf event transport. Risks are JIT-dependent symbol validation, missing kallsyms, fewer events than expected, and stack walking limitations. Test signals are expected load failure for the bad object, valid perf samples, non-corrupt kernel stack, and user stack/build-id data present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stack_raw_tp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stackid_cannot_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stackid_cannot_attach.c

## Purpose

`get_stackid_cannot_attach.c` checks that a perf-event BPF program using stack/build-id collection can attach only to perf events with compatible callchain sampling.

## Important APIs, Types, and Functions

The test uses `test_stacktrace_build_id.skel.h`, overrides program type to `BPF_PROG_TYPE_PERF_EVENT`, opens hardware CPU-cycle perf events with branch-stack sampling, and attaches with `bpf_program__attach_perf_event()`.

## Control Flow and Data Flow

It loads the skeleton, opens a precise CPU-cycle event without `PERF_SAMPLE_CALLCHAIN`, and expects attach failure. It then adds `PERF_SAMPLE_CALLCHAIN` and expects attach success. Finally it sets `exclude_callchain_kernel` and expects attach failure again.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is perf event FDs and a perf-event link. Dependencies include hardware PMU support for precise CPU cycles, branch stacks, and callchains; unsupported PMUs are skipped. Integration is kernel validation between perf event sample type and BPF stack helper needs. Risks are PMU permission/support differences and exact attach error behavior. Test signals are fail/succeed/fail attach sequence for no-callchain, callchain, and kernel-callchain-excluded configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stackid_cannot_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data.c

## Purpose

`global_data.c` validates libbpf global data map relocation for `.bss`, `.data`, and `.rodata` numbers, strings, structs, and read-only enforcement.

## Important APIs, Types, and Functions

The test loads `test_global_data.bpf.o` as `BPF_PROG_TYPE_SCHED_CLS`, runs it with `bpf_prog_test_run_opts()`, locates result maps by name, and uses `bpf_map_lookup_elem()`. It also queries internal map aliases `test_glo.rodata` and `.rodata` and attempts `bpf_map_update_elem()`.

## Control Flow and Data Flow

After program run, helper functions validate numeric, string, and struct result maps against hard-coded expected relocations. The read-only subtest confirms the internal `.rodata` map is discoverable by both generated and ELF names and rejects updates with `EPERM`.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is internal global-data maps and result maps produced by the BPF object. Dependencies include libbpf datasec support, scheduler classifier test-run, and global data relocation. Integration points are internal map naming, relocation emission, and read-only map enforcement. Risks are layout drift in the paired BPF object or result map names. Test signals are exact scalar/string/struct matches, `.rodata` alias equality, and failed `.rodata` update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data_init.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data_init.c

## Purpose

`global_data_init.c` verifies `bpf_map__set_initial_value()` for internal global data maps before object load and rejects wrong-size or post-load initial-value changes.

## Important APIs, Types, and Functions

It opens `test_global_data.bpf.o`, finds the `.rodata` internal map, uses `bpf_map__value_size()`, `bpf_map__set_initial_value()`, `bpf_object__load()`, and `bpf_map_lookup_elem()`.

## Control Flow and Data Flow

The test allocates a zeroed buffer matching `.rodata`, checks that `sz - 1` is rejected, sets the full-size value, loads the object, reads map element zero, compares bytes, then tries to set a new initial value after load and expects failure.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the pre-load internal map initial-value buffer and loaded `.rodata` map. Dependencies are libbpf object open/load and internal map support. Integration is libbpf initial data override semantics. Risks include paired object layout changes and allocation failure. Test signals are wrong-size rejection, successful full-size override, byte-for-byte map match after load, and post-load rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_args.c

## Purpose

`global_func_args.c` validates passing and mutating arguments through global BPF functions, including NULL pointers, return values, local/global variables, and pointer-to-pointer writes.

## Important APIs, Types, and Functions

The file loads `test_global_func_args.bpf.o` as `BPF_PROG_TYPE_CGROUP_SKB`, runs it with `bpf_prog_test_run_opts()`, finds the `values` map with `bpf_find_map()`, and looks up indexed expected results.

## Control Flow and Data Flow

The BPF program is run once against `pkt_v4`; afterward `test_global_func_args0()` iterates seven expected result slots and compares map values with the expected semantics for each global function argument case.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the `values` map populated by the BPF object. Dependencies include global subprogram support, cgroup skb test-run, and packet fixture availability. Integration is verifier and codegen support for global function argument passing. Risks are paired BPF object result-index drift. Test signals are successful load/run and exact values `[0, 1, 100, 101, 42, 43, 1]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_dead_code.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_dead_code.c

## Purpose

`global_func_dead_code.c` verifies that freplace can target a live global subprogram but cannot target a global subprogram eliminated as dead code.

## Important APIs, Types, and Functions

The test uses `verifier_global_subprogs.skel.h`, `freplace_dead_global_func.skel.h`, `bpf_program__set_autoload()`, `bpf_program__set_attach_target()`, `bpf_program__set_log_buf()`, and skeleton load calls.

## Control Flow and Data Flow

It loads the target skeleton with `chained_global_func_calls_success`, gets its FD, loads a freplace program targeting `global_good` and expects success, then opens another freplace skeleton targeting `global_dead`, captures verifier log, and expects load failure containing a missing-subprogram message.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the loaded target program and verifier log buffer. Dependencies include freplace, global function metadata, and dead-code elimination behavior. Integration is attach-target symbol resolution after verifier/linker optimization. Risks are verifier log wording drift and target BPF object changes. Test signals are successful live target replacement and failed dead target load with `Subprog global_dead doesn't exist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_dead_code.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_map_resize.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_map_resize.c

## Purpose

`global_map_resize.c` tests resizing libbpf global datasec maps before load for `.bss` and custom `.data`, and verifies BTF metadata handling for invalid resize layouts.

## Important APIs, Types, and Functions

The test uses `test_global_map_resize.skel.h`, `bpf_map__set_value_size()`, `bpf_map__value_size()`, `bpf_map__initial_value()`, BTF key/value type queries, skeleton attach, and syscall triggers (`getpid`, `getuid`) for attached programs.

## Control Flow and Data Flow

The BSS subtest opens the skeleton, seeds one element, resizes `.bss` to include a large trailing array, resizes a percpu data map, refreshes the initial-value pointer, fills new elements, sets rodata lengths/PID, loads/attaches, triggers, and checks sum. The data subtest mirrors this for `.data.custom`. The invalid subtest resizes maps whose BTF cannot remain valid and asserts resize succeeds while BTF IDs are cleared.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is pre-load skeleton global-data memory, resized map definitions, BTF metadata, and post-trigger BSS sum. Dependencies include libbpf support for datasec resizing and kernel support for attached syscall probes. Integration is libbpf map sizing, initial-value preservation, and BTF invalidation policy. Risks are page-size dependence, struct layout assumptions, and stale skeleton pointers after resize. Test signals are preserved first element, sum equals computed array length, percpu resize success, and BTF IDs cleared for invalid layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_map_resize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hash_large_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hash_large_key.c

## Purpose

`hash_large_key.c` verifies BPF hash map behavior with a large key structure around 4 KiB and BPF-side map access that changes an associated value.

## Important APIs, Types, and Functions

The harness uses `test_hash_large_key.skel.h`, obtains `hash_map` FD, attaches raw tracepoint programs, and calls `bpf_map_update_elem()`/`bpf_map_lookup_elem()` with a `struct bigelement` key.

## Control Flow and Data Flow

It loads and attaches the skeleton, inserts key `{0}` with value 21, mutates only `key.c` to 1, then looks up the value and expects 42, indicating the BPF-side program populated/used the large key path.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is one hash map with large keys and skeleton links. Dependencies include hash map large-key support and the paired BPF program's tracepoint trigger. Integration is kernel hashing/copying of large keys. Risks are stack/heap key layout mismatch and paired BPF object assumptions. Test signal is successful lookup with value 42 for the mutated large key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hash_large_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hashmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hashmap.c

## Purpose

`hashmap.c` unit-tests libbpf's user-space `struct hashmap` implementation for integer keys, pointer/string keys, collision-heavy multimap behavior, deletion, iteration, clear, size, and empty-map semantics.

## Important APIs, Types, and Functions

The file uses `bpf/hashmap.h` APIs: `hashmap__new()`, `hashmap__free()`, `hashmap__add()`, `hashmap__set()`, `hashmap__update()`, `hashmap__append()`, `hashmap__insert()`, `hashmap__find()`, `hashmap__delete()`, `hashmap__clear()`, `hashmap__size()`, `hashmap__capacity()`, `hashmap__for_each_entry()`, and `hashmap__for_each_key_entry()`. It supplies custom hash/equality functions for integer, string, and forced-collision cases.

## Control Flow and Data Flow

Subtests create maps, insert/update/delete entries, verify returned old keys/values, iterate all buckets and per-key chains, and assert final sizes. The generic test covers normal map operations and deletion during iteration. The multimap test forces all keys into one bucket and validates per-key iteration. The empty test asserts lookups/deletes/iterations are inert. The pointer interface test uses string keys and values with custom hash/equality.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is entirely heap-allocated user-space hashmap data. Dependencies are libbpf's internal hashmap implementation and test macros; no kernel BPF state is used. Integration is with libbpf internals used by loaders and symbol maps. Risks are pointer/integer casting assumptions and collision-chain regressions. Test signals are expected size/capacity transitions, found bitmasks covering all inserted values, correct old key/value returns, no entries after deletion/clear, and no iteration from empty maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hashmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/helper_restricted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/helper_restricted.c

## Purpose

`helper_restricted.c` checks that a set of BPF programs using restricted helpers fail verifier load as expected.

## Important APIs, Types, and Functions

The test uses `test_helper_restricted.skel.h`, skeleton metadata `prog_cnt`, iterates generated `skeleton->progs`, toggles autoload with `bpf_program__set_autoload()`, and calls `test_helper_restricted__load()`.

## Control Flow and Data Flow

For each program slot, the harness opens a fresh skeleton, enables autoload for all programs up to the skeleton's program count, attempts load, asserts error, destroys, and repeats until every program has participated.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is per-open skeleton autoload configuration and verifier result. Dependencies are the paired restricted-helper BPF object and verifier policy. Integration is helper availability enforcement by program type/context. Risks are unusual loop shape relying on `prog_cnt` discovered from the first skeleton and missing exact verifier message checks. Test signal is load failure for each attempted configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/helper_restricted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_reuse.c

## Purpose

`htab_reuse.c` stress-tests hash map element reuse under concurrent update/delete/lookup with `BPF_F_LOCK`, including a large-value consistency race.

## Important APIs, Types, and Functions

The file uses `htab_reuse.skel.h`, pthreads, `bpf_map_update_elem()`, `bpf_map_delete_elem()`, `bpf_map_lookup_elem_flags()` with `BPF_F_LOCK`, a pipe start barrier, and map values containing `bpf_spin_lock`.

## Control Flow and Data Flow

The basic subtest runs one writer repeatedly inserting/deleting two keys and four readers repeatedly locked-looking-up a key. The consistency subtest seeds a large locked value, starts locked updaters, delete+update threads, and locked lookup threads simultaneously, then scans all 256 data words from each lookup for torn writes.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is hash map contents, spin-lock-protected values, thread stop flags, and torn-write flag. Dependencies include BPF spin locks in map values, locked lookup/update support, pthread scheduling, and the paired map definitions. Integration is kernel htab element reuse and value-copy atomicity around `BPF_F_LOCK`. Risks are race sensitivity, long loop runtime, and missing failures due to scheduling. Test signals are no thread setup failures and `ctx.torn_write == false` after high-volume concurrent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_update.c

## Purpose

`htab_update.c` verifies hash map update behavior for reentrant update prevention and concurrent user-space updates.

## Important APIs, Types, and Functions

The test uses `htab_update.skel.h`, selectively autoloads `bpf_obj_free_fields`, attaches fentry hooks, allocates values sized from `bpf_map__value_size()`, and uses `bpf_map_update_elem()` from the main thread and worker threads.

## Control Flow and Data Flow

The reentry subtest inserts an element, then replaces it. During old-value free, the BPF fentry program attempts a nested map update; the BPF-side `update_err` should record `-EDEADLK`. The concurrent subtest loads the skeleton and starts four threads, each updating key zero 1000 times, expecting no update errors.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the `htab` map, BPF-side `update_err`, and thread context. Dependencies include map value free hooks, fentry support, and htab locking. Integration is htab deadlock avoidance and update synchronization. Risks are race sensitivity and paired BPF program assumptions. Test signals are successful insert/replace with `update_err == -EDEADLK` and all concurrent updater threads returning NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/htab_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/inner_array_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/inner_array_lookup.c

## Purpose

`inner_array_lookup.c` validates lookup and update behavior for an inner array map referenced by the loaded BPF program.

## Important APIs, Types, and Functions

The harness uses `inner_array_lookup.skel.h`, skeleton attach, `bpf_map__fd()`, `bpf_map_update_elem()`, and `bpf_map_lookup_elem()`.

## Control Flow and Data Flow

After load and attach, the test writes value 1 at key 3 of `inner_map1`. The attached BPF probe is expected to observe/update that slot, so the host reads key 3 back and asserts value 2.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the inner array map contents and attached probe link. Dependencies are array-in-array map handling and the paired BPF trigger path. Integration is inner map lookup from BPF. Risks include missing trigger if attach point does not fire promptly. Test signal is key 3 value changed to 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/inner_array_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ip_check_defrag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ip_check_defrag.c

## Purpose

`ip_check_defrag.c` tests BPF-driven IP defragmentation/checksum behavior across IPv4 and IPv6 in a two-namespace topology.

## Important APIs, Types, and Functions

The file uses `ip_check_defrag.skel.h`, network namespace helpers, raw and UDP sockets, veth/topology setup, `start_server()`, `client_socket()`, manual packet buffers, and skeleton attach routines for IPv4/IPv6. It uses IP addressing constants, server/client ports, and BPF program state for observed defrag results.

## Control Flow and Data Flow

For each family, the harness loads the skeleton, builds ns0/ns1 topology, attaches the relevant BPF program, starts a UDP server in ns1, opens raw TX and UDP RX sockets in ns0, binds a chosen receive port, sends crafted fragmented traffic, and checks that expected payloads/ICMP or UDP replies are observed. Cleanup tears down sockets, links, and namespaces.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes netns topology, routes, raw sockets, UDP sockets, fragmented packet buffers, and skeleton counters. Dependencies are CAP_NET_ADMIN, raw sockets, IPv4/IPv6 stack support, and BPF helper support for defrag/checksum. Integration is BPF packet processing with kernel IP defragmentation and namespace routing. Risks are privilege gaps, timing in socket receive paths, route cleanup failures, and family-specific fragmentation differences. Test signals are successful topology/attach, received expected data, and no socket or packet assertions failing for both IPv4 and IPv6 subtests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ip_check_defrag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iter_buf_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iter_buf_null_fail.c

## Purpose

`iter_buf_null_fail.c` is a verifier negative-test wrapper for iterator buffer NULL handling.

## Important APIs, Types, and Functions

The file includes `iter_buf_null_fail.skel.h` and invokes `RUN_TESTS(iter_buf_null_fail)`, which runs all annotated skeleton verifier cases through the selftest framework.

## Control Flow and Data Flow

There is no custom control flow beyond delegating to `RUN_TESTS`. The paired BPF object contains the individual programs and expected outcomes.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier load result and framework subtest metadata. Dependencies are the generated skeleton and verifier expectations embedded in the BPF source. Integration is iterator buffer pointer validation. Risks are opaque coverage from the C wrapper alone and verifier log wording drift in the paired object. Test signal is `RUN_TESTS` passing all negative cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iter_buf_null_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iters.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iters.c

## Purpose

`iters.c` validates numeric, task, VMA, cgroup, css, testmod, and state-safety iterator behavior, including both attached iterators and open-coded iterator programs.

## Important APIs, Types, and Functions

The harness uses many skeletons: `iters`, `iters_state_safety`, `iters_looping`, `iters_num`, `iters_testmod`, `iters_testmod_seq`, `iters_task_vma`, `iters_task`, `iters_css_task`, `iters_css`, and `iters_task_failure`. It uses `bpf_iter_create()`, direct `bpf_prog_test_run_opts()`, `/proc/self/maps`, cgroup helpers, pthreads, `mmap`-related triggers, and `RUN_TESTS` for verifier cases.

## Control Flow and Data Flow

Numeric iterator subtests attach, briefly run, detach, and compare many BSS results to rodata expected values. Testmod seq iterators run only when `env.has_testmod`. Task VMA tests compare BPF-seen ranges to `/proc/self/maps`. Task iterator tests create blocked threads and verify process/thread counts. CSS/cgroup tests create and join cgroups before triggering. Additional subtests cover looping/state safety and expected failures.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes iterator links/FDs, BSS result arrays, cgroups, temporary threads, and process VMA snapshots. Dependencies are BPF iterator kernel support, cgroupfs setup, testmod for module iterators, pthreads, and procfs. Integration is iterator next/destroy semantics, open-coded iterators, task/mm/css references, and verifier state safety. Risks are environmental cgroup setup failure, thread-count races, `/proc/self/maps` special entries, and skipped module coverage. Test signals are BSS result equals rodata expected values, VMA ranges match procfs, process/thread counts match, cgroup/css counts are correct, and verifier-case skeletons pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jeq_infer_not_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jeq_infer_not_null.c

## Purpose

`jeq_infer_not_null.c` wraps verifier tests for nullability inference across equality comparisons.

## Important APIs, Types, and Functions

It includes `jeq_infer_not_null_fail.skel.h` and delegates to `RUN_TESTS(jeq_infer_not_null_fail)`.

## Control Flow and Data Flow

The C harness has no bespoke logic; the selftest framework loads/runs the paired negative verifier programs and checks expected failures.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier result metadata. Dependencies are the generated skeleton and verifier annotations in the BPF source. Integration is verifier reasoning for `JEQ`-derived non-null facts. Risks are verifier message/behavior changes not visible in the wrapper. Test signal is successful `RUN_TESTS` completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jeq_infer_not_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jit_probe_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jit_probe_mem.c

## Purpose

`jit_probe_mem.c` validates JIT handling of probe-memory style accesses in a packet-processing BPF program.

## Important APIs, Types, and Functions

The harness uses `jit_probe_mem.skel.h`, packet fixture `pkt_v4`, and `bpf_prog_test_run_opts()` against `test_jit_probe_mem`.

## Control Flow and Data Flow

It loads the skeleton, runs the BPF program once with IPv4 packet input, asserts no test-run error and zero BPF retval, then checks `skel->data->total_sum == 192`.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the BPF data variable `total_sum`. Dependencies include JIT/probe memory support and packet test-run. Integration is JIT code generation for guarded memory probing. Risks are architecture-specific JIT differences and paired BPF object changes. Test signal is exact total sum 192 after a successful run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jit_probe_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kernel_flag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kernel_flag.c

## Purpose

`kernel_flag.c` tests kernel-origin tracking for `bpf()` invocations by using an LSM program to allow normal skeleton loading while blocking light-skeleton kernel-based calls.

## Important APIs, Types, and Functions

The test uses `test_kernel_flag.skel.h`, `kfunc_call_test.skel.h`, and `kfunc_call_test.lskel.h`. It sets `monitored_tid` to `sys_gettid()`, attaches the LSM skeleton, then attempts normal and light skeleton open/load.

## Control Flow and Data Flow

After the LSM program attaches, a normal libbpf skeleton load is expected to pass the gatekeeper. A light skeleton load is expected to fail because it uses kernel-origin BPF invocations that the LSM program blocks. The monitored TID is reset before cleanup.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is LSM BSS `monitored_tid` and attached LSM link. Dependencies are BPF LSM support, kfunc test skeletons, and light skeleton generation. Integration is kernel flag propagation through BPF syscall paths. Risks include LSM availability and assumptions about libbpf vs lskel call paths. Test signals are successful LSM attach, successful normal skeleton load, and failed lskel open/load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kernel_flag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfree_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfree_skb.c

## Purpose

`kfree_skb.c` validates raw tracepoint and fentry/fexit access to skb data and control buffer around packet free paths.

## Important APIs, Types, and Functions

The test uses `kfree_skb.skel.h`, loads `test_pkt_access.bpf.o`, attaches raw tracepoint `kfree_skb` and fentry/fexit probes on `eth_type_trans`, creates a perf buffer, and runs a sched_cls packet program with a crafted `__sk_buff` context.

## Control Flow and Data Flow

It sets `skb.cb` to known bytes, runs the packet program on `pkt_v6`, polls the perf buffer, and the callback validates metadata (`ifindex`, cb bytes/words) and IPv6/TCP header fields. It then reads the skeleton BSS map and checks both fentry/fexit result flags.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes perf-buffer events, BSS flags, loaded packet program, and attached trace links. Dependencies are raw tracepoint, fentry/fexit, perf buffer, loopback ifindex assumptions, and packet test-run. Integration is skb memory access from tracing programs. Risks include spurious `kfree_skb` events, parallel instability noted by serial test comment, and loopback metadata assumptions. Test signals are callback `passed == true`, perf poll success, and both BSS test flags true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfree_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_call.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_call.c

## Purpose

`kfunc_call.c` validates kernel function call support from BPF across tc and syscall program types, including success cases, verifier failure cases, runtime failure cases, light skeletons, subprograms, and destructive kfunc capability gating.

## Important APIs, Types, and Functions

It uses `kfunc_call_fail.skel.h`, `kfunc_call_test.skel.h`, `kfunc_call_test.lskel.h`, subprog skeletons, destructive skeletons, `cap_helpers.h`, `bpf_prog_test_run_opts()`, verifier log buffers through `bpf_object_open_opts`, and tables of `kfunc_test_params`.

## Control Flow and Data Flow

For each table case, success paths load normal and light skeletons, select the named program, run with tc packet data or syscall context, and compare retval. Failure paths enable one failing program, capture verifier logs, either expect load failure or runtime `bpf_prog_test_run_opts()` error, and assert the expected diagnostic substring. Additional subtests exercise subprogram variants and destructive kfunc loading under capability constraints.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier log text, program retvals, and skeleton BSS where applicable. Dependencies include kernel BTF kfunc definitions, syscall and tc test-run support, capabilities for destructive calls, and light skeleton ABI. Integration is verifier kfunc type checking, memory acquisition/release rules, nullable context handling, and runtime syscall kfunc behavior. Risks are verifier log wording drift, missing kfuncs on older kernels, and capability-dependent skips/failures. Test signals are exact retvals for success cases, expected `-EINVAL` runtime failures, verifier load rejection for bad memory/type cases, and log substrings matching the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_dynptr_param.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_dynptr_param.c

## Purpose

`kfunc_dynptr_param.c` validates kfuncs that accept dynptr parameters, especially PKCS#7 signature verification behavior with NULL dynptr data.

## Important APIs, Types, and Functions

The test uses `test_kfunc_dynptr_param.skel.h`, a libbpf print callback to detect missing `bpf_verify_pkcs7_signature` kfunc, `bpf_program__attach()`, `bpf_prog_get_next_id()` as a trigger, and `RUN_TESTS` for paired verifier cases.

## Control Flow and Data Flow

`has_pkcs7_kfunc_support()` opens/loads once with a temporary print callback and skips if the extern kfunc is missing. Each runtime subtest loads the skeleton, sets current PID, attaches the selected program, calls `bpf_prog_get_next_id()` to trigger, destroys the link, and checks `skel->bss->err` against the expected runtime error.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS `pid` and `err`, plus transient link state. Dependencies include kernel/module BTF exposing PKCS#7 kfuncs, dynptr support, and libbpf extern resolution. Integration is kfunc dynptr parameter validation and runtime error reporting. Risks are feature skips on kernels without the kfunc and log-format matching in the print callback. Test signals are skip when unsupported, expected `-EBADMSG` for `dynptr_data_null`, and passing verifier cases from `RUN_TESTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_dynptr_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_implicit_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_implicit_args.c

## Purpose

`kfunc_implicit_args.c` is a selftest wrapper for BPF kfunc implicit-argument verifier/runtime cases.

## Important APIs, Types, and Functions

The file includes the generated `kfunc_implicit_args.skel.h` and invokes the standard `RUN_TESTS(kfunc_implicit_args)` macro.

## Control Flow and Data Flow

All substantive cases live in the paired BPF object; the C file delegates enumeration, loading, and assertion of expected outcomes to the selftest framework.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier/runtime result metadata maintained by the framework. Dependencies are kernel support for the relevant kfuncs and implicit argument annotations. Integration is verifier injection/checking of implicit kfunc arguments. Risks are limited visibility from the wrapper and feature-dependent failures in the paired object. Test signal is successful completion of all generated `RUN_TESTS` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_implicit_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_module_order.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_module_order.c

## Purpose

`kfunc_module_order.c` verifies kfunc resolution when two test modules exporting relevant kfuncs are loaded in a specific order.

## Important APIs, Types, and Functions

It uses `kfunc_module_order.skel.h`, `testing_helpers.h` module load/unload helpers, and `bpf_prog_test_run_opts()` on `call_kfunc_xy` and `call_kfunc_yx`.

## Control Flow and Data Flow

The test loads `bpf_test_modorder_x.ko`, then `bpf_test_modorder_y.ko`, opens/loads the skeleton, runs both BPF programs with dummy packet data, requires zero syscall error and zero retval, destroys the skeleton, then unloads modules in reverse order.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is loaded kernel modules and transient BPF programs. Dependencies include available module files, module load permissions, kernel BTF for module kfuncs, and test-run support. Integration is module kfunc lookup ordering and ambiguity handling. Risks are cleanup if module Y load or skeleton load fails, missing modules, and permission restrictions. Test signals are successful module loads, skeleton load, and zero retvals for both call orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_module_order.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_param_nullable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_param_nullable.c

## Purpose

`kfunc_param_nullable.c` wraps selftests for kfunc nullable-parameter validation.

## Important APIs, Types, and Functions

The C harness includes `kfunc_param_nullable.skel.h` and delegates through `RUN_TESTS(kfunc_param_nullable)`.

## Control Flow and Data Flow

The generated selftest framework loads/runs each annotated BPF program from the paired skeleton; this wrapper adds no custom control flow.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier/runtime outcome metadata. Dependencies are kernel kfunc nullable annotations and the generated skeleton. Integration is verifier enforcement of nullable versus non-null kfunc parameter contracts. Risks are hidden in the paired BPF object and kernel-version feature availability. Test signal is all `RUN_TESTS` cases passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_param_nullable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kmem_cache_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kmem_cache_iter.c

## Purpose

`kmem_cache_iter.c` validates BPF iteration over kernel slab caches and open-coded kmem-cache iterator behavior.

## Important APIs, Types, and Functions

The test uses `kmem_cache_iter.skel.h`, `bpf_iter_create()`, reads from the iterator FD, compares against `/proc/slabinfo`, and directly runs `check_task_struct` and `open_coded_iter` programs with `bpf_prog_test_run_opts()`.

## Control Flow and Data Flow

After skeleton load/attach, it creates an iterator FD for `slab_info_collector` and drains it. Subtests verify the current task's `task_struct` belongs to a slab cache, compare BPF-collected slab names/object sizes against `/proc/slabinfo`, and run the open-coded iterator to ensure it sees the same number of caches as the explicit iterator.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the iterator link/FD, `slab_result` map, and BSS counters. Dependencies include kmem-cache iterator support, `/proc/slabinfo` availability, and stable enough slabinfo ordering during comparison. Integration is BPF iterator output and open-coded iterator parity. Risks are `/proc/slabinfo` absence, dynamic slab changes during comparison, and name truncation to 32 bytes. Test signals are `task_struct_found == 1`, BPF slab entries matching proc names/object sizes, read EOF after draining, and open-coded count equal to explicit count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kmem_cache_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_test.c

## Purpose

`kprobe_multi_test.c` is the main kprobe-multi selftest harness. It validates skeleton attach, raw link creation by symbols and addresses, libbpf attach helpers, invalid option handling, sessions, cookies, unique-match behavior, override-return restrictions, write-context rejection, duplicate symbol resolution, and verifier cases.

## Important APIs, Types, and Functions

It uses `kprobe_multi.skel.h`, empty/override/session/cookie/verifier/write-ctx/sleepable skeletons, `trace_helpers.h`, kallsyms helpers, `bpf_link_create()`, `bpf_program__attach_kprobe_multi_opts()`, `bpf_program__attach_kprobe()`, `bpf_prog_test_run_opts()`, `prctl()`, and `RUN_TESTS(kprobe_multi_verifier)`. Options include symbol arrays, address arrays, wildcard patterns, return probes, cookies, and `unique_match`.

## Control Flow and Data Flow

The test loads kallsyms, then runs subtests. Positive paths attach to `bpf_fentry_test1..8`, trigger a BPF program, and assert entry/return result fields. Negative attach paths exercise conflicting option combinations, nonexistent patterns/names, huge counts, and sleepable programs. Session tests count entry/exit firings and cookie propagation. Override tests check `bpf_override_return` can attach only to error-injection targets and can change `prctl()` return. Bench helpers attach to many kernel/module symbols for timing in a separate serial entry point.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes kprobe links, skeleton BSS result counters, kallsyms caches, and temporary override hooks. Dependencies are kprobe-multi, ftrace/kallsyms visibility, bpf_testmod for duplicate symbols, error-injection symbol availability, and architecture support for write-context test. Integration is libbpf kprobe-multi option validation and kernel attachment semantics. Risks include symbol availability, swapped subtest labels for addrs/syms in the entry function, exact errno expectations, and global side effects from override probes. Test signals are all result counters equal to expected values, invalid attaches returning expected negative errno, override `prctl()` returning 123 only when attached, and verifier suite passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_testmod_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_testmod_test.c

## Purpose

`kprobe_multi_testmod_test.c` validates kprobe-multi attachment to symbols exported by `bpf_testmod`, using both symbol names and module-local addresses.

## Important APIs, Types, and Functions

The harness reuses `kprobe_multi.skel.h`, `trace_helpers.h`, local kallsyms via `load_kallsyms_local()`, `ksym_get_addr_local()`, `bpf_program__attach_kprobe_multi_opts()`, and `trigger_module_test_read()`.

## Control Flow and Data Flow

The serial test loads local kallsyms, runs symbol and address subtests. Each subtest opens the skeleton, sets current PID, attaches entry probes to three `bpf_testmod_fentry_test*` functions, flips `retprobe`, attaches return probes, triggers module read, and checks six BSS result flags.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is local kallsyms cache and kprobe links. Dependencies include loaded/available `bpf_testmod`, module kallsyms visibility, and kprobe-multi support for module symbols. Integration is module symbol resolution by name and address. Risks are missing test module, symbol renames, and return-probe option mutation. Test signals are all three entry and all three return result fields equal to one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_testmod_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kptr_xchg_inline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kptr_xchg_inline.c

## Purpose

`kptr_xchg_inline.c` verifies code generation for inline `bpf_kptr_xchg` by inspecting the loaded program instructions.

## Important APIs, Types, and Functions

The test uses `kptr_xchg_inline.skel.h`, `bpf_program__insns()`, `bpf_program__insn_cnt()`, and compares expected `struct bpf_insn` values generated with BPF instruction macros.

## Control Flow and Data Flow

It loads the skeleton, obtains the instruction stream for the relevant program, asserts instruction count/shape, and compares key instructions such as map-value pointer setup and `BPF_ATOMIC_OP(... BPF_XCHG ...)` against expected encodings.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the libbpf-side loaded instruction array. Dependencies include compiler/codegen stability for the paired BPF source and kptr support. Integration is inline lowering of kptr exchange to atomic xchg instruction form. Risks are brittle instruction-index expectations when compiler output changes. Test signals are exact instruction-count and `memcmp` matches for expected mov/xchg instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kptr_xchg_inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms.c

## Purpose

`ksyms.c` validates BPF kernel symbol resolution for normal symbols, weak/missing symbols, percpu symbols, and vmlinux BTF size exposure.

## Important APIs, Types, and Functions

The test uses `test_ksyms.skel.h`, `kallsyms_find()`, `stat()` on the vmlinux BTF path, skeleton attach, and BSS data fields such as `out__bpf_link_fops`, `out__btf_size`, and `out__per_cpu_start`.

## Control Flow and Data Flow

The harness finds `bpf_link_fops` and `__per_cpu_start` in kallsyms, reads BTF file size, loads/attaches the skeleton, triggers it, and compares BPF-resolved outputs with user-space discovered values. Weak missing symbol output is expected to be zero.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS output values and kallsyms/BTF file metadata. Dependencies include kallsyms access, vmlinux BTF file, and ksym extern support. Integration is BPF ksym relocation. Risks are symbol visibility restrictions and missing BTF. Test signals are exact address matches for visible symbols, zero for missing weak symbol, and BTF size equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_btf.c

## Purpose

`ksyms_btf.c` validates typed BTF ksyms, percpu DATASEC handling, null-check enforcement, weak ksyms in normal and light skeletons, and write protection for ksym references.

## Important APIs, Types, and Functions

The file uses `test_ksyms_btf.skel.h`, null-check, weak, lskel, and write-check skeletons; `libbpf_find_kernel_btf()`, `btf__find_by_name_kind()`, `kallsyms_find()`, skeleton attach, and BSS result fields.

## Control Flow and Data Flow

The top-level test confirms kernel BTF and PERCPU DATASEC support, then runs subtests. Basic resolves `runqueues` and `bpf_prog_active`, attaches the skeleton, and compares addresses/values. Null-check expects load failure when required checks are absent. Weak ksym tests verify existing/missing typed and typeless symbol outputs for both skeleton styles. Write checks disable one handler at a time and expect load rejection.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is kernel BTF handle, skeleton BSS outputs, and verifier load results. Dependencies include vmlinux BTF with percpu DATASEC, kallsyms, and typed ksym support. Integration is libbpf ksym relocation with BTF types and verifier protections. Risks are kernel BTF shape differences, symbol visibility, and CHECK-style legacy assertions. Test signals are address/value matches, expected null-check load failure, weak symbol outputs, and write-check load failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_module.c

## Purpose

`ksyms_module.c` verifies module ksym resolution through both light skeleton and normal libbpf skeleton paths.

## Important APIs, Types, and Functions

It uses `test_ksyms_module.lskel.h`, `test_ksyms_module.skel.h`, `bpf_prog_test_run_opts()`, and BSS field `out_bpf_testmod_ksym`.

## Control Flow and Data Flow

Two subtests load the lskel and normal skeleton, run the `load` program with empty test-run options, assert zero retval, and check that the module ksym value read by BPF equals 42.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS module-symbol output and loaded skeleton resources. Dependencies include `bpf_testmod` and module BTF/ksym exposure. Integration is module ksym relocation in both skeleton implementations. Risks are missing module or changed test symbol value. Test signals are zero test-run retval and `out_bpf_testmod_ksym == 42` in both subtests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ksyms_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/l4lb_all.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/l4lb_all.c

## Purpose

`l4lb_all.c` validates three L4 load-balancer BPF object variants: inline, noinline, and noinline dynptr.

## Important APIs, Types, and Functions

The harness uses `bpf_prog_test_load()` for sched_cls programs, `bpf_find_map()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_prog_test_run_opts()`, packet fixtures `pkt_v4`/`pkt_v6`, and per-CPU stats sized by `bpf_num_possible_cpus()`.

## Control Flow and Data Flow

For each object file, it configures `vip_map`, `ch_rings`, and `reals`, runs IPv4 and IPv6 packets for `NUM_ITER`, checks `TC_ACT_REDIRECT`, output sizes, and magic marker, then sums per-CPU `stats` bytes/packets and checks totals for both packet families.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BPF maps for VIPs, consistent-hash rings, real servers, output packet buffer, and stats. Dependencies include the three BPF object files and sched_cls test-run support. Integration is packet rewriting/load-balancer logic and dynptr parity. Risks are object/map name drift and per-CPU stats aggregation mistakes. Test signals are redirect retval 7, IPv4 output size 54, IPv6 output size 74, expected magic value, and aggregate bytes/packets equal to `MAGIC_BYTES * NUM_ITER * 2` and `NUM_ITER * 2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/l4lb_all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/legacy_printk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/legacy_printk.c

## Purpose

`legacy_printk.c` verifies both legacy and modern `bpf_printk`-style paths, while allowing the modern variant to fail loading on older kernels.

## Important APIs, Types, and Functions

It uses `test_legacy_printk.skel.h`, toggles autoload for `handle_legacy` or `handle_modern`, updates/reads maps for the legacy path, uses BSS variables for the modern path, attaches the skeleton, and sleeps briefly to trigger.

## Control Flow and Data Flow

`test_legacy_printk()` requires `execute_one_variant(true)` to succeed. The legacy variant writes current PID into `my_pid_map`, attaches, then reads `res_map`. The modern variant sets `bss->my_pid_var`, attaches if load succeeded, and reads `bss->res_var`; its return is not asserted by the top-level test.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is map-stored PID/result for legacy mode and BSS PID/result for modern mode. Dependencies include trace attachment support and kernel support for modern printk globals if that variant is to pass. Integration is compatibility between legacy map-based and modern global-variable-based printk use. Risks are load failure accepted for modern path and trigger timing via `usleep(1)`. Test signal is legacy result greater than zero; modern result greater than zero when load succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/legacy_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_get_fd_by_id_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_get_fd_by_id_opts.c

## Purpose

`libbpf_get_fd_by_id_opts.c` tests `*_get_fd_by_id_opts()` open flags, especially read-only map FD behavior, and verifies unsupported opts for prog/link/BTF get-by-id calls.

## Important APIs, Types, and Functions

The harness uses `test_libbpf_get_fd_by_id_opts.skel.h`, `bpf_map_get_info_by_fd()`, `bpf_map_get_fd_by_id()`, `bpf_map_get_fd_by_id_opts()`, `bpf_prog_get_fd_by_id_opts()`, `bpf_link_get_fd_by_id_opts()`, `bpf_btf_get_fd_by_id_opts()`, and `BPF_F_RDONLY`.

## Control Flow and Data Flow

After skeleton load/attach, it gets the `data_input` map ID. Legacy get-by-id and opts-NULL get-by-id are expected to fail in this test context, while opts with read-only flag should return an FD. Lookup through the read-only FD must work; update through it must fail; update through the original FD must work. Prog/link/BTF opts calls with ID 0 and read-only opts must return `-EINVAL`.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is map ID/FD and one map value. Dependencies include kernel support for map get-by-id open flags. Integration is libbpf syscall wrappers and map FD access mode. Risks are permission-sensitive behavior around get-by-id without opts and exact `-EINVAL` for unsupported object types. Test signals are read-only lookup success, read-only update failure, normal update success, and expected `-EINVAL` for prog/link/BTF opts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_get_fd_by_id_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_probes.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_probes.c

## Purpose

`libbpf_probes.c` validates libbpf feature-probing helpers for BPF program types, map types, and selected helpers.

## Important APIs, Types, and Functions

It parses `/sys/kernel/btf/vmlinux` with `btf__parse()`, enumerates `enum bpf_prog_type` and `enum bpf_map_type`, and calls `libbpf_probe_bpf_prog_type()`, `libbpf_probe_bpf_map_type()`, and `libbpf_probe_bpf_helper()`.

## Control Flow and Data Flow

Program-type and map-type tests enumerate kernel BTF enum values, skip `UNSPEC` and max sentinels, create one subtest per enum, and assert libbpf probe result is supported. Helper tests use a small fixed table of supported/unsupported helper/program-type pairs and compare boolean results.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is only the parsed BTF object. Dependencies include vmlinux BTF and kernel support for probing all enumerated types. Integration is libbpf feature probe behavior against the running kernel's ABI. Risks are kernels exposing enum values that probing intentionally reports unsupported and helper support changing over time. Test signals are probe result 1 for all real enum types and table-expected helper support values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_str.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_str.c

## Purpose

`libbpf_str.c` verifies libbpf string conversion coverage for attach types, link types, map types, and program types.

## Important APIs, Types, and Functions

The file uses vmlinux BTF enum enumeration, `libbpf_bpf_attach_type_str()`, `libbpf_bpf_link_type_str()`, `libbpf_bpf_map_type_str()`, `libbpf_bpf_prog_type_str()`, and a local `uppercase()` helper.

## Control Flow and Data Flow

Each subtest parses BTF, finds the relevant enum, iterates values excluding max sentinels, converts enum value to libbpf string, reconstructs the expected uppercase kernel enum name with the correct prefix, and compares. Deprecated cgroup storage duplicate enum names are skipped because libbpf returns the non-deprecated spelling.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the parsed BTF object and temporary string buffers. Dependencies include complete vmlinux BTF enums and libbpf conversion tables. Integration is human-readable string API coverage for all kernel enum values. Risks are new enum values without libbpf table updates, duplicate enum aliases, and naming exceptions. Test signals are non-NULL strings and exact reconstructed enum names for all covered values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/link_pinning.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/link_pinning.c

## Purpose

`link_pinning.c` validates BPF link pinning to BPFFS, reopening pinned links, unpinning, and attachment lifetime after FD destruction.

## Important APIs, Types, and Functions

The test uses `test_link_pinning.skel.h`, `bpf_program__attach()`, `bpf_link__pin()`, `bpf_link__pin_path()`, `bpf_link__open()`, `bpf_link__unpin()`, `bpf_link__destroy()`, `stat()`, and BSS `in`/`out` trigger fields.

## Control Flow and Data Flow

For raw tracepoint and tp_btf programs, it attaches, verifies BSS output follows input, pins to `/sys/fs/bpf/pinned_link_test`, verifies path and file, destroys the original FD while expecting the pinned link to remain active, reopens it, unpins while FD remains open, verifies continued activity, then destroys the final FD and loops until output stops changing.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is a pinned BPFFS link path, open link FDs, and BSS input/output values. Dependencies include mounted/writable BPFFS at `/sys/fs/bpf`, raw_tp and tp_btf attach support, and trigger timing. Integration is link pin persistence and libbpf pin path tracking. Risks are stale pinned path from prior failures, delayed detach, and permission issues on BPFFS. Test signals are BSS output tracking through pin/destroy/open/unpin phases and eventual detachment after final destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/link_pinning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_funcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_funcs.c

## Purpose

`linked_funcs.c` validates linked BPF functions and weak function behavior across two manually autoloaded raw tracepoint handlers.

## Important APIs, Types, and Functions

It uses `linked_funcs.skel.h`, enables autoload for `handler1` and `handler2`, sets rodata `my_tid`, BSS `syscall_id`, loads/attaches the skeleton, triggers `SYS_getpgid`, and checks BSS outputs.

## Control Flow and Data Flow

The handlers are optional sections by default, so the harness enables them before load. After attach, the syscall trigger causes both handlers to execute linked functions. The test asserts computed output values, captured syscall context, and weak function results.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is rodata filter TID, BSS syscall id, and output fields. Dependencies include raw tracepoint attach, syscall availability, and linked subprogram/weak symbol support. Integration is BPF static linking across functions and optional program autoload. Risks are missing trigger due to TID/syscall filtering or changes in paired BPF computations. Test signals are `output_val1 == 4000`, `output_ctx1 == SYS_getpgid`, `output_weak1 == 42`, `output_val2 == 6000`, `output_ctx2 == SYS_getpgid`, and `output_weak2 == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_funcs.c -->

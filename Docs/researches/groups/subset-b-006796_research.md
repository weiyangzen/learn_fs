# Research: subset-b-006796

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter.c

## Purpose
This selftest is the broad regression harness for BPF iterator attachment, iterator file descriptors, bpffs-pinned iterator links, map-scoped iterators, task/socket/VMA iterators, and verifier rejection of invalid iterator programs. It validates both generic iterator mechanics and many target-specific iterator contracts by loading generated libbpf skeletons from `tools/testing/selftests/bpf/progs`.

## Important APIs, Types, And Functions
The file centers on `bpf_program__attach_iter()`, `bpf_iter_create()`, `bpf_link__pin()`, `bpf_link__update_program()`, `bpf_link_get_info_by_fd()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_map_get_info_by_fd()`, `sys_pidfd_open()`, `get_uprobe_offset()`, `kern_sync_rcu()`, and the skeleton APIs generated from the many included `bpf_iter_*.skel.h` headers. `union bpf_iter_link_info` and `struct bpf_iter_attach_opts` are used to scope iterators to task IDs, PID FDs, and particular maps.

## Control Flow
`test_bpf_iter()` initializes a mutex and dispatches dozens of subtests through `test__start_subtest()`. Common helpers attach an iterator program, create an iterator FD, drain it with `read()`, and destroy the link. Specialized paths check task selection by TID/PID/PIDFD, sleepable task access with a forked child, task stacks and files, BTF rendering of `task_struct`, TCP/UDP/UNIX socket iterators, anonymous and bpffs-pinned iterator links, seq-file overflow/restart behavior, map iterators for hash/array/per-CPU maps, socket local storage iteration and mutation, BPF link/ksym iterators, task VMA output versus `/proc/<pid>/maps`, dead-task VMA stability, sockmap iterator lifetime, and VMA offset calculation.

## State And Persistence Behavior
Most state is transient kernel object state held by skeleton BSS/data, iterator links, iterator FDs, maps, sockets, threads, child processes, and pinned bpffs paths. `test_file_iter()` persists an iterator link at `/sys/fs/bpf/bpf_iter_test1` long enough to validate file-based reads and link program replacement, then unlinks it. Map iterator lifetime tests deliberately destroy links and skeletons before draining iterator FDs to prove the iterator keeps required references alive across RCU grace periods.

## Dependencies And Integration Points
The test depends on libbpf skeleton generation, bpffs at `/sys/fs/bpf`, procfs maps, pthreads, fork/wait, kernel RCU synchronization helpers, pidfd support, socket APIs, BTF support, and the BPF selftest harness. It integrates with BPF program files such as `bpf_iter_tasks`, `bpf_iter_task_vmas`, `bpf_iter_bpf_hash_map`, `bpf_iter_bpf_sk_storage_map`, and `bpf_iter_sockmap`.

## Risks And Edge Cases
Risk concentrates around kernel-version-sensitive iterator targets, timing-sensitive thread/process counts, short-lived processes during VMA iteration, seq-file overflow semantics, and resource cleanup after early assertions. Several checks rely on expected verifier failures and exact errno values. The test mutates bpffs and opens many kernel resources, so cleanup of FDs, links, sockets, maps, child processes, and pinned paths is critical.

## Test Signals
Passing signals include successful skeleton loads and iterator attachment, nonnegative read termination, expected BSS counters, exact map value sums, expected `E2BIG`, `EACCES`, or load failures for invalid programs, matching first-line VMA output against `/proc/<pid>/maps`, stable link info, and successful reads after premature map/link closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt.c

## Purpose
This serial selftest verifies that a TCP BPF iterator can call socket option helpers to change congestion control on listening, reuseport listening, established, and accepted TCP sockets. It specifically migrates sockets from the test `bpf_cubic` congestion-control implementation to `bpf_dctcp`.

## Important APIs, Types, And Functions
Key helpers are `create_netns()`, `set_bpf_cubic()`, `check_bpf_dctcp()`, `make_established()`, `get_local_port()`, `do_bpf_iter_setsockopt()`, and `serial_test_bpf_iter_setsockopt()`. It uses `unshare(CLONE_NEWNET)`, `system("ip link set dev lo up")`, `start_server()`, `start_reuseport_server()`, `connect_to_fd()`, `accept()`, `setsockopt(TCP_CONGESTION)`, `getsockopt(TCP_CONGESTION)`, `bpf_program__attach_iter()`, `bpf_iter_create()`, and struct_ops attachment through `bpf_map__attach_struct_ops()`.

## Control Flow
The entry point creates a private network namespace, loads and attaches the iterator skeleton, then loads and attaches `bpf_cubic` and `bpf_dctcp` struct_ops. `do_bpf_iter_setsockopt()` creates one non-reuseport listener and 256 accepted/established connections, creates 256 reuseport listeners, records the listen ports in the iterator BSS, drains the iterator FD, and then checks every participating socket reports `bpf_dctcp` as its congestion algorithm. The same workflow runs with `random_retry` enabled and disabled.

## State And Persistence Behavior
State is transient in the new network namespace, socket FDs, congestion-control struct_ops links, and iterator skeleton BSS fields `listen_hport`, `reuse_listen_hport`, and `random_retry`. The test leaves no intended persistent state; all sockets, links, and skeletons are destroyed in `done` paths.

## Dependencies And Integration Points
It depends on network namespace support, loopback configuration via `ip`, TCP congestion-control socket options, BPF iterator helpers, and the `bpf_iter_setsockopt`, `bpf_cubic`, and `bpf_dctcp` BPF programs. It integrates with selftest network helpers for server setup, reuseport fanout, connection creation, and FD cleanup.

## Risks And Edge Cases
The test is resource-heavy because it creates hundreds of sockets twice. It can fail if network namespaces are unavailable, `ip` is missing, loopback cannot be brought up, struct_ops TCP CA attachment is unsupported, or congestion-control names collide with system algorithms. Read handling tolerates `EAGAIN` retry from iterator draining.

## Test Signals
Passing signals are successful netns setup, successful struct_ops attachment, all sockets initially accepting `bpf_cubic`, iterator read completion without error, and `check_bpf_dctcp()` returning the full socket count for reuseport listeners, normal listener, established clients, and accepted server sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt_unix.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt_unix.c

## Purpose
This selftest validates that a UNIX-domain socket iterator can use BPF get/set socket option helpers on `SO_SNDBUF`. It covers abstract AF_UNIX socket discovery and confirms helper-observed values match userspace getsockopt results.

## Important APIs, Types, And Functions
The main helpers are `create_unix_socket()`, `test_sndbuf()`, and `test_bpf_iter_setsockopt_unix()`. It uses `socket(AF_UNIX, SOCK_STREAM)`, abstract `sockaddr_un` binding, `getsockname()`, `bpf_program__attach_iter()`, `bpf_iter_create()`, `read()`, userspace `setsockopt(SO_SNDBUF)`, and `getsockopt(SO_SNDBUF)`.

## Control Flow
The entry point loads `bpf_iter_setsockopt_unix`, creates an abstract UNIX socket, copies the kernel-assigned abstract path into skeleton BSS so the BPF iterator can identify the socket, attaches the `change_sndbuf` iterator program, drains the iterator FD while tolerating `EAGAIN`, then runs five userspace comparisons in `test_sndbuf()`.

## State And Persistence Behavior
All state is transient: one AF_UNIX socket FD, skeleton data arrays for BPF-observed send-buffer values, BSS arrays for expected userspace values, and one iterator link. No filesystem path is created because the socket is abstract.

## Dependencies And Integration Points
The test depends on AF_UNIX abstract sockets, BPF iterator support for UNIX sockets, generated `bpf_iter_setsockopt_unix.skel.h`, and the selftest assertion framework. It integrates userspace socket option operations with BPF-side option helper effects.

## Risks And Edge Cases
The test assumes the abstract socket path copied from `getsockname()` is sufficient for the BPF program to match the socket. Cleanup is minimal and relies on skeleton destruction and process FD cleanup. It must handle Linux doubling or normalizing `SO_SNDBUF` values by comparing BPF-observed results against userspace `getsockopt()` after the same set operation.

## Test Signals
Passing signals are successful socket creation and abstract bind, iterator attach/create/read success, nonnegative BPF helper result slots, successful userspace set/get operations, and exact equality between each BPF-recorded send-buffer value and the corresponding userspace expected value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter_setsockopt_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_loop.c

## Purpose
This selftest validates behavior of the `bpf_loop` helper through a generated skeleton that exposes multiple BPF programs. It checks normal loop counts, early callback stop, null callback context, invalid flags, nested loops, nonconstant callback selection, and stack/map behavior across loop callbacks.

## Important APIs, Types, And Functions
Important functions are `check_nr_loops()`, `check_callback_fn_stop()`, `check_null_callback_ctx()`, `check_invalid_flags()`, `check_nested_calls()`, `check_non_constant_callback()`, `check_stack()`, and `test_bpf_loop()`. The userspace side uses `bpf_program__attach()`, skeleton BSS/data fields, `bpf_map_update_elem()`, and `bpf_map_lookup_elem()`.

## Control Flow
`test_bpf_loop()` opens and loads `bpf_loop`, sets the test PID in BSS, and runs each subtest. Each subtest attaches one BPF program, mutates control fields in BSS/data, sleeps briefly so the attached program can run, then checks output fields or map values. The stack test prepopulates a map, runs the BPF program, and confirms every value was incremented.

## State And Persistence Behavior
State is kept in the skeleton's BSS/data and one BPF map. Attachments are temporary links destroyed after each check. There is no persistent filesystem state. Because the program execution is asynchronous relative to userspace writes, the test uses small sleeps to allow attached programs to observe BSS changes.

## Dependencies And Integration Points
It depends on the `bpf_loop` BPF program skeleton, the selftest harness, and whatever attach point the skeleton programs use. It integrates helper return semantics with userspace-visible BSS counters and a BPF map used for stack callback verification.

## Risks And Edge Cases
Timing is the main risk: the test assumes `usleep(1)` is enough for the attached BPF program to execute and update BSS state. It also checks exact errno values for too many loops and invalid flags, so kernel helper contract changes would be visible.

## Test Signals
Passing signals include exact returned loop counts for zero and 500 loops, `-E2BIG` for excessive loop count, early stop at `stop_index + 1`, `-EINVAL` for flags, correct nested-loop multiplication, correct selected callback output, and map values incremented by one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_mod_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_mod_race.c

## Purpose
This serial selftest constructs a verifier/module lifetime race around `btf_try_get_module()` while `bpf_testmod` is still in `MODULE_STATE_COMING`. It verifies that BPF programs referring to module ksyms or kfuncs fail to load with `ENXIO` instead of taking references to an uninitialized module that could later be freed.

## Important APIs, Types, And Functions
Key pieces are `struct test_config`, `enum bpf_test_state`, atomic global `state`, `load_module_thread()`, `sys_userfaultfd()`, `test_setup_uffd()`, `test_bpf_mod_race_config()`, `ksym_config`, `kfunc_config`, and `serial_test_bpf_mod_race()`. It uses `mmap()`, `userfaultfd`, `UFFDIO_API`, `UFFDIO_REGISTER`, pthreads, `load_bpf_testmod()`, `unload_bpf_testmod()`, `kern_sync_rcu()`, and skeletons `bpf_mod_race`, `ksym_race`, and `kfunc_call_race`.

## Control Flow
For each config, the test maps a faulting page, unloads `bpf_testmod`, loads and attaches an fmod_ret BPF program configured to fault on that page during module init, registers the address with userfaultfd, and starts a module-loading thread. Once the BPF program is known to be blocked in the page fault and the module is still initializing, the test attempts to load either a ksym-using or kfunc-using program. Correct behavior is load failure with `ENXIO`; then closing userfaultfd unblocks module loading so the injected error frees the module path safely.

## State And Persistence Behavior
State spans an atomic test-state enum, skeleton BSS/data fields, a userfaultfd registration, a thread running module load, and the loaded/unloaded `bpf_testmod` kernel module. Cleanup restores `bpf_testmod`, destroys skeletons, waits for RCU, unmaps memory, and resets the atomic state.

## Dependencies And Integration Points
It requires `bpf_testmod`, userfaultfd support, module loading permissions, pthreads, fmod_ret program attachment, BTF/kfunc/ksym verifier paths, and the selftest helper library. It directly integrates with kernel module lifecycle and verifier module-reference handling.

## Risks And Edge Cases
This is timing- and privilege-sensitive. Failure to observe the block, userfaultfd restrictions, blocked module thread cleanup, or exact verifier errno changes can affect results. The test intentionally handles the dangerous success case by closing userfaultfd, waiting for the injected failure path, syncing RCU, and destroying the unexpectedly loaded skeleton.

## Test Signals
Passing signals are module load blocking before init completes, a userfaultfd page-fault event, failed ksym/kfunc program load with `errno == ENXIO`, `res_try_get_module == false`, module-load thread ending in `TS_MODULE_LOAD_FAIL`, successful RCU sync, and successful restoration of `bpf_testmod`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_mod_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_nf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_nf.c

## Purpose
This selftest validates BPF netfilter connection-tracking kfunc behavior for XDP and TC/SKB programs, including successful allocation, insertion, lookup, NAT/status/timeout mutation, zone handling, and expected verifier failures for invalid kfunc usage.

## Important APIs, Types, And Functions
Important elements include `test_bpf_nf_fail_tests`, `connect_to_server()`, `test_bpf_nf_ct()`, `test_bpf_nf_ct_fail()`, and `test_bpf_nf()`. It uses `iptables-legacy` to enable conntrack, `start_server()`, `connect_fd_to_fd()`, `accept()`, `bpf_prog_test_run_opts()`, verifier log buffers via `bpf_object_open_opts`, `bpf_object__find_program_by_name()`, and skeletons `test_bpf_nf` and `test_bpf_nf_fail`.

## Control Flow
`test_bpf_nf()` runs two positive subtests, one with the XDP program and one with the TC/SKB program. `test_bpf_nf_ct()` checks for `iptables-legacy`, loads the skeleton, adds a raw-table CONNMARK rule to enable conntrack, creates a loopback TCP connection, stores tuple fields in BSS, runs the selected program with `pkt_v4`, and verifies BSS/data results. It then removes the iptables rule and destroys resources. Negative subtests autoload one invalid program at a time and assert load failure plus an expected verifier-log substring.

## State And Persistence Behavior
The test temporarily mutates the system's iptables raw PREROUTING chain, opens TCP sockets, and uses skeleton BSS/data to hold tuple fields and result codes. The iptables rule is removed on exit from the positive test path. Verifier log state is held in a static 1 MiB buffer.

## Dependencies And Integration Points
It depends on `iptables-legacy`, conntrack support, IPv4 TCP sockets, BPF kfunc support for netfilter conntrack, XDP and SCHED_CLS program execution through test-run APIs, and selftest packet fixtures such as `pkt_v4`.

## Risks And Edge Cases
The test is environment-sensitive because missing `iptables-legacy` causes skip and rule cleanup relies on command execution. Timeout and ct timeout assertions allow a narrow range, so slow systems can be noisy. Negative tests depend on exact verifier diagnostic substrings.

## Test Signals
Positive pass signals include expected errno results for invalid options, successful new and existing conntrack lookups, timeout/status changes, mark values, NAT operations, and zone-specific lookup behavior. Negative pass signals are load failure and matching verifier messages for each invalid kfunc pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_nf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_id.c

## Purpose
This serial selftest validates kernel object ID enumeration and info retrieval for BPF programs, maps, and links. It loads two identical raw tracepoint programs, records their map/program/link info, and confirms get-by-id and get-next-id APIs expose consistent metadata.

## Important APIs, Types, And Functions
The entry point is `serial_test_bpf_obj_id()`. It uses `bpf_prog_test_load()`, `bpf_find_map()`, `bpf_map_update_elem()`, `bpf_object__find_program_by_name()`, `bpf_program__attach()`, `bpf_map_get_info_by_fd()`, `bpf_prog_get_info_by_fd()`, `bpf_link_get_info_by_fd()`, `bpf_prog_get_next_id()`, `bpf_map_get_next_id()`, `bpf_link_get_next_id()`, and get-FD-by-ID variants for prog/map/link.

## Control Flow
The test first verifies ID zero cannot be resolved for program, map, or link. It then loads `test_obj_id.bpf.o` twice, updates each map with a magic value, attaches each raw tracepoint program, and records map, program, and link metadata. It enumerates all program IDs, finds the two loaded programs, checks a negative `EFAULT` case for missing `map_ids`, and compares retrieved info. It repeats analogous enumeration and comparison for maps and links.

## State And Persistence Behavior
State consists of two loaded BPF objects, two program FDs, two map FDs, two BPF links, captured `bpf_*_info` structures, instruction buffers, map ID buffers, and a magic array value. No bpffs pinning is used. All links are destroyed and objects closed in the `done` cleanup loop.

## Dependencies And Integration Points
It depends on `test_obj_id.bpf.o`, raw tracepoint support, JIT status exposed in `env.jit_enabled`, kernel object ID APIs, and stable metadata fields such as names, UID, load time, map IDs, and raw tracepoint name.

## Risks And Edge Cases
ID enumeration is global and can race with other BPF objects disappearing, so the code tolerates `ENOENT` for objects in the "dead row." Load time comparison allows a 60-second window. JIT instruction assertions are conditional on `env.jit_enabled`.

## Test Signals
Passing signals are `ENOENT` for ID zero, correct map/program/link metadata lengths and fields, nonzero translated instructions, expected JIT data when JIT is enabled, correct created UID and load time, matching map IDs and magic values, raw tracepoint link info for `sys_enter`, and finding both loaded objects during enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_pinning.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_pinning.c

## Purpose
This selftest validates BPF object pin/get behavior through both detached bpffs mounts and normally mounted bpffs paths. It specifically exercises the newer `BPF_F_PATH_FD` path mode for `bpf_obj_pin_opts()` and `bpf_obj_get_opts()`.

## Important APIs, Types, And Functions
Important wrappers are `sys_fsopen()`, `sys_fsconfig()`, `sys_fsmount()`, and unused `sys_move_mount()`. Test helpers include `bpf_obj_pinning_detached()`, `validate_pin()`, `validate_get()`, `bpf_obj_pinning_mounted()`, and `test_bpf_obj_pinning()`. It uses `bpf_map_create()`, `bpf_obj_pin_opts()`, `bpf_obj_get_opts()`, `bpf_obj_pin()`, `bpf_obj_get()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `open(O_PATH)`, `chdir()`, and `unlink()`.

## Control Flow
The detached subtest creates a detached bpffs mount with the new mount API, creates an array map, pins it relative to the detached mount FD, retrieves it relative to that same mount FD, and verifies both FDs access the same map contents. Mounted subtests create an array map and validate pin/get through three path forms: absolute string, cwd-relative string under `/sys/fs/bpf`, and directory-FD-relative path using `BPF_F_PATH_FD`.

## State And Persistence Behavior
Persistent state is intentionally short-lived: bpffs pins under `/sys/fs/bpf/<map_name>` for mounted cases and an unexposed detached mount for the detached case. Cleanup closes map, fs, and mount FDs and unlinks mounted pins. Relative-path tests temporarily change cwd and restore it.

## Dependencies And Integration Points
It depends on bpffs mounted at `/sys/fs/bpf`, support for `fsopen/fsconfig/fsmount`, `BPF_F_PATH_FD`, array maps, and libbpf internal headers for option structures. It integrates BPF syscalls with Linux VFS mount and path resolution behavior.

## Risks And Edge Cases
The detached mount path depends on modern mount API availability and privileges. Relative-path tests can affect process cwd if restoration fails, so cleanup is important. The mounted pin name is fixed and can collide with stale pins from interrupted runs.

## Test Signals
Passing signals are successful detached bpffs creation, successful pin/get through mount FD, successful pin/get through absolute, relative, and FD-relative mounted paths, and matching map values read through a second FD after updates through the first FD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_pinning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_qdisc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_qdisc.c

## Purpose
This selftest validates BPF qdisc struct_ops attachment and behavior for FIFO and FQ qdiscs, attachment constraints under classful/multiqueue qdiscs, incomplete operation rejection, and default-qdisc integration.

## Important APIs, Types, And Functions
Core helpers are `do_test()`, `test_fifo()`, `test_fq()`, `test_qdisc_attach_to_mq()`, `test_qdisc_attach_to_non_root()`, `test_incompl_ops()`, `get_default_qdisc()`, `test_default_qdisc_attach_to_mq()`, `test_ns_bpf_qdisc()`, and `serial_test_bpf_qdisc_default()`. It uses `bpf_tc_hook_create()`, `bpf_tc_hook_destroy()`, `bpf_map__attach_struct_ops()`, selftest network helpers, `tc`/`ip` shell commands, and `/proc/sys/net/core/default_qdisc`.

## Control Flow
FIFO and FQ tests load and attach their qdisc skeletons, create a BPF TC qdisc hook on loopback root, transfer 10 MiB over a TCP connection, and destroy the hook. Multiqueue tests attach `bpf_fifo`, create veth devices, add `mq`, and attach BPF qdisc to a child queue. Non-root attachment creates HTB on loopback and asserts BPF qdisc attachment below a class fails. The default-qdisc test temporarily writes `bpf_fifo` to the sysctl, creates a netns and veth, adds `mq`, and checks the BPF qdisc init callback ran.

## State And Persistence Behavior
State includes temporary qdiscs on loopback or veth devices, temporary veth devices, struct_ops links, a private netns object, TCP sockets, and a temporary sysctl override. Cleanup removes qdiscs, frees netns, restores the saved default qdisc, and destroys skeletons.

## Dependencies And Integration Points
It depends on `tc`, `ip`, rtnetlink/qdisc support, loopback ifindex 1, veth support, network helper utilities, BPF TC hook APIs, and BPF qdisc skeletons. It integrates BPF struct_ops qdiscs with normal Linux traffic-control configuration.

## Risks And Edge Cases
The test mutates network configuration and `/proc/sys/net/core/default_qdisc`, so cleanup and namespace isolation are important. Fixed interface names and loopback ifindex assumptions can collide with external state. Missing privileges or qdisc support will fail setup.

## Test Signals
Passing signals include successful traffic through `bpf_fifo` and `bpf_fq`, success attaching to an `mq` child, failure attaching to a non-root HTB class, failure attaching incomplete qdisc ops, and `init_called == true` when `bpf_fifo` is selected as the default qdisc under `mq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_qdisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_tcp_ca.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_tcp_ca.c

## Purpose
This selftest validates BPF TCP congestion-control struct_ops programs, including DCTCP and Cubic behavior, socket-local storage interaction, autoattach, license and helper restrictions, fallback behavior, link update semantics, unsupported operation rejection, and TCP CA kfunc loading.

## Important APIs, Types, And Functions
Important helpers include `settcpca()`, `start_test()`, `do_test()`, `cc_cb()`, `stg_post_socket_cb()`, `libbpf_debug_print()`, and test functions such as `test_cubic()`, `test_dctcp()`, `test_dctcp_autoattach_map()`, `test_invalid_license()`, `test_dctcp_fallback()`, `test_rel_setsockopt()`, `test_update_ca()`, `test_update_wrong()`, `test_mixed_links()`, `test_multi_links()`, `test_link_replace()`, `test_tcp_ca_kfunc()`, and `test_cc_cubic()`. It uses `setsockopt(TCP_CONGESTION)`, `getsockopt()`, `bpf_map__attach_struct_ops()`, `bpf_link__update_map()`, and `bpf_link_update()`.

## Control Flow
`test_bpf_tcp_ca()` dispatches subtests. Positive congestion-control tests load a skeleton, attach its struct_ops map, set sockets to the BPF CA name through network helper callbacks, send 10 MiB, and inspect BSS counters or socket-local storage values. Negative tests install libbpf print hooks to verify expected verifier/libbpf warnings, or attach incomplete/unsupported struct_ops and expect failure. Link update tests attach one CA map, run traffic, update or replace the backing map, then verify either new counters advanced or invalid updates failed.

## State And Persistence Behavior
State is transient in TCP sockets, struct_ops links, BPF maps, BSS counters, libbpf print callback globals `err_str` and `found`, and socket-local storage. The file does not pin objects. The fallback test checks recursive `setsockopt(TCP_CONGESTION)` behavior during CA init and reads the resulting server-side algorithm.

## Dependencies And Integration Points
It depends on IPv6 TCP loopback helpers, BPF struct_ops support for TCP congestion control, generated skeletons for several valid and invalid CA programs, socket-local storage maps, libbpf logging, and kernel support for link update/replace semantics.

## Risks And Edge Cases
Traffic volume and TCP state transitions make the test timing-sensitive. Exact warning substrings are part of negative checks. System congestion-control availability, permissions, and struct_ops feature support can gate execution. Link update tests rely on precise map compatibility checks.

## Test Signals
Passing signals include data transfer success, BPF Cubic ack callbacks, DCTCP socket-local storage result `0xeB9F`, expected GPL/helper/unsupported-op diagnostics, fallback to `cubic` with `-ENOTSUPP` and `EBUSY` counts, rejection of incomplete ops, successful and failed map updates as appropriate, successful `BPF_F_REPLACE` only with the correct old map FD, and successful TCP CA kfunc skeleton load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_tcp_ca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_verif_scale.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_verif_scale.c

## Purpose
This file is a verifier scalability harness. It loads a collection of prebuilt BPF object files with selected program types to ensure large programs, loops, subprograms, open-coded iterators, and helper-based loops remain within verifier limits or fail when intentionally invalid.

## Important APIs, Types, And Functions
The core helpers are `libbpf_debug_print()`, `check_load()`, and `scale_test()`. Individual entry points call `scale_test()` for each BPF object, including `test_verif_scale1/2/3`, many `pyperf*` variants, `loop*` variants, `strobemeta*`, sysctl loop tests, XDP, SEG6 local, and `twfw`. It uses `bpf_object__open_file()`, `bpf_object__next_program()`, `bpf_program__set_type()`, `bpf_program__set_flags()`, `bpf_program__set_log_level()`, and `bpf_object__load()`.

## Control Flow
Each exported test function is independent and loads one object file. `check_load()` opens the object, selects the first program, sets the requested program type and testing flags, requests verifier log level 4 plus global extra flags, loads the object, closes it, and returns the load result. `scale_test()` optionally installs a debug print callback when `env.verifier_stats` is enabled, then asserts success or failure.

## State And Persistence Behavior
No BPF object is retained after the load check; `bpf_object__close()` always releases it. Global state touched by this file is limited to optional libbpf print callback replacement and `extra_prog_load_log_flags`. No maps, links, sockets, or pinned paths persist.

## Dependencies And Integration Points
It depends on a large set of `.bpf.o` fixtures, the BPF verifier, libbpf, selftest environment flags, and correct program-type selection for each fixture. It integrates with test harness settings such as `env.verifier_stats` and `testing_prog_flags()`.

## Risks And Edge Cases
The tests are sensitive to verifier complexity accounting, instruction limits, compiler output, object availability, and program type support. `loop3.bpf.o` is intentionally expected to fail; if verifier behavior changes, that failure expectation may need updating. Debug printing has a suspicious `vprintf("%s", args)` pattern that relies on the harness path and is only used for stats logging.

## Test Signals
Passing signals are successful loads for all non-failing fixtures, failure for `loop3.bpf.o`, and optional verifier logs when stats are enabled. Because each object is closed immediately, resource leaks should be minimal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_verif_scale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_maps_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_maps_access.c

## Purpose
This selftest validates bpftool access to BPF maps under BPF LSM/security policy. It checks read, BTF dump, write, delete, iterator access, nested map creation, and BTF listing for protected and unprotected maps, both by name and by pinned path.

## Important APIs, Types, And Functions
Important structures and helpers include `enum map_protection`, `struct test_desc`, `general_setup()`, `general_cleanup()`, `update_test_desc()`, `test_setup()`, `test_cleanup()`, `lookup_map_value()`, `read_map_btf_data()`, `write_map_value()`, `delete_map_value()`, `iterate_on_map_values()`, `create_inner_map()`, `create_outer_map()`, `add_outer_map_entry()`, `test_basic_access()`, `test_create_nested_maps()`, `test_btf_list()`, and `test_bpftool_maps_access()`. It uses `run_bpftool_command()`, `security_bpf_map` skeleton attach, bpffs pinning, and shell `cat` for pinned iterators.

## Control Flow
`general_setup()` loads and attaches the security skeleton, initializes protected and unprotected maps, enables protection in a status map, and creates `/sys/fs/bpf/test_bpftool_map`. Each table-driven subtest resolves the skeleton map, optionally pins it, builds a bpftool handle, checks lookup and BTF dump succeed, and checks write/delete either fail or succeed according to protection. It restores deleted values when needed. Iterator access pins `bpf_iter_map_elem.bpf.o` and reads the iterator file. Additional subtests create hash-of-maps nested maps through bpftool and run `btf list`.

## State And Persistence Behavior
The test temporarily creates a bpffs directory, optional map pins, iterator pins, and nested map pins. It also keeps security policy in loaded BPF LSM programs and skeleton maps. Cleanup unpins maps, unlinks iterator and nested-map pins, removes the directory, and destroys the skeleton.

## Dependencies And Integration Points
It depends on bpftool helper wrappers, bpffs, BPF LSM/security programs in `security_bpf_map`, `bpf_iter_map_elem.bpf.o`, map-in-map support, and bpftool command syntax for map lookup/update/delete, BTF dump, iter pin, map create, and BTF list.

## Risks And Edge Cases
Assertions around `write_must_fail` invert bpftool return status intentionally: protected maps should make update/delete fail while lookup/BTF/iteration remain allowed. Fixed bpffs paths can collide with stale state. `iterate_on_map_values()` uses `snprintf(cmd, MAP_NAME_MAX_LEN, "cat %s", iter_pin_path)`, so command length is capped by map-name size rather than full command size.

## Test Signals
Passing signals include successful security skeleton attach, successful initial map seeding, lookup/BTF dump success for all handles, expected write/delete success or failure based on protection, successful map iterator pin/read, nested outer map accepting two entries but rejecting a third, and successful `bpftool btf list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_maps_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_metadata.c

## Purpose
This selftest validates bpftool display of BPF program metadata stored in a `.rodata` metadata map. It covers both unused and used metadata fixtures and checks default and JSON output formats.

## Important APIs, Types, And Functions
Important elements are `struct test_desc`, static `tests[]`, `setup()`, `cleanup()`, `check_metadata()`, `run_test()`, and `test_bpftool_metadata()`. It uses `run_bpftool_command()`, `get_bpftool_command_output()`, bpffs program pinning, `prog load`, `prog show pinned`, `prog -j show pinned`, and `map show name`.

## Control Flow
For each fixture, the entry point creates `/sys/fs/bpf/test_metadata`, loads the BPF object to a pinned bpffs path using bpftool, checks human-readable `prog show` output for expected tokens, checks JSON output for the compact metadata JSON token, verifies the metadata map can be found by name, then unlinks the pin and removes the directory.

## State And Persistence Behavior
State is limited to a temporary bpffs directory, one pinned program path per subtest, static output buffer storage, and the metadata map created by loading the object. Cleanup removes the program pin and directory after each subtest.

## Dependencies And Integration Points
It depends on bpftool command helpers, bpffs, the object files `metadata_unused.bpf.o` and `metadata_used.bpf.o`, and bpftool's metadata rendering for maps named `metadata.rodata`. It integrates BPF object metadata generation with bpftool display and map discovery.

## Risks And Edge Cases
The token checks are substring-based and sensitive to formatting in bpftool output, especially JSON compactness. The setup function ignores its `test` parameter and uses a fixed directory, so stale directories from interrupted runs can cause setup failure. Output larger than 64 KiB would be truncated.

## Test Signals
Passing signals are successful bpffs directory creation, successful program load and pin, expected default-format metadata tokens for `a` and `b`, expected JSON metadata token, successful map lookup by metadata map name, and cleanup of the pinned path and directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_metadata.c -->

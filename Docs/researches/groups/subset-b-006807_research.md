<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.c

## Purpose
Implements the AF_XDP selftest traffic engine used by `test_xsk.h` test specifications. It creates UMEMs and XSK sockets, attaches XDP programs, generates deterministic packet streams, runs threaded TX/RX paths, and validates normal, poll, shared-UMEM, metadata, multibuffer, invalid-descriptor, ring-size, teardown, and `bpf_xdp_adjust_tail()` behavior.

## APIs, Types, and Functions
Public helpers include `test_init()`, `ifobject_create()`, `ifobject_delete()`, `init_iface()`, `xsk_configure_umem()`, `xsk_configure_socket()`, `kick_tx()`, `kick_rx()`, packet-stream helpers, worker thread entry points, and many `testapp_*()` cases referenced from the header tables. Core internal helpers manage UMEM allocation, socket busy-poll options, hardware ring sizing, XDP program reattachment, XSK map updates, packet generation, descriptor validation, statistics validation, and socket/UMEM cleanup.

## Control Flow, State, and Persistence
`test_init()` resets the two `ifobject` instances into TX/RX roles and chooses copy, driver, or zero-copy bind flags. `testapp_validate_traffic()` applies MTU/ring prerequisites, attaches the desired XDP programs, then `__testapp_validate_traffic()` starts RX and TX worker threads with a barrier. RX allocates UMEM, populates fill rings, installs sockets into XSK maps, receives descriptors, validates offsets, payload sequence words, metadata, fragments, and packet lengths, and returns buffers to the fill ring. TX reserves descriptors, writes Ethernet headers and payloads into UMEM, kicks TX, drains completions, and enforces an in-flight pacing counter. Persistent state is all in `test_spec`, `ifobject`, `xsk_socket_info`, `xsk_umem_info`, global packet-in-flight counters, and libbpf skeleton state; no on-disk state is persisted.

## Dependencies and Integration
Depends on libbpf AF_XDP APIs, Linux XDP flags/statistics, pthreads, `network_helpers`, `xsk.h`, `xsk_xdp_common.h`, and `xsk_xdp_progs.skel.h`. It integrates with ethtool ring helpers, `/proc` and `/sys` tunables reported by the header, and generated XDP programs that perform forwarding, dropping, metadata population, shared UMEM routing, and tail adjustment.

## Risks and Test Signals
Risks include timing-sensitive TX/RX loops, driver-specific zero-copy and multibuffer support, hugepage availability for unaligned mode, hardware ring resize flakiness, shared UMEM base-address assumptions, and complex invalid descriptor expectations that differ between aligned and unaligned modes. Strong signals are successful packet count/sequence validation, expected XDP statistics (`rx_dropped`, `rx_ring_full`, fill-empty, invalid TX descriptors), clean socket/UMEM teardown, correct skip behavior for unsupported features, and no timeout in threaded send/receive loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.h

## Purpose
Defines the AF_XDP selftest contract shared by the test harness and `test_xsk.c`. It declares modes, return codes, socket/UMEM/interface/test state, packet stream representation, helper prototypes, and the test case tables.

## APIs, Types, and Functions
Important types are `enum test_mode`, `struct xsk_socket_info`, `struct xsk_umem_info`, `struct ifobject`, `struct pkt`, `struct pkt_stream`, and `struct test_spec`. Function pointer typedefs describe validation callbacks, worker thread entry points, and test case functions. Inline helpers provide integer ceiling division, procfs integer reads, packet-continuation decoding, and mode-name formatting.

## Control Flow, State, and Persistence
The header has no runtime control flow beyond inline helpers, but it defines all state that persists across individual test phases: selected XDP mode, bind flags, ring sizes, XSK map/program pointers, UMEM layout, per-socket packet streams, validation callbacks, MTU, step count, and failure flags. The `tests[]` array lists default cases and `ci_skip_tests[]` isolates flaky, hugepage-dependent, hardware-ring-dependent, long, or otherwise unsuitable cases for CI.

## Dependencies and Integration
Includes Linux ethtool and if_xdp UAPI, kselftest utilities, and local `xsk.h`. It is consumed by AF_XDP test runner code and by `test_xsk.c`; generated XDP skeleton types are forward-referenced through `struct xsk_xdp_progs`.

## Risks and Test Signals
Risks are ABI drift between declarations and implementation, duplicated constants such as packet sizes, and stale CI skip policy. Build failures catch type/prototype drift; runtime signals come from each named `testapp_*()` case being discovered and run under SKB, DRV, or ZC modes as supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/time_tai.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/time_tai.c

## Purpose
Validates BPF access to TAI time by comparing timestamps produced by `test_time_tai` BPF code against user-space `CLOCK_TAI`.

## APIs, Types, and Functions
The file exposes `test_time_tai()`. `ts_to_ns()` converts `timespec` to nanoseconds. It uses `bpf_prog_test_run_opts` with an IPv4 packet and `__sk_buff` context, where the BPF program writes two TAI values into `skb.tstamp` and `skb.cb`.

## Control Flow, State, and Persistence
The skeleton is opened and loaded, the TC/XDP-style test program is run once, and two timestamps are recovered from the output context. Assertions verify nonzero values, monotonic ordering, timestamps not in the future, and a one-second freshness threshold. State is transient in stack variables and the generated skeleton.

## Dependencies and Integration
Depends on `test_progs.h`, `network_helpers.h`, `test_time_tai.skel.h`, `clock_gettime(CLOCK_TAI)`, and `bpf_prog_test_run_opts`.

## Risks and Test Signals
Risks include systems without correct TAI clock support, scheduling delays exceeding the threshold, and context-output layout mismatches. Passing signals are successful skeleton load, program test-run success, nonzero ordered timestamps, and less-than-one-second delta to user-space TAI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/time_tai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer.c

## Purpose
Exercises BPF timer functionality, including normal timer callbacks, async cancellation, spin-lock stress, NMI-context races, map-in-map timer lifetime, verifier failure cases via `timer_failure`, and interrupt-context behavior.

## APIs, Types, and Functions
Test entry points are `serial_test_timer()`, `serial_test_timer_stress()`, `serial_test_timer_stress_async_cancel()`, `serial_test_timer_async_cancel()`, `serial_test_timer_stress_nmi_race()`, `serial_test_timer_stress_nmi_update()`, `serial_test_timer_stress_nmi_cancel()`, and `test_timer_interrupt()`. Helpers include `perf_event_open()`, `spin_lock_thread()`, `timer_stress_runner()`, `run_nmi_test()`, `timer()`, `timer_cancel_async()`, and `test_timer()`.

## Control Flow, State, and Persistence
`test_timer()` opens/loads the `timer` skeleton, skipping on `EOPNOTSUPP`, then invokes a supplied scenario. The normal timer test attaches programs, runs a test program, detaches, sleeps briefly, and checks callback counters, BSS values, pinned callback counters, error flags, and completion bits. Stress tests run many `bpf_prog_test_run_opts()` calls across eight pthreads while toggling async cancellation. NMI tests fork a CPU-consuming child, attach a perf-event program to CPU cycles, and assert hit/update/cancel counters. `test_timer_interrupt()` checks timer callback interrupt context through `timer_interrupt`.

## Dependencies and Integration
Uses libbpf skeletons `timer`, `timer_failure`, and `timer_interrupt`, perf events, pthreads, fork/wait, `bpf_prog_test_run_opts`, and test harness serial entry points. It integrates with kernel timer map value semantics and perf-event attachment.

## Risks and Test Signals
Risks include timing flakiness from short sleeps, perf hardware event unavailability, races that are hard to reproduce, and architecture/preemption differences in interrupt accounting. Signals are exact counter values, zero BPF-side error flags, expected verifier failures from `RUN_TESTS(timer_failure)`, perf-event skip on unsupported hardware, and no hangs under concurrent timer operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_crash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_crash.c

## Purpose
Regression test for BPF timer crash scenarios against array and hash maps.

## APIs, Types, and Functions
Defines `MODE_ARRAY`, `MODE_HASH`, `test_timer_crash_mode()`, and public `test_timer_crash()`.

## Control Flow, State, and Persistence
For each subtest, the skeleton is opened and loaded, `pid` and `crash_map` are written into BSS, the program is attached, and the test sleeps briefly to allow the timer path to execute. There is no persistent user-space state beyond skeleton BSS and the temporary attachment.

## Dependencies and Integration
Depends on `timer_crash.skel.h` and the test harness. The actual crash-provoking timer/map behavior lives in the generated BPF program.

## Risks and Test Signals
The main signal is absence of kernel crash plus successful load/attach; skip happens when timers are unsupported. Risks are that a one-microsecond sleep may not always trigger the intended path, and failures may manifest as kernel diagnostics rather than user-space assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_lockup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_lockup.c

## Purpose
Stresses a BPF timer locking race intended to detect lockups or bad deadlock error propagation when two timer programs run on separate CPUs.

## APIs, Types, and Functions
Exports `test_timer_lockup()`. `timer_lockup_thread()` pins a pthread to a distinct CPU and repeatedly runs one BPF program with an IPv4 packet test context.

## Control Flow, State, and Persistence
The test requires at least two CPUs. It opens the skeleton, records BSS error pointers for timer1 and timer2, then starts two affinity-pinned threads running `timer1_prog` and `timer2_prog`. Threads stop when either error value is set or after enough attempts to declare the race unreproduced and skip. Final assertions allow `0` or `-EDEADLK` for both timer errors.

## Dependencies and Integration
Depends on pthread CPU affinity, `get_nprocs()`, `network_helpers` packet data, `timer_lockup.skel.h`, and `bpf_prog_test_run_opts`.

## Risks and Test Signals
Risks include race non-reproducibility, CPU affinity failure in constrained environments, and static globals retaining skip/error state across reruns in one process. Signals are no process lockup, no unexpected error values, and skip when the race cannot be reproduced in bounded attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_lockup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_mim.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_mim.c

## Purpose
Tests BPF timers stored inside maps that are themselves stored in an outer map, and verifies rejection of invalid map-in-map timer patterns.

## APIs, Types, and Functions
Entry point is `serial_test_timer_mim()`. Helper `timer_mim()` attaches the accepted skeleton, runs the trigger program, checks callback progress, deletes the inner map from the outer array, and verifies callbacks stop.

## Control Flow, State, and Persistence
The test first suppresses libbpf output and confirms `timer_mim_reject` fails to load. It then loads `timer_mim`, attaches, runs `test1`, detaches, polls BSS `cnt` until it changes, checks `err == 0` and expected `ok` bits, closes the inner map fd, deletes the outer map element, and polls until `cnt` stops changing. State is transient in BPF maps/BSS.

## Dependencies and Integration
Uses `timer_mim.skel.h`, `timer_mim_reject.skel.h`, BPF map deletion APIs, skeleton attach/detach, and serial test harness sequencing.

## Risks and Test Signals
Risks are timing-dependent polling and cleanup ordering around closing the inner map fd. Signals are reject skeleton load failure, increasing callback count before deletion, stable count after map removal, zero error flag, and expected code-path bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_mim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_deadlock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_deadlock.c

## Purpose
Regression test ensuring `bpf_timer_start()` from a syscall-triggered BPF path does not deadlock when combined with the tracepoint path used by the BPF program.

## APIs, Types, and Functions
Defines `test_timer_start_deadlock()`, using the `timer_start_deadlock` skeleton and the `start_timer` BPF program.

## Control Flow, State, and Persistence
The skeleton opens/loads, attaches, retrieves the `start_timer` program fd, and runs it through `bpf_prog_test_run_opts()`. If the kernel deadlocks, the call never returns. On success it checks retval zero and BSS `tp_called == 1`.

## Dependencies and Integration
Depends on `timer_start_deadlock.skel.h`, syscall-program test-run support, and the test harness.

## Risks and Test Signals
The failure mode is a hang rather than a normal assertion. Passing signals are successful load/attach, returning test-run, retval zero, and tracepoint callback observed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_deadlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_delete_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_delete_race.c

## Purpose
Stresses a race between `bpf_timer_start()` and map element deletion that could otherwise produce a use-after-free when a timer becomes scheduled after async cancellation/free starts.

## APIs, Types, and Functions
Defines `struct ctx`, `start_timer_thread()`, `delete_elem_thread()`, and public `test_timer_start_delete_race()`. Each worker repeatedly runs a BPF program from `timer_start_delete_race.skel.h`.

## Control Flow, State, and Persistence
The test opens/loads the skeleton, starts two pthreads pinned to CPUs 0 and 1, flips a volatile start flag, and runs 1000 iterations of timer start and map delete test-runs. Any syscall or BPF retval error increments `ctx.errors`. The final assertion requires zero thread errors; deeper UAF detection is expected from KASAN or kernel crash diagnostics if the bug exists.

## Dependencies and Integration
Uses pthreads, CPU affinity, `bpf_prog_test_run_opts`, and the generated skeleton. It integrates with kernel map deletion, timer scheduling, async refcounting, and RCU tasks trace behavior.

## Risks and Test Signals
Risks include systems with fewer CPUs, affinity failures not asserted, race non-determinism, and memory-safety failures being external to user-space assertions. Signals are zero worker errors and no KASAN/kernel crash during the stress window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_delete_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/token.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/token.c

## Purpose
Comprehensive BPF token selftest. It validates delegated bpffs mount options, token creation in a user namespace, token-gated map/BTF/program/object loading, libbpf explicit and implicit token discovery, LSM veto hooks, freplace behavior, struct_ops BTF delegation, token info reporting, and kallsyms exposure.

## APIs, Types, and Functions
Key helpers wrap mount API syscalls (`fsopen`, `fsconfig`, `fsmount`, `fspick`, `move_mount`), capability drop/restore, delegation mask formatting, Unix fd passing (`sendfd`, `recvfd`), user namespace setup, and parent/child orchestration. `struct bpffs_opts` describes delegated command/map/program/attach masks. Callback tests include `userns_map_create()`, `userns_btf_load()`, `userns_prog_load()`, object privileged map/prog/freplace tests, BTF success/failure checks, implicit token tests, `userns_obj_priv_prog_kallsyms()`, and `userns_bpf_token_info()`.

## Control Flow, State, and Persistence
`serial_test_token()` runs subtests by constructing `bpffs_opts` and calling `subtest_userns()`. The child loads an LSM skeleton, enters a new user and mount namespace, creates a bpffs fs context, proves unprivileged delegation reconfiguration is rejected, sends the fs fd to the parent, receives completion notification, materializes a detached bpffs mount, creates a token fd, sends it back, and runs the callback. The parent receives the fs context, applies privileged delegation options, signals the child, receives the token fd, and waits for child exit. State is in transient fds, namespaces, bpffs mounts, environment variable `LIBBPF_BPF_TOKEN_PATH`, BSS flags in `token_lsm`, and temporary custom mount directory.

## Dependencies and Integration
Depends on Linux new mount API, user namespaces, capability helpers, sysctl helpers, libbpf token APIs, BTF APIs, kallsyms helpers, and skeletons for private map/prog, struct_ops, kallsyms, LSM, and freplace programs. It integrates with bpffs delegation options such as `delegate_cmds`, `delegate_maps`, `delegate_progs`, and `delegate_attachs`.

## Risks and Test Signals
Risks include kernel/config support for user namespaces, bpffs token delegation, LSM hooks, struct_ops, kallsyms visibility, mount namespace permissions, and cleanup of custom directories or env vars. Signals include expected `-EPERM` without both token and namespaced caps, success with correct token delegation, LSM-induced failures, implicit token success from `/sys/fs/bpf` or env path, expected freplace success/failure split, token info masks, and kallsyms containing loaded token BPF functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_attach_query.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_attach_query.c

## Purpose
Tests tracepoint attachment querying through `PERF_EVENT_IOC_QUERY_BPF` after attaching multiple BPF tracepoint programs through perf events.

## APIs, Types, and Functions
Entry point is `serial_test_tp_attach_query()`. It uses `bpf_prog_test_load()`, `bpf_prog_get_info_by_fd()`, `perf_event_open`, `PERF_EVENT_IOC_SET_BPF`, `PERF_EVENT_IOC_QUERY_BPF`, and perf enable/disable ioctls.

## Control Flow, State, and Persistence
The test reads the sched_switch tracepoint id from tracingfs/debugfs, configures a perf tracepoint attr, allocates a query buffer, and loops three times loading the same tracepoint BPF object, recording each program id, opening/enabling a perf event, attaching the program, and querying attached ids. It also checks null-id-array query, count-only query, bad pointer `EFAULT`, and undersized buffer `ENOSPC`. Cleanup unwinds perf fds and BPF objects.

## Dependencies and Integration
Depends on tracingfs/debugfs availability, perf event tracepoint support, `test_tracepoint.bpf.o`, BPF prog info APIs, and the legacy test harness `CHECK` macros.

## Risks and Test Signals
Risks include tracing filesystem path differences, perf permissions, CPU 0 availability, and cleanup labels using loop index state. Signals are queried program counts matching attachment order, returned ids matching saved prog ids, and expected negative ioctl errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_attach_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_btf_nullable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_btf_nullable.c

## Purpose
Runs BTF tracepoint nullable argument tests supplied by the `test_tp_btf_nullable` skeleton.

## APIs, Types, and Functions
Only public entry point is `test_tp_btf_nullable()`, which calls `RUN_TESTS(test_tp_btf_nullable)` when the BPF test module is available.

## Control Flow, State, and Persistence
The test checks `env.has_testmod`, skips if missing, and delegates all subtest execution to the skeleton test runner. There is no user-space state beyond the environment flag.

## Dependencies and Integration
Depends on `test_progs.h`, `test_tp_btf_nullable.skel.h`, and the kernel BPF test module that exposes the required tracepoints and BTF signatures.

## Risks and Test Signals
Main risk is missing or incompatible test module. Signals are skip without testmod and skeleton subtest success when nullable BTF tracepoint handling works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_btf_nullable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_ext.c

## Purpose
Validates tracing a freplace extension program: a classifier program is replaced by an extension and fentry/fexit tracing programs attach to the extension.

## APIs, Types, and Functions
Entry point `test_trace_ext()` uses skeletons `test_pkt_md_access`, `test_trace_ext`, and `test_trace_ext_tracing`. It calls `bpf_program__set_attach_target()` twice: first to attach an extension to the base program, then to attach tracing programs to the extension fd.

## Control Flow, State, and Persistence
The base packet metadata program is open/load/attached. The extension skeleton is opened, its replacement program target is set to the base program fd and function name, then it loads and attaches. The tracing skeleton is opened, fentry and fexit target the extension fd/function, then it loads and attaches. A test packet run triggers the base program; BSS counters verify the extension ran and fentry/fexit counts equal extension invocations.

## Dependencies and Integration
Depends on packet data from `network_helpers`, libbpf attach-target APIs, freplace, fentry/fexit support, and the three generated skeletons.

## Risks and Test Signals
Risks include attach target name/fd mismatch, verifier changes around tracing extension programs, and BTF availability. Signals are nonzero extension call count, fentry/fexit counters equal to extension count, and successful program test run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_printk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_printk.c

## Purpose
Tests `bpf_trace_printk()` output, including mutable rodata format text, UTF-8 format content, return values, and invalid format specifier failure.

## APIs, Types, and Functions
Entry point is `serial_test_trace_printk()`. Callback `trace_pipe_cb()` scans trace pipe lines for two expected messages. Uses lightweight skeleton `trace_printk.lskel.h`.

## Control Flow, State, and Persistence
The test opens the skeleton, checks and modifies the first byte of a rodata format string before load, loads and attaches, sleeps briefly for tracepoint execution, detaches, asserts BSS run counts and positive return values, asserts invalid specifier return is negative, and reads trace pipe to match printed message counts. State is transient in BSS counters and the kernel trace buffer.

## Dependencies and Integration
Depends on trace pipe helper `read_trace_pipe_iter`, tracepoint attachment in the lskel, and kernel trace buffer access.

## Risks and Test Signals
Risks include stale trace buffer data, tracefs access restrictions, timing around tracepoint trigger, and UTF-8 handling in terminals/logs. Signals are BSS counters, positive printk returns, negative invalid-spec return, and trace pipe matches equal to run counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_vprintk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_vprintk.c

## Purpose
Tests `bpf_trace_vprintk()` behavior for multi-argument formatting and error handling for null data.

## APIs, Types, and Functions
Entry point is `serial_test_trace_vprintk()`. `trace_pipe_cb()` counts trace pipe lines containing the expected comma-separated message. It uses `trace_vprintk.lskel.h`.

## Control Flow, State, and Persistence
The lightweight skeleton opens/loads, attaches, waits briefly, detaches, and checks that the BPF program ran and returned a positive vprintk length. It reads the trace pipe and requires found messages to equal the BSS run count, then verifies `null_data_vprintk_ret` is negative.

## Dependencies and Integration
Depends on trace pipe iteration helpers, tracefs access, the generated lskel, and kernel support for `bpf_trace_vprintk`.

## Risks and Test Signals
Risks are trace buffer contamination or permissions, short sleep timing, and helper behavior changes. Signals are matching trace pipe count, positive return for valid vprintk, and negative return for null data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trace_vprintk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_failure.c

## Purpose
Negative tests for tracing program load/attach restrictions, including spin lock helpers, denied tracing targets, and fexit on noreturn functions.

## APIs, Types, and Functions
Entry point is `test_tracing_failure()`. Helpers are `test_bpf_spin_lock()`, `test_tracing_fail_prog()`, `test_tracing_deny()`, and `test_fexit_noreturns()`.

## Control Flow, State, and Persistence
Spin-lock subtests open the skeleton, enable one autoloaded program, load successfully, and assert attach fails. Verifier/log-message subtests find a program by name, enable autoload, install a log buffer, expect skeleton load to fail, and assert the log contains the expected rejection text. `tracing_deny` first verifies the target BTF id exists and skips otherwise.

## Dependencies and Integration
Depends on `tracing_failure.skel.h`, libbpf program autoload/log APIs, vmlinux BTF lookup, and tracing attach policy in the kernel.

## Risks and Test Signals
Risks include exact verifier message drift, kernel config dependency for `__rcu_read_lock`, and changed allowed/denied target policy. Signals are attach failure for spin lock/unlock programs and load failure logs containing the expected policy messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_struct.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_struct.c

## Purpose
Validates BPF tracing argument decoding for structs, many arguments, unions, return values, and register extraction from test-module functions.

## APIs, Types, and Functions
Public entry point `test_tracing_struct()` runs subtests `test_struct_args()`, `test_struct_many_args()`, and `test_union_args()`. It uses `tracing_struct` and `tracing_struct_many_args` skeletons plus `trigger_module_test_read()`.

## Control Flow, State, and Persistence
Each subtest opens/loads/attaches a skeleton, triggers the BPF test module read path, and validates BSS fields populated by BPF programs. The assertions cover nested struct fields, register-slot values, return values, wide argument lists, and union member interpretation. State is transient in BSS counters/fields.

## Dependencies and Integration
Depends on the BPF test module, fentry/fexit or tracing BTF support, generated skeletons, and `test_progs` module trigger helper.

## Risks and Test Signals
Risks include ABI-specific argument passing, compiler/kernel BTF layout changes, and missing test module. Signals are exact BSS field equality for all struct/union arguments and return values after `trigger_module_test_read()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tracing_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trampoline_count.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trampoline_count.c

## Purpose
Tests enforcement of the kernel maximum number of BPF trampoline links for fentry/fmod_ret/fexit programs.

## APIs, Types, and Functions
Defines `struct inst`, `load_prog()`, and `test_trampoline_count()`. Uses `get_bpf_max_tramp_links()` and `trigger_module_test_read()`.

## Control Flow, State, and Persistence
The test allocates one more instance slot than the kernel limit. It repeatedly opens, loads, finds, and attaches programs from `test_trampoline_count.bpf.o` up to the limit. It then loads one extra fmod_ret program and asserts attach fails with `-E2BIG` and a null link pointer. Finally it triggers the probed module function and destroys all links/objects.

## Dependencies and Integration
Depends on libbpf object APIs, BPF test module trigger, and kernel trampoline accounting.

## Risks and Test Signals
Risks include leaks on partial load failure, module trigger availability, and limit semantics changing. Signals are successful attaches up to the reported limit, `-E2BIG` for the extra attach, and successful module trigger after attachments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/trampoline_count.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/type_cast.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/type_cast.c

## Purpose
Tests BPF type casting helpers/kfuncs against XDP metadata and skb contexts, plus negative verifier cases for invalid casts.

## APIs, Types, and Functions
Entry point `test_type_cast()` runs `test_xdp()`, `test_tc()`, and `test_negative()`. It uses `type_cast.skel.h`, `bpf_prog_test_run_opts`, and packet data from `network_helpers`.

## Control Flow, State, and Persistence
Each positive subtest opens the skeleton with only the relevant program autoloaded, loads it, runs with `pkt_v4`, checks retval, and validates BSS fields such as ifindex, ingress ifindex, netdev name, inode, skb lengths, metadata length, and fragment length. Negative tests open the skeleton, autoload one named invalid program, and require load failure.

## Dependencies and Integration
Depends on XDP and TC program test-run support, BTF-aware type casts in BPF code, loopback interface assumptions, and the generated skeleton.

## Risks and Test Signals
Risks include interface index/name assumptions, verifier diagnostic changes hidden by generic failure assertions, and packet context differences. Signals are exact BSS values for positive casts and load failure for `untrusted_ptr` and `kctx_u64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/type_cast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/udp_limit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/udp_limit.c

## Purpose
Tests cgroup socket create/release BPF programs that enforce a single UDP socket per cgroup.

## APIs, Types, and Functions
Entry point is `test_udp_limit()`. It uses `test__join_cgroup()`, `bpf_program__attach_cgroup()`, and normal `socket()`/`close()`.

## Control Flow, State, and Persistence
The test joins/creates `/udp_limit`, loads the skeleton, attaches socket-create and socket-release programs to the cgroup, opens one UDP socket successfully, asserts the second UDP socket fails, closes the first, opens another successfully, and checks BSS `invocations == 4` and `in_use == 1`. Fds and skeleton are cleaned up on exit.

## Dependencies and Integration
Depends on cgroup BPF support, cgroup test helpers, `udp_limit.skel.h`, and UDP socket creation.

## Risks and Test Signals
Risks include cgroup setup permission issues and unexpected socket-create side effects from the test environment. Signals are first socket success, second socket failure, reopen success after release, and exact BSS counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/udp_limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uninit_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uninit_stack.c

## Purpose
Delegates uninitialized stack verifier/runtime tests to the generated `uninit_stack` skeleton.

## APIs, Types, and Functions
Only entry point is `test_uninit_stack()`, which invokes `RUN_TESTS(uninit_stack)`.

## Control Flow, State, and Persistence
All subtest selection and assertions live in generated skeleton test metadata. The C wrapper has no persistent state.

## Dependencies and Integration
Depends on `uninit_stack.skel.h` and the `test_progs` `RUN_TESTS` framework.

## Risks and Test Signals
Risks are limited to skeleton generation and test harness integration. Signals are individual skeleton subtests passing or failing under `RUN_TESTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uninit_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/unpriv_bpf_disabled.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/unpriv_bpf_disabled.c

## Purpose
Tests behavior when unprivileged BPF is disabled: already accessible pinned maps, perf/ring buffers, and links remain usable without capabilities, while privileged creation, lookup-by-id, enumeration, query, and BTF loading fail with `-EPERM`.

## APIs, Types, and Functions
Important helpers are `process_ringbuf()`, `process_perfbuf()`, `test_unpriv_bpf_disabled_positive()`, `test_unpriv_bpf_disabled_negative()`, and public `test_unpriv_bpf_disabled()`. Uses capability helpers, sysctl helpers, map pinning, perf/ring buffer APIs, BPF program/map/link id APIs, and BTF APIs.

## Control Flow, State, and Persistence
The test opens/loads the skeleton, records the current pid in BSS, pins seven maps under `/sys/fs/bpf/unpriv_bpf_disabled_*`, lowers perf restrictions, sets `unprivileged_bpf_disabled` to disabled-for-unprivileged mode when possible, opens a software perf event, attaches the skeleton, drops effective capabilities, and runs positive and negative subtests. Cleanup restores capabilities and sysctls, closes perf fd, unlinks pins, and destroys the skeleton.

## Dependencies and Integration
Depends on sysctl write permissions, CAP management, bpffs pinning, perf events, libbpf buffer APIs, and `test_unpriv_bpf_disabled.skel.h`.

## Risks and Test Signals
Risks include global sysctl mutation, failure to restore capabilities/sysctls on early errors, map pin path collisions, and distro policy where `unprivileged_bpf_disabled=1` is immutable. Signals include successful use of pinned maps and buffers after cap drop, successful link creation to an existing perf event, and `-EPERM` for all privileged negative operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/unpriv_bpf_disabled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe.c

## Purpose
Tests basic uprobe and uretprobe attachment to selftest binaries/libraries, symbol-version resolution, same-offset autoattach, and x86 register/IP modification by uprobe BPF programs.

## APIs, Types, and Functions
Entry point `test_uprobe()` runs `test_uprobe_attach()` and x86-only `test_uprobe_regs_change()`. Helpers spawn `./urandom_read`, attach to symbols in `liburandom_read.so`, and define naked assembly triggers for register snapshots and IP redirection.

## Control Flow, State, and Persistence
`test_uprobe_attach()` loads `test_uprobe`, starts `urandom_read`, sets target pid, confirms unversioned ambiguous `urandlib_api` attach fails, attaches a versioned symbol manually, autoattaches the remaining probes, triggers the child by closing the pipe, and checks BSS results. x86 register tests attach to `/proc/self/exe`, run assembly that captures registers before and after probe execution, and assert either register replacement or redirected return target.

## Dependencies and Integration
Depends on `test_uprobe.skel.h`, selftest helper binaries `urandom_read` and `liburandom_read.so`, libbpf uprobe attach APIs, `/proc/self/exe`, and x86 register layout for the assembly subtests.

## Risks and Test Signals
Risks include symbol versioning differences, helper binary availability, architecture-specific assembly, and compiler instrumentation affecting naked functions. Signals are expected attach conflict for ambiguous symbol, correct result counters for versioned/same-offset probes, and expected register/IP changes on x86.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_autoattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_autoattach.c

## Purpose
Validates skeleton autoattach for uprobes and uretprobes against both local functions and shared-library functions resolved by name.

## APIs, Types, and Functions
Defines local noinline `autoattach_trigger_func()` and public `test_uprobe_autoattach()`. Uses `test_uprobe_autoattach.skel.h`.

## Control Flow, State, and Persistence
The skeleton opens/loads and autoattaches. The test sets its pid, calls the local trigger function with eight arguments, then opens `/dev/null` to trigger libc/shared-library probes. It validates BSS counters, captured parameters, return codes, and architecture-dependent register argument slots. State is transient in BSS and the temporary `FILE *`.

## Dependencies and Integration
Depends on libbpf skeleton autoattach metadata, uprobe/uretprobe support, shared-library symbol resolution, and `FUNC_REG_ARG_CNT` architecture limits.

## Risks and Test Signals
Risks include compiler inlining despite `noinline`, libc symbol differences, and missing register arguments on some architectures. Signals are exact BSS counters, argument values, and return values after local and shared-library triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_autoattach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_multi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_multi_test.c

## Purpose
Large coverage test for uprobe multi attach APIs, link-create APIs, USDT attach through uprobes, pid filtering, consumer combinations, session uprobes, cookies, recursion, verifier cases, and attach/detach benchmark behavior.

## APIs, Types, and Functions
Entry point `test_uprobe_multi_test()` dispatches many subtests. It defines target functions `uprobe_multi_func_[123]`, `usdt_trigger()`, `uprobe_session_recursive()`, child process/thread orchestration helpers, `test_skel_api()`, attach API helpers, negative attach tests, raw `bpf_link_create()` tests, consumer-combination generators, pid-filter tests, session tests, and benchmark tests.

## Control Flow, State, and Persistence
Basic tests attach skeleton-generated or manual uprobe/uretprobe/sleepable links to three functions and optionally a child pid or thread, trigger functions, and assert BSS hit counts and pid/tid filtering. Attach API tests cover pattern matching and explicit symbol lists; link API tests resolve ELF offsets manually. Negative tests exercise invalid counts, pointers, paths, flags, pids, trap instruction attach failure, and refcount offset conflicts. Consumer tests run all 16 before/after combinations of entry, return, and session consumers across threads. Session tests validate entry/return counts, cookies, and recursive cookie lifetimes. Benchmarks attach to many probes in `./uprobe_multi` and count 50000 hits.

## Dependencies and Integration
Depends on many generated skeletons, libbpf internal ELF symbol resolution, `clone`, `fork`, pthreads, `/proc/self/exe`, selftest binary `./uprobe_multi`, USDT macros, and raw `BPF_TRACE_UPROBE_MULTI` link creation.

## Risks and Test Signals
Risks include architecture-specific trap behavior, symbol resolution fragility, child cleanup complexity, high concurrency in consumer tests, and benchmark runtime. Signals are exact BSS hit counters, no bad pid flags, expected kernel errors for invalid link options, `-E2BIG` where limits are exceeded, correct session cookie results, verifier subtests passing, and benchmark counts of 50000.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_multi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_syscall.c

## Purpose
x86_64-focused tests for syscall-backed optimized uprobes/uretprobes, register preservation, kernel test-module register modification, uretprobe syscall misuse handling, trampoline mapping, shadow stack compatibility, attach/detach races, and direct `uprobe` syscall error behavior.

## APIs, Types, and Functions
Public entry point `test_uprobe_syscall()` calls `__test_uprobe_syscall()` on x86_64 and skips elsewhere. Helpers include naked trigger functions, `test_uprobe_regs_equal()`, `write_bpf_testmod_uprobe()`, `test_regs_change()`, `test_uretprobe_syscall_call()`, trampoline discovery helpers, `test_uprobe_legacy()`, `test_uprobe_multi()`, `test_uprobe_session()`, `test_uprobe_usdt()`, `test_uretprobe_shadow_stack()`, race workers, and `test_uprobe_error()`.

## Control Flow, State, and Persistence
Register tests attach uprobes/uretprobes to a self function, trigger optimization, run assembly that snapshots registers, and compare BPF-observed registers with before/after snapshots. The test-module path writes an offset to `/sys/kernel/bpf_testmod_uprobe`, triggers a probe that modifies registers, then unregisters. Uretprobe syscall misuse forks a child that invokes the uretprobe syscall directly and expects SIGILL without executing BPF. Optimized attach tests inspect patched NOP sites for call instructions into `[uprobes-trampoline]`, destroy links, and verify trampoline mapping persists. Shadow stack mode reruns the main cases with CET shadow stack enabled when available. Race test alternates attach/detach with trigger threads for a configurable duration and validates the USDT semaphore is inactive at the end.

## Dependencies and Integration
Depends on x86_64 assembly, arch prctl shadow-stack constants, raw syscall numbers, `/proc/self/maps`, BPF test module sysfs file, libbpf uprobe and uprobe_multi APIs, USDT macros, and generated skeletons.

## Risks and Test Signals
Risks include x86-only assumptions, compiler control-flow protection altering instruction layout, shadow stack availability, test module availability, race nondeterminism, and raw syscall number drift. Signals are register equality/modification assertions, child SIGILL, expected trampoline mapping and patched instruction bytes, no active race semaphore after attach/detach stress, and direct `uprobe` syscall returning `ENXIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uretprobe_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uretprobe_stack.c

## Purpose
Validates user stack traces captured from entry uprobes, return uprobes, and USDT probes across a controlled nested call chain.

## APIs, Types, and Functions
Defines weak section-placed `target_1()` through `target_4()`, a USDT probe in `target_4()`, linker-provided section boundary symbols, `struct range`, `validate_stack()`, and weak test entry `test_uretprobe_stack()`.

## Control Flow, State, and Persistence
The target functions are placed in custom sections so their address ranges are available. The test loads/attaches `uretprobe_stack`, calls recursive `target_1(0)` which flows through `target_2`, `target_3`, `target_4`, and a USDT, then validates BSS stack arrays. `validate_stack()` checks stack length and confirms expected frames fall inside caller and target section ranges, with optional verbose printing. It checks entry stacks for progressively deeper calls, a USDT stack including the full chain, and exit stacks where returned functions are absent as expected.

## Dependencies and Integration
Depends on linker section start/stop symbols, USDT macros, `uretprobe_stack.skel.h`, user stack collection support, and libbpf skeleton autoattach.

## Risks and Test Signals
Risks include compiler inlining despite weak attributes, frame-pointer/unwind behavior differences, stack truncation, and linker section layout changes. Signals are the trigger returning `43`, positive stack lengths, and all expected instruction pointers falling within the declared function ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uretprobe_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/usdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/usdt.c

## Purpose
Tests libbpf USDT attach and argument decoding, including semaphores, cookies, zero/three/twelve argument probes, SIB addressing specs, optimized USDT patching, many inlined call sites, spec-id reuse, excessive distinct specs, deduplicated specs, and USDTs in helper binaries/shared libraries.

## APIs, Types, and Functions
Entry point `test_usdt()` runs `subtest_basic_usdt()`, x86 optimized variants, `subtest_multispec_usdt()`, and `subtest_urandom_usdt()`. It defines semaphore variables in `.probes`, trigger functions using `STAP_PROBE*`, x86 SIB inline assembly, optimized attach instruction scanners, many-call-site generators, and `urand_spawn()`/`urand_trigger()` helpers.

## Control Flow, State, and Persistence
Basic tests load `test_usdt`, attach skeleton and manual USDT links, trigger probes once or twice depending on optimized mode, and validate BSS call counts, cookies, argument counts, return codes, values, and byte sizes. Reattach tests destroy and recreate USDT links with a different cookie. x86 optimized attach verifies single-NOP probes use int3 while NOP+NOP5 probes use optimized call patching. Multispec tests trigger 100 sites, repeatedly detach/reattach to prove spec ids are freed, expect failure for too many distinct specs on supported builds, and expect success for 400 call sites sharing a deduplicated spec. Urandom tests attach automatically or manually to executable and shared-library USDTs and validate counts/sums.

## Dependencies and Integration
Depends on `../sdt.h`, generated `test_usdt` and `test_urandom_usdt` skeletons, selftest `urandom_read` and `liburandom_read.so`, libbpf USDT attach APIs, architecture-specific instruction patching on x86, and generated assembly symbols for optimized probes.

## Risks and Test Signals
Risks include compiler inlining/codegen changing USDT sites, architecture differences in argument specs, optimized patch instruction layout, semaphore cleanup, helper binary availability, and spec limit behavior differences. Signals are exact call counts, cookies, argument values/sizes, expected `-E2BIG` for excessive distinct specs, no dangling attachments after partial failure, optimized instruction bytes, and urandom call counts/sums of 256.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/usdt.c -->

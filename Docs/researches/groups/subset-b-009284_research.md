# subset-b-009284 research

Grouped research report for liburing test files under `sources/test-tools/liburing/test`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/bind-listen.c -->
# sources/test-tools/liburing/test/bind-listen.c

Purpose: integration test for creating and operating TCP sockets through io_uring socket, bind, listen, accept, connect, send, recv, and socket-name commands, including direct/fixed-file sockets.

Important APIs/types/functions: `io_uring_prep_socket_direct`, `io_uring_prep_cmd_sock`, `io_uring_prep_bind`, `io_uring_prep_listen`, `io_uring_prep_accept_direct`, `io_uring_prep_cmd_getsockname`, `io_uring_prep_fixed_fd_install`, `io_uring_prep_connect`, `io_uring_prep_send`, `io_uring_prep_recv`, `t_create_ring`, and `io_uring_get_probe`. Local helpers are `msec_to_ts`, `setup_srv`, `connect_client`, `do_getsockname`, and negative test functions for bind/listen/sockname.

Control flow: `main` skips when `IORING_OP_LISTEN` is unsupported, then runs a good-server path under normal, defer-taskrun, and SQPOLL rings. The good path registers three fixed files, builds a linked server setup chain, discovers the ephemeral port, creates a direct client, accepts into a fixed slot, validates peer address, and receives the magic string. It then runs malformed bind/listen/sockname operations and checks kernel error codes.

State/persistence behavior: all state is transient socket and fixed-file table state inside one ring. The `no_getsockname` flag persists a detected missing getsockname command and switches later checks to a fixed-fd-install syscall fallback.

Dependencies/integration: requires kernel io_uring socket op support, loopback TCP, fixed files, and helper wrappers. It integrates newer socket commands with older syscall fallbacks.

Risks/test signals: failures are wrong CQE results, incorrect peer address, missing data, or unexpected success for invalid arguments. It is sensitive to kernel feature level and SQPOLL permission/support.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/bind-listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/bpf-progs/cp.bpf.c -->
# sources/test-tools/liburing/test/bpf-progs/cp.bpf.c

Purpose: eBPF struct_ops program that drives an io_uring copy loop from inside the kernel-side io_uring BPF hook.

Important APIs/types/functions: `BPF_PROG(cp_loop_step)`, `bpf_io_uring_get_region`, `bpf_io_uring_submit_sqes`, `struct io_uring_sqe`, `struct io_uring_cqe`, `struct iou_loop_params`, and the exported `io_uring_bpf_ops cp_ops`. Global BSS/rodata fields carry ring offsets, file descriptors, buffer pointer/size, current offset, in-flight count, and `cp_result`.

Control flow: on the first loop step it submits a read from `input_fd` into `buffer_uptr`. Each CQE is consumed from the mapped CQ ring: read completion of zero marks EOF/success, read completion with bytes submits a write to `output_fd`, and write completion advances `cur_offset` before issuing the next read. It stops on errors, malformed multiple CQEs, or unknown `user_data`.

State/persistence behavior: persistent program state is in BPF globals: `nr_infligt`, `cur_offset`, and `cp_result`. The file data is copied through a single userspace buffer; the BPF program manually advances CQ head and sets `cq_wait_idx`.

Dependencies/integration: compiled into a libbpf skeleton used by `bpf_cp.c`. It depends on io_uring BPF ksyms and the layout contract in `bpf_defs.h`.

Risks/test signals: risks include typo-prone shared state (`nr_infligt`), CQ wrap math, partial writes treated as full forward progress, and bad offset setup. Success is `cp_result == 0` after the userspace harness enters the ring.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/bpf-progs/cp.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/bpf-progs/nops.bpf.c -->
# sources/test-tools/liburing/test/bpf-progs/nops.bpf.c

Purpose: eBPF struct_ops program that stress-submits a bounded stream of io_uring NOP SQEs from the BPF loop hook.

Important APIs/types/functions: `BPF_PROG(nops_loop_step)`, `nr_to_submit`, `bpf_io_uring_get_region`, `bpf_io_uring_submit_sqes`, `REQ_TOKEN`, `max_inflight`, and `nops_ops`. Ro-data supplies SQ/CQ offsets and ring sizes; BSS tracks `reqs_inflight` and `reqs_to_run`.

Control flow: every loop step maps SQ and CQ regions, submits enough NOPs to keep up to eight requests in flight, scans CQEs with the expected token, advances CQ head, decrements in-flight and remaining counts, and stops when no work remains. It sets `cq_wait_idx` to sleep until enough completions arrive unless CQEs remain immediately available.

State/persistence behavior: state lives in BPF globals only. No filesystem data is touched; the ring itself is the durable integration object for the duration of the test.

Dependencies/integration: loaded and attached by `bpf_nops.c` through a generated libbpf skeleton and `bpf_defs.h` io_uring struct_ops definitions.

Risks/test signals: bad region offsets, token mismatch, short BPF submit, or underflow in `reqs_to_run - inflight` would stop prematurely. The userspace harness verifies that all requested NOPs were consumed.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/bpf-progs/nops.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/bpf_cp.c -->
# sources/test-tools/liburing/test/bpf_cp.c

Purpose: userspace harness for the `cp.bpf.c` io_uring BPF struct_ops copy program.

Important APIs/types/functions: generated `cp_bpf` skeleton APIs, `bpf_map__attach_struct_ops`, `io_uring_enter`, `t_create_ring_params`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_NO_SQARRAY`, `IORING_SETUP_CQSIZE`, and `IORING_SETUP_SQ_REWIND`.

Control flow: `main` requires input and output filenames, opens them with `O_DIRECT`, stats input size, allocates an aligned buffer, creates a specialized ring, fills skeleton rodata/BSS with ring offsets and file state, loads and attaches struct_ops, truncates output to input size, then calls `io_uring_enter(...GETEVENTS...)` to let BPF drive the loop. It checks `skel->bss->cp_result`.

State/persistence behavior: input/output file descriptors and copy buffer are shared with the BPF program through skeleton BSS. The output file is created/truncated and mutated by BPF-issued reads/writes; BPF link and skeleton are destroyed on success.

Dependencies/integration: requires libbpf, generated `cp.skel.h`, io_uring BPF ops support, direct-I/O-capable files, and the BPF program layout.

Risks/test signals: skips on missing io_uring BPF ops (`-ESRCH`), fails on skeleton load/attach, direct I/O setup, copy errors, or nonzero `cp_result`. It does not compare output bytes itself.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/bpf_cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/bpf_defs.h -->
# sources/test-tools/liburing/test/bpf_defs.h

Purpose: shared BPF-side ABI shim for io_uring struct_ops tests.

Important APIs/types/functions: placeholder `struct io_ring_ctx`, `struct iou_loop_params`, region constants `IOU_REGION_MEM`, `IOU_REGION_CQ`, `IOU_REGION_SQ`, loop return constants `IOU_LOOP_CONTINUE`/`IOU_LOOP_STOP`, `struct io_uring_bpf_ops`, and weak ksym declarations for `bpf_io_uring_get_region` and `bpf_io_uring_submit_sqes`.

Control flow: header-only; it declares the types and symbols consumed by BPF programs and includes `liburing/io_uring.h` for SQE/CQE layouts.

State/persistence behavior: no runtime state. Its definitions define the persistent contract between generated BPF objects and the userspace skeletons that fill rodata/BSS.

Dependencies/integration: depends on kernel BPF helper/tracing headers and liburing io_uring layout headers. Used by both `cp.bpf.c` and `nops.bpf.c`.

Risks/test signals: any drift between these local definitions and kernel struct_ops expectations breaks BPF verifier/load or runtime ring-region interpretation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/bpf_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/bpf_nops.c -->
# sources/test-tools/liburing/test/bpf_nops.c

Purpose: userspace harness for the `nops.bpf.c` io_uring BPF struct_ops NOP-submission program.

Important APIs/types/functions: generated `nops_bpf` skeleton APIs, `bpf_map__attach_struct_ops`, `io_uring_enter`, `t_create_ring_params`, and the same specialized ring flags used by `bpf_cp.c`.

Control flow: `setup_ring_ops` creates a ring with eight SQ/CQ entries, opens the skeleton, writes ring fd and CQ offsets into struct_ops/rodata, sets `reqs_to_run` to 1000, loads the BPF object, and attaches struct_ops. `main` enters the ring and verifies `reqs_to_run` reached zero.

State/persistence behavior: state is confined to ring kernel state and skeleton BSS. No files are modified.

Dependencies/integration: requires libbpf, generated `nops.skel.h`, io_uring BPF ops support, and ring setup features such as SQ rewind/no SQ array.

Risks/test signals: skip on unsupported BPF ops; fail on load/attach/run errors or leftover requests. It exercises completion processing and BPF SQE submission under bounded in-flight pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/bpf_nops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-mshot.c -->
# sources/test-tools/liburing/test/buf-ring-mshot.c

Purpose: verifies that one provided buffer ring can be shared safely by multiple concurrent multishot `recv` operations across four socket streams.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_free_buf_ring`, `io_uring_prep_recv_multishot`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, pthread barriers, and helper `t_create_socket_pair`.

Control flow: `run_shared_test` creates a ring, socket pairs, a buffer ring, sender threads, and one multishot recv per stream. It reaps CQEs until all streams hit EOF, validates stream ID from `user_data`, handles `-ENOBUFS` by rearming, checks buffer IDs and byte pattern integrity, recycles buffers, and compares sent/received byte totals. Three scenarios cover normal load, buffer exhaustion, and uneven stream pressure.

State/persistence behavior: per-stream byte counters and reusable buffer-ring entries form the main state. No persistent files exist; socket shutdown marks stream completion.

Dependencies/integration: depends on buffer ring and multishot recv kernel support plus pthread synchronization.

Risks/test signals: skips when buffer rings or multishot recv are unsupported. Failures signal cross-stream buffer corruption, bad CQE flags, lost EOF, unbalanced byte counts, or incorrect exhaustion behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-mshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-nommap.c -->
# sources/test-tools/liburing/test/buf-ring-nommap.c

Purpose: tests `IOU_PBUF_RING_MMAP` provided-buffer rings with a ring initialized using `IORING_SETUP_NO_MMAP` and caller-supplied ring memory.

Important APIs/types/functions: `io_uring_queue_init_mem`, `io_uring_register_buf_ring`, `mmap` of `IORING_OFF_PBUF_RING`, `io_uring_buf_ring_add`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, and pipe I/O.

Control flow: allocate aligned memory for the SQ/CQ ring, initialize an unmapped io_uring, register one mmap-backed provided-buffer ring group, mmap the pbuf ring from the ring fd, add one buffer with a fixed bid, submit a selected-buffer pipe read, write data to the pipe, and assert the CQE has a selected buffer with the expected bid.

State/persistence behavior: transient ring memory is explicitly owned by the process. The provided-buffer ring is kernel-registered but mmap-visible; no persistent files.

Dependencies/integration: requires `IORING_SETUP_NO_MMAP`, pbuf ring mmap support, and pipes. It skips on older kernels reporting `-EINVAL`, `-ENOMEM`, or mmap allocation limits.

Risks/test signals: wrong buffer ID, missing `IORING_CQE_F_BUFFER`, or registration/mmap failures show integration issues between no-mmap ring setup and mmap-provided buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-nommap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-put.c -->
# sources/test-tools/liburing/test/buf-ring-put.c

Purpose: verifies that mmap-backed provided buffer ring mappings remain safe to touch after their buffer groups are unregistered.

Important APIs/types/functions: `io_uring_register_buf_ring`, pbuf-ring `mmap`, `io_uring_unregister_buf_ring`, `IORING_OFF_PBUF_RING`, and `IOU_PBUF_RING_MMAP`.

Control flow: create one ring, register and mmap ten buffer groups starting at bgid 60 with 512 entries each, unregister all groups, then repeatedly memset every still-mapped ring for 1000 iterations before exiting.

State/persistence behavior: the test intentionally keeps user mappings after unregister to exercise lifetime/pinning behavior. No data persists beyond process memory.

Dependencies/integration: depends on pbuf ring mmap support and kernel cleanup/refcounting of registered provided-buffer rings, including low and higher bgid storage paths.

Risks/test signals: crashes or mmap/register/unregister errors are the main signal. It does not submit I/O; it targets mapping lifetime and use-after-free regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-put.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-stress.c -->
# sources/test-tools/liburing/test/buf-ring-stress.c

Purpose: stress tests provided-buffer ring drain/refill behavior under high-volume read workloads, overflow, and rapid single-buffer cycles.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `provide_buffers`, selected-buffer `io_uring_prep_read`, `IORING_CQE_F_BUFFER`, `io_uring_buf_ring_advance`, helper `t_create_file`, and temporary files.

Control flow: `test_read_drain_refill` creates a patterned file sized for 10,000 rounds, provides eight buffers per round, submits eight reads, validates returned buffer data, and repeats. `test_read_overflow_refill` submits twice as many reads as buffers and expects exactly eight successes and eight `-ENOBUFS`, then refills successfully. `test_rapid_drain_refill` provides one buffer and one read per iteration for 80,000 cycles.

State/persistence behavior: temporary files are created and unlinked; buffer ring state is repeatedly drained and replenished. Data integrity is checked against an in-memory pattern.

Dependencies/integration: requires provided-buffer ring support and ordinary file reads. It uses large loops, so it can be runtime-sensitive.

Risks/test signals: failures include missing buffer flags, bad bid, unexpected `-ENOBUFS`, data mismatch, short reads, or refill stalls.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-upgrade.c -->
# sources/test-tools/liburing/test/buf-ring-upgrade.c

Purpose: race/regression test for converting a legacy provided-buffer group into a ring-provided group after the legacy group is drained, while receives and registration race.

Important APIs/types/functions: `io_uring_prep_provide_buffers`, raw `io_uring_register(... IORING_REGISTER_PBUF_RING ...)`, selected-buffer `recv`, `socketpair`, `fork`, shared anonymous `mmap`, CPU affinity, and alarm timeout.

Control flow: `run_poc` provides one legacy buffer for bgid `0x444`, prepares a userspace buffer ring with 1024 entries, forks a sender spinning zero-length datagrams and a registrar repeatedly trying to register the ring. The parent repeatedly submits async selected-buffer receives until registration succeeds, no support is detected, timeout fires, or post-registration iterations elapse.

State/persistence behavior: shared memory reports stop and registration outcomes across processes. The ring transitions from legacy buffer storage to pbuf-ring registration. No files persist.

Dependencies/integration: depends on UNIX datagram socketpairs, process scheduling, pbuf ring registration, and race timing. CPU pinning is best-effort.

Risks/test signals: primarily detects crashes, hangs, and unexpected registration errors. It returns pass even if the race does not hit a strong assertion, relying on survival under pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring-upgrade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring.c -->
# sources/test-tools/liburing/test/buf-ring.c

Purpose: broad sanity test for shared provided-buffer rings, including registration lifecycle, invalid registration, classic-buffer conflicts, page-boundary safety, normal consumption, and mmap-backed pbuf rings.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `io_uring_register_buf_ring`, `io_uring_unregister_buf_ring`, `io_uring_free_buf_ring`, `io_uring_prep_provide_buffers`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, `IOU_PBUF_RING_MMAP`, `mmap`, and `mprotect`.

Control flow: main iterates bgids 1 and 127 through register/unregister, bad pointer registration, double register/unregister, classic-vs-ring conflict tests, and full-page registration with a protected next page. It then runs selected-buffer reads from `/dev/zero` for entry counts 1, 32768, and 4096 using both userspace and mmap-backed pbuf rings, checking unique bid consumption and `-ENOBUFS` after draining.

State/persistence behavior: buffer-ring state is transient; the test tracks consumed buffer IDs in a boolean array and uses `/dev/zero` for deterministic data.

Dependencies/integration: requires provided-buffer ring support and optionally pbuf ring mmap support. hppa skips the protected-page test.

Risks/test signals: catches group collision, duplicate registration, invalid address acceptance, buffer reuse, data spill, and incorrect empty-ring handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/buf-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cancel-fd-userdata.c -->
# sources/test-tools/liburing/test/cancel-fd-userdata.c

Purpose: validates combined `IORING_ASYNC_CANCEL_FD` and `IORING_ASYNC_CANCEL_USERDATA` matching, including fixed-file cancellation and same-userdata requests on different fds.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_cancel`, `IORING_ASYNC_CANCEL_FD`, `IORING_ASYNC_CANCEL_USERDATA`, `IORING_ASYNC_CANCEL_FD_FIXED`, `IORING_ASYNC_CANCEL_ALL`, fixed-file registration, and pipes.

Control flow: first test submits four polls on one fd with different `user_data`, cancels exactly the target pair, tolerates either cancel CQE or canceled poll CQE arriving first, then cancels remaining polls. It runs for normal and fixed fds. Second test submits same `user_data` on two fds plus another on the target fd, cancels only `(fd1, ud=1)`, then cleans up all remaining requests.

State/persistence behavior: pending poll requests are the state under test. No persistent resources beyond pipes and optional registered file table.

Dependencies/integration: depends on async cancel flag support; `-EINVAL` on the first cancel path skips. It integrates cancellation matching with the kernel union fields for fd and userdata.

Risks/test signals: failures show overbroad cancel, missed cancel, unsupported fixed-file flag handling, or unexpected CQE ordering/result codes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cancel-fd-userdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cancel-race.c -->
# sources/test-tools/liburing/test/cancel-race.c

Purpose: stress test for races between operation completion and async cancellation.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_read`, `io_uring_prep_cancel64`, `IORING_ASYNC_CANCEL_ANY`, pthreads, pipes, nonblocking setup, and encoded `user_data` sequence/type fields.

Control flow: `test_poll_cancel_race` repeats 10,000 pairs of poll and immediate cancel, expecting both CQEs with allowed results. `test_read_cancel_race` does the same for pipe reads that may cancel or complete with `-EAGAIN`. `test_concurrent_cancel` has one ring submit polls while another thread/ring repeatedly submits cancel-any operations, then drains/cancels leftovers.

State/persistence behavior: state is in-flight request identity and per-iteration user_data. No persistent files.

Dependencies/integration: relies on cancellation support, pipe readiness semantics, and thread scheduling. `no_cancel` skips later tests when unsupported.

Risks/test signals: hangs, missing CQEs, invalid cancel result codes, or duplicate/neither completion outcomes indicate races in cancellation accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cancel-race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cbpf_filter.c -->
# sources/test-tools/liburing/test/cbpf_filter.c

Purpose: comprehensive test suite for classic BPF filters registered against io_uring operations at task and ring scope.

Important APIs/types/functions: `struct io_uring_bpf`, `io_uring_register_bpf_filter_task`, `io_uring_register_bpf_filter`, `IORING_REGISTER_BPF_FILTER`, `IO_URING_BPF_FILTER_DENY_REST`, `IO_URING_BPF_FILTER_SZ_STRICT`, cBPF `sock_filter` arrays, `prctl(PR_SET_NO_NEW_PRIVS)`, and test helpers for NOP, socket, openat/openat2, and connect.

Control flow: the file defines context offsets and endian-safe constants for socket/open/connect filter payloads, then builds allow/deny filters for all ops, socket family/type, open flags/resolve, connect family/address/port/subnet, and stale connect addrlen behavior. `main` probes support, verifies no-new-privs requirements, sets no-new-privs, runs task-level filter tests in child processes, conditionally runs connect filter tests, runs ring-level tests, validates pdu_size writeback/strict errors, and checks inheritance/stacking/cannot-loosen behavior across fork levels.

State/persistence behavior: task-level filter state is inherited across fork and intentionally isolated by child processes; ring-level filter state is bound to a specific ring. Temporary open targets are created/unlinked by open tests.

Dependencies/integration: depends on kernel cBPF filter support, liburing `io_uring/bpf_filter.h`, no-new-privs, sockets, openat2, IPv4/IPv6 address encoding, and fork behavior.

Risks/test signals: high risk of feature drift and endian/layout mismatch. Failures are wrong `-EACCES` allow/deny decisions, pdu size errors, restriction inheritance bugs, or filters that can loosen parent policy.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cbpf_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ce593a6c480a.c -->
# sources/test-tools/liburing/test/ce593a6c480a.c

Purpose: regression for task_work not running while a task blocks in another kernel wait path, using io_uring eventfd notifications.

Important APIs/types/functions: `eventfd`, `io_uring_register_eventfd`, `io_uring_prep_poll_add`, pthread delayed writer, optional SQPOLL fixed file setup, and `t_create_ring_params`.

Control flow: create an eventfd registered as the ring notification target and another eventfd used for a poll request. Submit a poll on the second fd, spawn a thread that writes after one second, synchronously read the notification eventfd, then wait for and validate the poll CQE.

State/persistence behavior: eventfd counters and one pending poll request are the only state. No persistent files.

Dependencies/integration: eventfd notification, poll task_work, optional SQPOLL path via `use_sqpoll` global, and pthread timing.

Risks/test signals: failure or hang indicates the ring failed to process task_work and signal the eventfd while userspace was blocked in `read`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ce593a6c480a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/close-opath.c -->
# sources/test-tools/liburing/test/close-opath.c

Purpose: checks that `IORING_OP_CLOSE` handles both ordinary and `O_PATH` file descriptors without unexpected errors.

Important APIs/types/functions: `io_uring_prep_close`, `io_uring_submit`, `io_uring_wait_cqe`, `openat`, `O_PATH`, and a small `oflgs_t` table.

Control flow: initialize a ring, open `.` once with `O_RDONLY` and once with `O_PATH`, submit close through io_uring for each, and treat unsupported/invalid/EBADF close results as tolerable while flagging other negative errors.

State/persistence behavior: no persistent mutation beyond closing transient fds. Return bits encode which open/close case failed.

Dependencies/integration: depends on Linux `O_PATH` and io_uring close support.

Risks/test signals: useful for regressions where close of `O_PATH` fd crashes or returns unexpected errors. It is intentionally permissive for older kernel support codes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/close-opath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cmd-discard.c -->
# sources/test-tools/liburing/test/cmd-discard.c

Purpose: destructive block-device test for `io_uring_cmd` discard operations.

Important APIs/types/functions: `io_uring_prep_cmd_discard`, `BLOCK_URING_CMD_DISCARD`, `io_uring_submit_and_wait`, `BLKGETSIZE64`, `BLKSSZGET`, `BLKROSET`, `O_DIRECT`, `O_EXCL`, and aligned buffers.

Control flow: `main` requires one block device/file argument, discovers device size and logical block size, allocates an aligned buffer, then for each enabled opcode runs basic ranges, parallel random discard queueing, readonly/BLKROSET rejection, and invalid edge cases for beyond-capacity, overflow, and unaligned ranges.

State/persistence behavior: this test may discard real blocks on the target device and toggles block read-only state. The `config` file warns that mapped devices may be erased/overwritten.

Dependencies/integration: requires a suitable block target, exclusive direct access, discard command support, and privileges for `BLKROSET`.

Risks/test signals: high data-destruction risk. Skips on unsupported direct/exclusive/discard paths; failures are successful invalid commands, failed valid discards, or readonly bypass.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cmd-discard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/config -->
# sources/test-tools/liburing/test/config

Purpose: template configuration file for liburing tests requiring external files/devices and exclusions.

Important APIs/types/functions: shell comments for `TEST_EXCLUDE`, associative `TEST_MAP`, and `TEST_FILES`.

Control flow: no executable flow in the checked-in template. Users copy it to `config.local`, uncomment variables, and define test resources.

State/persistence behavior: warns that configured devices/files may be destructively overwritten by tests. It does not itself persist active settings unless copied/edited outside this file.

Dependencies/integration: consumed by the liburing test runner conventions rather than C code directly.

Risks/test signals: the key risk is accidental inclusion of real devices in destructive tests such as discard/write tests. The template's comments are the main safety signal.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/conn-unreach.c -->
# sources/test-tools/liburing/test/conn-unreach.c

Purpose: verifies io_uring connect and shutdown behavior when connecting to an unreachable IPv4 address.

Important APIs/types/functions: `io_uring_prep_connect`, `io_uring_prep_shutdown`, `getsockopt(SO_ERROR)`, `TCP_NODELAY`, `TCP_SYNCNT`, `TCP_USER_TIMEOUT`, nonblocking sockets, and helper `t_set_nonblock`.

Control flow: configure a TCP socket for faster failure, submit connect to `172.31.5.5:12345`, wait 200 ms, submit shutdown on the same socket, then reap two CQEs. `check_cqe` accepts connect `-ECONNRESET` or `-ENETUNREACH` and shutdown success or `-ENOTCONN`; `-EINVAL` skips for unsupported connect.

State/persistence behavior: transient socket state only. `SO_ERROR` is read between completions to clear/check socket error state.

Dependencies/integration: depends on network stack routing behavior and io_uring connect/shutdown support.

Risks/test signals: environmental networking can affect whether the address is unreachable vs reset. The test accepts two expected connect failures to reduce flake.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/conn-unreach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/connect-rep.c -->
# sources/test-tools/liburing/test/connect-rep.c

Purpose: regression test that repeated io_uring connects to a bound but non-listening socket consistently return `-ECONNREFUSED`, not `-ECONNABORTED`.

Important APIs/types/functions: `io_uring_prep_connect`, `io_uring_queue_init_params`, SQPOLL setup, `bind`, `getsockname`, loopback sockets, and repeated `user_data`.

Control flow: `test` creates a server socket bound to an ephemeral loopback port without listen, creates a bound client socket, optionally lets SQPOLL sleep, then submits 32 connect attempts to the same server address. It runs under normal and SQPOLL rings.

State/persistence behavior: socket local/peer state is reused across attempts; `local_sa` is overwritten after submit to detect stale userspace address use.

Dependencies/integration: depends on loopback TCP and SQPOLL support. Uses `getsockname` for ephemeral port discovery.

Risks/test signals: failure is any connect CQE not equal to `-ECONNREFUSED`, indicating wrong error translation or stale address handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/connect-rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/connect.c -->
# sources/test-tools/liburing/test/connect.c

Purpose: general io_uring connect test covering refused connects, successful connects, async connects, linked timeout cancellation, SQPOLL, and defer-taskrun.

Important APIs/types/functions: `io_uring_prep_connect`, `io_uring_prep_poll_add`, `io_uring_prep_link_timeout`, `IOSQE_ASYNC`, `IOSQE_IO_LINK`, `getsockopt(SO_ERROR)`, `listen`, `bind`, `poll` masks, and TCP syncookies check.

Control flow: each `test(flags)` creates a ring, random loopback port, verifies no-peer connect returns `-ECONNREFUSED` or skips unsupported kernels, then tests successful connect with and without `IOSQE_ASYNC`. `test_connect_timeout` fills a zero-backlog accept queue, submits a second linked connect plus tiny timeout, and expects connect `-ECANCELED` plus timeout `-ETIME`. Main tries normal, SQPOLL, and defer-taskrun rings and passes if any supported path passes.

State/persistence behavior: transient sockets and random port state; no files except probing `/proc/sys/net/ipv4/tcp_syncookies`.

Dependencies/integration: requires loopback TCP, io_uring connect, and optionally SQPOLL/defer support.

Risks/test signals: timing and kernel TCP settings affect timeout case. Failures indicate connect result, poll completion, or link-timeout cancellation regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/coredump.c -->
# sources/test-tools/liburing/test/coredump.c

Purpose: regression test that a process with an outstanding io_uring async read can segfault and core-dump without hanging in uninterruptible state.

Important APIs/types/functions: `fork`, `wait`, `pipe`, `io_uring_queue_init`, `io_uring_prep_read`, `IOSQE_ASYNC`, and sanitizer conditional compilation.

Control flow: non-sanitizer builds fork a child. The child creates a ring, submits an async pipe read, then dereferences NULL. The parent waits and unlinks `core`, treating return from wait as pass.

State/persistence behavior: may generate a `core` file, which is removed. No data validation is performed.

Dependencies/integration: disabled under `CONFIG_USE_SANITIZER`; depends on OS coredump behavior and io_uring async task cleanup.

Risks/test signals: the primary signal is absence of hang. It does not assert signal status, so it is a liveness regression test rather than a semantic CQE test.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cq-full.c -->
# sources/test-tools/liburing/test/cq-full.c

Purpose: simple CQ overflow/full-ring test using repeated NOP submission.

Important APIs/types/functions: `io_uring_queue_init_params`, `io_uring_prep_nop`, `io_uring_peek_cqe`, `io_uring_cqe_seen`, `ring.cq.koverflow`, and `IORING_FEAT_NODROP`.

Control flow: create a four-entry ring, submit three batches of four NOPs without draining between batches, then peek/drain all visible CQEs and check that at least eight completions were observed and overflow accounting matches kernels without `NODROP`.

State/persistence behavior: CQ head/tail and overflow counters are the tested state. No external persistence.

Dependencies/integration: depends on small CQ sizing and kernel overflow feature semantics.

Risks/test signals: failures are too few visible CQEs or incorrect overflow counter behavior. Newer `NODROP` kernels alter expected overflow accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cq-full.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cq-overflow.c -->
# sources/test-tools/liburing/test/cq-overflow.c

Purpose: extensive CQ overflow and dropped-CQE handling test across NOP fairness, batch reaping, IOPOLL/defer modes, direct reads, and fault injection.

Important APIs/types/functions: `io_uring_cq_has_overflow`, `io_uring_get_events`, `io_uring_wait_cqe`, `io_uring_peek_batch_cqe`, `io_uring_cq_ready`, `ring.cq.koverflow`, `IORING_FEAT_NODROP`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_DEFER_TASKRUN`, direct `readv`, and helper buffer/file creation.

Control flow: `test_overflow_handling` creates a tiny CQ, overflows it with NOPs, cycles completions back into submissions, optionally batch-reaps, and checks fair per-user_data counts. `test_overflow` checks fixed overflow count on a four-entry CQ. `test_io` submits many direct reads, optionally injects a bad buffer, and reconciles reaped completions with overflow/drop counters. Main runs 16 mode combinations, then file I/O overflow tests with increasing delay and fault mode.

State/persistence behavior: creates `.cq-overflow` temporary file and allocated iovecs. The CQ overflow counter and dropped-CQE `-EBADR` paths are central state.

Dependencies/integration: direct I/O support, optional fault-injection environment, defer-taskrun probing, and kernel overflow semantics.

Risks/test signals: high coverage but timing-sensitive. Failures include lost CQEs, out-of-order sequence when no drops occurred, wrong overflow accounting, or bad read result handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cq-overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cq-peek-batch-mixed.c -->
# sources/test-tools/liburing/test/cq-peek-batch-mixed.c

Purpose: validates `io_uring_peek_batch_cqe` on `IORING_SETUP_CQE_MIXED` rings containing both 16-byte and 32-byte CQEs plus internal skip entries at wrap.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_NOP_CQE32`, `IORING_CQE_F_32`, `IORING_CQE_F_SKIP`, `io_uring_cqe_nr`, `io_uring_peek_batch_cqe`, and custom `advance_cqes`.

Control flow: initialize a mixed CQE ring and require 16 CQ slots. Submit plain and 32-byte NOPs, verify batch count returns logical CQEs not slots, then advance by physical slot count. It constructs a wrap case where a 32-byte CQE cannot fit before the end, expects the batch to stop before the skip entry, then expects the next batch to hide the skip and return the wrapped 32-byte CQE plus following plain CQE.

State/persistence behavior: CQ head advancement must account for variable CQE slot width. No external persistence.

Dependencies/integration: requires kernel mixed-CQE support and exact ring size assumptions.

Risks/test signals: catches skip CQEs exposed to applications, wrong big CQE payload, bad `F_32` flags, or incorrect batch count/advance behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cq-peek-batch-mixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cq-peek-batch.c -->
# sources/test-tools/liburing/test/cq-peek-batch.c

Purpose: basic test for `io_uring_peek_batch_cqe` on a normal CQ ring.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_prep_nop`, `io_uring_peek_batch_cqe`, `io_uring_cq_advance`, and `user_data` verification.

Control flow: create a four-entry ring, assert empty batch returns zero, submit four NOPs and verify batch returns four CQEs with user_data 0-3, submit four more before advancing, advance the first batch, verify the next batch returns user_data 4-7, then advance all and exit.

State/persistence behavior: CQ head/tail and user_data order are tested. No persistent resources.

Dependencies/integration: depends only on core io_uring NOP and batch peek behavior.

Risks/test signals: detects incorrect batch count, order, or CQ advancement behavior, especially when more CQEs arrive before old ones are advanced.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cq-peek-batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cq-ready.c -->
# sources/test-tools/liburing/test/cq-ready.c

Purpose: verifies `io_uring_cq_ready` accurately tracks visible completion count as CQEs are produced and advanced.

Important APIs/types/functions: `io_uring_cq_ready`, `io_uring_cq_advance`, `io_uring_prep_nop`, and a four-entry ring.

Control flow: start with zero ready CQEs, submit four NOPs and expect four ready, advance all and expect zero, submit four more, then advance by 1, 2, and 1 while expecting ready counts 3, 1, and 0.

State/persistence behavior: only CQ head/tail memory state is tested.

Dependencies/integration: core liburing CQ helpers and NOP completion.

Risks/test signals: catches stale cached readiness or incorrect advancement math.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cq-ready.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/cq-size.c -->
# sources/test-tools/liburing/test/cq-size.c

Purpose: checks `IORING_SETUP_CQSIZE` behavior for explicit CQ sizing and rejection of zero-sized CQ.

Important APIs/types/functions: `io_uring_queue_init_params`, `IORING_SETUP_CQSIZE`, `io_uring_params.cq_entries`, and `io_uring_queue_exit`.

Control flow: request four SQ entries with 64 CQ entries and verify the kernel-provided CQ size is at least 64; then try CQ size zero and require `-EINVAL`. `-EINVAL` on the first setup is treated as unsupported and skipped/pass.

State/persistence behavior: no persistence beyond ring setup parameters.

Dependencies/integration: kernel support for `IORING_SETUP_CQSIZE`.

Risks/test signals: detects kernels accepting invalid zero CQ size or ignoring requested larger CQ size.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/cq-size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/d4ae271dfaae.c -->
# sources/test-tools/liburing/test/d4ae271dfaae.c

Purpose: SQPOLL regression test for a missing return-value clear when the SQ thread is busy.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, fixed-file registration, direct `readv`, `t_create_file`, `t_posix_memalign`, and `io_uring_wait_cqe`.

Control flow: create an SQPOLL ring, use an argument file or create `.sqpoll.tmp`, open it with `O_DIRECT`, allocate ten aligned 4 KiB iovecs, register the file, submit ten fixed-file reads with short sleeps, and verify each CQE returns 4096 bytes.

State/persistence behavior: optional temporary file is unlinked after open; registered file table and SQPOLL thread state are central.

Dependencies/integration: depends on SQPOLL permissions/support and direct I/O. Skips on direct-I/O permission/flag failures.

Risks/test signals: failures are short/negative reads or wait errors, indicating SQPOLL busy-path accounting regression.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/d4ae271dfaae.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/d77a67ed5f27.c -->
# sources/test-tools/liburing/test/d77a67ed5f27.c

Purpose: SQPOLL wakeup regression test ensuring `io_uring_submit_and_wait` wakes a sleeping SQ thread and returns a NOP completion.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `sq_thread_idle`, `io_uring_prep_nop`, `io_uring_sqe_set_data`, `io_uring_submit_and_wait`, `io_uring_peek_cqe`, alarm timeout, and `io_uring_cqe_get_data`.

Control flow: create an SQPOLL ring with 100 ms idle, sleep long enough for SQ thread to idle, arm a one-second alarm, submit a NOP and wait for one completion, then verify CQE data is 42.

State/persistence behavior: only SQPOLL thread sleep/wakeup state and CQE user data.

Dependencies/integration: SQPOLL support and signal/alarm handling.

Risks/test signals: timeout or missing CQE indicates SQPOLL wakeup failure; wrong data catches CQE data corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/d77a67ed5f27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/defer-taskrun.c -->
# sources/test-tools/liburing/test/defer-taskrun.c

Purpose: multi-scenario test for `IORING_SETUP_DEFER_TASKRUN`, taskrun flags, eventfd notification, disabled rings, exec cleanup, ring shutdown, and drained writes.

Important APIs/types/functions: `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_TASKRUN_FLAG`, `IORING_SETUP_R_DISABLED`, `io_uring_get_events`, `io_uring_enable_rings`, eventfd helpers, `execve("/proc/self/exe")`, socket pairs, direct reads, and `IOSQE_IO_DRAIN`.

Control flow: after probing defer support, main runs: disabled-ring/thread shutdown error expectations; child exec while direct read is pending; eventfd notification where task_work is deferred until `get_events`; taskrun flag visibility and clearing through peek; ring shutdown processing of pending recv; and a drained writev whose iovec bases are nulled after submit to verify state capture.

State/persistence behavior: may create/unlink `.defer-taskrun`; otherwise state is ring flags, pending task_work, eventfd counters, socket buffers, and child process lifecycle.

Dependencies/integration: defer-taskrun kernel support, eventfd, pthread/fork/exec, direct I/O optional test input, and socket pairs.

Risks/test signals: catches missed task_work, wrong `-EBADFD`/`-EEXIST` disabled-ring behavior, eventfd notification timing bugs, taskrun flag cache issues, and shutdown cleanup regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/defer-taskrun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/defer-tw-timeout.c -->
# sources/test-tools/liburing/test/defer-tw-timeout.c

Purpose: verifies `io_uring_submit_and_wait_timeout` with `DEFER_TASKRUN` times out waiting for too many events while still making the one completed CQE visible.

Important APIs/types/functions: `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `io_uring_submit_and_wait_timeout`, `io_uring_peek_cqe`, direct file reads, pipe reads, and pthread delayed writer.

Control flow: create a defer-taskrun ring. `test_file` submits one direct file read and waits for two events with a one-second timeout; it expects return 1 and exactly one CQE. `test_poll` submits one pipe read, writes from a thread after 100 ms, again waits for two and expects exactly one CQE.

State/persistence behavior: optional temporary file `.defer-tw-timeout.<pid>` is created/unlinked; pending task_work and CQ visibility are the core state.

Dependencies/integration: defer-taskrun support, direct I/O support for file case, pipes and pthread timing.

Risks/test signals: failure indicates timeout path failed to flush deferred task_work or exposed too many/few completions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/defer-tw-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/defer.c -->
# sources/test-tools/liburing/test/defer.c

Purpose: regression tests for deferred/drained/link behavior, CQ overflow/dropped counters, and linked cancellation in poll/SQPOLL rings.

Important APIs/types/functions: `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `io_uring_prep_nop`, `io_uring_prep_remove_buffers`, `io_uring_prep_timeout`, `io_uring_prep_link_timeout`, `ring.cq.koverflow`, `ring.sq.kdropped`, `IORING_SETUP_IOPOLL`, and `IORING_SETUP_SQPOLL`.

Control flow: helper context allocates arrays of SQEs/CQEs and waits for completions. Tests verify linked NOPs preserve user_data, remove-buffer links cancel after first `-ENOENT`, linked timeouts with drain complete, artificial CQ overflow and dropped counters do not hang drained NOPs, and SQPOLL+IOPOLL linked remove-buffer cancellation behaves as expected.

State/persistence behavior: manipulates ring overflow/dropped counters directly and uses pending linked request chains. No external persistence.

Dependencies/integration: IOPOLL and SQPOLL support for specific subtests; core timeout/link/drain support.

Risks/test signals: catches hangs in drain scheduling, wrong cancellation result propagation, and user_data corruption in canceled linked chains.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/defer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/double-poll-crash.c -->
# sources/test-tools/liburing/test/double-poll-crash.c

Purpose: syzkaller-derived crash reproducer for double-poll/io_uring interactions.

Important APIs/types/functions: raw `__sys_io_uring_setup`, raw ring/SQE `mmap`, manual SQ tail/array manipulation in `syz_io_uring_submit`, `__sys_io_uring_enter`, `syz_open_dev`, fixed virtual addresses, and an `ioctl` on `/dev/char/4:21`.

Control flow: x86 non-sanitizer builds mmap fixed regions, set up a large io_uring through raw syscalls, open a device path, hand-build an SQE at a fixed address, submit it by writing ring memory manually, enter the ring with a large submit count, then issue an ioctl with crafted data.

State/persistence behavior: mutates kernel ring state through raw mapped memory and device ioctl state; no persistent files are created by the test itself.

Dependencies/integration: architecture-specific, skips non-x86 and sanitizer builds, depends on syzkaller syscall wrappers and device availability.

Risks/test signals: primary signal is survival without kernel crash. It is intentionally low-level and brittle to layout/architecture changes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/double-poll-crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/drop-submit.c -->
# sources/test-tools/liburing/test/drop-submit.c

Purpose: tests `IORING_SETUP_SUBMIT_ALL` behavior when a submission batch contains invalid SQEs that would otherwise be dropped.

Important APIs/types/functions: `IORING_SETUP_SUBMIT_ALL`, `io_uring_prep_nop`, invalid `io_uring_prep_read`, bad `ioprio`, and `io_uring_submit`.

Control flow: `test` queues four NOPs and two invalid reads. With `SUBMIT_ALL`, it expects all six SQEs to be submitted; without the flag, it expects five due to the first invalid SQE stopping/dropping further submission. Main runs both modes.

State/persistence behavior: no persistent state; the test checks submit return counts rather than reaping CQEs.

Dependencies/integration: depends on kernel support for `IORING_SETUP_SUBMIT_ALL`; if setup fails, main returns success/skip-like zero for the first mode.

Risks/test signals: catches regressions in batch submission semantics and invalid SQE handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/drop-submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eeed8b54e0df.c -->
# sources/test-tools/liburing/test/eeed8b54e0df.c

Purpose: validates `RWF_NOWAIT` read behavior through io_uring after dropping file cache.

Important APIs/types/functions: `io_uring_prep_readv`, `RWF_NOWAIT`, `posix_fadvise(...DONTNEED)`, `fsync`, temporary file creation/unlink, and `io_uring_peek_cqe`.

Control flow: create and unlink a one-block file, write zeros, fsync, evict with fadvise, submit a NOWAIT readv for 4096 bytes, and accept either `-EAGAIN` or a full 4096-byte read. `-EOPNOTSUPP` skips.

State/persistence behavior: temporary `testfile` is unlinked after open; page cache state is intentionally manipulated.

Dependencies/integration: filesystem support for NOWAIT/direct cache behavior and io_uring readv.

Risks/test signals: failure is any unexpected CQE result. Cache state may make either EAGAIN or success valid.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eeed8b54e0df.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/empty-eownerdead.c -->
# sources/test-tools/liburing/test/empty-eownerdead.c

Purpose: regression test ensuring an empty `io_uring_enter` on an SQPOLL ring does not fail with `EOWNERDEAD` or other errors.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `sq_thread_idle`, `t_create_ring_params`, and raw `__sys_io_uring_enter`.

Control flow: create a one-entry SQPOLL ring, then call `io_uring_enter` with zero submit and zero wait. Any negative return is failure, with a special diagnostic for historical `EOWNERDEAD`.

State/persistence behavior: only SQPOLL ring/thread state; no files.

Dependencies/integration: SQPOLL support and raw syscall wrapper.

Risks/test signals: catches old-kernel empty-enter failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/empty-eownerdead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eploop.c -->
# sources/test-tools/liburing/test/eploop.c

Purpose: verifies that adding an io_uring fd to epoll and then polling that epoll fd from the same ring does not recursively generate unbounded completion events.

Important APIs/types/functions: `epoll_create1`, `epoll_ctl`, `io_uring_prep_poll_multishot`, `io_uring_prep_nop`, `io_uring_wait_cqe`, and `io_uring_peek_cqe`.

Control flow: create a ring and epoll instance, add the ring fd to epoll, submit a multishot poll on the epoll fd, submit a NOP to make the ring readable, reap two CQEs, then assert no extra CQE is generated.

State/persistence behavior: epoll interest in the ring fd and the ring's own completion readiness form a potential feedback loop; no persistent resources.

Dependencies/integration: epoll, multishot poll, and io_uring fd readiness.

Risks/test signals: failure is extra CQE generation or wait errors, indicating recursive event-loop handling regression.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eploop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/epwait.c -->
# sources/test-tools/liburing/test/epwait.c

Purpose: tests `IORING_OP_EPOLL_WAIT` under ready, delayed, deletion, closed-epoll, race, defer-taskrun, and SQPOLL scenarios.

Important APIs/types/functions: `io_uring_prep_epoll_wait`, `epoll_create1`, `epoll_ctl`, pipes, pthread writer, atomic stop flag, `IORING_SETUP_DEFER_TASKRUN`, and `IORING_SETUP_SQPOLL`.

Control flow: `test` creates two pipes in an epoll set and runs: immediate ready events, delayed writer events, fd deletion during wait, closing epoll fd while wait is pending, and a race test. The race test creates eight pipes, repeatedly submits epoll waits while a thread writes to all pipes, prunes readiness, and verifies submitted/completed user_data sequences for 1000 completions. Main runs normal, defer-taskrun, and SQPOLL.

State/persistence behavior: pipe buffers and epoll interest lists are transient state. Global `no_epoll_wait` skips if kernel returns `-EINVAL`.

Dependencies/integration: kernel `IORING_OP_EPOLL_WAIT`, epoll, pipes, pthread timing, and supported ring modes.

Risks/test signals: catches missing support, stale/deleted epoll state bugs, CQE user_data mismatch, negative epoll results, or race-induced lost completions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/epwait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-disable.c -->
# sources/test-tools/liburing/test/eventfd-disable.c

Purpose: verifies runtime disable/enable of CQ eventfd notifications, including defer-taskrun rings.

Important APIs/types/functions: `io_uring_register_eventfd`, `io_uring_cq_eventfd_enabled`, `io_uring_cq_eventfd_toggle`, `eventfd`, `io_uring_prep_readv`, `io_uring_prep_nop`, and `IORING_SETUP_DEFER_TASKRUN`.

Control flow: register an eventfd, disable CQ eventfd notifications, submit an io_uring read on that eventfd plus 63 NOPs, and verify only NOP CQEs arrive. Re-enable notifications, submit one NOP, then expect both the NOP CQE and the eventfd read CQE with value 1. Main runs normal and, if probed, defer-taskrun mode.

State/persistence behavior: eventfd counter and CQ notification enabled flag are the tested state. No files persist.

Dependencies/integration: requires CQ eventfd toggle support; skips if CQ flags are unavailable.

Risks/test signals: failures indicate notifications still firing while disabled, not firing after re-enable, wrong eventfd value, or defer-taskrun notification regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-disable.c -->

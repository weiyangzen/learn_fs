# subset-b-009381 research

Grouped research report for the subset B work item `subset-b-009381`. Each section preserves the source path in its title and is wrapped with the exact `BEGIN_FILE_RESEARCH` / `END_FILE_RESEARCH` markers expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sleep.c -->
# sources/test-tools/stress-ng/stress-sleep.c

## Purpose

`stress-sleep.c` implements the `sleep` stressor, which creates many pthreads per worker and repeatedly exercises short sleep primitives. It stresses scheduler wakeups, interruptible sleeps, high-resolution timer behavior, CPU idle-state residency delays, and x86 WAITPKG `tpause` when available. Verification is always enabled because the stressor checks that requested sleep durations do not complete earlier than expected.

## Important APIs, Types, and Functions

- `stress_ctxt_t` carries per-thread state: the shared `stress_args_t`, requested thread count, pthread handle, and underrun counter.
- `stress_sleep_times_t` stores both `stress_time_now()` and `CLOCK_MONOTONIC` readings so timing checks can tolerate platform clock differences.
- `stress_sleep_time_now()` captures wall-clock and monotonic timestamps, falling back to `stress_time_now()` if `clock_gettime(CLOCK_MONOTONIC)` fails or is unavailable.
- `stress_time_delta()` returns the larger observed delta across the two time sources to avoid falsely reporting underruns during clock warps.
- `stress_pthread_func()` is the worker thread body. It performs C-state residency sleeps, `nanosleep()`, `shim_usleep()`, optional `pselect()`, `select()`, and optional x86 `stress_asm_x86_tpause()`.
- `stress_sleep()` is the stressor entry point. It parses `sleep-max`, creates the counter lock, installs the `SIGALRM` handler, starts up to `sleep_max` threads, waits until stop, joins threads, aggregates underruns, and destroys the lock.

## Control Flow

The stressor determines `sleep_max` from settings or maximize/minimize flags, creates a shared bogo-operation lock, installs a `SIGALRM` handler that flips `thread_terminate`, and synchronizes with the global stress-ng start barrier. It then attempts to create up to `sleep_max` pthreads. Each thread loops while both `stress_continue(args)` and `thread_terminate == false`.

Inside each pthread iteration, the code first walks the CPU idle-state list from `stress_cpuidle_cstate_list_head()` and sleeps for each residency target using `nanosleep()`. It then runs fixed nanosecond sleep sequences via `nanosleep()`, fixed microsecond sequences via `shim_usleep()`, optional nanosecond sleeps through `pselect()`, optional microsecond sleeps through `select()`, and optional x86 `tpause` loops when WAITPKG is present. After the sequence it increments the bogo counter with `stress_bogo_inc_lock()`. The parent sleeps in a 10 ms interruptible loop until termination, then cancels the alarm, sets `thread_terminate`, joins all created threads, and fails if any underruns were detected.

## State and Persistence Behavior

Persistent state is limited to process-local globals under pthread builds: `stress_sleep_counter_lock`, `thread_terminate`, and a signal set. The large `ctxts[MAX_SLEEP]` array is static inside `stress_sleep()` and reused across invocations in the same process. Each thread writes only its own `underruns` field, while the bogo counter is protected by the shared stress-ng lock. The stressor has no file persistence and no external state beyond CPU idle-state discovery.

## Dependencies and Integration Points

The file depends on pthread support, `sys/select.h`, stress-ng's timing, locking, signal, synchronization, CPU idle, and bogo accounting helpers. Optional integration points include `CLOCK_MONOTONIC`, `pselect()`, `select()`, x86 WAITPKG detection through `stress_cpu_x86_has_waitpkg()`, and assembly `tpause`. The exported `stress_sleep_info` registers the stressor with classes `CLASS_INTERRUPT | CLASS_SCHEDULER | CLASS_OS`, its option table, and `VERIFY_ALWAYS`. Without pthread support it exports `stress_unimplemented`.

## Risks and Edge Cases

The stressor can request up to 30,000 threads per worker, so resource exhaustion is expected and handled for `pthread_create()` returning `EAGAIN`. Early wakeup checks depend on timing precision; the dual-clock delta reduces false positives but cannot eliminate timing noise on virtualized or heavily loaded systems. The signal handler writes a volatile boolean only, which is appropriate, but `thread_terminate` is global and should be reset if this entry point were ever reused in-process after a terminated run. Failure paths before `stress_lock_destroy()` can leak the counter lock if signal handler setup fails after lock creation.

## Test Signals

Good test signals include a successful run with `--sleep 1 --sleep-max 1`, a higher-thread resource-limited run showing the informational "could not reach requested threads" path, and verification failure absence under `--verify`. Platform coverage should include builds with and without `pselect()`, with x86 WAITPKG when available, and without pthread support to validate the unimplemented registration.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-smi.c -->
# sources/test-tools/stress-ng/stress-smi.c

## Purpose

`stress-smi.c` implements the `smi` stressor, which triggers x86 System Management Interrupts by writing a no-op command to the APM I/O port. It optionally reads the x86 `MSR_SMI_COUNT` model-specific register before and after the run to estimate SMI rate. On x86_64 it also checks that SMI handling does not unexpectedly clobber general-purpose registers other than the registers used by the `out` instruction.

## Important APIs, Types, and Functions

- `MSR_SMI_COUNT`, `APM_PORT`, and `STRESS_SMI_NOP` define the hardware interfaces used by the stressor.
- `smi_regs_t`, `SAVE_REG`, and `SAVE_REGS` capture x86_64 register snapshots around the port write.
- `stress_smi_supported()` enforces `CAP_SYS_MODULE`, `CAP_SYS_RAWIO`, root privileges, and CPU MSR support before the stressor is allowed to run.
- `stress_smi_count()` sums `MSR_SMI_COUNT` across all online CPUs via `stress_x86_readmsr64()`.
- `stress_smi()` is the entry point. It tries to load `msr` if needed, enables I/O permissions with `ioperm()`, synchronizes, repeatedly emits `out` to port `0xb2`, checks registers on x86_64, increments bogo operations, reports SMI rate, and unloads the module if it loaded it.

## Control Flow

At startup, the stressor probes MSR readability on CPU 0. If the read fails, instance zero attempts to load the `msr` module, but module-load failure is tolerated because only rate reporting depends on MSR reads. The process then enables write access to the APM port with `ioperm(APM_PORT, 2, 1)`. After the stress-ng synchronization barrier, instance zero captures the initial summed SMI count and timestamp when readable.

The main loop snapshots registers on x86_64, executes inline assembly `out %al,%dx` with the no-op SMI command and APM port, snapshots registers again, normalizes expected `rax` and `rdx` differences, reports any other register clobber, and increments the bogo counter. On shutdown it disables I/O permissions, takes a final MSR count, computes SMIs per second per CPU and microseconds per SMI when reliable, and unloads the `msr` module if this run loaded it.

## State and Persistence Behavior

The stressor modifies host-visible state by enabling I/O port permissions for the process and potentially loading/unloading the Linux `msr` kernel module. It stores only local counters, timestamps, and static register snapshots. No files are written. Hardware SMI counts are read from per-CPU MSRs but not persisted.

## Dependencies and Integration Points

The implementation is Linux x86-specific and requires `sys/io.h`, `ioperm()`, in/out assembly support, and stress-ng helpers for capabilities, architecture, CPU count, MSR access, and module management. The exported `stress_smi_info` is `CLASS_CPU | CLASS_PATHOLOGICAL`, `VERIFY_ALWAYS`, and has a `.supported` callback. Nonmatching builds export `stress_unimplemented`.

## Risks and Edge Cases

This is a privileged, pathological hardware stressor. It needs raw I/O and root-level permissions, may trigger firmware paths with platform-specific behavior, and can perturb system latency. The module load/unload path is intentionally best-effort but can race with external module users; `already_loaded` mitigates unloading a preexisting module. SMI count arithmetic assumes final count is not lower than initial count. Register verification is only compiled for x86_64 and intentionally excludes `rax`/`rdx` because the `out` instruction uses them.

## Test Signals

Expected skip behavior is a key test signal: non-root, missing `CAP_SYS_RAWIO`, missing `CAP_SYS_MODULE`, non-x86, or non-Linux builds should skip or register unimplemented. On a suitable x86 Linux test host, a short run should increment bogo operations and print either an SMI rate or a message that `MSR_SMI_COUNT` is unreadable. Verification should not report register clobbering.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sock.c -->
# sources/test-tools/stress-ng/stress-sock.c

## Purpose

`stress-sock.c` implements the main `sock` stressor. It creates a forked client/server pair and exercises socket creation, connection setup, send/receive APIs, socket options, ioctls, TCP options, port reservation, interface selection, and optional zero-copy sends. It supports multiple domains, socket types, protocols, and send/receive methods, with metrics for message rate and queue depth.

## Important APIs, Types, and Functions

- `stress_sock_options_t` maps user-facing method/type/protocol names to numeric constants.
- `sock_options_opts`, `sock_options_types`, and `sock_options_protocols` back the `sock-opts`, `sock-type`, and `sock-protocol` option parsers.
- `stress_get_congestion_controls()` reads `/proc/sys/net/ipv4/tcp_allowed_congestion_control` and returns congestion-control names for optional TCP testing.
- `stress_sock_ioctl()` exercises socket-related ioctls such as ownership, interface config, timestamps, namespace fd, and Unix socket backing-file queries.
- `stress_sock_invalid_recv()` intentionally calls `recv`, `recvmsg`, and `recvmmsg` with invalid flags or fds.
- `stress_sock_client()` connects to the server, exercises get/set socket options and receive paths, samples input queue metrics, and unlinks AF_UNIX socket paths.
- `stress_sock_server()` binds/listens, accepts clients, sends data through `send`, `sendmsg`, or `sendmmsg`, samples output queue metrics, and kills the client on cleanup.
- `stress_sock_kernel_rt()` detects PREEMPT_RT kernels and avoids some ownership ioctls when realtime behavior could be sensitive.
- `stress_sock()` parses options, validates interfaces, reserves a port, allocates the shared I/O buffer, forks the client, and runs the server.

## Control Flow

The entry point installs a `SIGCHLD` handler, loads settings for domain, interface, port, zero-copy, send method, socket type, and protocol, and adjusts protocol to zero for AF_UNIX. It validates the requested interface and reserves a wrapped per-instance port through stress-ng's network port allocator. It installs a `SIGPIPE` stop handler, mmaps a 64 KiB anonymous I/O buffer, synchronizes start, and forks.

The child applies failure-injection setup, pins to the parent CPU, and runs `stress_sock_client()`. The client loops over socket creation, deliberately tries invalid socket arguments, connects with retries, optionally enables zero-copy, randomizes TCP congestion control for IPv4, exercises IP/TCP/SOL_SOCKET get/set paths, then receives data using the method corresponding to the selected sender. It periodically samples `FIONREAD`/`SIOCINQ`, calls invalid receive helpers, and records average queued input bytes.

The parent runs `stress_sock_server()`. The server creates a socket, enables `SO_REUSEADDR`, deliberately tests invalid `setsockopt()` combinations, binds/listens with retry on `EADDRINUSE`, optionally mmaps the socket fd just to exercise that path, and accepts connections. For each accepted socket it checks names, socket buffer sizes, optional TCP quickack/nodelay, fills the shared buffer, and sends a configured number of message batches. It periodically samples `SIOCOUTQ`, reads fdinfo, runs socket ioctls, closes the accepted fd, and records messages per second plus average output queue length. Cleanup closes sockets, unmaps buffers, unlinks AF_UNIX paths, kills the child, and releases the reserved port.

## State and Persistence Behavior

The stressor persists no repository or user data. Runtime state includes a shared anonymous mmap buffer inherited across fork, reserved network port state maintained by stress-ng, transient AF_UNIX socket paths, and per-run metrics. It reads but does not write `/proc/sys/net/ipv4/tcp_allowed_congestion_control`. It can change socket-local options extensively, but those changes are per-fd.

## Dependencies and Integration Points

The file integrates with stress-ng network helpers (`stress_net_sockaddr_if_set`, `stress_net_interface_exists`, port reserve/release, domain names), signal helpers, affinity helpers, mmap/madvise helpers, fdinfo readers, and metrics. It depends on standard socket APIs, Linux socket ioctls, TCP headers, Unix-domain socket headers, and optional `sendmsg`, `sendmmsg`, `recvmsg`, `recvmmsg`, `MSG_ZEROCOPY`, and `SO_ZEROCOPY`. The exported stressor is `CLASS_NETWORK | CLASS_OS | CLASS_IPC`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

The main risks are resource exhaustion, flaky kernel-option availability, and network namespace/interface assumptions. Port reservation mitigates instance collisions but bind can still hit `EADDRINUSE` and retries. Some socket options are read-only, privileged, or protocol-specific; failures are usually intentionally ignored, while core socket/connect/bind/listen failures are reported. AF_UNIX cleanup depends on the address helper returning a stable `sun_path`. Zero-copy enablement is best-effort and disables itself after a warning. `stress_get_congestion_controls()` returns pointers into a static buffer plus a heap pointer array, so consumers must not outlive the static buffer contents.

## Test Signals

Useful test coverage includes default IPv4 stream TCP, AF_UNIX, random send method, `sendmsg`/`sendmmsg` builds, `--sock-nodelay`, invalid interface fallback, MPTCP availability when compiled, and `--sock-zerocopy` on kernels with and without support. Expected metrics are "messages sent per sec", "byte average out queue length", and "byte average in queue length"; successful runs should release ports and leave no AF_UNIX socket path behind.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockabuse.c -->
# sources/test-tools/stress-ng/stress-sockabuse.c

## Purpose

`stress-sockabuse.c` implements `sockabuse`, a socket misuse and abuse stressor. It builds a normal IPv4 client/server pair but also applies many file, xattr, mmap, fcntl, ioctl, and socket-option operations to socket file descriptors, and cycles through a broad set of socket domains and types to probe kernel error paths.

## Important APIs, Types, and Functions

- `sockabuse_domains`, `sockabuse_types`, and `sockabuse_sockopts` are compile-time arrays of available address families, socket types, and `SOL_SOCKET` options.
- `sockabuse_domain_type_flags` records which domain/type combinations still appear usable so the stressor can stop retrying combinations that fail.
- `stress_sockabuse_socket()` iterates through domain/type combinations, opens sockets with protocol zero and random protocols, and updates the flags.
- `stress_sockabuse_sockopts()` rotates through `getsockopt(SOL_SOCKET, option)` calls on a supplied fd.
- `stress_sockabuse_fd()` deliberately applies inappropriate file operations to a socket fd: `fdatasync`, `fsync`, `fallocate`, `fchdir`, `fchmod`, `fchown`, `flock`, xattr calls, `ftruncate`, `lseek`, pidfd signal, mmap, copy-file-range, fadvise, and sync-file-range.
- `stress_sockabuse_client()` connects and receives one buffer, then abuses the connected fd.
- `stress_sockabuse_server()` repeatedly binds/listens/sends one buffer to accepted clients, abuses accepted and listening fds, and updates throughput metrics.
- `stress_sockabuse()` handles option parsing, port reservation, signal setup, fork, and cleanup.

## Control Flow

The entry point initializes all domain/type flags to enabled, installs child and `SIGPIPE` handlers, reads `sockabuse-port`, reserves a per-instance IPv4 port, synchronizes, and forks. The child runs the client loop on the same CPU as the parent. The parent runs the server and kills the child on completion.

The client repeatedly opens an IPv4 stream socket, resolves the server address, retries connection with increasing backoff, receives a fixed 8 KiB buffer, abuses the fd with general file operations and socket options, then shuts down and closes it. The server repeatedly opens a listening IPv4 stream socket, enables `SO_REUSEADDR`, binds/listens, accepts up to sixteen client sockets per listener instance, sends an 8 KiB pattern buffer, abuses the accepted socket and the listening socket, closes them, and calls `stress_sockabuse_socket()` to exercise unrelated socket-family/type construction paths. Bogo operations increment once per server listener cycle.

## State and Persistence Behavior

The stressor uses process-local static state to remember domain/type combinations that have failed. It creates no persistent files, but it may call xattr and file-like syscalls against socket fds and may invoke mmap attempts on them. Network port reservation state is maintained by stress-ng and released at the end. Runtime metrics record messages per second.

## Dependencies and Integration Points

The file depends on stress-ng networking, affinity, signal, kill, builtin, and fd shim helpers. Platform features are heavily conditional: many address families, `SO_*` options, `flock`, xattr APIs, `futimens`, `FIONREAD`, `copy_file_range`, `pidfd_send_signal`, `posix_fadvise`, and sync-file-range are included only when available. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`, with `sockabuse-port` as its only option.

## Risks and Edge Cases

This stressor intentionally sends invalid operations to socket fds; most failures are expected and ignored. It can generate noisy kernel paths on systems with unusual protocol modules or restricted address families. The static domain/type flag array is mutable and process-local, so it adapts during a run but is not shared across forked processes. Some file operations can be permission-sensitive or return platform-specific errors; the code intentionally does not treat those as failures. Port bind loops can spin through `EADDRINUSE` until the global continue flag clears.

## Test Signals

Expected signals include successful client/server message exchange, bogo increments, and "messages sent per sec" metric. Runs should tolerate missing optional APIs through compile-time guards. Port exhaustion should produce skip/no-resource behavior rather than unbounded failure. Kernel logs should be monitored when adding new abuse operations because this stressor is intended to exercise unusual syscall combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockabuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockdiag.c -->
# sources/test-tools/stress-ng/stress-sockdiag.c

## Purpose

`stress-sockdiag.c` implements `sockdiag`, a Linux netlink stressor that sends `NETLINK_SOCK_DIAG` dump requests and parses returned socket diagnostic attributes. It focuses on kernel sock_diag request/response paths, especially Unix socket diagnostic messages, while cycling request families and `udiag_show` masks.

## Important APIs, Types, and Functions

- `stress_sockdiag_request_t` combines `nlmsghdr` and `unix_diag_req` into the request payload sent to netlink.
- `sockdiag_send()` fills the diagnostic family and `udiag_show` mask, sends requests via `sendmsg()`, cycles families, and returns positive/zero/negative status for sent/stopped/error.
- `stress_sockdiag_parse()` validates response length, iterates `rtattr` attributes with `RTA_OK`/`RTA_NEXT`, and adds the attribute count to bogo operations.
- `sockdiag_recv()` reads netlink responses with `recvmsg()`, validates `nlmsghdr` entries, handles `NLMSG_DONE` and `NLMSG_ERROR`, and dispatches diagnostic payloads to the parser.
- `stress_sockdiag()` repeatedly opens `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, sends one query, receives the dump, closes the socket, and loops while the stressor continues.

## Control Flow

After the synchronization barrier, each loop opens a raw netlink sock_diag socket. If the protocol is unsupported, instance zero reports a skip and returns `EXIT_NOT_IMPLEMENTED`. Otherwise `sockdiag_send()` prepares a `SOCK_DIAG_BY_FAMILY` request with `NLM_F_REQUEST | NLM_F_DUMP`, chooses a family from a compiled list, tries `udiag_show` bits one at a time, and finally tries all bits. The first successful `sendmsg()` returns to the caller.

The receive side loops through netlink messages in a static aligned buffer. It rejects malformed messages, stops on `NLMSG_DONE`, treats `NLMSG_ERROR` or unexpected message types as errors, and otherwise counts response attributes. The entry point ignores receive errors but treats send failures as stressor failure. Each outer iteration closes the netlink fd.

## State and Persistence Behavior

The stressor keeps static request, address, iovec, message, family index, and receive buffer state inside helper functions. These are process-local and reused across loop iterations. It creates no files and no persistent kernel objects beyond transient netlink sockets.

## Dependencies and Integration Points

This file is Linux-only and requires `linux/netlink.h`, `linux/rtnetlink.h`, `linux/sock_diag.h`, and `linux/unix_diag.h`. It uses stress-ng state transitions, continue checks, bogo accounting, and logging. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`; unsupported builds export `stress_unimplemented`.

## Risks and Edge Cases

The request structure is Unix-diag-specific but the family field is varied across many address families; unsupported family/show combinations are expected to fail. Static mutable request state makes the helper simple but not reentrant. `sockdiag_recv()` treats unexpected netlink payloads as failures, which is appropriate for verification but can be sensitive to kernel ABI changes. The code handles `EINTR` during receive and send retry loops but does not deeply inspect netlink error payloads.

## Test Signals

On Linux kernels with `NETLINK_SOCK_DIAG`, a short run should open netlink sockets, send requests, parse attributes, and increment bogo counts. On kernels lacking support it should print a skip and return not implemented/no-resource rather than fail. Build testing should cover missing header paths to validate the unimplemented branch.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockdiag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockfd.c -->
# sources/test-tools/stress-ng/stress-sockfd.c

## Purpose

`stress-sockfd.c` implements `sockfd`, a Linux stressor that sends file descriptors over AF_UNIX sockets using `SCM_RIGHTS`. It exercises ancillary data construction/parsing, descriptor pressure, descriptor reuse between sender and receiver, Unix socket addressing, and cleanup of many fds.

## Important APIs, Types, and Functions

- `stress_socket_fd_send()` builds a `sendmsg()` call with one byte of data and a `SOL_SOCKET` / `SCM_RIGHTS` control message containing `fd_send`.
- `stress_socket_fd_recv()` receives one message, validates the marker byte, rejects truncated control data, and extracts the passed fd from `CMSG_DATA`.
- `stress_socket_client()` connects to the AF_UNIX server, receives up to `max_fd` descriptors, optionally sends descriptors back when `sockfd-reuse` is active and `select()` is available, tries to read pending bytes via `FIONREAD`, then closes the received descriptor array.
- `stress_socket_server()` binds/listens on the AF_UNIX address, accepts clients, repeatedly opens `/dev/zero`, sends the fd, closes the local copy, sends an invalid fd to exercise receiver handling, and increments bogo operations.
- `stress_sockfd()` computes descriptor limits, reserves a per-instance Unix socket port/name, allocates the fd array, forks client/server, and releases resources.

## Control Flow

The entry point installs `SIGCHLD`, reads `sockfd-port` and `sockfd-reuse`, reserves a per-instance port, determines the file descriptor limit, caps it for root and at one million descriptors, allocates an integer array, synchronizes, and forks. The child lowers OOM protection, enables failure injection, and runs the receiver. The parent runs the sender, then signals the child with `SIGALRM` and waits.

The server creates an AF_UNIX stream socket, enables `SO_REUSEADDR`, binds to a stress-ng-generated address, and listens. For each accepted connection it loops up to `max_fd`, optionally checks if the peer returned a reusable descriptor with `select()`, otherwise opens `/dev/zero`, sends that descriptor via `SCM_RIGHTS`, closes it locally, sends one bad fd, increments messages and bogo operations, and continues. The client connects with retry, receives descriptors into the allocated array, optionally returns them to the server, probes readable data with `FIONREAD`, closes all received fds, and removes the Unix socket path on cleanup.

## State and Persistence Behavior

Runtime state includes the allocated fd array, AF_UNIX socket path, opened `/dev/zero` descriptors, and stress-ng port reservation. Descriptor ownership is intentionally transferred between processes through kernel ancillary-data semantics. No files are persistently written; the Unix socket path is unlinked on both client/server cleanup paths when available.

## Dependencies and Integration Points

The implementation is Linux-only and depends on AF_UNIX, `sendmsg()`/`recvmsg()` control messages, `CMSG_*` macros, stress-ng network address helpers, out-of-memory adjustment, signal helpers, and fd cleanup helpers. Optional `select()` enables descriptor reuse. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`, with `sockfd-port` and `sockfd-reuse` options; non-Linux builds export unimplemented.

## Risks and Edge Cases

The stressor can open and pass a very large number of descriptors; root runs are deliberately given headroom to avoid exhausting the whole process. Ancillary data can fail with expected pressure errors such as `ETOOMANYREFS`, `ENOMEM`, `EPIPE`, and reset conditions. The server does not explicitly call `stress_net_release_ports()` at the end in this file, so correctness relies on process-local reservation cleanup elsewhere or the reservation being only a coordination guard. AF_UNIX path unlinking happens in helpers, but double unlink is harmless.

## Test Signals

Useful tests include default descriptor passing, `--sockfd-reuse`, low file-limit environments, root and non-root runs, and builds without `select()`. Expected behavior is bogo increments per successful descriptor send, no leaked fds after client cleanup, and graceful handling of pressure-related `sendmsg()` errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockmany.c -->
# sources/test-tools/stress-ng/stress-sockmany.c

## Purpose

`stress-sockmany.c` implements `sockmany`, a stressor that opens many simultaneous IPv4 TCP connections to a local server. It is aimed at file descriptor limits, ephemeral port exhaustion, TCP accept/connect paths, listen backlog behavior, and small-message send/receive throughput.

## Important APIs, Types, and Functions

- `stress_sock_fds_t` is a shared mmap structure that records the maximum number of client fds opened in one pass.
- `stress_sockmany_cleanup()` shuts down and closes an array of sockets.
- `stress_sockmany_client()` opens up to `SOCKET_MANY_FDS` client sockets, connects each to the server, receives a small buffer, updates the shared maximum, and then closes all opened sockets.
- `stress_sockmany_server()` binds/listens on the per-instance port, accepts clients, sends `sockmany-max-size` bytes, applies TCP timeout/sync/quickack options when available, and increments bogo operations.
- `stress_sockmany()` parses `sockmany-if`, `sockmany-max-size`, and `sockmany-port`, validates the interface, reserves the port, creates shared state, forks, and cleans up.

## Control Flow

The entry point installs child and `SIGPIPE` handlers, reads options with maximize/minimize handling for max payload size, validates an optional interface, reserves a per-instance IPv4 port, and mmaps a shared `stress_sock_fds_t`. After synchronization it forks. The child runs the client on the same CPU as the parent, while the parent runs the server and kills the child when done.

The client initializes its local fd array to `-1`, then tries to create and connect sockets until the global continue flag clears or resource limits are hit. Expected resource conditions such as `EMFILE`, `ENFILE`, `ENOBUFS`, `ENOMEM`, `EADDRNOTAVAIL`, and `ECONNREFUSED` end the current batch rather than failing the stressor. Each connected socket receives a buffer, and the batch is then closed. The server creates a listening socket with `SO_REUSEADDR`, optional TCP retry/timeout tuning, and bind retry on `EADDRINUSE`. It accepts one client at a time, validates socket name/buffer paths, optionally sets `TCP_QUICKACK`, sends the configured payload, closes the accepted fd, and increments the bogo count.

## State and Persistence Behavior

The only shared state is the anonymous shared mmap used to report `max_fd` from client to parent. It also uses stress-ng's port reservation table and transient TCP sockets. No persistent files or network configuration changes are made.

## Dependencies and Integration Points

The file uses stress-ng network interface/address/port helpers, mmap helpers, signal helpers, affinity helpers, and kill helpers. It depends on IPv4 TCP sockets, optional `TCP_SYNCNT`, `TCP_USER_TIMEOUT`, `TCP_QUICKACK`, and `SO_REUSEADDR`. The exported stressor is `CLASS_NETWORK | CLASS_OS`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

Opening up to 100,000 sockets is intentionally resource-heavy and may quickly hit fd, memory, socket buffer, or ephemeral port limits. Those limits are mostly treated as normal end-of-batch conditions. The client uses a static local fd array and a shared maximum index, so reported "sockets opened" is the highest index, not necessarily a count including zero. Interface validation falls back to loopback if the requested interface does not support AF_INET. The server uses a small listen backlog relative to the possible client burst, so connection refusal can be expected.

## Test Signals

Expected test signals include successful default loopback runs, controlled resource-limit exits without failure, correct max-socket debug reporting, and no unclosed fds after cleanup. Option tests should cover `--sockmany-max-size 1`, maximize/minimize, invalid interface fallback, and explicit port reservation conflicts.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockpair.c -->
# sources/test-tools/stress-ng/stress-sockpair.c

## Purpose

`stress-sockpair.c` implements `sockpair`, a Unix socketpair throughput and resource stressor. It creates as many AF_UNIX stream socket pairs as possible, forks a reader child, writes patterned buffers across all pairs, optionally verifies data, and includes a targeted out-of-band send sequence for a historical AF_UNIX leak fix.

## Important APIs, Types, and Functions

- `socket_pair_memset()` writes incrementing byte data and stores a checksum byte at the front of the buffer.
- `socket_pair_memchk()` validates the checksum for received data.
- `socket_pair_close()` closes one side of every socketpair in a two-dimensional fd array.
- `socket_pair_try_leak()` sends `MSG_OOB` both ways over a temporary socketpair to exercise a Linux AF_UNIX OOB leak fix.
- `stress_sockpair_oomable()` is the main implementation run under `stress_oomable_child()`. It creates socket pairs, forks reader/writer roles, handles low-memory avoidance, records metrics, and cleans up.
- `stress_sockpair()` sets up state, ignores `SIGPIPE`, and delegates to the oomable child wrapper.

## Control Flow

The implementation first parses `sockpair-max-size`, deliberately exercises invalid `socketpair()` domain/type/protocol calls, and then creates up to `MAX_SOCKET_PAIRS` AF_UNIX stream socket pairs. It records the creation rate as "socketpair calls sec". If no pairs can be created, it maps common errno values to skip/no-resource outcomes.

After successful creation, it forks. The child closes writer ends, sets OOM adjustment and parent-death alarm, then continuously reads from each reader fd. With `--verify`, it checks the checksum generated by the parent. It also calls `socket_pair_try_leak()` unless `--oom-avoid` detects low memory. The parent closes reader ends, writes patterned buffers to each writer fd while measuring write duration and bytes, optionally backs off under low memory, yields after writes, increments bogo operations, reports MB/sec, shuts down writer ends, kills the child, and closes all fds.

## State and Persistence Behavior

State is process-local plus inherited socketpair fd arrays. The fd array is static inside the oomable function and can hold 32,768 pairs. There is no file persistence. Metrics include socketpair creation rate and MB written per second. Low-memory backoff count is reported only in debug output.

## Dependencies and Integration Points

The stressor integrates with stress-ng OOM wrappers, signal handling, affinity, scheduler settings, OOM adjustment, and metrics. It depends on AF_UNIX `socketpair()`, `read()`, `write()`, `shutdown()`, optional `MSG_OOB`, and optional verification flags. It registers as `CLASS_NETWORK | CLASS_OS`, `VERIFY_OPTIONAL`, with a `sockpair-max-size` option.

## Risks and Edge Cases

This stressor can consume many file descriptors and socket buffers. It is designed to be OOM-killable and supports `--oom-avoid`, but large `sockpair-max-size` combined with many pairs can still create strong memory pressure. The checksum is intentionally simple and catches corruption but not all data-order issues. Parent write failures from `EPIPE`, `ECONNRESET`, and fd exhaustion are expected under pressure. The static fd array is large, so stack placement is avoided by using static storage.

## Test Signals

Test signals include creation-rate metrics, MB/sec metrics, optional verify success, graceful skip when socketpairs cannot be created, and low-memory backoff debug messages under constrained memory. Builds with `MSG_OOB` should exercise the leak-test path; builds without it should compile out cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sockpair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-softlockup.c -->
# sources/test-tools/stress-ng/stress-softlockup.c

## Purpose

`stress-softlockup.c` implements `softlockup`, a privileged scheduler stressor intended to create CPU starvation/soft-lockup-like conditions. It forks one child per online CPU, gives them realtime scheduler policies at maximum priority when possible, drops niceness, and runs busy loops bounded by CPU/RT time limits.

## Important APIs, Types, and Functions

- `stress_softlockup_supported()` requires `CAP_SYS_NICE`.
- `stress_policy_t` describes supported realtime policies and their maximum priorities.
- `stress_softlockup_loop()` performs a memory-barrier-heavy no-op loop.
- `stress_softlockup_loop_count()` calibrates a loop count that takes roughly 0.01 seconds.
- `stress_softlockup_rep_stosb()` optionally runs x86 `rep stosb` over a shared 1 MiB buffer to add memory pressure.
- `stress_rlimit_handler()` handles CPU-time signals by clearing the continue flag and long-jumping out.
- `drop_niceness()` attempts to reduce nice level as far as permissions allow.
- `stress_softlockup_child()` applies rlimits, signal handling, realtime policy cycling, busy loops, and bogo increments.
- `stress_softlockup()` allocates child PID synchronization state, forks per CPU, starts children together, makes the parent realtime, pauses, then kills/waits children.

## Control Flow

The entry point calibrates the loop count, optionally maps the x86 `rep stosb` buffer, allocates a shared PID synchronization array sized to online CPUs, initializes per-child start gates, validates available scheduling policies, and records maximum priorities. It forks one child per online CPU with retry support. Each child waits on its per-PID start gate, sets failure injection and CPU affinity, then enters `stress_softlockup_child()`.

The child sets `RLIMIT_CPU` and optional `RLIMIT_RTTIME` to the global timeout, installs a `SIGXCPU` long-jump handler, drops niceness, cycles through realtime policies, sets max priority, runs a randomized number of calibrated busy loops, optionally performs the x86 memory-fill path, increments bogo operations, and exits when timeout or continue flags stop it. The parent synchronizes the global start, releases all children, sets its own scheduler to the first policy, pauses, then kills/waits all children with `SIGALRM`.

## State and Persistence Behavior

The stressor creates process-local global state for optional x86 buffer and the signal jump environment. It maps temporary shared memory for child synchronization and optional shared memory for `rep stosb`, both unmapped on cleanup. It changes scheduler policy and niceness of the stressor processes but does not persist system configuration.

## Dependencies and Integration Points

This file depends on `sched_get_priority_max()`, `sched_setscheduler()`, realtime policies such as `SCHED_FIFO` and `SCHED_RR`, rlimits, stress-ng capability checks, child synchronization helpers, affinity helpers, kill/wait helpers, and optional x86 assembly. It registers as `CLASS_SCHEDULER`, `VERIFY_ALWAYS`, with a `.supported` callback. Unsupported scheduler builds export unimplemented.

## Risks and Edge Cases

This is intentionally disruptive and requires `CAP_SYS_NICE`. Realtime children can starve other work until rlimits or external signals stop them; the code adds CPU/RT time bounds and parent kill logic to limit damage. Some systems may not support the compiled realtime policies or may report low maximum priorities. The parent calls `pause()` after becoming realtime, so correct signal delivery and child termination paths are important. If fork fails partway through, already-started PID records are cleaned up through the finish path.

## Test Signals

Primary test signals are skip behavior without `CAP_SYS_NICE`, successful policy priority discovery, child start synchronization, and clean termination at timeout. On capable systems, bogo counts should increase and no child should survive after the stressor exits. Tests should also cover kernels lacking `SCHED_FIFO` or `SCHED_RR` support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-softlockup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sparsematrix.c -->
# sources/test-tools/stress-ng/stress-sparsematrix.c

## Purpose

`stress-sparsematrix.c` implements `sparsematrix`, a CPU/cache/memory/search stressor that compares multiple sparse-matrix storage methods under a deterministic insert, lookup, random lookup, and delete workload. Supported methods include chained hash, preallocated quick hash, dense mmap, optional Judy arrays, optional hash-of-Judy arrays, optional BSD circle queues, optional red-black trees, and optional splay trees.

## Important APIs, Types, and Functions

- `stress_sparsematrix_method_info_t` provides a common method interface: `create`, `destroy`, `put`, `del`, and `get`.
- `test_info_t` accumulates max object memory estimate, put/get durations and operation counts, and no-memory skip state per method.
- `value_map()` deterministically maps `(x, y)` to a nonzero expected value.
- Hash methods use `sparse_hash_table_t` / `sparse_hash_node_t`; quick hash uses `sparse_qhash_table_t` with preallocated nodes.
- Optional Judy methods use `Pvoid_t` arrays and Judy macros (`JLI`, `JLG`, `JLMU`, `JLFA`).
- Optional tree methods use BSD `RB_*` and `SPLAY_*` macros with global roots and object-memory counters.
- Optional list method uses BSD `CIRCLEQ` y-lists containing sorted x-lists.
- Dense mmap uses `sparse_mmap_t`, `stress_mmap_populate()`, `mincore`, and direct offset indexing.
- `stress_sparse_method_test()` is the shared workload runner and verifier for every method.
- `stress_sparsematrix()` parses options, clamps item counts to matrix capacity, runs one or all methods, records per-method metrics, and returns failure on verification mismatch.

## Control Flow

The stressor initializes per-method metric structures, reads the selected method, matrix size, and item count with maximize/minimize support, clamps item count to `size * size`, logs density from instance zero, and enters the synchronized run state. Each loop iteration runs either every method except the special `all` entry or the selected method.

For a method, `stress_sparse_method_test()` creates the backend, saves two random seeds, and uses those seeds to make the put and verification passes deterministic. The put pass generates random coordinates, computes `value_map()`, inserts only when `get()` returns zero, and records put operations and duration. The verification pass resets the seed and expects every coordinate to return the deterministic value. It then performs random gets and finally resets the seed again to delete inserted coordinates. Destroy returns an estimated object-memory footprint. On mismatch or put failure, the stressor reports failure.

After the loop, the stressor emits per-method get and put rates as harmonic mean metrics for methods that were not skipped for memory. It also logs geometric means in debug output.

## State and Persistence Behavior

All storage is transient heap, Judy, mmap, or global in-process tree/list roots. The dense mmap method maps anonymous private memory and uses `mincore()` during destroy to estimate resident pages. Red-black and splay methods use global roots and object-memory counters, making them non-reentrant but fine for one stressor process. No external files are written.

## Dependencies and Integration Points

The file integrates with stress-ng random number seeding, prime-number helper, memory-limit helper, mmap helper, metrics, option parsing, and continue flags. It conditionally depends on BSD queue/tree headers, libbsd red-black support, Judy headers/library, `mincore`, `math.h` `frexp()`/`pow()`, and platform word size for Judy support. The exported stressor is `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, `VERIFY_ALWAYS`, with max metrics sized to twice the number of methods.

## Risks and Edge Cases

Large sizes and item counts can request very large hash tables, Judy arrays, or dense mmaps. The dense mmap method checks free memory plus swap and size_t overflow, but memory pressure can still be high. Some delete methods zero values while tree methods remove nodes; the shared test only requires subsequent destruction and does not re-verify deletion semantics. The list insertion paths can leave a newly allocated y-node if x-node allocation fails, though destroy should clean reachable nodes if the handle survives. Global tree roots and static Judy pointer storage make these methods unsuitable for concurrent use inside one process without isolation.

## Test Signals

Strong signals include successful `--sparsematrix-method all` with verify, individual method runs, no-memory skips that do not fail the whole stressor, and metrics named "`<method> gets per sec`" and "`<method> puts per sec`". Build coverage should include configurations with and without Judy, libbsd RB trees, splay trees, and circle queues.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sparsematrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-spawn.c -->
# sources/test-tools/stress-ng/stress-spawn.c

## Purpose

`stress-spawn.c` implements `spawn`, a scheduler/OS stressor that repeatedly starts the current stress-ng executable using `posix_spawn()` and waits for it to exit. The spawned child is invoked with `--exec-exit`, so the workload measures process creation and image setup without running another full stress workload.

## Important APIs, Types, and Functions

- `stress_spawn_supported()` prevents running the stressor as root, avoiding accidental privileged spawning of another executable.
- `stress_spawn()` obtains `LD_LIBRARY_PATH` environment setup, resolves the current executable with `stress_proc_self_exe_get()`, builds `argv_new` as `{ path, "--exec-exit", NULL }`, repeatedly calls `posix_spawn()`, waits with `shim_waitpid()`, counts failures, and optionally fails verification if any spawn failed.
- `stress_spawn_info` registers the stressor with `CLASS_SCHEDULER | CLASS_OS` and `VERIFY_OPTIONAL`.

## Control Flow

Both the supported callback and the entry point reject effective UID zero. The entry point builds a minimal environment containing the current library-path variable returned by `stress_env_ld_library_path_get()`, resolves the running executable path, synchronizes start, and enters the run loop. Each iteration increments the attempted spawn count, calls `posix_spawn()`, logs and counts spawn-call failures, or waits for the child and increments bogo operations. Exited child statuses other than `EXIT_SUCCESS` are counted as spawn failures. On exit it frees the library-path string and, under `--verify`, reports and fails if any failures occurred.

## State and Persistence Behavior

The stressor creates only transient child processes. Static `argv_new` and `env_new` arrays are mutated with the resolved executable and optional environment string. It writes no files and leaves no persistent state.

## Dependencies and Integration Points

The file requires `spawn.h` and `posix_spawn()`. It uses stress-ng helpers for current executable discovery, environment construction, synchronization, waitpid, bogo accounting, option flags, and logging. Unsupported builds export `stress_unimplemented`.

## Risks and Edge Cases

The root guard is deliberate because the executable path comes from the running process and should not be repeatedly spawned with elevated privileges in this test. Failure to resolve `/proc/self/exe` or platform equivalent yields `EXIT_NOT_IMPLEMENTED`. `env_new[0]` can be NULL, which is acceptable for an empty environment array. Spawn failures are tolerated unless verification is enabled, making this suitable for resource-pressure runs.

## Test Signals

A non-root run should repeatedly spawn stress-ng with `--exec-exit`, increment bogo operations, and exit success when children exit cleanly. Root runs should skip or fail early. Verification runs should report a failure percentage when child exits or spawn calls fail.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-spawn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-spinmem.c -->
# sources/test-tools/stress-ng/stress-spinmem.c

## Purpose

`stress-spinmem.c` implements `spinmem`, a shared-memory synchronization stressor. A parent writer and child reader spin on one shared page using 8-, 16-, 32-, 64-, or optional 128-bit loads/stores, explicit memory barriers, cache-line flushes, optional scheduling yields, optional CPU-affinity changes, and optional NUMA page migration.

## Important APIs, Types, and Functions

- `SPINMEM_READER` and `SPINMEM_WRITER` macros generate typed reader/writer functions for each supported integer width.
- `SPINMEM_MB()` combines compiler/CPU barriers, `shim_mfence()`, and optional ARM DMB SY.
- `SPINMEM_FLUSH()` flushes cache data around the shared location.
- `spinmem_funcs_t` maps method names to reader/writer function pointers.
- `stress_spinmem_change_affinity()` randomly moves a process among allowed CPUs when `--spinmem-affinity` is enabled.
- `stress_spinmem_numa()` periodically randomizes NUMA placement when `--spinmem-numa` is enabled and Linux mempolicy support exists.
- `stress_spinmem_handler()` long-jumps out on `SIGALRM` when `siglongjmp` support exists.
- `stress_spinmem()` parses options, maps the shared page, installs signal handling, forks the reader child, runs writer loops in the parent, records nanoseconds per spin write/read, kills the child, and frees affinity/NUMA state.

## Control Flow

The stressor reads boolean options for affinity, NUMA, and yield, plus a method index defaulting to 32-bit. It disables unsupported affinity or NUMA modes with informational messages. It maps one shared anonymous page, installs a `SIGALRM` long-jump handler if available, selects the reader and writer functions, synchronizes, and forks.

The child repeatedly runs the selected reader. The reader waits until slot 0 changes from the last value, writes the observed value into slot `SPINMEM_OFFSET`, flushes/barriers, and optionally yields. With affinity enabled, the child runs blocks of 1000 reads and randomly changes CPU, also periodically invoking NUMA page randomization. The parent repeatedly runs the selected writer, which increments a value, publishes it to slot 0, waits for the child to echo it in slot `SPINMEM_OFFSET`, and optionally yields. The parent measures elapsed writer duration, counts loop iterations, increments bogo operations, handles affinity/NUMA variants, restores signal handling, kills the child, reports nanoseconds per operation, unmaps memory, and releases helper state.

## State and Persistence Behavior

The only shared state is one anonymous shared mmap page. Optional NUMA masks and affinity CPU arrays are allocated and freed within the stressor. Static signal jump state is process-local. No files or persistent system settings are modified, though `sched_setaffinity()` and NUMA page migration affect the running processes and page placement.

## Dependencies and Integration Points

The file integrates with stress-ng affinity, cache flush, mmap, NUMA, signal, kill/wait, and metrics helpers. It conditionally depends on Linux mempolicy, `sched_setaffinity()`, architecture memory barriers, and `siglongjmp`. The exported stressor is `CLASS_CPU | CLASS_MEMORY | CLASS_CPU_CACHE`, `VERIFY_NONE`, with method, affinity, NUMA, and yield options.

## Risks and Edge Cases

The generated spin loops have a fixed `SPINMEM_SPINS` escape count, so they avoid infinite waits but can silently move on if the peer is delayed. There is no data-correctness verification beyond the handshake. Method selection depends on the option parser limiting the index to `spinmem_funcs`; invalid external mutation could index out of bounds. NUMA page movement and affinity changes can make timing metrics noisy by design. The signal long-jump path must avoid jumping after cleanup, so `do_jmp` is cleared before restoring the handler.

## Test Signals

Expected signals include a populated "nanoseconds per spin write/read" metric, successful runs for every compiled method, fallback messages for unsupported affinity/NUMA modes, and child termination on cleanup. Test matrices should include `--spinmem-yield`, `--spinmem-affinity` with a restricted taskset, and `--spinmem-numa` on multi-node systems.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-spinmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-splice.c -->
# sources/test-tools/stress-ng/stress-splice.c

## Purpose

`stress-splice.c` implements `splice`, a Linux pipe-I/O stressor that moves data through pipes and `/dev/null` using `splice()`. It also exercises pipe-size tuning, splice flags, zero-length and invalid-flag calls, invalid offset combinations, and a looped pipe-to-pipe splice path.

## Important APIs, Types, and Functions

- `stress_splice_flag()` randomly combines available `SPLICE_F_MOVE` and `SPLICE_F_MORE` flags.
- `stress_splice_pipe_size()` uses `F_SETPIPE_SZ` to set pipe capacity to a random multiple of the fixed buffer length.
- `stress_splice_write()` is a fallback writer used when the kernel does not support splicing from `/dev/zero` to a pipe.
- `stress_splice_non_block_write_4K()` primes a pipe for looped splice tests using a temporary nonblocking write.
- `stress_splice_looped_pipe()` splices from one pipe to another and back, disabling the loop path after the first failure.
- `stress_splice()` allocates a fallback buffer, opens `/dev/zero` and `/dev/null`, creates four pipes, configures pipe sizes, runs the splice pipeline, records throughput metrics, and closes/unmaps everything.

## Control Flow

The entry point resolves `splice-bytes`, scaling the configured total across worker instances and enforcing a minimum. It allocates an anonymous fallback buffer, opens `/dev/zero`, creates four pipes, opens `/dev/null`, optionally resizes all pipe ends, primes the looped-pipe path, and enters the synchronized run state.

Each iteration tries to splice `splice_bytes` from `/dev/zero` into pipe 1. If the kernel returns `EINVAL`, the stressor logs once and switches permanently to writing the fallback buffer into the pipe. It then splices pipe 1 to pipe 2 and pipe 2 to `/dev/null`, sampling only every thousandth iteration for lower overhead metrics. It deliberately invokes splice calls expected to fail with `ESPIPE` or invalid flags, performs a zero-size no-op splice, attempts self-splicing, runs the looped pipe path twice, and increments bogo operations. Cleanup follows labeled close paths for every fd and reports "MB per sec splice rate".

## State and Persistence Behavior

Runtime state consists of transient fds for `/dev/zero`, `/dev/null`, and pipes, plus one anonymous fallback buffer. Pipe capacity changes apply only to these fds. No persistent files are created.

## Dependencies and Integration Points

The file depends on `splice()` support and stress-ng mmap, madvise, memory sizing, metrics, and option parsing helpers. It uses `fcntl(F_SETPIPE_SZ)` when available and registers as `CLASS_PIPE_IO | CLASS_OS`. Without `splice()` it exports `stress_unimplemented`.

## Risks and Edge Cases

Linux kernel behavior changed so splicing from `/dev/zero` may be invalid; the fallback write path explicitly handles that. Pipe-size changes may fail because of limits and are ignored. Metrics sample a subset of iterations, so rates are approximate. The multiple cleanup labels set the process state to deinit repeatedly, which is harmless but noisy structurally. Some intentionally invalid splice calls may return different errors across kernels and are ignored.

## Test Signals

Expected signals include successful default runs, fallback log on kernels that reject `/dev/zero` splice, MB/sec splice metric, and no fd leaks. Option coverage should include minimum and large `--splice-bytes` values and builds without `splice()`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-stack.c -->
# sources/test-tools/stress-ng/stress-stack.c

## Purpose

`stress-stack.c` implements `stack`, a VM/memory stressor that recursively consumes stack until a fault occurs, catches the fault on an alternate signal stack, and repeats. It can fill stack pages, mlock stack regions, request pageout, or unmap stack pages to exercise stack growth, fault handling, and VM behavior.

## Important APIs, Types, and Functions

- `stress_stack_check_t` links stack frames and stores a self pointer used for stack corruption sanity checks.
- `stress_segvhandler()` handles `SIGSEGV` and `SIGBUS` by long-jumping to the recovery point.
- `stress_stack_alloc()` recursively allocates a 256 KiB local array, touches pages, optionally fills, mlocks, pageouts, or unmaps stack pages, validates recent frame links, increments bogo operations, and recurses until stop or fault.
- `stress_stack_child()` parses stack options, allocates and installs an alternate signal stack, sets parent-death alarm and OOM adjustment, installs fault handlers, wraps each recursive run in `sigsetjmp()`, and returns success/failure.
- `stress_stack()` runs the implementation under `stress_oomable_child()`.

## Control Flow

The main stressor synchronizes and then launches an oomable child. The child resolves options, defaulting aggressive mode to fill/mlock/pageout/unmap where supported, maps an alternate signal stack with `stress_mmap_populate()`, touches it with `stress_mincore_touch_pages()`, installs it via `stress_stack_sigalt()`, and marks itself OOM-killable.

The child loop installs `SIGSEGV` and `SIGBUS` handlers using the alternate stack and sets a recovery point with `sigsetjmp()`. On the initial path it calls `stress_stack_alloc()`, which creates a large stack array, touches or fills stack memory, optionally mlocks newly grown regions, optionally calls `madvise(MADV_PAGEOUT)`, optionally force-unmaps a page in the stack, validates a linked list of up to 128 previous stack frames, increments bogo, and recurses. When stack overflow or forced unmap triggers a signal, the handler long-jumps back, and the loop increments bogo again before repeating.

## State and Persistence Behavior

The stressor uses process-local signal jump state and heap/anonymous mappings for the alternate signal stack. It may mlock portions of its own stack and madvise or unmap stack pages, but all state is process-local and disappears on exit. No files are written.

## Dependencies and Integration Points

The implementation requires `siglongjmp`; otherwise it exports unimplemented. It integrates with stress-ng OOM wrappers, alternate signal stack helpers, memory-low checks, cache flush helpers, mincore helpers, forced munmap, and option parsing. It registers as `CLASS_VM | CLASS_MEMORY`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

This stressor deliberately faults and manipulates its own stack. Correct alternate signal stack setup is essential because a normal signal frame may not fit on an overflowed stack. `--stack-unmap` can create `SIGBUS`/`SIGSEGV` before natural overflow, which is expected. Mlocking stack regions can fail or create memory pressure, so the code disables mlock after failure. The recursive function passes `last_size` by value, so mlock growth tracking is local to each recursion path rather than global.

## Test Signals

Expected signals are repeated bogo increments, clean recovery from stack faults, and failure if the stack-frame self-check detects corruption. Option tests should cover `--stack-fill`, `--stack-mlock`, `--stack-pageout` on systems with and without `MADV_PAGEOUT`, and `--stack-unmap`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-stackmmap.c -->
# sources/test-tools/stress-ng/stress-stackmmap.c

## Purpose

`stress-stackmmap.c` implements `stackmmap`, a VM/memory stressor that runs code on a file-backed mmap region used as a stack through `ucontext`/`swapcontext`. It recursively pushes data, periodically `msync()`s pages, uses guard pages, and validates stack-frame integrity until the mapped stack is exhausted.

## Important APIs, Types, and Functions

- `stress_stack_check_t` stores a previous-frame link, self pointer, and waste data for sanity checking.
- Global `ucontext_t c_main, c_test`, `stack_mmap`, `page_mask`, `page_size`, and `check_status` coordinate the alternate context and stack.
- `stress_stackmmap_push_msync()` recursively writes stack data, msyncs when crossing page boundaries, validates up to 256 linked stack frames, and recurses while the continue flag is set.
- `stress_stackmmap_push_start()` starts recursion for `makecontext()`.
- `stress_stackmmap()` creates a temporary file, maps it as the stack, maps a separate signal stack, sets guard pages with `mprotect()`, prepares the ucontext, forks children to run the mapped stack, waits for them, and cleans up.

## Control Flow

The stressor creates a temporary directory/file, opens the file with `O_SYNC`, unlinks it, truncates it to 256 KiB, maps an anonymous signal stack, and maps the file as shared writable stack memory. It applies `MADV_RANDOM`, zeroes the stack mapping, and marks the first and last pages `PROT_NONE` as guards. It initializes `c_test` with a stack region excluding guard pages and links it back to `c_main`.

After synchronization, the parent loop forks a child for each bogo iteration. The child installs a `SIGSEGV` handler on an alternate signal stack, sets OOM adjustment and parent-death alarm, initializes `check_status`, creates a context that runs `stress_stackmmap_push_start()`, and swaps from the main context to the mmap-backed stack. Recursion writes random waste values, emits addresses through stress-ng put helpers, msyncs the current page when page boundaries change, validates frame links and data complements, and keeps recursing until stop or guard-page fault. The child exits with `check_status`; the parent waits and treats nonzero child exit as failure.

## State and Persistence Behavior

The mapped stack is backed by an unlinked temporary file, so it has no lasting pathname and is removed with the temporary directory cleanup. The signal stack is anonymous. Global context and stack variables are process-local. The stressor calls `msync()` on the file-backed mapping, but the file is unlinked and removed after use.

## Dependencies and Integration Points

The file requires `ucontext.h` and `swapcontext()`; otherwise it exports unimplemented. It integrates with stress-ng temporary-file helpers, mmap helpers, signal alternate stack helpers, kill/wait helpers, OOM adjustment, scheduler settings, and continue/bogo accounting. It registers as `CLASS_VM | CLASS_MEMORY`, `VERIFY_ALWAYS`.

## Risks and Edge Cases

`ucontext` APIs are obsolete or absent on some platforms, so the compile guard is important. Running on a deliberately small file-backed stack depends on correct guard pages and alternate signal stack setup. The static `laddr` in `stress_stackmmap_push_msync()` persists within a process and avoids repeated msyncs for the same page; each forked child starts with inherited value but only one context uses it. Temporary file creation, mmap, and mprotect failures are handled through skip/failure paths.

## Test Signals

Expected signals include successful child exits, bogo increments per child run, and no sanity mismatch logs. Filesystem tests should verify temporary directories are removed and no stack file remains. Build tests should cover absence of `swapcontext()` and runtime tests should cover `ENXIO` mmap skip paths where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-stackmmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-statmount.c -->
# sources/test-tools/stress-ng/stress-statmount.c

## Purpose

`stress-statmount.c` implements `statmount`, a Linux filesystem/OS stressor for the newer `statmount` and `listmount` syscalls. It finds the unique mount ID for `/`, repeatedly stats that root mount, lists mount IDs under the root mount tree, stats each listed mount with mount and superblock masks, and reports call rate.

## Important APIs, Types, and Functions

- `shim_statmount()` wraps `syscall(__NR_statmount)` using `struct mnt_id_req`.
- `shim_listmount()` wraps `syscall(__NR_listmount)` using the same request structure.
- `stress_statmount_statroot()` calls `statmount` on the root mount ID, measures duration, verifies returned structure size and mount ID, and counts one call.
- `stress_statmount_listroot()` calls `listmount(LSMT_ROOT, ...)`, tracks the maximum returned mount count, and stats every returned mount with `STATMOUNT_MNT_BASIC` and `STATMOUNT_SB_BASIC`.
- `stress_statmount()` probes syscall availability, uses `shim_statx()` with `STATX_MNT_ID_UNIQUE` to get `/`'s mount ID, runs the loop, prints max mount points, and emits "statmount calls per sec".

## Control Flow

At startup, the stressor calls `shim_statmount(0, 0, NULL, 0, 0)` as an availability probe and skips if `ENOSYS`. It then calls `shim_statx(AT_FDCWD, "/", 0, STATX_MNT_ID_UNIQUE, &sx)` to retrieve the unique mount ID for root. After synchronization, each loop verifies the root mount via `stress_statmount_statroot()`, lists root mount descendants into a fixed 1024-entry array, stats each listed mount with both mount and superblock masks when successful, increments bogo operations, and continues until stopped. At the end instance zero reports the maximum mount count and metrics are recorded from accumulated duration/count.

## State and Persistence Behavior

The stressor only reads mount metadata through syscalls. It stores local timing counters and maximum mount count. No files are created, no mount table changes are made, and no state persists after exit.

## Dependencies and Integration Points

The file is guarded on Linux syscall numbers and mount/statx constants: `__NR_statmount`, `__NR_listmount`, `__NR_statx`, `MNT_ID_REQ_SIZE_VER0`, `STATMOUNT_*`, `STATX_MNT_ID_UNIQUE`, and `LSMT_ROOT`. It integrates with stress-ng `shim_statx`, state transitions, metrics, and logging. Unsupported builds export `stress_unimplemented`.

## Risks and Edge Cases

The syscall ABI is relatively new, so headers may expose constants on systems whose running kernel returns `ENOSYS`; the runtime probe handles that. `listmount()` can return more than 1024 entries, but this stressor requests a bounded list and tracks only the returned count. Individual `statmount()` calls for listed IDs can fail due to races with mount changes and are ignored in `stress_statmount_listroot()`, while root stat failures are fatal. The skip log for failed `statx` is missing a trailing newline in the source.

## Test Signals

Expected signals include skip behavior on older kernels, successful root mount ID verification on supported kernels, instance-zero mount count logging, and "statmount calls per sec" metrics. Tests should include mount namespace environments with small and large mount tables and concurrent mount churn to exercise ignored per-mount races.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-statmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-str.c -->
# sources/test-tools/stress-ng/stress-str.c

## Purpose

`stress-str.c` implements `str`, a CPU/cache/memory stressor for libc string functions. It generates deterministic-looking random strings from disjoint alphabets and repeatedly calls selected string APIs, optionally verifying expected results and collecting per-method call-rate metrics.

## Important APIs, Types, and Functions

- `stress_str_args_t` carries the selected libc function pointer, method name, source strings, lengths, destination buffer, and failure flag.
- `stress_str_func` and `stress_str_method_info_t` define the common method interface and method table.
- `stress_rndstr_case()` fills a buffer with random uppercase-like or lowercase-like characters and terminates it, avoiding `+` so search-negative checks are stable.
- `strchk()` and `STRCHK` report verification failures when `--verify` is enabled.
- Method functions cover `strcasecmp`, `strncasecmp`, `index`, `rindex`, `strlcpy` or `strcpy`, `strlcat` or `strcat`, `strncat`, `strchr`, `strrchr`, `strcmp`, `strncmp`, `strcoll`, `strlen`, and `strxfrm`, depending on build features.
- `stress_str_all()` rotates through all methods except the special `all` entry and records per-method metrics.
- `stress_str()` parses the method, initializes buffers, alternates generated strings, calls the selected method in a loop, swaps string buffers, records metrics, and returns failure if verification detected any mismatch.

## Control Flow

The stressor selects a method from `str-method`, initializes `str1`, `str2`, and `strdst` stack buffers, generates the first string, zeros the metrics array, synchronizes, and enters the run loop. Each iteration generates `str2` with the opposite alphabet case, times one call to the selected method function, adds the method's reported call count to metrics, then swaps `str1`/`str2` and their lengths so subsequent iterations cover both buffer sizes.

Each method runs a tight loop over offsets or string lengths while the global continue flag remains set. Verification checks include equality on identical strings, inequality across disjoint alphabets and shifted pointers, negative search for `+`, positive search for known first characters, expected lengths, expected destination pointer returns, and expected `strl*` lengths where available. At shutdown the stressor emits one metric per method with nonzero duration, named "`<method> calls per sec`".

## State and Persistence Behavior

All strings and destination buffers are stack-local to the worker. The metrics array is static at file scope and process-local. No heap allocation, files, locale changes, or persistent state are created by this stressor. Locale-dependent functions such as `strcoll()` and `strxfrm()` use the process's current locale.

## Dependencies and Integration Points

The file depends on libc string APIs and stress-ng option parsing, metrics, random generator, continue flags, state transitions, and verification flags. Some methods are conditional on `strings.h`, BSD `strlcpy`/`strlcat`, static build mode, `index`, and `rindex`. It registers as `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY | CLASS_HOT`, `VERIFY_OPTIONAL`, with `max_metrics_items` equal to the method table size.

## Risks and Edge Cases

The method table intentionally swaps between BSD `strl*` and standard `str*` implementations depending on availability, so metric names and semantics differ by build. Verification assumptions rely on the uppercase and lowercase alphabets having no overlapping characters and excluding `+`. `strcoll()` and `strxfrm()` can be locale-sensitive; the disjoint alphabets make inequality likely but locale behavior should be considered when changing alphabets. The `stress_bogo_add()` calls add fixed small counts rather than the full local operation count; metrics carry the detailed call counts.

## Test Signals

Expected test signals include successful `--str-method all`, individual method selection, per-method call-rate metrics, and verification failure reporting when expectations are broken. Build tests should cover systems with BSD `strlcpy`/`strlcat`, systems without `strings.h` aliases, and static builds where BSD `strl*` methods are excluded.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-str.c -->

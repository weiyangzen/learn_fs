# subset-b-009368 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-enosys.c -->
# sources/test-tools/stress-ng/stress-enosys.c

Purpose: implements the `enosys` stressor, which searches syscall-number space for unimplemented system calls and verifies they return `ENOSYS` while avoiding known live or dangerous syscalls. On x86-64 Linux it can also exercise the raw `syscall` instruction path in addition to libc `syscall()`.

Important APIs/types/functions: `stress_hash_syscall_t` stores syscall numbers already known to be real or unsafe; `stress_enosys_rpc_t` is the pipe RPC payload exchanged between parent and child. `syscall_ignore[]` hard-skips clone/fork/reboot/vhangup-like calls, while the very large `skip_syscalls[]` table is a compile-time catalogue of known syscall numbers to avoid. `stress_enosys_syscall()` performs the actual call with seven `-1` arguments, optional `x86_64_syscall6()`, signal recovery, and child-escape detection. `stress_enosys_parent()`, `stress_enosys_child()`, and `stress_enosys_push_syscall()` implement the harness.

Control flow: `stress_enosys()` installs SIGPIPE handling, seeds the hash table with known syscall numbers, creates two pipes, forks a constrained child, and loops until the global stop condition. The parent chooses sequential, high, random, masked, and bit-pattern syscall numbers, writes each request, reads back errno/count, caches any non-`ENOSYS` result, increments bogo operations, and later kills the child. The child drops capabilities, makes shared mappings read-only, sets CPU/process limits and signal handlers, arms a short interval timer around each syscall, then returns the observed errno.

State and persistence behavior: no durable state is stored. Runtime state is a process-local hash table of skipped numbers, pipe messages, static syscall sequence counters, signal jump state, and aggregate syscall metrics. The child is disposable by design because unexpected syscalls may fork, fault, block, or mutate per-process state.

Dependencies and integration points: requires `sys/syscall.h` and `syscall()` support. It integrates with stress-ng capability dropping, OOM/fork retry, signal, CPU feature, read-only shared memory, scheduler, timing, metrics, and process-state helpers. The exported `stress_enosys_info` registers `CLASS_OS`.

Risks: calling arbitrary syscall numbers is inherently hazardous. The file mitigates this with skip tables, child isolation, capability dropping, resource limits, timers, signal longjmp, and explicit exit when a syscall unexpectedly creates a child, but new architectures or kernel syscall additions can make the skip tables stale. The x86 raw syscall path is architecture-sensitive and disabled outside guarded builds.

Test signals: build with and without syscall support, run short `--enosys` timeouts as non-root and root, verify nonzero `syscalls per second`, no leaked child processes, no unexpected real syscall side effects, and stable behavior on x86-64 with and without `syscall` CPU support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-enosys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-env.c -->
# sources/test-tools/stress-ng/stress-env.c

Purpose: implements the `env` stressor, repeatedly creating, verifying, and removing environment variables with randomized names and randomized value lengths up to the platform argument/environment limit.

Important APIs/types/functions: `stress_env_size()` chooses a random value length, `stress_env_max()` chooses how many variables to create before a reap cycle, and `stress_env_child()` owns allocation, random value generation, set/get/unset loops, optional verification, and cleanup. `stress_env()` runs the child through `stress_oomable_child()`.

Control flow: the child derives `arg_max` from `_SC_ARG_MAX`, `ARG_MAX`, or `NCARGS`, caps it at 16 MiB, mmaps a value buffer, fills it with random text, then sync-starts. It repeatedly builds names `STRESS_ENV_<hex>`, temporarily null-terminates the buffer at a random offset, calls `setenv()`, and increments bogo operations. When the selected limit is reached or `setenv()` fails, it reseeds to replay the same lengths, optionally compares `getenv()` values, calls `unsetenv()`, and begins a new cycle.

State and persistence behavior: state lives in the process environment and an anonymous mmap buffer. Environment mutations are local to the worker child and are removed during each reap pass; no filesystem state is created. Low-memory checks deliberately terminate the child cleanly so the OOM wrapper can manage pressure.

Dependencies and integration points: uses stress-ng random, memory, OOM-child, killpid, sync, process-state, and verification flag helpers. The stressor is registered as `CLASS_OS | CLASS_VM` with optional verification.

Risks: very large environment values can exhaust memory or hit platform-specific `ARG_MAX` behavior. Verification depends on replaying the RNG seed sequence exactly across set and unset passes. Early stop can leave variables in the exiting child, but they disappear with the process.

Test signals: run with `--env 1 --verify`, minimized/maximized modes, low memory pressure, and varied libc/kernel argument limits; check for skip messages on mmap failure and for missing/incorrect variable failures only under real corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-epoll.c -->
# sources/test-tools/stress-ng/stress-epoll.c

Purpose: implements `epoll`, a network/OS stressor that drives many short socket connections through epoll server processes, exercising `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, and optionally `epoll_pwait2`.

Important APIs/types/functions: `stress_epoll_pwait()` selects `epoll_pwait2` when available and falls back to `epoll_pwait`. `epoll_spawn()` starts synchronized server children. `epoll_set_fd_nonblock()`, `epoll_ctl_add/mod/del()`, `epoll_notification()`, `epoll_recv_data()`, `test_eloop()`, and `test_epoll_exclusive()` cover normal and invalid epoll operations. `epoll_client()`, `epoll_server()`, and `stress_epoll()` coordinate traffic.

Control flow: `stress_epoll()` parses domain/port/socket limits, reserves ports, forks one AF_UNIX server or up to four INET servers, sync-starts them, and runs a client loop. The client cycles ports, creates sockets, arms a realtime timer to bound blocking connects, sends a random buffer, and closes. Each server binds/listens, creates epoll fds, registers the listen socket, accepts nonblocking clients, adds fds to epoll, reads ready data, handles HUP/ERR, and probes invalid arguments, bad fds, circular epoll membership, unmapped event buffers, and exclusive-event restrictions.

State and persistence behavior: server state is fd tables, port reservations, optional AF_UNIX socket paths, epoll event arrays, and timer state. It persists no durable data. Cleanup kills servers, releases ports, unlinks AF_UNIX paths, closes fds, and unmaps synchronized PID storage.

Dependencies and integration points: requires epoll headers/functions, librt timer APIs, and glibc 2.3.2 support. It integrates with stress-ng network address/port helpers, synchronized child start, process-state, fork retry, scheduler, signal, bad-fd, and mapped guard-page helpers.

Risks: connection-table saturation, `TIME_WAIT`, fd exhaustion, unavailable ports, and domain-specific socket cleanup can affect behavior. The intentional EFAULT/EINVAL/ELOOP probes are kernel-version-sensitive; SIGSEGV recovery guards invalid event-buffer tests. AF_INET/AF_INET6 runs can be noisier than AF_UNIX because they consume real local port ranges.

Test signals: run default AF_UNIX and explicit AF_INET/AF_INET6 with small and large `--epoll-sockets`, confirm server children exit, ports are released, no AF_UNIX socket paths remain, and verification failures only appear for unexpected successful invalid epoll calls.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eth-sniff.c -->
# sources/test-tools/stress-ng/stress-eth-sniff.c

Purpose: implements `eth-sniff`, a Linux raw-packet sniffing stressor that receives Ethernet frames and records traffic rates by common IPv4 and IPv6 protocol numbers.

Important APIs/types/functions: `stress_eth_sniff_supported()` enforces `CAP_NET_RAW`. `common_proto_t` and `common_proto[]` map protocol numbers to metric labels. `stress_eth_sniff_metrics()` emits per-protocol KB/sec metrics. `stress_eth_sniff()` owns raw socket creation, packet receive, protocol classification, and cleanup.

Control flow: the stressor allocates a 65534-byte packet buffer, sync-starts, creates `socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))`, then loops on `recvfrom()`. It ignores short frames, reads the IP version from byte 14, validates IPv4 header length, accumulates payload bytes by protocol byte for IPv4 and IPv6, and increments bogo operations per classified packet. At stop it closes the socket, emits metrics for nonzero common protocols, and unmaps the buffer.

State and persistence behavior: state is local metric arrays and an anonymous packet buffer. It does not transmit packets or persist files; it passively observes packets visible to the host namespace and permissions.

Dependencies and integration points: Linux-only path requiring ethernet/IP headers, `AF_PACKET`, `SOCK_RAW`, `ETH_P_ALL`, mmap helpers, capability helpers, and stress-ng metrics/state APIs. Unsupported builds register an unimplemented stressor with the same capability check.

Risks: requires elevated raw socket rights and may expose traffic metadata in metrics. Packet parsing assumes Ethernet II layout without VLAN offset handling, so some frames are ignored or misclassified. Idle interfaces can produce few or no operations.

Test signals: run with and without `CAP_NET_RAW`, on active and quiet interfaces, confirm skip behavior on missing privileges, nonzero bogo count when traffic exists, and protocol metrics for TCP/UDP/ICMP where traffic is present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eth-sniff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eventfd.c -->
# sources/test-tools/stress-ng/stress-eventfd.c

Purpose: implements `eventfd`, stressing Linux eventfd counters with bidirectional parent/child read-write traffic, optional nonblocking mode, fdinfo reads, and invalid read/write coverage.

Important APIs/types/functions: option `eventfd-nonblock` controls `EFD_NONBLOCK`. `stress_eventfd()` creates two eventfds, forks a child, coordinates ping-pong writes and reads, and validates full `uint64_t` transfers. It also tests invalid `eventfd(0, ~0)` and small-buffer/overflow writes.

Control flow: after creating `fd1` and `fd2` with `EFD_CLOEXEC`, `EFD_SEMAPHORE`, and optional `EFD_NONBLOCK`, the parent sync-starts and forks. The child is pinned near the parent CPU, applies stress-ng child settings, repeatedly reads from `fd1`, periodically attempts invalid small or all-ones writes, then writes `1` to `fd2`. The parent reads eventfd proc fdinfo, writes `1` to `fd1`, reads from `fd2`, and increments bogo operations. Both sides retry `EAGAIN` and `EINTR`.

State and persistence behavior: state is entirely kernel eventfd counters and process-local loop variables. No files are created except transient `/proc/self/fdinfo` reads. Cleanup kills the child and closes both fds.

Dependencies and integration points: gated by `sys/eventfd.h`, `eventfd()`, and glibc 2.8. Uses stress-ng affinity, killpid, fdinfo, scheduler, sync, process-state, and filesystem-usage accounting helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: nonblocking mode can spin on `EAGAIN`; semaphore mode changes read decrement semantics but still works for single-token ping-pong. Short writes/reads are intentionally invalid and must not be treated as failures unless valid 8-byte operations are short. Fork failure handling retries through stress-ng helpers.

Test signals: run blocking and `--eventfd-nonblock` modes with `--verify`, inspect for short read/write failures, confirm child cleanup, and check eventfd fdinfo paths are exercised without requiring persistent files.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-exec.c -->
# sources/test-tools/stress-ng/stress-exec.c

Purpose: implements `exec`, stressing process creation plus `execve`, `execveat`, and `fexecve` paths against the current stress-ng executable, including optional pthread-originated execs and intentionally invalid executable payloads.

Important APIs/types/functions: `stress_exec_context_t` carries executable paths, large argv/env string, argv/env arrays, O_PATH fd, method selectors, and pthread control. `stress_pid_hash_t` and the hash/free-list helpers track live children and clone stacks. `stress_call_exec_method()`, `stress_do_exec()`, `stress_exec_child()`, `stress_exec_wait()`, and `stress_exec()` implement execution, error classification, reaping, and metrics.

Control flow: `stress_exec()` refuses to run as root, resolves `/proc/self/exe`, allocates PID hash/cache storage and optional huge argument buffer, creates a temp directory for garbage executables, opens the executable with `O_PATH` when needed, and sync-starts. Each iteration spawns up to `exec-max` children using fork, vfork, clone, posix_spawn, or rfork as available. Children redirect stdio, drop capabilities, choose an exec method, sometimes build a garbage executable, sometimes pass huge argv/env data, and either successfully exec `--exec-exit` or return an expected error. The parent continuously reaps children and records failures for optional verification.

State and persistence behavior: runtime state is PID hash tables, clone stacks, child contexts, temp garbage executable paths, optional large mmap strings, and `LD_LIBRARY_PATH` copy. Temporary files are unlinked on cleanup; successful execs replace child process images and leave no durable state.

Dependencies and integration points: uses stress-ng capability, temp-dir, process self-exe, environment, mmap, pthread, scheduler, fork/clone/vfork/spawn/rfork feature gates, and process-state helpers. It registers options for exec method, fork method, max workers, and pthread suppression.

Risks: high `exec-max` can exhaust PIDs, fds, memory, or process limits. `vfork` is intentionally restricted to simple exec paths. Error classification must distinguish expected resource/argument/garbage-exec failures from real regressions. Running as root is blocked because execing arbitrary paths as root would be unsafe.

Test signals: run as non-root with each available `--exec-method` and `--exec-fork-method`, small `--exec-max`, `--exec-no-pthread`, and `--verify`; check no live children remain, temp garbage files are removed, and expected `E2BIG`/`ENOEXEC` paths do not count as verification failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-exit-group.c -->
# sources/test-tools/stress-ng/stress-exit-group.c

Purpose: implements `exit-group`, verifying that the Linux `exit_group` syscall terminates all threads in a process by repeatedly forking a child that starts multiple pthreads and exits the group from thread context.

Important APIs/types/functions: `stress_exit_group_info_t` stores pthread handles and creation results. Static state includes `mutex`, `keep_running_flag`, shared `exit_group_failed`, `pthread_count`, and `pthreads[]`. `stress_exit_group_func()` calls `shim_exit_group(0)` from a pthread, `stress_exit_group_child()` starts and coordinates threads, and `stress_exit_group()` owns fork/reap and failure reporting.

Control flow: the parent maps a shared failure counter, sync-starts, and loops creating a mutex and forking a child. The child blocks SIGALRM, initializes thread state, starts up to 16 pthreads under a mutex, waits briefly for them to report started, and then calls `shim_exit_group(0)`. Each pthread sleeps until enough peers exist or stop is requested, then also calls `shim_exit_group(0)`. The parent waits for the child, destroys the mutex, and increments bogo operations.

State and persistence behavior: no durable state is stored. The only cross-process state is the anonymous shared `exit_group_failed` counter used to detect impossible returns from `exit_group`. Thread counts and flags are static process state inside each forked child.

Dependencies and integration points: requires pthread support and `__NR_exit_group`. Integrates with stress-ng mmap, pthread, signal, scheduler, process-state, and syscall shim helpers. Registered as `CLASS_SCHEDULER | CLASS_OS` with always-on verification.

Risks: pthread creation may hit `EAGAIN`, which shortens the child run. The static mutex is initialized in the parent and used after fork, so lifecycle ordering is important. A true `exit_group` failure would leave code paths that intentionally increment the shared failure counter.

Test signals: run `--exit-group` with short timeouts and process/thread limits, confirm no child or pthread leaks, no shared failure count, and unimplemented registration on non-Linux or non-pthread builds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-exit-group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-expmath.c -->
# sources/test-tools/stress-ng/stress-expmath.c

Purpose: implements `expmath`, a CPU floating-point stressor for exponential math functions across real and complex `double`, `float`, and `long double` variants when libc/compiler support is available.

Important APIs/types/functions: `stress_expmath_method_t` maps method names to function pointers. Method functions such as `stress_expmath_exp()`, `stress_expmath_cexp()`, `stress_expmath_exp10l()`, and `stress_expmath_exp2f()` run 10,000 operations and compare against a first-run reference. `stress_expmath_exercise()`, `stress_expmath_all()`, and `stress_expmath()` handle method dispatch, metrics, and loop control.

Control flow: compile-time feature gates populate `stress_expmath_methods[]` with `all` plus available math functions. At runtime the selected method defaults to `all`, metrics are zeroed, workers sync-start, and each loop executes the chosen method. The `all` method invokes every concrete function, while each concrete method accumulates exponentials over normalized inputs, increments bogo operations, and returns failure if its result diverges beyond fixed precision.

State and persistence behavior: no persistent state exists. Each method has static `result` and `first_run` variables used as deterministic per-process reference values. Metrics are static arrays reset at worker start and emitted as operations per second.

Dependencies and integration points: depends on `<math.h>`, optional `<complex.h>`, stress-ng shim math wrappers, target clone/optimization pragmas, process-state, metrics, and option parsing. Unsupported builds retain the option parser but register `stress_unimplemented`.

Risks: static reference comparisons assume deterministic floating-point behavior within one process. Different libm implementations, excess precision, compiler vectorization, or fast-math settings can affect tolerances. Complex and long-double availability is highly platform-dependent.

Test signals: build with varied libm feature sets, run `--expmath-method all` and individual methods, verify per-method metrics appear, and confirm a missing function set reports unimplemented rather than accepting an invalid method silently.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-expmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-factor.c -->
# sources/test-tools/stress-ng/stress-factor.c

Purpose: implements `factor`, a GMP-backed integer stressor that generates large composite integers and factors them by repeated division over prime candidates.

Important APIs/types/functions: option `factor-digits` bounds requested decimal digits from 8 to 100,000,000. `stress_factor()` uses GMP `mpz_t` values for the target, divisor, quotient, remainder, and temporary factors; key GMP calls include `mpz_mul`, `mpz_sizeinbase`, `mpz_sqrt`, `mpz_cdiv_qr`, and `mpz_nextprime`.

Control flow: after option parsing and GMP initialization, the stressor sync-starts. Each iteration builds a value by multiplying small odd non-multiple-of-three random chunks until the decimal digit target is reached. It then sets the divisor to 2, computes a square-root bound, repeatedly divides, records successful factors, advances to the next prime on nonzero remainder, and stops when the divisor exceeds the bound or the value reaches 1. It increments bogo operations and records timing.

State and persistence behavior: all state is in local GMP objects and scalar metric accumulators. There is no filesystem or shared state. GMP objects are cleared on exit.

Dependencies and integration points: requires `gmp.h` and libgmp; otherwise registers unimplemented. Integrates with stress-ng settings, maximize/minimize flags, random helpers, timing, bogo counters, metrics, and process-state reporting. Classifier is `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE`.

Risks: very large digit counts can consume substantial CPU and memory. The factor generator intentionally produces composites from small chunks, so it is a stress workload rather than a cryptographic factor benchmark. Stop checks inside both generation and factoring are required to avoid long uninterruptible operations.

Test signals: build with and without GMP, run minimum/default/moderate `--factor-digits`, confirm metrics for average factors, milliseconds per factorization, and largest digits, and check graceful stop during long factorizations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-factor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fallocate.c -->
# sources/test-tools/stress-ng/stress-fallocate.c

Purpose: implements `fallocate`, a filesystem stressor that allocates, truncates, punches, zeroes, collapses, inserts, and invalidly fallocates ranges in temporary files.

Important APIs/types/functions: option `fallocate-bytes` controls total allocation size divided by worker instances. `modes[]` contains supported `fallocate()` flags; `illegal_modes[]` contains invalid flag combinations. `stress_fallocate()` drives temp-file setup, async/sync fds, mode permutation generation, allocation/truncation loops, optional size verification, and cleanup.

Control flow: the stressor computes per-instance size, reports expected disk usage, creates a temp directory and file, optionally opens a second `O_SYNC` fd, probes pathconf values, unlinks the name, and sync-starts. Each iteration uses `posix_fallocate()` or `fallocate()`, fsyncs, verifies file size when requested, truncates to zero and back, randomly applies supported modes at page-aligned offsets, walks all flag permutations, probes bad fds, illegal modes, pipe fds, and negative offsets/lengths, then increments bogo operations.

State and persistence behavior: file data lives in an unlinked temp file and is removed when descriptors close. The temp directory is removed at teardown. Runtime state includes mode permutations, ftruncate error counts, pipe fds, and filesystem type strings used in diagnostics.

Dependencies and integration points: gated on `HAVE_FALLOCATE`; uses stress-ng temp-dir, filesystem usage, flag permutation, shim fallocate/fsync/stat/unlink, bad-fd, and verification helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS` with optional verification.

Risks: can consume significant disk space or trigger filesystem-specific fallocate semantics. Some modes are Linux/filesystem dependent and may legitimately fail. Verification assumes successful allocation changes file size to the requested length for the chosen path, which may differ for keep-size or specialized modes only used after reset.

Test signals: run on tmpfs/ext4/xfs where available, with small and maximized `--fallocate-bytes`, with `--verify`, and confirm cleanup leaves no temp files while expected invalid operations do not produce failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fallocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fanotify.c -->
# sources/test-tools/stress-ng/stress-fanotify.c

Purpose: implements `fanotify`, a Linux filesystem notification stressor that marks mounted filesystems/mounts for many fanotify events, generates file activity, reads notification metadata, and exercises invalid fanotify calls.

Important APIs/types/functions: `stress_fanotify_account_t` records event counts. `fan_stress_settings[]` and `init_flags[]` enumerate available fanotify masks and initialization flags. `stress_fanotify_supported()` checks `CAP_SYS_ADMIN` and fanotify availability. `fanotify_event_init_invalid()`, `test_fanotify_mark()`, `fanotify_event_init()`, `fanotify_event_clear()`, `stress_fanotify_read_events()`, and `stress_fanotify()` implement the workload.

Control flow: setup installs SIGCHLD handling, creates a temp directory and two filenames, sync-starts, forks a child, and gathers mount points. The child loops creating, closing, writing, reading, renaming, and unlinking a temp file to generate close, access, modify, and rename events. The parent initializes fanotify instances across mounts/filesystems, tests invalid marks, waits with `select()`, reads event buffers, counts known masks, closes event fds, probes `FIONREAD`, and repeatedly tries supported `fanotify_init()` flags for extra kernel coverage.

State and persistence behavior: state is event counters, static mount path storage, fanotify descriptors, aligned read buffer, and temporary files. Temporary files/directories are removed, child is killed, descriptors are closed, marks are flushed/removed, and mount strings are freed on teardown.

Dependencies and integration points: requires `mntent.h`, `sys/select.h`, `sys/fanotify.h`, fanotify syscalls, and `CAP_SYS_ADMIN`. Integrates with stress-ng mount enumeration, capability, temp-dir, killpid, signal, scheduler, metrics, and filesystem-usage helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: fanotify is privilege-heavy and kernel-version-sensitive. Marking every mount can consume descriptors/marks and trigger `EMFILE`/`ENOMEM`; event masks and report flags vary widely. Permission-event flags are included when available, but the code mainly counts metadata and closes event fds to avoid leaks.

Test signals: run as non-root and with `CAP_SYS_ADMIN`, check skip reasons, run on systems with multiple mounts, confirm event-rate metrics for opens/closes/accesses/modifies, and verify no lingering fanotify fds, marks, child processes, or temp files.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fanotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-far-branch.c -->
# sources/test-tools/stress-ng/stress-far-branch.c

Purpose: implements `far-branch`, a CPU/cache stressor that fills many memory pages with return opcodes, spreads callable function pointers across the address space, and repeatedly calls them to stress branch prediction, instruction cache, TLB, and executable mapping behavior.

Important APIs/types/functions: options `far-branch-pages`, `far-branch-flush`, and `far-branch-pageout` control scale and cache/pageout behavior. `stress_far_try_mmap()` and `stress_far_mmap()` map executable return pages at varied addresses and sometimes remap from a backing file. `stress_far_branch_shuffle()`, `stress_far_branch_page_flush()`, `stress_far_branch_pageout()`, and `stress_far_branch()` implement function generation and call loops.

Control flow: setup creates an unlinked temp backing file, installs SIGILL/SIGSEGV/SIGBUS handlers with `sigsetjmp`, allocates function and page arrays, maps pages at offsets from the stressor or random fixed addresses, writes architecture-specific return opcodes, mprotects pages executable, and records function pointers. The loop calls functions in unrolled groups of 32, tracks call count, optionally flips bytes and flushes instruction cache, optionally pageouts/offlines random pages and local labels, periodically shuffles pointer order, and emits call-rate metrics.

State and persistence behavior: executable pages are anonymous or file-backed mappings; the backing file is unlinked and removed with the temp directory. State includes signal diagnostics, `check_flag`, function pointer arrays, mapped page pointers, and call metrics. Cleanup unmaps pages and closes the file.

Dependencies and integration points: requires `mprotect()` and supported return-opcode assembly, excluding NetBSD mitigation paths. Uses stress-ng arch, ret-opcode, cacheflush, madvise, mmap, temp-file, process-state, metrics, and signal helpers.

Risks: executable writable mappings, fixed-address attempts, file-backed executable mappings, and pageout/offline requests are highly platform and policy dependent. Bad return opcodes or stale icache flush behavior can produce SIGILL/SIGSEGV/SIGBUS; handlers convert this into controlled cleanup. Mapping failure fallback duplicates successful page pointers, so cleanup must tolerate aliases carefully.

Test signals: run default, `--far-branch-pages 1`, `--far-branch-flush`, and `--far-branch-pageout`; confirm nonzero calls/sec, check function executed, no duplicate-unmap failures, and unimplemented reporting on unsupported architectures or hardened kernels.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-far-branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fault.c -->
# sources/test-tools/stress-ng/stress-fault.c

Purpose: implements `fault`, a page-fault stressor that creates major faults through tiny file-backed mappings and minor faults through remapped anonymous pages, then reports fault rates when `getrusage()` exposes counters.

Important APIs/types/functions: `stress_segvhandler()` uses `siglongjmp` to escape unexpected SIGSEGV/SIGBUS. `stress_fault()` coordinates temp-file creation, mmap/fallocate/write, unlink timing, `madvise()` fault forcing, resource usage metrics, and cleanup.

Control flow: setup creates a temp directory and filename, installs SIGSEGV/SIGBUS handlers, maps a read-only page placeholder, sync-starts, and loops. Each iteration opens/creates the temp file, ensures it has one byte via `posix_fallocate()` or write, sometimes unlinks it before mapping, maps one byte shared writable, writes through the mapping to fault it in, optionally applies `MADV_DONTNEED` and `MADV_PAGEOUT` and writes again, unmaps, unlinks when needed, then tries a minor fault path by remapping and reading from an anonymous page.

State and persistence behavior: temporary file state is created and removed under stress-ng temp directories. Runtime state includes signal jump flags, fault timing/count accumulators, resource usage snapshots, and one anonymous mapping. No durable state remains after cleanup.

Dependencies and integration points: requires `siglongjmp`; optionally uses `getrusage`, `posix_fallocate`, `madvise`, and `MADV_PAGEOUT`. Integrates with stress-ng executable text address, temp-file, mmap force-unmap, signal, put, process-state, and metrics helpers. Classifier is `CLASS_INTERRUPT | CLASS_OS`.

Risks: page-fault behavior varies by filesystem, memory pressure, and kernel VM policy. Mapping a one-byte file then naming the mapping with page size relies on page granularity. Unexpected SIGBUS/SEGV is treated as failure, while ENOSPC/ENOMEM capacity errors are retried.

Test signals: run on disk-backed and tmpfs temp locations, check major/minor fault debug output, verify `nanosecs per page fault` metrics where supported, and interrupt runs to confirm temp files are unlinked.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fcntl.c -->
# sources/test-tools/stress-ng/stress-fcntl.c

Purpose: implements `fcntl`, a broad file-control stressor that exercises descriptor duplication, fd flags, file status flags, owner/signal settings, leases, POSIX and OFD locks, write-life hints, path fds, and platform-specific `fcntl()` commands.

Important APIs/types/functions: `check_return()` filters acceptable `fcntl()` errors. `setfl_flag_perms` stores permutations of supported `F_SETFL` flags. `do_fcntl()` performs all command probes against a regular temp file, bad fd, and optional `O_PATH` fd. `stress_fcntl()` manages shared temp-file creation and the main loop.

Control flow: the stressor builds all flag permutations, creates a temp directory shared by workers with the same parent PID, opens a temp file with retry handling, optionally opens `/bin/true` as an `O_PATH` fd, and sync-starts. Each loop duplicates fds, toggles close-on-exec and append-like flags, sets/get owners and signals, queries leases and owner UIDs, truncates the file for lock tests, applies POSIX locks with `SEEK_SET/CUR/END`, applies open-file-description locks, cycles write-life hints, tests invalid structs/flags/fds, runs path-fd commands, then increments bogo operations.

State and persistence behavior: persistent state is limited to a temporary file/directory that are unlinked/removed at teardown. Runtime state includes fd flag permutations and lock ranges. Some file flags, owners, signals, locks, and hints are changed on the open temp fd but discarded when it closes.

Dependencies and integration points: depends on whichever `F_*` constants the platform provides; unavailable commands compile out. Uses stress-ng temp-file, bad-fd, racy-unused-pid, syscall, random, and process-state helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS` with always-on verification.

Risks: `fcntl()` semantics are highly OS and filesystem dependent. Some expected failures are `EINVAL`, `EINTR`, `EPERM`, `EAGAIN`, `EACCES`, or `EDEADLK`; incorrect filtering can create false failures. Shared temp directories mean one worker may see `ENOENT` when another has already removed the directory, which the code treats as successful shutdown.

Test signals: run multiple workers with `--verify`, on Linux and BSD-like builds, confirm no unexpected `fcntl` failures, no stale temp directory, lock operations do not deadlock, and new kernel commands such as `F_DUPFD_QUERY`/`F_CREATED_QUERY` return expected boolean-like results when available.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fcntl.c -->

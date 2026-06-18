# subset-b-009385 research

Grouped research for stress-ng source files in `sources/test-tools/stress-ng`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tun.c -->
## sources/test-tools/stress-ng/stress-tun.c

Purpose: Implements the `tun` network/OS stressor, creating transient `/dev/net/tun` interfaces and driving UDP traffic through a TUN or TAP endpoint.

Important APIs/types/functions: `stress_tun_info`, `stress_tun_supported`, and `stress_tun` integrate with stress-ng option parsing (`tun-tap`, `tun-port`), capability checks, network port reservation, and process state transitions. It depends on Linux `if_tun.h`, `ifreq`, `TUNSETIFF`, `TUNSETOWNER`, `TUNSETGROUP`, `TUNSETPERSIST`, and optional TUN ioctl probes.

Control flow: support first requires `CAP_NET_ADMIN` and a readable `/dev/net/tun`. Each loop reserves a randomized port, opens the tun device, creates either TUN or TAP with `IFF_NO_PI`, assigns owner/group, assigns a random `192.168.x.y` address using `SIOCSIFADDR`, forks a child UDP receiver bound to that address/port, and the parent sends up to 64 small datagrams before killing/reaping the child.

State and persistence: device persistence is explicitly disabled with `TUNSETPERSIST`; ports are reserved/released per iteration; file descriptors, child processes, and temporary interface state are cleaned on each path.

Dependencies/integration: uses `core-net`, `core-capabilities`, affinity and scheduler helpers, stress-ng bogo counters, and Linux networking ioctls.

Risks: requires elevated capability and kernel TUN support; random address assignment may fail; port collisions or socket resource pressure can turn into skip/no-resource paths; one suspicious probe uses `TUNSETVNETHDRSZ` after `TUNGETSNDBUF`, likely intentional ioctl exercise but worth reviewing.

Test signals: `VERIFY_ALWAYS`; failures come from ioctl/socket/bind/child exit checks and successful bogo increments after each create/send/reap cycle.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-udp-flood.c -->
## sources/test-tools/stress-ng/stress-udp-flood.c

Purpose: Implements `udp-flood`, a UDP send flood stressor that varies datagram size and alternates between sequential and random reserved destination ports.

Important APIs/types/functions: `stress_udp_flood_info`, `stress_udp_flood`, options `udp-flood-domain`, `udp-flood-if`, and `udp-flood-max-size`; uses `socket`, `sendto`, `ioctl(SIOCOUTQ)`, stress-ng sockaddr construction, interface validation, and port reservation.

Control flow: reads settings, validates optional interface, creates a datagram socket, builds a target sockaddr, then repeatedly reserves one sequential port and one random port. It fills a stack buffer with rotating ASCII bytes, sends to both ports, increases payload size up to the configured maximum, periodically checks socket output queue, and releases/recycles ports every 16384 changes.

State and persistence: maintains transient socket fd, sockaddr, byte/send counters, failure count, and reserved port state. No persistent files are created.

Dependencies/integration: relies on `core-net`, domain masks, global maximize/minimize flags, and stress-ng metrics.

Risks: intentionally resembles flood traffic; can be blocked by interface/domain mismatch, unsupported protocol, packet filtering, or network buffer pressure. A 100 percent `sendto` failure rate is treated as failure.

Test signals: `VERIFY_ALWAYS`; reports MB/sec, sendto/sec, and percent successful sends.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-udp-flood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-udp.c -->
## sources/test-tools/stress-ng/stress-udp.c

Purpose: Implements `udp`, a verified datagram client/server stressor for IPv4/IPv6 UDP and optional UDP-Lite/GRO.

Important APIs/types/functions: `stress_udp_info`, `stress_udp`, `stress_udp_client`, and `stress_udp_server`; options cover domain, interface, port, max size, UDP-Lite, and UDP-GRO. Uses `socket`, `bind`, `sendto`, `recvfrom`, `setsockopt`, `getsockopt`, `ioctl(SIOCINQ/SIOCOUTQ)`, fork, and signal handlers.

Control flow: parent reserves a per-instance port and forks a client. The child repeatedly creates a datagram socket, configures UDP-Lite checksum coverage and optional GRO/cork/encap/no-check/segment probes, then sends buffers whose first bytes encode the child PID. The parent binds, receives datagrams, verifies the embedded PID, and increments bogo operations.

State and persistence: port reservation is per run; AF_UNIX paths, when supported by helper address construction, are unlinked; child is killed and reaped on exit.

Dependencies/integration: uses core networking, affinity, signal, and killpid helpers plus Linux UDP socket options when present.

Risks: network namespaces, packet filters, ENOBUFS/ENOMEM, unsupported UDP-Lite/domain combinations, or fork failure affect behavior; verification is content-based but minimal.

Test signals: `VERIFY_ALWAYS`; primary correctness signal is server PID validation and clean child exit.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-umask.c -->
## sources/test-tools/stress-ng/stress-umask.c

Purpose: Implements `umask`, exercising process umask semantics together with create/stat/close/unlink filesystem operations.

Important APIs/types/functions: `stress_umask_info` and `stress_umask`; uses `umask`, `open(O_CREAT)`, `fstat`, `unlink`, stress-ng temporary directory/name helpers, and random mask generation.

Control flow: saves original umask, creates a temp directory, synchronizes, then iterates all masks from `0000` to `0777`. For each mask it verifies `umask` returned the previous mask, creates a mode `0777` file, verifies effective file permissions equal `~mask & 0777`, closes and unlinks it. It then performs random mask round-trip checks.

State and persistence: mutates process umask but restores the original mask on all exit paths; creates and removes temporary files/directories per iteration.

Dependencies/integration: uses stress-ng temp filesystem helpers, bogo counters, and `VERIFY_ALWAYS`.

Risks: umask is process-global, so unexpected control-flow changes must restore it; filesystem ACL/default-mode behavior could influence permission expectations on unusual filesystems.

Test signals: failures report invalid returned masks, mode mismatches, create/stat/unlink errors; one bogo increment covers a full sweep plus random checks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-umask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-umount.c -->
## sources/test-tools/stress-ng/stress-umount.c

Purpose: Implements `umount`, a Linux/CAP_SYS_ADMIN stressor that races mounting, unmounting, and `/proc/mounts` reading.

Important APIs/types/functions: `stress_umount_info`, `stress_umount_supported`, `stress_umount_umount`, `stress_umount_mounter`, `stress_umount_umounter`, `stress_umount_read_proc_mounts`, and `stress_umount_spawn`; uses `mount` or the fsopen/fsconfig/fsmount/move_mount API, `umount`/`umount2`, fork synchronization, and kill/reap helpers.

Control flow: creates a realpath temp mount point, spawns three synchronized children: one repeatedly mounts tmpfs/ramfs, one aggressively unmounts it, and one repeatedly reads `/proc/mounts`. Parent synchronizes starts, waits until the stressor stops, then kills all children and removes the temp directory.

State and persistence: transient mount state under a temp directory; cleanup forces unmount and removes the directory. Shared PID synchronization state is mmap-backed.

Dependencies/integration: needs Linux mount APIs and `CAP_SYS_ADMIN`; uses core capabilities, signal, and process synchronization.

Risks: high kernel/filesystem impact; permission, ENOSPC, ENOMEM, EBUSY, and unsupported new mount API paths are expected. Cleanup correctness is critical to avoid leaked mounts.

Test signals: `VERIFY_ALWAYS`; detects unexpected mount/umount errors, child setup failures, and uses bogo increments on successful mount cycles.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-umount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-unlink.c -->
## sources/test-tools/stress-ng/stress-unlink.c

Purpose: Implements `unlink`, stressing directory entry removal, open/unlink races, hard links, sync flags, and file close ordering.

Important APIs/types/functions: `stress_unlink_info`, `stress_unlink`, `stress_unlink_exercise`, and `stress_unlink_shuffle`; uses `open`, `link`, `unlink`, `fsync`, `fdatasync`, shared mmap metrics, and multiple forked workers.

Control flow: builds 1024 randomized filenames in a temp dir, forks three child exercisers, and the parent runs the same workload. Each exerciser opens/creates files with randomized flags, occasionally creates hard links, closes one in eight files before unlinking, unlinks all in shuffled order while timing, reshuffles, and closes remaining fds.

State and persistence: temp filenames are heap allocated and cleaned; shared `stress_metrics_t` records unlink count and duration across processes; no intended persistent files remain.

Dependencies/integration: uses `core-mmap`, `core-killpid`, stress-ng temp fs helpers, and metrics.

Risks: intentionally races sibling workers on the same names, so many open/link/unlink failures are tolerated; `VERIFY_NONE` means performance and cleanup are stronger signals than semantic verification.

Test signals: metric `unlink calls per sec`; bogo increments only in parent exercise loop.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-unshare.c -->
## sources/test-tools/stress-ng/stress-unshare.c

Purpose: Implements `unshare`, exercising Linux namespace/resource unsharing across many forked children and flag combinations.

Important APIs/types/functions: `stress_unshare_info`, `check_unshare`, `enough_memory`, and `stress_unshare`; uses `shim_unshare`, clone flag permutations, mmap-shared metrics, OOM adjustment, and kill/reap helpers.

Control flow: builds a permutation list from available `CLONE_*` flags, then repeatedly forks up to 32 short-lived children. Each child optionally unshares a random flag combination and then tries individual flags such as `CLONE_FS`, `CLONE_FILES`, namespace flags, `CLONE_SYSVSEM`, `CLONE_THREAD`, `CLONE_SIGHAND`, and `CLONE_VM`, treating EPERM/EACCES/EINVAL/ENOSPC as expected.

State and persistence: per-child duration/count fields are stored in shared anonymous memory and summarized after the run; no persistent files.

Dependencies/integration: uses Linux `unshare`, memory pressure checks, OOM helpers, and stress-ng flag permutation utilities.

Risks: namespace creation can be expensive or permission-restricted; memory throttling prevents deep swap pressure. The root/newnet special case avoids excessive network namespace cost.

Test signals: `VERIFY_ALWAYS`; reports nanoseconds per unshare call and fails only on unexpected errno paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-unshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-uprobe.c -->
## sources/test-tools/stress-ng/stress-uprobe.c

Purpose: Implements `uprobe`, generating Linux uprobe trace events on a libc function to stress kernel tracing.

Important APIs/types/functions: `stress_uprobe_info`, `stress_uprobe_supported`, `stress_uprobe_write`, `stress_uprobe_libc_start`, and `stress_uprobe`; uses `/proc/$pid/maps`, debugfs tracing files, `select`, `read`, and `getpid` calls as event triggers.

Control flow: support rejects static builds and requires `CAP_SYS_ADMIN`. Runtime locates libc text base, computes the offset of `getpid`, creates a unique uprobe event under `/sys/kernel/debug/tracing/uprobe_events`, enables it, clears the trace, calls `getpid` repeatedly, reads `trace_pipe`, and counts occurrences of the event name.

State and persistence: manipulates global tracing/debugfs state; cleanup disables uprobe events and removes the named event each loop. Metrics track trace bytes.

Dependencies/integration: Linux-only debugfs tracing, libc mapping format, stress-ng capability checks and metrics.

Risks: intrusive tracing side effects; debugfs permissions/availability, busy trace_pipe, or libc path parsing can skip the stressor. Event parsing is intentionally quick and can undercount across read boundaries.

Test signals: bogo count equals parsed event hits; reports MB trace data per second.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-uprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-urandom.c -->
## sources/test-tools/stress-ng/stress-urandom.c

Purpose: Implements `urandom`, stressing `/dev/urandom`, nonblocking/blocking `/dev/random`, random ioctls, select readiness, mmap attempts, and optional verification of permission failures.

Important APIs/types/functions: `stress_urandom_info`, `stress_urandom`, and `check_eperm`; uses random device fds, `read`, `ioctl(RNDGETENTCNT/RNDCLEARPOOL/RNDZAPENTCNT/RNDADDTOENTCNT/RNDRESEEDCRNG)`, `select`, `mmap`, `mprotect`, and optional writes to `/dev/random`.

Control flow: opens available random devices, synchronizes, reads large chunks from `/dev/urandom`, conditionally reads one byte from `/dev/random` only when entropy is high enough, probes privileged ioctls only when not `CAP_SYS_ADMIN`, mmaps `/dev/urandom`, and uses `select` before potentially blocking random reads.

State and persistence: only device descriptors and metrics; it avoids destructive entropy operations when privileged.

Dependencies/integration: Linux random ioctls, capability helper, page-size handling, and stress-ng metrics.

Risks: device absence yields not-implemented skip; entropy depletion is avoided but still environment-sensitive; optional verification assumes privileged ioctls fail with expected errno.

Test signals: optional verify checks EPERM-like failures; metrics report random bits read and bits/sec.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-urandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-userfaultfd.c -->
## sources/test-tools/stress-ng/stress-userfaultfd.c

Purpose: Implements `userfaultfd`, handling user-space page faults from a shared-VM cloned child.

Important APIs/types/functions: `stress_userfaultfd_info`, `stress_userfaultfd_supported`, `stress_userfaultfd_child`, `stress_userfaultfd_clone`, and `handle_page_fault`; uses `userfaultfd`, `UFFDIO_API`, `UFFDIO_REGISTER`, `UFFDIO_COPY`, `UFFDIO_ZEROPAGE`, `UFFDIO_WAKE`, `poll`, `clone(CLONE_VM...)`, and OOM wrapper helpers.

Control flow: allocates a page-aligned zero page and anonymous region sized by `userfaultfd-bytes`, registers missing-page handling, clones a child sharing VM that repeatedly `madvise(MADV_DONTNEED)`s and writes each page, and parent polls/reads `uffd_msg` events. Each write fault is range-checked and resolved either by copying a zero page or zeropage ioctl.

State and persistence: anonymous mapping, userfault fd, clone stack, and OOM child lifecycle are transient. Metrics are updated continuously with nanoseconds per page fault.

Dependencies/integration: Linux userfaultfd headers/syscall, poll, clone, posix_memalign, nonblocking fd helper, OOMable stress-ng wrapper.

Risks: userfaultfd may be disabled or privilege-gated; failure to unregister, wake, or kill child could hang faulting memory; verify depends on write-fault flags.

Test signals: `VERIFY_ALWAYS`; validates API version, supported ioctls, event type, write flag, and address range.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-userfaultfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-usersyscall.c -->
## sources/test-tools/stress-ng/stress-usersyscall.c

Purpose: Implements `usersyscall`, stressing Linux syscall user dispatch and SIGSYS handling.

Important APIs/types/functions: `stress_usersyscall_info`, `stress_supported`, `stress_sigsys_handler`, optional `x86_64_syscall0`, `stress_sigsys_libc_mapping`, and `stress_usersyscall`; uses `prctl(PR_SET_SYSCALL_USER_DISPATCH)`, `syscall`, `sigaction(SA_SIGINFO)`, and architecture-specific direct syscall assembly on x86_64.

Control flow: installs a SIGSYS handler that disables dispatch and copies `siginfo`. Each loop first verifies a blocked fake syscall returns ENOSYS with dispatch disabled, then enables dispatch and expects the SIGSYS path to return the syscall number. On x86_64 it optionally configures libc address bounds so libc syscalls are allowed while raw direct syscalls are trapped.

State and persistence: process-global dispatch selector and static `siginfo` are mutated; dispatch is turned off after each test. No external persistence.

Dependencies/integration: Linux prctl user dispatch support, signal mask handling, architecture helpers, `/proc/self/maps` parsing for libc.

Risks: nested syscalls inside the handler are dangerous, hence broad signal masking and minimal handler work; unsupported kernels return skip/not-implemented.

Test signals: `VERIFY_ALWAYS`; checks return values, `SYS_USER_DISPATCH`, `si_errno`, and reports nanoseconds per trapped syscall.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-usersyscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-utime.c -->
## sources/test-tools/stress-ng/stress-utime.c

Purpose: Implements `utime`, stressing timestamp update APIs over normal, invalid, boundary, and optional fsync paths.

Important APIs/types/functions: `stress_utime_info`, `stress_utime_str`, and `stress_utime`; options include `utime-fsync`. Uses `utimes`, `futimens`, `utimensat`, `utime`, `pathconf(_PC_TIMESTAMP_RESOLUTION)`, `O_PATH` directory fds, bad fd helpers, and temp fs helpers.

Control flow: creates one temp file, then loops through many timestamp update variants: current time, NULL timestamps, invalid names, huge names, FAT-era/2038/boundary values, `UTIME_NOW`, `UTIME_OMIT`, invalid flags, directory-fd empty path, and `AT_SYMLINK_NOFOLLOW`. Every thousand operations it records timing samples.

State and persistence: temp directory/file and optional directory fd are cleaned on exit; no persistent timestamp state remains.

Dependencies/integration: compile-gated timestamp APIs, stress-ng verify flag, filesystem type diagnostics, and metrics.

Risks: filesystem-specific timestamp ranges/resolution can make some probes fail or be ignored; optional verification only checks times are not earlier than requested.

Test signals: `VERIFY_OPTIONAL`; metrics report utime calls/sec and verification reports atime/mtime regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-utime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-varyload.c -->
## sources/test-tools/stress-ng/stress-varyload.c

Purpose: Implements `varyload`, coordinating multiple stressor instances to vary active CPU load over time and optionally apply scheduler policies.

Important APIs/types/functions: `stress_varyload_info`, init/deinit pipe handlers, `stress_varyload_set_sched`, `stress_varyload_waste_time`, `stress_varyload_by_type`, and `stress_varyload`; options select workload method, interval, scheduler, and load pattern.

Control flow: instance zero collects other instance PIDs via a pipe, then synchronizes all workers. Controller stops/continues peers according to brownian, saw-increase, saw-decrease, triangle, pulse, random, or all-rotating load patterns. Active intervals call `stress_workload_waste_time`; non-controller instances just run workload batches when continued.

State and persistence: global pipe fds live across stressor init/deinit; pattern state is static inside `stress_varyload_by_type`; PIDs and one shared workload buffer are transient.

Dependencies/integration: scheduler APIs (`sched_setscheduler`, optional deadline/ext policies), workload method table, mmap/madvise, pipe synchronization, signals.

Risks: depends on multi-instance coordination; scheduler changes may require privilege; SIGSTOP/SIGCONT control can leave peers stopped if cleanup fails, so final continue loop is important.

Test signals: `VERIFY_ALWAYS`; logs selected method/type/interval and bogo increments during workload time.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-varyload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vdso.c -->
## sources/test-tools/stress-ng/stress-vdso.c

Purpose: Implements `vdso`, discovering callable vDSO symbols and measuring their invocation cost.

Important APIs/types/functions: `stress_vdso_info`, wrapper functions for getcpu/gettimeofday/time/clock_gettime/clock_getres, `dl_wrapback`, symbol-list helpers, `stress_vdso_supported`, and `stress_vdso`; option `vdso-func` restricts to one symbol.

Control flow: support gets `AT_SYSINFO_EHDR`, iterates program headers, parses the vDSO dynamic section hash/string/symbol tables, and records known function symbols. Runtime removes duplicate aliases, optionally filters by configured symbol, calls each wrapper until stop, then runs dummy wrappers to estimate overhead and subtract it from per-call timing.

State and persistence: global linked list `vdso_sym_list` is allocated during support probing and freed at the end of the stressor; no external state.

Dependencies/integration: ELF/linker structures, `getauxval`, `dl_iterate_phdr`, stress-ng setting and metric APIs.

Risks: fragile across architectures/libcs with different symbol names or missing SysV hash; global symbol list means support/runtime ordering matters.

Test signals: reports nanoseconds per call excluding overhead plus overhead nanoseconds; invalid `vdso-func` fails with allowed names.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-veccmp.c -->
## sources/test-tools/stress-ng/stress-veccmp.c

Purpose: Implements `veccmp`, a compiler-vector integer comparison stressor with deterministic checksum validation.

Important APIs/types/functions: `stress_veccmp_info` and `stress_veccmp`; uses vector typedefs for 8/16/32/64-bit lanes and optional 128-bit lanes, constants assembled by macros, `OPS` comparison macro, `TARGET_CLONES`, SIGILL catch, and `stress_put_*` sinks.

Control flow: after sync, each loop initializes vector registers from constants, performs repeated greater/less/equal/not-equal comparison mixes across vector widths, folds the resulting vectors into scalar checksums, compares them against fixed expected values, and increments bogo on success.

State and persistence: all computation state is stack/register-local; no heap or file state.

Dependencies/integration: compile gated on `HAVE_VECMATH` and compiler version support; integrates with CPU/vector classifiers and mandatory verification.

Risks: compiler vector semantics and target-clone codegen can vary by architecture; SIGILL handling protects unsupported runtime CPU paths, but checksum mismatches indicate real compiler/CPU bugs or changed semantics.

Test signals: `VERIFY_ALWAYS`; per-width checksum failures are explicit.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-veccmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecfp.c -->
## sources/test-tools/stress-ng/stress-vecfp.c

Purpose: Implements `vecfp`, a selectable floating-point vector arithmetic throughput stressor.

Important APIs/types/functions: `stress_vecfp_info`, generated add/mul/div/neg functions, `stress_vecfp_call_method`, `stress_vecfp_all`, `stress_vecfp_method`, and `stress_vecfp`; option `vecfp-method` selects all or a specific float/double width/operator.

Control flow: allocates initialization records for the maximum vector width, fills deterministic random initial/add/multiply/reverse values, and repeatedly calls the selected vector method. Each method runs `LOOPS_PER_CALL` arithmetic on vector types and stores results. Optional verification reruns into a second result slot and compares float/double tolerances.

State and persistence: per-method static metrics accumulate duration/count; init data is anonymous mmap and freed on exit.

Dependencies/integration: compiler vector extensions, target clones, SIGILL catching, `core-mmap`, stress-ng method option parsing, and metric reporting.

Risks: floating point tolerance is fixed and may be sensitive to compiler optimization, FMA, precision, or target-specific math; huge vector types require compiler support.

Test signals: `VERIFY_OPTIONAL`; emits per-method Mfp-ops/sec and reports result mismatches when verify is active.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecmath.c -->
## sources/test-tools/stress-ng/stress-vecmath.c

Purpose: Implements `vecmath`, a deterministic integer vector arithmetic stressor.

Important APIs/types/functions: `stress_vecmath_info` and `stress_vecmath`; uses vector typedefs, constant-building macros, `OPS` arithmetic/bitwise/shift/mod/div swap operations, `TARGET_CLONES`, SIGILL catch, and stress put sinks.

Control flow: initializes vectors for multiple lane widths, repeats a large mixed operation schedule, increments bogo, then folds each vector width into scalar checksums. Any checksum mismatch marks failure and exits the loop.

State and persistence: stack/register-local only; no persistent resources.

Dependencies/integration: `HAVE_VECMATH`, optional `HAVE_INT128_T`, architecture-specific target clone handling, CPU/vector classifier.

Risks: vector modulo/division and shifts across signed vector lane types are compiler-extension heavy; architecture/compiler differences may reveal bugs. Runtime SIGILL handling is needed for cloned paths on CPUs lacking selected instructions.

Test signals: `VERIFY_ALWAYS`; fixed expected checksums validate 8/16/32/64/optional 128-bit results.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecshuf.c -->
## sources/test-tools/stress-ng/stress-vecshuf.c

Purpose: Implements `vecshuf`, stressing vector shuffle operations across 64-byte vectors of different element widths.

Important APIs/types/functions: `stress_vecshuf_info`, generated shuffle functions, builtin/manual shuffle shims, `stress_vecshuf_set_data`, `stress_vecshuf_set_mask`, `stress_vecshuf_check_data`, and `stress_vecshuf_call_method`; option `vecshuf-method` selects all or one width.

Control flow: allocates a vector data block, seeds original data, then each loop generates reversible rotate masks, applies two shuffles repeatedly so data should return to original order, records ops/bytes/duration, and verifies the final data equals the original.

State and persistence: vector data is anonymous mmap; static per-method metrics/byte counters accumulate until exit; no external resources.

Dependencies/integration: compiler vector support, optional `__builtin_shuffle`, target clones, SIGILL handling, metrics and debug logging.

Risks: manual fallback relies on mask values being in-range; x86 optimization level workarounds indicate compiler sensitivity. Verification catches irreversible shuffle/codegen faults.

Test signals: `VERIFY_ALWAYS`; logs instance-zero throughput and fails on any data mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecshuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecwide.c -->
## sources/test-tools/stress-ng/stress-vecwide.c

Purpose: Implements `vecwide`, measuring behavior across increasingly wide integer vector types.

Important APIs/types/functions: `stress_vecwide_info`, generated `stress_vecwide_*` functions, `vec_args_t`, and `stress_vecwide`; uses vector widths from 32 to 2048 bits by default, optional very small/wide builds, target clones, and metrics.

Control flow: allocates a page-aligned argument/result block, fills byte arrays, then loops over vector-width functions. Each function copies byte arrays into vector locals, performs repeated add/sub/xor/mul operations, stores results, and emits bytes to put sinks. Optional verification runs the same function twice and compares result buffers.

State and persistence: anonymous mmap for vector arguments; static metrics per width; no files or child processes.

Dependencies/integration: compiler vector extensions, SIGILL catch, target clone support, stress-ng metrics/debug output.

Risks: extremely wide vector types can stress compiler backends and instruction selection; note a likely typo copies `vec_args->v23` into local `v3`, making the workload use 23 rather than 3 for that vector input.

Test signals: `VERIFY_OPTIONAL`; reports per-width ops/sec and instance-zero duration share/performance comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vecwide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-verity.c -->
## sources/test-tools/stress-ng/stress-verity.c

Purpose: Implements `verity`, exercising Linux fs-verity enable, measure, readback, and metadata ioctls on temporary files.

Important APIs/types/functions: `stress_verity_info`, `stress_verity`, `hash_info_t`, and shim metadata arg; uses `FS_IOC_ENABLE_VERITY`, `FS_IOC_MEASURE_VERITY`, optional `FS_IOC_READ_VERITY_METADATA`, `FS_IOC_GETFLAGS`, and fs-verity hash algorithm constants.

Control flow: creates a temp file of sparse 64 KiB-offset chunks, writes identifiable 512-byte blocks, fsyncs/syncs, reopens read-only, rotates hash algorithm, enables verity with page-size block size, measures digest, checks `FS_VERITY_FL`, reopens and reads each chunk to validate the first byte, optionally reads verity metadata, unlinks, and increments bogo.

State and persistence: temporary directory/file only; verity state is discarded by unlinking after each iteration.

Dependencies/integration: Linux fsverity headers/ioctls, filesystem support, crypto availability, stress-ng fs usage reporting.

Risks: many filesystems/kernels lack fs-verity or required crypto; errors map to not-implemented/no-resource. Once verity is enabled the file is immutable, so per-iteration unlink/recreate is required.

Test signals: `VERIFY_ALWAYS`; checks verity flag and readback block content.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-verity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vforkmany.c -->
## sources/test-tools/stress-ng/stress-vforkmany.c

Purpose: Implements `vforkmany`, creating long chains of vforked processes and optional VM pressure.

Important APIs/types/functions: `stress_vforkmany_info`, `vforkmany_shared_t`, `vforkmany_wait`, and `stress_vforkmany`; options `vforkmany-vm` and `vforkmany-vm-bytes`; uses `fork`, `shim_vfork`, waitpid, alternate signal stack, KSM/madvise/mincore/OOM helpers.

Control flow: parent sets up alt signal stack and shared state, forks a worker, then sleeps until timeout and sets a termination flag. Worker can allocate/touch memory, then repeatedly vforks children; vfork children increment shared counters, measure startup latency, optionally madvise/touch memory, and continue spawning until stop. Parents wait for children to avoid zombies.

State and persistence: mmap-shared counters and termination flag; optional anonymous waste mappings; no files.

Dependencies/integration: careful static variables due to vfork shared address-space semantics, OOM adjustment, signal stack helpers, memory pressure utilities.

Risks: vfork semantics are fragile; stack/global misuse can corrupt parent state. Resource exhaustion and OOM are expected. Parent clears OOMable flag so the controller is less likely to be killed.

Test signals: `VERIFY_ALWAYS`; reports nanoseconds to start vforked process and fails if children were invoked but none waited successfully.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vforkmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-addr.c -->
## sources/test-tools/stress-ng/stress-vm-addr.c

Purpose: Implements `vm-addr`, stressing memory addressing patterns over mappings placed at many virtual addresses.

Important APIs/types/functions: `stress_vm_addr_info`, many `stress_vm_addr_*` pattern functions, `stress_vm_addr_all`, `stress_vm_addr_child`, and `stress_vm_addr`; options select method, mlock, and NUMA randomization.

Control flow: parent allocates a shared bit-error counter, optional NUMA masks, then runs an OOMable child. Child loops over power-of-two address hints and buffer sizes from 8 to 64 MiB, mmaps anonymous memory, optionally marks mergeable/randomizes NUMA/mlocks it, applies the selected address pattern, adds any readback mismatches to the shared counter, unmaps, and increments bogo.

State and persistence: only anonymous mappings and NUMA mask allocations; shared error counter survives child restarts until parent checks it.

Dependencies/integration: bit operations, cache flush in aggressive mode, madvise, NUMA helpers, OOM wrapper, target clones, SIGILL catch.

Risks: address-hint mmap may fail frequently; OOM avoidance adjusts size under low memory. Pattern correctness assumes power-of-two sizes and masks; detected bit errors are treated as failure.

Test signals: `VERIFY_ALWAYS`; any nonzero bit error count fails, and debug logs selected method.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-rw.c -->
## sources/test-tools/stress-ng/stress-vm-rw.c

Purpose: Implements `vm-rw`, stressing cross-process memory copying with `process_vm_readv` and `process_vm_writev`.

Important APIs/types/functions: `stress_vm_rw_info`, `stress_vm_child`, `stress_vm_parent`, and `stress_vm_rw`; option `vm-rw-bytes`; uses `clone(CLONE_VM)`, pipes, `process_vm_readv`, `process_vm_writev`, iovecs, and kill/reap helpers.

Control flow: parent computes per-instance transfer size, creates two pipes, clones a child sharing VM, and waits for child buffer-address messages. Parent reads the child buffer in chunks up to 1 GiB, optionally verifies zeros, fills local pages with an incrementing value, probes invalid flags/pids, writes data back to the child, and notifies it. Child verifies the written byte per page when verify is enabled, clears pages, and sends the address again.

State and persistence: transient anonymous mappings, pipes, clone stack, and child pid; no files. Transfer size is page-aligned and split by `iov_count`.

Dependencies/integration: Linux process_vm APIs, `sys/uio.h`, clone support, stress-ng memory usage reporting.

Risks: clone with shared VM plus separate mappings is subtle; pipe termination writes use the wrong pipe descriptor in one cleanup path, but child killing limits impact. Verification is optional.

Test signals: `VERIFY_OPTIONAL`; failures report read/write syscall errors or page-content mismatches, bogo increments after complete read/write cycles.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-rw.c -->

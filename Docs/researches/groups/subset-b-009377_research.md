# subset-b-009377 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-oom-pipe.c -->
# sources/test-tools/stress-ng/stress-oom-pipe.c

Purpose: `stress-oom-pipe.c` implements the `oom-pipe` stressor, which deliberately opens many pipes, grows pipe buffers with `F_SETPIPE_SZ`, and fills/drains them to stress kernel pipe memory allocation and OOM handling.

Important APIs/types/functions: the build requires `F_SETPIPE_SZ`, `F_SETFL`, and `O_NONBLOCK`. `stress_oom_pipe_context_t` carries descriptor limits, maximum pipe size, shared read/write buffers, and the descriptor array. `pipe_fill()` writes page-sized chunks with a changing first word; `pipe_empty()` drains page-sized chunks. `stress_oom_pipe_child()` performs the pipe open/grow/fill/shrink loop, and `stress_oom_pipe()` allocates buffers/descriptors and runs the child through `stress_oomable_child()`.

Control flow: the parent mmaps two page buffers, discovers file-descriptor and pipe-size limits, allocates an fd table, waits at the sync barrier, and launches an oomable child. The child drops capabilities, initializes all fds to `-1`, opens as many nonblocking pipes as possible, then repeatedly grows each pipe to the maximum rounded pipe size, fills it, optionally drains it unless aggressive mode is active, exercises invalid pipe sizes, shrinks to one page, fills/drains again, and increments bogo ops.

State and persistence behavior: all state is process-local or anonymous memory: descriptor arrays, two pipe buffers, and kernel pipe buffers. The child closes every opened fd in cleanup. No filesystem artifacts are created.

Dependencies and integration points: it integrates with stress-ng OOM controls, capability dropping, memory-low checks, file-limit helpers, pipe-size helpers, mmap naming, sync barriers, and `CLASS_MEMORY | CLASS_OS | CLASS_PATHOLOGICAL` registration with `VERIFY_ALWAYS`.

Risks: the stressor intentionally consumes pipe memory and file descriptors; on systems without OOM avoidance it can trigger memory pressure. `fcntl(F_SETFL, O_NONBLOCK)` failure aborts through cleanup, but fd pressure before `pipes_open` can return `EXIT_NO_RESOURCE`. Aggressive mode leaves pipe contents queued for more memory pressure.

Test signals: direct `--oom-pipe` runs should show bogo progress and clean descriptor teardown. Useful variants include aggressive mode, OOM-avoid mode, low fd limits, systems with small `/proc/sys/fs/pipe-max-size`, and builds missing the required fcntl constants.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-oom-pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-opcode.c -->
# sources/test-tools/stress-ng/stress-opcode.c

Purpose: `stress-opcode.c` implements the `opcode` stressor, generating executable pages of random, incrementing, mixed, or mutated text opcodes and forking contained children to execute them while counting attempted, successful, and signal-faulting instructions.

Important APIs/types/functions: `stress_opcode_state_t` is shared state for opcode value, attempts, successes, previous opcode, and per-signal counts. Generator methods are `stress_opcode_random()`, `stress_opcode_inc()`, `stress_opcode_mixed()`, and `stress_opcode_text()`, selected by `--opcode-method`. `stress_opcode_child_sighandler()` records signals and uses `siglongjmp` where available. A seccomp BPF filter permits only exit, signal, and `mprotect`-style syscalls and traps others.

Control flow: the parent mmaps shared state and an executable opcode arena with guard pages, chooses the method, synchronizes, and repeatedly forks. Each child installs signal handlers, marks shared state read-only, disables core dumps, drops capabilities, creates guard pages around the opcode buffer, fills the buffer, changes it to `PROT_READ | PROT_EXEC`, starts a short real-time interval timer, optionally installs seccomp, and calls into successive opcode offsets. Fault handlers either exit for termination/serious memory signals or jump back for lesser traps. The parent waits, counts a bogo op per fork, and emits metrics at shutdown.

State and persistence behavior: shared anonymous state persists across child forks during the run and is munmapped at deinit. The opcode buffer is private anonymous memory. Process signal handlers, interval timers, seccomp state, dumpability, and capabilities are child-local containment state.

Dependencies and integration points: it depends on Linux audit/filter/seccomp headers, `mprotect`, architecture opcode-size macros, cache-flush helpers, executable text address discovery, stress-ng metrics, fork retry, scheduler settings, and process naming for incrementing opcode mode.

Risks: executing arbitrary bytes is inherently crash-heavy; containment relies on guard pages, signal handling, timer aborts, seccomp, closed stdio, and child isolation. Metrics use signal counters in a page made read-only between opcode calls, so handler `mprotect()` behavior is central. Architecture opcode-size and signal semantics can make coverage and success percentages nonportable.

Test signals: direct `--opcode` plus each `--opcode-method` should produce fork/opcode/signal metrics without wedging. Important checks are no stuck child after timer expiry, no leaked executable mappings, valid unsupported-build fallback, and plausible metrics for illegal opcode, SIGBUS, SIGSEGV, SIGFPE, and SIGTRAP rates.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-opcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-open.c -->
# sources/test-tools/stress-ng/stress-open.c

Purpose: `stress-open.c` implements the `open` stressor, exercising high-volume file descriptor opening and closing across many `open`, `openat`, `openat2`, device, directory, pseudo-terminal, `dup`, procfs, `O_TMPFILE`, `O_DIRECT`, and timestamp update paths.

Important APIs/types/functions: `stress_open_func_t` describes open variants stored in `open_funcs[]`. Wrappers `open_arg2()` and `open_arg3()` time successful opens and call obsolete `futimes` variants. Helpers cover flag permutations (`open_flag_perm()`), `/dev/zero`, `/dev/null`, `O_TMPFILE`, `posix_openpt`, directory and `O_PATH`, invalid `O_CREAT` on a directory, `openat` from cwd or dirfd, Linux `openat2`, `/proc/self/fd`, `dup`, undefined `O_RDONLY | O_TRUNC`, and mode cycling.

Control flow: `stress_open()` creates a temp directory, resolves `open-max` with size and fd limits, mmaps an fd array, optionally forks an `open-fd` child that endlessly opens paths under `/proc/$pid/fd`, computes all flag permutations, synchronizes, and then repeatedly fills the fd array by choosing random open functions until hitting `open_max` or fd exhaustion. It samples fdinfo, periodically syncs, then closes a random fd and tries `close_range()` over the observed min/max range, falling back to individual close and verifying closure with `F_GETFL`.

State and persistence behavior: state includes global `open_count` and `open_perms`, the mmap fd table, optional child process, temp directory/files, cwd changes in `openat` helpers, and metrics for successful open latency. Temporary files are unlinked after each helper and the temp directory is removed at deinit.

Dependencies and integration points: it uses stress-ng filesystem limits, temp-dir helpers, flag permutation generation, `/proc` fdinfo helpers, syscall shims, `close_range`, openat2 headers, futimes shims, fork/kill helpers, and registers as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: many helpers intentionally trigger invalid or platform-specific open combinations, so failures are often expected and retried. `open_with_openat_cwd()` and `open_with_openat2_cwd()` temporarily change cwd and must restore it. `close_range()` over min/max can close fds that were not opened by this stressor if fd ranges overlap in unexpected ways, though the code uses process-local descriptors. High `open-max` values can exhaust memory or descriptors.

Test signals: direct `--open`, `--open-max`, and `--open-fd` should produce nonzero `nanosecs per open` metrics. Good coverage includes kernels with and without `openat2`, filesystems lacking `O_TMPFILE` or `O_DIRECT`, low fd limits, procfs unavailable, and verification that closed descriptors fail `F_GETFL`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pagemove.c -->
# sources/test-tools/stress-ng/stress-pagemove.c

Purpose: `stress-pagemove.c` implements the `pagemove` stressor, using Linux `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)` to rotate physical page mappings through virtual addresses and verify that page contents move as expected.

Important APIs/types/functions: `page_info_t` records the original virtual address and page number stored at each page. `stress_pagemove_info_t` carries parsed byte count, page count, mlock, and NUMA settings. `stress_pagemove_child()` performs the moving and verification. `stress_pagemove_remap_fail()` reports failed remaps.

Control flow: the top-level function resolves `pagemove-bytes`, scales it per instance, aligns to page size, enforces at least three pages and a 32-bit-safe maximum, reports memory use, and invokes an oomable child. The child mmaps one extra page, optionally mlocks, unmaps the extra page as a swap slot, optionally prepares NUMA masks, then loops: writes page identity records, protects the region read-only, verifies identities, and for each adjacent pair moves the current page to the unmapped slot, the next page down, and the slot page back up. It periodically records remap timing metrics and validates the final rotated page numbers.

State and persistence behavior: all state is anonymous memory plus optional NUMA placement and mlock state. The extra page is intentionally unmapped to provide a temporary fixed remap target. Cleanup unmaps the main region and frees NUMA masks.

Dependencies and integration points: it requires `mremap` with fixed/maymove flags, `mprotect`, stress-ng mmap/oom/memory accounting, optional `mlock`, optional Linux NUMA helpers, and registers as `CLASS_VM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: fixed remaps are sensitive to alignment and mapping holes; any failed intermediate remap can leave parts of the original region moved, so cleanup uses broad unmap attempts. NUMA randomization mutates the shared `pagemove_numa` flag inside child context. Verification assumes every page can hold `page_info_t`.

Test signals: `--pagemove` should report bogo progress and `page remaps per sec`. Variants should include `--pagemove-mlock`, `--pagemove-numa`, tiny byte values that force minimum adjustment, large byte values that force maximum adjustment, and unsupported builds without `mremap` flags.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pagemove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pageswap.c -->
# sources/test-tools/stress-ng/stress-pageswap.c

Purpose: `stress-pageswap.c` implements the `pageswap` stressor, allocating one page at a time and asking the kernel to page it out with `madvise(MADV_PAGEOUT)` before later touching and unmapping the list.

Important APIs/types/functions: `page_info_t` embeds `self`, `next`, and `size` in each mapped page for list walking and verification. `stress_pageswap_supported()` gates on `MADV_PAGEOUT`. `stress_pageswap_count_paged_out()` optionally uses `mincore()` to count nonresident pages. `stress_pageswap_unmap()` pages out, verifies, counts, and unmaps the list. `stress_pageswap_child()` performs the allocation/pageout loop.

Control flow: `stress_pageswap()` resolves `pageswap-pages`, reports memory use, synchronizes, and runs an oomable capability-dropping child. The child maps private anonymous pages, links them into a list, stores self pointers, calls `MADV_PAGEOUT` on the new and previous head, optionally repopulates reads in aggressive mode, and unmaps the whole list when the configured page count or memory-low condition is reached. Bogo ops increment on each successful page mapping.

State and persistence behavior: state is only anonymous page mappings linked through in-page metadata. No files are created. Verification reads back `self` before unmapping; this intentionally faults pages back in after pageout.

Dependencies and integration points: it depends on Linux `MADV_PAGEOUT`, optional `MADV_POPULATE_READ`, optional `mincore`, stress-ng OOM child handling, memory-low checks, sync barriers, metrics, and `CLASS_OS | CLASS_VM` registration with `VERIFY_OPTIONAL`.

Risks: `MADV_PAGEOUT` is advisory, so mincore counts can vary with kernel memory pressure and policy. The stressor can create many VMAs and provoke reclaim; OOM avoidance is important under constrained memory. Verification only checks page metadata after reaccess, not that the kernel actually swapped the page.

Test signals: direct `--pageswap` runs should produce bogo progress and possibly `microsecs per page swapout`. Useful variants include `--pageswap-pages 1`, maximize pages, aggressive mode, verify mode, and systems without `MADV_PAGEOUT` where the supported callback must skip cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pageswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pci.c -->
# sources/test-tools/stress-ng/stress-pci.c

Purpose: `stress-pci.c` implements the Linux `pci` stressor, scanning PCI sysfs device directories and repeatedly opening, mmaping, and reading regular PCI attribute/resource files.

Important APIs/types/functions: `stress_pci_info_t` stores sysfs path, device name, ignore flag, per-device read metrics, and list linkage. Discovery uses `stress_pci_dev_filter()`, `stress_pci_info_get_by_name()`, and `stress_pci_info_get()`, with optional `--pci-dev`. `stress_pci_exercise_file()` opens a sysfs file, validates it is regular/nonempty, tries `mmap`, reads non-ROM files, and toggles ROM access. `stress_pci_handler()` longjmps out of unexpected SIGSEGV/SIGBUS.

Control flow: the stressor resolves optional operation rate, synchronizes, installs SIGSEGV/SIGBUS handlers, builds a linked list from `/sys/bus/pci/devices`, and loops over unignored devices. Each device directory is scanned, files are exercised, bogo ops increment, and optional rate limiting sleeps until the next target time. If a signal occurs while reading/mmaping a device, that device is marked ignored and iteration continues.

State and persistence behavior: state is the heap device list plus per-device metric counters. Sysfs files are opened read-only except ROM files, where `"1\n"` and `"0\n"` are written to enable/disable ROM access. No normal filesystem persistence is created.

Dependencies and integration points: Linux sysfs PCI layout, `scandir`, `mmap`, `read`, signal longjmp, stress-ng settings, metrics, rate limiting, sync barriers, and `CLASS_OS` registration.

Risks: PCI sysfs contents vary by hardware, permissions, driver state, and platform firmware. Reading or mmaping resource/ROM files can trigger SIGBUS/SIGSEGV or hardware-specific failures, so signal recovery and ignore flags are important. ROM reads are deliberately avoided because reported ROM sizes can be unreliable.

Test signals: `--pci` should skip when no sysfs entries exist and otherwise report config/resource MB/s for instance zero. `--pci-dev` should limit discovery to one device. Tests should cover permission-denied resource files, signal recovery, rate limiting, and cleanup of allocated device lists.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-personality.c -->
# sources/test-tools/stress-ng/stress-personality.c

Purpose: `stress-personality.c` implements the `personality` stressor, cycling through Linux execution-domain/personality constants and restoring/querying personality state.

Important APIs/types/functions: the implementation is gated on `HAVE_PERSONALITY` and includes generated `personality.h` entries into a static `personalities[]` array terminated by `INVALID_PERSONALITY`. `stress_personality_supported()` skips if the generated list is empty. `stress_personality()` tracks per-personality failures in a boolean array.

Control flow: the stressor allocates a failure table, reports how many personalities will be attempted, synchronizes, and loops over all generated personalities until stop. For each personality it skips permanently failed entries, calls `personality(p)`, retrieves the current personality via `personality(0xffffffffUL)`, exercises an invalid random high personality, restores `p`, and counts a bogo op per full pass. If every real personality fails, it reports failure.

State and persistence behavior: state is process personality flags plus the heap `failed[]` table. There is no filesystem state and no child process. Failed personalities are remembered for the duration of the run to reduce repeated unsupported calls.

Dependencies and integration points: it depends on `sys/personality.h`, generated build-time personality constants, stress-ng sync/state helpers, random number helpers, memory-free reporting, and registers as `CLASS_OS` with `VERIFY_ALWAYS`.

Risks: personality availability is architecture and kernel dependent; many constants can fail legitimately. Personality changes may alter process behavior such as address layout or uname quirks, so restoring/querying within the same loop matters. Treating all entries failing as hard failure distinguishes unsupported constants from a completely nonfunctional interface.

Test signals: direct `--personality` should either skip due to no generated personalities or make bogo progress. Failure signals include inability to query with `0xffffffffUL`, all personalities rejected, or unsupported builds without the syscall/header.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-peterson.c -->
# sources/test-tools/stress-ng/stress-peterson.c

Purpose: `stress-peterson.c` implements the `peterson` stressor, validating Peterson's two-process mutual exclusion algorithm under explicit memory fences and architecture barriers.

Important APIs/types/functions: `peterson_mutex_t` contains volatile `turn`, `check`, and two flags. `peterson_t` is shared and cache-aligned, containing the mutex and two metric slots. `peterson_mfence()` wraps `shim_mfence()`, and `peterson_mbarrier()` uses ARM `dmb sy` when present. `stress_peterson_p0()` increments the check value; `stress_peterson_p1()` decrements it and increments bogo ops.

Control flow: support probing installs a temporary SIGILL handler and executes the memory barrier path to ensure it is usable. The stressor mmaps shared state, synchronizes, initializes flags, records the parent CPU, and forks. The child optionally moves to the parent CPU and repeatedly enters the p0 side; the parent runs p1. Each side sets its flag, gives turn to the other, fences, waits until the critical section is allowed, updates `check`, clears its flag, records timing, and verifies the check changed exactly by one.

State and persistence behavior: shared anonymous memory holds the lock variables, check counter, and metrics. The only persistent process effect is temporary affinity adjustment in the child. Cleanup kills/waits the child and unmaps shared memory.

Dependencies and integration points: it requires shim memory fencing and siglongjmp support, optional architecture barriers, affinity helpers, mmap helpers, fork/kill helpers, scheduler helpers, and registers as CPU cache plus IPC with `VERIFY_ALWAYS`.

Risks: the algorithm is sensitive to memory ordering; weakly ordered architectures rely on the fence/barrier placements. A child exit status overwrites parent result if the child exits normally. If fork fails after mmap, the current code returns no-resource without unmapping the shared mapping, a small error-path leak.

Test signals: `--peterson` should produce `nanosecs per mutex` and no check mismatch. Useful coverage includes ARM/PPC/RISC-V fence behavior, SIGILL support skip, same-CPU affinity changes, and forced stop while the peer is spinning.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-peterson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-physmmap.c -->
# sources/test-tools/stress-ng/stress-physmmap.c

Purpose: `stress-physmmap.c` implements the Linux `physmmap` stressor, attempting to mmap physical System RAM ranges from `/dev/mem` page by page and optionally read from successful mappings.

Important APIs/types/functions: `stress_physmmap_t` represents a `/proc/iomem` System RAM range, with base address, size, page count, bitmap of still-mappable pages, mappable flag, and list link. `stress_physmmap_supported()` requires `CAP_SYS_ADMIN`. `stress_physmmap_get_ranges()` parses `/proc/iomem`; `stress_physmmap_flags()` randomizes `MAP_SHARED`/`MAP_PRIVATE` and optional `MAP_POPULATE`; `stress_physmmap_read()` performs volatile 64-bit reads.

Control flow: the stressor reads `--physmmap-read`, opens `/dev/mem`, builds the range list, synchronizes, and logs total pages for instance zero. Each pass attempts a whole-range mmap and then iterates every still-enabled page in each mappable range. Successful page mappings optionally read and are unmapped; failed pages are cleared from the bitmap. Ranges with no page successes become non-mappable. The loop stops when no ranges remain mappable or the run ends.

State and persistence behavior: state is heap range metadata and per-range bitmaps. Kernel state is transient `/dev/mem` mappings. No files are written.

Dependencies and integration points: Linux `/proc/iomem`, `/dev/mem`, `CAP_SYS_ADMIN`, mmap/munmap, stress-ng metrics, sync barriers, random flags, and `CLASS_VM` registration with `VERIFY_NONE`.

Risks: modern kernels often restrict `/dev/mem`, so inability to map pages is expected. Mapping physical RAM may be dangerous or denied depending on kernel config and lockdown mode. The range bitmap avoids retrying known failures, but whole-region attempts still occur each pass.

Test signals: privileged `--physmmap` should report total attempted pages and metrics for successful/failed mmaps and max pages mapped. Unprivileged runs should skip. `--physmmap-read` adds volatile read coverage for successful mappings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-physmmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-physpage.c -->
# sources/test-tools/stress-ng/stress-physpage.c

Purpose: `stress-physpage.c` implements the Linux `physpage` stressor, translating virtual pages through `/proc/self/pagemap`, checking `/proc/kpagecount`, and optionally exercising `/dev/mem` and MTRR operations for the resulting physical page.

Important APIs/types/functions: `PAGE_PRESENT` and `PFN_MASK` decode pagemap entries. `stress_physpage_supported()` requires `CAP_SYS_ADMIN`. `stress_virt_to_phys()` does the virtual-to-physical lookup, kpagecount validation, `/dev/mem` read/mmap attempts, optional writable mapping, and optional MTRR exercise. On x86 with MTRR headers, `stress_physpage_mtrr()` adds, verifies, and deletes MTRR entries for several cache types.

Control flow: the stressor opens `/proc/self/pagemap`, optionally `/proc/kpagecount`, and optionally `/dev/mem`, then synchronizes. Each iteration maps one private writable page near an incrementing preferred address, names it, translates it, unmaps it, also translates `g_shared->stats`, increments bogo ops, and continues while no hard verification failure occurs.

State and persistence behavior: state is transient anonymous page mappings plus open proc/dev descriptors. Optional MTRR modification touches kernel-wide MTRR state but deletes entries after each successful add. No normal files are created.

Dependencies and integration points: Linux proc pagemap interfaces, `/dev/mem`, x86 MTRR ioctls, stress-ng capability checks, mmap helpers, shared stats pointer, and `CLASS_VM` registration with `VERIFY_ALWAYS`.

Risks: pagemap PFNs are privileged and can be masked or restricted; `/proc/kpagecount` and `/dev/mem` may be absent or denied. MTRR operations are global and platform-specific, so `--physpage-mtrr` is risky and should be privileged-only. A zero physical address is treated as nonfatal.

Test signals: `--physpage` should skip without `CAP_SYS_ADMIN`; privileged runs should bogo-progress while kpagecount is sane. Additional signals include debug messages when `/proc/kpagecount` is unavailable, `/dev/mem` denial tolerance, and MTRR add/get/delete behavior under `--physpage-mtrr`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-physpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pidfd.c -->
# sources/test-tools/stress-ng/stress-pidfd.c

Purpose: `stress-pidfd.c` implements the `pidfd` stressor, exercising Linux pidfd opening, signaling, pidfd getfd, stat, and invalid operation paths against short-lived child processes.

Important APIs/types/functions: the implementation is gated by `HAVE_PIDFD_SEND_SIGNAL`. `stress_pidfd_open()` probes invalid pid/flags and randomly uses `pidfd_open()` or `/proc/$pid` directory open as a fallback pidfd-like descriptor. `stress_pidfd_supported()` validates pidfd send-signal support. `stress_pidfd_reap()` kills/waits a child and closes its pidfd.

Control flow: after sync, the stressor repeatedly forks a paused child. The parent optionally tests `PIDFD_NONBLOCK`, opens a pidfd, `fstat`s it, tries illegal `mmap`, attempts `pidfd_getfd` on fd 0 plus invalid flags/bad fd, sends signal 0 for existence, then SIGSTOP and SIGCONT through `pidfd_send_signal`. It also exercises special pidfd constants when available, reaps the child, and increments bogo ops.

State and persistence behavior: state is a child process per iteration, the pidfd/proc descriptor, and transient file-descriptor copies returned by `pidfd_getfd`. No filesystem output is created, though `/proc` is used for fallback descriptors.

Dependencies and integration points: pidfd syscall shims, procfs, fork retry, bad fd helpers, kill/wait helpers, `stress_unused_racy_pid_get()`, mmap failure probing, sync barriers, and `CLASS_INTERRUPT | CLASS_OS` registration with `VERIFY_ALWAYS`.

Risks: fallback opening `/proc/$pid` may not support every pidfd operation. Child lifetime races can make pidfd open fail and retry. `pidfd_getfd` behavior depends on ptrace permissions and kernel support. ENOSYS during send-signal is converted to not-implemented.

Test signals: direct `--pidfd` should make bogo progress and no send-signal failures. Tests should cover kernels without pidfd syscalls, procfs unavailable, permission-denied `pidfd_getfd`, `PIDFD_NONBLOCK`, and valid SIGSTOP/SIGCONT delivery.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pidfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ping-sock.c -->
# sources/test-tools/stress-ng/stress-ping-sock.c

Purpose: `stress-ping-sock.c` implements the `ping-sock` stressor, sending ICMP echo packets over Linux datagram ICMP sockets to loopback while varying payload contents and destination ports.

Important APIs/types/functions: the build requires Linux, `PF_INET`, `SOCK_DGRAM`, `IPPROTO_ICMP`, and `struct icmphdr`. `stress_rawsock_open()` opens `socket(AF_INET, SOCK_DGRAM, IPPROTO_ICMP)` and maps permission/protocol failures to skip/not-implemented. `stress_rawsock_supported()` probes open/close. `stress_ping_sock()` builds and sends packets.

Control flow: the stressor resolves `ping-sock-max-size`, opens the ping socket, initializes a loopback `sockaddr_in`, prepares an ICMP echo header with pid-based id, chooses a starting unprivileged port, synchronizes, and loops. Each iteration fills the payload with a rotating ASCII byte, sends with `sendto()`, records bytes and bogo ops on success, increments ICMP sequence and destination port, and wraps ports back above 1024.

State and persistence behavior: state is a socket fd, stack packet buffer, sockaddr, sequence number, port counter, and metrics. No persistent files or network state are created beyond transient loopback ICMP traffic.

Dependencies and integration points: it integrates with Linux ping-group permissions, stress-ng option parsing, sync barriers, metrics, and `CLASS_NETWORK | CLASS_OS` registration.

Risks: unprivileged ping sockets depend on `/proc/sys/net/ipv4/ping_group_range`; EPERM/EACCES are expected skip conditions. The call uses `ping_sock_max_size` as send length even though the buffer also includes the header, so the configured max size represents total sent bytes from the header start. `sendto()` failures are logged as stressor failures but the loop continues.

Test signals: direct `--ping-sock` should report `ping sendto calls per sec` and `ping bytes per sec`. Permission-denied, unsupported protocol, minimum and maximum size, and loopback-only behavior are the key validation cases.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ping-sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pipe.c -->
# sources/test-tools/stress-ng/stress-pipe.c

Purpose: `stress-pipe.c` implements the `pipe` stressor, creating reader and writer process groups around a pipe to stress pipe throughput, packet mode, pipe sizing, `vmsplice`, signal shutdown, and optional data verification.

Important APIs/types/functions: `stress_pipe_write_t` stores per-writer duration and byte counts in shared memory. `pipe_get_size()` and `pipe_change_size()` read/set pipe buffer size. Read/write helpers cover generic `read`/`write` and optional `vmsplice`, with verified and unverified variants. Option callbacks parse `pipe-size` and `pipe-data-size`.

Control flow: the stressor resolves reader/writer counts, data size, pipe size, and vmsplice option, disables verification when multiple readers or writers make ordering nondeterministic, mmaps writer metrics, installs SIGPIPE stop handling, creates a pipe or `pipe2(O_DIRECT)` packet-mode pipe, sizes the pipe, mmaps read/write buffers, fills write data, synchronizes, and forks readers then writers. Children close unused pipe ends, apply scheduling/affinity, and run the chosen read or write loop. The parent sleeps until stop, sends SIGPIPE to children, waits for them, aggregates writer bytes/durations, and reports MB/s.

State and persistence behavior: state is anonymous shared writer metrics, pipe fds, private read/write buffers inherited by children, and child pid arrays. No files persist. SIGPIPE handling controls orderly shutdown.

Dependencies and integration points: pipe/pipe2, optional `O_DIRECT` packet mode, `F_GETPIPE_SZ`/`F_SETPIPE_SZ`, optional `vmsplice`, `FIONREAD`, stress-ng affinity/scheduler/signal/mmap helpers, and `CLASS_PIPE_IO | CLASS_MEMORY | CLASS_OS | CLASS_IPC` registration with optional verify.

Risks: high process counts can exhaust fork capacity. Verified mode only works for one reader and one writer. In the final wait section, the writer wait loop iterates `i < pipe_readers` while indexing `wr_pids`, so if writer count exceeds reader count some writer children may not be waited there. `vmsplice` is disabled unless packet mode is available.

Test signals: `--pipe` should produce MB/s metrics and clean child exit. Important variants include `--pipe-vmsplice`, explicit pipe sizes, min/max reader/writer counts, verify with a single reader/writer, and low fork/fd resource conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pipeherd.c -->
# sources/test-tools/stress-ng/stress-pipeherd.c

Purpose: `stress-pipeherd.c` implements the `pipeherd` stressor, simulating a token-passing herd of processes over one pipe to stress pipe wakeups, context switching, and exclusive wait behavior.

Important APIs/types/functions: `stress_pipeherd_data_t` carries a token counter and random check value. `stress_pipeherd_read_write()` repeatedly reads the token, increments the counter, writes it back, and optionally yields. `stress_pipeherd()` owns pipe setup, process herd creation, token recovery, metrics, and verification.

Control flow: the stressor resolves process count and yield option, creates one pipe, optionally enables pipe packet mode with `O_DIRECT` on the write end, writes an initial token, initializes pid tracking, synchronizes, and forks up to `pipeherd-procs` children. Each child runs the token read/write loop until stop. The parent also participates in token passing, then reads the final token, sets bogo ops from the counter, kills/waits children, closes fds, and optionally reports context-switch metrics from `getrusage`.

State and persistence behavior: state is the pipe token, child pid array, optional rusage snapshots, and bogo counter. There are no filesystem artifacts.

Dependencies and integration points: pipe/fcntl packet mode, fork/kill-many helpers, scheduler and parent-death helpers, optional `getrusage` context-switch fields, stress-ng settings, and `CLASS_PIPE_IO | CLASS_MEMORY | CLASS_OS | CLASS_IPC` registration with `VERIFY_ALWAYS`.

Risks: the single pipe is both input and output for all processes, so fairness and wakeup behavior dominate throughput. Fork failures are recorded as pid `-1` without immediate abort. Verification only checks that the token's check field survives; it does not validate every counter transition.

Test signals: `--pipeherd` should produce bogo count equal to the passed token counter and no check mismatch. Variants include min/max `--pipeherd-procs`, `--pipeherd-yield`, packet mode availability, and context-switch metric availability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pipeherd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pkey.c -->
# sources/test-tools/stress-ng/stress-pkey.c

Purpose: `stress-pkey.c` implements the `pkey` stressor, exercising memory protection key allocation, free, get/set, and `pkey_mprotect` permission changes on a small anonymous mapping.

Important APIs/types/functions: the build requires `HAVE_PKEY_MPROTECT`. `stress_pkey()` maps eight pages, randomly chooses one page per iteration, uses shim wrappers `shim_pkey_alloc()`, `shim_pkey_free()`, `shim_pkey_mprotect()`, `shim_pkey_get()`, and `shim_pkey_set()`, and drives valid and invalid pkey paths.

Control flow: after mmap and sync, each loop exercises invalid allocation flags and rights, invalid frees, tries to allocate a pkey with `PKEY_DISABLE_WRITE` or no rights, falls back to pkey `-1` if allocation fails, applies `PROT_NONE`, read, write, read/write, exec, and combined exec permissions via `pkey_mprotect`, then tests invalid protection flags, unaligned address, address wrap, and zero length. If a real pkey was allocated, it gets and restores rights and frees it.

State and persistence behavior: state is the anonymous eight-page mapping and transient pkey allocations. No files are created. Protection changes are reset by later `pkey_mprotect` calls or by unmapping at deinit.

Dependencies and integration points: Linux/glibc pkey syscall support via shims, mmap helpers, stress-ng sync/state helpers, random page selection, and `CLASS_OS` registration.

Risks: pkey availability depends on CPU, kernel, and libc; ENOSYS during `pkey_mprotect` converts to not-implemented. Using pkey `-1` intentionally falls back toward standard mprotect semantics. Some architectures may reject exec/write combinations differently.

Test signals: direct `--pkey` should bogo-progress or skip as not implemented. Useful checks include pkey exhaustion, ENOSYS fallback, invalid argument tolerance, and that mappings are unmapped after failure and success paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-plugin.c -->
# sources/test-tools/stress-ng/stress-plugin.c

Purpose: `stress-plugin.c` implements the `plugin` stressor, dynamically loading a user-specified shared object, discovering exported `stress_*` functions, and executing selected plugin methods in isolated child processes.

Important APIs/types/functions: the implementation requires `link.h`, libdl, and non-static builds. `stress_plugin_so()` handles `--plugin-so`: it `dlopen()`s the `.so`, obtains the link map, scans dynamic symbol/string tables for `STT_FUNC` symbols named `stress_*`, builds `stress_plugin_methods`, and stores function pointers from `dlsym()`. `stress_plugin_method_all()` calls every discovered method after index 0. `stress_sig_handler()` counts unexpected signals in shared `sig_count`.

Control flow: option parsing loads and indexes the plugin before support checks. `stress_plugin()` validates the selected method, mmaps shared signal counters, synchronizes, and repeatedly forks. Each child applies scheduler settings, disables dumps, drops capabilities, installs signal handlers, disables stack-smash messages, then calls the selected plugin function until it returns nonzero or the run stops. The parent waits, force-kills on wait errors, and reports counted unexpected signals after shutdown.

State and persistence behavior: global state holds the dlopen handle and discovered method table. Shared anonymous memory holds signal counts. Loaded plugin code remains in process until `dlclose()` at deinit. No files are written by this stressor itself.

Dependencies and integration points: ELF dynamic metadata, libdl `dlopen`/`dlinfo`/`dlsym`, stress-ng option callbacks, capability dropping, fork retry, metrics through bogo counters, and `CLASS_CPU | CLASS_OS` registration with a supported callback requiring a plugin.

Risks: symbol-table parsing assumes ELF layout and uses dynamic table pointers from the loaded object. Plugin code is untrusted and can crash or hang children; isolation is by fork, signal handlers, disabled core dumps, and capability drop. `stress_plugin_methods` is freed at deinit, so option/method lookup order matters.

Test signals: `--plugin-so /path/plugin.so --plugin-method all` should discover methods and bogo-progress. Tests should cover missing/invalid `.so`, no `stress_*` symbols, crashing plugin methods with signal counts, static builds, and method-name enumeration.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-poll.c -->
# sources/test-tools/stress-ng/stress-poll.c

Purpose: `stress-poll.c` implements the `poll` stressor, using many pipes and a writer child to exercise `poll`, optional `ppoll`, `select`, and `pselect` with short or randomized timeouts.

Important APIs/types/functions: `pipe_fds_t` stores a pipe pair. `pipe_read()` reads a 16-bit pipe index token and verifies it when global verify is enabled. `stress_poll()` allocates pipe, pollfd, and randomized index arrays, creates pipes, forks a writer, and runs poll/select loops in the parent.

Control flow: the stressor resolves `poll-fds` and `poll-random-us`, allocates arrays, randomizes an index schedule, creates `max_fds` pipes, synchronizes, and forks. The child closes read ends and writes the pipe index as a token to randomly selected write ends. The parent prepares `pollfd` entries, intentionally sets one invalid fd to exercise `POLLNVAL`, and loops through `poll`, `ppoll`, invalid `ppoll` timeout, optional rlimit-lowered `ppoll`, `select`, `pselect`, and `sleep(0)`, draining ready pipes and incrementing bogo ops on readiness.

State and persistence behavior: state is heap arrays, pipe descriptors, a writer child, randomized index schedule, and optional temporary `RLIMIT_NOFILE` changes restored immediately. No files are created.

Dependencies and integration points: `poll.h`, optional select/pselect/ppoll, pipe I/O, rlimit, stress-ng affinity/scheduler/fork helpers, sync barriers, and `CLASS_SCHEDULER | CLASS_OS` registration with optional verification.

Risks: `select` and `pselect` only include fds below `FD_SETSIZE`; high pipe counts can reduce select coverage. The intentionally invalid fd should not make `poll()` fail but should set `POLLNVAL`. Writer child may hit pipe backpressure if readers cannot keep up.

Test signals: `--poll` should bogo-progress. Useful variants include `--poll-fds 1`, max fds, `--poll-random-us`, verify mode, systems without ppoll/pselect, and rlimit behavior for too many fds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-powmath.c -->
# sources/test-tools/stress-ng/stress-powmath.c

Purpose: `stress-powmath.c` implements the `powmath` stressor, repeatedly calling scalar and complex power/root/hypotenuse math functions and verifying deterministic sums against first-run baselines.

Important APIs/types/functions: `stress_powmath_method_t` maps method names to function pointers. Methods include complex `cpow*`/`csqrt*`, scalar `cbrt*`, `hypot*`, `pow*`, and `sqrt*` variants when available. Each method loops `STRESS_POWMATH_LOOPS` times, accumulates a sum, sets a static expected result on first run, and returns true on mismatch beyond `PRECISION` or `PRECISION_L`. `stress_powmath_exercise()` records per-method duration/count metrics.

Control flow: `stress_powmath()` reads `powmath-method`, zeroes metrics, synchronizes, and repeatedly exercises the selected method. The `all` method calls every concrete method in table order. On mismatch, the stressor reports failure and exits the loop. At deinit it emits per-method operation-rate metrics for every method exercised.

State and persistence behavior: state is static per-method first-run result/flag pairs and a static metrics array. No heap, files, or child processes are used. Static baselines persist for the process lifetime.

Dependencies and integration points: libm functions through shim wrappers, optional `complex.h`, target clone optimization, stress-ng method option parsing, bogo counters, and `CLASS_CPU | CLASS_FP | CLASS_COMPUTE` registration with `VERIFY_ALWAYS`.

Risks: first-run baselines make repeatability local to one process and toolchain/libm configuration; floating-point mode changes or CPU-specific math differences can trip verification. Some methods are compiled conditionally, so method indexes depend on available headers/functions. The `all` method reports specific mismatches only for concrete method indexes.

Test signals: `--powmath` and each `--powmath-method` should produce per-function ops/sec metrics and no mismatch. Coverage should include builds with no complex support, long double variants, target-clone-enabled builds, and different CPU/libm combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-powmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prctl.c -->
# sources/test-tools/stress-ng/stress-prctl.c

Purpose: `stress-prctl.c` implements the `prctl` stressor, forking short-lived children that exercise a broad cross-section of Linux `prctl()` and x86 `arch_prctl()` operations, including valid get/set round trips and deliberately invalid argument paths.

Important APIs/types/functions: `stress_arch_prctl()` covers x86-64 CPUID, FS/GS, and XCOMP permission queries/requests. `stress_prctl_syscall_user_dispatch()` optionally installs SIGSYS handling and validates `PR_SET_SYSCALL_USER_DISPATCH` by trapping `kill()`. `stress_prctl_child()` contains the main catalogue: capabilities, child subreaper, dumpability, endian/fp/SVE/SME modes, tagged addresses, MCE kill, `PR_SET_MM`, names, no-new-privs, pdeathsig, ptracer, seccomp query, securebits, THP, perf events, timerslack, speculation control, IO flusher, sched core, memory merge, PAC, VMA naming, auxv, RISC-V/PPC/shadow-stack/timer/futex/indirect-branch/rseq controls, and invalid command checks.

Control flow: the top-level function mmaps one anonymous page for VMA naming, synchronizes, and loops. Each iteration forks a child; the child applies scheduler settings and runs `stress_prctl_child()`, returning failure only for unexpected successes/failures on checked invalid paths. The parent waits and aborts the stressor on nonzero child exit, otherwise increments bogo ops.

State and persistence behavior: state is mostly process attributes inside forked children, so mutations such as no-new-privs, names, timerslack, seccomp queries, speculation settings, and VMA names do not escape the child except where prctl semantics are system/global. The parent owns the anonymous page and unmaps it at deinit.

Dependencies and integration points: Linux `sys/prctl.h`, many UAPI option macros, optional `asm/prctl.h`, optional seccomp headers, signal handlers, environment/auxv discovery, mmap helpers, fork retry, and `CLASS_OS` registration with `VERIFY_ALWAYS`.

Risks: this file is highly kernel-version and architecture dependent; most blocks are compile-time guarded but runtime `EINVAL`/`ENOSYS` is expected for newer or unsupported controls. Some `PR_SET_MM` and capability operations require privileges and are intentionally ignored. Syscall user dispatch temporarily changes signal handling and must disable dispatch before returning from SIGSYS.

Test signals: direct `--prctl` should fork repeatedly without child failure. Useful validation includes kernels with new prctl constants, x86 syscall user dispatch, unprivileged runs where privileged calls fail harmlessly, and unexpected success checks for invalid commands.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prefetch.c -->
# sources/test-tools/stress-ng/stress-prefetch.c

Purpose: `stress-prefetch.c` implements the `prefetch` stressor, benchmarking memory read throughput with no prefetch and many software/architecture-specific prefetch distances and methods.

Important APIs/types/functions: `stress_prefetch_info_t` records offset, count, duration, bytes, and rate for each tested distance. `stress_prefetch_method_t` maps method names to numeric codes, availability probes, and whether prefetch-rate sanity should be checked. Methods include compiler builtin localities, x86 prefetch variants, PPC `dcbt`/`dcbtst`, and ARM `prfm` variants. `stress_prefetch_benchmark()` flushes cache, measures loop overhead, performs the read/prefetch loop, verifies checksum if requested, and updates stats.

Control flow: the stressor selects a method, checks CPU availability, determines L3 cache size from Linux CPU cache details or defaults, maps a buffer plus prefetch-offset slack, fills deterministic 64-bit data and checksum, initializes 128 cache-line offsets, synchronizes, and loops over all offsets. At shutdown it computes per-offset rates, finds the best offset, emits non-prefetch and best-read GB/s metrics, and in verify mode can fail if the best prefetch rate is slower than no prefetch where rate checking is enabled.

State and persistence behavior: state is a private anonymous data buffer and stack metrics array. CPU cache state is intentionally flushed and perturbed. No files are written.

Dependencies and integration points: architecture asm helpers, CPU feature/cache detection, cache flush helper, builtin prefetch shim, stress-ng option parsing, metrics, and `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY` registration with optional verification.

Risks: performance comparisons are noisy and hardware-dependent; the verify rate check is enabled broadly on x86-64 and may be sensitive to virtualization, CPU frequency changes, or cache topology detection. Prefetch availability probes must match actual instruction support to avoid illegal instructions. Offset slack prevents prefetch pointers from running beyond the mapping.

Test signals: `--prefetch` should report non-prefetch and best-read GB/s metrics plus debug best offset. Variants should cover each available `--prefetch-method`, explicit `--prefetch-l3-size`, verify checksum mode, CPUs without a requested instruction, and systems without L3 cache info.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prime.c -->
# sources/test-tools/stress-ng/stress-prime.c

Purpose: `stress-prime.c` implements the `prime` stressor, using GMP to find successive primes from configurable starting values and growth methods.

Important APIs/types/functions: the implementation requires GMP, libgmp, and siglongjmp; MPFR is optional for parsing floating-point start values. `stress_prime_start()` parses `--prime-start` as an `mpz_t` integer or MPFR floating value converted to integer and rejects negatives. `stress_prime_alarm_handler()` stops the stressor on SIGALRM and longjmps after repeated alarms. `stress_prime()` owns GMP values and the prime loop.

Control flow: the stressor initializes `mpz_t` values for start, current prime, and factorial multiplier, reads `prime-method`, `prime-progress`, and `prime-start`, parses the start or defaults to 1, disables progress for nonzero instances, synchronizes, installs the SIGALRM handler, and loops. Each iteration times `mpz_nextprime(value, start)`, advances `start` by factorial multiplication, value+2, power-of-two growth, or power-of-ten growth, increments bogo ops, records digit count, and optionally prints progress every 60 seconds.

State and persistence behavior: state is GMP heap-backed integers, progress timing, bogo counter, and signal longjmp state. On normal exit it clears GMP objects; after signal longjmp it intentionally skips cleanup to avoid heap corruption risks. No files are created.

Dependencies and integration points: GMP, optional MPFR, stress-ng settings/method parsing, signal handling, metrics, sync barriers, and `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE` registration with `VERIFY_NONE`.

Risks: very large starts or multiplicative methods can create enormous GMP values and long `mpz_nextprime` calls. Signal interruption during GMP work is handled conservatively but can leak GMP allocations on longjmp. Floating start parsing depends on MPFR availability.

Test signals: `--prime` should emit primes/sec, primes found, and largest-digit metrics. Useful variants include all `--prime-method` values, integer and scientific-notation `--prime-start`, invalid negative starts, progress output on instance zero, and unsupported builds without GMP.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prime.c -->

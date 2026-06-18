# Group Research: group_560_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_88f9ad8696d9

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strsubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strsubr.c

## Purpose

Implements core private STREAMS subsystem support for illumos: STREAMS queue allocation and teardown, stream-head allocation, module/device attach and detach, multiplexor link/unlink plumbing, service scheduling, syncq/perimeter concurrency, bufcall handling, asynchronous esballoc free processing, signal/poll notification, flow-control backenable, synchronous callback support, and per-netstack STREAMS state.

This is one of the central STREAMS concurrency files. It defines the framework machinery that lets drivers and modules safely push/pop queues, run put/service procedures, defer work to syncqs/taskqs, and change stream topology without stale `q_next`, queue, or syncq references.

## Main Responsibilities

- Initialize STREAMS caches, service threads, kstats, TPI support, and per-netstack STREAMS state in `strinit()`.
- Allocate/free stream heads, queue pairs, syncqs, qbands, and linkinfo records.
- Attach, reopen, detach, insert, and remove STREAMS modules/drivers.
- Convert driver `devflag` MT declarations into queue flags and syncq concurrency flags.
- Maintain per-module/per-driver shared `perdm_t` syncq records for `QPERMOD` and outer perimeter users.
- Implement stream plumbing serialization with `STRPLUMB`, `STPLEX`, `STWOPEN`, `STRCLOSE`, and mated stream locking.
- Implement multiplexor `I_LINK`, `I_PLINK`, `I_UNLINK`, and `I_PUNLINK` support, including cycle detection and persistent-link zone shutdown cleanup.
- Implement syncq entry/exit, exclusive writer upgrade, inner/outer perimeter handling, qwriter callback queues, queued put-message draining, and syncq flushing/propagation during queue removal.
- Schedule queue service routines through taskqs, foreground service draining, and fallback background threads when taskq dispatch fails.
- Implement bufcall wakeups and asynchronous `esballoc` free callback throttling.
- Provide STREAMS signal/error/EOF/wait helper routines for stream heads and sockets.
- Maintain `q_nfsrv`, `QFULL`, `QWANTW`, `QBACK`, and priority-band backenable state.

## Key Entry Points

- `strinit()`
  Initializes STREAMS kmem caches, taskq references, background service threads, kstats, TPI support, and netstack registration.

- `qattach()`, `qreopen()`, `qdetach()`
  Attach/open/reopen/close a STREAMS driver or module queue pair, including syncq setup, module open/close calls, service disabling, syncq flushing, and fmod reference release.

- `setq()`
  Installs `qinit`/module-info values on a queue pair, replaces old syncq topology, creates per-queue/per-module/outer perimeter syncq layout, and updates synchronous STREAMS uio metadata.

- `devflg_to_qflag()`
  Validates STREAMS driver MT flags and converts them to internal `QMTSAFE`, `QPERQ`, `QPAIR`, `QPERMOD`, `QMTOUTPERIM`, `QSYNCSTR`, `_QDIRECT`, and syncq concurrency bits.

- `hold_dm()` / `rele_dm()`
  Create, share, reference, and free `perdm_t` records keyed by `streamtab` for shared per-module or outer-perimeter syncqs.

- `mlink_file()`, `mlink()`, `munlink()`, `munlinkall()`
  Implement multiplexor linking/unlinking, pass-through queue insertion, lower-stream conversion between stream-head and mux queues, LDI linkage registration, mux graph updates, and cleanup.

- `linkcycle()`, `mux_addedge()`, `mux_rmvedge()`, `findlinks()`
  Maintain and query the per-netstack mux graph used to detect cycles and locate link records.

- `insertq()`, `removeq()`
  Change stream topology. These are the critical queue graph mutation paths and use `strlock()`/`strunlock()` plus syncq lists to avoid stale queue references.

- `strlock()` / `strunlock()`
  Acquire the stream locks and optional syncq locks needed to safely mutate `q_next` and related cached pointers.

- `entersq()`, `leavesq()`, `claimq()`, `releaseq()`
  Enter/leave/claim syncqs for open, close, service, callback, and put-side synchronization.

- `outer_enter()`, `outer_exit()`, `qwriter_outer()`, `qwriter_inner()`
  Implement exclusive qwriter semantics for outer and inner perimeters.

- `qfill_syncq()`, `drain_syncq()`, `qdrain_syncq()`, `flush_syncq()`, `propagate_syncq()`
  Queue, drain, flush, or move delayed put messages and qwriter events on syncqs.

- `qenable_locked()`, `queue_service()`, `stream_service()`, `stream_runservice()`, `stream_willservice()`
  Manage service-procedure scheduling, foreground draining, and taskq/fallback handling.

- `wait_svc()`, `wait_sq_svc()`, `disable_svc()`, `enable_svc()`
  Stop service entry and wait for queued/running service or syncq background work to finish.

- `strmakemsg()`, `strmakectl()`, `strmakedata()`, `putiocd()`, `getiocd()`
  Build STREAMS message blocks from user/kernel data and copy ioctl payloads.

- `strwaitq()`, `strwaitbuf()`, `str_cv_wait()`, `strwaitmark()`
  Blocking wait helpers for stream readability/writability, buffer availability, timed waits, and socket mark detection.

- `strsendsig()`, `str_sendsig()`, `strsignal()`, `strsignal_nolock()`, `strhup()`
  Deliver SIGPOLL/SIGURG/terminal signals and poll wakeups for stream events.

- `strsetrerror()`, `strsetwerror()`, `strseteof()`, `strflushrq()`
  Update stream-head error/EOF/read-queue state and wake waiters.

- `freebs_enqueue()`, `esballoc_process_queue()`, `esballoc_enqueue_mblk()`
  Throttle and asynchronously process external-buffer free callbacks.

- `mblk_setcred()`, `mblk_copycred()`, `lso_info_set()`, `lso_info_cleanup()`, `bcksum()`, `freemsgchain()`, `copymsgchain()`
  Message-block credential, offload metadata, checksum, and chain helpers.

## Important Data Structures

- `stdata_t`
  Stream-head state. Major fields used here include `sd_lock`, `sd_reflock`, `sd_qlock`, `sd_wrq`, `sd_flag`, `sd_siglist`, `sd_pollist`, `sd_qhead`, `sd_qtail`, `sd_svcflags`, `sd_refcnt`, `sd_pushcnt`, `sd_mate`, uio/cache hook fields, and stream error state.

- `queue_t`
  STREAMS queue state. This file initializes and mutates `q_next`, `q_qinfo`, `q_flag`, `q_syncq`, `q_nfsrv`, `q_first`, `q_count`, `q_mblkcnt`, band data, syncq-delayed message lists, service timestamps, and fmod references.

- `syncq_t`
  Synchronization queue/perimeter state. Key fields include `sq_lock`, `sq_count`, `sq_flags`, `sq_type`, queued queue/message/event lists, outer perimeter links, service scheduling flags, callback-pending list, `sq_needexcl`, and per-CPU put-count controls.

- `perdm_t`
  Shared per-driver/module syncq record keyed by `streamtab`, used when modules share a `QPERMOD` syncq or outer perimeter.

- `linkinfo_t`, `mux_node`, `mux_edge`, `str_stack_t`
  Multiplexor link records and graph nodes/edges, tracked per netstack for persistent links and cycle detection.

- `sqlist_t`
  Temporary sorted, duplicate-free list of syncqs to lock/wait on during queue removal or stream freezing.

- `strbufcall_t`, `callbparams_t`, `esb_queue_t`
  Support structures for bufcalls, qtimeout/qbufcall callback cancellation, and asynchronous external-buffer freeing.

## Locking and Synchronization

- `sd_lock` protects stream-head flags, signals, error state, monitor waiters, and many stream-head state transitions.
- `sd_reflock` and `sd_refcnt` protect `q_next` walkers using `claimstr()` / `releasestr()`.
- `sd_qlock` protects per-stream service queue lists and `sd_svcflags`.
- `QLOCK(q)` protects queue-local message, service, and flow-control state.
- `SQLOCK(sq)` protects syncq counts, flags, delayed queues/events, outer perimeter links, and callback lists.
- `service_queue` protects fallback background lists for queues, syncqs, and asynchronous frees.
- `strbcall_lock` and `bcall_monitor` protect bufcall queues and callback execution waits.
- `muxifier` serializes multiplexor link/unlink operations globally.
- `perdm_rwlock` protects the global `perdm_list`.
- `strlock()` uses stream locks plus sorted syncq lock lists to avoid deadlock while topology is being changed.
- Outer perimeter operations define a lock ordering between outer `SQLOCK` and inner `SQLOCK`s while setting or dropping `SQ_WRITER`.

## Lifecycle Notes

- Queue allocation returns a read/write pair plus an attached syncq; `setq()` may replace that syncq with per-queue, per-module, or shared outer syncqs.
- `qattach()` allocates queues, configures syncq policy, enters open/close perimeter, calls module/driver open, and relies on successful open to call `qprocson()`.
- `qdetach()` waits for service/syncq activity, calls close when needed, verifies `qprocsoff()` behavior, flushes syncqs, releases fmod references, and frees queues.
- `removeq()` handles the hard case: preventing stale references while unlinking a queue pair, propagating queued messages to the next syncq or freeing them, updating `q_nfsrv`, and maintaining push counts.
- Multiplexor link/unlink temporarily inserts a pass-through queue below the lower stream head and uses `STRPLUMB`/`STPLEX` to block reopen and stream-head entry during conversion.
- Persistent links are undone during netstack/zone shutdown before other stack destroy callbacks run.
- Shared `perdm_t` syncqs are only freed after background syncq service is disabled and drained.

## Error and Edge Handling

- `devflg_to_qflag()` rejects invalid legacy or inconsistent MT flag combinations.
- `mlink_file()` rejects hung-up, FIFO upper, non-mux, self-linked, already-plexed, invalid-major, and cycle-producing links.
- `munlink()` can continue cleanup on close even if the mux rejects `I_UNLINK`, warning and forcing teardown.
- Syncq draining intentionally stops on `SQ_STAYAWAY` or queued events to preserve qwriter ordering.
- `flush_syncq()` is explicitly close-context-oriented and documents assumptions where it mutates queued state without each queue lock.
- `qdrain_syncq()` delays decrementing `q_syncqmsgs` until after put procedure execution to preserve ordering with direct `putnext()` optimizations.
- `strwaitq()` handles nonblocking, timeout, signal/no-signal, delayed-error, and `M_READ` notification semantics.
- `runbufcalls()` limits each pass with an initial event count to avoid indefinite looping under low-memory conditions.
- `freebs_enqueue()` panics early if an external-buffer free callback is missing, because asynchronous execution would otherwise lose useful context.

## External Dependencies

This file depends on core STREAMS headers and stream-head code, VFS/vnode/file state, poll, signals and process groups, taskq, kmem/vmem, netstack zones, LDI, SAD/autopush, TPI, message block allocation/freeing, DDI device flags, and IP checksum support.

## Research Notes

The main correctness risks are concurrency and ordering risks: stale `q_next` references during push/pop/remove, syncq count underflow or missed wakeups, qwriter ordering violations, mux link/unlink races, incorrect `q_nfsrv` flow-control caching, and freeing a shared syncq before fallback/background service has drained. The file’s large comments around `qprocsoff()`, `strlock()`, `removeq()`, syncq draining, and outer perimeters are the key design documentation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strsubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/subr.c

## Purpose

Provides miscellaneous low-level kernel helper routines used across illumos: default device entry points, unused major allocation, device-number conversion, suboption parsing/building, BCD lookup tables, hot patching of kernel text, non-executable-data execution logging, memlist range checking, `on_trap` cleanup, and zone-aware node-name lookup.

## Main Responsibilities

- Supply `nodev()` and `nulldev()` placeholders for device switch tables.
- Allocate fallback/unused major device numbers with `getudev()`.
- Convert between native `dev_t` and 32-bit `dev32_t` encodings.
- Provide 32-bit-only `min`/`max`/`umin`/`umax` compatibility functions.
- Parse and append comma-separated suboptions.
- Export byte-to-BCD and BCD-to-byte lookup tables.
- Patch kernel text instructions by temporarily mapping physical pages writable.
- Report attempted execution from stack or other non-executable user data.
- Test whether an address range is fully contained in a `memlist`.
- Pop current-thread `on_trap()` protection.
- Return global or zone-local nodename.

## Key Entry Points

- `nodev()`
  Returns `ENXIO`, and when called from an LWP stores it in `lwp_error`.

- `nulldev()`
  Returns success for unused device operations.

- `getudev()`
  Allocates a major number above `devcnt` when possible; if exhausted, scans `devnamesp` backward for an unused slot and marks it `DN_TAKEN_GETUDEV`.

- `cmpldev(dev32_t *dst, dev_t dev)`
  Compresses native device numbers to 32-bit encoding, returning failure if major/minor cannot fit.

- `expldev(dev32_t dev32)`
  Expands 32-bit device numbers back to native `dev_t`, preserving `NODEV`.

- `getsubopt(char **optionsp, char * const *tokens, char **valuep)`
  Kernel implementation of `getsubopt(3C)`-style comma/equal option parsing.

- `append_subopt(const char *buf, size_t len, char *str, const char *opt)`
  Appends an option string with comma separation, failing if the target buffer lacks space.

- `hot_patch_kernel_text(caddr_t iaddr, uint32_t new_instr, uint_t size)`
  Hot-patches a 1-, 2-, or 4-byte kernel instruction, handling page-straddling writes and instruction-cache synchronization.

- `report_stack_exec(proc_t *p, caddr_t addr)`
  Logs attempts to execute stack or non-executable user data when logging is enabled.

- `address_in_memlist(struct memlist *mp, uint64_t addr, size_t len)`
  Returns whether `[addr, addr + len)` is contained in one memlist segment.

- `no_trap(void)`
  Pops the top `t_ontrap` frame, with SPARC deferred-error barrier handling.

- `uts_nodename(void)`
  Returns `utsname.nodename` without a current process, otherwise the current zone’s nodename.

## Important Data

- `udevlock`
  Serializes `getudev()` allocation and sparse devnames fallback reuse.

- `byte_to_bcd[256]`, `bcd_to_byte[256]`
  Lookup tables for BCD conversion.

- `devnamesp`, `devcnt`
  Device major namespace inspected by `getudev()`.

- `heap_arena`, `kas`, HAT mappings
  Used by `hot_patch_kernel_text()` to map kernel text pages writable without changing original virtual mapping protections.

## Locking and Synchronization

- `getudev()` uses `udevlock` and individual `devnamesp[i].dn_lock` entries while scanning/reusing sparse major slots.
- `hot_patch_kernel_text()` page-locks the affected kernel address range, maps the backing PFNs into a temporary writable virtual range, writes the instruction, issues memory/icache synchronization, unlocks pages, unloads the mapping, and frees virtual space.
- `no_trap()` mutates only the current thread’s `t_ontrap` stack.

## Error and Edge Handling

- `getudev()` warns when it reuses a sparse major number and returns `DDI_MAJOR_T_NONE` only if no usable number exists.
- `cmpldev()` sets output to `NODEV32` on overflow as a defensive value for callers.
- `append_subopt()` includes room for a comma and the null terminator in its bounds check.
- `hot_patch_kernel_text()` panics on unsupported patch sizes and explicitly supports instruction writes that straddle a page boundary.
- `report_stack_exec()` rate-slows via a short delay after logging.

## External Dependencies

Device switch tables and `devnamesp`, DDI major/minor encodings, VM/HAT/page locking, instruction-cache synchronization, process credentials, zones, `utsname`, `ontrap`, and memlist structures.

## Research Notes

This file is small but low-level. The most sensitive code is `hot_patch_kernel_text()`, where size/alignment assumptions, temporary writable mappings, page-straddling behavior, and icache synchronization are correctness-critical. `getudev()` is also boot-sensitive because it is designed to succeed even when the major-number namespace is sparse or near exhaustion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/subr.c -->
# sources/distributed-fs/coda/coda-src/venus/vproc.cc

## Purpose

`vproc.cc` implements Venus' lightweight process abstraction on top of the Coda LWP and IOMGR libraries. It provides vproc creation, current-thread lookup through LWP rocks, wait/signal/sleep/yield wrappers with transaction-safety checks, retry backoff, volume-entry wrappers for VFS operations, process diagnostics, vnode attribute initialization, and fid-to-kernel-node conversion.

This abstraction underpins daemon threads, workers, reintegrators, resolvers, callback handlers, and foreground VFS call handling.

## Important APIs, Types, and Functions

`VprocInit` initializes the main vproc and retry schedule. `VprocPreamble` runs in each new LWP, finds the owning `vproc`, installs LWP rocks for the vproc and RVM thread data, then calls the vproc's virtual `main`.

`VprocSelf`, `FindVproc`, `vproc_iterator`, and the static `vproc::tbl` provide lookup and iteration.

`VprocWait`, `VprocMwait`, `VprocSignal`, `VprocSleep`, `VprocYield`, and `VprocSelect` wrap LWP/IOMGR primitives. In debug builds, they assert that the current thread is not inside an RVM transaction before context switching.

`VprocSetRetry`, `VprocRetryN`, and `VprocRetryBeta` configure bounded exponential retry sleeps.

The `vproc` constructor, `start_thread`, `main`, destructor, `GetStamp`, and `print` manage lifecycle, LWP startup synchronization, dispatch, diagnostic stamps, and stack reporting.

`vproc::Begin_VFS` resolves the target volume, maps VFS operations to volume modes, applies red/yellow resource-zone throttling, blocks non-ASR processes while ASR is running, and calls `volent::Enter`.

`vproc::End_VFS` exits the volume, handles synchronous resolve, decides whether errors should retry, sleeps for retry/would-block/timeout cases, updates VFS statistics, and releases the volume reference.

`va_init`, `VPROC_printvattr`, and `FidToNodeid` are utility functions for kernel/VFS attribute and node-id handling.

## Control Flow

At startup, `VprocInit` creates the `Main` vproc with a placeholder function. The first `start_thread` initializes LWP and IOMGR and immediately runs `VprocPreamble`; later `start_thread` calls create new LWPs with a startup lock so the new thread can map itself back to its `vproc` object before running `main`.

Derived classes such as reintegrator and resolver pass `NULL` to the base constructor and call `start_thread` after their constructors finish. This avoids virtual dispatch before derived initialization is complete.

For a VFS operation, the caller initializes user context and calls `Begin_VFS`. If no volume is already in context, it obtains one from `VDB`. The operation is mapped to `VM_MUTATING`, `VM_OBSERVING`, or `VM_RESOLVING` unless explicitly supplied. Mutating replicated operations may throttle in yellow/red cache pressure zones by waking the FSO daemon and sleeping until red-zone pressure drops. ASR process-group checks can reject unrelated callers with `EAGAIN`. Finally, `volent::Enter` performs state-machine locking.

`End_VFS` mirrors this. It may set `transition_pending` for synchronous reintegration after successful create/destroy-like mutations, exits the volume, handles `ESYNRESOLVE` by waiting on `ResAwait`, and then processes retryable errors. `ERETRY` uses the configured exponential schedule, `EWOULDBLOCK` uses bounded fixed waits, and `ETIMEDOUT` waits only for users configured to wait forever. It sets `*retryp` when the caller should retry the whole operation.

## State and Persistence Behavior

`vproc` objects are transient process structures, but each has `rvm_perthread_t rvm_data` installed as an LWP rock so RVMLIB can associate transactions with the current lightweight process. The wait/signal/sleep/yield wrappers are important persistence safety gates because they prevent context switches while an RVM transaction is active in debug builds.

`u` is the per-vproc user/VFS context. It stores current volume, uid, operation, volume mode, retry counters, resolve wait block, priority, process group, and timing fields.

The retry schedule is global process state allocated once by `VprocSetRetry`.

## Dependencies and Integration Points

This file depends on LWP, IOMGR, RVMLIB thread data, `local.h`, `user.h`, `venus.private.h`, `venusrecov.h`, `venusvol.h`, and `worker.h`.

It is used by nearly every other Venus subsystem. `vol_daemon.cc`, `vol_reintegrate.cc`, and `vol_resolve.cc` all define `vproc`-based daemons or pooled workers. Volume methods depend on `Begin_VFS` and `End_VFS` for consistent state transitions, retries, and statistics. FSDB pressure control integrates through `FSOD_ReclaimFSOs`, cache block counts, free MLE counts, and CML length thresholds.

## Risks and Edge Cases

Context switching inside RVM transactions is dangerous; the debug checks catch it, but non-debug builds rely on discipline. New code should avoid `VprocWait`, `VprocSleep`, `VprocYield`, or blocking I/O inside recovery transactions.

The startup handshake is delicate. Derived vproc classes must not let the base constructor start the thread before derived fields and virtual methods are ready.

`Begin_VFS` red-zone throttling can stall mutators indefinitely until reintegration or cache reclamation frees resources. This is intentional backpressure but can look like a hang if reintegration is also blocked by tokens or conflicts.

`End_VFS` converts `ERETRY` to `EWOULDBLOCK` if the caller did not provide a retry pointer. Callers must opt into retry loops explicitly.

ASR gating compares process groups. Incorrect pgid setup can either block the ASR itself or allow unrelated mutators during ASR.

## Test Signals

Useful tests include vproc creation and freelist users, `VprocSelf` lookup through rocks, retry beta calculation bounds, debug detection of waits in transactions, `Begin_VFS` mode mapping for representative CODA operations, red/yellow zone throttling, ASR pgid exclusion, `End_VFS` retry handling for `ERETRY`, `EWOULDBLOCK`, `ETIMEDOUT`, synchronous resolve handling for `ESYNRESOLVE`, and VFS statistic updates.

Runtime signals include `PrintVprocs`, per-vproc stamps from `GetStamp`, VFS stats counters, Mariner red/yellow zone messages, wait/retry `eprint` messages, and stack usage in `vproc::print`.

# subset-b-007973

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.hh

Purpose: declares `XrdSysPlugin`, XRootD's utility for loading runtime plugin shared libraries, resolving exported C symbols, optionally comparing plugin and caller version metadata, and controlling library lifetime.

Important APIs/types/functions: public entry points are `getLibrary()`, both `getPlugin()` overloads, `Persist()`, static `Preload()`, and static `VerCmp()`. Constructors support three error-routing modes: no version checking, version checking with `XrdSysError`, and version checking with a caller-supplied error buffer. Private helpers such as `chkVersion()`, `badVersion()`, `DLflags()`, `Find()`, `Inform()`, `libMsg()`, and `msgSuffix()` are implemented in `XrdSysPlugin.cc`. `PLlist` tracks preloaded libraries.

Control flow: callers construct the loader with a library path or null path for the executable image, then call `getPlugin()`. `getPlugin()` implicitly opens the library through `getLibrary()`, finds the requested symbol, optionally finds the `<symbol>Version` companion, and validates compatibility when `myInfo` is present. `Persist()` transfers ownership of the loaded handle by clearing `libHandle`, causing the destructor not to close it.

State and persistence: each instance owns `libPath` storage created by `strdup`, a transient `libHandle`, optional logical name and version pointer, and either an error route or buffer. The static `plList` persists preloaded handles process-wide. `Persist()` intentionally leaks the library handle to the caller/process lifetime.

Dependencies and integration: depends on `XrdVersionInfo` naming conventions from `XrdVersion.hh`, `XrdSysError` for diagnostics, and POSIX dynamic loader behavior implemented in the `.cc`. It is used by plugin stacks such as XrdThrottle to load alternate file system modules.

Risks: the header documents that `Preload()` is not thread-safe and should run before threads start. `Persist()` can cause a later `getPlugin()` on the same object to reopen the library. Version checking depends on plugin authors exporting the exact symbol name with `Version` appended. Constructor comments require path/name storage to persist, but `path` is copied while `lname` is not, so callers must keep `lname` valid.

Test signals: useful checks include loading an existing plugin, missing-library and missing-symbol error paths, optional symbol suppression, `Persist()` lifetime behavior, preload lookup, and clean/dirty version combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.cc

Purpose: implements process privilege switching for Unix-like builds, including temporary effective UID/GID changes through `XrdSysPrivGuard` and permanent privilege drops through `XrdSysPriv::ChangePerm()`.

Important APIs/types/functions: `XrdSysPriv::Restore()`, `ChangeTo()`, `ChangePerm()`, `DumpUGID()`, `XrdSysPrivGuard` constructors/destructor, and `XrdSysPrivGuard::Init()` are the behavioral surface. Local fallback implementations of `setresuid`, `setresgid`, `getresuid`, and `getresgid` cover platforms without native `setres*` APIs. `XSPERR(errno)` maps failures to negative errno-style returns.

Control flow: `ChangeTo()` records the current effective IDs, restores real privileges if needed, then sets effective GID and UID while saving the old effective values. `Restore(saved)` restores either saved or real IDs as effective IDs. `ChangePerm()` locks the global recursive mutex, restores real privileges, sets all real/effective/saved IDs to the new values, verifies the result, and unlocks. `XrdSysPrivGuard::Init()` locks the global mutex, checks current IDs, temporarily changes identity only when running with real UID 0, and leaves the lock held until the guard destructor restores saved privileges.

State and persistence: global state is the process credential set; changes affect all threads, so `fgMutex` serializes operations. `XrdSysPrivGuard` stores only `dum` and `valid` flags, with `dum == false` meaning the guard changed credentials and owns the global mutex until destruction.

Dependencies and integration: uses `XrdSysRecMutex` from `XrdSysPthread.hh`, POSIX UID/GID APIs, `XrdSysPwd` for name-to-UID/GID lookup, and platform compatibility blocks for SGI/AIX/Linux/Cygwin. Windows builds compile no-op success paths for most operations.

Risks: credential state is process-wide, so any unguarded thread doing filesystem or security-sensitive work while a guard is active observes the temporary identity. Several error paths return without unlocking in `DumpUGID()` when `getres*` fails after the mutex is locked. `ChangePerm()` is irreversible by design. Fallback `setres*` emulation cannot provide all saved-ID semantics of native APIs.

Test signals: run only in controlled privilege-aware tests. Validate name constructor with existing and missing users, non-root guard failure, root temporary switch and restoration, permanent drop behavior, and negative errno returns on invalid UIDs/GIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.hh

Purpose: declares the privilege-management API and intentionally restricts most operations to `XrdSysPrivGuard`, encouraging scoped temporary identity changes.

Important APIs/types/functions: `XrdSysPriv` exposes only `ChangePerm()` publicly; `ChangeTo()`, `Restore()`, and `DumpUGID()` are private static helpers available to the friend `XrdSysPrivGuard`. `XrdSysPrivGuard` provides constructors by numeric UID/GID or username, a destructor for restoration, and `Valid()` for status.

Control flow: callers create a guard in a scope, test `Valid()`, perform work under the temporary identity, and rely on the destructor to restore the previous saved credentials. Permanent drops use `XrdSysPriv::ChangePerm()` directly.

State and persistence: declares the static recursive mutex `fgMutex` and debug flag `fDebug`. Guards persist no credential snapshot themselves; the implementation relies on saved UID/GID slots and the global mutex.

Dependencies and integration: includes `sys/types.h` on non-Windows and defines placeholder `uid_t`/`gid_t` on Windows. It depends on `XrdSysPthread.hh` for `XrdSysRecMutex` and is used by code needing privileged open, chown, or user-context filesystem operations.

Risks: the guard API can serialize changes but cannot isolate credentials per thread. `Valid()` must be checked when a switch is required; otherwise code may continue under the original identity. The username constructor depends on passwd lookup availability.

Test signals: compile on Unix and Windows, exercise RAII restore on normal scope exit, and verify failures do not leave the global mutex locked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.cc

Purpose: implements the non-inline portions of XRootD's pthread abstraction: condition-variable timed waits, Apple/GNU semaphore fallback behavior, thread creation helpers, thread numeric IDs, stack sizing, joins, and recursive mutex initialization.

Important APIs/types/functions: `XrdSysThread_Xeq()` is the extern C trampoline. `XrdSysCondVar::Wait()`, `WaitMS()`, and `XrdSysCondVar2::WaitMS()` wrap pthread condition waits. Apple/GNU `XrdSysSemaphore` methods implement a counting semaphore with `XrdSysCondVar`. `XrdSysThread::Run()`, `Num()`, `setStackSize()`, and `Wait()` provide process-wide thread utilities. `XrdSysRecMutex::{InitRecMutex,ReInitRecMutex}` build recursive mutexes.

Control flow: `Run()` allocates `XrdSysThreadArgs`, initializes attributes based on bind/detach/stack options, and launches `XrdSysThread_Xeq()`, which logs start messages, calls the user procedure, deletes the args, and returns the procedure result. Timed waits calculate an absolute `timespec`, retry on `EINTR`, and report timeout as true. The fallback semaphore uses a condition variable, `semVal`, and `semWait` to block or post waiters.

State and persistence: static `XrdSysThread::eDest` controls debug logging and `stackSize` affects future thread creation. Condition variables, semaphores, and mutexes store pthread handles in object state.

Dependencies and integration: wraps pthreads, semaphores, `gettimeofday`, platform-specific thread IDs (`SYS_gettid`, `pthread_mach_thread_np`), and Windows sleep/time headers where needed. This file underpins many XrdSys classes and XrdThrottle's recompute thread.

Risks: `Run()` leaks `XrdSysThreadArgs` if `pthread_create()` fails. `XrdSysThread::Wait()` assumes the joined thread returned an `int *` and dereferences it, which is only safe for legacy callers following that convention. Timed waits use wall-clock time, so clock jumps affect timeout behavior. `InitRecMutex()` destroys `cs` during construction before it has necessarily been initialized by the base constructor path.

Test signals: tests should cover detached and joinable thread creation, stack size forcing/default suppression, timed wait timeout and signal paths, semaphore post/wait fairness, and recursive mutex reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.hh

Purpose: provides XRootD's common synchronization and thread utility wrappers over pthread APIs.

Important APIs/types/functions: declares `XrdSysCondVar`, `XrdSysCondVarHelper`, `XrdSysMutex`, `XrdSysRecMutex`, `XrdSysMutexHelper`, `XrdSysCondVar2`, `XrdSysRWLock`, `XrdSysRWLockHelper`, `XrdSysFusedMutex`, `XrdSysSemaphore`, and static `XrdSysThread`. Thread options are `XRDSYSTHREAD_BIND` and `XRDSYSTHREAD_HOLD`.

Control flow: RAII helper classes lock in constructors or `Lock()` and unlock in destructors. `XrdSysCondVar` optionally owns its mutex depending on `relMutex`; `XrdSysCondVar2` uses a caller-provided mutex. `XrdSysRWLock` wraps read/write locking with optional writer preference on glibc/uClibc. `XrdSysFusedMutex` dispatches to either mutex or rwlock based on construction. `XrdSysSemaphore` uses native semaphores except on Apple/GNU, where the `.cc` condition-variable implementation is used.

State and persistence: objects own pthread mutex/cond/rwlock/semaphore handles. `XrdSysThread` is effectively static and holds only global debug route and stack-size configuration.

Dependencies and integration: includes pthread, signal, semaphore, and Apple clock compatibility code. It is used across XrdSys, XrdOuc, and XrdThrottle for locking, condition signaling, and thread creation.

Risks: wrappers throw string literals or abort in some low-level failure paths rather than returning errors. Some constructors do not check pthread initialization failures. `XrdSysCondVar::Signal()` optionally locks internally only when `relMutex` is set, so callers must match the selected locking model. The glibc writer-preference constructor does not explicitly initialize the rwlock attribute object before setting kind.

Test signals: compile matrix across Linux, macOS, and Windows compatibility branches; stress mutex helpers for double-lock replacement; validate timed locks and timed condition waits; and run thread sanitizer style tests around shared/exclusive lock usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPwd.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPwd.hh

Purpose: wraps thread-safe passwd database lookups in a small object with reusable storage.

Important APIs/types/functions: `XrdSysPwd::Get(const char *)`, `Get(uid_t)`, constructors that immediately call `getpwnam_r()` or `getpwuid_r()`, public `rc`, and private `passwd`/buffer storage.

Control flow: callers either construct and call `Get()` repeatedly or construct with a user/UID and receive a `passwd **`. Each lookup writes into `pwStruct` backed by `pwBuff` and stores the returned pointer in `Ppw` or caller-provided pointer.

State and persistence: returned `passwd *` points into the `XrdSysPwd` instance; it is invalid after the object is destroyed or another lookup overwrites the buffer. No global state is changed.

Dependencies and integration: uses POSIX `<pwd.h>` reentrant functions and is consumed by privilege handling to resolve usernames before temporary credential switches.

Risks: fixed 4096-byte buffer may be too small for unusual passwd entries, yielding an error in `rc`. `Ppw` is not initialized by the default constructor until `Get()` is called. Consumers must not store returned pointers beyond object lifetime.

Test signals: lookup known user, lookup invalid user, lookup by current UID, and simulate/verify `ERANGE` handling on systems with large passwd records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPwd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysRAtomic.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysRAtomic.hh

Purpose: defines `XrdSys::RAtomic`, a relaxed-memory-order atomic wrapper for integral, pointer, and boolean types, plus typedef aliases matching common scalar names.

Important APIs/types/functions: the primary template supports relaxed assignment, conversion, increment/decrement, arithmetic/bitwise compound operations, fetch bit operations, compare-exchange, exchange, and `load()`. The pointer specialization supports pointer arithmetic and `operator->()`. The bool specialization supports assignment, conversion, compare-exchange, exchange, and `load()`.

Control flow: most operators directly call the matching `std::atomic` method with `std::memory_order_relaxed`, returning either the old value for post operations or the computed new value for pre/compound operations. Compare-exchange and exchange allow callers to override memory order.

State and persistence: each wrapper owns one `std::atomic<T>` member. No locking or persistence exists beyond the object's lifetime.

Dependencies and integration: includes `<atomic>`, `<cstddef>`, and `<cstdint>`. XrdThrottle uses it for advisory counters, relaxed wake-order arrays, and per-user EWMA/accounting values where strict ordering is not required.

Risks: relaxed ordering is intentional but dangerous if callers use these atomics for multi-variable synchronization without an external lock. The pointer compare-exchange signatures use `T&` for the expected argument instead of `T*&`, which is suspicious for pointer atomics. Return types for compare-exchange are declared as `T`/`T*` but `std::atomic::compare_exchange_*` returns `bool`; this works only through implicit conversion for scalar specializations and is semantically misleading.

Test signals: compile use cases for all typedefs, pointer arithmetic, volatile overloads, and compare-exchange call sites; add concurrency tests only for atomicity, not ordering guarantees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysRAtomic.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysSemWait.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysSemWait.hh

Purpose: implements a simple counting semaphore with a timed wait primitive using `XrdSysCondVar`.

Important APIs/types/functions: `CondWait()`, `Post()`, blocking `Wait()`, timed `Wait(int secs)`, constructor with initial value and condition ID, and private `semVal`/`semWait` counters.

Control flow: `CondWait()` takes the condition mutex, decrements `semVal` if positive, otherwise returns would-block. `Wait()` decrements immediately when possible or increments `semWait` and waits on the condition variable. `Wait(secs)` is the timed version and decrements `semWait` on timeout. `Post()` signals a waiter if `semWait > 0`; otherwise it increments the available count.

State and persistence: the semaphore count and waiting count live in the object and are protected by `semVar`'s mutex. There is no kernel semaphore or cross-process state.

Dependencies and integration: depends on `XrdSysPthread.hh` for `XrdSysCondVar`. It is a lightweight in-process primitive used where timed semaphore behavior is needed independent of platform semaphore APIs.

Risks: `Wait()` uses an `if` rather than a loop around the condition wait, so spurious wakeups can consume a nonexistent post. `Post()` decrements `semWait` before the waiter has necessarily resumed, which makes accounting sensitive to races and cancellation. Fairness is explicitly not guaranteed.

Test signals: exercise immediate acquire, timeout, post-before-wait, post-after-wait, multiple waiters, and spurious wakeup/cancellation behavior if the platform can inject it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysSemWait.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysShmem.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysShmem.hh

Purpose: provides header-only POSIX shared-memory helpers for creating, opening, mapping, and constructing arrays in shared memory.

Important APIs/types/functions: `XrdSys::shm_error` carries `errcode` and `errmsg`. `XrdSys::shm::create()`, templated `get<T>()`, templated `make_array<T>()`, variadic `make_array<T, Args...>()`, and private `map_shm()` are the core API.

Control flow: `create()` calls `shm_open(O_CREAT|O_RDWR)`, `ftruncate()`, `fstat()`, maps with `mmap(MAP_SHARED)`, closes the descriptor, and returns pointer/size. `get<T>()` opens an existing object, stats, maps, closes, and casts the pointer. `make_array()` creates a block then placement-news `count` objects into the mapped region.

State and persistence: the POSIX shared memory object persists by name until unlinked outside this helper. The mapping persists in the process until callers `munmap()` it; this header provides no unmap/unlink/destroy helper.

Dependencies and integration: uses POSIX `shm_open`, `ftruncate`, `fstat`, `mmap`, `close`, C++ tuples/strings, and placement new. It is suitable for XRootD components that need process-shared counters or tables.

Risks: file descriptors are not closed on several exception paths after `shm_open()`. `create()` ignores `EINVAL` from `ftruncate()`, then trusts the existing object size, which may differ from requested size. The variadic `make_array` uses `std::forward<Args...>(args...)`, which is not the usual forwarding form and may not compile as intended. No destructor calls are provided for objects constructed in shared memory.

Test signals: create/get round trip, existing object resize behavior, mapping failure cleanup, typed array construction, and caller-side `munmap()`/`shm_unlink()` lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysShmem.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysStatx.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysStatx.hh

Purpose: abstracts Linux `statx` and legacy `stat` structures behind `XrdSysStatx` plus conversion helpers.

Important APIs/types/functions: on Linux/GNU, `XrdSysStatx` aliases `struct statx` and `HAVE_STATX` is set. Elsewhere, `XrdSysStatx` contains `stx_mask` and an embedded `struct stat`. `XrdSysStatxHelpers` provides `Stat2Statx()`, `Statx2Stat()`, timestamp conversions, and `GetSize()`.

Control flow: `Stat2Statx()` zeroes and fills statx fields on Linux, including dev/rdev major/minor and atime/mtime/ctime. On fallback platforms it copies `stat` into the embedded member and sets a basic mask. `Statx2Stat()` zeroes `stat` then conditionally copies each statx field based on mask bits; fallback copies the embedded `stat`.

State and persistence: no mutable global state; all operations are stack/buffer conversions.

Dependencies and integration: uses `<sys/stat.h>`, `<fcntl.h>`, `<sys/sysmacros.h>` on Linux, and mask constants such as `STATX_SIZE`. It lets filesystem code consume richer statx data while preserving older API compatibility.

Risks: non-Linux fallback defines only a subset of statx constants. `Statx2Stat()` intentionally leaves fields zero when mask bits are absent, which can surprise callers expecting complete `stat` data. Birth time is defined by mask constant but not converted into `struct stat` because portable `stat` has no uniform birth-time field.

Test signals: conversion round trips for regular files, devices, sparse files, timestamps with nanoseconds, partial statx masks, and fallback compilation on non-Linux targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysStatx.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.cc

Purpose: implements elapsed-time measurement, sleep helpers, midnight calculations, duration formatting, timezone offset calculation, and midnight waiting.

Important APIs/types/functions: implements `Delta_Time()`, static `Midnight()`, several `Report()` overloads, `Snooze()`, `s2hms()`, `TimeZone()`, `Wait()`, and `Wait4Midnight()`.

Control flow: `Reset()` in the header captures `StopWatch`; `Report()` captures now, computes delta into `LastReport`, and overloads add that delta into caller totals as seconds, milliseconds, or `timeval`. `Snooze()` and `Wait()` loop around `nanosleep()` after `EINTR`. `Midnight()` returns local midnight for a timestamp or the next 23:59:59 plus one second special case. `Wait4Midnight()` uses absolute `clock_nanosleep()` except on Apple, where it uses relative sleeps and an NTP-adjustment loop.

State and persistence: each `XrdSysTimer` instance stores `StopWatch` and `LastReport`. Static helpers do not persist state.

Dependencies and integration: uses `gettimeofday`, `time`, `localtime_r`, `mktime`, `gmtime_r`, `nanosleep`, and Windows `Sleep()` compatibility. It is used by scheduling, periodic recompute loops, and coarse elapsed-time accounting, including XrdThrottle.

Risks: wall-clock APIs are sensitive to clock adjustments; elapsed timers would be more stable with monotonic clocks. `TimeZone()` approximates offset by comparing local and GMT hours and can be wrong across DST/date boundaries. `s2hms()` calls `snprintf(buff, blen-1, ...)`, which underuses the provided size and is unsafe for `blen <= 0`.

Test signals: validate duration accumulation, EINTR sleep retry, midnight around DST transitions, formatting buffer boundaries, and `Wait4Midnight()` behavior under clock jumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.hh

Purpose: declares a small stopwatch-style timer class plus static time/sleep utilities used throughout XRootD.

Important APIs/types/functions: `Delta_Time()`, `Midnight()`, `TimeLE()`, `Report()` overloads, `Reset()`, `Seconds()`, `Set()`, `Snooze()`, `s2hms()`, `TimeZone()`, and `Wait4Midnight()`.

Control flow: construct or `Reset()` to establish `StopWatch`; later `Report()` calls compute and accumulate elapsed time since that point. Static helpers cover sleeps, formatting, timezone, and midnight boundaries.

State and persistence: instance state is just two `timeval` values. There is no synchronization, so one timer object should not be shared mutably across threads without external locking.

Dependencies and integration: includes POSIX `sys/time.h` or Windows time/winsock compatibility headers. XrdThrottle uses `XrdSysTimer::Wait()` for recompute pacing.

Risks: API uses wall-clock `timeval` rather than monotonic time. `TimeLE()` compares only seconds and ignores microseconds. Return types use `unsigned long` for current epoch seconds, which is platform-width dependent.

Test signals: constructor reset, `Set()` with a known timestamp, all `Report()` overloads, and cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.cc

Purpose: implements a stream-like tracing formatter that batches message fragments in an `iovec` and emits to `XrdSysLogger`, a callback, or stderr.

Important APIs/types/functions: `SetLogger()` overloads, `Beg()`, `operator<<(XrdSysTrace*)` as `End()`, overloads for bool, char, C strings, `std::string`, signed/unsigned integer widths, pointers, and `Insert(long double)`. The anonymous `ToMsgCB()` converts `iovec` payloads into callback strings.

Control flow: `Beg()` builds a prefix from optional user, instance name, endpoint, and text, locks the trace mutex, initializes the `iovec` array, and resets formatting buffers. Each insertion appends either a pointer to caller/static text or formatted bytes in `dBuff`. Sending `End()` appends a newline, writes through the selected destination, and unlocks.

State and persistence: each trace object owns its mutex, logger pointer, prefix name, formatting state, iovec array, prefix buffer, and data buffer. A single static callback pointer is process-wide. The fallback stderr logger is static in the end operator.

Dependencies and integration: depends on `XrdSysLogger`, `XrdSysFD_Dup`, `XrdSysPthread`, `sys/uio.h`, and trace macros in higher layers. It is the lower-level stream formatter for components not using `XrdOucTrace`.

Risks: message data is capped by 16 iovec entries and 256 formatted bytes; excess fragments silently drop. `operator<<(const char *)` calls `strlen()` and does not handle null. The char hex/octal code appears to have nibble/index mistakes, and `doFmt` state can persist until reset rules fire. The static callback is not protected by a mutex.

Test signals: verify prefix variants, logger/callback/stderr paths, all numeric formatting modes, truncation behavior, null handling expectations, and concurrent trace calls on one object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.hh

Purpose: declares the `XrdSysTrace` stream-style tracing class and simple formatting enum.

Important APIs/types/functions: `Xrd::Fmt` values `dec`, `hex`, `hex1`, `oct`, `oct1`; macro `SYSTRACE`; `Beg()`, `End()`, `SetLogger()`, `Tracing()`, public trace mask `What`, and insertion operators for common scalar types and strings.

Control flow: users call `trace.Beg(...) << pieces << trace.End()` or the macro. The object serializes message construction with `myMutex`, accumulates iovec fragments, and emits when the end sentinel is inserted.

State and persistence: each object keeps trace mask, logger, instance name, formatting state, buffers, and a mutex. It is reusable but not reentrant while a trace is in progress.

Dependencies and integration: includes `sys/uio.h`, `iostream`, `XrdSysPthread.hh`, and forward-declares `XrdSysLogger`. Components can plug into either logger objects or callback-based routing.

Risks: callers can forget to send `End()`, leaving the mutex locked. The macro assumes a variable-like object expression and debug operand formatting. Public `What` has no synchronization, so concurrent trace-mask updates need external ordering.

Test signals: compile all insertion overloads, macro use, runtime mask filtering with `Tracing()`, and callback routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.cc

Purpose: implements process/system utility helpers for executable path discovery, uname formatting, signal-name parsing, and signal blocking.

Important APIs/types/functions: `XrdSysUtils::ExecName()`, `FmtUname()`, `GetSigNum()`, and both `SigBlock()` overloads. The local `sigtab` maps selected signal names to numbers.

Control flow: `ExecName()` lazily computes and caches the executable path using `/proc/self/exe`, `_NSGetExecutablePath`, or Solaris `getexecname()`, returning an empty string on failure. `FmtUname()` formats platform-specific uname fields. `GetSigNum()` strips a leading `sig`/`SIG` and scans the table. `SigBlock()` ignores `SIGPIPE`, optionally installs a coverage SIGTERM dumper, builds a signal set, and calls `pthread_sigmask()`.

State and persistence: `ExecName()` stores a static heap string for process lifetime. Signal handlers and blocked masks affect the calling thread and, when called early, future threads.

Dependencies and integration: uses POSIX signals, pthread signal masks, uname, readlink, platform executable path APIs, and optional gcov support. It should be called early by daemon startup code.

Risks: `ExecName()` is only loosely thread-safe and may leak if raced. Blocking applies to the calling thread; callers must invoke it before thread creation for process-wide effect. Signal mapping is intentionally small and omits common signals such as `USR1`/`USR2`.

Test signals: executable path on Linux/macOS/Solaris, uname formatting per platform, signal lookup with and without `SIG` prefix, invalid signal names, and signal mask verification in child threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.hh

Purpose: declares static utility functions for process metadata and signal setup.

Important APIs/types/functions: `ExecName()`, `FmtUname()`, `GetSigNum()`, `SigBlock()`, and `SigBlock(int)`.

Control flow: callers use the class as a namespace. `SigBlock()` should be called during process startup; other methods are on-demand query helpers.

State and persistence: the header declares no state, but the implementation caches executable name and mutates signal masks/handlers.

Dependencies and integration: includes `sys/types.h` and `sys/stat.h`; implementation pulls platform APIs. Used by daemon bootstrap, diagnostics, and configuration signal handling.

Risks: the API returns raw C strings and integer snprintf results, so callers must manage buffer sizes and null checks. Signal blocking has process design implications if called late.

Test signals: compile consumers, validate buffer truncation handling, and assert expected masks after startup calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.cc

Purpose: provides default behavior shared by extended-attribute implementations: copying attributes between files and setting the message route.

Important APIs/types/functions: `XrdSysXAttr::Copy()` and `XrdSysXAttr::SetMsgRoute()` are implemented here; concrete plugins provide `Del()`, `Free()`, `Get()`, `List()`, and `Set()`.

Control flow: when no attribute name is supplied, `Copy()` calls `List(getSz=1)`, allocates a buffer larger than the reported maximum value size, loops over all returned attributes, gets each value, sets it on the output, frees the list, and returns the last status. For a single attribute, it first probes size via `Get(Aval=null, Avsz=0)`, allocates exactly that size, gets the value, sets it on the target, and treats `-ENOTSUP` as a successful no-op.

State and persistence: no persistent state besides the inherited `Say` pointer. Memory for copy buffers is temporary; `List()` ownership is released through the virtual `Free()`.

Dependencies and integration: includes `XrdSysError` and `XrdSysXAttr.hh`. The default copy routine works with native and plugin xattr backends.

Risks: in the all-attributes path, `malloc(maxSz)` is not checked before use. The loop passes `aNow->Vlen` to `Set()` even when `Get()` returned a different byte count. Missing or unsupported attributes are considered success, which is deliberate but may hide configuration mistakes.

Test signals: copy all attributes, copy one attribute, no xattr support, zero-length attributes, allocation failure injection, and plugin `List()`/`Free()` ownership correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.hh

Purpose: defines the abstract extended-attribute interface used by XRootD native and plugin xattr providers.

Important APIs/types/functions: `XrdSysXAttr::AList` describes linked attribute names and value lengths. Virtual API includes default `Copy()`, pure `Del()`, `Free()`, `Get()`, `List()`, `Set()`, and default `SetMsgRoute()`. Factory typedefs are `XrdSysGetXAttrObject_t` and `XrdSysAddXAttrObject_t`.

Control flow: consumers call `List()` to enumerate, `Get()`/`Set()`/`Del()` to operate on one attribute, and `Copy()` to copy one or all attributes. Plugins can be loaded via `ofs.xattrlib`; add-style plugins can wrap an existing active implementation.

State and persistence: each implementation may store backend state; base class stores only `XrdSysError *Say`. `AList` allocations are implementation-owned and must be released by `Free()`.

Dependencies and integration: forward-declares `XrdOucEnv` and `XrdSysError`. The header documents expected extern C factory symbols and version declaration with `XrdVERSIONINFO`.

Risks: `AList` uses a flexible-array-style `Name[1]`, so implementations must allocate enough storage and preserve alignment. API returns negative errno values, not positive errno. File descriptors are optional and implementations must correctly choose fd-based or path-based syscalls.

Test signals: plugin load/factory ABI, list/free memory checks, fd and path variants, binary attribute values, `isNew` semantics, unsupported filesystem behavior, and wrapper plugin chaining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.cc -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.cc

Purpose: implements a custom shared/exclusive lock with semaphore-based wait queues and anti-starvation toggling.

Important APIs/types/functions: `XrdSysXSLock::~XrdSysXSLock()`, `Lock(XrdSysXS_Type)`, and `UnLock(XrdSysXS_Type)` implement the behavior declared in the header.

Control flow: `Lock()` serializes on `LockContext`; shared lock requests can join existing shared holders only when no exclusive waiter exists, otherwise wait on `WantShr`; exclusive requests wait on `WantExc` until `cur_count` reaches zero. `UnLock()` validates state and optional usage, decrements `cur_count`, then wakes either one exclusive waiter or all shared waiters based on `exc_wait`, `shr_wait`, and `toggle`.

State and persistence: mutable state includes current mode/count, exclusive/shared waiter counts, a toggle bit, a mutex, and two semaphores. No state persists outside the object.

Dependencies and integration: uses `XrdSysHeaders.hh`, `XrdSysXSLock.hh`, `XrdSysMutex`, and `XrdSysSemaphore`. It predates the standard/shared pthread rwlock wrapper and may be used by legacy code needing explicit fairness behavior.

Risks: destructor aborts if destroyed while active or with waiters. Unlock misuse throws string literals after writing to `std::cerr`. The waiting counts are decremented by the unlocker before the waiter resumes, so cancellation or unexpected wakeups can corrupt accounting. No upgrade/downgrade support exists.

Test signals: multiple readers, writer exclusion, writer preference once waiting, alternating reader/writer fairness, invalid unlock mode, unlock inactive lock, and destruction while idle only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.hh -->
# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.hh

Purpose: declares the legacy shared/exclusive lock class and its usage enum.

Important APIs/types/functions: `XrdSysXS_Type` values are `xs_None`, `xs_Shared`, and `xs_Exclusive`. `XrdSysXSLock` exposes `Lock()` and `UnLock()`, and stores mode/count/waiter state plus mutex and semaphore wait channels.

Control flow: callers request either shared or exclusive access, then unlock with either the matching type or `xs_None` to skip mode validation. Multiple shared holders are allowed; one exclusive holder is allowed; upgrades and downgrades are unsupported.

State and persistence: object-local counters and wait queues represent all state. No static state or OS rwlock is used.

Dependencies and integration: includes `XrdSysPthread.hh` for mutex/semaphore abstractions. It is a compatibility synchronization primitive for older XRootD code.

Risks: no RAII helper is provided in this header, so exception paths can leak locks. `UnLock(xs_None)` weakens misuse detection. Destruction with waiters aborts the process.

Test signals: API-level lock/unlock cycles, shared compatibility, exclusive exclusion, and negative misuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdThrottle/CMakeLists.txt

Purpose: defines the `XrdThrottle-${PLUGIN_VERSION}` module target and its install rule.

Important APIs/types/functions: CMake creates a `MODULE` library from XrdThrottle sources plus `src/XrdOfs/XrdOfsFS.cc`, links privately to `XrdServer` and `XrdUtils`, adds the vendored `inih` include directory, and installs the module into `${CMAKE_INSTALL_LIBDIR}`.

Control flow: during configure/generate, the target name is computed from `PLUGIN_VERSION`; during build, listed sources are compiled into a loadable plugin rather than a normal shared library.

State and persistence: build artifacts are the module library and installed plugin file. No runtime state.

Dependencies and integration: integrates with the main XRootD CMake project, XrdOfs, XrdSfs, XrdUtils, XrdServer, and INIReader from `vendor/inih`.

Risks: adding `XrdOfsFS.cc` directly means the plugin target depends on OFS implementation internals. Missing `PLUGIN_VERSION` or vendor include layout breaks target naming/compilation. Source list must stay synchronized with new throttle headers and implementation files.

Test signals: configure/build the target, inspect module symbol exports, install path verification, and plugin loading in an XRootD runtime test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdOssThrottleFile.cc -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdOssThrottleFile.cc

Purpose: implements the newer OSS-layer throttle wrapper, allowing throttling after OFS authorization has made the authenticated user available.

Important APIs/types/functions: anonymous `File` derives from `XrdOssWrapDF` and wraps open/close, reads, writes, paged reads/writes, vector reads, and AIO shims. Anonymous `FileSystem` derives from `XrdOssWrapper`, configures `XrdThrottleManager`, and wraps `newFile()`. Exported `XrdOssAddStorageSystem2()` is the OSS plugin factory with `XrdVERSIONINFO`.

Control flow: the factory constructs `FileSystem`, calls `Configure()`, sets environment flag `XrdOssThrottle=1`, and returns it. `FileSystem` initializes the manager, loads configuration, applies config, and optionally attaches g-stream monitoring. Each wrapped file derives user info from `env.secEnv()` on open, checks open/connection limits, delegates to the wrapped OSS file, and closes manager accounting on failure or close. I/O methods call `DoThrottle()`, which applies data/IOPS shares, starts an RAII I/O timer, fails with `-EMFILE` when concurrency wait times out, and then invokes the wrapped operation.

State and persistence: `FileSystem` owns the wrapped OSS, log, trace, and throttle manager. Each `File` stores wrapped file ownership, user string, hashed UID, and references to manager/trace/log. Environment flag persists in `XrdOucEnv` to prevent OFS-layer double stacking.

Dependencies and integration: depends on XrdOss wrapper APIs, `XrdOucGatherConf`, `XrdSfsAio`, `XrdThrottleConfig`, `XrdThrottleManager`, `XrdThrottleTrace`, and XRootD plugin ABI. It complements the older OFS-layer wrapper in `XrdThrottleFileSystemConfig.cc`.

Risks: `Close()` always calls `CloseFile()` even if open accounting did not succeed or close is repeated. AIO is forced synchronous by doing the operation and then calling done callbacks. `getFD()` and mmap are disabled, which may affect sendfile/mmap optimizations. `DoThrottle()` returns `int` even when wrapping `ssize_t` operations.

Test signals: OSS plugin load, no double OFS stacking, open-limit failures, close rollback on open failure, read/write throttling, AIO callback behavior, g-stream monitoring, and sendfile/mmap expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdOssThrottleFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottle.hh -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottle.hh

Purpose: declares the OFS/SFS-facing throttle plugin classes that wrap an existing `XrdSfsFileSystem` and per-file `XrdSfsFile` objects.

Important APIs/types/functions: `XrdThrottle::File` overrides open, close, checkpoint, fctl, read/write variants, paged I/O, sync, stat, truncate, checksum info, and `SendData()`. `XrdThrottle::FileSystem` overrides SFS filesystem operations, mostly pass-through, plus static `Initialize()` and private `Configure()`. `unique_sfs_ptr` abstracts unique ownership for C++11 or pre-C++11 builds.

Control flow: `FileSystem::newFile()` wraps an underlying SFS file in `File`. `File::open()` identifies the user, prepares load-shed opaque data, increments open accounting, and delegates open. Data-transfer methods throttle then delegate. `FileSystem::Initialize()` constructs/configures the singleton plugin instance.

State and persistence: `File` stores open flag, wrapped file, hashed UID, load-shed opaque, connection ID, user, manager reference, and error route. `FileSystem` stores singleton state, logger/error route, trace object, config filename, underlying filesystem pointer, initialized flag, manager, and version info pointer.

Dependencies and integration: depends on `XrdSfsInterface.hh`, `XrdVersion.hh`, `XrdSysError`, `XrdThrottleTrace`, and `XrdThrottleManager`. It is exported through factory functions in `XrdThrottleFileSystemConfig.cc`.

Risks: many operations are pass-through and only file data-transfer paths are throttled. Sendfile and mmap are intentionally disabled because the plugin cannot observe bytes read through those paths. The singleton `FileSystem` initialization is documented as not thread-safe in the implementation.

Test signals: SFS factory load, wrapping of all file operations, data path throttling, pass-through metadata operations, disabled fd/mmap paths, singleton reuse, and version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottle.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.cc

Purpose: parses throttle configuration directives from the XRootD config file into a `Configuration` object.

Important APIs/types/functions: `Configuration::Configure()`, parsers `xmaxopen()`, `xmaxconn()`, `xmaxwait()`, `xthrottle()`, `xloadshed()`, `xtrace()`, and `xuserconfig()`. The `TS_Xeq` macro dispatches recognized directive names.

Control flow: `Configure()` opens the config file, attaches it to `XrdOucStream`, captures throttle plugin config lines, then loops over directive names. `throttle.fslib` is handled inline; other known directives call parser methods. Numeric values are parsed with `XrdOuca2x`. `xthrottle()` scans option pairs for data rate, IOPS rate, recompute interval, and concurrency. `xloadshed()` requires a host and parses optional port/frequency. `xtrace()` accumulates trace flags with support for negation and off/none.

State and persistence: parsed settings persist in `Configuration` members until consumed by `XrdThrottleManager::FromConfig()` or filesystem loading. It does not write files or mutate global runtime state.

Dependencies and integration: depends on `XrdOucStream`, `XrdOuca2x`, `XrdOucEnv`, `XrdSysError`, trace constants, and config syntax used by both OSS and OFS throttle wrappers.

Risks: parser functions log missing mandatory values but do not always immediately return after the log before using `val`, which can lead to null handling issues. `TS_Xeq` resets `NoGo` to zero for every nonmatching directive, so unknown directives are ignored by this plugin. `xloadshed()` defaults port/frequency to zero even though comments mention defaults; loadshed is applied only when all three are positive later.

Test signals: parse complete config, missing values, bad numeric ranges, trace flag accumulation/negation, unknown options, user config path, and fslib override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.hh

Purpose: declares the throttle configuration container and parser interface.

Important APIs/types/functions: `Configuration` constructor accepts `XrdSysError` and optional `XrdOucEnv`; `Configure()` populates state; getters expose filesystem library, loadshed host/port/frequency, max open files, max active connections, max wait, throttle concurrency/data/IOPS/recompute interval, trace levels, and per-user config path.

Control flow: users instantiate `Configuration`, call `Configure(config_file)`, then pass it to manager/filesystem code. Private parser methods handle each directive family.

State and persistence: defaults are `libXrdOfs.so`, no loadshed, unlimited max open/connection if `-1`, max wait 30 seconds, no data/IOPS/concurrency throttle if `-1`, recompute interval 1000 ms, trace off, and no user config file.

Dependencies and integration: forward-declares `XrdOucEnv`, `XrdOucStream`, and `XrdSysError`. Consumed by both OSS and OFS throttle setup.

Risks: comments for connection limits use `-1` as unset, while manager's per-user `GetUserMaxConn()` uses `0` to mean global/default; conversions must remain consistent. All getters return raw primitive/string values without validation after parse.

Test signals: default construction, each directive parser via full `Configure()`, and manager `FromConfig()` consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFile.cc -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFile.cc

Purpose: implements the SFS file wrapper that enforces load shedding, bandwidth/IOPS throttling, concurrency throttling, and open-file accounting around data operations.

Important APIs/types/functions: `File::open()`, `close()`, `fctl()`, `getMmap()`, read/write/paged/AIO variants, `SendData()`, and pass-through methods for checkpoint/sync/stat/truncate/checksum info. Macros `DO_LOADSHED` and `DO_THROTTLE` centralize pre-I/O checks.

Control flow: `open()` maps client identity to user/UID, prepares load-shed opaque data, calls `OpenFile()`, delegates to underlying SFS open, and rolls back accounting on failure. `close()` clears `m_is_open`, closes accounting, and delegates close. Data-transfer methods execute load-shed check, apply share throttling, start an I/O timer, fail with `SFS_ERROR`/`EMFILE` when concurrency wait times out, then call the wrapped operation. AIO methods perform synchronous wrapped calls and immediately complete callbacks.

State and persistence: per-file state includes open flag, wrapped SFS file, user identity, hashed UID, prepared load-shed opaque string, connection ID, and references to throttle manager/error route. Open counters persist in the manager until `close()` or destructor rollback.

Dependencies and integration: depends on `XrdSfsAio`, security entity attributes, and `XrdThrottle.hh`. It is created by `FileSystem::newFile()`.

Risks: macros rely on member names and local `error`, making control flow hard to audit. Destructor rolls back only if `m_is_open`, so any accounting mismatch outside normal open/close can persist. AIO is no longer asynchronous. Disabling `SFS_FCTL_GETFD` and mmap can reduce performance or change client behavior.

Test signals: open success/failure accounting, close idempotence, all throttled I/O paths, load-shed redirect, max wait timeout mapping to `EMFILE`, AIO completion, and pass-through metadata methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystem.cc -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystem.cc

Purpose: implements SFS filesystem wrapper methods, forwarding metadata/control operations to the underlying filesystem and wrapping new files with throttle-aware `File` objects.

Important APIs/types/functions: `newDir()`, `newFile()`, `chksum()`, `chmod()`, `Connect()`, `Disc()`, `EnvInfo()`, `exists()`, `FAttr()`, `fsctl()`, `getChkPSize()`, `getStats()`, `getVersion()`, `gpFile()`, `mkdir()`, `prepare()`, `rem()`, `remdir()`, `rename()`, `stat()` overloads, and `truncate()`.

Control flow: every method except `newFile()` and `getVersion()` delegates directly to `m_sfs_ptr`. `newFile()` obtains a raw file from the underlying filesystem, wraps it in `unique_sfs_ptr`, constructs an `XrdThrottle::File`, and returns it. `getVersion()` reports `XrdVERSION`.

State and persistence: uses `m_sfs_ptr`, `m_throttle`, and `m_eroute` from the `FileSystem` instance; this file adds no state. Wrapped files own underlying file objects after construction.

Dependencies and integration: includes `XrdOfs/XrdOfs.hh` and `XrdThrottle.hh`. It is the pass-through layer that keeps the throttle plugin compatible with the full SFS interface.

Risks: null `m_sfs_ptr` would crash all pass-through methods, so configuration must complete before use. Only files are wrapped; directories and metadata operations are not throttled. Ownership transfer around pre-C++11 `auto_ptr` must be compiled carefully.

Test signals: wrap creation, null underlying `newFile()` handling, pass-through behavior for each SFS method, and version string reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystemConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystemConfig.cc

Purpose: provides the OFS/SFS plugin factory and initialization/configuration path for the throttle filesystem wrapper.

Important APIs/types/functions: local `LoadFS()`, `XrdThrottle::XrdSfsGetFileSystem_Internal()`, exported `XrdSfsGetFileSystem()` and `XrdSfsGetFileSystem2()`, `FileSystem::Initialize()`, constructor/destructor, and `FileSystem::Configure()`. Version symbols are declared with `XrdVERSIONINFO`.

Control flow: factory calls internal function; if the OSS throttle flag is set, it logs a compatibility warning and returns the native filesystem to avoid double stacking. Otherwise `Initialize()` creates/reuses the singleton, sets config/logging, calls `Configure()`, initializes the manager, and marks the instance initialized. `Configure()` parses throttle config, applies manager settings and trace mask, loads the underlying filesystem through `LoadFS()` or uses `native_fs`, exports `XRDOFSLIB`, attaches optional g-stream monitoring, and copies feature flags.

State and persistence: `FileSystem::m_instance` is a process-wide singleton. The loaded filesystem plugin handle is persisted via `XrdSysPlugin::Persist()`. Environment variable `XRDOFSLIB` is exported. Manager recompute thread starts during initialization.

Dependencies and integration: depends on `XrdSysPlugin`, `XrdSysLogger`, `XrdOucEnv`, `XrdOucStream`, `XrdThrottleConfig`, and the XrdSfs plugin ABI. It can load the default OFS directly or a custom `throttle.fslib`.

Risks: file notes that nothing is thread-safe; singleton initialization should happen during single-threaded startup. If `XrdOssThrottle` is loaded, current behavior is warning and bypass for backward compatibility but may become failure later. `LoadFS()` persists the dynamic library and assumes factory ABI compatibility. Reconfiguration after first initialization is ignored.

Test signals: plugin factory symbols, default OFS load, custom fslib load, native filesystem path, OSS-throttle bypass, failed config handling, feature propagation, and environment export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystemConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.cc -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.cc

Purpose: implements the throttle manager: user-aware fair-share data/IOPS throttling, I/O concurrency throttling, open-file/active-connection limits, load shedding, per-user limit loading, and g-stream monitoring.

Important APIs/types/functions: public behavior includes `FromConfig()`, `Init()`, `GetUserInfo()`, `OpenFile()`, `CloseFile()`, `Apply()`, `StartIOTimer()`, load-shed helpers, `LoadUserLimits()`, `ReloadUserLimits()`, and `GetUserMaxConn()`. Internal algorithms are `GetShares()`, `StealShares()`, `Recompute()`, `RecomputeInternal()`, `UserIOAccounting()`, `ComputeWaiterOrder()`, `NotifyOne()`, `StopIOTimer()`, `Waiter::Wait()`, and `GetTimerListHash()`.

Control flow: `FromConfig()` applies global limits, throttle rates, trace mask, loadshed target, and optional per-user INI limits. `Init()` sizes per-user share vectors, initializes waiter manager pointers, bootstraps each hashed user with initial shares, and starts the recompute thread. Data operations call `Apply()` to consume primary shares, secondary shares, and stealable idle shares; if unsatisfied, they wait on `m_compute_var` until the recompute loop refills shares. Operations then call `StartIOTimer()`, which increments active I/O, blocks on per-user waiters when the concurrency limit is exceeded, and returns an RAII timer. Timer destruction calls `StopIOTimer()`, updates I/O accounting, decrements active count, and wakes an eligible waiter. The recompute thread periodically garbage-collects idle connection counters, refills shares, recomputes waiter wake order from EWMA concurrency, emits monitoring JSON, broadcasts share waiters, and sleeps for the configured interval.

State and persistence: fixed logical user slots (`m_max_users == 1024`) are indexed by hash of username. Share vectors hold primary and secondary byte/op allocations. File/connection maps track open counts by entity and active thread IDs under `m_file_mutex`. Per-user limits live in an atomically swapped `m_user_limits` map protected by `std::shared_mutex`. I/O state includes active counters, total counters, timer linked lists sharded by CPU, waiter arrays, wake-order arrays, EWMA concurrency, and g-stream handle. The recompute thread runs for process lifetime; destructor intentionally does not stop it.

Dependencies and integration: uses `XrdSysThread`, `XrdSysTimer`, XrdSys atomics/relaxed atomics, `XrdSecEntity` and entity attributes for user naming, `INIReader` for per-user config, `XrdXrootdGStream` for monitoring, and throttle trace macros. It is shared by both OFS and OSS throttle wrappers.

Risks: user IDs are hash buckets, not unique identities, so unrelated users can share throttling/accounting. `StealShares()` loop condition is written `i % m_max_users == uid`, which prevents the intended full scan for most starts and should be reviewed. `ComputeWaiterOrder()` divides by `users_with_waiters` and `shares_sum`; current call patterns may avoid zero users for some paths but edge cases need testing. `std::default_random_engine()` without a varying seed makes wake-order shuffling deterministic per process. Open connection accounting uses thread ID as connection proxy, which may not match actual client connection lifecycle under all schedulers. `CheckLoadShed()` uses `rand()` and frequency comparison that appears off by one for 100%.

Test signals: manager unit tests should cover share refill, byte/IOPS blocking and wakeup, secondary share stealing, concurrency timeouts, RAII timer removal from timer lists, EWMA wake ordering, open-file and active-connection limits, per-user exact/wildcard/catch-all limits, user identity precedence (`token.subject`, `request.name`, `name`), loadshed opaque handling, and g-stream JSON insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.cc -->

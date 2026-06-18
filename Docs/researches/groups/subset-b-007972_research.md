# Research: subset-b-007972

This grouped report covers the requested XRootD XrdSut and XrdSys files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.hh -->
## sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.hh

Purpose: declares `XrdSutRndm`, the security utility random-bit provider used by SUT code to produce random buffers, random strings, unsigned integers, and random tags.

Important APIs/types/functions: `static bool fgInit` tracks one-time initialization; the constructor lazily invokes `Init()`; `Init(bool force=false)` initializes or reinitializes the provider; `GetBuffer(int len, int opt=-1)` returns a newly supplied random byte buffer; `GetString(int opt, int len, XrdOucString&)` and `GetString(const char *copt, int len, XrdOucString&)` fill an `XrdOucString`; `GetUInt()` returns a random unsigned integer; `GetRndmTag()` fills a random tag.

Control flow: this header only declares the interface, but its constructor contract makes object creation a lazy initializer. Callers then use static methods directly.

State and persistence: state is process-local static state only. No persistent storage is declared here. Returned buffers likely transfer ownership to callers, so implementation and callers must agree on allocation/freeing.

Dependencies and integration: includes `XrdSutAux.hh` and forward-declares `XrdOucString`. It is consumed by SUT authentication/security helpers needing entropy.

Risks: weak initialization, non-thread-safe `fgInit` updates, ambiguous buffer ownership, and option parsing differences between integer and string options are the main risks.

Test signals: tests should cover lazy initialization, forced reinitialization, buffer length and null handling, string option variants, uniqueness/distribution smoke checks, and concurrent initialization calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutTrace.hh -->
## sources/distributed-fs/xrootd/src/XrdSut/XrdSutTrace.hh

Purpose: provides compile-time-controlled tracing macros for XrdSut code.

Important APIs/types/functions: declares external `XrdOucTrace *sutTrace`; defines `QTRACE(act)`, `PRINT(y)`, `TRACE(act,x)`, `DEBUG(y)`, and `EPNAME(x)` when `NODEBUG` is not set. In debug-enabled builds, `QTRACE` checks `sutTrace->What` against `sutTRACE_<act>` masks, and `PRINT` formats through `sutTrace->Beg(epname)`, `std::cerr`, and `sutTrace->End()`.

Control flow: callers place `EPNAME("...")` in a function and call `TRACE`/`DEBUG`; macros short-circuit when tracing is disabled or the mask is absent. In `NODEBUG` builds all macros compile away.

State and persistence: the only state is global pointer `sutTrace`, owned elsewhere, plus static function-local endpoint names emitted by `EPNAME`.

Dependencies and integration: depends on `XrdOucTrace.hh`, `XrdSutAux.hh`, and `XrdSysHeaders.hh` for iostream compatibility. It integrates with SUT diagnostic masks from `XrdSutAux.hh`.

Risks: macros rely on a visible `epname`; stream expressions are evaluated only under tracing, so side effects in trace expressions vary by build/mask. Global `sutTrace` lifetime and thread safety are external assumptions.

Test signals: build both with and without `NODEBUG`; verify mask gating, endpoint names, no evaluation when disabled, and concurrent trace formatting through the shared trace object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdSys/CMakeLists.txt

Purpose: attaches the XrdSys implementation and public/private support headers to the `XrdUtils` target.

Important APIs/types/functions: uses `target_sources(XrdUtils PRIVATE ...)` to include atomics, directory wrappers, error translation, extended attributes, CLOEXEC FD helpers, fallocate compatibility, IO event pollers, logging, platform portability, plugin loading, privilege/thread/timer/trace/util/xattr/lock helpers, and platform-specific `.icc` implementations.

Control flow: CMake configuration does not contain conditional logic here; platform selection happens inside source files with preprocessor directives. This list is the build integration point that ensures inline `.icc` files and headers are visible to the target source graph.

State and persistence: no runtime state. Its persistent effect is build graph membership for `XrdUtils`.

Dependencies and integration: integrates the XrdSys module into the larger XRootD build. The listed files expose utility services used by higher-level Xrd, XrdCl, XrdOss, and authentication code.

Risks: missing a `.cc`, `.hh`, or `.icc` here can cause unresolved symbols or platform-specific missing code. Adding headers as private sources helps IDE visibility but does not install them by itself.

Test signals: configure and build on Linux, macOS, BSD/Solaris where applicable; verify `XrdUtils` exports expected symbols and that platform-specific `.icc` selections compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysAtomics.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysAtomics.hh

Purpose: defines legacy atomic-operation macros and C++11 atomic compatibility macros for low-level XrdSys code.

Important APIs/types/functions: `AtomicAdd`, `AtomicFAdd`, `AtomicCAS`, `AtomicDec`, `AtomicFAZ`, `AtomicFZAP`, `AtomicGet`, `AtomicInc`, `AtomicSub`, `AtomicFSub`, `AtomicZAP`, and `AtomicRet` map either to GCC `__sync_*` builtins under `HAVE_ATOMICS` or to caller-supplied locking via `AtomicBeg(Mtx)`/`AtomicEnd(Mtx)` and non-atomic expressions otherwise. `CPP_ATOMIC_TYPE`, `CPP_ATOMIC_LOAD`, and `CPP_ATOMIC_STORE` map to `std::atomic` only under C++11 or later.

Control flow: compile-time feature macros select true atomic builtins versus lock-assisted/non-atomic fallbacks.

State and persistence: no state is owned here. The macros mutate caller-owned variables and, in fallback mode, caller-owned mutexes.

Dependencies and integration: optionally includes `<atomic>`. Used by event polling and other utility code requiring portable counters or flags.

Risks: macro semantics are fragile. Fallback `AtomicCAS` does not return a boolean like the builtin version, `AtomicFAZ` expands to two statements, and fallback use is only safe if callers actually bracket access with locks. C++03 `CPP_ATOMIC_*` removes undefined-behavior protection.

Test signals: compile with and without `HAVE_ATOMICS`; exercise expression contexts, assignment contexts, compare-and-swap expectations, and fallback lock paths under thread sanitizer where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysAtomics.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.cc

Purpose: implements `XrdSysDir`, a small cross-platform directory iteration wrapper.

Important APIs/types/functions: constructor opens a directory handle; destructor closes it; `nextEntry()` returns the next entry name or null; `isValid()` and `lastError()` are declared in the header. Unix uses `opendir`, `readdir`, and `closedir`. Windows uses `FindFirstFile`, `FindNextFile`, and `FindClose`.

Control flow: construction validates the path, opens the handle, and stores `errno`/`EINVAL`/`ENOTDIR` on failure. `nextEntry()` clears `lasterr`, validates the handle, calls platform iteration, and records only real errors.

State and persistence: per-object `void *dhandle` and `int lasterr`; no persistent storage. Returned `char *` points into platform-owned directory-entry storage and must be copied by callers that need it later.

Dependencies and integration: depends on `XrdSysDir.hh`, POSIX `dirent.h`, Windows APIs, `cerrno`, and `cstring`. Used wherever XrdSys needs portable directory traversal without exposing platform conditionals.

Risks: Windows constructor calls `FindFirstFile(path)` without appending a wildcard, so behavior depends on passed path shape. Returned pointer lifetime is short. `errno` is checked for `EBADF` only on Unix end-of-directory.

Test signals: valid/invalid paths, empty directories, permission-denied directories, end-of-directory without error, repeated `nextEntry()` calls, and Windows wildcard/non-wildcard paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.hh

Purpose: declares the `XrdSysDir` directory iteration API.

Important APIs/types/functions: constructor `XrdSysDir(const char *path)`, virtual destructor, `bool isValid()`, `int lastError()`, and `char *nextEntry()`. The private state is an opaque `void *dhandle` plus `lasterr`.

Control flow: callers construct an instance, check `isValid()`, loop on `nextEntry()`, and inspect `lastError()` if null is returned unexpectedly.

State and persistence: object-scoped directory handle only. No persistent filesystem mutation is performed by this class.

Dependencies and integration: includes `sys/types.h` on non-Windows and defines `uid_t`/`gid_t` aliases for Windows. It hides the platform-specific directory handle behind `void *`.

Risks: inline accessors expose no synchronization, so each instance is single-consumer unless externally serialized. The `char *` return type suggests mutable data even though callers should not modify platform buffers.

Test signals: compile on Windows and Unix, validate destructor closes resources, and assert `lastError()` distinguishes invalid construction from normal iteration exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.cc

Purpose: implements thread-safe errno-to-text conversion with cached strings and platform adjustments.

Important APIs/types/functions: `XrdSysE2T(int errcode)` returns a stable `const char *`; local `initErrTable()` precomputes known error strings into `Errno2String`; `e2sMap` stores generic messages for unknown positive error codes; `e2sMutex` guards the map.

Control flow: static initialization preloads slots 1..143 using `strerror(ERRNOBASE+i)`, lowercases the first character, remaps `EBADE` to an authentication-focused message, fills holes up to the last known error, and sets slot 0 to "no error". Calls return immediately for 0 and known ranges, return "negative error" for negative values, or lazily create `"unknown error N"` in the map.

State and persistence: process-lifetime allocated strings and map entries; no deallocation is attempted. This is intentional stable-storage behavior for returned pointers.

Dependencies and integration: uses C library `strerror`, `strdup`, `tolower`, STL `map`/`string`, and `XrdSysMutex`. Used by logging, plugin loading, IOEvents, and error reporting.

Risks: returning `eTxt.c_str()` after unlocking is safe only because `std::map` node storage is stable for non-erased entries; heavy insertion from many unknown codes still grows memory. Static initialization depends on pthread mutex readiness.

Test signals: known errno, unknown positive code, negative code, GNU/Hurd `ERRNOBASE`, `EBADE` remapping, and concurrent lookup of unknown codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.hh

Purpose: declares the global errno-to-text helper `XrdSysE2T`.

Important APIs/types/functions: `extern const char* XrdSysE2T(int errcode);` accepts an errno-like integer and returns non-null descriptive text.

Control flow: no local control flow; callers delegate all conversion to the implementation.

State and persistence: no header-owned state. The implementation owns cached text storage.

Dependencies and integration: includes `<cerrno>` for errno constants. It is a central utility used by `XrdSysError`, `XrdSysLogger`, `XrdSysLogging`, `XrdSysPlugin`, and IO event diagnostics.

Risks: returned pointer lifetime and thread safety are implementation contracts, so alternate implementations must preserve stable storage. It intentionally does not expose buffer-based APIs like `strerror_r`.

Test signals: include in C++ translation units with varying platform headers, verify symbol linkage, and test common errno conversions through callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.cc

Purpose: implements formatted error and trace emission for `XrdSysError`.

Important APIs/types/functions: static tables `XrdSysError::etab` and `etab_errno`; `baseFD()` delegates to `Logger->originalFD()`; `ec2text()` looks up custom error text then falls back to `XrdSysE2T`; `ec2errno()` maps extended codes through registered errno tables; `Emsg()` overloads produce timestamped/prefixed messages; `Say()` emits an unprefixed line; `TBeg()` and `TEnd()` bracket trace output through the logger.

Control flow: formatting is built as `struct iovec` arrays to avoid temporary concatenation. `Emsg(esfx, ecode, ...)` formats "Unable to ..." plus translated error text. The string-only overload and `Say()` conditionally append non-empty fragments.

State and persistence: shared static error tables are process-global and not synchronized for mutation. Each instance owns prefix pointer, prefix length, message mask, and logger pointer but does not own the pointed-to prefix/logger.

Dependencies and integration: depends on `XrdSysE2T`, `XrdSysLogger`, `XrdSysHeaders`, and platform headers. It is the standard diagnostic facade for XrdSys and plugin-loading code.

Risks: `SetPrefix()` calls `strlen()` on the supplied pointer and stores it without copying, so caller lifetime matters. Static table additions must happen before multithreading. Logger must be non-null.

Test signals: custom table lookup, negative error handling, extended errno mapping, prefix changes, null/empty optional fragments, `Log()` mask gating, and trace begin/end serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.hh

Purpose: declares error table types and `XrdSysError`, the logger-backed error-reporting API.

Important APIs/types/functions: `XrdSysError_Table` maps numeric codes to static text; `XrdSysError_Table_Errno` maps extended codes to errno values; log-mask constants `SYS_LOG_01` through `SYS_LOG_08`; `XrdSysError` exposes `addTable()`, `baseFD()`, `ec2text()`, `ec2errno()`, `Emsg()` overloads, `Log()`, `logger()`, `Say()`, `setMsgMask()`, `getMsgMask()`, `SetPrefix()`, `TBeg()`, and `TEnd()`.

Control flow: table lookups are range checks plus array indexing. `Log()` is an inline mask gate before calling `Emsg()`. `logger()` can swap the logger pointer and returns the old one.

State and persistence: global linked lists of registered tables; per-instance prefix pointer/length, message mask, and `XrdSysLogger *`. Tables are not freed by this class and are expected to refer to static text arrays.

Dependencies and integration: forward-declares `XrdSysLogger`; includes C string/platform headers. Used by components that need uniform diagnostics and errno mapping.

Risks: no ownership or synchronization around registered tables, prefixes, or loggers. `ec2errno()` is non-static because it uses registered static state but no instance state.

Test signals: table boundary conditions, multiple table ordering, mask filtering, logger replacement, prefix lifetime assumptions, and compile behavior on Windows and POSIX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.cc

Purpose: selects and implements the native extended-file-attribute adapter and plugin hook.

Important APIs/types/functions: process-global `XrdSysXAttrNative` references default `dfltXAttr`; `XrdSysXAttrActive` and `XrdSysFAttr::Xat` point to the active attribute processor. Platform `.icc` files implement `Del`, `List`, `Get`, and `Set`; unsupported platforms return `-ENOTSUP`. Common helpers include `Diagnose()`, `Free()`, `getEnt()`, and `SetPlugin()`.

Control flow: compile-time platform selection includes BSD, Linux/GNU, macOS, or Solaris implementations. `Diagnose()` suppresses common missing-attribute/missing-path errors and logs other failures through `Say`. `getEnt()` optionally probes value size, allocates a variable-length `AList`, and links it at the head.

State and persistence: active implementation is global mutable state. `AList` nodes are heap-allocated with `malloc` and freed through `Free()`. Plugin replacement can delete the previous non-default implementation unless `push` is true.

Dependencies and integration: depends on `XrdSysXAttr.hh`, `XrdSysError.hh`, errno conventions, and platform xattr syscalls hidden in `.icc` files.

Risks: global active-plugin changes are unsynchronized. Ownership of plugin objects is subtle. Negative errno returns must be consistently interpreted by callers. `getEnt()` relies on dynamic struct sizing.

Test signals: platform xattr CRUD, missing attributes, unsupported platforms, plugin replacement/push behavior, `AList` list/free correctness, and diagnostics suppression versus emitted errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.hh

Purpose: declares `XrdSysFAttr`, the internal native extended-attribute provider implementing `XrdSysXAttr`.

Important APIs/types/functions: public static `XrdSysXAttr *Xat` is the active provider pointer; `SetPlugin(XrdSysXAttr *xaP, bool push=false)` replaces or pushes an alternate processor. The constructor/destructor are trivial. Inherited operations `Del`, `Free`, `Get`, `List`, and `Set` are private to force callers through `Xat` or the abstract `XrdSysXAttr` interface.

Control flow: callers do not directly invoke private methods on a `XrdSysFAttr` instance; they use `XrdSysFAttr::Xat->...` so the active implementation can be swapped globally.

State and persistence: only static active-provider state is exposed here. The object itself has no per-instance data.

Dependencies and integration: derives from `XrdSysXAttr`, whose `AList` type and virtual interface define the external contract.

Risks: public mutable static pointer can be changed from any translation unit. The private inheritance implementations make misuse harder but not impossible through friend/global objects.

Test signals: verify callers use `Xat`, compile-time prevention of direct private method calls, plugin install behavior, and ABI stability against `XrdSysXAttr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFD.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFD.hh

Purpose: provides inline wrappers for common file descriptor creation APIs that set `FD_CLOEXEC` portably.

Important APIs/types/functions: anonymous-namespace wrappers `XrdSysFD_Accept`, `XrdSysFD_Dup`, `XrdSysFD_Dup1`, `XrdSysFD_Dup2`, `XrdSysFD_Open`, `XrdSysFD_OpenDir`, `XrdSysFD_Pipe`, `XrdSysFD_Socket`, `XrdSysFD_Socketpair`, `XrdSysFD_Openat`, and `XrdSysFD_Yield`.

Control flow: on Linux/GNU with `SOCK_CLOEXEC` and `O_CLOEXEC`, wrappers use atomic CLOEXEC variants such as `accept4`, `dup3`, `pipe2`, and `socket(...|SOCK_CLOEXEC)`. Fallbacks call traditional APIs then `fcntl(F_SETFD, FD_CLOEXEC)`.

State and persistence: no owned state. Wrappers return descriptors/directories whose lifecycle belongs to callers. `XrdSysFD_Yield()` clears `FD_CLOEXEC` on an existing descriptor.

Dependencies and integration: POSIX file, socket, directory, and errno headers. Used by logger, poller, plugin-adjacent code, and other subprocess-safe components.

Risks: fallback paths have an unavoidable fork/exec race between descriptor creation and `fcntl`. `Dup2` fallback returns `dup2` status, whose zero success assumption only holds when duplicating to descriptor 0; this deserves careful review. `openat` always ORs `O_CLOEXEC`, assuming it exists.

Test signals: descriptor flags after every wrapper, fallback builds, `OpenDir` error preservation, `Yield()` clearing, and fork/exec leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.cc

Purpose: supplies a macOS implementation of `posix_fallocate()`.

Important APIs/types/functions: `int posix_fallocate(int fd, off_t offset, off_t len)` is compiled only under `__APPLE__`. It uses `fcntl(F_PREALLOCATE)` with `fstore_t`, first requesting contiguous allocation and then falling back to non-contiguous allocation, followed by `ftruncate(fd, offset + len)`.

Control flow: detects signed overflow of `offset + len` with `__builtin_saddll_overflow`; on no overflow, tries contiguous preallocation, then all-or-nothing preallocation, then extends/truncates file size. On overflow or failed fcntl/ftruncate, returns a negative system-call-style result.

State and persistence: mutates file allocation and potentially file length for the supplied descriptor. No process-global state.

Dependencies and integration: macOS `fcntl`, `unistd`, and stat/types headers. Paired with `XrdSysFallocate.hh` so XRootD code can call `posix_fallocate` uniformly.

Risks: POSIX `posix_fallocate` normally returns an error number rather than `-1` with `errno`; this implementation returns raw negative syscall status. `ftruncate` may alter size even when the original file was larger/smaller according to platform semantics.

Test signals: macOS sparse file allocation, overflow inputs, fragmented allocation fallback, `ftruncate` failure, and consistency with caller expectations for return convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.hh

Purpose: declares or includes platform support for `posix_fallocate`.

Important APIs/types/functions: on macOS, declares `extern int posix_fallocate(int fd, off_t offset, off_t len);`; elsewhere includes `<fcntl.h>` so the system declaration is available.

Control flow: compile-time branch only.

State and persistence: none in the header; the function mutates file allocation when called.

Dependencies and integration: used by code that needs file-space preallocation without carrying platform-specific includes. It relies on the `.cc` macOS shim being linked where required.

Risks: the header uses `off_t` in the macOS branch without including a type header locally, so include order matters. Return semantics must match caller expectations across platforms.

Test signals: compile on macOS and Linux with this header included first, link macOS shim, and verify caller handling of returned errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysHeaders.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysHeaders.hh

Purpose: centralizes compatibility selection between modern `<iostream>` and old-style `<iostream.h>`.

Important APIs/types/functions: no functions or classes; includes `<iostream>` unless `HAVE_OLD_HDRS` is defined and `WIN32` is not, in which case it includes `<iostream.h>`.

Control flow: compile-time branch only.

State and persistence: none.

Dependencies and integration: included by legacy XrdSys/XrdSut files that write to `std::cerr` or need old compiler compatibility.

Risks: old-header support can mask namespace differences; modern code assumes `std::` names are available. The header is intentionally broad and can increase transitive dependency on iostream.

Test signals: compile with and without `HAVE_OLD_HDRS`, especially files using `std::cerr`, and verify Windows always uses modern include.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysHeaders.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.cc

Purpose: implements the common channel/poller state machine for XrdSys non-blocking I/O event dispatch, leaving backend poll-set mechanics to platform `.icc` files.

Important APIs/types/functions: local sentinel pollers `pollInit`, `pollWait`, and `pollErr1`; `BootStrap::Start()` starts the poll thread; `Channel` methods implement `Delete`, `Enable`, `Disable`, `SetFD`, `SetCallBack`, `Reset`; `Poller` methods implement `Create`, `Attach`, `Detach`, callback execution, command-pipe I/O, timeout queue management, `Stop`, and `WakeUp`.

Control flow: `Poller::Create()` creates a CLOEXEC pipe, constructs the backend via `newPoller()`, starts a bound thread, and waits on a semaphore for readiness. A `Channel` starts attached to `pollInit`; first `Enable()` transitions through `pollWait`, includes the fd in the backend poll set, then modifies event masks. Poller callbacks call `CbkXeq()`, which removes/updates timeouts, handles fatal errors, drops the channel lock before invoking user callbacks, then either detaches or re-arms deadlines. `Stop()` sends a pipe command, closes pipes, disables channels, invokes optional stop callbacks, and runs backend shutdown.

State and persistence: per-channel state includes fd, callbacks, event masks, read/write timeouts, deadlines, status, poll-set membership, deferred modifications, and faults. Per-poller state includes attached and timeout linked lists, command pipe fds, wake-pending atomic flag, poll thread id, locks, and static parent PID/max time. No durable persistence.

Dependencies and integration: uses `XrdSysFD`, `XrdSysPthread`, `XrdSysAtomics`, `XrdSysE2T`, platform headers, and includes epoll/kqueue/poll/port backends by preprocessor.

Risks: high concurrency surface: callback deletion, fd lifetime, lock handoff, deferred modify, and timeout rearming must remain consistent. Header warns callers must disable/delete channels before closing fds. Wakeup ordering relies on atomics plus `toMutex`.

Test signals: enable/disable/read/write/error events, callback deleting channel, external deletion during callback, `SetFD(-1)` before close, timeout auto-rearm and `optTOM`, poller stop callback, backend command pipe partial reads, and stress with many concurrent channel mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.hh

Purpose: declares the public event polling architecture under `XrdSys::IOEvents`.

Important APIs/types/functions: `CallBack` exposes event flags `ReadyToRead`, `ReadTimeOut`, `ReadyToWrite`, `WriteTimeOut`, `ValidEvents`, pure virtual `Event()`, and optional `Fatal()`/`Stop()` hooks. `Channel` exposes `Delete`, `Enable`, `Disable`, `GetCallBack`, `GetEvents`, `GetFD`, `SetCallBack`, `SetFD`, and constructor. `Poller` exposes `Create`, `Stop`, constructor/destructor, and protected virtual backend methods `Begin`, `Exclude`, `Include`, `Modify`, `Shutdown`.

Control flow: users create a specialized `Poller` through `Poller::Create()`, construct `Channel` objects against it, enable events, and react through `CallBack`. Backend implementations subclass `Poller` and use protected helpers to synchronize command dispatch and callback execution.

State and persistence: channel and poller fields define all runtime state: lists, locks, fd, callback, timeouts, status, command pipe, and wake flag. The API explicitly requires callers to detach/disable channels before closing descriptors.

Dependencies and integration: depends on `poll.h`, pthread wrappers, and atomic macros. Platform backends are included by the `.cc` file.

Risks: destructor for `Channel` is private, so callers must use `Delete()`. Callback code may deadlock if it manages unrelated channels without a clear lock model. Event bits and callback event bits are related but distinct masks.

Test signals: API-level lifecycle tests, callback return false behavior, fatal and stop hook behavior, timeout settings per read/write, and compile tests for custom backend subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysKernelBuffer.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysKernelBuffer.hh

Purpose: implements a Linux-oriented zero-copy-ish kernel buffer abstraction around pipes, `splice`, and `vmsplice`.

Important APIs/types/functions: class `XrdSys::KernelBuffer`; public `Empty()` and `IsPageAligned()`; private `Alloc`, `Free`, `ReadFromFD`, `WriteToFD`, `ToUser`, and `FromUser`; free helper functions `Read(fd, buffer, length[, offset])`, `Write(fd, buffer, offset)`, `Send(fd, buffer)`, and `Move()` in both directions.

Control flow: reading frees existing pipes, allocates one or more pipes up to `MAX_PIPE_SIZE`, splices fd data into pipe write ends, and tracks per-pipe data size. Writing splices pipe read ends to an fd/socket and drains state. `ToUser()` allocates a page-aligned user buffer and vmsplices/copies pipe data into it. `FromUser()` requires page alignment, vmsplices with `SPLICE_F_GIFT`, frees the user buffer on success, and sets it null.

State and persistence: `capacity`, `size`, `pipes`, and `pipes_cursor` are object state. Pipe fds are closed in `Free()`/destructor. No durable state.

Dependencies and integration: POSIX `pipe`, `fcntl`, `splice`, `vmsplice`, `posix_memalign`, and vector/array/tuple. If splice support macros are missing, operations return `-ENOTSUP`.

Risks: move constructor and move assignment reset `capacity`/`size` on the destination rather than the source in the shown code, which appears to lose ownership accounting and can leak/skip cleanup. `Alloc()` leaks pipe fds if `F_SETPIPE_SZ` fails. `ToUser()` uses `delete[] buffer` on a pointer managed as `free()`/`posix_memalign`, likely wrong. State is not thread-safe.

Test signals: splice-supported and unsupported builds, read/write/send round trips, offset and non-offset paths, page-alignment rejection, `FromUser()` ownership transfer, move construction/assignment destructor behavior, and failure injection for `fcntl`, `splice`, and `posix_memalign`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysKernelBuffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogPI.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogPI.hh

Purpose: defines the logging plugin ABI used by `XrdSysLogging`.

Important APIs/types/functions: `XrdSysLogPI_t` is the per-message callback type taking generation time, thread id, message text, and message length. `XrdSysLogPInit_t` is the plugin initialization entry point type returning an `XrdSysLogPI_t` and accepting a config file name plus plugin-specific argv/argc. Documentation also prescribes `extern "C" XrdSysLogPInit(...)` and optional version declaration via `XrdVERSIONINFO`.

Control flow: the logging system loads a plugin initializer, calls it once, stores the returned callback, then invokes the callback per log message either synchronously or from the async forwarding thread.

State and persistence: no state in the header. Plugin implementations own any state created during init and must keep callback state alive.

Dependencies and integration: includes `<sys/time.h>`. Integrated with `XrdSysPlugin` version checking and `XrdSysLogging::Configure`.

Risks: ABI stability is critical. Callback thread-safety requirements differ by sync versus async mode. Message text is length-delimited but also expected to be null-terminated by current forwarding code.

Test signals: plugin loading, missing init symbol, versioned plugin declarations, synchronous concurrent callbacks, async single-threaded callback ordering, and handling of `tID == 0` captured stderr messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogPI.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.cc

Purpose: implements local log routing, timestamping, capture, rotation, trimming, and midnight/signal/fifo handlers for `XrdSysLogger`.

Important APIs/types/functions: constructor honors `XrdSysLOGFILE`/`XrdOucLOGFILE`; `AddMsg()` queues rotation-time messages; `AtMidnight()` queues tasks; `Bind()` binds to a log file and starts a handler thread; `Capture()` redirects messages to `XrdOucTListFIFO`; `ParseKeep()` parses rotation keep policy; `Put()` writes `iovec` messages; `Time()`/`TimeStamp()` format timestamps; private `FifoMake`, `FifoWait`, `HandleLogRotateLock`, `RmLogRotateLock`, `putEmsg`, `ReBind`, `Trim`, and `zHandler` implement log lifecycle.

Control flow: `Put()` gets time/thread id, optionally forwards through `XrdSysLogging`, prefixes timestamp when `iov[0].iov_base` is null, locks, captures or `writev`s. `Bind()` tears down conflicting handler mode, opens/rebinds the log file, creates rotation lock/fifo/signal handling, then starts `zHandler()`. `zHandler()` waits for fifo input, midnight, or signal, reopens/rotates logs, emits queued messages, and launches midnight tasks.

State and persistence: object state includes file descriptors, base fd, log path, suffix, keep policy, fifo path, rotation thread id, queued messages/tasks, and mutex. It creates log files, rotated date-suffixed files, fifo files, and `.lock` files.

Dependencies and integration: uses `XrdSysFD`, `XrdSysLogging`, `XrdSysTimer`, `XrdSysUtils`, `XrdSysThread`, `XrdSysE2T`, POSIX filesystem/signal APIs, and `XrdOucTListFIFO`.

Risks: partial `writev` is explicitly ignored. Handler thread is killed when rebinding. Rotation lock path handling has pointer arithmetic assumptions. Global capture pointer is shared across logger instances. Destructor removes lock but does not visibly stop handler thread.

Test signals: timestamp formats, env log binding, file/fifo/signal rotation, keep-by-count and keep-by-size trimming, capture mode, forwarding suppression, lock-file creation/removal, and write errors/partial writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.hh

Purpose: declares `XrdSysLogger`, the local logging and log-rotation facade.

Important APIs/types/functions: constructor/destructor; nested abstract `Task::Ring()` for midnight work; `AddMsg`, `AtMidnight`, `Bind`, `Capture`, `Flush`, `originalFD`, `ParseKeep`, `Put`, static `setForwarding`, `setHiRes`, `setKeep`, `setRotate`, `traceBeg`, `traceEnd`, `xlogFN`, and public `zHandler`. Private helpers cover fifo creation, timestamping, rotation lock, rebinding, and trimming.

Control flow: callers configure binding/rotation, then write messages through `Put()`. Trace users call `traceBeg()` and `traceEnd()` around direct stream output under the logger mutex.

State and persistence: owns current log fd binding state, path strings, rotation suffix, queued midnight messages/tasks, keep policy, fifo path, and handler thread id. It creates/removes filesystem artifacts during rotation.

Dependencies and integration: depends on pthread wrappers and platform `iovec` support. Used by `XrdSysError`, `XrdSysLogging`, and tracing code.

Risks: caller-supplied tasks must outlive the logger's queue. `traceBeg`/`traceEnd` must be paired or the mutex stays locked. `setForwarding` is static global state affecting all logger instances.

Test signals: API compile coverage, trace lock pairing, keep option parsing, static forwarding behavior, destructor cleanup, and multi-logger capture/forwarding interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogger.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.cc

Purpose: implements remote/plugin log forwarding and base logger configuration.

Important APIs/types/functions: `XrdSysLogging::Configure()` configures local file output, plugin callback, sync/async mode, buffer allocation, and forwarding thread. `Forward()` sends or enqueues messages. Private `CopyTrunc`, `EMsg`, `getMsg`, and `Send2PI` support truncation, errors, ring-buffer queueing, and async delivery.

Control flow: configuration optionally binds the local logger, then if a plugin exists either sets synchronous forwarding when buffer size is zero or allocates a page-aligned queue buffer and starts `Send2PI`. `Forward()` computes message length; sync mode copies/truncates into an 8 KiB stack buffer and calls the plugin directly. Async mode locks `msgMutex`, drops too-long or no-room messages into a lost count, writes `MsgBuff` headers and text into a circular buffer, posts `msgAlert` when the queue transitions from empty, and returns whether local logging should stop. `Send2PI()` waits, drains queued messages, and synthesizes lost-message notices.

State and persistence: module-static queue pointers, plugin function pointer, semaphore, mutex, lost-message counters, mode flags, and forwarding thread id. No disk persistence except through configured local logger.

Dependencies and integration: uses `XrdSysLogger`, `XrdSysLogPI`, `XrdSysThread`, `XrdSysSemaphore`, `posix_memalign`, and `getpagesize`.

Risks: async queue has bounded capacity and drops messages. `logDone` suppresses local output when only remote output is configured. The forwarding thread runs indefinitely. Plugin callbacks must tolerate message lifetime only during the call.

Test signals: local-only, remote-only, local+remote, sync and async plugin modes, queue overflow/lost notices, oversized messages, plugin thread id/time arguments, and startup failure for allocation/thread creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.hh

Purpose: declares the singleton-style logging plugin forwarding helper.

Important APIs/types/functions: `XrdSysLogging::Parms` carries `logfn`, `logpi`, `bufsz`, `keepV`, and `hiRes`; static `Configure(XrdSysLogger&, Parms&)` applies those settings; static `Forward(timeval, unsigned long, iovec*, int)` forwards a message. Private `MsgBuff` encodes async queue records with timestamp, thread id, next offset, buffer size in doublewords, and signed message length.

Control flow: users prepare `Parms`, call `Configure()`, then `XrdSysLogger::Put()` calls `Forward()` when global forwarding is enabled.

State and persistence: exposes static `lpiTID`, `lclOut`, and `rmtOut` declarations plus private static methods. Runtime queue state lives in the `.cc` file.

Dependencies and integration: includes `XrdSysLogPI.hh`, pthread wrappers, `sys/time.h`, and `sys/uio.h`. It sits between local logger and logging plugin ABI.

Risks: `MsgBuff` size limits cap messages at `SHRT_MAX` and queue records at the encoded doubleword size. Static output flags imply one process-wide logging configuration.

Test signals: parameter defaults, message length boundaries, struct layout assumptions, and integration with `XrdSysLogger::setForwarding`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPageSize.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPageSize.hh

Purpose: defines a uniform compile-time page size contract for XrdSys components.

Important APIs/types/functions: namespace constants `XrdSys::PageSize = 4096`, `PageMask = 4095`, and `PageBits = 12`.

Control flow: none.

State and persistence: none.

Dependencies and integration: no includes. Intended for components that need page alignment or page arithmetic without calling `getpagesize()`.

Risks: hard-coding 4 KiB is not universally correct across all architectures or filesystems. Code using this for kernel/user alignment must be validated on non-4K-page platforms.

Test signals: compile-time use in alignment math, runtime comparison with `sysconf(_SC_PAGESIZE)` on supported platforms, and behavior on systems with larger pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPageSize.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.cc

Purpose: implements portability helpers declared in `XrdSysPlatform.hh`.

Important APIs/types/functions: `Swap_n2hll()` is provided for little-endian platforms lacking GCC byte-swap support or on Apple; fallback `strlcpy()` is implemented when `HAVE_STRLCPY` is absent; `XrdSys::getIovMax()` returns the maximum supported iovec count, using `sysconf(_SC_IOV_MAX)` when `IOV_MAX` is unavailable.

Control flow: compile-time endianness and feature checks select helper definitions. `getIovMax()` uses a static lambda-backed value when it must query `sysconf`, defaulting to 1024 if the query fails.

State and persistence: no mutable external state except static cached `IOV_MAX` inside `getIovMax()` on platforms needing runtime discovery.

Dependencies and integration: uses byte-order/network conversion headers, C string routines, and `sysconf`. Used by logging and I/O vector code.

Risks: strict-aliasing/alignment assumptions in `Swap_n2hll()` can be sensitive. Fallback `strlcpy()` assumes `sz > 0` before writing `dst[0]` in one branch. `IOV_MAX` macro shadowing by static local name is unusual.

Test signals: endian conversion round trips, fallback `strlcpy()` boundary sizes including zero, `getIovMax()` with and without `IOV_MAX`, and builds on Apple/non-GCC little-endian targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.hh -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.hh

Purpose: central platform portability header for constants, byte swapping, networking types, filesystem macros, and utility declarations.

Important APIs/types/functions: platform definitions for `MAXNAMELEN`, `MAXPATHLEN`, `fdatasync`, `off64_t`, `STATFS`, `FS_BLKFACT`, `FLOCK_t`, `SHMDT_t`, endian macros/conversions `htonll`, `ntohll`, `h2nll`, `n2hll`, `bswap()` overloads, `SOCKLEN_t`, `PTR2INT`, `Netdata_t`, `Sokdata_t`, `IOV_INIT`, `MAKEDIR`, `CHMOD`, `net_errno`, `LT_MODULE_EXT`, and `XrdSys::getIovMax()`.

Control flow: large preprocessor matrix selects behavior for Linux, Apple, FreeBSD, GNU/Hurd, Solaris, AIX, and Windows. Endianness detection either defines pass-through conversions, byte-swap conversions, or errors out on unknown non-Windows targets.

State and persistence: no runtime state in the header. It defines compile-time contracts consumed across XrdSys.

Dependencies and integration: includes C standard integer/stdlib headers and platform headers such as byteswap, OSByteOrder, sys/param, and Windows compatibility. Nearly all low-level XRootD utility code can depend on it.

Risks: macro-heavy portability code can collide with system headers or caller identifiers. Hardcoded GNU/Hurd path/name limits are acknowledged as imperfect. `PTR2INT` truncates pointers by design. Unknown endianness is a hard compile failure.

Test signals: platform matrix builds, endian conversion tests, socket type compatibility, filesystem macro use, `LT_MODULE_EXT` override, and inclusion-order tests with system headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.cc -->
## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.cc

Purpose: implements runtime plugin loading, symbol lookup, optional preloading, and version compatibility checks.

Important APIs/types/functions: destructor closes `libHandle`; `badVersion()` formats incompatibility messages; `chkVersion()` finds `<pluginSymbol>Version` and applies `XrdVERSIONPLUGINRULES`/`MAXIMS`; `DLflags()` chooses `dlopen` flags; `Find()` searches the preload list; `getLibrary()` opens the shared object or executable image; `getPlugin()` resolves a symbol and reports loaded versions; `Inform()`, `libMsg()`, and `msgSuffix()` route diagnostics; static `Preload()` stores handles in `plList`; `VerCmp()` compares two linked-module versions.

Control flow: `getPlugin()` calls `getLibrary()`, `dlsym()`, `chkVersion()`, then optionally emits a load message. `getLibrary()` reuses object handles or preloaded handles, builds `dlopen` flags, maps `dlerror()` text to `ENOENT`/`ENOEXEC`, and emits errors depending on optionality. Version checking handles no-version, missing-version, dirty/unreleased, bad, and clean outcomes.

State and persistence: each object owns duplicated `libPath` and an optional `dlopen` handle unless `Persist()` detached it. Static `plList` holds preloaded library paths/handles for process lifetime. Diagnostic state points to either `XrdSysError` or caller buffer.

Dependencies and integration: uses POSIX `dlopen`/`dlsym`/`dlclose`, Windows compatibility include, `XrdSysError`, `XrdSysPlatform`, `XrdVersion.hh`, and `XrdVersionPlugin.hh`. Used by plugin-based subsystems including logging and xattr providers.

Risks: preload list is not thread-safe. Version rules depend on symbol naming and copied `XrdVersionInfo` layout. `RTLD_GLOBAL` is unsupported on Windows. `XRDPIHUSH` suppresses non-forced informational messages, which can hide useful client diagnostics.

Test signals: missing library, bad shared object, missing symbol optionality levels, executable-image symbol lookup, preloaded library reuse, `Persist()` lifetime, version clean/missing/bad/unreleased paths, and `XRDPIHUSH` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.cc -->

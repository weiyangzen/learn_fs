# subset-b-007952 Research

Grouped research for selected XRootD `XrdOuc` cache, callback, configuration, environment, export, mapping, hash, and utility files. Each section preserves the source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheCM.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheCM.hh

## Purpose
Defines the plugin ABI for cache context management modules loaded by the proxy/storage stack when a POSIX cache is enabled. The header is documentation-heavy and establishes the expected `extern "C"` initializer used by the `pss.ccmlib` directive.

## Important APIs, Types, And Functions
Forward declarations cover `XrdOucEnv`, `XrdPosixCache`, and `XrdSysLogger`. The central API is `XrdOucCacheCMInit_t`, a function pointer returning `bool` and accepting the cache object, optional logger, config filename, optional directive parameters, and optional environment. The comments prescribe the concrete exported symbol `XrdOucCacheCMInit(...)` and recommend `XrdVERSIONINFO(XrdOucCacheCMInit,<name>)` for plugin/version compatibility.

## Control Flow
There is no executable control flow in this header. Runtime flow is external: configuration loads a shared library, locates `XrdOucCacheCMInit`, passes the live `XrdPosixCache` and context objects, and treats `true` as initialization success.

## State And Persistence
The file defines no state. State is owned by the cache, the plugin implementation, and the process environment passed through `XrdOucEnv`; any persistence depends on the plugin and cache backend.

## Dependencies And Integration Points
This is an ABI contract between cache plugins, the POSIX cache layer, the XRootD logger, and pss configuration. The signature and symbol spelling are integration-critical because dynamic loading depends on C linkage.

## Risks And Test Signals
Risks are ABI drift, missing `extern "C"` linkage, omitted version information, and plugins assuming logger/config/env pointers are non-null. Test signals are plugin load tests with and without directive parameters, disabled cache behavior, and failure propagation when the initializer returns false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheCM.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheStats.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheStats.hh

## Purpose
Provides a thread-serialized statistics container for cache usage. It groups cumulative cache I/O counters, file counters, disk and memory state, and POSIX-layer deferred-open/close counters.

## Important APIs, Types, And Functions
`XrdOucCacheStats::CacheStats` is a POD record stored as public member `X`. Counters include read/write bytes (`BytesRead`, `BytesGet`, `BytesPass`, `BytesWrite`, `BytesPut`), hit/miss/pass and preread counts, file lifecycle counts, disk and memory gauges, and deferred-file counters. Methods `Get`, `Add`, and `Set` copy, aggregate, or replace selected portions under `XrdSysMutex`. Scalar helpers `Add(long long&, long long)`, `Count`, and `Set(long long&, long long)` update individual counters.

## Control Flow
Callers update `X` either directly while holding `Lock()`/`UnLock()` or through scalar helpers. `Get` snapshots the full POD with `memcpy`; `Add` aggregates only activity counters; `Set` refreshes gauge-like file/disk/memory fields. Construction zeroes the POD.

## State And Persistence
All state is in-memory. The mutex guards concurrent updates but the public `X` member allows callers to bypass locking unless they follow the convention. No counters are persisted by this class.

## Dependencies And Integration Points
Depends on `XrdSysAtomics.hh` and `XrdSysPthread.hh`. It is meant to be embedded in cache objects and integrated with monitoring/statistics export paths that snapshot or merge cache counters.

## Risks And Test Signals
Risks include public mutable state, inconsistent use of lock helpers, and `Add(XrdOucCacheStats&)` intentionally omitting some counters such as deferred opens/closes and gauges. Test signals should cover concurrent counter increments, aggregate semantics, snapshot consistency, and monitoring output after cache reads, writes, purges, and open/close events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.cc

## Purpose
Implements `XrdOucCallBack`, a wrapper that turns an `XrdOucErrInfo` callback capability into a controlled asynchronous reply sequence.

## Important APIs, Types, And Functions
`Cancel()` replies with retry semantics when a callback is outstanding. `Init(XrdOucErrInfo*)` captures the original callback object and argument, copies the user id, and replaces the input error-info callback with this wrapper. `Reply(int,int,const char*,const char*)` constructs a fresh `XrdOucErrInfo`, waits for the initial wait-for-callback notification, invokes the original callback's `Done`, and waits again for send completion.

## Control Flow
Initialization only succeeds when no callback is already pending and `eInfo` supplies a callback. Reply first atomically detaches `cbObj`, waits on `cbSync`, fills callback error text/code, calls the original callback, then waits for the wrapper `Done()` to post again. `Cancel` is just `Reply(1, 0, "")`, signaling retry.

## State And Persistence
State is transient: `cbObj`, `cbArg`, `UserID`, and semaphore `cbSync`. The object is deliberately not multi-thread safe and must be used serially. No persistent state is written.

## Dependencies And Integration Points
Depends on `XrdOucCallBack.hh`, `XrdOucErrInfo`, `XrdOucEICB`, and `XrdSysSemaphore`. It integrates with plugin/server flows where an operation returns an intermediate wait state and later completes asynchronously.

## Risks And Test Signals
The major risk is deadlock if `Init()` is called and neither `Reply()` nor `Cancel()` completes the two-semaphore protocol. Other risks are object reuse races and callbacks that never invoke the nested `Done`. Test signals include async completion ordering, destructor-triggered cancel, retry behavior, and callback clients that verify causality between wait notification and final reply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.hh

## Purpose
Declares `XrdOucCallBack`, a serial-use helper for managing `XrdOucErrInfo` asynchronous callbacks safely enough for common XRootD framework use.

## Important APIs, Types, And Functions
The class derives from `XrdOucEICB`. Public methods are `Allowed`, `Cancel`, `Init`, and `Reply`. `Next` is a public link field for pools/lists. Private overrides `Done` and `Same` satisfy the callback interface; `Done` posts the semaphore used by `Reply`, while `Same` always returns false.

## Control Flow
Users check `Allowed`, call `Init`, return/emit the wait-for-callback response, and later call `Reply` or `Cancel`. The destructor calls `Cancel` when a callback is still armed.

## State And Persistence
The class holds only in-memory callback handoff state: semaphore, opaque callback argument, original callback pointer, and copied 64-byte user id. It has no ownership of external callback objects beyond the temporary pointer.

## Dependencies And Integration Points
Includes `XrdOucErrInfo.hh` and `XrdSysPthread.hh`. The class is a utility layer over the `XrdOucEICB` callback contract used by plugins and request handlers.

## Risks And Test Signals
The header explicitly warns that the object is not MT-safe and that failing to effect a callback response after `Init` can hang future users. Compile coverage should verify virtual signatures, while runtime tests should exercise allowed/not-allowed paths, destructor cancel, and reply with optional path tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChain.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChain.hh

## Purpose
Defines simple template node, stack, and queue containers used by older XRootD utility code where intrusive allocation patterns are preferred.

## Important APIs, Types, And Functions
`XrdOucQSItem<T>` stores `nextelem` and `dataitem`. `XrdOucStack<T>` exposes `Push`, `Pop`, and `isEmpty` over a singly linked LIFO chain. `XrdOucQueue<T>` exposes `Add`, `Remove`, and `isEmpty` over a singly linked FIFO chain with head and tail pointers.

## Control Flow
Callers allocate/wrap items in `XrdOucQSItem`, push/add them, and later pop/remove to retrieve only the `T*`. The container does not delete wrapper nodes during removal; ownership remains with callers.

## State And Persistence
State is only the in-memory anchor/tail pointers. There is no locking, refcounting, or persistence.

## Dependencies And Integration Points
The header has no external includes and is used as a lightweight utility by modules that can manage node lifetime externally.

## Risks And Test Signals
Risks include wrapper leaks, stale node reuse, and no thread-safety. Queue `Remove` returns data without clearing the removed node's `nextelem`, unlike stack `Pop`, so callers should not assume detached nodes are reset. Test signals are basic FIFO/LIFO ordering, empty removal, and lifecycle tests in any owner code that embeds these wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChain.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChkPnt.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChkPnt.hh

## Purpose
Defines an abstract checkpoint interface for file implementations that support create, restore, truncate, write, and cleanup of checkpointed file state.

## Important APIs, Types, And Functions
`XrdOucChkPnt` declares pure virtual methods `Create`, `Delete`, `Finished`, `Query(iov&)`, `Restore(bool*)`, `Truncate(iov*&)`, and `Write(iov*&, int)`. The interface uses `struct iov` from `XrdOucIOVec.hh` by forward declaration for offset/length/vector data.

## Control Flow
Consumers obtain an implementation object, call `Create`, stream writes/truncates through `Write` and `Truncate`, query limits with `Query`, restore with `Restore`, and end lifecycle with `Finished`. The destructor comment says use `Finished()` rather than deleting directly, allowing implementations to self-delete or clean outstanding checkpoint files.

## State And Persistence
The interface itself has no state, but implementations are expected to manage persistent checkpoint data and restore/truncate semantics. `Restore` can report whether read access remains safe after an error through `readok`.

## Dependencies And Integration Points
It is an integration contract between storage/cache code and checkpoint backends. It depends on `iov` layout compatibility and errno-style return values.

## Risks And Test Signals
Risks include ambiguous ownership of `iov*&` ranges, callers deleting instead of calling `Finished`, and inconsistent restore behavior after partial checkpoint failures. Test signals include create/delete idempotence, write/truncate ordering, restore after failure, checkpoint length queries, and implementations returning `-errno` consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChkPnt.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCloneSeg.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCloneSeg.hh

## Purpose
Defines a compact segment descriptor for file clone/copy-range operations.

## Important APIs, Types, And Functions
`XrdOucCloneSeg` contains source file descriptor `srcFD`, reserved integer `reserved`, source offset `srcOffs`, length `srcLen`, and destination offset `dstOffs`, all using fixed-width `uint64_t` for offsets and lengths. The constructor initializes only `reserved` to zero.

## Control Flow
There is no executable logic beyond construction. Callers fill one or more descriptors and pass them to clone-capable storage routines.

## State And Persistence
The struct carries transient operation parameters. It does not own file descriptors or buffers and persists nothing.

## Dependencies And Integration Points
Includes `<cstdint>`. It is a generic utility ABI for modules that support cloning segments from a source descriptor into a destination file.

## Risks And Test Signals
Risks are uninitialized `srcFD`, offsets, and lengths if callers rely on the default constructor, plus future ABI use of `reserved`. Test signals are clone operations with multiple segments, zero-length/large-offset segments, and validation that source descriptors remain caller-owned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCloneSeg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCompiler.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCompiler.hh

## Purpose
Provides a small compiler-portability macro for marking return values as important.

## Important APIs, Types, And Functions
Defines `XRD_WARN_UNUSED_RESULT` as `__attribute__((warn_unused_result))` for GCC and Clang, and as empty for other compilers.

## Control Flow
No runtime control flow. The macro affects compile-time diagnostics when attached to function declarations.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
No includes. It is intended for portable header use across XRootD modules.

## Risks And Test Signals
Risks are compiler-feature drift and inconsistent warnings on non-GNU compilers. Test signals are build logs confirming annotated APIs warn when ignored under GCC/Clang and compile cleanly elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCompiler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucDLlist.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucDLlist.hh

## Purpose
Defines an intrusive circular doubly linked list node template that can also serve as an anchorless list.

## Important APIs, Types, And Functions
`XrdOucDLlist<T>` stores `next`, `prev`, and `item`. Public methods include `Apply`, `Insert`, `Remove`, `Next`, `Prev`, `Item`, `setItem`, and `Singleton`. The destructor removes the node when it appears linked.

## Control Flow
Nodes start as self-referential singletons. `Insert` links a node immediately after the receiver and optionally sets its item. `Remove` unchains and resets the node to singleton. `Apply` traverses from an optional start node or `this`, snapshots the next node before invoking the callback, and stops when the callback returns non-zero.

## State And Persistence
State is in-memory list links and a non-owning `T*` item. The list does not manage item lifetime.

## Dependencies And Integration Points
Header-only utility with no external dependencies. Used by code that needs stable traversal while callbacks may mutate current nodes.

## Risks And Test Signals
Risks include no locking, destructor removal based on `prev != next` missing some corrupted-link states, and caller-owned item lifetime. Test signals are insert/remove order, callback traversal while removing current nodes, singleton detection, and repeated remove/destruct behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucDLlist.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.cc

## Purpose
Implements a mutex-protected error-code/message accumulator with optional append semantics and errno integration.

## Important APIs, Types, And Functions
Implemented methods are `Get`, `Msg`, `Msgf`, `MsgVA`, `MsgVec`, `SetErrno`, and private `Setup`. `Msg` builds a vector of up to five text fragments with spaces. `Msgf` and `MsgVA` format into a 2048-byte buffer. `SetErrno` stores errno/error code and either system error text or alternate text.

## Control Flow
All state mutations lock `ecMTX`. `Get(..., rst=false)` snapshots without clearing; reset mode moves the string out, clears `eCode`, and erases the internal string. `Append` state is consumed by `Setup`: when `Delim` is non-zero it appends delimiter plus new text, otherwise it replaces the message.

## State And Persistence
State is in-memory `ecMsg`, `eCode`, default message id `msgID`, and pending delimiter `Delim`. `SetErrno` also writes process/thread-visible `errno`. There is no persistence.

## Dependencies And Integration Points
Depends on `XrdOucECMsg.hh` and `XrdSysE2T` for errno-to-text conversion. It integrates with code wanting chainable message construction and compact error propagation.

## Risks And Test Signals
Risks include `vsnprintf` truncation handling, appending only one delimiter per `Append` call, global `errno` side effects, and alternate text beginning with `*` suppressing message replacement. Test signals include concurrent setters/getters, append chaining, long formatted messages, `SetErrno` with default/alternate/suppressed text, and reset versus non-reset `Get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.hh

## Purpose
Declares `XrdOucECMsg`, a small synchronized holder for an integer error code and associated text message.

## Important APIs, Types, And Functions
Public API includes `Append`, `Get`, `hasMsg`, `Msg`, `Msgf`, `MsgVA`, `MsgVec`, `Set`, `SetErrno`, assignment operators for code and message text, and the constructor accepting an optional default message id. Private state is protected by mutable `XrdSysMutex`.

## Control Flow
Callers set or format a message, optionally call `Append` before the next message write, and later retrieve code/text with `Get`. Assignment operators update either code or message under lock.

## State And Persistence
Stores only in-memory message state. The `msgID` pointer is not owned and must remain valid if used as the default prefix in `SetErrno`.

## Dependencies And Integration Points
Includes `<cstdarg>`, `<string>`, and `XrdSysPthread.hh`. It is a reusable utility for error-reporting paths that need safe sharing across threads.

## Risks And Test Signals
The copy assignment from another `XrdOucECMsg` locks only the destination, not the source, so concurrent source mutation can race. Other risks are non-owned prefix lifetime and public methods returning copies with possible staleness. Test signals include thread sanitizer coverage and API behavior for assignment, append, and reset retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucECMsg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.cc

## Purpose
Implements static helpers for formatting errno-style failures and routing them to logs and/or streams.

## Important APIs, Types, And Functions
`Format` builds `"Unable to <action> <object>; <reason>"` plus optional additional context. It uses `XrdSysError::ec2text` and lowercases an initially uppercase reason. `Route` formats into a 2048-byte buffer, calls `XrdSysError::Emsg` and/or `XrdOucStream::Put`, and returns negative errno.

## Control Flow
`Route` is a thin wrapper: format first, route to each non-null destination, then normalize the return value to `-abs(ecode)` or `-1` when the code is zero.

## State And Persistence
No stored state. Side effects are emitted log/stream messages.

## Dependencies And Integration Points
Depends on `XrdOucStream`, `XrdSysError`, `XrdSysPlatform`, and C string/ctype formatting. It is used by configuration or I/O paths that need consistent user-facing failures.

## Risks And Test Signals
Risks are truncation in fixed buffers, incorrect handling if `etxt1` is null, and returning `blen-1` even for very small buffers. Test signals include known errno formatting, optional context formatting, stream/log dual routing, and return-code normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.hh

## Purpose
Declares `XrdOucERoute`, a stateless formatter/router for standard XRootD error messages.

## Important APIs, Types, And Functions
Static methods are `Format(char*, int, int, const char*, const char*, const char*)` and `Route(XrdSysError*, XrdOucStream*, const char*, int, const char*, const char*)`. Forward declarations avoid pulling in full stream/error definitions.

## Control Flow
Consumers call `Format` for buffer-only use or `Route` to both format and emit to selected destinations.

## State And Persistence
No state. Constructing an `XrdOucERoute` object is unnecessary but supported by trivial constructor/destructor.

## Dependencies And Integration Points
Integrates `XrdSysError` logging with `XrdOucStream` client/config streams. The contract specifies negative errno returns.

## Risks And Test Signals
Risks are declaration drift against the `.cc` implementation and callers passing undersized buffers. Build coverage and formatting tests are sufficient for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucERoute.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnum.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnum.hh

## Purpose
Provides a macro to add bitwise operators to strongly named enum types.

## Important APIs, Types, And Functions
`XRDOUC_ENUM_OPERATORS(T)` defines inline `|`, `|=`, `&`, `&=`, `^`, `^=`, and `~` by casting enum values to `int` and back to `T`.

## Control Flow
No runtime control flow beyond inline operator evaluation.

## State And Persistence
No state.

## Dependencies And Integration Points
No dependencies. It integrates with enum flag declarations elsewhere in XRootD that need type-preserving bit operations.

## Risks And Test Signals
Risks include truncation or sign issues for enum values wider than `int`, namespace pollution if used in headers, and duplicate operator definitions if expanded multiple times for the same type in one namespace. Test signals are compile coverage for representative enum flags and static assertions where wide values are possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnum.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.cc

## Purpose
Implements parsing and manipulation of XRootD environment strings, process environment export/import, and typed string conversions for integers and pointers.

## Important APIs, Types, And Functions
The constructor normalizes a variable blob to one leading `&`, copies it into `global_env`, and populates `env_Hash` with `name=value` entries. `EnvTidy` and `EnvBuildTidy` remove `authz=` data and cache the sanitized result under an internal key. `Export`, `Import`, `GetInt`, `PutInt`, `GetPtr`, `PutPtr`, and `Delimit` implement process and extended-env helpers.

## Control Flow
Construction scans `&name=value` segments in-place on the private copy, temporarily null-terminating names and values before restoring separators. `EnvTidy` returns the original environment unless a cached tidy version exists or can be built. Pointer values are serialized as two hex characters per byte of the pointer representation and deserialized with strict length/hex validation.

## State And Persistence
State is in-memory `global_env`, `global_len`, `secEntity`, and a hash table owning duplicated values with `Hash_dofree`. `Export` intentionally allocates strings for `putenv`, making process environment variables persistent for process lifetime.

## Dependencies And Integration Points
Depends on `XrdOucEnv.hh`, `XrdOucString`, C library environment APIs, and `XrdOucHash`. Security context is exposed through `secEnv()`. The environment blob integrates with protocol/plugin paths that pass opaque request metadata.

## Risks And Test Signals
Risks include no internal locking, intentionally leaked `putenv` buffers, sentinel `GetInt` value colliding with legitimate data, pointer serialization being process/endianness-specific, and authz sanitization edge cases. Test signals include parsing empty/multiple ampersand blobs, duplicate variable replacement, tidy auth removal with one or many `authz` fields, pointer round-trips, and import failure on malformed integers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.hh

## Purpose
Declares `XrdOucEnv`, a container for XRootD extended environment variables plus optional security entity context.

## Important APIs, Types, And Functions
Public methods include `Env`, `EnvTidy`, static `Export`/`Import`, `Get`, `GetInt`, `GetPtr`, `Put`, `PutInt`, `PutPtr`, `Delimit`, and `secEnv`. The object stores an `XrdOucHash<char>` for variable values, a non-owned `XrdSecEntity` pointer, and the copied raw environment string.

## Control Flow
Callers construct from a serialized variable string, then query typed values or mutate hash entries. `Env` returns the original normalized blob; `EnvTidy` returns a sanitized version suitable for contexts that should not expose authorization data.

## State And Persistence
The class owns `global_env` and hash values. The security entity pointer is non-owned. Static `Export` affects the process environment outside the object.

## Dependencies And Integration Points
Includes `XrdOucHash.hh` and forward-declares `XrdSecEntity`. It is used by plugins, request handlers, and stream/config utilities that need structured environment metadata.

## Risks And Test Signals
Risks include returning mutable internal pointers, no synchronization, ownership assumptions for `secEntity`, and caller responsibility not to free returned hash strings. Test signals are constructor/destructor memory checks, hash replacement cleanup, and callers using `EnvTidy` before logging request environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucEnv.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucErrInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucErrInfo.hh

## Purpose
Defines the central error, data, user-capability, environment, and callback carrier used between XRootD plugins and framework components.

## Important APIs, Types, And Functions
`XrdOucEI` contains fixed 2048-byte message storage, user pointer, capability flags, and code. Capability constants advertise async replies, redirects, IPv4/IPv6 support, private-network status, file URL support, redirect flags, and EC redirects. `XrdOucErrInfo` offers setters/getters for error code/text, external `XrdOucBuffer` text, user, callback object/argument, environment, trace data offset, monitoring id, and user capabilities. `XrdOucEICB` declares virtual `Done` and `Same`.

## Control Flow
Callers fill `XrdOucErrInfo` synchronously with `setErrInfo` or attach a callback/environment. Callback and environment are mutually exclusive in the API: `getEnv` returns null when callback is set, and `setEnv` clears callback state. `Reset` recycles external buffers and clears code/message. Assignment clones external buffers when present.

## State And Persistence
State is in-memory. Fixed message storage is embedded; extended data is owned as an `XrdOucBuffer*` and recycled. User string, callback object, and environment pointers are non-owned.

## Dependencies And Integration Points
Depends on `XrdOucBuffer`, `XrdSysPlatform`, and callback implementers such as `XrdOucCallBack`. It is a broad ABI surface for plugins, redirects, monitoring, and asynchronous completion.

## Risks And Test Signals
Risks include non-owned pointer lifetimes, the callback/environment union requiring disciplined use, `setErrData` offset bounds depending on caller input, fixed-buffer truncation, and lack of locking. Test signals include buffer recycling, assignment clone behavior, callback completion contract, environment handoff, capability flag propagation, and long message truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucErrInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.cc

## Purpose
Implements parsing for export path options in XRootD/OSS configuration.

## Important APIs, Types, And Functions
`ParseDefs` consumes option words from `XrdOucStream` and mutates a 64-bit flag set using a static table mapping names such as `readonly`, `forcero`, `cache`, `mig`, `mkeep`, `mlock`, `mmap`, `stage+`, `nodread`, `local`, `globalro`, `noxattrs`, and `noficl`. Each entry defines bits to remove, bits to add, and mask bits marking options explicitly set. `ParsePath` parses the path, applies defaults, validates conflicts, and inserts/updates an `XrdOucPList` in an `XrdOucPListAnchor`.

## Control Flow
`ParseDefs` loops over remaining config words and logs warnings for unknown options. `ParsePath` obtains the path, handles object-id wildcard paths beginning with `*`, merges defaults for unspecified options using the high mask half, forces readonly semantics for memory mapping on writable paths, rejects `noxattrs` combined with migration/purge, and either updates an existing matching path or inserts a new node.

## State And Persistence
No static mutable state. Persistent runtime state is the caller-owned export prefix list and per-node flag values. Config parsing changes in-memory namespace policy.

## Dependencies And Integration Points
Depends on `XrdOucExport.hh`, `XrdOucPList`, `XrdOucStream`, `XrdSysError`, and platform `strlcpy`. It integrates with OSS namespace export directives and downstream access, staging, migration, and cache policy checks.

## Risks And Test Signals
Risks include subtle default-mask logic, warnings rather than hard failures for unknown options, path truncation at 1024 bytes, and conflicts that are only partially validated. Test signals include parsing every option pair, default inheritance, repeated path update semantics, wildcard path behavior, memory-map forcing, and `noxattrs` conflict rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.hh

## Purpose
Declares export option bit definitions and the `XrdOucExport` parsing helpers.

## Important APIs, Types, And Functions
The header defines low-half setting bits and high-half explicit-mask bits such as `XRDEXP_READONLY`, `XRDEXP_FORCERO`, `XRDEXP_NODREAD`, `XRDEXP_STAGE`, `XRDEXP_MIG`, `XRDEXP_MMAP`, `XRDEXP_MLOK`, `XRDEXP_MKEEP`, `XRDEXP_PURGE`, `XRDEXP_NOXATTR`, `XRDEXP_INPLACE`, `XRDEXP_PFCACHE`, `XRDEXP_LOCAL`, `XRDEXP_GLBLRO`, `XRDEXP_NOFICL`, plus aggregate masks `XRDEXP_SETTINGS`, `XRDEXP_MEMAP`, and `XRDEXP_MIGPRG`. Static methods are `ParseDefs` and `ParsePath`.

## Control Flow
No runtime logic in the header beyond declarations. Consumers pass config streams and export-list anchors to the static parser functions.

## State And Persistence
Defines policy flags only. Parsed state lives in `XrdOucPList` instances maintained by callers.

## Dependencies And Integration Points
Includes `XrdSysError.hh`, `XrdOucPList.hh`, and `XrdOucStream.hh`. The bit layout is shared with configuration, namespace export, cache, staging, migration, and access-control code.

## Risks And Test Signals
Changing flag values or mask positions can break persisted assumptions across modules. `XRDEXP_NOLK` is currently zero because lock options are prescreened elsewhere, so callers must not infer a stored lock bit. Compile and config-parser regression tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.cc

## Purpose
Implements `XrdOucFileInfo`, a description of a logical file, target file name, size, available protocol names, ordered URLs, and validation digests.

## Important APIs, Types, And Functions
Private helper classes `XrdOucFIHash` and `XrdOucFIUrl` store linked-list digest and URL entries. `XrdOucFIHash::XrdhName` maps Adler variants to XRootD digest name `a32`. Implemented methods add digests, URLs, filenames, logical filenames, protocols, and iterate digests/URLs with `GetDigest`/`GetUrl`.

## Control Flow
`AddDigest` prepends a lowercase digest name/value and resets digest iteration to the new head. `AddUrl` inserts by increasing priority; with `fifo=true`, equal priority entries are appended, otherwise inserted before equal priority entries. `GetDigest` and `GetUrl` are stateful iterators: returning null resets the next pointer to the head for a future pass.

## State And Persistence
All state is in-memory and owned by the object: linked digest nodes, linked URL nodes, duplicated LFN/target strings, file size, and a concatenated protocol string. Destructor frees all owned allocations.

## Dependencies And Integration Points
Depends on `XrdOucFileInfo.hh` and C allocation/string APIs. It integrates with redirect/discovery code that reports multiple file locations and checksums to clients.

## Risks And Test Signals
Risks include no locking, stateful iterators that reset only after an end-of-list call, protocol membership via substring search on concatenated names, no URL/digest allocation failure handling, and potential `strncpy(user)`-style assumptions in consumers of returned country codes. Test signals include URL priority/FIFO ordering, digest name normalization, iterator reset behavior, target/LFN replacement, and protocol false-positive cases such as overlapping protocol names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.hh

## Purpose
Declares the file-resource description object used to collect alternate URLs, digests, logical names, target names, size, and protocol availability.

## Important APIs, Types, And Functions
Public API includes `AddDigest`, `AddUrl`, `AddFileName`, `AddLfn`, `AddProtocol`, `GetDigest`, `GetLfn`, `GetTargetName`, `GetSize`, `GetUrl`, `HasProtocol`, and `SetSize`. `nextFile` is a public link for chaining multiple file descriptions. Private members are digest and URL list heads/iterators, strings, size, and protocol list.

## Control Flow
Callers populate the object with metadata, iterate URLs and digests until null, and may chain objects through `nextFile`. Constructor optionally sets the LFN and initializes size to `-1` as unknown.

## State And Persistence
The object owns duplicated strings and helper nodes until destruction. It does not persist data outside the process.

## Dependencies And Integration Points
Includes C string/allocation headers and `<string>`. It is a utility contract for modules that need to return file-location metadata independent of a specific protocol.

## Risks And Test Signals
Risks include non-copy-safe raw ownership because no copy constructor/assignment is defined, public link ownership ambiguity, and iterator state embedded in the object. Test signals are destructor memory checks, unknown-size handling, and API users avoiding accidental copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.cc

## Purpose
Implements grid-mapfile loading and distinguished-name to local-user mapping for GSI/HTTP security contexts.

## Important APIs, Types, And Functions
The plugin factory `XrdOucgetGMap` returns a valid `XrdOucGMap` instance or null. The constructor parses parameters `debug`/`dbg` and `to=<seconds>`, selects a map path from argument, `GRIDMAP`, or `/etc/grid-security/grid-mapfile`, checks readability, and loads mappings. `load` parses full, begins-with (`^`), ends-with (`$`), and contains (`+`) entries into an `XrdOucHash<XrdSecGMapEntry_t>`. `dn2user` performs exact lookup first, then scans pattern entries with `FindMatchingCondition`.

## Control Flow
Loading holds an exclusive `XrdSysXSLock`, skips reload when mtime has not advanced unless forced, purges mappings before reading, parses quoted or space-delimited DNs followed by usernames, records mtime, and returns negative errno on I/O errors. Mapping optionally reloads after timeout expiry, then holds a shared lock while looking up or scanning.

## State And Persistence
State is in-memory: validity flag, mapping hash, map filename, last mtime, timeout/notafter, logger/tracer, debug flag, and shared/exclusive lock. Persistent input is the external grid-mapfile; no output is persisted.

## Dependencies And Integration Points
Depends on `XrdOucEnv`, `XrdOucGMap.hh`, `XrdOucTrace`, `XrdOucStream`, `XrdSysE2T`, POSIX `open/stat/access`, and environment variables. It integrates as a shared-library plugin through `extern "C" XrdOucgetGMap`.

## Risks And Test Signals
Risks include parser overrun on malformed lines missing a closing delimiter, username buffer overflow because `dn2user` copies `mc->user.length()` without bounding to `ulen-1`, leaked `tracer` because the destructor is empty, and `load` ignoring its `mf` parameter. Test signals include exact/prefix/suffix/contains matching, timeout reload after mtime changes, deleted map purge, malformed line handling, too-small username buffers, and plugin factory failure on unreadable maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.hh

## Purpose
Declares the grid-map interface used to translate security distinguished names into local user names.

## Important APIs, Types, And Functions
`XrdSecGMapEntry_t` stores a match value, mapped user, and match type. `XrdOucGMap` exposes `dn2user`, constructor macro `XrdOucGMapArgs`, `isValid`, and private `load`. Internal members include mapping hash, map filename/mtime, timeout, logger/tracer, debug flag, and `XrdSysXSLock`. The header also declares factory `extern "C" XrdOucgetGMap(XrdOucGMapArgs)`.

## Control Flow
Callers normally obtain an instance from the factory, check non-null validity implicitly, and call `dn2user` for connection setup. Reloading and lookup details are implemented in the `.cc`.

## State And Persistence
The class owns its mapping hash and runtime reload metadata. The mapfile is external persistent input.

## Dependencies And Integration Points
Includes `XrdOucHash`, `XrdOucString`, and `XrdSysXSLock`. The factory ABI and version-info recommendation are important for plugin loading.

## Risks And Test Signals
Risks include ABI drift in `XrdOucGMapArgs`, empty destructor despite owning a tracer pointer in the implementation, and performance sensitivity because mapping is used during physical connection creation. Test signals include factory loading, repeated mapping throughput, shared/exclusive lock behavior during reload, and version-info plugin checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.cc

## Purpose
Implements a configuration-gathering helper that extracts selected directives or directive prefixes into a tokenizable buffer for later plugin/config parsing.

## Important APIs, Types, And Functions
Private `XrdOucGatherConfData` stores an `XrdOucTokenizer`, optional `XrdSysError`, last line, wanted-match list, gathered buffer, and echo ordering. Constructors build an `XrdOucTList` of exact or prefix matches. Implemented public methods include `EchoLine`, `EchoOrder`, `Gather`, `GetLine`, `GetToken`, `hasData`, `LastLine`, message helpers, `RetToken`, `Tabs`, and `useData`.

## Control Flow
`Gather` opens a config file, attaches `XrdOucStream` with a fresh `XrdOucEnv`, scans first words after substitutions/conditionals, matches exact directives or prefixes ending in `.`, optionally trims the prefix, copies rest-of-line into `body`, appends selected lines or bodies to `theGrab`, then duplicates the result into `gBuff` and attaches the tokenizer. `GetLine` skips empty lines and records `lline`. Message helpers require an error object and print the last line before or after the diagnostic based on `EchoOrder`.

## State And Persistence
State is in-memory selected config text and tokenizer position. Persistent input is the config file; no output file is written. Existing gathered data is freed before new gather/useData.

## Dependencies And Integration Points
Depends on `XrdOucEnv`, `XrdOucStream`, `XrdOucString`, `XrdOucTList`, `XrdOucTokenizer`, `XrdSysError`, POSIX `open`, and errno. It integrates with plugins that need only their directive subset from a full xrootd config.

## Risks And Test Signals
Risks include a constructor overload bug where the `const char**` loop never increments `i`, fixed 64-byte directive and 4096-byte body buffers, message methods throwing when no error object exists, and subtle `trim_body`/`only_body` differences. Test signals include prefix and exact matching, all four gather levels, initial `parms` prepending, oversized directive/body errors, tokenizer backup, echo ordering, and vector constructor coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.hh

## Purpose
Declares `XrdOucGatherConf`, a utility for collecting selected configuration directives and then tokenizing the gathered subset.

## Important APIs, Types, And Functions
The `Level` enum controls gathered output: `full_lines`, `trim_lines`, `only_body`, and `trim_body`. Public API includes `Gather`, `GetLine`, `GetToken`, `LastLine`, `hasData`, `MsgE`, `MsgW`, `MsgfE`, `MsgfW`, `RetToken`, `Tabs`, `useData`, `EchoLine`, and `EchoOrder`. Constructors accept either a space-separated wanted string or null-terminated vector.

## Control Flow
Callers construct with desired directive names/prefixes, call `Gather` or `useData`, then iterate lines and tokens. Diagnostic helpers include the last consumed line to improve config error messages.

## State And Persistence
Hides all mutable state behind `XrdOucGatherConfData *gcP`. The object owns gathered data and match-list allocations until destruction.

## Dependencies And Integration Points
Forward-declares `XrdSysError` and `XrdOucGatherConfData`. It is a parser helper for plugin and subsystem configuration code.

## Risks And Test Signals
Risks are declaration/implementation mismatch, exceptions from message methods without `XrdSysError`, and callers retaining pointers returned by tokenizer after new gather/destruction. Test signals are API-level parse loops and message helpers for each `Level`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHash.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHash.hh

## Purpose
Declares a templated hash table with optional key/data ownership policies, replacement, lifetimes, and counted duplicate entries.

## Important APIs, Types, And Functions
`XrdOucHash_Options` defines `Hash_data_is_key`, `Hash_replace`, `Hash_count`, `Hash_keep`, `Hash_dofree`, and `Hash_keepdata`. `XrdOucHash_Item<T>` stores key, hash, data, expiry time, count, options, and next pointer. `XrdOucHash<T>` exposes `Add`, `Del`, `Find`, `Num`, `Purge`, `Rep`, and `Apply`, and includes implementation from `XrdOucHash.icc`.

## Control Flow
`Add` computes `XrdOucHashVal`, searches the bucket, optionally increments count, returns existing data unless replacing or expired, expands when load threshold is reached, and inserts a new item. `Find` removes expired entries. `Apply` scans all buckets, deletes expired or callback-negative entries, and stops on callback-positive entries. `Expand` grows table sizes by Fibonacci progression.

## State And Persistence
State is an in-memory bucket array and owned item nodes. Ownership behavior depends on options: keys may be duplicated or kept; data may be deleted, freed, kept, or aliased to key. No locking or persistence exists.

## Dependencies And Integration Points
Includes C allocation/string/time headers and external hash function `XrdOucHashVal`. Used widely by utility classes such as `XrdOucEnv` and `XrdOucGMap`.

## Risks And Test Signals
Risks include complicated ownership flags, no null checks after constructor allocation, no synchronization, counted delete semantics independent of the ignored `Del` option parameter, and exceptions thrown as integer `ENOMEM`. Test signals include replacement and expiry behavior, every ownership option combination under sanitizers, expansion rehashing, `Apply` deletion while iterating, and duplicate count add/delete cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHash.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHashVal.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHashVal.cc

## Purpose
Implements the string hash function used by `XrdOucHash`.

## Important APIs, Types, And Functions
`XrdOucHashVal(const char*)` hashes a null-terminated string by delegating to `XrdOucHashVal2(const char*, int)`. `XrdOucHashVal2` returns the raw bytes for short keys up to `sizeof(unsigned long)` and otherwise XORs machine-word chunks seeded by key length, returning 1 instead of zero.

## Control Flow
For short names the function copies bytes into an `unsigned long`. For longer names it handles a leading remainder, then walks word-sized blocks via `memcpy` and XOR accumulation.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses C string headers and is declared externally by `XrdOucHash.icc`. The hash result is bucketed by `XrdOucHash<T>`.

## Risks And Test Signals
Risks include architecture-dependent results due to word size and endian layout, weak collision resistance from XOR folding, and reliance on callers passing valid buffers of `KeyLen` bytes. Test signals include stable hash distribution for representative keys on supported architectures, zero-hash avoidance, and consistency between `XrdOucHashVal` and `XrdOucHashVal2(strlen)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHashVal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucIOVec.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucIOVec.hh

## Purpose
Defines generic file I/O vector structures shared by SFS, OFS, OSS, and checkpoint interfaces.

## Important APIs, Types, And Functions
`XrdOucIOVec` stores file `offset`, byte `size`, arbitrary `info`, and data buffer pointer. `XrdOucIOVec2` is a convenience subclass constructor filling those fields. `struct iov : public XrdOucIOVec` restores an older intended type name while preserving layout compatibility.

## Control Flow
No logic beyond `XrdOucIOVec2` construction. Callers build arrays of these structures and pass them to vector I/O or checkpoint APIs.

## State And Persistence
Each struct is transient parameter state. It does not own the buffer pointer or persist anything.

## Dependencies And Integration Points
No external includes. It is an ABI/layout bridge for old signatures using `struct iov` and newer code using `XrdOucIOVec`.

## Risks And Test Signals
Risks include buffer lifetime/ownership ambiguity, signed `int size` limits for large I/O, and assumptions that subclass layout remains identical to the base. Test signals include compile ABI checks with `sizeof(iov) == sizeof(XrdOucIOVec)`, vector read/write behavior, and checkpoint code using both type names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucIOVec.hh -->

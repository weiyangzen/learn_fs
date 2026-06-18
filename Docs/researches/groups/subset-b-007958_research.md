# Research: subset-b-007958

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRange.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRange.hh

Purpose: defines `XrdOucRange`, a small generic range descriptor used to pass file offsets, byte counts, and caller-defined metadata through XRootD storage and file-system interfaces. The header also standardizes `XrdOucRangeList` as `std::vector<XrdOucRange>` for pre-read and vectored I/O APIs.

Important APIs, types, and functions: `XrdOucRange` exposes public `offset`, `size`, and `info` fields plus a value constructor. `XrdOucRangeList` is the only named container alias. The destructor is virtual, allowing derived range records to be passed through base pointers if a component extends the record.

Control flow: there is no algorithmic flow; callers construct range objects, populate fields directly or through the constructor, and pass vectors to consumers. The `info` field is deliberately opaque so sfs/ofs/oss layers can attach local semantics without another type.

State and persistence: all state is caller-owned in memory. No locking, allocation beyond the vector container, or persistence is involved.

Dependencies and integration points: depends only on `<vector>`. The comment identifies integration with sfs, ofs, and oss pre-read paths where file offsets and lengths must be batched across module boundaries.

Risks and test signals: `size` is an `int`, so very large single ranges need splitting by callers. `info` is untyped and can become ambiguous between producers and consumers. Useful tests are compile-time API compatibility, vector handoff through pre-read paths, and bounds handling for zero or negative sizes at consuming layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRange.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRash.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRash.hh

Purpose: declares a templated radix-tree cache/table, `XrdOucRash<K,V>`, for binary integral keys and values. It provides hash-like add, replace, lookup, delete, purge, and scan behavior while indexing by nibbles of the key rather than computing a conventional hash.

Important APIs, types, and functions: `XrdOucRash_Options` controls replacement and duplicate-count semantics. `XrdOucRash_Item` stores key, value, expiration time, and duplicate count. `XrdOucRash_Tent` owns either a child table or one item. Public table methods are `Add()`, `Rep()`, `Del()`, `Find()`, `Apply()`, `Purge()`, and `Num()`. The implementation is included from `XrdOucRash.icc`.

Control flow: `Add()` looks up an existing key, optionally increments a count, returns existing unexpired data unless replacement is requested, or inserts a newly allocated item. `Find()` lazily expires stale entries. `Del()` decrements counted entries before removing them. `Apply()` recursively visits all 16-way child tables and lets a callback delete, continue, or stop at an item.

State and persistence: state is a root array of 16 entries, dynamically allocated child arrays, item objects, and `rashnum`. Expiration is wall-clock based through `time(0)`. There is no persistence and no internal locking; the header explicitly requires external serialization for multi-threaded use.

Dependencies and integration points: depends on `<ctime>`, `<sys/types.h>`, errno values from the included implementation, and `XrdSysPlatform.hh` endian definitions for key conversion. It is useful for small in-memory caches keyed by fixed-width binary identifiers.

Risks and test signals: replacement of an expired existing item calls `Set()` with `KeyTime` still zero in the implementation, so lifetime refresh on expired replacement should be checked. The structure is not MT-safe, recursive deletion depends on ownership in `XrdOucRash_Tent`, and key type assumptions are limited to integral-like objects fitting into 64 bits. Tests should cover add/find/replace, expiration, `Rash_count`, deletion during `Apply()`, endian behavior, and purge cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRash.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.cc

Purpose: implements request identifier generation and ownership decoding. IDs combine a local or encoded network prefix, CRC hash, timestamp, and monotonically increasing sequence number so request flows can identify origin and distribute keys across slots.

Important APIs, types, and functions: constructors build the ID format string and prefix; `ID()` emits the next ID under `myMutex`; `isMine()` compares an incoming ID with `reqPFX` and can decode alternate host/port information; `Index()` maps arbitrary key bytes to a modulo bucket using `XrdOucCRC::CRC32`.

Control flow: the default constructor formats the process ID and epoch time into a short local prefix and printf template. The address-aware constructor uses `XrdNetUtils::Encode()` to encode a socket address and port, falls back to port/time formatting if encoding fails, hashes the prefix, and builds a longer template. `ID()` increments `reqNum`, writes the formatted ID, and returns either the full buffer or the post-prefix internal part depending on `reqIntern`. `isMine()` first checks the prefix, otherwise tries to decode a host from the request ID.

State and persistence: persistent process-local state includes duplicated strings for the prefix and format, sequence number, and mutex. IDs are not persisted across process restarts; uniqueness relies on process/time/address prefix plus sequence. The destructor intentionally leaves static-style allocations to process exit.

Dependencies and integration points: depends on `XrdSysMutex`, `XrdNetAddr`, `XrdNetUtils`, `XrdOucCRC`, libc time/PID/string calls, and socket address types. It integrates with routing, request tracking, and any code needing stable modulo assignment through `Index()`.

Risks and test signals: callers must provide `ID()` buffers large enough for the formatted string despite only a comment documenting `blen >= 48`. `snprintf(buff, blen-1, ...)` leaves one byte unused and depends on positive lengths. `reqNum` can eventually wrap. Tests should verify format stability, concurrent `ID()` uniqueness, `isMine()` for local and remote IDs, fallback constructor behavior, and `Index()` consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.hh

Purpose: declares `XrdOucReqID`, the request ID helper used to generate per-process or per-address request identifiers and to test whether an ID belongs to the current endpoint.

Important APIs, types, and functions: public methods are `ID(char*, int)`, `isMine(char*, int&, char*, int)`, `PFX()`, and static `Index(int, const char*, int)`. Constructors support a local PID/time identity or a network-address identity. Private fields hold the mutex, prefix length, internal return offset, duplicated prefix/format strings, and sequence counter.

Control flow: users construct an instance once, repeatedly call `ID()` to fill caller buffers, use `PFX()` when a prefix is needed externally, and call `isMine()` to split local IDs from remote IDs while optionally discovering the remote hostname.

State and persistence: the class owns process-local mutable sequence state protected by `XrdSysMutex`. It stores C string pointers allocated by the implementation and does not expose copy/move control, so instances should not be copied.

Dependencies and integration points: includes platform string compatibility and `XrdSysPthread.hh`, forward-declares `XrdNetSockAddr`, and is implemented by the companion `.cc` using XrdNet and CRC utilities.

Risks and test signals: the header does not encode buffer size in the type system, and the default destructor does not free duplicated strings. Tests should focus on ABI compatibility, object lifetime expectations, concurrent use, and behavior with both constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSFVec.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSFVec.hh

Purpose: defines `XrdOucSFVec`, a compact sendfile vector entry for mixed file-descriptor and memory-buffer output segments.

Important APIs, types, and functions: the struct contains a union of `buffer` and `offset`, plus `sendsz`, `fdnum`, and enum constant `sfMax = 16`. A negative `fdnum` means the union is interpreted as a memory buffer pointer; otherwise it is a file offset for the descriptor.

Control flow: there is no function flow. Callers build an array of up to `sfMax` entries and pass it to sendfile-style code that chooses between file and memory segments based on `fdnum`.

State and persistence: state is transient caller-owned memory. No allocation, locking, or persistence exists.

Dependencies and integration points: depends on `<unistd.h>` for `off_t` and integrates with xrd, sfs, ofs, and oss components that need scatter/gather sendfile descriptions.

Risks and test signals: the union requires consumers to obey the `fdnum` convention exactly. `sendsz` is an `int`, so large fragments must be split. Tests should cover mixed buffer/file vectors, maximum element count, zero-length elements, and correct interpretation when `fdnum < 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSFVec.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.cc

Purpose: implements the `XrdOucSHA3` SHA-3 and SHAKE primitives, adapted from tiny_sha3, including Keccak-f[1600], fixed-length SHA3 digests, and extensible-output SHAKE reads.

Important APIs, types, and functions: `sha3_keccakf()` is the 24-round permutation; `Calc()` performs one-shot hashing; `Init()`, `Update()`, and `Final()` implement streaming SHA3; `shake_xof()` and `SHAKE_Out()` implement SHAKE output after the same absorb phase.

Control flow: `Init()` clears the 1600-bit state and computes the rate from digest length. `Update()` XORs input bytes into the state and permutes when the rate fills. `Final()` applies SHA3 padding bytes `0x06` and `0x80`, permutes once, and copies `mdlen` bytes. `SHAKE_Out()` lazily applies SHAKE padding `0x1F` on first output, then streams bytes and permutes on rate boundaries.

State and persistence: all state lives in caller-provided `sha3_ctx_t`. The one-shot API uses a stack context. No heap state, globals, locks, or persistence are used. Big-endian platforms perform explicit byte-order conversion around the permutation.

Dependencies and integration points: depends on `XrdOucSHA3.hh`, fixed-width integer types, compiler byte-order macros, and callers needing checksums or extendable pseudo-random output without OpenSSL.

Risks and test signals: there is no validation that `mdlen` is one of the documented enum values, so unsupported rates could corrupt the context contract. `Final()` is terminal for SHA3 but does not mark the context finalized. Tests should use FIPS 202 vectors for all SHA3 lengths, SHAKE128/SHAKE256 vectors across repeated `SHAKE_Out()` calls, empty input, multi-update equivalence, and big-endian builds if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.hh

Purpose: declares the public SHA3/SHAKE interface and context structure used by XRootD utility code.

Important APIs, types, and functions: `sha3_ctx_t` contains the 200-byte Keccak state as bytes or 64-bit words plus rate, digest length, cursor, and xof flag. `MDLen` enumerates byte lengths for SHA3-128/224/256/384/512. Public static methods are `Calc()`, `Init()`, `Update()`, `Final()`, `SHAKE128_Init()`, `SHAKE256_Init()`, `SHAKE_Update()`, and `SHAKE_Out()`.

Control flow: callers either use `Calc()` for a complete digest or call init/update/final manually. SHAKE users initialize with one of the SHAKE helpers, absorb with `SHAKE_Update()`, and call `SHAKE_Out()` one or more times.

State and persistence: the header exposes a POD-like context so callers can allocate it on the stack or embed it. There is no class instance state.

Dependencies and integration points: depends on `<stddef.h>` and `<cstdint>`. The implementation provides a small internal crypto primitive without requiring external crypto libraries.

Risks and test signals: exposing internal context makes ABI and layout changes visible to callers. The enum names are digest byte lengths despite comments saying bits-to-bytes. Tests should verify header/API compatibility and known-vector behavior through both one-shot and streaming paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSHA3.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.cc

Purpose: implements a bit-vector stream ID allocator with optional locking and optional overflow delegation to a global `XrdOucSid` pool.

Important APIs, types, and functions: the constructor allocates and initializes `sidVec`; `Obtain()` finds and clears a free bit; `Release()` sets a bit back; `Reset()` marks all local IDs free; the destructor frees the vector.

Control flow: `Obtain()` locks when configured, advances `sidFree` past full bytes, chooses the lowest available bit through a nibble lookup table, clears that bit, and returns the calculated short ID. If the local vector is exhausted and `globalSid` exists, it obtains from the global pool and offsets by `sidMax`. `Release()` reverses this for local IDs or delegates back to the global pool after subtracting `sidMax`.

State and persistence: state is in-memory only: the mutex, local free-bit vector, current free-byte cursor, size/max values, global pool pointer, and lock flag. No IDs persist across object destruction or reset.

Dependencies and integration points: depends on `XrdSysPthread.hh` through the header and libc allocation/string routines in practice. It integrates with connection/session stream management where small integer stream IDs need reuse.

Risks and test signals: the constructor computes `sidSize` as `(numSid / 8) + ((numSid % 8 ? 1 : 0) * 8)`, which adds eight bytes rather than one for non-multiples of eight; this overallocates and changes `sidMax`. `Release()` does not reject negative or duplicate local IDs before setting bits. Tests should cover non-multiple sizes, exhaustion and global fallback, duplicate release, reset, signed short overflow behavior, and MT contention when `mtproof` is true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.hh

Purpose: declares `XrdOucSid`, a fast stream ID generator backed by a bit vector.

Important APIs, types, and functions: `theSid` overlays a `short` and two bytes for protocol-friendly SID transfer. Public methods are `Obtain()`, `Release()`, and `Reset()`. The constructor accepts local capacity, optional internal locking, and optional global overflow pool.

Control flow: a connection can allocate a local SID object sized for expected concurrent streams and pass a global pool for overflow. IDs should be released when streams complete so bits can be reused.

State and persistence: private state includes an `XrdSysMutex`, global pool pointer, allocated bit vector, free cursor, vector sizing, max ID count, and lock flag. State is process memory only.

Dependencies and integration points: includes `XrdSysPthread.hh` and is used by stream/multiplexing code that exchanges two-byte IDs.

Risks and test signals: the API accepts raw `theSid*` casts, so endian and signed-short handling must match protocol expectations. The class is not copy-safe. Tests should verify byte representation, allocation order, release reuse, and local/global ID boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSid.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.cc

Purpose: implements site-name normalization and exports the result as `XRDSITE`.

Important APIs, types, and functions: `XrdOucSiteName::Set()` duplicates the supplied name, truncates it to `maxlen`, replaces characters outside `[A-Za-z0-9_-:]` with `.`, exports it through `XrdOucEnv::Export()`, and returns the allocated string.

Control flow: null input becomes an empty string. Non-null input is copied before mutation. The function then walks each retained byte and sanitizes invalid characters.

State and persistence: the duplicated string is intentionally retained because `XrdOucEnv::Export()` installs it into the process environment. Persistent state is the process environment variable, not a file.

Dependencies and integration points: depends on `<cctype>`, `<cstring>`, `XrdOucEnv`, and the declaration header. It integrates with startup/configuration code that needs a bounded site label exposed to child processes and plugins.

Risks and test signals: `isalnum(site[i])` should ideally cast to unsigned char for non-ASCII bytes. Each call allocates a new string and returns a pointer that should not be freed after export. Tests should cover truncation, allowed punctuation, replacement behavior, null input, and environment visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.hh

Purpose: declares the one-method `XrdOucSiteName` utility for setting a sanitized XRootD site name.

Important APIs, types, and functions: `static const char *Set(const char *name, int maxlen=15)` is the only functional API. Constructor and destructor are trivial.

Control flow: users call `Set()` during configuration or process initialization; implementation handles normalization and environment export.

State and persistence: no object state exists. Side effects are process-environment state managed by the implementation.

Dependencies and integration points: the header has no includes and integrates with any code wanting to publish `XRDSITE` without depending directly on `XrdOucEnv` in the caller.

Risks and test signals: callers must understand the returned pointer lifetime follows environment export behavior. Tests should compile the header standalone and verify default maximum length through the `.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStats.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStats.hh

Purpose: provides a tiny stats increment helper that hides whether the build has atomic operations or must serialize increments through a mutex.

Important APIs, types, and functions: macros `_statsADD` and `_statsINC` select `AtomicAdd`/`AtomicInc` when `HAVE_ATOMICS` is defined, otherwise lock `statsMutex`. `XrdOucStats::Bump()` overloads increment or add to `int` and `long long` counters.

Control flow: callers pass a counter reference to `Bump()`. The method expands to an atomic or lock-protected update and returns immediately.

State and persistence: the only object state is `statsMutex` for non-atomic builds. Counters are owned by callers and are in-memory only.

Dependencies and integration points: depends on `XrdSysAtomics.hh` and `XrdSysMutex` availability from that include path. It integrates with modules that keep simple process-local counters.

Risks and test signals: macro bodies are not wrapped in `do { } while (0)`, so unusual call contexts could surprise maintainers. Atomic semantics depend on the platform implementation. Tests should compile both atomic and non-atomic configurations and stress concurrent increments for lost updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.cc

Purpose: implements `XrdOucStream`, a file-descriptor stream wrapper used for line/token parsing, configuration-file processing, variable substitution, conditional/continuation directives, command execution, and optional capture/echo of effective configuration.

Important APIs, types, and functions: construction parses optional instance metadata. `Attach()`, `AttachIO()`, `Close()`, `Detach()`, and `Drain()` manage descriptors and child processes. `Exec()` starts a child with stdout/stdin/stderr routing. `GetLine()`, `GetToken()`, `GetWord()`, `GetFirstWord()`, `GetMyFirstWord()`, `GetRest()`, and `RetToken()` drive parsing. `Put()`, vector `Put()`, `PutLine()`, and `Wait4Data()` handle output and polling. Private helpers implement config capture, continuations (`docont*`), `if/else/fi`, `set`/`setenv`, file-value reads, and `$var` substitution.

Control flow: input is buffered and split into null-terminated records by `GetLine()`. `GetWord()` skips blanks/comments, handles backslash continuations, substitutes variables through `XrdOucEnv`, and advances across directory/file continuations. `GetMyFirstWord()` adds component-specific processing for `continue`, `if`, `else`, `fi`, `set`, and `setenv`. `Exec()` creates pipes as requested, serializes fork with `forkMutex`, sets process groups, redirects descriptors, exports environment variables from `myEnv`, and `execv()`s the command. `Close()` drains children unless held, closes descriptors, frees buffers, and emits pending captured config lines.

State and persistence: state includes file descriptors, buffer pointers and cursors, parser flags, child PID, last error, line/capture buffers, environment pointer, instance metadata in `StreamInfo`, and static capture string `theCFG`. Persistent side effects are limited to environment exports, spawned process effects, and optional global capture text.

Dependencies and integration points: depends on POSIX I/O, `poll`, `fork/exec/wait`, `fcntl`, `stat`, `XrdOucEnv`, `XrdOucNSWalk`, `XrdOucString`, `XrdOucTList`, `XrdOucUtils::doIf`, `XrdSysError`, `XrdSysFD`, logging, and platform wrappers. It is a central integration point for XRootD config readers and helper process execution.

Risks and test signals: `Put(const char*, int)` writes `dlen` on every retry instead of the remaining `dcnt`, so short writes can duplicate bytes. `Exec(const char*)` splits only on spaces and does not honor shell quoting. `Drain()` kills the whole child process group with SIGKILL. Parser state for nested conditionals is limited and comments say `continue` cannot be nested. Variable substitution uses fixed 512-byte buffers and limited variable-name parsing. Tests should cover long lines, comments, tabs, continuations, directory continuation filtering, `if/else/fi` host/name/exec matching, `set` and `setenv` variants including `<file`, substitution errors, process stdout/stderr routing, partial writes, and child cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.hh

Purpose: declares the stream abstraction used by XRootD configuration and utility code to read/write file descriptors, parse tokenized records, execute helper commands, and capture effective configuration.

Important APIs, types, and functions: public APIs include descriptor management (`Attach`, `AttachIO`, `Close`, `Detach`, `FDNum`, `FENum`), command execution (`Exec`, `Drain`, `isAlive`), parsing (`GetLine`, `GetToken`, `GetWord`, `GetFirstWord`, `GetMyFirstWord`, `GetRest`, `RetToken`), output (`Put`, `PutLine`, `Flush`), error/capture (`LastError`, `Echo`, `noEcho`, `Capture`), and configuration helpers (`SetEnv`, `SetEroute`, `Tabs`, `Wait4Data`).

Control flow: callers typically attach a descriptor or execute a command, then consume records/tokens. Configuration readers use `GetMyFirstWord()` to process local directives and variable assignments while normal stream users can use lower-level token methods.

State and persistence: the class owns descriptors unless detached, owns parser buffers, stores a child PID for executed commands, and references external error and environment objects. Static `theCFG` points to an optional capture string shared across streams.

Dependencies and integration points: forward-declares `XrdOucEnv`, `XrdOucString`, and `XrdOucTList`, includes `XrdSysError`, and depends on POSIX signal/types. It is ABI-sensitive, as shown by reserved fields and the `StreamInfo *myInfo` comment.

Risks and test signals: ownership rules around attached descriptors, child processes, and static capture require careful lifecycle tests. The API exposes mutable internal line buffers that are invalidated by subsequent reads. Tests should cover standalone header use, destructor cleanup, `Detach()` semantics, and capture toggling across multiple streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStream.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.cc

Purpose: implements `XrdOucString`, a lightweight mutable C-string wrapper with manual capacity management, substring search, wildcard matching, insertion, replacement, erasure, case conversion, formatting, tokenization, numeric parsing, and overloaded operators.

Important APIs, types, and functions: private `adjust()` normalizes ranges and `bufalloc()` manages `realloc()` with optional block sizing. Constructors, `assign()`, `setbuffer()`, and destructor manage ownership. Search methods implement `find()`/`rfind()`/`endswith()`/`matches()`. Modifiers include `keep()`, `insert()`, `replace()`, `erase()`, `lower()`, `upper()`, `hardreset()`, `reset()`, and `tokenize()`. Operators implement assignment, concatenation, equality, stream output, and numeric conversion helpers.

Control flow: most mutations compute an effective range, resize only when capacity is insufficient, then use `memmove`, `memcpy`, or `strncpy` to mutate the internal null-terminated buffer. Replacement handles shorter replacements from left to right and longer replacements from right to left to avoid overwriting source text. Formatting uses a growing `vsnprintf()` loop on non-Windows builds.

State and persistence: each object owns `str`, `len`, and `siz`; static `blksize` controls allocation granularity process-wide. There is no locking or persistence. `setbuffer()` transfers ownership of a malloc-compatible buffer into the object.

Dependencies and integration points: depends on `XrdOucString.hh`, C stdio/string/limits, and varargs formatting. It is used broadly where legacy code wants a lighter mutable string than `std::string` and is also used by `XrdOucStream` capture logic.

Risks and test signals: `replace()` rejects null `s2`, but `erase(const char*)` calls `replace(s, 0, ...)`, so erase-by-substring currently returns no removal. `reset()` can read before the buffer when `len` is zero. `bufalloc()` leaves the old pointer intact only if callers do not overwrite it after failed `realloc`; several callers assign directly. Tests should cover empty strings, failed/large allocation behavior where practical, insert at boundaries, replace shorter/equal/longer, erase substring, `reset()` on empty strings, wildcard matching, tokenization with empty tokens, and numeric parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.hh

Purpose: declares a legacy mutable string class used across XRootD utility code as a C-string-compatible owned buffer with convenience operations.

Important APIs, types, and functions: the class exposes `c_str()`, `length()`, `capacity()`, indexed access, find/rfind, prefix/suffix checks, wildcard `matches()`, tokenization, resize/append/assign/insert/replace/erase/case/reset operations, assignment and concatenation operators, equality operators, digit/atoi helpers, and static block-size controls. `STR_NPOS` is `-1`.

Control flow: callers generally construct from a char pointer or empty capacity, mutate through append/insert/replace, and pass `c_str()` to older APIs. Optional `form()` methods provide printf-style formatting on non-Windows platforms.

State and persistence: private state is the owned char buffer, current length, capacity, and static allocation granularity. No persistence or synchronization is provided.

Dependencies and integration points: includes `XrdSysHeaders.hh` and C stdlib/stdio/varargs. Stream output operator and free `operator+` overloads integrate it with C++ stream and concatenation syntax.

Risks and test signals: many methods pass `XrdOucString` by value, creating extra copies and depending on correct copy semantics. `operator[]` aborts on invalid indexes. Tests should verify ABI, null-string handling, copy/assignment independence, and compatibility with functions expecting mutable C strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucString.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.cc

Purpose: implements file-based serialization locks using `fcntl()` record locks, with optional shared mode, non-blocking mode, and unlink-on-destruction for exclusive lock files.

Important APIs, types, and functions: constructors open or build lock-file paths; `Serialize()` acquires read or write locks; `Release()` unlocks; static `Serialize(int, int)` and `Release(int)` operate on external descriptors; destructor optionally unlinks and closes.

Control flow: construction opens the lock file with user-write/group/world-read permissions and may immediately call `Serialize()`. `Serialize()` builds an `FLOCK_t`, chooses `F_SETLK` or `F_SETLKW`, retries on `EINTR`, sets `lokUL` if an exclusive unlink-on-release lock was requested, and records `lokRC`. `Release()` unlocks and disables pending unlink.

State and persistence: object state is the lock filename, descriptor, unlink flag, and last error. Lock state is kernel-managed against the open file description. The lock file may persist unless `Unlink` is used and the object is destroyed while locked.

Dependencies and integration points: depends on POSIX `open`, `fcntl`, `close`, `unlink`, `sys/stat`, `MAXPATHLEN`, and `XrdSysPlatform.hh` for `FLOCK_t`. It integrates with process-level singleton/critical-section code.

Risks and test signals: the path-concatenating constructor uses `strcpy()` into a fixed `MAXPATHLEN+1` buffer without length checks. `Release()` returns `0` on unopened object while static `Release()` returns `EBADF`, so callers must distinguish APIs. Tests should cover shared/exclusive contention between processes, non-blocking failure, EINTR retry, unlink behavior, long paths, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.hh

Purpose: declares `XrdOucSxeq`, a serialization lock wrapper around lock files and file descriptors.

Important APIs, types, and functions: option constants are `noWait`, `Share`, `Unlink`, and `Lock`. Public methods include `Detach()`, object and static `Release()`, object and static `Serialize()`, `lastError()`, and two constructors for direct paths or suffix/dir composition.

Control flow: callers construct a lock object, optionally with immediate locking, use `Serialize()`/`Release()` to bracket critical work, and let the destructor close/unlink according to state. `Detach()` transfers descriptor ownership out of the object.

State and persistence: private members record filename, descriptor, unlink request, and last result. The file system lock file is the persistent coordination point.

Dependencies and integration points: the header has no includes beyond its guard, keeping the declaration lightweight for utilities needing cross-process serialization.

Risks and test signals: copy operations are not disabled despite owning a descriptor and filename. Tests should ensure objects are not copied accidentally, and should verify `Detach()` prevents destructor close of externalized descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTList.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTList.hh

Purpose: defines simple linked-list utility nodes and RAII helpers for text plus small numeric payloads.

Important APIs, types, and functions: `XrdOucTList` stores `next`, duplicated `text`, and a union payload (`dval`, `ival`, `sval`, `cval`, or `val`) with constructors for each payload shape. `XrdOucTListHelper` clears a list anchored by a pointer on destruction. `XrdOucTListFIFO` tracks first/last and supports `Add()`, `Clear()`, and `Pop()`.

Control flow: callers allocate nodes and link them manually or through FIFO `Add()`. Destructors free only the node's own text; list-wide cleanup is performed by helper/FIFO or caller loops.

State and persistence: all state is heap memory owned by the list users. There is no locking or persistence.

Dependencies and integration points: depends on C allocation/string headers. It is used by parsers such as `XrdOucStream` to hold suffix lists and by other utility code needing lightweight text-value lists.

Risks and test signals: `XrdOucTListFIFO::Pop()` returns the full list and clears both FIFO anchors, not a single node. Nodes do not recursively delete `next`, so ownership must be explicit. Tests should cover each constructor, helper cleanup, FIFO add/pop/clear semantics, and null text handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.cc

Purpose: implements third-party-copy CGI helpers that generate and filter `tpc.*` query fragments for source and destination negotiation.

Important APIs, types, and functions: static key names define all supported `tpc.*` parameters. `cgiC2Dst()` builds destination-side CGI with key, source, logical file name, checksum, stream count, delegation host, source/target protocols, push, and delegation-on flag. `cgiC2Src()` builds source-side CGI with key, destination host, and optional TTL. `cgiD2Src()` forwards origin information. `cgiHost()` parses optional user and port, resolves host canonical name through `XrdNetAddr`, and `copyCGI()` copies user CGI keys while filtering system prefixes.

Control flow: CGI builders validate required parameters and buffer length, normalize host specs through `cgiHost()`, then append parameters with `snprintf()` while tracking remaining buffer space. `copyCGI()` skips leading ampersands, treats tab as the input separator, requires an equals sign, filters `tpc.`, `xrd.`, and `xrdcl.` prefixes, and emits ampersand-separated output.

State and persistence: only static constant key strings are global. Per-call state is stack/heap memory owned by `tpcInfo`, which frees a duplicated hostname. No persistence or locking exists.

Dependencies and integration points: depends on `XrdNetAddr` for hostname normalization and is consumed by XRootD TPC flows that pass CGI strings between clients, sources, destinations, and delegates.

Risks and test signals: the final overflow test compares only the last `snprintf()` result with remaining length, so earlier truncation can be hard to distinguish. Inputs are inserted without URL encoding. `cgiHost()` resolution can block or fail depending on DNS. Tests should cover IPv6 bracket parsing, user@host:port, buffer truncation, optional parameter combinations, filtering in `copyCGI()`, and canonical host failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.hh

Purpose: declares the static utility interface for third-party-copy CGI parameter construction and filtering.

Important APIs, types, and functions: public methods are `cgiC2Dst()`, `cgiC2Src()`, `cgiD2Src()`, and `copyCGI()`. Public static string constants name CGI keys such as `tpc.key`, `tpc.src`, `tpc.dst`, `tpc.ttl`, and `tpc.dlgon`. Private `tpcInfo` stores parsed user/host/port fragments, and `cgiHost()` performs normalization.

Control flow: callers choose the helper based on copy direction and role, provide a caller-owned output buffer, and receive either that buffer or a string beginning with `!` describing invalid parameters or generation failure.

State and persistence: no instance state exists. Static key strings are read-only process globals.

Dependencies and integration points: includes `<cstdlib>` for `free()` in `tpcInfo` destructor and integrates with TPC protocol and CGI handling code.

Risks and test signals: error signaling as a string pointer requires callers to check for leading `!` rather than errno/status. Tests should verify all declared static key names match protocol expectations and are initialized by the `.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTUtils.hh

Purpose: provides templated utility functions that cannot live in non-template `XrdOucUtils`, currently string splitting and case-insensitive map lookup.

Important APIs, types, and functions: `splitString(Container&, const std::string&, const std::string&)` appends non-empty delimited substrings via `emplace_back()`. `caseInsensitiveFind<T>()` scans a `std::map<std::string,T>` comparing each key lowercased against a caller-supplied lower-case search key.

Control flow: `splitString()` repeatedly calls `find()` from the current start position and skips empty tokens. `caseInsensitiveFind()` delegates to `std::find_if()` and `std::equal()` with a lowercase comparison lambda.

State and persistence: no state is stored. All output is written into caller-provided containers or returned iterators.

Dependencies and integration points: depends on `<string>`, `<map>`, and `<algorithm>`. It integrates with code using STL containers while preserving XRootD utility naming.

Risks and test signals: `splitString()` with an empty delimiter can loop incorrectly because `delimiter.size()` is zero. `caseInsensitiveFind()` uses `std::equal()` without checking equal string lengths, so a shorter search key can be treated as matching a longer map key depending on iterator range assumptions. Tests should cover empty delimiters, consecutive delimiters, missing/partial case-insensitive keys, and mixed-case maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTable.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTable.hh

Purpose: implements a fixed-capacity templated pointer table with optional string keys and a free-list allocator for numeric slots.

Important APIs, types, and functions: constructor allocates `OucTable` entries and initializes free-list links. Public methods include `Alloc()`, `Insert()`, `Find()`, `Item()`, `Next()`, `Apply()`, `Remove()`, and `Delete()`. Each entry stores either an item key or next-free index in a union.

Control flow: `Alloc()` pops a slot from the free list and extends `curnum`. `Insert()` places an item and duplicated key in a chosen or allocated slot. `Find()` scans live entries for a matching key. `Remove()` frees the key, returns the item without deleting it, pushes the slot onto the free list, and may shrink the current high-water mark. `Delete()` wraps `Remove()` and deletes the returned item.

State and persistence: state is an owned heap array, free-list head, maximum size, and current high-water mark. Items are heap pointers owned by the table until removed. No persistence or locking exists.

Dependencies and integration points: depends on C allocation/string headers and is useful where legacy code needs stable small integer handles for object pointers.

Risks and test signals: `Insert()` calls `strdup(key)` even when `key` is null, which is undefined or crashes on typical libc. The shrink loop in `Remove()` checks `Table[curnum]` after decrement choices and needs boundary coverage. Tests should cover capacity exhaustion, keyed and unkeyed insertion, null keys, removal/deletion ownership, `Next()` iteration, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTable.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.cc

Purpose: implements an in-place tokenizer for caller-owned character buffers, providing line extraction, blank-delimited tokens, optional lowercasing, tab handling, and one-token rollback.

Important APIs, types, and functions: `Attach()` resets the tokenizer to a buffer. `GetLine()` returns the next line after trimming leading blanks and optionally tabs, replacing the line terminator with null. `GetToken()` returns the next blank-delimited token and optionally the rest of the line. `RetToken()` restores the previous token boundary once.

Control flow: `GetLine()` advances `buff` over newline-separated records and sets `tnext` to the current line start. `GetToken()` skips spaces from `tnext`, lowercases if requested while scanning, null-terminates the token, advances `tnext`, and fills `rest` after skipping spaces. `RetToken()` changes the token's trailing null back to a space when possible and resets the cursor.

State and persistence: state is four fields pointing into the caller's mutable buffer plus a tab-conversion flag. The tokenizer does not allocate or persist data and modifies the input buffer destructively.

Dependencies and integration points: depends on C ctype/string headers and the declaration header. It is a lower-overhead counterpart to `XrdOucStream` for tokenizing existing memory.

Risks and test signals: the `Tabs()` comment says `0` converts tabs, but implementation converts tabs when `notabs` is true, set by `Tabs(0)`. Leading tabs are only skipped in that mode. Tests should cover empty buffers, trailing lines without newline, tabs on/off, rollback after end-of-line, `rest` behavior, and lowercasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.hh

Purpose: declares a simple destructive tokenizer for mutable memory buffers.

Important APIs, types, and functions: constructor calls `Attach()`. Public methods are `Attach()`, `GetLine()`, `GetToken()`, `RetToken()`, and `Tabs()`. Private fields track the input buffer, last token, next token cursor, and tab conversion flag.

Control flow: users attach a mutable buffer, iterate lines, then tokens within a line. One call to `RetToken()` can push back the last returned token.

State and persistence: all parser state points into the caller-provided buffer and is invalid if that buffer is freed or replaced. No data is persisted.

Dependencies and integration points: the header is standalone and integrates with configuration or protocol parsing code that can safely mutate its input.

Risks and test signals: because tokenization writes null bytes into the source, callers must not pass string literals or shared immutable buffers. Tests should compile the header standalone and verify object reuse through `Attach()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTokenizer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.cc

Purpose: implements binary-to-hex formatting for tracing.

Important APIs, types, and functions: `XrdOucTrace::bin2hex(char *inbuff, int dlen, char *buff)` converts up to 24 bytes into lower-case hex pairs with spaces after every four bytes and at the end. If no output buffer is supplied, it uses a static 56-byte buffer.

Control flow: the method clamps `dlen`, iterates input bytes, writes two hex chars per byte, adds spacing, null-terminates, and returns the static buffer pointer.

State and persistence: the only state is the function-static output buffer used when `buff` is null. That static buffer is overwritten on each call and is not thread-safe.

Dependencies and integration points: depends on `XrdOucTrace.hh`. It supports trace log formatting alongside `XrdSysError` trace begin/end methods from the header.

Risks and test signals: when a caller supplies `buff`, the function still returns `xbuff` rather than the supplied buffer, which appears incorrect. Callers must also size custom buffers for the formatted output. Tests should cover explicit-buffer return value, 0/1/4/24/over-24 byte lengths, signed-char inputs, and concurrent use of the static buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.hh

Purpose: declares a lightweight tracing helper that wraps an `XrdSysError` destination and a bitmask of enabled trace classes.

Important APIs, types, and functions: `Beg()` and `End()` forward trace context calls to `XrdSysError`. `Tracing(mask)` checks `mask & What`. `What` is public for direct bitmask configuration. Static `bin2hex()` formats binary data for logs.

Control flow: components instantiate a trace object with an error route, update `What`, test `Tracing()` before expensive trace construction, and bracket trace records with `Beg()`/`End()`.

State and persistence: state is the error destination pointer and `What` mask. There is no ownership or persistence.

Dependencies and integration points: includes `XrdSysHeaders.hh` and `XrdSysError.hh`. It integrates with XRootD's logging/tracing infrastructure.

Risks and test signals: `Beg()`/`End()` assume `eDest` is non-null. Public mutable `What` is simple but unsynchronized. Tests should verify null handling expectations, mask checks, and trace forwarding with a fake `XrdSysError`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.cc

Purpose: implements URL percent-encoding and decoding for ASCII/binary byte strings, adapted from URI-Encode-C with XRootD naming and table changes.

Important APIs, types, and functions: static `hexval` maps ASCII hex digits to nibbles. `uri_encode_tbl` maps each byte to either a two-character hex code or zero bytes to indicate no encoding. `Decode()` decodes `%XX` sequences when both hex digits are valid. `Encode()` has allocating and caller-buffer variants. `Encoded()` computes the required output size including the null byte.

Control flow: `Decode()` scans input, copies normal bytes, and converts valid percent sequences while leaving invalid sequences mostly unchanged by copying the `%` then continuing. `Encode(char*)` scans each byte, emits `%HH` for entries present in the encode table, otherwise copies the byte. Allocating `Encode(char**)` computes size with `Encoded()`, mallocs, and delegates.

State and persistence: state is read-only static lookup tables. Allocating `Encode()` returns heap memory that callers must free. No locking or persistence is needed.

Dependencies and integration points: depends on C allocation/string headers and `XrdOucUri.hh`. It integrates with CGI/query construction and protocol code needing URL-safe strings.

Risks and test signals: `Encoded()` indexes `uri_encode_tbl[((unsigned int)src[i]) << 1]` without casting `src[i]` to unsigned char, so negative signed chars can index before the table. Allocating `Encode()` returns `0` both for allocation failure and potentially empty encoded length ambiguity through the length return. Tests should cover all unreserved/reserved byte classes, invalid percent sequences, high-bit bytes on signed-char platforms, allocation API ownership, and exact size from `Encoded()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.hh

Purpose: declares the static URI percent-encoding and decoding helper.

Important APIs, types, and functions: `Decode(const char*, int, char*)`, `Encode(const char*, int, char**)`, `Encode(const char*, int, char*)`, and `Encoded(const char*, int)` form the complete API. The class has no stateful behavior.

Control flow: callers either precompute size with `Encoded()` and encode into their own buffer, or use the allocating `Encode()` variant and free the returned buffer. Decoding writes into a caller buffer at least as large as the source plus null.

State and persistence: no object state exists. Allocating encode transfers heap ownership to the caller.

Dependencies and integration points: the header is standalone and documents the two-clause FreeBSD origin. It is used wherever XRootD needs percent-encoding without bringing in a larger URI library.

Risks and test signals: length parameters are explicit `int`, so callers must pass valid non-negative lengths. Tests should verify header/API use from C++ code, buffer sizing, and round-trips with the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.hh -->

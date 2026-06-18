<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_vc.c -->
# sources/user-network-fs/libtirpc/src/svc_vc.c

Purpose: `svc_vc.c` implements server-side RPC transports for connection-oriented endpoints. It provides a listening "rendezvous" transport that accepts sockets and a per-connection transport that decodes RPC record streams, unwraps service authentication, and writes replies.

Important APIs, types, and functions: Public entry points are `svc_vc_create`, `svc_fd_create`, `__xprt_set_raddr`, `__rpc_get_local_uid`, and compatibility `__svc_clean_idle`. Internal state lives in `cf_rendezvous` for listener buffer sizes/max record size and `cf_conn` for stream status, XID, XDR record handle, verifier storage, nonblocking mode, and last receive time. Core operations are `rendezvous_request`, `makefd_xprt`, `svc_vc_recv`, `svc_vc_getargs`, `svc_vc_reply`, `read_vc`, `write_vc`, and `__svc_destroy_idle`.

Control flow: `svc_vc_create` validates socket metadata, allocates an `SVCXPRT` plus extension state, records the local address, installs rendezvous ops, and registers the transport. A readable listener calls `rendezvous_request`, accepts a socket, wraps it with `makefd_xprt`, sets remote address fields, enables `TCP_NODELAY` for TCP, optionally switches to nonblocking max-record mode, and may reap idle nonblocking connections when fd usage is high. Per-connection receive uses `xdrrec_skiprecord`/`__xdrrec_getrec`, decodes `xdr_callmsg`, stores the XID, and later encodes `xdr_replymsg` plus authenticated wrapped results before flushing the XDR record.

State and persistence behavior: State is in heap-allocated `SVCXPRT`, `SVCXPRT_EXT`, `cf_rendezvous`, `cf_conn`, `xp_ltaddr`, `xp_rtaddr`, `xp_netid`, and the XDR record buffers. Transports are registered in the global service fd tables and removed by `xprt_unregister`/`__xprt_unregister_unlocked`. No durable data is persisted; only live sockets, in-memory RPC state, and local peer UID discovery are managed.

Dependencies and integration points: This file depends on sockets, `poll`, `fcntl`, pthread-compatible locks via `reentrant.h`, `rpc/rpc.h`, `rpc_com.h`, XDR record streams, service authentication macros from `svc_mt.h`, global service fd tables, and `getpeereid` for AF_LOCAL credential lookup. It integrates directly with `svc_run`/poll dispatch through `xprt_register`.

Risks: The `svc_fd_create` error path references `rep->xp_ltaddr.maxlen`, but no `rep` variable exists; that is a compile-time defect if this path is built as shown. Accepted sockets can leak if address allocation fails after `makefd_xprt`. Blocking reads treat poll timeout as fatal after 35 seconds, and nonblocking writes kill the connection after an arbitrary two-second EAGAIN window. `__svc_clean_idle` is an ABI-preserving stub, so callers expecting cleanup get no effect. Address compatibility copies into an IPv6-shaped `xp_raddr`, which must remain ABI-compatible with legacy callers.

Test signals: Build coverage should compile `svc_fd_create` and catch the `rep` typo. Runtime tests should cover listener creation, accepted TCP and AF_LOCAL connections, `SVCSET_CONNMAXREC`, nonblocking partial headers/records, idle cleanup under high fd pressure, authentication wrap/unwrap reply paths, and local UID extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_vc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr.c -->
# sources/user-network-fs/libtirpc/src/xdr.c

Purpose: `xdr.c` supplies generic External Data Representation filters for scalar integers, booleans, enums, opaque data, counted bytes, netobjs, discriminated unions, strings, and 64-bit integer families.

Important APIs, types, and functions: Public filters include `xdr_free`, `xdr_void`, `xdr_int`, `xdr_u_int`, `xdr_long`, `xdr_u_long`, fixed-width signed/unsigned 8/16/32/64-bit variants, `xdr_char`, `xdr_u_char`, `xdr_bool`, `xdr_enum`, `xdr_opaque`, `xdr_bytes`, `xdr_netobj`, `xdr_union`, `xdr_string`, `xdr_wrapstring`, `xdr_hyper`, and quad/longlong aliases. It uses `XDR_GETLONG`, `XDR_PUTLONG`, `XDR_GETBYTES`, and `XDR_PUTBYTES` from the active stream backend.

Control flow: Each filter switches on `xdrs->x_op`. Encode paths convert host values to XDR units through stream ops; decode paths read XDR units and assign host values; free paths are no-ops for scalars and release dynamic storage for counted bytes/strings. `xdr_opaque` pads to four-byte alignment. `xdr_bytes` and `xdr_string` first encode/decode lengths, enforce maximum sizes, allocate missing decode buffers, and clean up newly allocated storage on decode failure. `xdr_union` decodes the discriminant and dispatches the matching arm procedure or a default.

State and persistence behavior: The file itself has no long-lived state except the static zero-padding buffer and a static scratch buffer used by `xdr_opaque` to discard padding. Dynamic state is owned by caller-visible pointers passed into `xdr_bytes` and `xdr_string`, which may be allocated on decode and freed on `XDR_FREE`.

Dependencies and integration points: It depends on `rpc/xdr.h`, `rpc/types.h`, `rpc/rpc_com.h`, and stream-specific XDR backends such as memory, stdio, and record streams. Higher-level RPC message, auth, rpcbind, and generated protocol XDR routines build on these primitives.

Risks: Numeric conversions intentionally marshal C `long` through 32-bit XDR units, so platform width assumptions matter. Decode does not range-check downcasts from long to smaller integer types. `xdr_opaque` uses a static padding discard buffer, which is small and adequate for padding but not reentrant if misused outside the fixed padding path. `xdr_string` protects `size + 1` overflow, while `xdr_bytes` relies on caller-provided max sizes to bound allocation.

Test signals: Round-trip tests should cover all scalar widths, signed truncation edges, opaque padding lengths 0-3, max-size rejection, decode allocation/failure cleanup for strings and bytes, union default/missing-arm behavior, and `XDR_FREE` idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_array.c -->
# sources/user-network-fs/libtirpc/src/xdr_array.c

Purpose: `xdr_array.c` implements generic XDR helpers for variable-length counted arrays and fixed-length vectors.

Important APIs, types, and functions: `xdr_array` serializes/deserializes arrays addressed by `caddr_t *addrp`, a count pointer, max element count, element size, and element XDR procedure. `xdr_vector` serializes/deserializes a fixed number of statically allocated elements.

Control flow: `xdr_array` first XDRs the element count, rejects counts above `maxsize` or multiplication overflow when not freeing, allocates and zeroes decode storage if `*addrp` is null, then iterates element by element calling `elproc`. On `XDR_FREE`, it calls each element free handler through the same loop and then frees the array. `xdr_vector` simply walks fixed storage and calls the element procedure for each entry.

State and persistence behavior: No module-global state is used. Decode may allocate heap storage with `mem_alloc`; free releases it with `mem_free` and nulls the caller pointer. Fixed vectors never allocate or free their backing storage.

Dependencies and integration points: It depends on `rpc/types.h`, `rpc/xdr.h`, and the caller-supplied element XDR procedures. Generated RPC protocol code uses this for arrays such as gids and rpcbind statistics lists.

Risks: If an element procedure fails during decode after partial allocation, the array remains allocated with partially decoded elements; callers must invoke `XDR_FREE` for cleanup. `xdr_array` does not reject a null encode pointer with nonzero count, so invalid caller state can reach element procedures. Pointer arithmetic uses byte-sized `caddr_t` assumptions.

Test signals: Tests should exercise zero-length arrays, max-count rejection, `UINT_MAX / elsize` overflow rejection, decode allocation, partial element failure followed by free, and fixed-vector round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_float.c -->
# sources/user-network-fs/libtirpc/src/xdr_float.c

Purpose: `xdr_float.c` provides XDR filters for `float` and `double`, encoding IEEE floating point values in network byte order and preserving legacy VAX conversion code when built for VAX.

Important APIs, types, and functions: Public functions are `xdr_float` and `xdr_double`. The normal `IEEEFP` path uses `XDR_PUTINT32`/`XDR_GETINT32` over the in-memory representation. The VAX path defines bitfield layouts and limit tables for single and double conversion.

Control flow: `xdr_float` encodes or decodes one 32-bit word. `xdr_double` encodes or decodes two 32-bit words, swapping word order on little-endian hosts so the XDR stream remains big-endian IEEE representation. `XDR_FREE` is a no-op for both.

State and persistence behavior: The file maintains no mutable state. It reads and writes caller-owned floating point objects directly through integer pointers.

Dependencies and integration points: It depends on endian macros from `<endian.h>` or `<machine/endian.h>`, `rpc/types.h`, and `rpc/xdr.h`. Protocols with floating point fields delegate to these filters.

Risks: The implementation type-puns floats/doubles through `int32_t *`, which can trigger strict-aliasing or alignment concerns on some compilers/architectures. IEEE handling assumes host IEEE representation; non-IEEE platforms outside the VAX branch are not covered. NaN payload and signed-zero preservation depends on raw bit transport.

Test signals: Round-trip tests should cover normal values, infinities, NaNs, signed zero, big- and little-endian builds if available, and compiler sanitizer/strict-aliasing builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_float.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_mem.c -->
# sources/user-network-fs/libtirpc/src/xdr_mem.c

Purpose: `xdr_mem.c` implements an XDR stream backend over a caller-provided memory buffer.

Important APIs, types, and functions: `xdrmem_create` initializes the stream and selects aligned or unaligned ops. Operation implementations include get/put long, get/put bytes, get/set position, inline access for aligned buffers, and a no-op destroy function.

Control flow: Creation stores the operation mode, base pointer, current pointer, and remaining byte count. Get/put long checks at least four bytes remain, converts via `ntohl`/`htonl`, advances the pointer, and decrements `x_handy`. Byte get/put uses `memmove`. Positioning computes offsets from `x_base` and refuses seeks beyond the original end. Inline access returns a direct pointer only for aligned streams with enough remaining bytes.

State and persistence behavior: All state is embedded in the caller-provided `XDR` object and references the caller-owned buffer. Destroy does not free or flush anything.

Dependencies and integration points: It depends on `<netinet/in.h>` byte order helpers and the generic XDR ops table. It is used for in-memory pre-serialization, raw RPC, testing, auth marshaling, and generated protocol encode/decode against fixed buffers.

Risks: Position values are `u_int`; comments note this is insufficient for 64-bit pointer-sized buffers. Aligned paths cast buffer memory to `u_int32_t *`, so creation's alignment detection is important. `xdrmem_setpos` computes bounds from current pointer plus remaining bytes, preserving the original end but relying on valid existing stream state.

Test signals: Tests should cover aligned and unaligned buffers, exact-boundary reads/writes, failed overrun, seek forward/backward within bounds, failed seek beyond end, and inline availability only for aligned streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_rec.c -->
# sources/user-network-fs/libtirpc/src/xdr_rec.c

Purpose: `xdr_rec.c` implements the ONC RPC record-marking XDR backend used over byte streams such as TCP.

Important APIs, types, and functions: Public routines are `xdrrec_create`, `xdrrec_skiprecord`, `xdrrec_eof`, `xdrrec_endofrecord`, `__xdrrec_getrec`, and `__xdrrec_setnonblock`. Internal `RECSTREAM` tracks input/output buffers, current fragment header, last-fragment state, read/write callbacks, nonblocking header/record accumulation, and maximum record limits.

Control flow: Creation allocates send and receive buffers, installs `xdrrec_ops`, reserves space for an outgoing fragment header, and initializes input as empty. Encode operations append XDR units/bytes to the output buffer and flush fragments when full. `xdrrec_endofrecord` marks the fragment with `LAST_FRAG` and either flushes or starts another buffered record. Blocking decode reads fragment headers through `set_input_fragment`, consumes bytes from input buffers, and skips leftover fragments before a new record. Nonblocking decode uses `__xdrrec_getrec` to accumulate a full record, validate fragment lengths against `in_maxrec`, resize the buffer if needed, and expose the complete record to XDR decoders.

State and persistence behavior: Stream state is heap-allocated and owned by the `XDR` object until `xdrrec_destroy`. It persists buffered output between batched calls and buffered/partial input between reads. No durable persistence exists.

Dependencies and integration points: It depends on caller-provided read/write functions, RPC service/client transport status enums, `rpc/xdr.h`, and memory allocation macros. `svc_vc.c` uses it for server-side TCP streams, and client connection-oriented transports use the same record layer.

Risks: Blocking mode only rejects zero-length fragment headers; huge fragment sizes can still drive long reads unless transport-level limits exist. Nonblocking mode rejects zero, over-`maxrec`, and cumulative over-`maxrec` fragments, but `realloc_stream` failure is ignored by `__xdrrec_getrec`, leaving potential decode failure or memory pressure behavior. Pointer arithmetic casts through integer types in several places. `xdrrec_getpos` decode position semantics are unusual and should not be treated as an absolute stream offset.

Test signals: Tests should cover multi-fragment records, batched records, blocking EOF/skip behavior, nonblocking partial headers and payloads, max-record rejection, realloc growth, write callback short writes, and XPRT status transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_rec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_reference.c -->
# sources/user-network-fs/libtirpc/src/xdr_reference.c

Purpose: `xdr_reference.c` implements XDR helpers for pointed-to objects and nullable recursive pointers.

Important APIs, types, and functions: `xdr_reference` XDRs a required referenced object, allocating it on decode when needed. `xdr_pointer` XDRs a boolean presence discriminator followed by the referenced object only when present.

Control flow: `xdr_reference` allocates and zeroes storage on decode if `*pp` is null, calls the supplied object XDR procedure, and frees/nulls the pointer on `XDR_FREE`. `xdr_pointer` first serializes/deserializes a `bool_t` indicating whether data exists; false clears the pointer and succeeds, true delegates to `xdr_reference`.

State and persistence behavior: No module-global state exists. The only persistent effect is caller pointer allocation during decode and caller pointer nulling during free or absent decode.

Dependencies and integration points: It depends on `rpc/types.h`, `rpc/xdr.h`, and caller-supplied object filters. Generated rpcgen code uses these helpers for linked lists and optional structures.

Risks: `xdr_reference` can leak newly allocated memory if the object procedure fails during decode and callers do not later free. The helper cannot detect graph sharing or cycles by itself; `xdr_pointer` only handles tree-like recursive structures encoded with presence booleans. A null pointer on encode with `xdr_reference` will be passed to the object filter.

Test signals: Tests should cover absent/present pointers, decode allocation, free nulling, recursive list round trips, and failure cleanup conventions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_reference.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_sizeof.c -->
# sources/user-network-fs/libtirpc/src/xdr_sizeof.c

Purpose: `xdr_sizeof.c` estimates how many bytes an object will occupy when XDR-encoded, without writing to a real output stream.

Important APIs, types, and functions: Public `xdr_sizeof` installs a synthetic encode-only `xdr_ops` table. `x_putlong` adds four bytes, `x_putbytes` adds the byte count, `x_inline` tracks inline byte requests and allocates scratch storage when needed, `x_getpostn` returns the accumulated count, and `x_destroy` frees scratch state.

Control flow: `xdr_sizeof` initializes an `XDR` in `XDR_ENCODE`, points it at synthetic ops, invokes the caller's XDR function, frees any scratch inline allocation, and returns the accumulated size on success or zero on failure. Decode-oriented operations are mapped to a harmless false-return function.

State and persistence behavior: State lives in the stack `XDR` object plus optional heap scratch used to satisfy inline encode requests. No caller data is modified except whatever side effects the supplied XDR function has during encode.

Dependencies and integration points: It depends on `rpc/xdr.h` and is used by callers that need buffer sizing before encoding variable RPC payloads or auth-protected data.

Risks: This is an estimate driven by encode paths; XDR functions with side effects, operation-sensitive behavior, or unsupported set-position requirements may report zero or inaccurate sizes. `x_inline` uses `x_base` as a stored allocation length cast through a pointer, which is clever but non-obvious. The returned type is `unsigned long`, but failure returns indistinguishable zero from a genuinely zero-sized encoding.

Test signals: Tests should compare `xdr_sizeof` against actual `xdrmem_create` encodings for scalars, strings, arrays, inline-heavy generated code, and failure cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_sizeof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_stdio.c -->
# sources/user-network-fs/libtirpc/src/xdr_stdio.c

Purpose: `xdr_stdio.c` implements an XDR stream backend over a C `FILE *`.

Important APIs, types, and functions: `xdrstdio_create` initializes the stream. Internal ops implement get/put long, get/put bytes, get/set position via `ftell`/`fseek`, no inline support, and destroy via `fflush`.

Control flow: Creation stores the `FILE *` in `x_private`. Reads use `fread` to obtain network-order 32-bit words or byte blocks. Writes range-check `long` values on LP64, convert through `htonl`, and use `fwrite`. Destroy flushes but deliberately does not close the underlying file.

State and persistence behavior: State is primarily in the stdio stream's file offset and buffers. The XDR object does not own the `FILE *`, and no heap storage is allocated by this backend.

Dependencies and integration points: It depends on stdio, `<arpa/inet.h>`, and generic XDR APIs. It is suitable for file-backed XDR payloads and compatibility code that serializes RPC structures to streams.

Risks: `xdrstdio_getpos` truncates `ftell` to `u_int`; large files are not safely represented. Inline operations always return null, so callers must support non-inline fallback. Destroy only flushes, leaving lifecycle and error handling for close to the caller. LP64 `putlong` rejects values outside signed 32-bit/unsigned 32-bit bounds, which may differ from other backends' casts.

Test signals: Tests should cover read/write round trips, zero-length byte transfers, failed short reads/writes, seek positioning, large-offset truncation expectations, flush-on-destroy, and LP64 range rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/xdr_stdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/getpeereid.h -->
# sources/user-network-fs/libtirpc/tirpc/getpeereid.h

Purpose: `getpeereid.h` declares `getpeereid`, the portability hook used to retrieve effective peer credentials from local sockets.

Important APIs, types, and functions: The only API is `int getpeereid(int s, uid_t *euid, gid_t *egid);`.

Control flow: This header has no control flow. Callers pass a socket descriptor and receive effective UID/GID outputs from the platform implementation.

State and persistence behavior: No state is declared or owned.

Dependencies and integration points: It integrates with `svc_vc.c` through `__rpc_get_local_uid`, which calls `getpeereid` for `AF_LOCAL` transports. The header assumes `uid_t` and `gid_t` are already available from included system/RPC headers.

Risks: Because this is only a prototype, portability depends on a matching implementation or system function being available at link time. Missing type includes can surface if included standalone before system type definitions.

Test signals: Build tests should include this header in the supported platform configurations, and AF_LOCAL service tests should validate peer UID extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/getpeereid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/libc_private.h -->
# sources/user-network-fs/libtirpc/tirpc/libc_private.h

Purpose: `libc_private.h` is an empty compatibility placeholder.

Important APIs, types, and functions: It declares no APIs, types, macros, or data.

Control flow: There is no executable or preprocessor control flow.

State and persistence behavior: No state exists.

Dependencies and integration points: Some source files conditionally include `<libc_private.h>` on BSD-like platforms. This placeholder allows those includes to resolve in libtirpc builds that do not need private libc declarations.

Risks: Code that expects real libc-private declarations from this header will still fail or silently compile against missing prototypes. Its empty contents are intentional but should be documented as a portability shim.

Test signals: Build tests across Linux/BSD compatibility configurations should confirm no source requires additional declarations from this placeholder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/libc_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/netconfig.h -->
# sources/user-network-fs/libtirpc/tirpc/netconfig.h

Purpose: `netconfig.h` defines the transport-independent network configuration record and iteration APIs used by TI-RPC client/server creation.

Important APIs, types, and functions: It defines `NETCONFIG`, `NETPATH`, `struct netconfig`, `NCONF_HANDLE`, network semantics constants (`NC_TPI_CLTS`, `NC_TPI_COTS`, `NC_TPI_COTS_ORD`, `NC_TPI_RAW`), flags, protocol family/protocol strings, and APIs such as `setnetconfig`, `getnetconfig`, `getnetconfigent`, `freenetconfigent`, `endnetconfig`, `setnetpath`, `getnetpath`, `endnetpath`, `nc_perror`, and `nc_sperror`.

Control flow: The header exposes iterator-style control flow: callers obtain a handle, repeatedly fetch `struct netconfig *` entries, and end the iteration. Direct lookup returns one entry by netid. Error reporting is via print/string helpers.

State and persistence behavior: The implementation behind these prototypes owns iterator state and allocated `netconfig` entries. The header reserves unused fields for ABI growth.

Dependencies and integration points: `clnt.h`, `svc.h`, `nettype.h`, and rpcbind APIs use `struct netconfig` to select TCP, UDP, loopback, IPv4, IPv6, and visibility semantics.

Risks: String constants and numeric semantics are ABI/protocol selection inputs; changing them breaks configuration parsing. Memory ownership must be respected: entries from direct lookup require `freenetconfigent`, while iterator entries are tied to the handle.

Test signals: Tests should parse `/etc/netconfig` or fixture data, iterate `NETPATH`, lookup visible TCP/UDP entries, and verify error reporting and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/netconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/reentrant.h -->
# sources/user-network-fs/libtirpc/tirpc/reentrant.h

Purpose: `reentrant.h` maps historical BSD/Solaris RPC threading abstraction names onto pthread APIs for Linux and Apple builds.

Important APIs, types, and functions: It aliases `mutex_t`, `cond_t`, `rwlock_t`, `once_t`, and `thread_key_t`, defines initializer macros, and maps mutex, condition variable, rwlock, thread-local key, signal-mask, once, self, and exit operations to pthread calls.

Control flow: There is no runtime control flow in the header. Preprocessor control includes the mappings only when `__linux__` or `__APPLE__` is defined; other platforms are expected to use native headers or alternate definitions.

State and persistence behavior: The types represent synchronization and thread-local state owned by the calling modules. The header itself owns none.

Dependencies and integration points: `svc_vc.c` and other libtirpc internals use these aliases for global service locks and operation-table initialization. It depends on `<pthread.h>`.

Risks: The file explicitly says definitions are only guaranteed valid on Linux. Apple support is included by the condition but may differ in subtle pthread/rwlock availability behavior. Platforms outside the guard get no definitions.

Test signals: Build and thread-safety tests should cover global ops initialization, fd table locking, condition variable users, and platform preprocessor paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/reentrant.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/auth.h

Purpose: `auth.h` defines the client-side RPC authentication ABI, common credential/verifier structures, auth status codes, DES block type, authenticator vtable, and public constructors/utilities for AUTH_NONE, AUTH_SYS/UNIX, AUTH_DES, and RPCSEC_GSS integration.

Important APIs, types, and functions: Key types include `sec_data_t`, `dh_k4_clntdata_t`, `enum auth_stat`, `des_block`, `struct opaque_auth`, and `AUTH` with `auth_ops`. Macros dispatch operations such as `AUTH_MARSHALL`, `AUTH_VALIDATE`, `AUTH_REFRESH`, `AUTH_WRAP`, and `AUTH_UNWRAP`. Constructors and helpers include `authunix_create`, `authunix_create_default`, `authnone_create`, `authdes_create`, `authdes_pk_create`, `authdes_seccreate`, `xdr_opaque_auth`, netname helpers, keyserv helpers, and server auth entry points.

Control flow: Client transports call the AUTH vtable to marshal credentials, validate response verifiers, refresh credentials after auth errors, and wrap/unwrap RPC body XDR. Flavor implementations fill the vtable and private state. Server auth dispatch functions are declared for use by service-side authentication.

State and persistence behavior: `AUTH` instances own credentials, verifiers, DES key material, vtable pointer, and flavor-specific private data until destroyed through the vtable. `_null_auth` is an exported static opaque auth object.

Dependencies and integration points: This header depends on XDR, client status, sockets/types, and is included by `clnt.h`, `svc_auth.h`, RPC message code, and GSS/DES/UNIX flavor headers. It is central to request marshaling and service authentication.

Risks: Many macros dereference vtable pointers without null checks; partially initialized `AUTH` handles crash. DES and AUTH_SYS are weak/legacy mechanisms. The header mixes old K&R-compatible conventions and modern prototypes, so ABI compatibility constrains changes. `authany_wrap`/`authany_unwrap` prototypes are untyped `int(void)`, reflecting compatibility rather than type-safe XDR signatures.

Test signals: Tests should cover AUTH_NONE/UNIX construction, XDR opaque auth bounds at `MAX_AUTH_BYTES`, auth refresh/retry behavior, wrap/unwrap passthrough and GSS behavior, and ABI compatibility with legacy names `AUTH_NULL`, `AUTH_SYS`, and `AUTH_UNIX`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth_des.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/auth_des.h

Purpose: `auth_des.h` defines the wire structures for legacy DES/Diffie-Hellman RPC authentication.

Important APIs, types, and functions: It defines `enum authdes_namekind`, `struct authdes_fullname`, `struct authdes_cred`, `struct authdes_verf`, verifier field aliases such as `adv_timestamp` and `adv_nickname`, and prototypes `rtime` and `kgetnetname`.

Control flow: DES credentials are either full names with client netname, conversation key, and window, or server-assigned nicknames. Verifiers carry encrypted timestamps/window verification or server nickname/time verification depending on direction.

State and persistence behavior: The header declares only caller-owned credential/verifier structures. Runtime nickname caches, time sync, and key material are managed by implementation files.

Dependencies and integration points: It includes `rpc/auth.h` for `des_block`, `MAXNETNAMELEN`, and auth flavor constants. `authdes_create` declarations live in `auth.h`; generated key protocol headers also share DES block types.

Risks: DES authentication is cryptographically obsolete and depends on time synchronization and keyserv behavior. The use of `u_int32_t` in places where historical APIs used `u_long` is ABI-sensitive. Time windows and nicknames can be replay-sensitive if implementation checks are weak.

Test signals: Tests should cover XDR round trips for full-name and nickname credentials, timestamp/window verifier construction, time sync fallback, and interoperability with legacy AUTH_DES peers where still supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth_des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth_gss.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/auth_gss.h

Purpose: `auth_gss.h` declares the lower-level RPCSEC_GSS client authentication structures and helpers used by libtirpc's GSS implementation.

Important APIs, types, and functions: It defines `rpc_gss_proc_t`, `rpc_gss_svc_t`, `RPCSEC_GSS_VERSION`, `struct rpc_gss_sec`, `struct authgss_private_data`, `struct rpc_gss_cred`, `struct rpc_gss_init_res`, `MAXSEQ`, XDR helpers for credentials/init/data, constructors `authgss_create` and `authgss_create_default`, service selection and private-data accessors, logging helpers, and `is_authgss_client`.

Control flow: Clients create an AUTH handle with mechanism/qop/service/credential requirements, perform INIT/CONTINUE_INIT exchanges, then send DATA or DESTROY procedures. `xdr_rpc_gss_data` wraps payload encoding with GSS integrity/privacy behavior based on service.

State and persistence behavior: GSS contexts, context handles, sequence windows, and private auth data persist inside the AUTH implementation. `authgss_get_private_data` exposes a copy-like private-data structure that must be freed through `authgss_free_private_data`.

Dependencies and integration points: It depends on `rpc/clnt.h` and `<gssapi/gssapi.h>`. It integrates with `auth.h` as the RPCSEC_GSS flavor and with service-side GSS code through shared credential structures.

Risks: Sequence-window handling and GSS context lifecycle are security-critical. Incorrect qop/service negotiation can silently downgrade integrity or privacy. Logging helpers can expose sensitive byte dumps if enabled improperly. External OID globals (`krb5oid`, `spkm3oid`) must resolve from the GSS/Kerberos integration.

Test signals: Tests should cover context establishment, continuation tokens, service changes, integrity/privacy data wrapping, sequence number rollover near `MAXSEQ`, destroy messages, and private-data lifetime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth_gss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth_unix.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/auth_unix.h

Purpose: `auth_unix.h` defines the weak UNIX/AUTH_SYS credential structure and XDR routine.

Important APIs, types, and functions: It defines `MAX_MACHINE_NAME`, `NGRPS`, `struct authunix_parms`, alias `authsys_parms`, `xdr_authunix_parms`, and `struct short_hand_verf`.

Control flow: AUTH_SYS credentials carry timestamp, machine name, uid, gid, and supplementary gids. Servers may return an AUTH_SHORT verifier containing a replacement opaque credential for shorthand reuse.

State and persistence behavior: The header declares only wire/data structures. Implementations allocate and marshal machine name and gid arrays.

Dependencies and integration points: It is included by `rpc.h` and used by `authunix_create`, server-side `_svcauth_unix`, and RPC message credential handling.

Risks: The header itself warns the system is weak: credentials are unauthenticated and unencrypted. `NGRPS` and `MAX_MACHINE_NAME` are protocol bounds that must be enforced in XDR. UID/GID type widths must match XDR implementation expectations.

Test signals: Tests should cover max machine name, zero and `NGRPS` gids, over-limit rejection, shorthand verifier decode, and AUTH_SYS interop with NFS/RPC services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/auth_unix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/clnt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/clnt.h

Purpose: `clnt.h` defines the client-side RPC handle ABI, error structures, control operations, creation APIs, simplified RPC calls, and broadcast APIs.

Important APIs, types, and functions: Key types are `struct rpc_err`, `CLIENT`, `struct clnt_ops`, `struct rpc_timers`, `struct rpc_createerr`, and `resultproc_t`. Macros dispatch `CLNT_CALL`, `CLNT_ABORT`, `CLNT_GETERR`, `CLNT_FREERES`, `CLNT_CONTROL`, and `CLNT_DESTROY`. Constructors include generic nettype/netconfig creators, version-negotiating creators, `clnt_vc_create`, `clnt_dg_create`, raw/unix compatibility creators, error printers, `rpc_call`, `rpc_broadcast`, and `rpc_broadcast_exp`.

Control flow: Applications create a `CLIENT`, install/use an `AUTH`, call remote procedures through the vtable with XDR argument/result filters and timeout, inspect errors, free decoded results, control transport options, then destroy the handle. Generic creators resolve netconfig/rpcbind addresses and select connection-oriented or datagram transports.

State and persistence behavior: A `CLIENT` persists authenticator, transport-private state, netid, and transport provider strings. Global creation error state is exposed through `__rpc_createerr`.

Dependencies and integration points: It depends on `auth.h`, `clnt_stat.h`, `netconfig.h`, and Unix socket types. It is the central include for client transports, rpcbind clients, broadcast code, and GSS authentication.

Risks: Vtable macros lack null checks. Global `rpc_createerr` can be thread-sensitive depending on implementation. Control request numbers are ABI and transport-specific; unsupported controls must fail predictably. Broadcast callbacks are varargs-compatible and require careful type discipline.

Test signals: Tests should cover all creation paths, version negotiation, timeout/retry controls, fd close/no-close controls, auth refresh on `RPC_AUTHERROR`, error string generation, broadcast early-stop callbacks, and unrecoverable-status classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/clnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/clnt_soc.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/clnt_soc.h

Purpose: `clnt_soc.h` exposes legacy socket-specific client constructors for backward compatibility with pre-TI-RPC APIs.

Important APIs, types, and functions: It defines `UDPMSGSIZE` and declares `clnttcp_create`, `clntraw_create`, optional IPv6 `clnttcp6_create`, `clntudp_create`, `clntudp_bufcreate`, and optional IPv6 UDP constructors.

Control flow: Callers pass `sockaddr_in`/`sockaddr_in6`, program/version, optional socket pointer, timeout for UDP, and buffer sizes. Implementations create the appropriate modern connection-oriented, datagram, or raw `CLIENT`.

State and persistence behavior: The header owns no state. Socket ownership is negotiated through the socket pointer and ultimately through client destroy/close controls.

Dependencies and integration points: It is included at the end of `clnt.h` for backward compatibility and maps old TS-RPC user code onto libtirpc client implementations.

Risks: IPv6 declarations are hidden behind `INET6`, so build flags affect ABI visibility. Legacy `u_long` program/version types must map correctly to 32-bit RPC types. `UDPMSGSIZE` is an RPC-imposed packet bound that may not match transport MTU.

Test signals: Compatibility tests should compile old `clnttcp_create`/`clntudp_create` callers, verify socket reuse/creation behavior, and cover optional IPv6 declarations where enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/clnt_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/clnt_stat.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/clnt_stat.h

Purpose: `clnt_stat.h` defines the client RPC status enumeration used to classify local, remote, rpcbind, TLI, async, and connection errors.

Important APIs, types, and functions: The core type is `enum clnt_stat`, including statuses such as `RPC_SUCCESS`, encode/decode/send/receive failures, timeout/interruption, version mismatch, auth errors, program/procedure unavailable, rpcbind failures, unknown host/protocol/address, async in-progress, stale handles, and connection failures.

Control flow: Client implementations return these values from `CLNT_CALL` and related helpers. Error-formatting routines and retry policies switch on this enum.

State and persistence behavior: No state is declared.

Dependencies and integration points: It is included by `auth.h` and `clnt.h`; status values are stored in `struct rpc_err` and `struct rpc_createerr`.

Risks: Numeric values are ABI-significant and cannot be reordered. Some values are legacy aliases or transport-specific, so new code must preserve old semantics. Callers often use retry/no-retry decisions based on exact enum values.

Test signals: Tests should verify status-to-string output, retry classification through `IS_UNRECOVERABLE_RPC`, and preservation of numeric ABI values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/clnt_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/des.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/des.h

Purpose: `des.h` defines the low-level DES parameter structure and software DES entry point used by legacy secure RPC.

Important APIs, types, and functions: It defines `DES_MAXLEN`, `DES_QUICKLEN`, `enum desdir`, `enum desmode`, `struct desparams`, direct/buffer aliases `des_data` and `des_buf`, and `_des_crypt`.

Control flow: Callers fill key, direction, mode, IV, length, and either inline quick data or buffer pointer before invoking DES implementation or historical ioctl paths.

State and persistence behavior: State is caller-owned inside `struct desparams`; CBC mode updates IV behavior in implementation code.

Dependencies and integration points: It integrates with `des_crypt.h`, AUTH_DES, keyserv, and DES block definitions from `auth.h`. Disabled ioctl constants document historical hardware-driver integration.

Risks: DES is obsolete and weak. Buffer selection through a union requires callers to honor `DES_QUICKLEN`. Hardware ioctl support is disabled, so callers must rely on software. Length and alignment requirements need implementation enforcement.

Test signals: Tests should cover CBC/ECB software calls, quick vs buffer storage, bad length rejection, IV update behavior, and parity/key handling with `des_crypt.h`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/des_crypt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/des_crypt.h

Purpose: `des_crypt.h` declares public DES encryption helpers for CBC and ECB modes plus key parity adjustment.

Important APIs, types, and functions: It defines `DES_MAXDATA`, mode flags `DES_ENCRYPT`, `DES_DECRYPT`, `DES_HW`, `DES_SW`, error codes, `DES_FAILED`, and functions `cbc_crypt`, `ecb_crypt`, and `des_setparity`.

Control flow: Callers combine direction and hardware/software flags, pass key, data, length, and optionally IV for CBC. Return codes distinguish full success, software fallback from missing hardware, and hard failures.

State and persistence behavior: The data buffer is modified in place. CBC IV is updated by the implementation. No global state is declared in the header.

Dependencies and integration points: It includes `rpc/rpc.h` and supports AUTH_DES/keyserv code paths.

Risks: DES is cryptographically deprecated. Length must be a multiple of eight and no more than `DES_MAXDATA`; callers must not assume hardware availability. In-place mutation can surprise callers that reuse plaintext buffers.

Test signals: Tests should cover encrypt/decrypt round trips, CBC IV mutation, ECB determinism, software fallback return handling, parity adjustment, and bad length/key inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/des_crypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/key_prot.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/key_prot.h

Purpose: `key_prot.h` is rpcgen output for the keyserv/key protocol used by AUTH_DES/Diffie-Hellman secure RPC.

Important APIs, types, and functions: It defines key constants (`KEY_PROG`, versions 1/2, `KEYSIZE`, `HEXKEYBYTES`), `enum keystatus`, `keybuf`, `netnamestr`, request/result structs for encrypt/decrypt/getcred/netst operations, procedure numbers, client and service stubs for versions 1 and 2, free-result helpers, and XDR functions for every protocol type.

Control flow: Clients call generated stubs such as `key_set_1`, `key_encrypt_2`, or `key_get_conv_2` with a `CLIENT`; servers implement `_svc` counterparts for the same procedure numbers. XDR functions marshal strings, DES blocks, netobjs, Unix credentials, and discriminated result unions.

State and persistence behavior: Header structs hold secrets, public/private key strings, netnames, DES session keys, and Unix credential arrays, but runtime persistence belongs to keyserv implementations. Generated client stubs may return pointers to static result storage depending on rpcgen conventions.

Dependencies and integration points: It includes `rpc/rpc.h` and uses `des_block`, `netobj`, `CLIENT`, `SVCXPRT`, and `struct svc_req`. AUTH_DES utilities in `auth.h` call keyserv APIs.

Risks: The file is generated and should not be hand-edited; changes should come from the `.x` source. It transports sensitive key material and obsolete DES-era secrets. RPC stub static storage and generated free-result ownership are common concurrency/lifetime pitfalls.

Test signals: Tests should cover rpcgen regeneration consistency, XDR round trips for every type, version 1/2 procedure number compatibility, service/client stub linkage, and secret material cleanup in implementation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/key_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/nettype.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/nettype.h

Purpose: `nettype.h` defines internal nettype selector constants and helper prototypes for mapping high-level RPC nettype strings to `netconfig` entries.

Important APIs, types, and functions: It defines `_RPC_NONE`, `_RPC_NETPATH`, `_RPC_VISIBLE`, `_RPC_CIRCUIT_V`, `_RPC_DATAGRAM_V`, `_RPC_CIRCUIT_N`, `_RPC_DATAGRAM_N`, `_RPC_TCP`, and `_RPC_UDP`, plus `__rpc_setconf`, `__rpc_endconf`, `__rpc_getconf`, and `__rpc_getconfip`.

Control flow: Implementations use `__rpc_setconf` to start an internal netconfig iteration for a nettype, `__rpc_getconf`/`__rpc_getconfip` to fetch matching entries, and `__rpc_endconf` to release iteration state.

State and persistence behavior: Iterator state is opaque and implementation-owned. The header owns no state.

Dependencies and integration points: It depends on `netconfig.h` and is used by generic client/server creation, broadcast, and rpcbind address discovery.

Risks: Constants are private but widely used inside libtirpc; mismatches with parser logic can select wrong transports. Opaque handles require strict cleanup to avoid leaks.

Test signals: Tests should cover each named nettype string, TCP/UDP shortcuts, visible-only selection, `NETPATH` ordering, IPv4/IPv6 filtering, and cleanup after partial iteration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/nettype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/pmap_clnt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/pmap_clnt.h

Purpose: `pmap_clnt.h` declares legacy portmapper v2 client routines for registering and discovering RPC services on port 111.

Important APIs, types, and functions: It declares `pmap_set`, `pmap_unset`, `pmap_getmaps`, `pmap_rmtcall`, `clnt_broadcast`, and `pmap_getport`.

Control flow: Callers register/unregister program/version/protocol/port tuples, query a port for a remote sockaddr, dump mappings, perform UDP-only remote calls through portmapper, or broadcast calls and process responses through a callback.

State and persistence behavior: Portmapper state is external in the local or remote portmapper service. Returned mapping lists are allocated by implementation/XDR code and require appropriate freeing.

Dependencies and integration points: It depends on RPC types, XDR, and `clnt.h`, and complements `pmap_prot.h` and `pmap_rmt.h`. `rpc.h` includes it for legacy API exposure.

Risks: Portmapper v2 is IPv4/port-centric and cannot represent modern transport-independent universal addresses. Broadcast and remote-call behavior uses null authentication and may be quiet on missing registrations.

Test signals: Tests should cover set/unset/getport against rpcbind/portmap compatibility, dump list decoding, UDP remote call, broadcast callback stop behavior, and IPv4-only expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/pmap_clnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/pmap_prot.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/pmap_prot.h

Purpose: `pmap_prot.h` defines the legacy portmapper v2 protocol constants, mapping structs, list structs, and XDR routines.

Important APIs, types, and functions: It defines `PMAPPORT`, `PMAPPROG`, `PMAPVERS`, procedure numbers `PMAPPROC_*`, `V2FIRST`, `struct pmap`, `struct pmaplist`, `xdr_pmap`, `xdr_pmaplist`, and `xdr_pmaplist_ptr`.

Control flow: Portmapper procedures register, unregister, resolve, dump, or indirectly call registered services using `struct pmap` tuples of program, version, protocol, and port.

State and persistence behavior: The header only defines wire structures. Mapping persistence lives in the portmapper/rpcbind service.

Dependencies and integration points: It is included by portmapper clients, servers, and `rpc.h`. `pmap_rmt.h` covers the CALLIT argument/result wrappers.

Risks: The protocol is bound to TCP/UDP port numbers and does not handle transport-independent addresses. The comment notes `PMAPPROC_CALLIT` is quiet on missing registrations, which complicates diagnostics. Linked list XDR must avoid leaks on partial decode failure.

Test signals: Tests should verify XDR of individual maps and map lists, procedure constants, dump/free behavior, and rpcbind compatibility mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/pmap_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/pmap_rmt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/pmap_rmt.h

Purpose: `pmap_rmt.h` defines client-side argument/result wrappers and XDR routines for portmapper remote-call service.

Important APIs, types, and functions: It defines `struct rmtcallargs`, `struct rmtcallres`, `xdr_rmtcall_args`, and `xdr_rmtcallres`.

Control flow: The caller supplies target program/version/procedure, argument XDR routine and pointer, result XDR routine and pointer, and receives the service port plus decoded results from a portmapper-mediated UDP call.

State and persistence behavior: The structures carry caller-owned pointers and XDR function pointers. No persistent state is declared.

Dependencies and integration points: It complements `pmap_clnt.h` and `pmap_prot.h`, and is used by `pmap_rmtcall`/broadcast implementations.

Risks: XDR of embedded opaque args/results depends on correct function pointers and length accounting. Remote call service uses null auth and quiet failure behavior. Pointer-bearing structs are not raw wire structs; they are helper representations for XDR routines.

Test signals: Tests should cover encoded argument length calculation, result length decode, bad XDR procedure failure, port output assignment, and missing-registration behavior through portmapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/pmap_rmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/raw.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/raw.h

Purpose: `raw.h` declares the shared in-memory communication buffer used by raw RPC client/server transports for testing and local performance paths.

Important APIs, types, and functions: The only exported symbol is `char *__rpc_rawcombuf`.

Control flow: Raw client and service implementations use the common buffer instead of sockets to pass encoded RPC messages in process.

State and persistence behavior: `__rpc_rawcombuf` is global mutable process state. Its allocation and lifetime are implementation-defined outside this header.

Dependencies and integration points: It is used by `clnt_raw_create`/`clntraw_create` and `svc_raw_create`/`svcraw_create`.

Risks: A single global buffer is inherently not thread-safe or reentrant across simultaneous raw RPC calls. It is suitable for tests and benchmarks, not isolated multi-client state.

Test signals: Tests should cover raw client/server round trips, buffer allocation, repeated calls, and expected non-thread-safe behavior or locking if implementations add it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpc.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpc.h

Purpose: `rpc.h` is the umbrella public include for TI-RPC, aggregating base types, XDR, auth, client, server, RPC message, portmapper, rpcbind, multithreaded service, and rpc database APIs.

Important APIs, types, and functions: Besides includes, it defines fallback `UDPMSGSIZE` and declares legacy helpers `get_myaddress`, `bindresvport`, `registerrpc`, `callrpc`, `getrpcport`, address converters `taddr2uaddr`/`uaddr2taddr`, `bindresvport_sa`, and internal library/rpcbind helpers like `__rpc_nconf2fd`, `__rpc_nconf2sockinfo`, `__rpc_fd2sockinfo`, and `__rpc_get_t_size`.

Control flow: Consumers include this header to access most RPC APIs. High-level helpers perform one-shot registration/calls, reserved-port binding, and transport address conversion. Internal helpers map netconfig/socket descriptors to fd and socket metadata for client/server creation.

State and persistence behavior: The header declares no storage. Included subheaders expose stateful client, server, auth, and rpcbind APIs.

Dependencies and integration points: It pulls in nearly every public libtirpc component and must maintain include ordering for types such as `netbuf`, `CLIENT`, `SVCXPRT`, and XDR.

Risks: Umbrella includes can create circular dependency sensitivity; this file includes both public and internal helpers, with comments warning internal functions may change. Including AUTH_DES by default exposes obsolete DES interfaces. Legacy helper prototypes use old integer types.

Test signals: Tests should compile representative legacy and modern consumers with only `<rpc/rpc.h>`, verify no include-order breakage, and exercise one-shot `callrpc`/`registerrpc` plus address conversion helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpc_com.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpc_com.h

Purpose: `rpc_com.h` declares internal common helpers shared by client, server, rpcbind, and transport-selection code.

Important APIs, types, and functions: It defines `RPC_MAXDATASIZE`, `RPC_MAXADDRSIZE`, `__RPC_GETXID`, and prototypes for address size, fd table size, netconfig lookup, default domain, universal address conversion by address family, address fixup, sockinfo/netid conversion, semantics/socket-type conversion, null procedure calls, socket-bound checks, rpcbind address discovery, global `rpc_control`, and token parsing.

Control flow: Internal code uses these helpers to generate XIDs, convert between netconfig and sockets, locate rpcbind addresses, and implement global RPC controls.

State and persistence behavior: The header declares no state, but helpers operate on process fd limits, environment/configuration, netconfig data, and rpcbind/client handles.

Dependencies and integration points: It depends on RPC base types, `CLIENT`, `netconfig`, `netbuf`, and `__rpc_sockinfo` definitions from other headers. `svc_vc.c` uses several declarations from this header.

Risks: This is marked internal and not stable for applications. `__RPC_GETXID` mixes pid and timeval fields; uniqueness depends on call timing. Transport conversion helpers must preserve IPv4/IPv6 and netid semantics exactly.

Test signals: Tests should cover socket-info round trips, netid mappings, universal address conversions, bound-socket detection, XID uniqueness under rapid calls, and rpcbind find-address behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpc_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpc_msg.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpc_msg.h

Purpose: `rpc_msg.h` defines the ONC RPC message wire model for calls and replies plus XDR routines and error mapping.

Important APIs, types, and functions: It defines `RPC_MSG_VERSION`, `RPC_SERVICE_PORT`, enums `msg_type`, `reply_stat`, `accept_stat`, and `reject_stat`, structures `accepted_reply`, `rejected_reply`, `reply_body`, `call_body`, and `rpc_msg`, field aliases, and XDR functions `xdr_callmsg`, `xdr_callhdr`, `xdr_replymsg`, `xdr_accepted_reply`, `xdr_rejected_reply`, plus `_seterr_reply`.

Control flow: Clients encode `CALL` messages with program/version/procedure and auth credentials. Servers decode calls and encode `REPLY` messages as accepted or denied. Accepted replies may carry results, version mismatch ranges, or null bodies; denied replies carry RPC version mismatch or auth error data.

State and persistence behavior: No module state is declared. Message structs contain pointers to auth bodies and result XDR callbacks, so ownership remains with callers and auth/protocol layers.

Dependencies and integration points: It depends on `auth.h` and is used by every client/server transport, `svc_vc.c`, auth code, and error translation in `clnt.h`.

Risks: Union aliases make it easy to access the wrong arm if direction/status is not set first. `ar_results` embeds a function pointer and location for local XDR use, not a direct wire field. Version and status numeric values are protocol ABI.

Test signals: Tests should cover call header pre-serialization, accepted success results, all accepted/rejected error statuses, auth error mapping through `_seterr_reply`, and malformed message decode rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpc_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_clnt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_clnt.h

Purpose: `rpcb_clnt.h` declares transport-independent rpcbind client routines for registering, unregistering, resolving, dumping, remote-calling, time querying, and address conversion.

Important APIs, types, and functions: APIs include `rpcb_set`, `rpcb_unset`, `rpcb_getmaps`, `rpcb_rmtcall`, `rpcb_getaddr`, `rpcb_gettime`, `rpcb_taddr2uaddr`, and `rpcb_uaddr2taddr`.

Control flow: Callers pass program/version and `netconfig` data to register or resolve universal addresses in rpcbind. Remote calls encode supplied args/results through XDR callbacks and may return an address. Address conversion bridges `struct netbuf` and universal address strings.

State and persistence behavior: Persistent mappings live in rpcbind, not the client library. Returned maps/addresses/netbufs are allocated by implementation and must be freed according to API conventions.

Dependencies and integration points: It depends on `rpcb_prot.h`, `rpc/types.h`, and netconfig/netbuf definitions. Generic `clnt_create` and `svc_register` code uses rpcbind client helpers.

Risks: `rpcb_rmtcall` takes `const caddr_t` for result storage, reflecting historical prototypes and requiring careful casts. Network failures and quiet remote-call semantics can obscure missing services. Memory ownership of returned universal addresses and map lists must be clear to callers.

Test signals: Tests should cover set/unset/getaddr against local rpcbind, map dump/free, time query, taddr/uaddr round trips, remote call success/failure, and IPv4/IPv6 netconfig variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_clnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_prot.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_prot.h

Purpose: `rpcb_prot.h` is rpcgen output for rpcbind protocol versions 3 and 4, including mapping records, remote-call wrappers, address-list records, statistics records, procedure stubs, and XDR prototypes.

Important APIs, types, and functions: It defines `struct rpcb`, list types `rpcblist`/`rpcblist_ptr`, `rpcb_rmtcallargs`, client-side `r_rpcb_rmtcallargs`, `rpcb_rmtcallres`, client-side `r_rpcb_rmtcallres`, `rpcb_entry`, stats list/types, `xdr_netbuf`, rpcbind socket paths, `RPCBPROG`, `RPCBVERS`, `RPCBVERS4`, procedure numbers, generated client/service stubs for v3/v4, and many `xdr_*` functions.

Control flow: Rpcbind v3 supports set/unset/getaddr/dump/callit/gettime/address conversion. Version 4 carries those plus broadcast alias, version-specific address lookup, non-quiet indirect calls, address-list lookup, and statistics retrieval. Generated stubs call these procedures through `CLIENT`, while `_svc` declarations define server dispatch hooks.

State and persistence behavior: The header defines wire and helper structures only. Runtime mapping tables and statistics persist in rpcbind. Linked-list results and string/netbuf fields are dynamically allocated during XDR decode and must be freed.

Dependencies and integration points: It includes `rpc/rpc.h` and therefore participates in a dense include graph. It is consumed by rpcbind client code, server code, generic service registration, and address conversion helpers.

Risks: It is generated and should be changed through the source `.x` file. The header contains separate kernel and non-kernel struct shapes, so conditional build paths must remain compatible. The abstract Unix socket string begins with `\0`, which requires length-aware handling. Linked list XDR is allocation-heavy and failure-prone if cleanup is missed.

Test signals: Tests should cover rpcgen regeneration, XDR round trips for maps/lists/entries/stats/netbuf, v3 and v4 stub linkage, abstract/local rpcbind socket connection, address list decode/free, and stats procedure compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcent.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpcent.h

Purpose: `rpcent.h` exposes RPC program-name database lookup compatibility APIs when the system C library does not provide them.

Important APIs, types, and functions: When enabled by platform macros, it defines `struct rpcent` and declares `getrpcbyname`, `getrpcbynumber`, `getrpcent`, `setrpcent`, and `endrpcent`.

Control flow: Callers iterate or look up `/etc/rpc`-style entries by name or number using static-storage legacy APIs.

State and persistence behavior: The declared lookup functions return pointers to static areas and are documented as MT-unsafe. Iteration state is implementation-owned.

Dependencies and integration points: It is included by `rpc.h` and provides fallback compatibility for libc configurations without RPC netdb support.

Risks: Conditional declarations vary by libc and feature macros, which can create portability surprises. Static returned storage is not thread-safe and is overwritten by subsequent calls.

Test signals: Build tests should cover glibc, uClibc-without-RPC, and non-glibc configurations. Runtime tests should verify lookup by name/number, iteration reset, and documented static-storage behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcsec_gss.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/rpcsec_gss.h

Purpose: `rpcsec_gss.h` declares the higher-level RPCSEC_GSS public API for creating secure RPC auth handles, configuring services, registering server names/callbacks, retrieving credentials, and discovering mechanisms.

Important APIs, types, and functions: It defines `rpc_gss_service_t`, `rpc_gss_principal_t`, option request/return structs, raw and Unix credential structs, lock and callback structs, error structs, OID aliases, error constants, and functions such as `rpc_gss_seccreate`, `rpc_gss_set_defaults`, max-data-length helpers, `rpc_gss_set_svc_name`, `rpc_gss_getcred`, `rpc_gss_set_callback`, principal/mechanism/qop discovery, version discovery, and error retrieval.

Control flow: Clients create an AUTH handle for a service principal/mechanism/qop/service, optionally inspect returned context options, and use it through normal `CLIENT` calls. Servers register accepted service names and callbacks, then dispatch code can retrieve raw and Unix-mapped credentials from `svc_req`.

State and persistence behavior: GSS contexts, service registrations, callbacks, errors, and credential mappings are implementation-owned. Credential pointers returned by `rpc_gss_getcred` are tied to request/auth context lifetime.

Dependencies and integration points: It depends on GSSAPI, `auth.h`, and `clnt.h`. It complements the lower-level `auth_gss.h` and service auth implementation.

Risks: This API is security-sensitive: default service/qop choices, callback authorization, and credential mapping must be correct. `rpc_gss_principal_t` uses a flexible one-byte tail idiom. Mechanism/qop strings and OIDs require precise ownership and lifetime handling.

Test signals: Tests should cover client context creation, server name registration, callback authorization accept/reject, credential retrieval, max-data calculations for integrity/privacy, mechanism discovery, qop mapping, and error reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/rpcsec_gss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/svc.h

Purpose: `svc.h` defines the server-side RPC transport/request ABI, service registration APIs, dispatch helpers, event-loop entry points, and transport constructors.

Important APIs, types, and functions: Key items include service control constants, `enum xprt_stat`, `SVCXPRT`, `struct svc_req`, `svc_getrpccaller`, SVC operation macros, `svc_reg`, `svc_unreg`, `xprt_register`, `xprt_unregister`, reply/error helpers, `rpc_reg`, global fd/poll sets, `svc_getreq*`, `svc_run`, `svc_exit`, transport constructors `svc_create`, `svc_tp_create`, `svc_tli_create`, `svc_vc_create`, `svc_dg_create`, `svc_fd_create`, raw/unix compatibility constructors, cache enablement, and `__rpc_get_local_uid`.

Control flow: Servers create transports, register dispatch functions for program/version pairs, enter `svc_run` or call `svc_getreq*` from their own event loop, decode arguments via `SVC_GETARGS`, execute handlers, send replies/errors, free arguments, and eventually unregister/destroy transports.

State and persistence behavior: `SVCXPRT` persists fd/address/auth/private transport state. Global `svc_fdset`, `svc_pollfd`, and max fd/poll indices track registered transports. Service registration tables are implementation-owned. No durable service state is stored by the header itself.

Dependencies and integration points: It depends on XDR, auth, netconfig, rpc message types, and compatibility `svc_soc.h`. `svc_vc.c` implements the connection-oriented constructor declared here.

Risks: `SVCXPRT` layout is ABI-sensitive, including compatibility `xp_raddr` and private slots. Operation macros dereference vtables directly. Global fd sets need locking in multithreaded implementations. Batched TCP calls must avoid replies to prevent deadlocks.

Test signals: Tests should cover service registration/unregistration, dispatch of success and all standard errors, custom event-loop polling, transport create/destroy, version quiet controls, fd table updates, and batched-call no-reply behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth.h

Purpose: `svc_auth.h` defines the server-side authentication vtable and authentication dispatch registration APIs.

Important APIs, types, and functions: It defines `SVCAUTH`, `struct svc_auth_ops`, macros `SVCAUTH_WRAP`, `SVCAUTH_UNWRAP`, `SVCAUTH_DESTROY`, and functions `_gss_authenticate`, `_authenticate`, and `svc_auth_reg`.

Control flow: Server transports use `_authenticate` to validate a decoded RPC message and populate request credentials. Authenticated service replies use `SVCAUTH_WRAP`/`UNWRAP` through the per-transport auth object. New auth flavors can be registered by flavor number through `svc_auth_reg`.

State and persistence behavior: `SVCAUTH` instances carry a vtable and private data, usually embedded in `SVCXPRT_EXT`. Flavor registries and private auth contexts are implementation-owned.

Dependencies and integration points: It depends on `struct svc_req`, `struct rpc_msg`, `XDR`, and auth status definitions from other RPC headers. `svc_vc.c` calls `SVCAUTH_UNWRAP` and `SVCAUTH_WRAP`.

Risks: Vtable macros have no null checks. Auth flavor registration must be synchronized in multithreaded code. GSS authentication returns an extra no-dispatch flag, so callers must handle handshake/control messages correctly.

Test signals: Tests should cover AUTH_NONE/UNIX/GSS authentication, custom flavor registration, wrap/unwrap error propagation, destroy cleanup, and rejected auth status replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth_gss.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth_gss.h

Purpose: `svc_auth_gss.h` exposes legacy University of Michigan service-side GSS helper APIs.

Important APIs, types, and functions: It declares `svcauth_gss_set_svc_name` and `svcauth_gss_get_principal`.

Control flow: Servers set the accepted GSS service name, then later retrieve a principal string from an `SVCAUTH` object associated with an authenticated request.

State and persistence behavior: Service-name registration and principal storage are implementation-owned. Returned principal string lifetime depends on the service auth implementation.

Dependencies and integration points: It includes `svc_auth.h` and GSSAPI. It is a legacy companion to the newer `rpcsec_gss.h` server APIs.

Risks: Legacy API behavior may differ from `rpc_gss_set_svc_name` and may have weaker ownership/lifetime documentation. GSS name handling is security-sensitive.

Test signals: Tests should cover service-name registration, principal retrieval after a GSS-authenticated call, failed/unauthenticated retrieval, and coexistence with `rpcsec_gss.h` APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth_gss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_dg.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/svc_dg.h

Purpose: `svc_dg.h` exposes internal datagram service transport state needed by rpcbind code.

Important APIs, types, and functions: It defines `struct svc_dg_data` with IO size, XID, XDR handle, verifier storage, duplicate request cache, received `msghdr`, control-message buffer, and macro `__rpcb_get_dg_xidp`.

Control flow: Datagram transport code stores per-request decode/reply state in `xp_p2`; rpcbind can access the current XID pointer through the macro.

State and persistence behavior: Instances are kept in `SVCXPRT->xp_p2` and persist for the datagram transport lifetime. The cache pointer may hold duplicate-request cache state.

Dependencies and integration points: It depends on `XDR`, `MAX_AUTH_BYTES`, `struct msghdr`, and the service transport private-slot convention. Comments restrict intended includes to `svc_dg.c` and rpcbind shared service code.

Risks: This is an internal layout exposed for rpcbind coupling; changing field order can break code such as `ti_opts.c` that expects `su_iosz` first. Fixed `su_cmsg[64]` may be insufficient for some ancillary data extensions.

Test signals: Tests should cover datagram request decode/reply, XID access by rpcbind, duplicate cache behavior, ancillary control-message handling, and ABI-sensitive field layout if external code depends on it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_dg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_mt.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/svc_mt.h

Purpose: `svc_mt.h` defines multithread/service transport extension data stored in `SVCXPRT->xp_p3`.

Important APIs, types, and functions: It defines `SVCXPRT_EXT` with `flags` and embedded `SVCAUTH xp_auth`, macros `SVCEXT`, `SVC_XP_AUTH`, `svc_flags`, `version_keepquiet`, and flag `SVC_VERSQUIET`.

Control flow: Transport implementations allocate `SVCXPRT_EXT`, attach it to `xp_p3`, then service/auth code reads or writes flags and auth state through macros. Version mismatch response behavior checks `version_keepquiet`.

State and persistence behavior: Extension state persists for the transport lifetime and is freed with the transport. Auth private state may need flavor-specific destroy handling before freeing.

Dependencies and integration points: It depends on `SVCAUTH` from `svc_auth.h` and `SVCXPRT` from `svc.h`. `svc_vc.c` allocates and uses this extension for auth wrap/unwrap.

Risks: Macros assume `xp_p3` is non-null and correctly typed. Missing extension allocation will crash service paths. Flags are raw ints with no locking in the macro layer.

Test signals: Tests should cover extension allocation in every transport constructor, version quiet controls, auth wrap/unwrap storage, and destroy cleanup for auth private data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_mt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_soc.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/svc_soc.h

Purpose: `svc_soc.h` exposes legacy socket-specific server APIs for backward compatibility with pre-TI-RPC code.

Important APIs, types, and functions: It defines `svc_getcaller`, `svc_getcaller_netbuf`, and declares `svc_register`, `svc_unregister`, `svcraw_create`, UDP constructors/cache APIs, optional IPv6 UDP constructors, TCP constructors, and `svcfd_create`.

Control flow: Legacy callers create UDP/TCP/fd/raw transports, register program/version dispatchers with an IP protocol number, and access caller addresses through old sockaddr-compatible macros.

State and persistence behavior: The header owns no state. Implementations create `SVCXPRT` objects and use the same global service registration and fd tables as modern APIs.

Dependencies and integration points: It is included from `svc.h` and maps old socket APIs onto modern `svc_vc_create`, `svc_dg_create`, `svc_fd_create`, and raw transports.

Risks: `svc_getcaller` exposes legacy `xp_raddr`, while newer code should use `xp_rtaddr`; keeping both coherent is required. IPv6 declarations depend on build configuration. Old `u_long` program/version types must remain compatible with `rpcprog_t`/`rpcvers_t`.

Test signals: Compatibility tests should build and run old `svctcp_create`, `svcudp_create`, `svc_register`, and `svc_getcaller` users, including IPv6 variants when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/svc_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/types.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/types.h

Purpose: `types.h` defines core RPC scalar types, boolean constants, allocation macros, compatibility typedefs, transport address buffers, bind-address structs, and internal socket metadata.

Important APIs, types, and functions: It defines `bool_t`, `enum_t`, `rpcprog_t`, `rpcvers_t`, `rpcproc_t`, `rpcprot_t`, `rpcport_t`, `rpc_inline_t`, `TRUE`, `FALSE`, `mem_alloc`, `mem_free`, compatibility typedefs for `u_char`, `u_short`, `u_int`, `u_long`, `quad_t`, `u_quad_t`, `daddr_t`, `caddr_t`, `struct netbuf`, `struct t_bind`, and `struct __rpc_sockinfo`.

Control flow: There is no runtime control flow. Preprocessor branches adapt typedefs for Apple, FreeBSD, non-glibc, Bionic, and libc feature macros.

State and persistence behavior: No state is declared. `mem_alloc` and `mem_free` map directly to `calloc` and `free`, which affects allocation initialization across XDR and transport code.

Dependencies and integration points: It includes system types/time/param, stdlib, and `netconfig.h`. Nearly every libtirpc header and source depends on these base definitions.

Risks: Typedef guards must avoid conflicting with libc definitions. `mem_free(ptr, bsize)` ignores size through the macro, but callers often pass sizes for historical allocators. `struct netbuf` ownership rules are convention-based and not encoded in the type.

Test signals: Build tests should cover supported libc/platform macro combinations, verify RPC scalar widths, ensure `mem_alloc` zero-initializes, and check `netbuf`/`__rpc_sockinfo` ABI layout expected by implementation code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/types.h -->

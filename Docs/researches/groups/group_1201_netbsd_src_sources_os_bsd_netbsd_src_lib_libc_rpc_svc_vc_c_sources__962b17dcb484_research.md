# Group Research: group_1201_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_rpc_svc_vc_c_sources__962b17dcb484

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_vc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_vc.c

This file implements libc RPC server-side connection-oriented transports. It supports two SVCXPRT modes: a rendezvous/listener transport created by `svc_vc_create`, and an established stream transport created by `svc_fd_create` or accepted from the rendezvous path.

Main exported entry points are `svc_vc_create`, `svc_fd_create`, and `__svc_clean_idle`. The listener path stores `struct cf_rendezvous` in `xp_p1`, records send/receive sizing and max-record policy, enables `LOCAL_CREDS` for AF_LOCAL sockets, snapshots the local address, installs rendezvous ops, and registers the transport. The established connection path uses `makefd_xprt`, which allocates `struct cf_conn`, creates an `xdrrec` stream over `read_vc`/`write_vc`, sets verifier storage, installs normal RPC ops, discovers `xp_netid`, and registers the transport.

`rendezvous_request` accepts incoming sockets, creates a new transport, copies the peer address, applies TCP_NODELAY when socket metadata is available, inherits rendezvous buffer/max-record settings, and optionally switches the accepted socket to nonblocking mode with `__xdrrec_setnonblock`. It returns `FALSE` because the listener itself never yields an RPC request.

The data path is built around `xdr_rec.c`: `svc_vc_recv` sets decode mode, skips to a record boundary, decodes an RPC call, and saves the transaction id; `svc_vc_reply` sets encode mode, restores the saved xid, serializes the reply, and ends/flushed the record. `svc_vc_getargs` and `svc_vc_freeargs` delegate argument decode/free to the service XDR procedure.

Connection I/O is fatal-on-error. `read_vc` has a blocking mode with a 35-second `pollts` timeout and a nonblocking mode that treats `EAGAIN` as no bytes. For AF_LOCAL sockets it consumes SCM_CREDS on first read and stores copied credentials in `xp_p2`. `write_vc` writes until all bytes are sent, marking the stream dead on hard write errors; nonblocking writes tolerate `EAGAIN` only for about two seconds.

Resource cleanup is centralized in `svc_vc_destroy` and `__svc_vc_dodestroy`, unregistering transports, closing fds, destroying XDR streams, freeing address buffers, transport strings, netids, and transport-private structs. `__svc_clean_idle` scans registered transports under `svc_fd_lock`, selects eligible VC connections, and destroys either those idle past a timeout or the least-active one when `timeout == 0`.

Research notes and risks:
- `svc_fd_create` has a cleanup branch using `rep->xp_ltaddr.maxlen` while the local variable is `ret`; as read, that appears to be a compile-time typo or stale code path.
- `makefd_xprt` cleanup frees only the `SVCXPRT` object on some failure paths after `struct cf_conn` allocation, so failure paths need careful review for leaks.
- Accepted transport error cleanup closes the socket directly rather than destroying a partially built `newxprt`; allocation/setup failures after `makefd_xprt` may leave registered transport state.
- The accepted remote address path sets `xp_rtaddr.len` but not `xp_rtaddr.maxlen`, while destruction frees with `maxlen`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_vc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_float.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_float.c

This file implements XDR serialization for `float` and `double`, exported as `xdr_float` and `xdr_double` with weak aliases for libc namespace handling.

For non-VAX targets it assumes IEEE floating point and serializes raw IEEE bits through `XDR_PUTINT32`/`XDR_GETINT32`. `xdr_float` is one 32-bit word. `xdr_double` is two 32-bit words, with word order selected by byte order and an old ARM FPA condition: big-endian or non-VFP ARM sends the first word first, while little-endian sends the high word first to match XDR network representation.

For VAX targets the file defines bitfield layouts for VAX and IEEE single/double values. Encode paths translate VAX exponent/mantissa/sign into IEEE-style fields, with limit tables for max/min edge encodings. Decode paths perform the inverse translation and copy the resulting VAX representation into the destination.

`XDR_FREE` is a no-op for both functions, returning `TRUE`.

Dependencies are the generic RPC XDR interface in `<rpc/xdr.h>`, machine endian definitions for IEEE targets, and VAX-specific bitfield assumptions when `__vax__` is defined.

Research notes and risks:
- The IEEE path type-puns `float *` and `double *` through `int32_t *`; this is traditional RPC libc code but sensitive to aliasing/alignment assumptions.
- VAX support relies on implementation-defined bitfield layout.
- Floating NaN payload/signaling behavior is not normalized on IEEE targets; the raw representation is transported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_rec.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_rec.c

This file implements XDR record marking streams, the framing layer used by connection-oriented RPC over byte streams. It creates an `XDR` backend that reads and writes records made of one or more fragments. Each fragment starts with a 32-bit network-order header: the top bit is `LAST_FRAG`, and the lower 31 bits are the fragment byte count.

The central private state is `RECSTREAM`, stored in `xdrs->x_private`. It contains output buffer pointers, current fragment header position, input buffer pointers, fragment bytes remaining, last-fragment state, callback handles for transport read/write, original send/receive sizes, and nonblocking assembly state including partial header, received byte count, record length, and max-record limit.

`xdrrec_create` allocates and initializes the stream, fixes small buffer sizes to rounded 4000-byte defaults, allocates input/output buffers, installs `xdrrec_ops`, and stores the caller-provided opaque TCP handle plus read/write callbacks.

The XDR ops implement word and byte encode/decode over the record buffer:
- `xdrrec_getlong`, `xdrrec_getbytes`, and `xdrrec_inline` consume bytes within the current fragment and fetch more fragments as needed.
- `xdrrec_putlong`, `xdrrec_putbytes`, and `xdrrec_inline` append to the current output fragment, flushing when full.
- `xdrrec_getpos`/`xdrrec_setpos` support limited repositioning inside buffered data.
- `xdrrec_destroy` frees both buffers and the `RECSTREAM`.

Public record controls are `xdrrec_skiprecord`, `xdrrec_eof`, and `xdrrec_endofrecord`. Skipping drains the current record and aligns the next decode. EOF checks whether buffered data remains after consuming the current record. End-of-record either flushes immediately or seals the current fragment and reserves a new fragment header for batching.

Nonblocking support is provided by `__xdrrec_getrec` and `__xdrrec_setnonblock`. In nonblocking mode, reads assemble a complete record into the input buffer before decode proceeds. It tracks partial headers, rejects zero fragments, rejects fragments or cumulative records above `in_maxrec`, reallocates the input buffer up to the record size, and returns transport status through `enum xprt_stat`.

Internal helpers handle flushing, blocking input refill, byte copying/skipping, fragment header parsing, buffer size rounding, and input buffer reallocation.

Research notes and risks:
- The blocking path does not enforce the nonblocking `in_maxrec` limit; it only rejects a literal zero header in `set_input_fragment`.
- `xdrrec_getpos` treats `tcp_handle` as an fd for `lseek`, which is only meaningful for transports where the opaque handle is actually fd-like.
- Nonblocking full-record buffering protects request size but can reallocate to the configured maximum, so the max-record setting is important for memory pressure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_rec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_reference.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_reference.c

This file implements pointer/reference XDR helpers: `xdr_reference` and `xdr_pointer`.

`xdr_reference` serializes or deserializes an object reached through a pointer. If the pointed-to storage is NULL during decode, it allocates `size` bytes with `mem_alloc`, zeroes the object, then invokes the supplied XDR procedure. During free, NULL references are ignored, and non-NULL objects are passed to the supplied XDR procedure in `XDR_FREE` mode before being freed and nulled.

`xdr_pointer` adds a boolean presence tag around `xdr_reference`, allowing recursive/tree-like pointer structures to preserve NULL vs non-NULL. It first encodes/decodes `more_data` with `xdr_bool`; if false, it sets the pointer to NULL and returns success. If true, it delegates to `xdr_reference`.

Dependencies are the RPC memory allocation API, `xdr_bool`, and caller-provided object XDR procedures.

Research notes and risks:
- Encode with a NULL pointer and direct `xdr_reference` can call the object procedure with NULL because only decode allocates; callers needing nullable pointers should use `xdr_pointer`.
- Allocation failure is reported with `warn` and returns `FALSE`.
- Free behavior assumes the object XDR procedure can safely free nested allocations before the outer object is freed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_reference.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_sizeof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_sizeof.c

This file implements `xdr_sizeof`, a measuring XDR backend that runs an XDR encode procedure without producing a real serialized buffer and returns the number of bytes that would be emitted.

It defines a local `xdr_ops` vector where put operations increment `x_handy`: `x_putlong` adds one XDR unit, and `x_putbytes` adds the requested byte count. `x_inline` supports encode-only inline requests by allocating or reusing a scratch buffer large enough for the inline region, incrementing `x_handy`, and returning that scratch memory. Get operations are harmless stubs returning false/null, because `xdr_sizeof` only runs in `XDR_ENCODE` mode.

`xdr_sizeof` initializes a stack `XDR`, installs these ops, calls the supplied `xdrproc_t`, frees any scratch inline buffer, and returns the counted size on success or 0 on failure.

Research notes and risks:
- Size counting depends on the supplied XDR procedure taking the normal encode path and honoring op return values.
- The inline scratch buffer exists only to satisfy encode procedures that write through `XDR_INLINE`; its contents are discarded.
- `x_base` is used as a stored allocation size via pointer/integer casts, which is compact but non-obvious.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_sizeof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_stdio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_stdio.c

This file implements an XDR backend over a standard C `FILE *`, exported as `xdrstdio_create`.

`xdrstdio_create` initializes the caller-provided `XDR` object with operation mode, a static stdio ops vector, and the `FILE *` in `x_private`. The ops serialize and deserialize 32-bit longs using `htonl`/`ntohl` around `fwrite`/`fread`, copy counted bytes with stdio calls, report position through `ftell`, seek through `fseek`, and flush the stream on destroy.

Inline access is deliberately unsupported and always returns NULL because stdio buffering cannot easily guarantee alignment and contiguous availability for XDR inline macros.

Research notes and risks:
- `xdrstdio_destroy` flushes but does not close the underlying file.
- Position is returned as `u_int`, so large stream offsets can truncate.
- Byte reads/writes use one `fread`/`fwrite` item of length `len`; partial I/O returns failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_stdio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.fenv.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.fenv.inc

This makefile fragment adds floating-environment support files for the libc softfloat build.

It extends `.PATH` to `${.CURDIR}/softfloat`, adds architecture and shared softfloat include directories, defines `SOFTFLOAT_FOR_GCC`, and appends the floating environment accessors to `SRCS`: `fpgetround.c`, `fpsetround.c`, `fpgetmask.c`, `fpsetmask.c`, `fpgetsticky.c`, and `fpsetsticky.c`.

Research notes and risks:
- Defining `SOFTFLOAT_FOR_GCC` narrows softfloat compilation to the ABI/compiler-support subset expected by this libc build.
- The fragment is included by `Makefile.inc`, so changes here affect all softfloat build variants using that include.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.fenv.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.inc

This makefile fragment wires softfloat into libc.

It defaults `SOFTFLOAT_BITS` to 64 and sets `.PATH` to architecture-specific softfloat files plus `${.CURDIR}/softfloat/bits${SOFTFLOAT_BITS}` and the common softfloat directory. It adds architecture/common include directories, defines `SOFTFLOAT_FOR_GCC`, starts `SRCS.softfloat` with `softfloat.c`, and includes `softfloat/Makefile.fenv.inc` for rounding/mask/sticky accessors.

For ARM EABI machine arches it adds AEABI comparison helper sources. For other architectures it adds GCC-style comparison/negation/unordered helper sources for single, double, quad, and extended formats as applicable. It always adds `flt_rounds.c` and then appends `SRCS.softfloat` to `SRCS`.

There is also a GCC-specific warning suppression for MIPS and SH3 softfloat builds, disabling `-Wenum-compare` for `softfloat.c`.

Research notes and risks:
- `SOFTFLOAT_BITS` selects between bits32 and bits64 implementations; the listed group researches the bits32 implementation, but the default here is bits64 unless overridden by architecture make context.
- Source selection is ABI-sensitive, especially ARM EABI comparison helpers versus generic libgcc-style helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits32/softfloat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits32/softfloat.c

This file is NetBSD’s bits32 variant of John Hauser’s SoftFloat Release 2a, adapted for GCC `-msoft-float`. It implements software IEEE-style single-precision and double-precision operations using 32-bit word arithmetic. This variant notes that `float64` is represented as a 64-bit integer rather than the original two-word structure, with `FLOAT64_MANGLE`/`FLOAT64_DEMANGLE` hooks for platform representation.

Global softfloat state is provided when not supplied externally: `float_rounding_mode` defaults to nearest-even, and `float_exception_flags` records raised exceptions. Target-specific behavior is pulled from `softfloat-specialize`, while primitive multiword arithmetic and estimates come from `softfloat-macros`.

The file defines low-level helpers for extracting, normalizing, packing, and rounding:
- single helpers extract sign/exponent/fraction, normalize subnormals, pack fields, and `roundAndPackFloat32`;
- double helpers extract high/low fraction words from the 64-bit value, normalize subnormals, pack fields through `FLOAT64_MANGLE`, and `roundAndPackFloat64`;
- normalization wrappers handle unnormalized significands before final rounding.

Always-built conversion and operation exports include `int32_to_float32`, `int32_to_float64`, `float32_to_int32_round_to_zero`, `float32_to_float64`, `float64_to_int32_round_to_zero`, `float64_to_float32`, `float32_add`, `float32_sub`, `float32_mul`, `float32_div`, `float64_add`, `float64_sub`, `float64_mul`, `float64_div`, and ordered comparisons `eq`, `le`, and `lt` for both float sizes. These implement IEEE special cases: NaN propagation, infinity handling, signed zeros, divide-by-zero, invalid operations such as infinity minus infinity or zero times infinity, and inexact/underflow/overflow flagging.

Additional functions are compiled only when `SOFTFLOAT_FOR_GCC` is not defined. These include current-rounding-mode integer conversions, round-to-integer, remainder, square root, signaling comparisons, and quiet comparison variants for both float32 and float64.

The arithmetic structure is classic SoftFloat:
- addition/subtraction split into same-sign significand addition and opposite-sign subtraction helpers;
- multiplication uses 32x32 or 64x64-to-128 intermediate products;
- division uses quotient estimates with correction loops;
- square root uses estimate functions plus remainder correction;
- comparisons explicitly handle NaNs and signed-zero equality.

Research notes and risks:
- This file’s normal libc build path defines `SOFTFLOAT_FOR_GCC` via the makefiles, excluding many non-GCC helper functions.
- Several non-`SOFTFLOAT_FOR_GCC` double routines still use `.high` and `.low` member syntax even though the file header says `float64` is a 64-bit integer in this NetBSD variant. That is likely harmless for the default GCC-support build but is a compatibility risk if building the full non-GCC bits32 file as-is.
- Correctness relies heavily on `softfloat-macros` and `softfloat-specialize`, especially NaN classification/propagation, tininess policy, exception raising, and multiword arithmetic.
- This code is central ABI support for soft-float targets; regressions would affect compiler-emitted floating-point helper calls and libc floating-environment behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/bits32/softfloat.c -->
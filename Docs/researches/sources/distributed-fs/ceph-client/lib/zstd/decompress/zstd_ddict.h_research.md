# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.h

## Purpose
Declares the private decompression-dictionary bridge used by the Zstd decompressor implementation. It keeps `ZSTD_DDict` internals opaque to most code while exposing the minimal accessors and context-copy hook needed by decompression setup.

## Important APIs, Types, and Functions
The header includes the Zstd dependency header for `size_t` and `<linux/zstd.h>` for public `ZSTD_DDict`, `ZSTD_DCtx`, and dictionary API declarations. It declares `ZSTD_DDict_dictContent()`, `ZSTD_DDict_dictSize()`, and `ZSTD_copyDDictParameters()`. Comments note that public construction, destruction, sizing, and dict-ID functions are declared in `zstd.h`; this header adds only implementation-facing accessors not intended as the broad public ABI.

## Control Flow
There is no executable control flow in the header. It only provides declarations guarded by `ZSTD_DDICT_H`. Runtime behavior is implemented by `zstd_ddict.c`, where the accessors assert a non-null DDict and where `ZSTD_copyDDictParameters()` seeds a `ZSTD_DCtx`.

## State and Persistence Behavior
The header owns no state. It exposes functions that read DDict-owned dictionary content and size, and a function that copies references and entropy pointers into a decompression context. The persistence contract is implicit: DDict storage must remain valid for users that reference its content or entropy tables.

## Dependencies and Integration Points
This header is included by `zstd_ddict.c` and `zstd_decompress.c`. It is the narrow interface between the DDict implementation and the frame/stream decompressor. It depends on public Linux Zstd declarations rather than defining `ZSTD_DDict` itself, preserving opacity outside the dictionary implementation.

## Risks and Edge Cases
Risk is mostly interface drift: if `ZSTD_DDict` fields or `ZSTD_DCtx` dictionary setup semantics change in `zstd_ddict.c` or `zstd_decompress_internal.h`, the prototypes here may no longer express enough contract for safe use. Because the accessors assert non-null input rather than returning nullable-safe defaults, callers must validate DDict pointers first unless the API explicitly permits `NULL` elsewhere.

## Test Signals
Compile coverage is the primary signal: both dictionary and decompressor translation units should build with this header, and public declarations in `<linux/zstd.h>` must remain compatible. Runtime tests are inherited from `zstd_ddict.c`: DDict creation, context seeding, by-reference lifetime, and dictionary-ID behavior.

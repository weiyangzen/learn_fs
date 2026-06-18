<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.c -->
# sources/distributed-fs/orangefs/src/proto/endecode-funcs.c

## Purpose
Provides non-inline wrapper functions for primitive encode/decode operations. These wrappers adapt typed macro encoders to generic function-pointer shapes that accept `void *`.

## Important APIs, Types, and Functions
Defines `encode_func_uint64_t`, `decode_func_uint64_t`, `encode_func_int64_t`, `decode_func_int64_t`, `encode_func_uint32_t`, `decode_func_uint32_t`, `encode_func_int32_t`, `decode_func_int32_t`, `encode_func_string`, and `decode_func_string`. It includes `endecode-funcs.h` with `__PINT_REQPROTO_ENCODE_FUNCS_C` set and `pvfs2-encode-stubs.h`.

## Control Flow
Each wrapper casts the generic `void *x` to the concrete expected pointer type and invokes the corresponding macro from `endecode-funcs.h`, advancing `*pptr` as the macro writes or reads wire data.

## State and Persistence
No state is stored. Functions operate on caller-provided encode/decode cursors and buffers.

## Dependencies and Integration Points
Used where encode/decode functions need to be referenced as symbols rather than header-only static inline macros. It depends on primitive byte-order macros and string encoding semantics defined in `endecode-funcs.h`.

## Risks
The wrappers trust callers to pass correctly typed storage. Passing a scalar value instead of a pointer, or a pointer with insufficient lifetime for decoded strings, will corrupt memory or produce dangling references.

## Test Signals
Unit-test primitive round trips through wrapper functions, verify pointer advancement for each primitive width and string alignment, and compile/link consumers that require `encode_func_*`/`decode_func_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/endecode-funcs.c -->

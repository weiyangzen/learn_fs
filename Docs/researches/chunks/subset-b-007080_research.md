# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-c.c lines 1-8661

## Scope

This chunk covers the start of GlusterFS's precompiled C erasure-coding backend. It includes the file prologue, `WIDTH` definition, and the generated-style `gf8_muladd_XX()` kernels from `0x00` through `0xBF`, plus the opening and partial body of `gf8_muladd_C0()`. The function-pointer dispatch table, zero buffer, and public `ec_code_c_prepare()`, `ec_code_c_linear()`, and `ec_code_c_interleaved()` wrappers are outside this chunk and appear later in the same file.

## Purpose

The covered code provides portable fallback kernels for GlusterFS dispersed-volume erasure coding when dynamic code generation is unavailable or disabled. Each `gf8_muladd_XX()` routine performs a fixed multiplication-add step over GF(2^8), using only 64-bit loads, XORs, and stores. The routines are fully unrolled per coefficient so the runtime encoder/decoder can select a coefficient-specific function instead of interpreting Galois-field operations inside the hot data path.

The arithmetic model is:

- Treat one erasure-coding chunk as eight bit planes, each `EC_METHOD_WORD_SIZE` bytes wide.
- For each `uint64_t` lane position, load the current `out` bit planes into `in0` through `in7`.
- Compute `coefficient * out` in GF(2^8) as XOR combinations of those bit planes.
- XOR the incoming `in` bit planes into the transformed result, producing `out = coefficient * old_out + in`.

`gf8_muladd_00()` is the initialization special case: it copies one full chunk from `in` to `out`, equivalent to `out = in` when the previous accumulator is ignored. `gf8_muladd_01()` is plain XOR accumulation. The remaining complete functions in this chunk implement coefficients `0x02` through `0xBF`; `gf8_muladd_C0()` starts at line 8655 but is not complete within the requested range.

## Important APIs, Types, and Functions

- `EC_METHOD_WORD_SIZE` and `EC_METHOD_CHUNK_SIZE` come from `ec-method.h`. In this tree they are 64 bytes and `64 * 8 == 512` bytes respectively.
- `WIDTH` is `EC_METHOD_WORD_SIZE / sizeof(uint64_t)`, so the inner loop processes eight 64-bit lanes per bit plane.
- `gf8_muladd_00(void *out, void *in)` copies `EC_METHOD_WORD_SIZE * 8` bytes from `in` to `out`.
- `gf8_muladd_01(void *out, void *in)` XORs each of the eight bit-plane lanes from `in` into `out`.
- `gf8_muladd_02()` through `gf8_muladd_BF()` are coefficient-specialized carryless multiply-add kernels. They differ only in the XOR network used to transform `old_out` before adding `in`.
- `gf8_muladd_C0()` is visible only through its setup and first output assignment in this chunk; the rest of that coefficient kernel belongs to the following chunk.

The kernels are `static` and are not exported directly. Later code in this file builds a `gf8_muladd[]` table mapping byte coefficients to these functions, and `ec-code-c.h` exports only the wrapper functions used by `ec-code.c`.

## Control Flow

Every complete kernel except `gf8_muladd_00()` follows the same loop shape:

1. Cast `in` and `out` to `uint64_t *`.
2. Iterate `i` from `0` to `WIDTH - 1`.
3. Read the current accumulator bit planes from `out_ptr[0]`, `out_ptr[WIDTH]`, ..., `out_ptr[WIDTH * 7]`.
4. Compute eight local `out0` through `out7` values using XOR-only expressions, often with temporary values to reduce repeated subexpressions.
5. Store each result as `computed_outN ^ in_ptr[WIDTH * N]`.
6. Increment both pointers by one 64-bit lane, advancing to the next lane within all eight planes.

The surrounding integration, visible in adjacent files, is:

- `ec-code.c` tries dynamic code generation first. If that fails, it calls `ec_code_c_prepare()` and returns either `ec_code_c_linear` or `ec_code_c_interleaved`.
- `ec-method.c` builds per-row encode/decode functions from matrix coefficients and calls the selected function over each `EC_METHOD_CHUNK_SIZE` or stripe-sized block.
- Encode paths use linear source layout; decode paths use interleaved source pointers. The actual public wrappers and dispatch table are after this chunk.

## State and Persistence Behavior

The covered functions have no persistent state, heap allocation, locks, I/O, or error returns. Their only state is the caller-provided `out` buffer, which is modified in place. The caller is responsible for passing buffers large enough for one `EC_METHOD_CHUNK_SIZE` block and for arranging source/destination offsets.

The code relies on stable field configuration from the broader EC method layer:

- `EC_GF_BITS == 8`;
- `EC_GF_MOD == 0x11D`;
- `EC_METHOD_WORD_SIZE == 64`;
- chunk layout is eight 64-byte bit planes.

Any change to those constants, bit-plane layout, or generated XOR networks changes the wire/storage-compatible erasure-coding result. The functions themselves do not validate those assumptions at runtime.

## Dependencies and Integration Points

Direct includes are `<inttypes.h>`, `<string.h>`, `ec-method.h`, and `ec-code-c.h`. The functional dependencies are broader:

- `ec-method.h` defines GF and chunk constants and the encode/decode method API.
- `ec-galois.c` prepares GF(2^8) log/pow tables and multiplication metadata with modulus `0x11D`.
- `ec-code.c` selects this C backend as fallback when dynamic backend generation cannot be used.
- `ec-method.c` invokes the backend through matrix row functions for normal encoding and inverse-matrix decoding.
- Higher EC translator files use `EC_METHOD_CHUNK_SIZE` and the same GF metadata in volume configuration, alignment, heal, read, and write paths.

The coefficient kernels are designed as hot-path internals. External callers should use `ec_code_build_linear()` / `ec_code_build_interleaved()` via the method layer rather than calling these static functions.

## Risks and Edge Cases

- The source is generated-style and hard to audit manually. A single wrong XOR term in one coefficient kernel can silently corrupt encoded fragments or decoded data for matrix rows using that coefficient.
- This chunk boundary cuts through `gf8_muladd_C0()`, so validation of coefficient `0xC0` and later coefficients must be handled by subsequent chunk research and whole-file tests.
- The kernels cast arbitrary `void *` buffers to `uint64_t *`. Callers must preserve the alignment guarantees enforced elsewhere in the EC translator; unaligned access can be slow or unsafe on strict-alignment platforms.
- There is no bounds checking. The code assumes at least `EC_METHOD_CHUNK_SIZE` bytes are readable from `in` and writable in `out`.
- `gf8_muladd_00()` uses `memcpy(out, in, ...)`; overlapping `in`/`out` ranges would be undefined. The normal encode/decode flow should provide distinct source and destination buffers.
- The routines assume little about byte order because they operate on bit-plane words with XOR only, but they do assume the bit-plane packing used by the rest of this backend.
- The fallback is portable but large. Compiler optimization level, inlining decisions, and instruction scheduling can materially affect EC throughput.
- The function table is outside this chunk. Whole-file validation must ensure every coefficient index maps to the matching `gf8_muladd_XX()` implementation exactly once.

## Test Signals

Useful tests for this chunk and its merge with later chunks include:

- Golden-vector tests for every coefficient from `0x00` through `0xBF`, comparing `gf8_muladd_XX()` behavior with a simple table-driven GF(2^8) multiply-add reference over the same bit-plane layout.
- Boundary tests for `gf8_muladd_00()` copy and `gf8_muladd_01()` XOR accumulation.
- Randomized encode/decode round trips through `ec_method_encode()` and `ec_method_decode()` with dynamic code generation disabled, forcing the C fallback.
- Matrix rows that exercise high coefficients covered here, especially `0x80` through `0xBF`.
- Alignment-sensitive tests or sanitizer runs on architectures/configurations that expose unaligned `uint64_t *` access.
- Memory-safety tests around exact `EC_METHOD_CHUNK_SIZE` buffers to catch off-by-one plane or lane indexing errors.
- Cross-backend equivalence tests comparing dynamically generated code with the C fallback for the same GF coefficients and input buffers.
- Whole-file table tests confirming that dispatch index `n` calls `gf8_muladd_nn`; this must include the table outside this chunk.

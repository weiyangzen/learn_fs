# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-c.c lines 8662-11679

## Scope

This chunk covers the tail of GlusterFS erasure-code C backend `ec-code-c.c`, beginning inside `gf8_muladd_C0()` and ending at the three exported C codec entry points. The visible section contains specialized GF(2^8) multiply-add kernels for coefficients `0xC0` through `0xFF`, the complete 256-entry `gf8_muladd[]` dispatch table, the static zero block used to flush the last interleaved operation, and the public functions declared by `ec-code-c.h`: `ec_code_c_prepare()`, `ec_code_c_linear()`, and `ec_code_c_interleaved()`.

The source file as a whole is a generated-style, scalar C implementation for the EC translator's Galois-field coding path. Earlier chunks define the same family of `gf8_muladd_XX()` kernels for coefficients `0x00` through `0xBF`; this chunk completes that table and shows how callers invoke it.

## Purpose

The code implements a portable fallback or baseline erasure-code arithmetic backend for GlusterFS. It operates on fixed-size EC method chunks where `EC_METHOD_WORD_SIZE` is `64`, `EC_GF_BITS` is `8`, and `EC_METHOD_CHUNK_SIZE` is `512` bytes. Internally each chunk is treated as eight bit-slices of `EC_METHOD_WORD_SIZE` bytes, accessed as `uint64_t` lanes. `WIDTH` is `EC_METHOD_WORD_SIZE / sizeof(uint64_t)`, so each kernel loops over eight 64-bit words per bit-slice.

Each `gf8_muladd_XX(out, in)` function applies a hard-coded multiplication by one GF(2^8) coefficient and XOR-adds the supplied source block into the destination accumulator. The functions are not generic table lookups at the byte level; they are straight-line XOR networks over eight bit planes. This keeps the hot encode/decode loop branch-light and avoids per-byte multiplication overhead.

The public entry points adapt this kernel family to two storage layouts:

- `ec_code_c_linear()` handles encode-style contiguous input stripes where source chunks are adjacent in memory.
- `ec_code_c_interleaved()` handles decode-style input where each surviving source column is passed as a separate pointer.
- `ec_code_c_prepare()` rewrites matrix row coefficients so the linear and interleaved loops can use chained multiply-add operations efficiently.

## Important APIs, Types, and Data

`gf8_muladd_C0()` through `gf8_muladd_FF()` are static functions with the uniform signature `void (*)(void *out, void *in)`. The chunk starts after the prologue of `gf8_muladd_C0()` but includes its result writes and all complete functions through `gf8_muladd_FF()`. Each complete kernel:

- casts `in` and `out` to `uint64_t *`;
- loops `i` from `0` to `WIDTH - 1`;
- reads eight existing destination bit planes from `out_ptr[0]`, `out_ptr[WIDTH]`, ..., `out_ptr[WIDTH * 7]`;
- computes transformed `out0` through `out7` using XOR-only expressions and temporary values;
- writes each transformed plane XORed with the corresponding source plane from `in_ptr`;
- increments both pointers by one 64-bit lane.

`gf8_muladd_00()` is defined earlier and is semantically special: it initializes the destination with `memcpy(out, in, EC_METHOD_WORD_SIZE * 8)`. In this file's calling convention, the first selected source chunk is copied into the destination accumulator, and later sources are XOR-added after coefficient transforms.

`gf8_muladd_01()` is also special and defined earlier: it is pure XOR-add without a coefficient transform. All other kernels, including this chunk's `0xC0` to `0xFF` range, encode a specific GF multiplication network before XORing the new input.

`gf8_muladd[]` is the static dispatch table indexed directly by an 8-bit coefficient. It lists all functions from `gf8_muladd_00` through `gf8_muladd_FF` in numeric order. This table is the integration point between prepared matrix coefficients and coefficient-specific code.

`zero` is a static `uint64_t zero[EC_METHOD_WORD_SIZE * 8] = { 0, };` used by `ec_code_c_interleaved()` as a zero source block. The array is larger than the number of `uint64_t` words actually read by the kernels, but it safely supplies zero-valued storage for the same `EC_METHOD_WORD_SIZE * 8` byte span used by normal chunks.

`ec_code_c_prepare(ec_gf_t *gf, uint32_t *values, uint32_t count)` walks a matrix row from right to left. For each nonzero coefficient, it divides that coefficient by the previous nonzero coefficient using `ec_gf_div()`, then updates `last` to the original coefficient. This mutates the row values in place.

`ec_code_c_linear(void *dst, void *src, uint64_t offset, uint32_t *values, uint32_t count)` offsets into a contiguous source stripe, initializes `dst` from the first source chunk with `gf8_muladd_00()`, then advances by `EC_METHOD_CHUNK_SIZE` for each remaining column and calls `gf8_muladd[*values]`.

`ec_code_c_interleaved(void *dst, void **src, uint64_t offset, uint32_t *values, uint32_t count)` walks separate source pointers. It skips leading zero coefficients, initializes `dst` from the first nonzero source with `gf8_muladd_00()`, then applies the previous nonzero coefficient to the current nonzero source while carrying the current coefficient forward as `last`. After all source columns have been processed, it calls `gf8_muladd[last](dst, zero)` to complete the final deferred transform.

The visible public signatures match `ec_code_func_linear_t` and `ec_code_func_interleaved_t` from `ec-types.h`, and are declared in `ec-code-c.h`.

## Control Flow

The kernel-level control flow is deliberately simple and repeated. For every 64-bit lane position in the 512-byte EC chunk, the function reads the destination accumulator as eight bit-sliced lanes, computes the GF multiplication network for its coefficient, and stores the transformed accumulator XORed with the source lanes. There are no conditionals in the per-lane hot path.

The dispatch flow is coefficient-driven. `ec_code_c_linear()` assumes `dst` should first become the first chunk at `src + offset`; this is a copy, not an add. It then decrements `count` in a loop, moves `src` by one chunk, dispatches through `gf8_muladd[*values]`, and advances `values`. The row coefficients are expected to have already been prepared so each dispatched coefficient represents the next transform in the chain rather than the raw matrix entry.

The interleaved decode flow defers multiplication by one nonzero coefficient. It first advances through leading zeros in `values`, preserving the source-column index `i`. It copies the first nonzero source chunk into `dst`. For later nonzero coefficients, it applies the previous coefficient (`last`) to the current source pointer, then assigns `last = tmp`. At loop end, applying `last` against the static zero block transforms the accumulator without adding a further source. This makes the same multiply-add primitive serve as both "multiply accumulated value" and "add next source" by feeding zero for the final addend.

At the EC-method layer, `ec_method_matrix_init()` builds row function pointers through `ec_code_build_linear()` for normal encoding rows and `ec_code_build_interleaved()` for inverse decode rows. The scalar C backend functions are then invoked from `ec_method_encode()` and `ec_method_decode()` over each chunk-sized position.

## State and Persistence Behavior

The multiply-add kernels have no durable state. They mutate only the caller-provided destination buffer and read the caller-provided source buffer. All temporaries are stack locals.

`ec_code_c_prepare()` is stateful with respect to its `values` array: it rewrites the coefficients in place. Those arrays are stored in matrix row data, so the prepared form persists for subsequent encode or decode calls using the same matrix object. The transformation depends on `ec_gf_t`, whose log/pow/table data is owned by the EC method's Galois-field context.

`gf8_muladd[]` and `zero` are file-scope static data. The dispatch table is immutable after program load. `zero` is initialized once to all zeroes and should remain read-only by convention, though it is not declared `const`.

The chunk functions do not allocate memory, take locks, or persist metadata. Buffer lifetime, alignment, and size are owned by the surrounding EC method and translator code.

## Dependencies and Integration Points

This chunk includes and depends on:

- `ec-method.h` for `EC_METHOD_WORD_SIZE`, `EC_METHOD_CHUNK_SIZE`, and the EC method constants.
- `ec-code-c.h` for the public C backend declarations.
- `ec-galois.h` through `ec-method.h` for `ec_gf_div()` and the `ec_gf_t` arithmetic context.
- `ec-types.h` for the function pointer typedefs and matrix structures used by callers.
- `<inttypes.h>` for fixed-width integer types and `<string.h>` indirectly for earlier `gf8_muladd_00()` copying.

The caller integration is in `ec-method.c`. Matrix initialization uses `ec_code_build_linear()` or `ec_code_build_interleaved()` to obtain a row function; encode loops call the linear function once per parity/output row and chunk position, while decode loops call interleaved functions over surviving input pointers to reconstruct output chunks.

The larger EC translator integrates this arithmetic with GlusterFS data placement, healing, reads, writes, and reconstruction. This file is below the policy layer: it only performs deterministic block arithmetic for matrices already chosen by the EC method.

## Risks and Edge Cases

The biggest correctness risk is coefficient/table drift. `gf8_muladd[]` must remain exactly ordered from `0x00` to `0xFF`; one misplaced function pointer silently corrupts all rows using that coefficient. The XOR networks inside `gf8_muladd_C0()` through `gf8_muladd_FF()` must match the same GF(2^8) polynomial and bit-sliced representation used by `ec_gf_mul()`/`ec_gf_div()` and the matrix generator.

`ec_code_c_interleaved()` assumes at least one nonzero coefficient exists. If all `values` are zero or if `count` is zero, the initial `while ((last = *values++) == 0)` can read past the coefficient array. Matrix construction likely guarantees usable rows, but this function itself does not guard that contract.

The code uses `void *` arithmetic (`src += offset`, `src[i] + offset`, `out[i] += EC_METHOD_CHUNK_SIZE` in callers). That is a GNU C extension, not ISO C. It is acceptable in the GlusterFS build context but matters for portability.

All kernels cast arbitrary buffers to `uint64_t *`. They assume the input and output buffers are aligned enough for 64-bit accesses and contain at least `EC_METHOD_CHUNK_SIZE` bytes. Misaligned buffers may be slow or invalid on strict-alignment architectures.

Source and destination aliasing is not explicitly handled beyond the intended accumulator update. If `in` overlaps `out` in an unexpected way, the kernels can read partially updated data because they load destination planes, compute, then write back while incrementing through the same memory layout.

`zero` is mutable static storage and not `const`. Accidental writes in this file or through memory corruption would break the final interleaved transform. Marking it `const` would better express intent, but that is outside this research chunk's task.

Because the code is hand-unrolled/generated and repetitive, review by inspection is error-prone. Small transcription mistakes in a single coefficient network are hard to detect without algebraic or exhaustive tests.

## Test Signals

Useful validation signals for this chunk include:

- Unit or self-test coverage comparing every `gf8_muladd_XX()` coefficient against a trusted byte-level `ec_gf_mul()` implementation over randomized 512-byte chunks.
- Exhaustive coefficient tests ensuring `gf8_muladd[]` index `n` dispatches the implementation for coefficient `n`, especially around the table tail `0xC0` through `0xFF`.
- Encode/decode round trips through `ec_method_encode()` and `ec_method_decode()` for multiple `(columns, rows)` configurations, masks, and recovered row sets.
- Tests that exercise coefficients in the high range covered by this chunk, not only common low coefficients.
- Matrix preparation tests checking that `ec_code_c_prepare()` produces the same encoded or decoded outputs as direct matrix multiplication with raw coefficients.
- Interleaved decode tests with leading zero coefficients and sparse coefficient rows, plus a negative/fuzz test for all-zero rows if the surrounding matrix builder is expected to reject them.
- Alignment-sensitive runs on architectures or sanitizers that can catch unaligned 64-bit loads/stores.
- Memory sanitizer or bounds-checking runs over exact `EC_METHOD_CHUNK_SIZE` buffers to catch overreads from `zero`, source chunks, or destination chunks.
- Performance regression tests for scalar C backend throughput because these functions are in the hot encode/decode path.

## Cross-Chunk Notes

This chunk starts in the middle of `gf8_muladd_C0()`. The function's signature and early local-variable setup appear in the preceding chunk. Earlier chunks also define `gf8_muladd_00()` through `gf8_muladd_BF()`, including the copy and XOR-only special cases that are essential to interpreting `ec_code_c_linear()` and `ec_code_c_interleaved()`.

The merge lane should combine this report with the preceding chunks for `sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-c.c` before producing the final source-tree-aligned per-file report. This chunk alone covers the dispatch closure and exported entry points, but not the complete set of coefficient kernels.

# sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress_safe.c

## Purpose
`lzo1x_compress_safe.c` builds the bounded-output variant of the LZO compressor by defining safety macros and including `lzo1x_compress.c`. This avoids duplicating the compressor algorithm while producing `_safe` entry points that honor the caller's destination length.

## Important APIs, types, and functions
This file defines `LZO_SAFE(name) name##_safe` and `HAVE_OP(x) ((size_t)(op_end - op) >= (size_t)(x))`, then includes the main compressor source. As a result, the generated exported symbols are `lzo1x_1_compress_safe()` and `lzorle1x_1_compress_safe()`. All helper functions from the included source are renamed consistently through the same macro.

## Control flow
The runtime control flow is inherited from `lzo1x_compress.c`. The important behavioral difference is that every `NEED_OP(x)` in the included file becomes a real capacity check against `op_end`. On failure, control jumps to the included source's `output_overrun` label and returns `LZO_E_OUTPUT_OVERRUN`.

## State and persistence
The safe object maintains no additional state beyond the included compressor's local variables and caller work memory. It treats `*out_len` as the destination capacity on entry and rewrites it to the produced compressed length on success. On output overrun, callers should treat destination contents as incomplete.

## Dependencies and integration points
The file is tightly coupled to the macro structure of `lzo1x_compress.c`; changes to helper names or output-check conventions there affect this object. It is linked into `lzo_compress.o` by `lib/lzo/Makefile` and is the variant used by crypto front ends that cannot assume worst-case destination sizing.

## Risks and test signals
The main risk is macro-inclusion fragility: adding a new output write in `lzo1x_compress.c` without `NEED_OP()` would silently bypass safe bounds here. Another risk is divergence between direct and safe symbol behavior beyond capacity handling. Test signals are deliberate tiny output buffers returning `LZO_E_OUTPUT_OVERRUN`, adequate worst-case buffers producing streams byte-compatible with the normal compressor for the same version, and build checks that both safe symbols export under `CONFIG_LZO_COMPRESS`.

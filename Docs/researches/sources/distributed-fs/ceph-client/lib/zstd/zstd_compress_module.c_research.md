# sources/distributed-fs/ceph-client/lib/zstd/zstd_compress_module.c

## Purpose
`zstd_compress_module.c` is the Linux kernel export wrapper for Zstd compression. It translates the kernel-facing `zstd_*` API into upstream `ZSTD_*` context, parameter, dictionary, one-shot, streaming, and external-sequence APIs.

## Important APIs, types, and functions
The helper `zstd_cctx_init` resets a compression context, sets pledged source size, and applies compression and frame parameters. Exported symbols include compression level queries, bound/parameter helpers, workspace-bound helpers with and without external sequence producers, static and dynamic context creation/free, CDict creation/free, one-shot compression, CDict compression, streaming init/reset/compress/flush/end, sequence producer registration, and `zstd_compress_sequences_and_literals`.

## Control flow
Most wrappers validate only the static workspace pointer or normalize Linux API conventions before calling upstream APIs. `zstd_cctx_init` is the central setup path for one-shot and streaming initialization. The external-sequence workspace-bound helpers register a dummy producer to force sizing for contexts that may use producer state. Streaming init and reset map a pledged size of zero to `ZSTD_CONTENTSIZE_UNKNOWN`.

## State and persistence
State is held in caller-provided or dynamically allocated `zstd_cctx`, `zstd_cstream`, and `zstd_cdict` objects. The module itself stores no mutable global state. Context state persists until reset or free and includes parameters, pledged size, dictionaries, and optional sequence producer hooks.

## Dependencies and integration points
It depends on Linux module/string/kernel headers, `<linux/zstd.h>`, Zstd deps/internal headers, and compression internals. Kernel users such as filesystems, crypto users, or storage code link to these exported wrappers instead of the raw upstream names.

## Risks and test signals
Risks include parameter translation drift, workspace-bound underestimation, static-context NULL handling, pledged-size convention mismatches, external sequence producer sizing, and error propagation through `size_t` Zstd error codes. Test signals include all compression levels, static and dynamic context paths, CDict by-reference lifetime tests, streaming with known and unknown sizes, external-sequence compression, and module export checks.

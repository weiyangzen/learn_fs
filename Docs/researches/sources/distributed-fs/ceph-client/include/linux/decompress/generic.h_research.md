# sources/distributed-fs/ceph-client/include/linux/decompress/generic.h

Purpose: Defines the common decompressor function signature and magic-detection helper used by kernel decompression frontends.

Important APIs, types, and functions: `decompress_fn` standardizes arguments for all supported decompressors. `decompress_method(const unsigned char *inbuf, long len, const char **name)` inspects input bytes and returns the matching decompressor and optional method name.

Control flow: Callers probe compressed data with `decompress_method()`, then invoke the returned function using either preloaded input (`len != 0`, `fill == NULL`) or streaming input (`len == 0`, optional allocated input buffer and repeated `fill` calls). Output is buffered directly when `flush == NULL` or emitted via `flush` when streaming output is needed.

State and persistence: This header owns no state. Position reporting through `posp` is caller-visible transient state.

Dependencies and integration points: Integrates all format-specific headers under a shared boot/initramfs decompression interface. Implementations rely on early boot or kernel allocation helpers from `decompress/mm.h`.

Risks and test signals: Risks include wrong magic detection with short buffers, violating the `len`/`fill` contract, and buffer sizing mistakes for streaming modes. Test every supported compression magic, empty/truncated buffers, preloaded versus callback input, flush output mode, and `posp` accounting.

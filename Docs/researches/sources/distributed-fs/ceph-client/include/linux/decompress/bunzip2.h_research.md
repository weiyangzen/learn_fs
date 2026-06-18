# sources/distributed-fs/ceph-client/include/linux/decompress/bunzip2.h

Purpose: Declares the bzip2 decompressor entry point used by kernel image, initramfs, or ramdisk decompression code.

Important APIs, types, and functions: Exports `bunzip2()` with common decompressor arguments: optional input buffer and length, streaming `fill` callback, streaming `flush` callback, output buffer, consumed-position pointer, and error callback.

Control flow: The caller either passes preloaded compressed input with nonzero `len` or supplies a `fill` callback for streaming input. Output is either written to a caller buffer or emitted through `flush`, following the generic decompressor contract.

State and persistence: No state is declared in the header. Decoder state and temporary buffers live inside the decompressor implementation and caller-provided storage.

Dependencies and integration points: Shares the signature defined by `decompress/generic.h`, allowing format selection code to call bzip2 uniformly with gzip, LZ4, LZMA, LZO, XZ, and ZSTD.

Risks and test signals: Risks include mismatched fill/flush semantics, invalid output sizing, and poor error propagation in early boot where allocators differ. Test preloaded and streaming bzip2 initramfs inputs, corrupt streams, position reporting, and early-boot decompression builds.

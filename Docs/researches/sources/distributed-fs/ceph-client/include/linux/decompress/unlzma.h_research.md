# sources/distributed-fs/ceph-client/include/linux/decompress/unlzma.h

Purpose: Declares the LZMA decompressor entry point for kernel decompression paths.

Important APIs, types, and functions: Exports `unlzma()` with the shared decompressor arguments, including input callbacks, output buffer/flush callback, consumed-position pointer, and error callback.

Control flow: The LZMA decoder is selected by magic or caller choice, then consumes preloaded or streamed input and emits output through the common ABI. The header allows generic decompression code to call it uniformly.

State and persistence: No header-owned state. LZMA dictionaries and temporary memory are allocated by the implementation via decompressor memory wrappers.

Dependencies and integration points: Works with `decompress/generic.h` and `decompress/mm.h` in boot and runtime initramfs contexts.

Risks and test signals: Risks include high memory use in early boot, malformed dictionary properties, truncated input, and incorrect `posp` reporting. Test valid and corrupt LZMA streams, minimal-memory boot configurations, callback input, direct output buffer mode, and error callback invocation.

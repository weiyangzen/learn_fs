# sources/distributed-fs/ceph-client/include/linux/decompress/unzstd.h

Purpose: Declares the Zstandard decompressor entry point for kernel decompression users.

Important APIs, types, and functions: Exports `unzstd()` with common arguments for input buffer/length, `fill`, `flush`, output buffer, input-position pointer, and error callback.

Control flow: Generic decompression code selects ZSTD by magic and invokes this entry point. The implementation handles either preloaded or streaming input and direct or flushed output.

State and persistence: No state is declared in the header. ZSTD frame/window state is temporary in the implementation.

Dependencies and integration points: Integrates with `decompress/generic.h`, boot/initramfs loading code, and decompressor memory allocation wrappers.

Risks and test signals: Risks include large window requirements, malformed frame handling, short callback reads, and output-size mismatches. Test ZSTD kernel/initramfs images, invalid frames, streaming modes, low-memory boot decompression, and position reporting.

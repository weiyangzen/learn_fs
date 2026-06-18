# sources/distributed-fs/ceph-client/include/linux/decompress/unlz4.h

Purpose: Declares the LZ4 decompressor entry point under the generic kernel decompression ABI.

Important APIs, types, and functions: Exports `unlz4()` with input buffer/length, `fill`, `flush`, output buffer, input position pointer, and error callback.

Control flow: Callers invoke `unlz4()` after magic detection or explicit LZ4 selection; the implementation streams input/output according to the shared decompressor contract.

State and persistence: The header declares no state. Temporary decoder state is implementation-local.

Dependencies and integration points: Integrates with kernel image and initramfs decompression, `decompress_method()`, and `decompress/mm.h` allocation wrappers.

Risks and test signals: Risks include malformed block handling, output-size assumptions, and early-boot callback behavior. Test LZ4-compressed kernel/initramfs data, corrupt streams, streaming input, flush output, and position accounting.

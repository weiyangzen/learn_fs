# sources/distributed-fs/ceph-client/include/linux/decompress/unlzo.h

Purpose: Declares the LZO decompressor entry point for kernel image, initramfs, and ramdisk loading paths.

Important APIs, types, and functions: Exports `unlzo()` with the generic decompressor ABI.

Control flow: The caller provides preloaded or callback-supplied compressed input and receives decompressed output via buffer or flush callback. Errors are reported through the supplied error function.

State and persistence: No state is held by the header; decompressor-local state is temporary.

Dependencies and integration points: Integrates with generic decompressor selection and the allocation behavior defined in `decompress/mm.h`.

Risks and test signals: Risks include malformed LZO block sizes, buffer overrun on direct output, short read handling, and early boot allocation constraints. Test valid LZO initramfs images, corrupt block headers, streaming reads, flush writes, and position tracking.

# sources/distributed-fs/ceph-client/include/linux/decompress/inflate.h

Purpose: Declares the gzip/inflate decompressor entry point for kernel decompression users.

Important APIs, types, and functions: Exports `gunzip()` with the common decompressor signature: input buffer/length, `fill`, `flush`, output buffer, consumed-position pointer, and error callback.

Control flow: The gzip implementation consumes either preloaded input or callback-provided input and writes decompressed bytes to the caller buffer or flush callback. Errors are reported through the supplied `error_fn`.

State and persistence: No state is held in the header. Inflate state is temporary inside the implementation.

Dependencies and integration points: Participates in the generic decompression method table and early boot/initramfs loading paths.

Risks and test signals: Risks include truncated gzip streams, CRC/header handling mismatches, callback contract violations, and early allocator differences. Test compressed kernel/initramfs gzip images, corrupt headers, short reads, flush-only output, and consumed-position reporting.

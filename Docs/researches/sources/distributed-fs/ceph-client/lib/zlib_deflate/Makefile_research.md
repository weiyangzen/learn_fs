# sources/distributed-fs/ceph-client/lib/zlib_deflate/Makefile

## Purpose
Builds the kernel's modified zlib deflate compressor, whose implementation performs memory allocation ahead of time. It is the compression counterpart to `lib/zlib_inflate`.

## Build flow
`obj-$(CONFIG_ZLIB_DEFLATE) += zlib_deflate.o` enables the composite object. `zlib_deflate-objs := deflate.o deftree.o deflate_syms.o` links the compressor implementation, tree logic, and exported symbols.

## State, dependencies, and integration
No runtime state is present in this Makefile. It integrates with `CONFIG_ZLIB_DEFLATE` and kernel consumers of exported deflate APIs.

## Risks and test signals
Object-list drift can cause link or modpost failures. Compression users still need separate inflate support for round trips. Test by building `CONFIG_ZLIB_DEFLATE` as built-in, module, and disabled, then running compression/decompression round-trip coverage.

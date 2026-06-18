# sources/distributed-fs/ceph-client/include/linux/decompress/unxz.h

Purpose: Declares the XZ decompressor wrapper for kernel, initramfs, and initrd decompression.

Important APIs, types, and functions: Exports `unxz(unsigned char *in, long in_size, fill, flush, unsigned char *out, long *in_used, error)` using the same streaming shape as the generic decompressor ABI.

Control flow: XZ input may be preloaded or supplied through `fill`; output is written to `out` or emitted through `flush`. `in_used` reports consumed bytes for callers that need trailer or concatenated data handling.

State and persistence: The header owns no state. Decoder dictionaries and stream state live inside the implementation and allocation wrappers.

Dependencies and integration points: Used by generic decompressor selection and boot/initramfs loaders. The SPDX license differs (`0BSD`) because this wrapper follows upstream XZ decompressor licensing.

Risks and test signals: Risks include dictionary memory pressure, unsupported XZ options in early boot, truncated streams, and error propagation. Test XZ-compressed kernel/initramfs images, corrupt headers, large dictionary rejection, streaming input, and `in_used` accuracy.

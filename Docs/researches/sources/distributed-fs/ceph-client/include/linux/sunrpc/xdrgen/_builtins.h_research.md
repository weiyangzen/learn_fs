# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_builtins.h

Purpose: provides inline encode/decode primitives used by generated in-kernel XDR code for RFC 4506 scalar, string, and opaque types.

Important APIs and types: helpers cover void, bool, signed/unsigned short, int, unsigned int, long, unsigned long, hyper, unsigned hyper, variable-length `string`, and variable-length `opaque`. They use `struct xdr_stream`, `xdr_inline_decode()`, `xdr_reserve_space()`, `xdr_stream_decode_u32()`, `xdr_encode_opaque()`, and alignment helpers.

Control flow: generated decoders inline-decode the needed XDR units and return `false` on missing data or max-length violation. Encoders reserve the aligned size and write big-endian wire values, returning `false` on overflow. Strings/opaque values expose pointers into the XDR stream rather than duplicating data.

State and persistence: no persistent state. Decoded string/opaque pointers are valid only as long as the backing XDR buffer remains valid.

Dependencies and integration points: depends on `xdr.h` and `_defs.h` type names. Used by generated protocol headers/implementations such as NFSv4.1 and NLMv4.

Risks and test signals: risks include pointer lifetime misuse, ignored `maxlen` in encode call sites, sign-extension assumptions for non-standard short types, and missing padding validation. Test generated XDR round trips, truncated inputs, max-length failures, and signed short vectors.

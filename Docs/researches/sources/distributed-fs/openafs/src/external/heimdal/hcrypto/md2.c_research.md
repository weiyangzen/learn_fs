# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.c

Purpose: implements the legacy MD2 message digest primitive.

Important APIs/types/functions: `MD2_Init` zeroes context state; private `calc` processes one 16-byte block using the MD2 substitution table, checksum, and 48-byte working state; `MD2_Update` buffers unaligned input and processes full blocks; `MD2_Final` applies MD2 padding, appends the checksum block, emits 16 bytes, and clears the context.

Control flow: updates accumulate `len`, process pending plus incoming bytes whenever 16-byte blocks are available, and keep any tail in `data`. Finalization computes padding length from total length, feeds padding and checksum through the same update path, then copies `state`.

State and persistence: `struct md2` persists total byte length, a 16-byte partial block, a 16-byte checksum, and a 16-byte state. Finalization zeroes the full context.

Dependencies and integration points: includes `hash.h` and `md2.h`; the digest is exposed through provider EVP descriptors and deprecated EVP MD2 APIs.

Risks and test signals: MD2 is cryptographically obsolete and should be compatibility-only. Test with RFC 1319 known-answer vectors, segmented update inputs, exact block boundaries, and finalization context clearing.

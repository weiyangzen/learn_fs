# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-comp.c

Purpose: implements the STAPL/Jam bytecode decompressor used by `altera.c` to expand compressed Boolean-array sections from firmware into executable variable buffers.

Important APIs and functions: `altera_shrink(u8 *in, u32 in_length, u8 *out, u32 out_length, s32 version)` is the exported decompression entry point. `altera_bits_req` computes the number of packed bits needed for offsets, and `altera_read_packed` consumes variable-width bitfields from the compressed stream.

Control flow: `altera_shrink` clears the output buffer, reads the uncompressed byte length from the compressed input, validates it against `out_length`, and then decodes a stream of literal blobs or back-references. A zero tag copies up to three literal bytes; a one tag reads an offset plus byte length and copies from already decompressed output. Version greater than zero reduces the match window by one.

State and persistence: all state is local to the decompression call. Output persists only in the caller-owned buffer, usually a dynamically allocated interpreter variable in `altera_execute`.

Dependencies and integration points: depends on kernel integer types and `altera-exprt.h`. It is called from `altera.c` while initializing compressed Boolean arrays in firmware data sections.

Risks: `in_length` is not used to bound packed reads, so corrupt firmware can drive reads past the compressed input if earlier validation is insufficient. Back-references assume nonzero valid offsets and can underflow `out[i - offset]` if the stream is malicious. Error signaling is limited to returning zero length.

Test signals: known-good compressed JBC fixtures, fuzzed malformed streams, boundary cases for zero-length output, out_length too small, maximum match-window offsets, and KASAN/UBSAN runs around packed reads.

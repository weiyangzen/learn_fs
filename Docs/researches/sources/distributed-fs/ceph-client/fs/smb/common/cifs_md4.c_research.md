# sources/distributed-fs/ceph-client/fs/smb/common/cifs_md4.c

Read coverage: full file.

## Purpose
`cifs_md4.c` implements the MD4 message digest algorithm for CIFS/SMB compatibility, notably NTLM/NT hash style authentication flows that historically require MD4 over UTF-16 password material.

## Important APIs, types, and functions
The exported API is `cifs_md4_init(struct md4_ctx *mctx)`, `cifs_md4_update(struct md4_ctx *mctx, const u8 *data, unsigned int len)`, and `cifs_md4_final(struct md4_ctx *mctx, u8 *out)`. Internal helpers include `lshift`, `F`, `G`, `H`, `ROUND1`, `ROUND2`, `ROUND3`, `md4_transform`, and `md4_transform_helper`.

## Control flow
Initialization zeros the context and seeds the four MD4 state words. Updates append input into a 64-byte block buffer, transform full blocks after converting little-endian words to CPU order, and keep trailing bytes buffered. Finalization appends the `0x80` bit, zero padding, and 64-bit bit count split into words 14 and 15, transforms the final block, converts the hash to little endian, copies 16 digest bytes to the output, and clears the context.

## State and persistence behavior
The mutable state is `struct md4_ctx`: four hash words, a sixteen-word block buffer, and `byte_count`. No global runtime state is changed. The final digest is persisted only through the caller-provided output buffer; the context is scrubbed after finalization.

## Dependencies and integration points
The file depends on kernel module infrastructure, endian helpers, string functions, and `md4.h`. It exports GPL symbols for use by SMB authentication code. Its implementation is intentionally self-contained rather than using a generic crypto API allocation path.

## Risks and test signals
MD4 is cryptographically broken and should only be used for protocol compatibility, never new security design. Padding and byte-count overflow behavior should be tested with RFC1320 vectors, empty input, inputs around 55/56/63/64/65 bytes, and multi-update inputs matching single-update digests. Endianness tests matter on big-endian architectures because block words are converted before transforms and digest words before output.

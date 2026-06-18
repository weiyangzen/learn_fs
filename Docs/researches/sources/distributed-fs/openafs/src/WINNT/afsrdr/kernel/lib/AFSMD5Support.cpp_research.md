# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSMD5Support.cpp

## Purpose

`AFSMD5Support.cpp` embeds an independent MD5 implementation derived from L. Peter Deutsch's Aladdin Enterprises source and exposes `AFSGenerateMD5` as the OpenAFS wrapper for hashing a buffer into a 16-byte digest.

## Important APIs, types, and functions

`md5_state_t` stores bit count, digest state words, and a 64-byte partial block. `md5_init` initializes the standard MD5 state. `md5_append` updates message length, processes full 64-byte blocks, and stores trailing bytes. `md5_finish` pads the message, appends the bit length, and emits the digest. `md5_process` performs the four MD5 compression rounds. `AFSGenerateMD5(char *, ULONG, UCHAR *)` initializes, appends, and finishes one complete buffer.

## Control flow

The wrapper allocates `md5_state_t` on the stack, initializes it, appends the caller buffer for the supplied length, and writes the final digest to the caller-provided output. `md5_append` fills any existing partial block, processes full blocks with `md5_process`, and stores a final partial block. `md5_finish` snapshots the original bit length, appends `0x80` plus zero padding to 56 bytes modulo 64, appends the saved length, and serializes the four words as little-endian digest bytes. `md5_process` aliases aligned input as words or copies unaligned input with `RtlCopyMemory`, then applies the standard F/G/H/I rounds and constants.

## State and persistence behavior

All hash state is local to the call chain. The file has no global mutable state and no durable persistence. Output is deterministic for the input buffer and length.

## Dependencies and integration points

The implementation includes `AFSCommon.h` for kernel types/macros and uses `RtlCopyMemory`. It likely supports identity, cache, checksum, or protocol code elsewhere in the redirector, but this file itself is self-contained.

## Risks and test signals

MD5 is not collision-resistant and must not be used as an authenticity or security boundary. `md5_append` takes `int nbytes`, while `AFSGenerateMD5` receives `ULONG Length`; values above `INT_MAX` can convert incorrectly. Null buffers are not validated. The direct word path assumes little-endian aligned interpretation. Tests should run RFC 1321 vectors, aligned and unaligned buffers, zero-length input, boundary lengths around 55/56/63/64/65 bytes, and large inputs below the signed-int limit. Security review should inspect every caller for misuse of MD5 as a trust primitive.

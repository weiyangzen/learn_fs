# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.c

Purpose: implements the legacy MD5 digest primitive for compatibility.

Important APIs/types/functions: `MD5_Init`, private `calc` with four MD5 rounds, endian swap helper for big-endian builds, `MD5_Update`, and `MD5_Final`. Round macros implement F/G/H/I functions and constants.

Control flow: update tracks total bit length in `sz`, accumulates data in `save`, transforms 64-byte blocks, and performs endian conversion as needed. Final adds `0x80` padding, zero fill, little-endian bit length, updates the state, and serializes four little-endian 32-bit words.

State and persistence: context stores split bit count, four digest words, and a partial block. Finalization does not zero the context, so callers should treat it as containing prior message state after use.

Dependencies and integration points: depends on `hash.h` and `md5.h`; exposed via deprecated EVP MD5 descriptors and useful for older Kerberos/OpenSSL-compatible formats.

Risks and test signals: MD5 is collision-broken and should not be used for new security decisions. Alignment-sensitive casts and overflow accounting need coverage. Test with RFC 1321 vectors, streaming splits, large inputs crossing `sz[0]`, and endian variants.

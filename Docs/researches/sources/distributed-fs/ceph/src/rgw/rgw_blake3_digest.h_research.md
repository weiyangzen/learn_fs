# sources/distributed-fs/ceph/src/rgw/rgw_blake3_digest.h

Purpose: provides a small RGW digest wrapper around the C BLAKE3 implementation so checksum code can treat BLAKE3 like other digest algorithms.

Important APIs/types/functions: `rgw::digest::Blake3` exposes `digest_size`, `Restart()`, `Update(const unsigned char*, uint64_t)`, and `Final(unsigned char*)`.

Control flow: constructor calls `Restart()`, `Update()` forwards data to `blake3_hasher_update()`, and `Final()` writes `BLAKE3_OUT_LEN` bytes through `blake3_hasher_finalize()`.

State/persistence: holds only the mutable `blake3_hasher` context. The digest bytes are consumed by higher-level `rgw::cksum::Cksum` persistence.

Dependencies/integration: depends on `BLAKE3/c/blake3.h` and is wrapped by `rgw_cksum_digest.h` as `TDigest<rgw::digest::Blake3>`.

Risks: the API does not guard null output buffers or concurrent use. Digest size must stay synchronized with the descriptor table in `rgw_cksum.h`.

Test signals: BLAKE3 known-answer tests, restart reuse, multi-update equivalence with single update, and integration through `finalize_digest(Type::blake3)`.

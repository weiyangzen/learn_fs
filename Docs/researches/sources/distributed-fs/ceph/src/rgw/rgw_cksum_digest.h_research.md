# sources/distributed-fs/ceph/src/rgw/rgw_cksum_digest.h

Purpose: adapts multiple concrete digest implementations behind a small polymorphic interface for RGW checksum calculation.

Important APIs/types/functions: abstract `Digest`; templated `TDigest<T>`; type aliases `Blake3`, `Crc32`, `Crc32c`, `XXH3`, `SHA1`, `SHA256`, `SHA512`, `Crc64Nvme`; `DigestVariant`; visitor `get_digest_ptr`; `get_digest()`, `digest_factory()`, and `finalize_digest()`.

Control flow: `TDigest` forwards restart/update/final calls and iterates over bufferlist buffers for buffer updates. `digest_factory()` switches on checksum type to construct the right variant. `finalize_digest()` creates a `Cksum` of the requested type and calls `Final()` when a digest implementation exists.

State/persistence: digest state is in-memory; output becomes a `Cksum` persisted elsewhere.

Dependencies/integration: Ceph SHA crypto classes, RGW Blake3/CRC/XXH wrappers, `rgw_cksum.h`, and bufferlist. Used by checksum pipe and multipart combiner.

Risks: `Type::none` produces `std::monostate` and `get_digest()` returns null; callers must not call `Update()` on null digest. `TDigest::Update(const bufferlist&)` lacks `override` annotation. Adding algorithms requires updating both enum descriptor and variant/factory.

Test signals: factory coverage for each `Type`, null behavior for none, known-answer digest tests, bufferlist vs contiguous update equivalence, and algorithm additions failing compile/tests unless all tables are updated.

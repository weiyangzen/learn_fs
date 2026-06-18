# sources/cloud-native/nydus/utils/src/digest.rs

Purpose: digest primitives for RAFS/Nydus content hashing with Blake3 and SHA256.

Important APIs/types/functions: `RAFS_DIGEST_LENGTH = 32`, `DigestData = [u8; 32]`, `Algorithm::{Blake3,Sha256}` with display, parsing, and numeric conversions. `DigestHasher` trait abstracts update/finalize. `RafsDigestHasher` wraps boxed `blake3::Hasher` or `Sha256`. `RafsDigest` is a 32-byte `repr(C)` digest with `from_buf`, `from_reader`, `from_string`, `hasher`, `Display`, `AsRef<[u8]>`, and conversions from digest data and into `String`.

Control flow: buffer and reader hashing select the requested algorithm and stream bytes until EOF. `from_string` parses a hex string in two-byte chunks into digest bytes. Display formats each byte as two lowercase hex digits. `From<&DigestData> for &RafsDigest` performs an unsafe reference cast for zero-copy digest interpretation.

State and persistence: digest values are plain 32-byte records commonly persisted in metadata. Incremental hashers hold transient state.

Dependencies and integration points: depends on `blake3`, `sha2`, and project error macros. Used by storage chunk metadata, hash verification, and image formats.

Risks: `from_string` unwraps UTF-8 and hex parsing and does not validate length; malformed or short/long strings can panic or partially fill data. The unsafe reference conversion relies on `repr(C)` single-field layout alignment compatibility. Display uses enum debug names (`Blake3`, `Sha256`) while parsing expects lowercase (`blake3`, `sha256`), so string forms are not symmetrical for algorithms.

Test signals: tests cover known Blake3/SHA256 vectors, incremental hashing, algorithm parsing/conversions/display, reader hashing, hex string conversion, `AsRef`, and data conversion.

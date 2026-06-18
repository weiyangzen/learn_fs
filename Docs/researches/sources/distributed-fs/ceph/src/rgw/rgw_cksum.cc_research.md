# sources/distributed-fs/ceph/src/rgw/rgw_cksum.cc

Purpose: implements checksum combination for multipart objects, including AWS-compatible CRC full-object synthesis and digest-style composite checksums.

Important APIs/types/functions: `combine_crc_cksum()`, private `DigestCombiner`, private `CRCCombiner`, and `CombinerFactory()`.

Control flow: `combine_crc_cksum()` rejects mismatched or non-CRC types, byteswaps stored CRC values into algorithm order, calls type-specific madler combiner functions for CRC64NVME/CRC32/CRC32C, byteswaps back to at-rest order, and returns a raw `Cksum`. `DigestCombiner` hashes concatenated part checksum bytes and marks `COMPOSITE_MASK`. `CRCCombiner` stores the first part checksum and combines each following part by length, marking `FULL_OBJECT_MASK`.

State/persistence: no direct storage writes; produced `Cksum` objects are persisted by object metadata/parts elsewhere. Flags distinguish legacy/composite/full-object multipart semantics.

Dependencies/integration: `rgw_cksum.h`, `rgw_cksum_digest.h`, CRC digest byte swapping, madler CRC combine routines, SPDK CRC64 include, and checksum callers in REST multipart completion.

Risks: parameter name says `len1` while header says `len2`; correctness depends on passing the second segment length expected by combine functions. `CRCCombiner::append()` dereferences optional combine result without guard. CRC byte order is subtle and AWS-visible.

Test signals: known multipart CRC32/CRC32C/CRC64NVME combinations, digest composite checksums with part count behavior at response layer, mismatched type rejection, one-part CRC combine, and byte-order regression vectors.

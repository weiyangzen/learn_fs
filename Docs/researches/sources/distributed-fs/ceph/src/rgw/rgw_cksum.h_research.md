# sources/distributed-fs/ceph/src/rgw/rgw_cksum.h

Purpose: defines RGW checksum algorithms, descriptors, serialized checksum value type, AWS/RGW header naming, checksum parsing, type compatibility rules, and combiner interface.

Important APIs/types/functions: enum `Type`; flags `FLAG_AWS_CKSUM`, `FLAG_CRC`; `Desc`; class `Cksum`; `no_cksum`; `to_string()`, `to_uc_string()`, `parse_cksum_type()`, `cksum_flags_of()`, `parse_cksum_type_hdr()`, `is_checksum_hdr()`, `permitted_cksum_algo_and_type()`, `combine_crc_cksum()`, abstract `Combiner`, `CombinerFactory()`, `get_checksum_type()`, and `get_part_checksum_type()`.

Control flow: `Cksum` constructors accept raw or armored input. Encoding stores type id, digest size, raw digest bytes, and flags. Header/element names are derived from algorithm descriptors. Compatibility allows composite for all but CRC64NVME and full-object only for CRC family. `get_checksum_type()` treats legacy v1 multipart checksums as composite.

State/persistence: `Cksum` is persisted in object/multipart metadata. Flags are a format and semantics contract; v2 marks newer stored checksums and full-object/composite masks identify combined checksum mode.

Dependencies/integration: Boost string helpers, `fmt`, Ceph armor, hex/base64 helpers, buffer encoding. Used by REST S3, put-object pipeline, multipart completion, and response checksum headers.

Risks: decode trusts stored type/digest size enough to copy into fixed array; malformed values can overrun if not protected by encoded data discipline. `to_base64()` encodes the hex string rather than raw digest, which is a display helper rather than AWS armor. Composite/full-object flag semantics are intentionally nuanced for 2023 and 2025 compatibility.

Test signals: descriptor table indexes match enum values, armor/raw constructors, header parsing case-insensitivity, v1/v2 decode semantics, compatibility matrix, checksum type response values, and malformed decode handling.

# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_mfa2_format.h

## Purpose
`mlxfw_mfa2_format.h` defines the on-file MFA2 TLV type IDs and packed payload layouts used by the parser.

## Important APIs, Types, and Functions
It declares TLV type enum values for multi-part, package descriptor, component descriptor, component pointer, and PSID. It also declares compression type values and packed payload structures: `mlxfw_mfa2_tlv_package_descriptor`, `mlxfw_mfa2_tlv_multi`, `mlxfw_mfa2_tlv_psid`, `mlxfw_mfa2_tlv_component_ptr`, and `mlxfw_mfa2_tlv_component_descriptor`. Macro invocations generate typed TLV payload accessors.

## Control Flow and State
There is no runtime flow. The structures define how parser code reads counts, offsets, compressed block sizes, PSID bytes, component indexes, component identifiers, offsets, and payload sizes from big-endian firmware bytes.

## Dependencies and Integration Points
It depends on `mlxfw_mfa2_file.h` and `mlxfw_mfa2_tlv.h`. It is used by both parser validation and component extraction.

## Risks and Test Signals
Risks include packed layout drift from the MFA2 specification, wrong endianness interpretation by callers, and type IDs not matching generated images. Test signals are parsing real MFA2 files, checking component counts and offsets against vendor tooling, and compile-time layout review for packed structures.

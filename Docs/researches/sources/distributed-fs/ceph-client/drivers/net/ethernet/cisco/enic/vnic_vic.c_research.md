# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.c

## Purpose
`vnic_vic.c` builds Cisco VIC provisioning information blobs containing network-order TLVs for firmware provisioning commands.

## Important APIs, types, and functions
- `vic_provinfo_alloc()` allocates a zeroed maximum-size provisioning buffer, copies OUI/type, and initializes length to include `num_tlvs`.
- `vic_provinfo_add_tlv()` appends a TLV with network-order type/length, copies its value, increments TLV count, and updates total length.
- `vic_provinfo_size()` returns the actual serialized provisioning buffer size.
- `vic_provinfo_free()` frees the buffer.

## Control flow and state
Provisioning state grows monotonically as TLVs are appended. Length and TLV count are stored in network byte order in the buffer, so callers and firmware share a serialized representation. Bounds checks prevent writes past `VIC_PROVINFO_MAX_TLV_DATA`.

## Dependencies and integration points
It depends on `vnic_vic.h`, slab allocation, endian helpers, and `unsafe_memcpy()` for flexible-array TLV payloads. The resulting buffer can be supplied to vNIC provisioning devcmds such as `CMD_INIT_PROV_INFO2`.

## Risks and test signals
Risks include length accounting errors, misuse of flexible array storage, NULL value handling, and endian mistakes. Test with multiple TLVs, maximum-size rejection, NULL inputs, and firmware acceptance of serialized provisioning data.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_vic.h

## Purpose
`vnic_vic.h` defines Cisco VIC generic provisioning TLV constants, serialized provisioning structures, maximum sizes, and helper prototypes.

## Important APIs, types, and functions
- `VIC_PROVINFO_CISCO_OUI` and `VIC_PROVINFO_GENERIC_TYPE` identify Cisco generic provisioning data.
- `enum vic_generic_prov_tlv_type` enumerates port profile, client, cluster, host, incarnation, OS, and client-type TLVs.
- `enum vic_generic_prov_os_type` defines OS IDs.
- `struct vic_provinfo` and nested `vic_provinfo_tlv` define the packed network-order wire format.
- `VIC_PROVINFO_ADD_TLV` is a convenience macro that jumps to `add_tlv_failure` on append error.

## Control flow and state
The packed provisioning object is mutable until sent to firmware. Its length and TLV count are network-order fields; callers must use helper functions to maintain them.

## Dependencies and integration points
It is consumed by `vnic_vic.c` and any ENIC provisioning path that sends VIC metadata to firmware.

## Risks and test signals
Risks include macro-imposed label naming, packed layout compatibility, and maximum size constraints. Compile coverage plus provisioning command tests with representative TLV sets are the useful signals.

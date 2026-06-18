# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_pce.h

Purpose: vendor-derived PCE parser/classification microcode table for Lantiq GSWIP devices.

Important APIs/types/functions: parser output enums, length/type constants, flag enums, `MC_ENTRY()` packing macro, and static `gswip_pce_microcode[]` entries using `struct gswip_pce_microcode`.

Control flow: no functions. `gswip_pce_load_microcode()` writes this array into PCE table registers during DSA setup and marks microcode valid.

State and persistence: read-only kernel data; once loaded, equivalent parser state persists in hardware until reset.

Dependencies and integration: includes `lantiq_gswip.h`; referenced by SoC `gswip_hw_info` descriptors.

Risks and test signals: opaque constants risk parser regressions for VLAN, SNAP, PPPoE, IPv4, IPv6, and IGMP. Test tagged/untagged VLAN traffic, IPv4/IPv6, PPPoE, IGMP trap, and bridge forwarding after microcode load.

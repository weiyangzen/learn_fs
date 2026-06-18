# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx_pce.h

Purpose: MaxLinear GSW1xx PCE parser/classification microcode for the common GSWIP setup path, including service-VLAN handling and an IPv6 issue fix noted by comments.

Important APIs/types/functions: parser output enums including `OUT_STAG0/OUT_STAG1`, parser type constants, flag enums including `FLAG_SVLAN`, `PCE_MC_M()` packing macro, and static `gsw1xx_pce_microcode[]`.

Control flow: no functions. GSW1xx descriptors point to the array, and `gswip_pce_load_microcode()` writes it during switch setup.

State and persistence: read-only kernel data mirrored into hardware PCE state until reset.

Dependencies and integration: includes `lantiq_gswip.h`; integrated by all GSW1xx `gswip_hw_info` descriptors.

Risks and test signals: opaque microcode constants can regress S-tag/C-tag, IPv6 extension, PPPoE, SNAP, and IGMP parsing. Test stacked VLANs, IPv6 forwarding, IGMP trapping, VLAN-aware bridging, and vendor-behavior parity.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpkg.h

Purpose: Defines the DPAA2 Data Path Key Generator profile language used to build classification, hashing, QoS, and flow-steering keys. It is a declarative header: callers describe protocol fields or byte ranges to extract, and DPNI command code serializes those profiles into MC/DMA command buffers.

Important APIs, types, and functions: Core limits are `DPKG_NUM_OF_MASKS` and `DPKG_MAX_NUM_OF_EXTRACTS`. Extraction selectors include `enum dpkg_extract_from_hdr_type`, `enum dpkg_extract_type`, `struct dpkg_mask`, `struct dpkg_extract`, and `struct dpkg_profile_cfg`. `enum net_prot` lists parser protocols such as Ethernet, VLAN, IPv4/IPv6, IP, TCP, UDP, SCTP, PPPoE, MPLS, IPsec, GRE, ARP, GTP, and user-defined layers. The many `NH_FLD_*` masks describe selectable fields within those protocols.

Control flow: There is no executable flow in this file. A driver constructs `struct dpkg_profile_cfg`, fills up to ten extracts with header/data/parser selections and optional byte masks, then passes it to `dpni_prepare_key_cfg()` in `dpni.c`, which serializes the profile into the 256-byte command extension consumed by DPNI distribution/QoS commands.

State and persistence behavior: The structs are transient configuration containers. The effective key profile persists only inside MC hardware/firmware after the relevant DPNI command succeeds; this header itself stores no state.

Dependencies and integration points: Includes `<linux/types.h>` and uses Linux `BIT()` masks through the including environment. It is included by `dpni.h`, consumed by `dpni_prepare_key_cfg()`, and indirectly used by DPAA2 Ethernet RSS/hash/flow-steering and switch tc offload code that needs hardware parser keys.

Risks: Field masks and `enum net_prot` values are an ABI with MC firmware/parser expectations; changing numeric values or mask meanings would break hardware classification. Callers must respect the maximum extract and mask counts, valid `hdr_index` semantics, and protocol-field combinations. Several protocol masks are very broad, increasing the chance of invalid combinations that only firmware can reject. Typographical issues in comments/names, such as `BEGGINING`, should not be renamed if firmware-facing values depend on them.

Test signals: Build key profiles for common RSS and flow-steering keys: Ethernet DA/SA, VLAN TCI, IPv4/IPv6 5-tuple, TCP/UDP ports, payload bytes, parser-result extracts, masked extracts, outer/last VLAN/MPLS/IP header indexes, maximum ten extracts, invalid extract type rejection in `dpni_prepare_key_cfg()`, and firmware rejection paths for unsupported protocol/field combinations.

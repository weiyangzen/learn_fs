# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.h

## Purpose
`mad.h` defines HFI1's local OPA MAD data structures, attribute IDs, trap payloads, congestion-control layouts, buffer-control layouts, counter conversion helpers, and function prototypes used by `mad.c` and other HFI1 code. It bridges OPA management definitions not fully represented by generic RDMA headers.

## Important APIs, types, and functions
- OPA trap constants identify GID, multicast, port-state, link-integrity, capability, system GUID, M_Key, P_Key, Q_Key, switch bad P_Key, and link-width downgrade notices.
- `struct opa_mad_notice_attr` models the notice payload union for multiple trap types.
- `struct ib_pma_portcounters_cong` provides an IB PMA congestion counter layout.
- Congestion data types include HFI congestion log events, congestion setting attributes and shadows, CCT table attributes and shadows, `struct cc_table_shadow`, and RCU-protected `struct cc_state`.
- Buffer and table types include `struct vl_limit`, `struct buffer_control`, and `struct sc2vlnt`.
- Attribute-modifier macros decode OPA nport, block count, start block, async update, SM config start, cable-info address, and cable-info length fields.
- Inline helpers `get_link_speed()` and `convert_xmit_counter()` support PMA transmit-wait conversion.
- Prototypes export P_Key change, trap timer, link-width conversion, and transmit-wait counter sampling.

## Control flow
The header has no standalone control flow. Its macros are used by `mad.c` dispatchers to validate and decode `attr_mod`, choose response sizes, convert counter units, and build or parse OPA management payloads. The inline conversion helpers are called by PMA counter reporting paths.

## State and persistence
Most types in this header describe wire-visible management payloads or runtime shadows. `struct cc_state` is explicitly designed as an active, RCU-protected per-port congestion state snapshot, while shadow structures let the driver keep host-endian copies of wire-endian management data. No state is allocated by this header itself.

## Dependencies and integration points
The header includes RDMA PMA, OPA SMI, OPA PortInfo, and local `opa_compat.h`. Its definitions must remain ABI-compatible with OPA management packet layouts because `mad.c` casts MAD payload bytes directly to these packed structures.

## Risks
- Packed structure layout and endian annotations are protocol-critical; field reordering or padding changes would break MAD interoperability.
- Attribute-modifier masks must match OPA bit assignments. Mistakes can make handlers accept invalid requests or reject valid fabric-manager traffic.
- `OPA_AM_CI_ADDR_SMASK` and `OPA_AM_CI_LEN_SMASK` are intended to describe cable-info fields; mask macro correctness should be checked carefully against the OPA definitions because downstream bounds checks rely on decoded address/length.
- Counter conversion uses integer scaling and assumes valid nonzero link width values passed by callers.

## Test signals
- Compile with `BUILD_BUG_ON()` or static assertions around packed structure sizes if adding fields.
- Exercise MAD get/set handlers that use every attribute-modifier macro.
- Validate transmit-wait conversion for 25G and 12.5G speeds, default and downgraded link widths, and zero or unsupported link-width masks.

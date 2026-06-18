# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/rx.c

## Purpose
`libie/rx.c` provides Intel Ethernet packet-type lookup data, mapping i40e/ice/iavf-style hardware packet type IDs into `struct libeth_rx_pt` fields and XDP RSS hash type bits.

## Important APIs, Types, and Functions
The key export is `libie_rx_pt_lut[LIBIE_RX_PT_NUM]`. Macro families such as `LIBIE_RX_PT`, `LIBIE_RX_PT_IP`, `LIBIE_RX_PT_IP_TUN`, and `LIBIE_RX_PT_IP_GRE` generate table entries for L2, timesync, IPv4/IPv6, fragmented, tunneled, GRE/NAT, and inner protocol cases.

## Control Flow
There is no runtime control flow beyond table lookup by consumers. The preprocessor expands packet-type patterns into a static table ordered according to hardware packet type numbering.

## State and Persistence Behavior
Static const lookup table only. Consumers treat it as immutable runtime metadata.

## Dependencies and Integration Points
Depends on `linux/net/intel/libie/rx.h` and `libeth_rx_pt` definitions. Imports `LIBETH` namespace. Used by Intel Ethernet drivers to convert hardware ptype numbers into parsed metadata in O(1), including XDP hash reporting.

## Risks and Edge Cases
- Table order must exactly match hardware ptype numbering; macro expansion mistakes cause wrong checksum/hash/protocol behavior.
- `LIBIE_RX_PT_UNUSED` entries intentionally represent unsupported or reserved ptypes.
- Supplemental XDP RSS macros fill gaps where token concatenation would not match XDP constants.

## Test Signals
Compile-time table size checks, known ptype-to-metadata fixtures for L2/IPv4/IPv6/tunnel/GRE/fragment/TCP/UDP/SCTP/ICMP/timesync, and consumer receive tests verifying RSS hash type classification.

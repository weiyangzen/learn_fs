# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/cmsg.h

## Purpose
This header defines the NFP Flower firmware control-message ABI and flow key/action wire structures. It is shared by action compilation, match compilation, representor management, tunnel handling, LAG, stats, and control-message dispatch.

## Important APIs, types, and functions
- Layer bit definitions (`NFP_FLOWER_LAYER_*`, `NFP_FLOWER_LAYER2_*`) describe which key blocks are present in a flow payload.
- Action opcodes and structs (`nfp_fl_output`, VLAN/MPLS/set-field/tunnel/pre-LAG/pre-tunnel/meter/Geneve structs) are the firmware action-list format.
- Key structs (`nfp_flower_meta_tci`, `ext_meta`, `in_port`, `mac_mpls`, VLAN, L4, IPv4/IPv6, UDP/GRE tunnel, Geneve options) define packed match/mask layout.
- `struct nfp_flower_cmsg_hdr` and `enum nfp_flower_cmsg_type_port` define control-message envelope and message types.
- Port ID helpers encode internal, physical, and PCIe representor ports. Inline netdev helpers recognize offloadable tunnel/internal netdevs.
- Function prototypes expose cmsg allocation/RX and representor messages.

## Control flow
The header has no standalone execution, but its inline helpers are used throughout the Flower app. Port encoding helpers compose bitfields consumed by firmware and decoded in `main.c`; tunnel type helpers are used by action validation; data pointer helpers strip the fixed cmsg header for typed payload access.

## State and persistence
The header defines in-memory and firmware-wire state layouts. Offloaded flow keys/actions persist in firmware after flow add messages; cmsg payloads are transient skbs. The port-id bit layout persists as the contract between host and firmware.

## Dependencies and integration points
It depends on Linux bitfield, skb, Geneve/GRE/VXLAN netdev helpers, NFP app/CPP types, and Ethernet/IP structs. It is central to `action.c`, `cmsg.c`, `conntrack.c`, `lag_conf.c`, `main.c`, tunnel code, and match compiler code not in this subset.

## Risks
This is ABI-critical. Changing struct sizes, alignment, action opcodes, layer bits, or port-id bitfields can break firmware. Max constants such as `NFP_FL_MAX_A_SIZ`, Geneve option limits, and workqueue queue length define enforcement points in C files. Inline `nfp_fl_is_netdev_to_offload()` uses string comparison for openvswitch kind plus tunnel helpers; new netdev kinds need explicit support.

## Test signals
Compile-time users should validate struct sizes through flow offload tests. Runtime signals include successful offload for each key/action layer, representor port ID round trips, tunnel netdev recognition, cmsg type dispatch coverage, and firmware acceptance/rejection of flow add payloads built from these layouts.

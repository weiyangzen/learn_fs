# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.h

## Purpose

`nfp_net_sriov.h` defines the NFP VF configuration mailbox and per-VF entry layout used by PF-side SR-IOV configuration code. It also declares the VF netdev operation helpers exported by `nfp_net_sriov.c`.

## Important APIs, Types, and Functions

The header defines mailbox size constants, capability bits (`MAC`, `VLAN`, `SPOOF`, `LINK_STATE`, `TRUST`, `VLAN_PROTO`, `RATE`), update bits, mailbox return/update/VF selector offsets, per-VF entry offsets for MAC/control/VLAN/rate, bit masks for trust/spoof/link-state/VLAN protocol/QoS/VID/rate, link-state encodings, and `NFP_NET_VF_RATE_MAX`. Declared functions mirror Linux VF ndo operations.

## Control Flow

There is no executable control flow. Setters use the layout to write a VF entry, fill mailbox update fields, and trigger firmware reconfiguration. Getter uses the same layout to decode `struct ifla_vf_info`.

## State and Persistence Behavior

The described state is a firmware-visible memory table. The first 16 bytes are the mailbox and the following fixed-width entries are indexed by VF number. The control byte combines link-state, spoof-check, and trust state; VLAN and rate fields pack multiple logical values.

## Dependencies and Integration Points

It integrates with PF runtime symbol mapping in `nfp_net_main.c`, Linux VF netdev operations in representor/netdev ops, and firmware handling of `NFP_NET_CFG_UPDATE_VF`.

## Risks and Edge Cases

Field packing must match firmware endian and bit placement. The comment notes MAC layout is chosen so firmware can read the address in one 6-byte read, which is easy to break by changing offsets. New capabilities need both mailbox cap and update bits to avoid host/firmware disagreement.

## Test Signals

Compile with SR-IOV paths, inspect generated offsets with firmware documentation, and run VF configuration tests for every declared capability, including old firmware that lacks VLAN protocol or rate capability.

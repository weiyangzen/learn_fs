<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_enet_desc.h

## Purpose

`cq_enet_desc.h` defines Ethernet-specific ENIC completion formats for TX work queues and RX receive queues, including 16-, 32-, and 64-byte RX completion variants and their bit masks.

## Important APIs, Types, and Definitions

`struct cq_enet_wq_desc` represents TX completions. RX completions are described by `struct cq_enet_rq_desc`, `cq_enet_rq_desc_32`, and `cq_enet_rq_desc_64`, which include completed index, queue/RSS flags, RSS hash, byte count, VLAN TCI, checksum/FCoE fields, packet flags, optional fetch index, timestamp, and programmable information fields. Capability macros define supported RX CQ entry sizes and `VNIC_RQ_ALL` for firmware commands.

Important masks describe SOP/EOP, ingress port, FCoE, RSS type, checksum-not-calculated, bytes written, truncation, VLAN stripped, VLAN TCI fields, FCoE SOF/EOF, TCP/UDP/IP checksum status, IPv4/IPv6/protocol flags, fragment status, and FCS status.

## Control Flow

The file has no direct control flow. ENIC RX CQ service code decodes these fields to validate packets, compute length, set checksum state, record RSS hash, restore VLAN tags, account truncation/FCS errors, and support extended CQ metadata.

## State and Persistence Behavior

These structures model hardware-written DMA completion entries. The only persistence is volatile ring memory until software consumes and clears/recycles descriptors.

## Dependencies and Integration Points

It includes `cq_desc.h` and is used by `enic_main.c` plus RX helper code. Firmware capability commands select RX CQ entry size through the constants defined here.

## Risks and Edge Cases

Bitfield interpretation differs by CQ entry size and firmware patch level for VXLAN metadata. Wrong masks would corrupt checksum offload decisions or packet length/VLAN/RSS handling. Structure padding must match hardware exactly.

## Test Signals

Validate RX with 16/32/64-byte CQ entries, VLAN stripped packets, RSS hash types, IPv4/IPv6/TCP/UDP checksum states, truncated/FCS-error packets, VXLAN offload metadata, and ring color/index wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_enet_desc.h -->

# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.h

Purpose: Defines transmit-side hardware descriptor formats, software queue state, buffer bookkeeping, offload metadata, status codes, and stats for the Octeon EP VF driver.

Important APIs/types/functions: `struct octep_vf_tx_sglist_desc` is a 40-byte hardware SGLIST entry with four lengths and four DMA pointers. `OCTEP_VF_SGLIST_ENTRIES_PER_PKT` and `OCTEP_VF_SGLIST_SIZE_PER_PKT` size per-packet gather storage for `MAX_SKB_FRAGS`. `struct octep_vf_tx_buffer` tracks the SKB, direct DMA address, SGLIST pointer/DMA address, and gather flag. `struct octep_vf_iq` is the persistent input queue object. `struct octep_vf_instr_hdr`, `struct tx_mdata`, and `struct octep_vf_tx_desc_hw` define the 64-byte hardware instruction including data pointer, instruction header, optional offload metadata, and extension headers. Offload macros classify checksum, VLAN insert, and TSO flags.

Control flow and integration: The main Tx path fills `octep_vf_tx_desc_hw` and `tx_mdata`, rings the IQ doorbell, and stores DMA/SKB metadata in `octep_vf_tx_buffer`; `octep_vf_tx.c` later uses the same structures for completion cleanup. Device setup stores MMIO doorbell/count/interrupt register pointers in `struct octep_vf_iq`.

State and persistence: `struct octep_vf_iq` persists per Tx queue while the device is open. Coherent descriptor and SGLIST memory is shared with hardware. Offload metadata is transient per descriptor but ABI-sensitive because firmware interprets the fields.

Dependencies: Depends on Linux networking constants (`MAX_SKB_FRAGS`, SKB types, `netdev_queue`), DMA address types, and hardware ABI bitfield layout. Static size assertions validate the three most critical wire-format structs.

Risks: Hardware bitfield layout and SGLIST length ordering must match firmware. TSO/checksum offload flags must be kept in sync with the advertised netdev features and firmware capability. Ring index fields are 16-bit while queue counts are 32-bit, so configuration must keep descriptor counts within valid hardware/software bounds.

Test signals: Compile-time static assertions, Tx checksum/TSO/VLAN traffic, maximum-fragment SKBs, queue stop/wake behavior, and DMA debug runs for direct and gather packets are relevant tests.

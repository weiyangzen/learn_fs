# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.h

Purpose: declares SXGBE DMA descriptor data structures and the descriptor operation table consumed by the main TX/RX paths.

Important APIs and types: `SXGBE_DESC_SIZE_BYTES` is 16. `enum tdes_csum_insertion` defines checksum insertion modes. `struct sxgbe_tx_norm_desc`, `struct sxgbe_rx_norm_desc`, `struct sxgbe_tx_ctxt_desc`, and `struct sxgbe_rx_ctxt_desc` map hardware normal/context descriptor formats. `struct sxgbe_desc_ops` declares all descriptor callbacks implemented in `sxgbe_desc.c`. `sxgbe_get_desc_ops()` returns the provider.

Control flow: queue code allocates rings of these descriptors, fills read-format fields before setting owner bits, and later decodes writeback-format fields after hardware clears ownership. Context descriptors carry TSO, VLAN, and timestamp metadata.

State and persistence: descriptor rings are DMA-visible memory owned by queue structures. Header fields persist only for ring lifetime and are reused per packet.

Dependencies and integration: forward-declares `sxgbe_extra_stats` and integrates with common private queue state, DMA programming, and netdev transmit/receive paths.

Risks: the structs use implementation-defined C bitfield layout for hardware ABI. `u64 buf2_addr:62` and unions spanning read/write formats require exact compiler behavior and correct endian target assumptions. Changes to descriptor size or fields must match hardware and ring-tail programming in DMA code.

Test signals: `sizeof`/layout validation against hardware documentation, descriptor ring DMA tests on target endian/architecture, TX/RX ownership transitions, context descriptor timestamp and TSO behavior, and sparse/compiler warnings.

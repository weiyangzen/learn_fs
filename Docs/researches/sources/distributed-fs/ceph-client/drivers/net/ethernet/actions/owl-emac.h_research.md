# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.h

Purpose: this header defines the register map, bit fields, constants, descriptor formats, and private data structures used by the Actions Semi Owl EMAC driver.

Important APIs, types, and functions: constants define driver name, poll/timeout durations, MTU bounds, RX frame size, SKB alignment/reserve, multicast/setup-frame limits, and ring sizes. Register macros cover MAC CSR0/1/2/3/4/5/6/7/8/9/10/11/16/17/18/19/20 and MAC_CTRL, including DMA start/stop, status, interrupt, MDIO, MAC address, flow-control, and RMII/SMII fields. Descriptor macros define RX `RDES0/RDES1` and TX `TDES0/TDES1` ownership, status, error, size, interrupt, setup-frame, and ring-end bits. Data structures include `struct owl_emac_addr_list`, `struct owl_emac_ring_desc`, `struct owl_emac_ring`, and `struct owl_emac_priv`. Clock definitions provide `owl_emac_clk_names[]`, `OWL_EMAC_NCLKS`, and `enum owl_emac_clk_map`.

Control flow: this header has no executable control flow. It shapes how `owl-emac.c` programs hardware: ring descriptor fields are written before ownership transfer, CSR status bits are cleared by writing status back, CSR6 controls DMA and link mode, CSR10 drives MDIO transactions, and CSR3/CSR4 receive descriptor base addresses.

State and persistence: `struct owl_emac_priv` is the central per-device state object. `struct owl_emac_ring` persists descriptor memory, DMA addresses, SKB pointers, and circular head/tail indices while the driver is active. `struct owl_emac_ring_desc` mirrors hardware DMA descriptors and must remain coherent with device-visible memory. `struct owl_emac_addr_list` caches multicast addresses for setup-frame programming.

Dependencies and integration points: the header expects kernel types and macros included by the C file, including `BIT`, `GENMASK`, `ETH_*`, `HZ`, `struct net_device`, `struct clk_bulk_data`, `struct reset_control`, `struct mii_bus`, `struct napi_struct`, `phy_interface_t`, `struct work_struct`, and spinlocks. Its register definitions must match the Actions Owl EMAC hardware manual and the C implementation.

Risks: duplicated `OWL_EMAC_VAL_MAC_CSR10_OPCODE_WR` definitions should remain consistent. Ring sizes are powers of two, required by `CIRC_SPACE` and the mask-based next-index helper. Descriptor bit definitions are correctness-critical; wrong masks can cause DMA ownership, length, or error interpretation bugs. Address fields are `u32`, tying the implementation to a 32-bit DMA mask. Header constants such as multicast limit and setup-frame length must align with hardware filtering behavior.

Test signals: compile with sparse/W=1 for type assumptions, validate ring sizes stay powers of two, exercise RX/TX descriptors under traffic, verify CSR bit programming by register traces if available, and test RMII/SMII, flow control, multicast, MDIO, and interrupt paths that consume these definitions.

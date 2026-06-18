# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/myri10ge/myri10ge_mcp.h

Purpose: host/firmware ABI definitions for Myri-10G MCP Ethernet firmware. It defines command, response, TX/RX descriptor, status block, firmware command IDs, error codes, flags, and limits used by `myri10ge.c`.

Important types: `mcp_dma_addr`, `mcp_slot`, `mcp_cmd`, `mcp_cmd_response`, `mcp_kreq_ether_send`, `mcp_kreq_ether_recv`, and `mcp_irq_data`. Important constants include firmware version `1.4`, send flags for checksum/TSO/small packets, SRAM command offsets, RSS commands, TSO mode commands, MDIO/I2C commands, and firmware error statuses.

Control flow: no code flow, but command enum values drive `myri10ge_send_cmd` interactions and firmware setup sequencing.

State and persistence: structs define shared memory and DMA-visible state exchanged with firmware. `mcp_irq_data` is persistently DMA-updated during interface runtime and holds link/drop/TX completion state.

Dependencies and integration: included by the Myricom driver; uses big-endian wire fields because firmware command descriptors are endian-defined.

Risks: ABI changes are high risk because firmware expects exact layouts and command numbers. Some flag values are intentionally overloaded for normal and TSO descriptors. `MXGEFW_OLD_IRQ_DATA_LEN` supports legacy stats DMA fallback.

Test signals: sparse/endian checks, firmware command coverage, descriptor layout validation, RSS/TSO/multicast command behavior, and ethtool stats derived from `mcp_irq_data`.

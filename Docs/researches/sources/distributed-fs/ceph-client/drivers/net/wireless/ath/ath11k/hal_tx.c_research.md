# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.c

## Purpose
`hal_tx.c` implements TX-side HAL helpers for filling TCL data command descriptors, programming hardware DSCP-to-TID mapping tables, and preinitializing TCL data ring entries with the correct TLV tag/length.

## Important APIs and functions
`ath11k_hal_tx_cmd_desc_setup()` fills a `struct hal_tcl_data_cmd` from `struct hal_tx_info`: DMA address, return buffer manager, descriptor cookie, descriptor type, encapsulation/encryption type, search type, address-search flags, metadata command number, data length, packet offset, TID, LMAC id, DSCP table id, AST search index/hash, and optional mesh enable through hardware ops.

`ath11k_hal_tx_set_dscp_tid_map()` programs the default 64-entry DSCP map into a selected hardware DSCP/TID table. `ath11k_hal_tx_init_data_ring()` walks an allocated TCL data SRNG and sets each entry's TLV header to `HAL_TCL_DATA_CMD`.

## Control flow
Descriptor setup is straight field packing. DSCP map programming enables TCL DSCP/TID programming access, packs eight 3-bit TID values into three bytes at a time, writes the 24-byte table via HIF register writes, then disables access. Data-ring init obtains SRNG parameters and entry size, then advances through ring memory.

## State and persistence behavior
The file mutates DMA ring entries and device registers. DSCP mapping persists in hardware until reset or reprogramming. Data-ring initialization writes shared ring memory. There is no disk persistence and no private mutable static state beyond the constant default map.

## Dependencies and integration points
It depends on `hal_desc.h`, `hal.h`, `hal_tx.h`, and `hif.h`. DP TX calls descriptor setup during TCL enqueue. DP setup programs DSCP/TID tables and initializes data rings. Mesh handling delegates to `ab->hw_params.hw_ops->tx_mesh_enable()`.

## Risks
Incorrect field packing can misroute TX buffers, break encryption/encapsulation, or corrupt completion cookies. DSCP packing uses byte copies and `*(u32 *)&hw_map_val[i]`, relying on safe layout/access assumptions. Register programming is not locally locked. Mesh enable assumes a valid hardware op when requested.

## Test signals
Successful TX traffic, correct QoS/TID behavior under DSCP-marked packets, valid TX completions, no TCL stalls, and mesh TX validation are the main signals.

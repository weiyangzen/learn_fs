# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi_enet.h

## Purpose
`bfi_enet.h` defines the ethernet-specific hardware/firmware ABI for the BNA driver. It covers data-path descriptor layouts for TX, RX, and completion queues, interrupt block configuration, control-path MSGQ command/response formats, RSS/RIT and MAC/VLAN filtering, pause and loopback requests, attributes, and the full DMA statistics layout.

## Important APIs, Types, and Functions
- Data-path formats: `struct bfi_enet_txq_entry`, `struct bfi_enet_txq_wi_base`, `struct bfi_enet_txq_wi_vector`, `struct bfi_enet_rxq_entry`, and `struct bfi_enet_cq_entry`.
- Queue configuration formats: `struct bfi_enet_q`, `bfi_enet_txq`, `bfi_enet_rxq`, `bfi_enet_cq`, `bfi_enet_ib`, and `bfi_enet_ib_cfg`.
- Control opcodes: `enum bfi_enet_h2i_msgs` and `enum bfi_enet_i2h_msgs`.
- Generic command/response layouts: `struct bfi_enet_req`, `bfi_enet_enable_req`, and `bfi_enet_rsp`.
- Attribute formats: `bfi_enet_attr_req` and `bfi_enet_attr_rsp`.
- TX/RX config messages: `bfi_enet_tx_cfg_req`, `bfi_enet_tx_cfg_rsp`, `bfi_enet_rx_cfg_req`, and `bfi_enet_rx_cfg_rsp`.
- Filter/config commands: RIT, RSS, unicast, multicast, MAC+VLAN, VLAN block, pause, and loopback structures.
- Statistics formats: `struct bfi_enet_stats` and nested MAC, BPC, RAD, FC RX/TX, RXF, and TXF counters.

## Control Flow and State
Higher layers fill these structures, set `bfi_msgq_mhdr` with class `BFI_MC_ENET`, set `num_entries` according to the structure size, and post through MSGQ. Firmware responds with matching I2H opcodes. `bna_enet.c` dispatches responses by `msg_id`: queue config responses go to TX/RX objects, filter responses go to RXF, port admin and loopback responses go to ETHPORT, pause responses go to ENET, attributes go to IOCETH, stats responses update software statistics, and link/port/bandwidth AENs update link/TX state.

## State and Persistence Behavior
The structures configure firmware and hardware state: queue DMA pages, interrupt/coalescing parameters, RX/TX mode, filters, VLAN blocks, RSS keys/RIT, pause mode, loopback mode, WOL, and stats DMA buffers. The host-visible state is stored in BNA objects and DMA memory; firmware-visible state persists until cleared, disabled, or reset.

## Dependencies and Integration Points
The header includes `bfa_defs.h` and `bfi.h`. It is consumed by `bna.h`, `bna_enet.c`, and TX/RX/RXF modules outside this work item. `bna_hw_defs.h` duplicates or mirrors several descriptor constants for the driver-side fast path. The MSGQ header from `bfi.h` is embedded in every ENET control-path command.

## Risks
- The file warns that all values must be written in big-endian; missed conversions cause firmware misconfiguration.
- Packed descriptor and response layouts are hardware ABI-sensitive.
- `BFI_ENET_CFG_MAX` is 32, while masks are 32-bit; out-of-range resource IDs would silently overflow masks.
- Statistics copy logic in `bna_enet.c` assumes firmware packs selected per-RID stats densely according to masks.
- Some command IDs are no longer needed per comments but remain in the ABI; removing them would risk compatibility.

## Test Signals
Strong signals include TX/RX queue configuration success and valid doorbell offsets, RX completions with expected CQ flags, RIT/RSS programming, unicast/multicast/VLAN filter responses, pause and loopback responses, attribute query population, link and port AEN handling, WOL commands if supported, and stats DMA with correct endian-converted counters.

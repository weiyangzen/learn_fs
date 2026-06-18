# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_dump.c

## Purpose
`igc_dump.c` provides debug dumping for selected hardware registers and Tx/Rx descriptor rings. It is used when hardware debug message levels are enabled, primarily from reset or diagnostic logging paths.

## Important APIs, Types, And Functions
The exported functions are `igc_rings_dump(struct igc_adapter *)` and `igc_regs_dump(struct igc_adapter *)`. `struct igc_reg_info` maps register offsets to names for `igc_reg_info_tbl[]`. The static `igc_regdump()` helper reads scalar registers or four queue-indexed instances for ring register families such as `RDLEN`, `RDH`, `RDT`, `RXDCTL`, `TDBAL`, `TDLEN`, `TDH`, and `TXDCTL`.

## Control Flow
`igc_regs_dump()` prints a header and walks `igc_reg_info_tbl[]`, delegating formatting to `igc_regdump()`. `igc_rings_dump()` first checks `netif_msg_hw(adapter)`, prints device state, then returns early if the netdev is not running. It prints Tx summaries, optionally detailed Tx descriptors and packet data when `netif_msg_tx_done()` and `netif_msg_pktdata()` are enabled, then prints Rx summaries and optional detailed Rx descriptors when `netif_msg_rx_status()` is enabled.

## State And Persistence
The file is observational. It reads MMIO registers, descriptors, DMA metadata, SKB pointers, page-backed Rx buffers, and ring indices, but does not intentionally mutate device or driver state.

## Dependencies And Integration Points
It depends on `igc.h` for adapter/ring layout, descriptor access macros, netdev logging, `rd32`, DMA unmap metadata, and buffer sizing. `igc_main.c` calls the dump helpers from reset-task diagnostics when message flags request hardware logging.

## Risks
Verbose dumps can expose packet contents and pointer-like values in logs when packet data logging is enabled. Ring dumps race with live traffic unless called in controlled contexts, so values are diagnostic snapshots rather than stable state. Excess logging may affect performance or log volume.

## Test Signals
Signals include enabling driver message levels, triggering reset or dump paths, confirming register and queue formats are readable, validating no crashes when rings are absent or netdev is down, and checking packet hex dumps only appear under the expected message flags.

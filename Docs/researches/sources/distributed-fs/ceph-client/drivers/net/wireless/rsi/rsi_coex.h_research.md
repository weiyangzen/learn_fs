# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_coex.h

## Purpose
This header declares the optional WLAN/Bluetooth coexistence control block and APIs used when `CONFIG_RSI_COEX` is enabled.

## Important APIs, Types, and Functions
It defines `COMMON_CARD_READY_IND`, `NUM_COEX_TX_QUEUES`, `struct rsi_coex_ctrl_block`, and prototypes for `rsi_coex_attach`, `rsi_coex_detach`, `rsi_coex_send_pkt`, and `rsi_coex_recv_pkt`.

## Control Flow
The header has no executable flow. In the implementation users, core initialization attaches coexistence for operating modes with BT, RX demux routes coex queue traffic to `rsi_coex_recv_pkt`, and the Bluetooth stack can transmit through `rsi_coex_send_pkt` via `rsi_proto_ops`.

## State and Persistence Behavior
`struct rsi_coex_ctrl_block` holds a back-pointer to `rsi_common`, coexistence TX queues, and a coexistence TX thread. State exists only while the module is loaded and coex is attached.

## Dependencies and Integration Points
It includes `rsi_common.h` and depends on SKB queues and the shared `rsi_thread` abstraction. Integration points are `rsi_91x_main.c`, RX queue demux, BT attach/detach callbacks, and bus packet transmission.

## Risks
Because all declarations are behind `CONFIG_RSI_COEX`, callers must guard references correctly. Queue numbering must stay consistent with firmware queue IDs. Coex teardown must stop its thread and purge SKBs before the shared `rsi_common` is freed.

## Test Signals
Builds with and without `CONFIG_RSI_COEX`, STA+BT/AP+BT operating modes, BT card-ready deferral, coex queue TX/RX ordering, and detach during active BT traffic are useful signals.

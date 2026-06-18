# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/sdio_txrx.c

## Purpose
Implements the active SDIO TX/RX datapath worker and IRQ entry point. It drains mt76 TX queues into SDIO write bursts, reads RX packets described by parsed interrupt metadata, accounts PSE/PLE/MCU quotas, and coordinates suspend/reset waits.

## Important APIs, Types, And Functions
Exported functions are `mt76s_txrx_worker()`, `mt76s_sdio_irq()`, and `mt76s_txqs_empty()`. Internal helpers include `mt76s_refill_sched_quota()`, `mt76s_rx_run_queue()`, `mt76s_rx_handler()`, `mt76s_tx_pick_quota()`, `mt76s_tx_update_quota()`, `__mt76s_xmit_queue()`, and `mt76s_tx_run_queue()`.

## Control Flow
The SDIO IRQ disables interrupts and schedules `txrx_worker`. The worker disables interrupts, repeatedly runs data TX queues, the MCU TX queue, and RX handling until no frames or quota updates remain, then re-enables interrupts. RX handling calls the chip-specific `parse_irq()`, reads RX0/RX1 blocks from `MCR_WRDR(qid)`, splits packets by RX descriptor length, builds SKBs, publishes them to RX queues, and schedules `net_worker`. TX handling batches entries into `sdio->xmit_buf`, respecting firmware-running state, block-size padding, transmit quotas, and MCU reset state.

## State And Persistence
Persistent runtime state includes SDIO scheduler quotas (`pse_mcu_quota`, `pse_data_quota`, `ple_data_quota`, page size, deficit), queue head/first/tail indexes, per-entry `done` flags, shared transmit buffer contents, and `bus_hung`. RX pages are transiently allocated per read and SKBs hold page references for fragments.

## Dependencies And Integration Points
Depends on `sdio.h` registers, chip-specific IRQ parsing, Linux SDIO block I/O, mt76 queue and worker infrastructure, driver `rx_check()` and `rx_skb()` callbacks, tracepoints, MCU/reset state bits, and `mt76_skb_adjust_pad()` for raw TX padding.

## Risks
Quota accounting can stall TX if interrupts do not refill counts or if PSE/PLE sizes are miscomputed. RX aggregation parsing trusts descriptor lengths after validation; malformed data can drop frames or set `bus_hung`. Worker interrupt masking must always be paired with re-enable. Queue pointer barriers are required so bus access sees complete entries.

## Test Signals
Sustained bidirectional traffic, MCU command TX before and after firmware start, RX0/RX1 delivery, quota exhaustion/recovery, suspend and MCU reset waits, injected SDIO read/write errors setting `bus_hung`, and no lost interrupts after worker exit.

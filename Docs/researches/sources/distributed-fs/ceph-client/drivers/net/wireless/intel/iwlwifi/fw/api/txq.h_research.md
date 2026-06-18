# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/txq.h

## Purpose
Defines TX queue numbering, FIFO selection, queue sizing, and TXQ hardware scheduler configuration ABI for iwlwifi DQA and newer queue APIs.

## Important APIs, Types, And Functions
`enum iwl_mvm_dqa_txq` reserves queue IDs for command, auxiliary, P2P device/monitor injection, groupcast, BSS client, management, AP probe response, and data queues. `enum iwl_mvm_tx_fifo`, `enum iwl_gen2_tx_fifo`, and `enum iwl_bz_tx_fifo` define firmware FIFO mappings. `enum iwl_tx_queue_cfg_actions` controls queue enablement and short TFD format. `iwl_tx_queue_cfg_cmd` and `iwl_tx_queue_cfg_rsp` are the packed command/response structures.

## Control Flow
During queue setup, the driver chooses a station/TID, flags, cyclic buffer size, byte-count table DMA address, and TFD queue DMA address, then sends `iwl_tx_queue_cfg_cmd`. Firmware returns the assigned queue number, failure flags, and initial write pointer. Higher-level TX code then maps station/TID traffic or reserved management/control traffic onto these queues.

## State And Persistence
Queue configuration persists in firmware scheduler state and host DMA rings until disabled or device reset. The header defines persistent queue IDs, FIFO mappings, default queue sizes for EHT/HE/legacy, and management/command queue capacities. DMA addresses in the command tie firmware queue state to host-allocated memory.

## Dependencies And Integration Points
Integrates with iwlwifi transport queue allocation, TX command submission, station/TID mapping, aggregation setup, management queue pools, monitor injection, P2P device operation, and generation-specific FIFO selection. It is closely related to scheduler commands in `tx.h`.

## Risks
Queue ID reservations are policy contracts; reusing reserved queues incorrectly can starve command, aux, BSS client, or management traffic. `cb_size` is encoded as an exponent-derived value with documented limits, so wrong encoding can mismatch host ring allocation. DMA addresses must remain valid and aligned for firmware ownership.

## Test Signals
Validate queue allocation on legacy, HE, EHT, Gen2, and BZ FIFO mappings; station/TID queue setup; management queue exhaustion fallback; monitor injection vs. P2P device mutual exclusion; aggregation queue creation; and firmware response failure flags. TX stalls and queue write-pointer mismatches are primary regression indicators.

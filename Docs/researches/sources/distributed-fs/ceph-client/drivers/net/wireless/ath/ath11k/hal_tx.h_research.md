# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal_tx.h

## Purpose
`hal_tx.h` declares the TX HAL interface used by DP TX and related REO command code. It defines the software input model for TCL data command descriptors and the parsed TX completion status structure used around WBM release descriptors.

## Important APIs, types, and data
`struct hal_tx_info` is the central input to `ath11k_hal_tx_cmd_desc_setup()`. It carries metadata flags, descriptor id/cookie, descriptor type, encapsulation and encryption type, DMA address, length, packet offset, checksum/control flags, address search behavior, AST hash/index, TID, LMAC id, DSCP/TID table index, mesh flag, and return buffer manager id.

`struct hal_tx_status` represents parsed TX status: WBM release source, TQM release reason/status, ACK RSSI, status flags, PPDU id, try count, TID, peer id, and rate stats. Declared functions are TX descriptor setup, DSCP/TID map programming, REO command send, and TCL data ring initialization.

## Control flow
The header has no control flow. It integrates DP TX with HAL descriptor creation and lets DP command paths submit REO commands.

## State and persistence behavior
All state is caller-owned. `hal_tx_info` is transient per transmit descriptor, while `hal_tx_status` is transient per completion. Persistent device state is changed by the declared functions through hardware registers and DMA rings.

## Dependencies and integration points
The header includes `hal_desc.h` and `core.h`, and depends on TCL, WBM, and TQM enums. Consumers include DP TX and REO command paths.

## Risks
Semantic mismatch between DP-provided `hal_tx_info` fields and hardware descriptor fields can cause TX drops. Missing or invalid `rbm_id`, AST index/hash, TID, LMAC id, or checksum flags are high-risk. Declaring `ath11k_hal_reo_cmd_send()` here couples TX callers to RX/REO implementation details.

## Test signals
TX enqueue/completion, QoS mapping, encrypted and unencrypted frames, mesh frames when supported, and REO command use from TX management paths should be validated.

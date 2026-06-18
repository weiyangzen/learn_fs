# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/qcu.c

## Purpose

`qcu.c` configures ath5k transmit queues and their Queue Control Unit/Distributed Coordination Function Control Unit hardware. It maps driver queue types to hardware queue IDs, stores per-queue software configuration in `ah->ah_txq[]`, programs contention, retry, CBR, ready-time, burst, beacon/CAB/UAPSD behavior, and maintains secondary per-queue interrupt masks.

## Important APIs, Types, and Functions

Public functions are `ath5k_hw_num_tx_pending()`, `ath5k_hw_release_tx_queue()`, `ath5k_hw_get_tx_queueprops()`, `ath5k_hw_set_tx_queueprops()`, `ath5k_hw_setup_tx_queue()`, `ath5k_hw_set_tx_retry_limits()`, `ath5k_hw_reset_tx_queue()`, `ath5k_hw_set_ifs_intervals()`, and `ath5k_hw_init_queues()`.

The main data type is `struct ath5k_txq_info`, stored per queue in `struct ath5k_hw::ah_txq`. Queue type and subtype values come from ath5k enums and WME access categories. Queue flags drive interrupt mask bits and DCU behavior: TXOK/TXERR/TXURN/TXDESC/TXEOL, CBR overrun/underrun, QTRIG, TXNOFRM, backoff policy, fragmentation burst backoff, and ready-time expiration policy.

`ath5k_cw_validate()` is a small but important helper that caps contention windows at 1023 and coerces requested values to power-of-two-minus-one form. This prevents invalid CW values from being written into DCU local IFS registers.

## Control Flow

Queue setup begins with `ath5k_hw_setup_tx_queue()`, which maps logical queue types to hardware queue IDs. AR5210 has only two non-QCU queues, while newer chips use WME subtype IDs for data, fixed IDs for UAPSD, beacon, and CAB queues. The function resets software state, applies optional queue properties, and marks the queue active in `ah_txq_status`.

Queue property updates run through `ath5k_hw_set_tx_queueprops()`, which rejects inactive queues, copies values, clamps AIFS to `0xFC` because larger values can hang the DCU, validates CW min/max, and forces post-frame backoff disable for video/voice data queues and UAPSD.

Hardware programming is done by `ath5k_hw_reset_tx_queue()`. It skips AR5210 and inactive queues, writes DCU local IFS, retry limits, fragmentation wait, sequence-control quirks, optional CBR/ready-time/burst registers, queue-type-specific beacon/CAB/UAPSD scheduling bits, per-queue interrupt mask state, secondary interrupt mask registers, TXNOFRM masks, and a 1:1 QCU-to-DCU mask.

Global initialization is `ath5k_hw_init_queues()`. On AR5211+ it resets every configured hardware queue; on AR5210 it only programs retry limits. It enables turbo IFS behavior for 40 MHz and calls `ath5k_hw_set_ifs_intervals()` when coverage class did not already set timing.

## State and Persistence Behavior

The file persists queue configuration in `ah->ah_txq[]` and interrupt masks in `ah_txq_status`, `ah_txq_imr_txok`, `ah_txq_imr_txerr`, `ah_txq_imr_txurn`, `ah_txq_imr_txdesc`, `ah_txq_imr_txeol`, `ah_txq_imr_cbrorn`, `ah_txq_imr_cbrurn`, `ah_txq_imr_qtrig`, and `ah_txq_imr_nofrm`. These values are then reflected into SIMR0-SIMR4 and TXNOFRM hardware registers during queue reset. `ath5k_hw_release_tx_queue()` marks queues inactive and clears the active-status mask so future operations filter them out.

Pending frame state is read from hardware through `AR5K_QUEUE_STATUS()` and `AR5K_QCU_TXE`. The function returns a boolean-like true when TXE remains set even with no frame count, allowing upper layers to treat the queue as not fully stopped.

## Dependencies and Integration Points

`qcu.c` includes `ath5k.h`, `reg.h`, `debug.h`, and Linux `log2.h`. It uses register helpers and queue bit macros from ath5k headers. The queue register addresses and fields come from `reg.h`, especially QCU status/control registers, DCU local/global IFS registers, retry limits, secondary interrupt masks, and AR5210 no-DCU registers.

The driver/mac80211 integration point is queue creation and WME parameter application. Reset code calls `ath5k_hw_init_queues()` after hardware reset, tx scheduling paths query `ath5k_hw_num_tx_pending()`, and interrupt setup depends on the per-queue masks written here. Timing code relies on PHY/mac helpers such as `ath5k_hw_htoclock()`, `ath5k_hw_get_default_sifs()`, `ath5k_hw_get_frame_duration()`, and `ath5k_hw_get_default_slottime()`.

## Risks and Edge Cases

The code must preserve AR5210 behavior, which lacks QCU/DCU, while programming richer queue hardware on newer chips. Off-by-one queue IDs or queue count mismatches would corrupt unrelated queue registers. AIFS above `0xFC` is explicitly hazardous because it can hang the DCU; CW values must also be normalized before use.

Beacon and CAB queues have timing-sensitive ready-time formulas involving `AR5K_TUNE_SW_BEACON_RESP`, `AR5K_TUNE_DMA_BEACON_RESP`, and `AR5K_TUNE_ADDITIONAL_SWBA_BACKOFF`. Bad ready time can break beacon delivery or buffered broadcast/multicast traffic. Secondary interrupt masks are derived from accumulated software state and active queue masks; stale bits for inactive queues could cause spurious interrupts, while missing bits can hide queue completions or underruns.

`ath5k_hw_set_ifs_intervals()` depends on a current channel and supported-band rate table. It warns and fails when no matching lowest rate exists for the bandwidth mode. Incorrect clock conversion or SIFS/EIFS programming affects contention fairness and ACK timeout behavior.

## Test Signals

Useful signals include queue reset errors, queue pending counts, TXOK/TXERR/TXEOL/TXURN interrupt distribution by queue, beacon/CAB delivery timing, WME access category latency, UAPSD behavior, and absence of DCU hangs under high AIFS/CW inputs. Tests should exercise AR5210 two-queue mode separately from AR5211+ QCU/DCU mode, all queue types, inactive queue release, 40 MHz turbo IFS, and 5/10 MHz rate-flag selection.

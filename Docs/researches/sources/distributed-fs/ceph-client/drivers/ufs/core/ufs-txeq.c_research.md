# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-txeq.c

## Purpose

`ufs-txeq.c` implements adaptive UFS TX equalization training and application for high-speed gears, including UFSHCI v5.0 TX EQTR flows, M-PHY adaptation length selection, FOM evaluation, preset filtering, debug printing, and manual retraining.

## Important APIs, Types, and Functions

Module parameters are `use_adaptive_txeq`, `adaptive_txeq_gear`, `use_txeq_presets`, and `txeq_presets_selected`. Public functions include exported `ufshcd_apply_tx_eq_settings()`, `ufshcd_print_tx_eq_params()`, `ufshcd_config_tx_eq_settings()`, `ufshcd_apply_valid_tx_eq_settings()`, `ufshcd_is_txeq_presets_used()`, `ufshcd_is_txeq_preset_selected()`, and `ufshcd_retrain_tx_eq()`. Key internal helpers initialize iterators, compute adaptation lengths, apply TXEQ/TXEQTR settings, retrieve RX FOM, and update cached params/records.

## Control Flow

Configuration exits unless TXEQ is supported and adaptive mode is enabled. For eligible HS gears, it trains when cached parameters are invalid or forced. Training prepares the link by switching to HS-G1 with all lanes, sets initial adapt type, notifies variant ops, computes `PA_TXADAPTLENGTH_EQTR`, reads host/device TX equalization capabilities, iterates supported preshoot/deemphasis combinations, writes local and peer TXEQTR settings, triggers UIC TX EQTR, reads local and peer RX_FOM values, records FOM matrices, and chooses best per-lane settings. Applying settings writes local and peer `PA_TxEQGnSetting` and enables precoding for HS-G6 when FOM asks for it. Manual retrain pauses command processing, scales clocks up, negotiates target gear, forces training, and changes power mode.

## State and Persistence Behavior

State lives in module parameters and per-HBA TXEQ caches: capability bitmaps, per-gear `tx_eq_params`, `is_valid`, `is_applied`, FOM records, saved adapt length, and timestamps. Settings are programmed into UniPro/M-PHY attributes and may be lost across reset, so valid cached settings can be reapplied.

## Dependencies and Integration Points

It depends on UniPro DME get/set/peer operations, UFS power-mode changes, clock scaling, command pause/resume, variant ops for FOM and TXEQTR notifications, and debugfs readers in `ufs-debugfs.c`.

## Risks and Test Signals

Risks include long training latency, invalid gear/rate/lane assumptions, capability bitmap interpretation errors, FOM zero fallback hiding bad links, failure to restore old power mode after training errors, module parameter combinations that skip all presets, and variant-op mismatches. Test signals include disabled adaptive mode no-op, HS-G4/G5/G6 training, preset filtering, adaptation length bounds, FOM matrix recording, precoding enablement, reset reapply, manual retrain success/failure, and error paths restoring command processing.

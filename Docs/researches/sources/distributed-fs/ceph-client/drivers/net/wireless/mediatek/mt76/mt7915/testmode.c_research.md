# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.c

## Purpose
This file implements NL80211 testmode support for MT7915/MT7916. It translates mt76 testmode state and parameters into firmware ATE/RF test commands and direct register programming for factory TX/RX, continuous transmit, frequency offset, TX power, timing, queue cleanup, RX statistics, and temporary register setup.

## Important APIs, Types, And Functions
The public object is `const struct mt76_testmode_ops mt7915_testmode_ops` with `.set_state`, `.set_params`, and `.dump_stats`. Key command helpers are `mt7915_tm_set_tx_power()`, `mt7915_tm_set_freq_offset()`, `mt7915_tm_mode_ctrl()`, `mt7915_tm_set_trx()`, `mt7915_tm_clean_hwq()`, `mt7915_tm_set_slot_time()`, `mt7915_tm_set_tam_arb()`, and `mt7915_tm_set_wmm_qid()`.

State-machine helpers include `mt7915_tm_init()`, `mt7915_tm_set_tx_frames()`, `mt7915_tm_set_rx_frames()`, `mt7915_tm_set_tx_cont()`, `mt7915_tm_set_state()`, and `mt7915_tm_set_params()`. `mt7915_tm_set_ipg_params()` converts requested inter-packet gap/duty timing into SIFS/AIFSN/contention window and TMAC checks. `mt7915_tm_set_tx_len()` derives an SKB payload length from requested TX airtime and rate. `mt7915_tm_reg_backup_restore()` backs up and restores AGG/TMAC/ARB/RMAC registers.

## Control Flow
Entering testmode from OFF calls `mt7915_tm_init()`, which enables SKU control, tells firmware to enter testmode, backs up and relaxes MAC registers, disables normal TX/RX, and creates monitor BSS/STA context. Leaving testmode restores registers, disables arbitration test mode, and returns the monitor station to disconnect state. TX frame mode disables RXV, clears hardware queues, updates channel, computes antenna/SPE, configures TAM arbitration, timing, TX length, and starts MAC TX if an SKB is available. RX frame mode updates channel, clears FCS counters, and enables RX/RXV. Continuous TX switches firmware into RF test mode, programs channel/bandwidth/rate/antenna, and returns to normal RF mode on stop.

## State And Persistence
Per-phy test state lives in `phy->mt76->test` and `phy->test`: last RSSI/RCPI/SNR/frequency offset, `spe_idx`, and `reg_backup`. Register backup memory is devm-allocated and persists for the device lifetime after first use. Hardware state is intentionally mutated while testmode is active and restored when state returns OFF.

## Dependencies And Integration Points
The code depends on mt76 testmode data, cfg80211 bitrate calculation, mt7915 MCU command helpers, MURU control, monitor vif setup, queue/WMM mapping, and register definitions from `regs.h`. It integrates with firmware `MCU_EXT_CMD(ATE_CTRL)`, `TX_POWER_FEATURE_CTRL`, and `RF_TEST` commands.

## Risks
Incorrect state transitions can leave normal MAC TX/RX disabled, test arbitration active, or RF test mode enabled. Register backup is per-band but the backup list is global and must match `TM_REG_MAX_ID`. IPG and TX length calculations can underflow or produce unrealistic queue limits if inputs are inconsistent. Continuous TX rate mapping depends on band rate tables and channel width validation. Antenna mask validation happens in `.set_params`, so stale or out-of-range test parameters can fail late.

## Test Signals
Exercise OFF to IDLE to TX_FRAMES/RX_FRAMES/TX_CONT and back to OFF, including both bands, MT7915 and MT7916 FCS counter masks, HE MU arbitration, duty-cycle derived IPG, explicit TX time, frequency offset, TX power, and invalid bandwidth/rate inputs. After testmode exit, normal association and traffic should recover and direct register dumps should show restored AGG/TMAC/RMAC values.

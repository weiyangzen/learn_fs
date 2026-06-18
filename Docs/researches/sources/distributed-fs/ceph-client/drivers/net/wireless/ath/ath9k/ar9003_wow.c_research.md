# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_wow.c

## Purpose
`ar9003_wow.c` implements Wake-on-Wireless-LAN support for AR9003 hardware. It programs user wake patterns, creates the hardware keep-alive frame, enables wake events such as magic packet/link change/beacon miss/user pattern, transitions the MAC/RTC/PCIe state into WoW sleep, reads wake reasons, clears wake events, and restores selected power/reset state on wake.

## Important APIs, Types, and Functions
Exported APIs are `ath9k_hw_wow_apply_pattern()`, `ath9k_hw_wow_wakeup()`, and `ath9k_hw_wow_enable()`. Internal helpers are `ath9k_hw_set_sta_powersave()`, `ath9k_hw_set_powermode_wow_sleep()`, `ath9k_wow_create_keep_alive_pattern()`, and `ath9k_hw_wow_set_arwr_reg()`.

The file uses `ah->wow.wow_event_mask`, `ah->wow.wow_event_mask2`, and `ah->wow.max_patterns` from `struct ath9k_hw_wow`; current MAC/BSSID from `ath_common`; current channel and chainmask from `ath_hw`; and WoW register definitions from `reg_wow.h`.

## Control Flow
`ath9k_hw_wow_apply_pattern()` validates the pattern index against hardware capacity, enables the pattern bit in legacy or extended pattern registers, writes fixed-size pattern and mask tables in 32-bit chunks, records the corresponding enabled wake-event bit in `wow_event_mask` or `wow_event_mask2`, writes the pattern length into one of four packed length registers, and returns `0` or `-ENOSPC`.

`ath9k_hw_wow_enable()` begins from the accumulated user-pattern mask, enables PCIe PME-related control bits, configures random backoff, AIFS/slot/keep-alive counts, beacon timeout, keep-alive timeout/delay, writes a generated keep-alive frame descriptor and data buffer, enables or disables link-change and beacon-miss event generation, enables magic packet matching when requested, enables pattern matching for packets under 256 bytes, programs host PM control for D1/D3 or AR9462 real D3, clears sequence-number preservation so hardware can transmit while asleep, applies a PCIe PHY low-power tweak, applies PCIe reset/POR wiring changes, keeps RTC awake for MCI, disables a PCU WoW bit, transitions to WoW sleep, and stores the final event mask.

`ath9k_hw_wow_wakeup()` reads legacy and extended WoW status registers, masks out events that were not enabled by the driver, maps hardware status bits to `AH_WOW_*` result flags, clears PME, clears all WoW events, restores RSSI threshold, restores PCIe power-save wiring, restarts TSF2 generation on affected chips if needed, clears the stored event masks, and returns the wake reason bitmap.

## State and Persistence Behavior
WoW state persists in hardware registers during sleep and in `ah->wow` event masks across the enable-to-wakeup interval. User patterns are stored in hardware pattern/mask tables. The keep-alive frame is generated from current station MAC and BSSID and stored in hardware WoW TX buffer registers. On wake, event masks are cleared in memory and event bits are cleared in hardware. No filesystem persistence is used.

## Dependencies and Integration Points
This file depends on `ath9k.h`, `reg.h`, `reg_wow.h`, and `hw-ops.h`. It integrates with MCI through `ath9k_hw_mci_is_enabled()` and `ar9003_mci_state(MCI_STATE_GET_WLAN_PS_STATE)`. In this source snapshot, that MCI state query is declared but not handled in `ar9003_mci_state()`, so the default zero return makes WoW treat WLAN PS as disabled and set `AR_STA_ID1_PWR_SAV`. It integrates with PCIe power management through `ath9k_hw_configpcipowersave()` and with gen timers through `ath9k_hw_gen_timer_start_tsf2()`.

## Risks
`ath9k_hw_wow_apply_pattern()` always copies `MAX_PATTERN_SIZE` and `MAX_PATTERN_MASK_SIZE` bytes from caller-provided buffers, so callers must provide fully sized buffers even when `pattern_len` is smaller. Endianness and alignment of `memcpy()` into `u32` pattern words matter. Wake status can include spurious hardware bits, so masking with stored event masks is essential. Power-state sequencing is revision-specific, especially AR9462 D3 handling and TSF2 disable/restart logic. The MCI PS-state query edge means any future implementation of `MCI_STATE_GET_WLAN_PS_STATE` may change WoW sleep behavior.

## Test Signals
Test signals include successful pattern programming for legacy and extended slots, correct length register fields, expected wake reasons for magic packet/user pattern/link change/beacon miss, no wake reason for masked spurious bits, successful RX DMA stop before sleep, correct PCIe PME assertion, keep-alive frame transmission at 1 Mbps CCK or 6 Mbps OFDM as appropriate, TSF2 restart on wake for affected revisions, and clean interaction with MCI-enabled devices.

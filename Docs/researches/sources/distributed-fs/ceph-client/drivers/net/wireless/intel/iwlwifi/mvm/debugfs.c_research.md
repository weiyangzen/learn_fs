# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.c

## Purpose

Implements device-level and link-station MVM debugfs: firmware/device telemetry, thermal/CTDP controls, TX flush, SRAM and debug memory access, station/rate/AMSDU state, power-off overrides, TAS/SAR/6E status, firmware/driver stats, firmware restart/NMI, scan antenna, RSS indirection, packet/beacon injection, firmware debug controls, HE sniffer configuration, LTR, RFI, NVM blobs, and PM-sleep debug flags.

## Important APIs, Types, and Functions

`iwl_mvm_dbgfs_register()` creates device entries; `iwl_mvm_link_sta_add_debugfs()` creates station-link entries. Notable handlers cover CTDP, temperature, `tx_flush`, `sram`, `mem`, `prph_reg`, station/rate stats, AMSDU length, power-off disable, TAS, RX/system/driver stats, restart/NMI, scan antenna, RSS indirection, injected RX packets, beacon IE injection/restore, firmware debug config/clear/timepoint, HE sniffer params, LTR, and RFI table access.

## Control Flow

Registration adds text file ops through macros, a custom binary `mem` file, NVM blobs, booleans, PM-sleep files, and a mac80211 symlink. Most writes check firmware state, parse bounded input, lock `mvm->mutex`, mutate state or send firmware commands, and return count/error. Reads allocate/format buffers and may request fresh firmware statistics first.

Special flows include synthetic RX packet injection through `iwl_mvm_rx_mq()`, beacon template modification for AP mode, notification-ordered HE sniffer AID/BSSID updates, and aligned LMAC/UMAC debug memory reads/writes selected by file offset.

## State and Persistence Behavior

Maintains runtime debug state such as SRAM window, temperature test override, AMSDU original length, power-off disable flags, scan RX antenna, PRPH address, firmware debug config, HE sniffer AID/BSSID, beacon injection flags/tailroom, driver RX stats, and exposed NVM blobs/booleans.

## Dependencies and Integration Points

Depends on debugfs, user-copy helpers, firmware commands, transport memory/prph access, mac80211 VIF/STA/link state, RX path, beacon templates, rate formatting, CTDP/thermal, SAR/TAS/ACPI, RFI, LTR, RSS, firmware debug runtime, notification waits, and NVM storage.

## Risks

Many entries are intentionally invasive: restart/NMI, raw memory/prph writes, packet injection, TX flush, beacon injection, thermal override, and power-off overrides can destabilize live hardware. Buffer estimates must remain bounded. Memory offset alignment and UMAC/LMAC selection are subtle. Beacon injection must restore `extra_beacon_tailroom`.

## Test Signals

Verify file creation/permissions, running vs stopped firmware reads, invalid input rejection, old/new TX flush, SRAM/mem alignment, station/rate/AMSDU override, restart/NMI triggers, scan antenna validation, RSS hex patterns, packet/beacon injection, HE sniffer ordering, RFI table read/default resend, and PM-sleep-only files.

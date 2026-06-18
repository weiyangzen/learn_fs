# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_main.h

## Purpose
This is the central shared state and constant header for the RSI 91x WLAN driver. It defines debug zones, firmware FSM states, queue constants, data/control structures, common adapter state, hardware wrapper state, and host-interface operation callbacks.

## Important APIs, Types, and Functions
Important definitions include `enum RSI_FSM_STATES`, queue and watermark constants, WoWLAN flags, `enum rsi_dev_model`, `struct version_info`, `struct skb_info`, `enum edca_queue`, `struct security_info`, `struct wmm_qinfo`, `struct transmit_q_stats`, `struct rsi_bgscan_params`, `struct vif_priv`, `struct rsi_event`, `struct rsi_thread`, `struct cqm_info`, `enum rsi_dfs_regions`, `struct rsi_9116_features`, `struct rsi_rate_config`, `struct rsi_common`, `struct eepromrw_info`, `struct eeprom_read`, `struct rsi_hw`, and `struct rsi_host_intf_ops`.

## Control Flow
The header has no executable flow, but it defines the control surfaces used by the driver. `struct rsi_common` carries the firmware FSM, TX queues, locking, VIF/station tables, scans, PS, WoWLAN, AP, P2P, rate, security, and coexistence state. `struct rsi_hw` wraps mac80211 hardware, transport identity, power-save state, debugfs, firmware metadata, EEPROM, interrupt state, bus-private pointer, and function pointers used by bus-independent HAL code.

## State and Persistence Behavior
All major runtime state is shaped here: initialization and MAC FSM state, queue backlogs, locks, completion objects, channel/band, bitrate masks, security ciphers, EDCA parameters, firmware version, MAC address, RF/channel state, sleep configuration, beacon/AP station records, remain-on-channel timer, BT/coex references, background scan configuration, 9116 feature bits, EEPROM work buffers, and host-interface callbacks. State is in-memory per adapter and is rebuilt on probe or hibernate reinit.

## Dependencies and Integration Points
It includes Linux SKB/string headers, mac80211, public RSI 91x net header, and `rsi_ps.h`. It is the common include for core, mac80211, management, USB, SDIO, debugfs, coex, and power-save code.

## Risks
This header is a high-blast-radius contract: changing struct layout, queue constants, or FSM values affects nearly every file. Locking responsibilities are implicit in fields rather than encoded in helper APIs. `RSI_MAX_VIFS`, `RSI_MAX_ASSOC_STAS`, queue counts, and `MAX_HW_QUEUES` must stay aligned with firmware and mac80211 registration. Function pointer callbacks may be NULL for unsupported transports, so callers must check where optional.

## Test Signals
Full driver builds for USB/SDIO, PM, debugfs, and coex variants; probe/init/deinit; all FSM transitions; VIF/station/queue limits; rate mask and EDCA behavior; WoWLAN/PS/scanning/AP/P2P workflows; and static analysis for structure initialization coverage are key signals.

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.c

## Purpose
This file implements firmware download, firmware mailbox command delivery, power-save/WoWLAN/P2P firmware commands, reserved-page packet download, and C2H rate-report handling for RTL8821AE/RTL8812AE. It bridges rtlwifi/mac80211 state to the chip firmware by writing firmware images into MCU memory, polling firmware readiness bits, serializing H2C commands through HME boxes, and constructing special packets that firmware later transmits for power-save and wake-on-wireless flows.

It supports both normal firmware and WoWLAN firmware, plus two reserved-page layouts: 256-byte pages for RTL8821AE and 512-byte pages for RTL8812AE. Large static byte arrays serve as packet templates for beacon, PS-Poll, null data, QoS null, BT QoS null, ARP response, remote wake control, and GTK extension memory pages.

## Important APIs, Types, And Functions
Firmware lifecycle helpers include `_rtl8821ae_enable_fw_download()`, `_rtl8821ae_write_fw()`, `_rtl8821ae_fw_free_to_go()`, `rtl8821ae_download_fw()`, optional `rtl8821ae_set_fw_related_for_wowlan()`, and `rtl8821ae_firmware_selfreset()`. H2C transport is handled by `_rtl8821ae_check_fw_read_last_h2c()`, `_rtl8821ae_fill_h2c_command()`, and exported `rtl8821ae_fill_h2c_cmd()`.

Command builders include `rtl8821ae_set_fw_pwrmode_cmd()`, `rtl8821ae_set_fw_media_status_rpt_cmd()`, `rtl8821ae_set_fw_ap_off_load_cmd()`, `rtl8821ae_set_fw_wowlan_mode()`, `rtl8821ae_set_fw_remote_wake_ctrl_cmd()`, `rtl8821ae_set_fw_keep_alive_cmd()`, `rtl8821ae_set_fw_disconnect_decision_ctrl_cmd()`, `rtl8821ae_set_fw_global_info_cmd()`, `rtl8812ae_set_fw_rsvdpagepkt()`, `rtl8821ae_set_fw_rsvdpagepkt()`, `rtl8821ae_set_p2p_ps_offload_cmd()`, and `rtl8821ae_c2h_ra_report_handler()`.

Important state comes from `struct rtl_hal` (`pfirmware`, `wowlan_firmware`, sizes, `fw_version`, `fw_ready`, `last_hmeboxnum`, `h2c_setinprogress`, `p2p_ps_offload`, `current_ra_rate`), `struct rtl_ps_ctl` (LPS, WoWLAN, ARP/GTK offload, P2P PS), `struct rtl_mac` (MAC address, BSSID, AID, hidden SSID, P2P role), `struct rtl_security`, and Bluetooth coexistence callbacks.

## Control Flow
`rtl8821ae_download_fw()` chooses normal or WoWLAN firmware from `rtlhal`, reads and skips a Realtek firmware header when the signature matches, clears an old downloaded state if MAC function is enabled, enables firmware download mode, writes the image in 4 KiB pages through `rtl_fw_page_write()`, disables download mode, then polls checksum and firmware-init-ready bits in `_rtl8821ae_fw_free_to_go()`. That helper also sets `MCUFWDL_RDY`, clears `WINTINI_RDY`, self-resets firmware, and waits until firmware reports initialization complete.

H2C command flow starts at `rtl8821ae_fill_h2c_cmd()`, which refuses to send if `fw_ready` is false, copies the command into an 8-byte local buffer, and calls `_rtl8821ae_fill_h2c_command()`. The lower helper serializes against `rtlhal->h2c_setinprogress` under `h2c_lock`, chooses one of four HME boxes using `last_hmeboxnum`, waits until firmware has read the box, writes the base and extension registers depending on command length, advances the box number, and clears the in-progress flag.

Power-save command builders pack small H2C byte arrays through macros from `fw.h`. LPS mode selection accounts for Bluetooth coexistence override, P2P awake intervals, smart PS, RPWM/power state, and records BT-selected power mode. WoWLAN builders configure pattern/magic/disconnect wake, remote wake ARP/GTK/RealWoW flags, keep-alive period, disconnect decision timeout, and AOAC security algorithms.

Reserved-page functions mutate static packet templates with current MAC/BSSID/AID, choose partial or whole reserved-page lengths, allocate an SKB, copy the reserved-page bytes, send them through `rtl_cmd_send_packet()`, then notify firmware of page locations via `H2C_8821AE_RSVDPAGE` and optionally `H2C_8821AE_AOAC_RSVDPAGE`. P2P PS offload updates CTWindow and NoA hardware registers, adjusts start times relative to TSF, updates `rtlhal->p2p_ps_offload`, and sends it as an H2C command. C2H RA reports translate firmware rates with `rtl8821ae_hw_rate_to_mrate()` and feed DM power tracking through `rtl8821ae_dm_update_init_rate()`.

## State And Persistence
Firmware image data is owned by `rtlhal` and not allocated here. This file persists firmware metadata (`fw_version`, `fw_subversion`), H2C mailbox position, H2C in-progress state, firmware readiness and PS state, P2P offload state, and current RA rate. Reserved-page packet templates are static mutable arrays; each call patches addresses/AID into shared template storage before copying to an SKB.

Hardware/firmware persistent effects include MCU download registers, HMEBOX/HMEBOX_EXT mailbox registers, firmware PS mode, WoWLAN/AOAC state, keep-alive/disconnect policy, reserved-page contents in firmware packet memory, NoA registers, and firmware station/rate state affected indirectly by H2C commands. Most of this state is lost on firmware reset and must be replayed by init, WoWLAN, or mac80211 power-save flows.

## Dependencies And Integration Points
The file depends on rtlwifi core register accessors, firmware utilities (`rtl_fill_dummy()`, `rtl_fw_page_write()`), command packet submission (`rtl_cmd_send_packet()`), SKB allocation APIs, endian helpers, mac80211 `ieee80211_hw`, Bluetooth coexistence ops, efuse/security state, and dynamic-management functions from `dm.c`. Command layout and IDs are defined in `fw.h`; register constants come from `reg.h` and `def.h`.

External callers include hardware init and resume paths for firmware download, power management code for LPS/WoWLAN/remote wake/keep-alive commands, AP/P2P flows for offload commands, reserved-page setup during power-save preparation, and firmware C2H dispatch for RA reports.

## Risks
`rtl8821ae_download_fw()` logs firmware readiness failure but returns `0` after `_rtl8821ae_fw_free_to_go()` regardless of `err`; callers that depend on the return value may mark firmware usable even after readiness polling failed. H2C serialization has long busy waits and can return early from timeout paths while relying on later cleanup of `h2c_setinprogress`; mailbox bugs can stall all firmware commands. Command length handling only covers one to seven bytes, so future longer commands need a new transport path.

The reserved-page templates are static mutable buffers, so concurrent calls could race and cross-contaminate MAC/BSSID/AID fields. SKB allocation failure silently returns without H2C location updates. Packet lengths subtract 40 bytes from fixed page totals, so descriptor/header assumptions must match `rtl_cmd_send_packet()` behavior. P2P NoA start-time adjustment mutates `noa_count_type[]` while iterating, which can affect later state. WoWLAN command composition is spread across several commands, so partial failure can leave firmware with inconsistent wake policy.

Hardware compatibility risk is high because RTL8812AE and RTL8821AE share much code but differ in page size, reset bits, RF path count, and firmware behavior. The file also uses hard-coded registers such as `0x5cf`, `0x5E0`-`0x5EC`, and `0x130`, which need hardware documentation when changed.

## Test Signals
Firmware tests should validate normal and WoWLAN image download, header stripping, page writes, checksum report, firmware init ready, self-reset behavior, and failure propagation. H2C tests should cover all four mailbox boxes, extension bytes for four-to-seven byte commands, timeout behavior when firmware does not clear a box, and concurrent command senders under lockdep.

Power-save and WoWLAN signals include correct LPS mode with and without BT control, firmware keep-alive intervals, wake on pattern/magic/disconnect, ARP/GTK offload, AOAC global security algorithms, and reserved-page location commands. Reserved-page validation should inspect transmitted template contents for correct MAC/BSSID/AID and page offsets on both RTL8821AE and RTL8812AE. P2P tests should cover CTWindow, two NoA descriptors, scan/scan-done transitions, GO/client role bits, and TSF-relative start adjustment. C2H tests should confirm RA report rates update `current_ra_rate` and trigger DM power tracking.

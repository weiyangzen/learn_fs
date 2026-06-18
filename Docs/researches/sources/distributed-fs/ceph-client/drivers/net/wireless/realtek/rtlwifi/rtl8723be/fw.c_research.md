# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.c

## Purpose
Implements RTL8723BE host-to-firmware command submission and firmware-side power-management support. It serializes H2C mailbox writes, constructs LPS power-mode and media-status commands, downloads reserved pages for firmware autonomous frames, and configures P2P power-save offload.

## Important APIs, Types, And Functions
`rtl8723be_fill_h2c_cmd()` is the public H2C wrapper, gated by `rtlhal->fw_ready`. `_rtl8723be_fill_h2c_command()` owns mailbox selection, locking, firmware-read polling, register writes to HMEBOX and extension boxes, and box index advancement. `rtl8723be_set_fw_pwrmode_cmd()` builds `H2C_8723B_SETPWRMODE` using LPS mode, smart PS, awake interval, RPWM state, and Bluetooth coexistence overrides. `rtl8723be_set_fw_media_status_rpt_cmd()` reports connect/disconnect. `rtl8723be_set_fw_rsvdpagepkt()` patches a static reserved-page packet image with current MAC/BSSID/AID, sends it as a command skb, and reports page locations to firmware. `rtl8723be_set_p2p_ps_offload_cmd()` programs CTWindow/NoA registers and sends P2P PS offload state.

## Control Flow
H2C submission waits for any in-progress command under `h2c_lock`, selects the next firmware mailbox, waits for firmware to clear that box, writes normal and extension payload bytes depending on command length, rotates `last_hmeboxnum`, and clears the in-progress flag. LPS command flow optionally lets BT coexistence force active/min mode and supply byte5/RPWM values. Reserved-page flow mutates static packet templates, sends them through `rtl_cmd_send_packet()`, then sends page-location H2C only if the packet download succeeded.

## State And Persistence
Persistent state includes `rtlhal->last_hmeboxnum`, `rtlhal->h2c_setinprogress`, `rtlhal->p2p_ps_offload`, `rtlps->p2p_ps_info`, firmware mailbox registers, P2P NoA hardware registers, and the static `reserved_page_packet` template. Firmware retains reserved-page locations and power-save/offload settings until replaced or reset.

## Dependencies And Integration Points
Depends on rtlwifi firmware common helpers, register definitions, `rtl_cmd_send_packet()`, power-save state from `rtl_ps_ctl`, Bluetooth coexistence callbacks, mac80211 BSSID/MAC/AID state, and H2C command ids/macros in `fw.h`. `hw.c` calls these through `set_hw_reg()` for join reports, keepalive, LPS, and P2P PS.

## Risks
Mailbox serialization is timing-sensitive; timeouts can silently drop firmware commands. Command lengths above seven bytes are unsupported by the switch. Reserved-page templates contain fixed frame bodies that are only partially patched, so wrong offsets or stale addresses break firmware PS responses. P2P NoA start-time adjustment loops mutate count values and depend on TSF timing. BT-controlled LPS can override requested mode, making power regressions hard to attribute.

## Test Signals
Verify firmware-ready gating, successful H2C logs, association reserved-page download, LPS entry/exit, keepalive behavior, P2P GO/client CTWindow and NoA operation, and Bluetooth coexistence LPS transitions. Failures show as HMEBOX wait warnings, missed PS-Poll/null/QoS-null behavior, P2P clients waking incorrectly, or firmware not acknowledging power-mode changes.

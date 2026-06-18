# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.c

## Purpose
`fw.c` implements RTL8723AE host-to-firmware command delivery and firmware-assisted power-save helpers, including reserved-page packet download and P2P power-save offload.

## APIs, Types, And Functions
Public functions are `rtl8723e_fill_h2c_cmd`, `rtl8723e_set_fw_pwrmode_cmd`, `rtl8723e_set_fw_rsvdpagepkt`, `rtl8723e_set_fw_joinbss_report_cmd`, and `rtl8723e_set_p2p_ps_offload_cmd`. Internals include mailbox-read checking, locked H2C box filling, CTWindow command setup, and a static 768-byte reserved-page template for beacon, PS-Poll, null data, and probe response pages.

## Control Flow, State, And Persistence
H2C command fill waits for exclusive `h2c_lock` ownership, selects the next firmware mailbox, polls until firmware has read it, writes normal/extended mailbox bytes for 1-5 byte commands, then advances the mailbox index. Reserved-page setup patches MAC/BSSID/AID fields, sends the template through `rtl_cmd_send_packet`, and tells firmware page locations. P2P offload writes NoA/CTWindow registers and sends a packed offload byte.

## Dependencies And Integration Points
The file depends on rtlwifi core/PCI, firmware common definitions, mac80211 P2P state, `rtl_cmd_send_packet`, register accessors, and H2C IDs. BT coexistence also uses the H2C helper heavily.

## Risks And Test Signals
Risks include mailbox races/timeouts, firmware-not-ready commands, static reserved-page corruption, skb allocation failure, and P2P NoA timing mistakes. Signals are firmware command completion, LPS/IPS behavior, reserved-page download success, P2P Notice-of-Absence operation, and BT coexistence H2C delivery.

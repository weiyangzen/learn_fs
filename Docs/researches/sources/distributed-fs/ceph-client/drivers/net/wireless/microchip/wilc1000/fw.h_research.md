# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/fw.h

Purpose: Defines packed firmware ABI structures and limits for WILC1000 host-interface commands, association data, PMKID/key payloads, P2P NoA/OPP data, join parameters, external authentication parameters, and NVMEM bank addressing.

Important APIs and types: Key structs include `wilc_assoc_resp`, `wilc_pmkid`, `wilc_pmkid_attr`, `wilc_reg_frame`, `wilc_drv_handler`, `wilc_sta_wpa_ptk`, `wilc_ap_wpa_ptk`, `wilc_wpa_igtk`, `wilc_gtk_key`, `wilc_op_mode`, `wilc_noa_opp_enable`, `wilc_noa_opp_disable`, `wilc_join_bss_param`, and `wilc_external_auth_param`. Constants define maximum stations, rates, PMKIDs, scanned channels, and NVMEM bank layout. `get_bank_offset_from_bank_index()` computes bank metadata offsets.

Control flow: No runtime control flow beyond the inline bank offset helper. The structures are filled in `cfg80211.c` and `hif.c`, then passed to firmware via WID commands.

State and persistence: These packed payloads represent firmware-visible state such as security keys, operation mode, join BSS details, PMKID cache, and external auth status. NVMEM bank constants refer to persistent device storage metadata.

Dependencies and integration points: Includes `linux/ieee80211.h` for WLAN constants. Used by HIF command construction and cfg80211 join/key/auth paths.

Risks: Packed layouts are firmware ABI; changing field order, size, endian annotations, or max lengths can break firmware commands. Flexible-array key structs must be allocated with exact payload lengths to avoid truncation or overflow. NVMEM bank offset calculations must match chip storage layout.

Test signals: Association to WPA/WPA2/WPA3 networks, PMKID operations, PTK/GTK/IGTK installation, P2P NoA parsing, external auth, and NVMEM read/write users of bank offsets validate this ABI.

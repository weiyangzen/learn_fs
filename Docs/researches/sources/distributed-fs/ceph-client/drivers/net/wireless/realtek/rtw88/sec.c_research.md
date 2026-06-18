## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.c

Purpose: manages rtw88 hardware security CAM allocation, programming, clearing, backup enumeration, and security engine enablement.

Important APIs/functions: `rtw_sec_get_free_cam()` chooses the next free CAM slot, reserving the first four entries when default-key search is enabled. `rtw_sec_write_cam()` fills an eight-word CAM entry with key index, cipher type, group/pairwise flag, valid bit, station/broadcast address, and key bytes. `rtw_sec_clear_cam()` invalidates one CAM entry. `rtw_sec_cam_pg_backup()` lists used CAM IDs for page backup. `rtw_sec_enable_sec_engine()` enables MAC security and default-key search bits.

Control flow: mac80211 key installation selects/free CAM indexes, writes content through `RTW_SEC_WRITE_REG`/`RTW_SEC_CMD_REG`, and updates the driver's shadow `cam_table` and `cam_map`. Enabling security toggles `REG_CR` and `RTW_SEC_CONFIG`.

State and persistence: persistent in-memory state is `rtw_sec_desc` shadow CAM map/table and `default_key_search`; hardware state is the CAM and security engine registers. Keys are referenced via `ieee80211_key_conf`.

Dependencies and integration: depends on rtw88 core structures, `sec.h` registers, and Linux key/cipher metadata. TX/RX descriptor paths use the installed key state for hardware crypto.

Risks and test signals: risks include CAM slot leaks, wrong group/pairwise address, unsupported cipher mapping, and stale CAM entries after key removal. Test with WEP/TKIP/CCMP association, group rekey, pairwise rekey, multi-VIF keys, and suspend/resume CAM backup paths.

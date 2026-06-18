# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.c

## Purpose
Implements hardware security CAM management for rtlwifi. It resets software security state, programs encryption keys into CAM entries, deletes/invalidates/empties CAM entries, and tracks free pairwise CAM slots for station MAC addresses.

## Important APIs, Types, and Functions
Exports `rtl_cam_reset_sec_info()`, `rtl_cam_add_one_entry()`, `rtl_cam_delete_one_entry()`, `rtl_cam_reset_all_entry()`, `rtl_cam_mark_invalid()`, `rtl_cam_empty_entry()`, `rtl_cam_get_free_entry()`, and `rtl_cam_del_entry()`. The main internal helper is `rtl_cam_program_entry()`, which writes the eight CAM content words for one entry through `WCAMI` and `RWCAM` mapped registers.

## Control Flow
`rtl_cam_add_one_entry()` validates the key ID, builds the CAM config word from valid bit, encryption algorithm, default-key flag, and key ID, then calls `rtl_cam_program_entry()`. Programming iterates CAM content indices from 7 down to 0. Entry 0 packs config and the first two MAC bytes, entry 1 packs the remaining MAC bytes, and entries 2-5 pack the 128-bit key; entries 6-7 are reserved but still written from key offsets implied by the loop. Delete writes zero to the first content word for the key ID. Reset all writes `BIT(31)|BIT(30)` to `RWCAM`. Mark invalid and empty write config-like content based on current pairwise encryption algorithm. Free-entry management scans entries 4 through `TOTAL_CAM_ENTRY - 1`, preserving entries 0-3 for default keys.

## State and Persistence Behavior
Software state lives in `rtlpriv->sec`: encryption algorithms, key buffers/lengths, pairwise key pointer, `hwsec_cam_bitmap`, and `hwsec_cam_sta_addr`. Hardware state persists in the CAM until entries are overwritten, invalidated, emptied, or globally reset. `rtl_cam_get_free_entry()` sets the bitmap and stores the station MAC; `rtl_cam_del_entry()` clears matching bitmap bits and addresses, but hardware removal is expected through separate CAM delete/empty calls.

## Dependencies and Integration Points
Depends on `wifi.h`, `cam.h`, `rtl_priv()`, `rtl_write_dword()`, hardware register maps `WCAMI`/`RWCAM`/`SEC_CAM_*`, Ethernet address helpers, Realtek debug macros, and exported symbols for other rtlwifi modules. It integrates with mac80211 key installation/removal paths in the driver.

## Risks and Test Signals
`rtl_cam_add_one_entry()` only rejects `ul_key_id == TOTAL_CAM_ENTRY`, not greater values. `rtl_cam_delete_one_entry()` ignores `mac_addr` and uses `ul_key_id` as the entry index. `rtl_cam_mark_invalid()` sets `BIT(15)`, which is named `CFG_VALID`, so its semantics are suspicious for an invalidation helper. `rtl_cam_empty_entry()` also leaves bit 15 set in entry 0. Bitmap updates are not locally locked, so callers must serialize key operations. Tests should cover pairwise versus default keys, all encryption algorithms, full CAM allocation, duplicate station lookup, deletion bitmap clearing, hardware readback after reset/empty/delete, and invalid key IDs.

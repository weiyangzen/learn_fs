# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.h

## Purpose
Defines the firmware command layouts, bit masks, constants, and exported function prototypes for `rtw89` CAM programming. It is the contract between CAM implementation code, firmware H2C builders, chip-specific DCTL paths, and mac80211-facing key/address management.

## Important APIs, Types, and Functions
The header defines `RTW89_SEC_CAM_LEN`, BSSID match masks, packed address CAM H2C structs `rtw89_h2c_addr_cam_v0` and `rtw89_h2c_addr_cam`, and packed DCTL update structs `rtw89_h2c_dctlinfo_ud_v1`, `rtw89_h2c_dctlinfo_ud_v2`, and `rtw89_h2c_dctlinfo_ud_v3`. Most of the file is field-mask definitions for address CAM words, BSSID CAM words, and DCTL words, including MAC ID, port, TSF sync, target indication, AID, WoW, WAPI, security entry mode, key IDs, security entry validity, MLD address/BSSID fields, VLAN fields, NAT25, and version-specific security entry widths. It declares all public CAM lifecycle, key, and H2C packing functions implemented in `cam.c`.

## Control Flow
The header has no runtime control flow, but its layouts drive firmware command construction. `fw.c` and chip hooks allocate command buffers and call `rtw89_cam_fill_addr_cam_info()`, `rtw89_cam_fill_bssid_cam_info()`, or the DCTL v1/v2/v3 fillers to populate these bitfields. `mac80211.c`, `mac.c`, SER, and WoW code call the lifecycle and key APIs declared here to keep firmware CAM state aligned with vif/link/station/key state.

## State and Persistence Behavior
The structs in this header are packed command payloads rather than long-lived state. Persistent CAM state lives in `core.h` structures referenced by the APIs, especially `rtwdev->cam_info`, per-link address/BSSID CAM entries, and security CAM entries. The masks encode the persistent state into firmware-visible little-endian words and must match firmware interpretation for each CAM/DCTL version.

## Dependencies and Integration Points
Includes `core.h` for driver-private types and constants. Integrates directly with `cam.c`, `fw.c`, chip-specific firmware command code, mac80211 key callbacks, MLO address handling, WoW PTK replay/IV restoration, and firmware role updates. The v2/v3 DCTL structs add MLD fields, so this header is also part of the driver's Wi-Fi 7/MLO firmware ABI.

## Risks
This is an ABI-sensitive header. Field masks, word numbering, packed layout, and version-specific widths must remain synchronized with firmware. Several masks differ subtly between v1, v2, and v3, especially MAC ID size, security entry indexing, and MLD address placement. A wrong mask may compile cleanly but corrupt unrelated firmware fields. Adding a cipher or changing `RTW89_SEC_CAM_LEN` requires coordinated changes in key installation and firmware command builders.

## Test Signals
Compile all chip variants using address CAM and DCTL v1/v2/v3. Validate H2C command dumps for station, AP, P2P, WoW, MLD, non-MLD, group and pairwise keys, BIP, and 256-bit ciphers. Runtime signals include successful association, encrypted data and management frames, MLD link setup, WoW resume, BSSID color/mask handling, and absence of firmware CAM update errors.

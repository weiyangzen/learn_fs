# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.h

Purpose: WoWLAN constants, helper types, and PM-facing declarations for rtw89.

Important APIs/types: defines PN/IPN bit masks, WoW key-info valid/symbol flags, MIC key length, firmware wake reason enum, firmware cipher algorithm enum, RSN/cipher suite structs, cipher metadata, key-iteration scratch data, security header length helper, link-state predicates, managed-feature predicate, AKM parser wrapper, and suspend/resume prototypes under `CONFIG_PM`.

Control flow/integration: TX paths call `rtw89_wow_parse_akm()` for association requests when PM is enabled. PM code calls `rtw89_wow_suspend()`/`rtw89_wow_resume()`. `rtw89_wow_get_sec_hdr_len()` supplies chip-specific security header length for older chips based on current WoW PTK algorithm.

State and persistence: declarations operate on `rtwdev->wow`; the header itself owns no state.

Dependencies: relies on `struct rtw89_dev`, vif link state, firmware enums, chip IDs, mac80211 skb/header helpers, and bitmap helpers through included project headers.

Risks/test signals: `CONFIG_PM` stubs mean non-PM builds compile out most WoW behavior. Algorithm/header-length tables must match firmware expectations. Build tests for PM and non-PM configs and WoW suspend/resume tests cover the surface.

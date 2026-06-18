# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.c

## Purpose
This file implements MT7925 regulatory CLC handling. It applies country-list constraints to channel availability and EHT support, responds to cfg80211 regulatory notifications, handles firmware CLC updates, and supports automatic 11d-driven country changes when allowed.

## Important APIs, Types, And Functions
Exports are `mt7925_regd_clc_supported()`, `mt7925_regd_be_ctrl()`, `mt7925_mcu_regd_update()`, `mt7925_regd_notifier()`, `mt7925_regd_change()`, and `mt7925_regd_init()`. The `disable_clc` module parameter disables CLC support. Important internal logic includes ACPI MTCL interpretation, CLC BE-control rule scanning, and channel-flag updates for UNII-4 through UNII-8.

## Control Flow
Regulatory notification records user-initiated changes, ignores repeated or late world-domain updates, copies alpha2/DFS/env into mt76 state, marks `regd_change`, and either defers during suspend or calls `mt7925_mcu_regd_update()`. The update path sets `regd_in_progress`, takes the MT792x mutex/PM reference, sends CLC to firmware, updates BE/EHT capability, disables unavailable 5.9/6 GHz channels, sends the channel domain, reapplies SAR TX power, then clears state and wakes waiters. The 11d change helper validates alpha2, CLC support, user override state, and current alpha2 before either issuing `regulatory_hint()` or directly setting CLC for non-11d chips.

## State And Persistence
Persistent state includes `mdev->alpha2`, `mdev->region`, `dev->country_ie_env`, `dev->regd_user`, `dev->regd_change`, `dev->regd_in_progress`, `dev->has_eht`, `phy->clc_chan_conf`, and channel flags in the wiphy bands. Updates can be postponed across suspend and replayed by PCI resume.

## Dependencies And Integration Points
The file integrates cfg80211 regulatory callbacks, ACPI MTCL helpers from `mt792x_acpi_sar.c`, MT7925 MCU CLC/channel-domain/SAR commands, wiphy band/channel flag storage, PM mutex handling, and the PCI suspend/resume wait path.

## Risks
Regulatory handling is high impact: incorrect CLC interpretation can expose disabled 5.9/6 GHz channels or incorrectly clear EHT support. The code mutates channel flags additively and does not visibly clear previous disables in this path, so update sequencing depends on cfg80211/mac80211 reset behavior. Suspended updates rely on resume replay. User-set regulatory domains intentionally block automatic 11d changes.

## Test Signals
Country changes for world, US/EU/6 GHz countries, user override, 11d beacons, suspend during regdom change, ACPI MTCL present/absent cases, `disable_clc`, USB exclusion, EHT flag changes, and SAR reapplication validate the behavior.

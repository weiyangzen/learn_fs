# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regd.h

## Purpose
This header exposes the MT7925 regulatory helper API to bus, MCU, init, and mac80211-facing code.

## Important APIs, Types, And Functions
It declares `mt7925_mcu_regd_update()`, `mt7925_regd_be_ctrl()`, `mt7925_regd_notifier()`, `mt7925_regd_clc_supported()`, `mt7925_regd_change()`, and `mt7925_regd_init()`. These are the external hooks used for cfg80211 regulatory notifier registration, 11d country changes, CLC updates, and EHT/channel capability recalculation.

## Control Flow
No runtime logic is implemented here. The header enables PCI resume and regulatory callback code to call into `regd.c` while keeping the file boundaries explicit.

## State And Persistence
No state is stored here. The declared functions manipulate `mt792x_dev`, `mt792x_phy`, wiphy regulatory flags, alpha2/country environment state, CLC data, and channel flags.

## Dependencies And Integration Points
It includes `mt7925.h`, so consumers get MT792x/MT7925 type definitions and firmware environment enums. It is included by PCI and regulatory-related MT7925 sources.

## Risks
The main risk is API mismatch with `regd.c` or missing declarations when regulatory behavior changes. Since it includes the large MT7925 header, circular include changes can have broad build impact.

## Test Signals
Compilation of MT7925 PCI/USB and regulatory code, plus successful notifier registration and resume-time `mt7925_mcu_regd_update()` calls, validate the header.

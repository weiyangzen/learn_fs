# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/cam.h

## Purpose
Declares rtlwifi hardware security CAM constants and functions for programming, deleting, resetting, and allocating CAM key entries.

## Important APIs, Types, and Functions
Defines `CAM_CONTENT_COUNT` as eight words per entry, `CFG_VALID`, `PAIRWISE_KEYIDX`, `CAM_PAIRWISE_KEY_POSITION`, and `CAM_CONFIG_NO_USEDK`. Public APIs mirror `cam.c`: reset all entries, add/delete one entry, mark invalid, empty an entry, reset software security info, get a free pairwise entry, and delete a tracked station entry.

## Control Flow
The header has no runtime flow. It exposes the CAM operations to key-management code and other rtlwifi modules.

## State and Persistence Behavior
No state is declared directly. Functions operate on `struct ieee80211_hw` and mutate `rtlpriv->sec` plus hardware CAM registers.

## Dependencies and Integration Points
Depends on kernel/driver definitions for `struct ieee80211_hw`, `u8`, `u32`, and `BIT()`. It is included by `cam.c` and by rtlwifi code that installs or removes encryption keys.

## Risks and Test Signals
The header provides low-level entry-index APIs without range annotations, so misuse can corrupt reserved/default CAM entries. Tests should compile-check all users, enforce index bounds in callers, and verify pairwise entries start at `CAM_PAIRWISE_KEY_POSITION`.

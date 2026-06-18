# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.h

Purpose: Declares miscellaneous utility helpers for TSO segmentation, beacon IE offset lookup, and negative dBm averaging.

Important APIs and functions: `iwl_tx_tso_segment()` is declared when `CONFIG_INET` is enabled and stubbed to warn/fail otherwise. `iwl_find_ie_offset()` returns the offset of an information element in a beacon frame. `iwl_average_neg_dbm()` returns a signed averaged dBm value from unsigned negative dBm samples.

Control flow: `iwl_find_ie_offset()` validates that the frame reaches the beacon variable area, subtracts fixed header length, calls `cfg80211_find_ie()`, and returns zero on missing/error or the IE offset on success.

State and persistence: Header owns no state. Helpers inspect caller-owned SKBs/beacon buffers and may mutate SKBs through the C implementation.

Dependencies and integration points: Includes cfg80211 and relies on ieee80211 management-frame layout. Used by TX and scanning/beacon parsing paths.

Risks: Offset zero is both a valid byte offset in abstract and the error sentinel, though beacon IEs normally start after fixed fields. Frame-size validation must avoid pointer underflow/overflow. The non-INET TSO stub returns `-1` rather than a specific errno.

Test signals: Beacon IE lookup with short frames, missing/present EIDs, CONFIG_INET disabled build, and callers treating zero as not found.

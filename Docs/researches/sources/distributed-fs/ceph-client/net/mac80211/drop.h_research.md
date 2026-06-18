# sources/distributed-fs/ceph-client/net/mac80211/drop.h

## Purpose

`drop.h` defines mac80211-specific RX drop reasons and the bitwise `ieee80211_rx_result` type. It gives RX handlers precise drop/error return values that can be converted into kernel skb drop reason space while still allowing sparse to distinguish handler results from ordinary integers.

## Important APIs, Types, And Functions

The file defines `typedef unsigned int __bitwise ieee80211_rx_result`, the macro list `MAC80211_DROP_REASONS_UNUSABLE(R)`, internal enum `___mac80211_drop_reason`, public enum `mac80211_drop_reason`, and the predicate `RX_RES_IS_UNUSABLE(result)`.

`MAC80211_DROP_REASONS_UNUSABLE` lists many `RX_DROP_U_*` values for MIC failures, replay, bad MMIE, duplicate/spurious frames, decrypt/key/cipher failures, invalid AMSDU/802.3 frames, unprotected robust management/action frames, malformed/runt management/data/control/BAR frames, mesh-specific failures, port-control mismatches, unknown stations/actions, and no-link cases.

## Control Flow

There is no runtime control flow beyond macro expansion and the `RX_RES_IS_UNUSABLE()` predicate. The two-enum design first creates untyped internal constants anchored to `SKB_CONSUMED`, `SKB_NOT_DROPPED_YET`, and the mac80211 unusable drop subsystem base, then casts the public enum values to `ieee80211_rx_result`.

## State And Persistence

No mutable state exists. Values are compile-time constants that become return values and skb drop reason inputs elsewhere.

## Dependencies And Integration Points

It depends on `<net/dropreason.h>` for `SKB_DROP_REASON_SUBSYS_MAC80211_UNUSABLE`, `SKB_DROP_REASON_SUBSYS_SHIFT`, masks, and skb consumed/not-dropped constants. RX path files include this header to return `RX_CONTINUE`, `RX_QUEUED`, or specific unusable drop reasons and to test whether a result belongs to the unusable subsystem.

## Risks

The macro list is an ABI-like diagnostic surface. Reordering or inserting values changes numeric drop reason meanings unless coordinated with drop-reason expectations. The comment marker near the trailing backslash is a maintenance guard; new reasons must be inserted before it. Sparse bitwise typing helps catch misuse but only where sparse is run. `RX_RES_IS_UNUSABLE()` relies on subsystem mask layout matching the internal enum base.

## Test Signals

Build with sparse to catch `ieee80211_rx_result` misuse. Runtime RX tests should verify specific malformed/security/drop cases map to expected `RX_DROP_U_*` values and that `kfree_skb_reason()` or tracing reports mac80211 subsystem reasons. Compile tests should cover additions to the reason list.

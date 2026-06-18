# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/testmode.c

## Purpose
This file implements MT7925 vendor testmode netlink commands for RF/test control and query responses. It lets monitor-mode users switch test mode on/off, send firmware test-control commands, and query testmode/RX-stat events.

## Important APIs, Types, And Functions
The exported callbacks are `mt7925_testmode_cmd()` and `mt7925_testmode_dump()`. Internal helpers are `mt7925_tm_set()` and `mt7925_tm_query()`. The file defines MT7925-specific nested netlink attributes, exact-length policies, `mt7925_tm_cmd`, and `mt7925_tm_evt`/response sizing.

## Control Flow
Command handling requires the PHY to be running and the hw config to be monitor mode. The set path parses nested driver data, copies it into an RF test command, locks the mt76 mutex, detects mode-switch actions, disables runtime PM and takes driver ownership before entering test mode, marks `phy->test.state`, sends `MCU_UNI_CMD(TESTMODE_CTRL)`, and restores normal test/PM state when switching back. The dump path accepts only one callback iteration, validates running/monitor/testmode state, sends either `MCU_UNI_QUERY(TESTMODE_CTRL)` or `MCU_UNI_QUERY(TESTMODE_RX_STAT)` based on the padding command selector, copies 512 bytes from the event payload, and emits `MT7925_TM_ATTR_RSP`.

## State And Persistence
State includes `phy->test.state`, `pm->enable`, pending PM work, and firmware testmode state. Query responses are transient SKBs. Testmode deliberately forces full-power driver ownership while active.

## Dependencies And Integration Points
The file depends on mac80211 testmode plumbing, mt76 testmode policies, nested netlink parsing, MT7925 MCU command IDs and RF test command structures, and MT792x PM ownership helpers.

## Risks
The query path uses a fixed 512-byte copy from `skb->data + 8`; firmware response size assumptions must hold. Entering testmode disables PM and cancels work, so failed transitions can leave PM/test state inconsistent. The command selector is read from raw padding bytes, which is ABI-sensitive. Requiring monitor mode prevents accidental use but can surprise tooling.

## Test Signals
Netlink set/query commands in monitor mode, transition to test and back to normal mode, PM reenable after normal transition, firmware response lengths, invalid attribute rejection, and single-dump iteration behavior validate this file.

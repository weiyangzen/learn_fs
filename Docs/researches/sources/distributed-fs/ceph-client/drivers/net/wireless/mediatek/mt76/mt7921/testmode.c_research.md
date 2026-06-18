# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/testmode.c

Purpose: cfg80211/mac80211 vendor testmode bridge for MT7921 RF test commands and queries. It exposes driver-private set/query netlink attributes and translates them into firmware test-control commands.

Important APIs/types/functions: `mt7921_testmode_cmd()` handles set operations; `mt7921_testmode_dump()` handles one-shot query dumps; `mt7921_tm_set()` switches normal/test/ICAP-like RF modes and sends `MCU_CE_CMD(TEST_CTRL)`; `mt7921_tm_query()` sends a query and copies `param0`/`param1` from `mt7921_rftest_evt`.

Control flow: entry points require the phy to be running, monitor mode enabled, and for dumps, mt76 testmode already enabled. Netlink data is parsed with mt76 testmode policy, then nested MT7921 driver data policy. Testmode switch disables PM and forces driver-own before enabling `MT76_TM_STATE_ON`; switching back to normal sends the command then clears test state and reenables PM.

State/persistence: modifies `phy->test.state`, `pm->enable`, and delayed/workqueue PM tasks. Firmware receives requested RF-test state, but no local durable configuration is stored.

Dependencies/integration: depends on cfg80211 testmode netlink, mt76 common testmode attributes, `mt76_mcu_send_msg()`, `mt76_mcu_send_and_get_msg()`, MT7921 RF-test command structures from `mcu.h`, and runtime PM helpers.

Risks: testmode is only reachable in monitor mode and returns `-ENOTCONN` otherwise. `mt7921_tm_query()` calls `dev_kfree_skb(skb)` on the `out` path even if send failed before assigning `skb`, which depends on compiler/control-flow assumptions and is worth auditing. Testmode disables power save, so failed normal-mode transitions can leave PM behavior altered.

Test signals: netlink policy validation, successful switch to RF test and back, query response formatting through `MT7921_TM_ATTR_RSP`, rejection outside monitor/running state, and PM restoration after normal mode.

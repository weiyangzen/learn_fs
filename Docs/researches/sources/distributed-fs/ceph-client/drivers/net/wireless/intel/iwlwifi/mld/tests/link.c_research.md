# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link.c

Purpose: Tests MLD missed-beacon handling around connection-loss decisions.

Important APIs and functions: Defines parameterized `missed_beacon_cases`, fake `ieee80211_connection_loss()`, and `test_missed_beacon()` which invokes `iwl_mld_handle_missed_beacon_notif()`.

Control flow: Each case creates a firmware missed-beacons notification packet, sets up either an EMLSR association or a non-MLO association, maps the firmware link ID, runs the notification handler under wiphy lock, and asserts whether association state was cleared by the fake connection-loss callback.

State and persistence: Per-test VIF association state is mutated to represent disconnect. No durable state.

Dependencies and integration points: Depends on production link notification handling, firmware MAC config notification layout, static stubbing of mac80211 connection loss, and common KUnit MLD setup helpers.

Risks: Current cases do not yet cover EMLSR-specific output despite the input field; a TODO notes ESR checks. The assertion uses association state as the observable proxy for connection loss.

Test signals: Covers below-threshold missed beacons, high total missed beacons with no since-last-RX loss, and disconnect when since-last-RX loss crosses threshold.

# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_sys.c

Purpose: exposes L2-only sysfs controls for BridgePort role/state/host notifications/reflected promiscuous mode and VNIC characteristics.

Important APIs and functions: `qeth_l2_attr_groups` publishes a BridgePort group and a `vnicc` group. BridgePort handlers call `qeth_bridgeport_allowed()`, `qeth_bridgeport_query_ports()`, `qeth_bridgeport_setrole()`, and `qeth_bridgeport_an_set()`. VNICC handlers convert attribute names with `qeth_l2_vnicc_sysfs_attr_to_char()` and call `qeth_l2_vnicc_get_state()`, `qeth_l2_vnicc_set_state()`, `qeth_l2_vnicc_get_timeout()`, and `qeth_l2_vnicc_set_timeout()`.

Control flow: BridgePort stores parse string or boolean values, lock `conf_mutex` and `sbp_lock`, reject conflicts with VNICC or learning_sync, optionally issue hardware commands if reachable, and otherwise cache desired settings. VNICC stores parse booleans or timeout values under `conf_mutex` and delegate policy and hardware checks to L2 main code.

State and persistence: sysfs stores update `card->options.sbp` and `card->options.vnicc`. Offline writes are cached in memory and applied by L2 online recovery where supported. There is no disk persistence.

Dependencies and integration: depends on L2 main exported functions, qeth card locks, sysfs device attributes, BridgePort hardware support, and VNICC IPA support. User-visible strings such as `n/a (VNIC characteristics)` and `n/a (BridgePort)` encode mutual exclusion state.

Risks: locking order (`conf_mutex` then `sbp_lock`) must stay consistent with notification work. Reflect-promisc deliberately forbids direct role manipulation once active. Attribute-name-to-character mapping returns zero for unknown names, so adding attributes requires updating the mapper.

Test signals: sysfs role/state read formatting, role write while offline and online, hostnotification uevents, reflect-promisc conflict with explicit role, VNICC attributes returning `n/a` on unsupported or BridgePort-active devices, timeout set/get, and invalid input handling.

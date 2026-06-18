# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2.h

Purpose: declares the layer 2 qeth discipline interface shared by L2 main code and L2 sysfs code.

Important APIs and types: exports `qeth_l2_attr_groups`, BridgePort operations (`qeth_bridgeport_query_ports()`, `qeth_bridgeport_setrole()`, `qeth_bridgeport_an_set()`), VNIC characteristic operations (`qeth_l2_vnicc_set_state()`, `qeth_l2_vnicc_get_state()`, `qeth_l2_vnicc_set_timeout()`, `qeth_l2_vnicc_get_timeout()`), and `qeth_bridgeport_allowed()`. `struct qeth_mac` is the cached multicast/unicast MAC entry with hash node and disposition flag.

Control flow: the header has no executable control flow beyond `qeth_bridgeport_is_in_use()`, which centralizes the test for active BridgePort role, reflected promiscuous mode, or host notification.

State and persistence: describes L2 runtime state stored in `struct qeth_card`: BridgePort options, VNIC characteristic options, and the `rx_mode_addrs` hash table entries represented by `struct qeth_mac`.

Dependencies and integration: depends on `qeth_core.h` for the core card model, enum definitions, and qeth disposition flags. It is consumed by `qeth_l2_main.c` and `qeth_l2_sys.c`.

Risks: `qeth_bridgeport_is_in_use()` is a policy gate used to enforce mutual exclusion. Any new BridgePort mode must update this helper or sysfs and VNICC can become simultaneously configurable in invalid combinations.

Test signals: compile coverage for L2 sysfs/main users, and behavior tests that enabling role, reflect-promisc, or host notification makes VNICC and learning_sync paths reject conflicting changes.

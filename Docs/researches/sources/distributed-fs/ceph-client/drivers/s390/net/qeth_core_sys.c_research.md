# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_sys.c

Purpose: implements the common qeth ccwgroup-device sysfs surface shared by layer 2 and layer 3 qeth disciplines. It exposes adapter identity, state, input-buffer sizing, recovery, layer selection, queueing policy, isolation, hardware trap, switch attributes, and BLKT timing knobs.

Important APIs and functions: `qeth_dev_groups` publishes three attribute groups; show/store handlers use `dev_get_drvdata()` to reach `struct qeth_card`. Key stores are `qeth_dev_portno_store()`, `qeth_dev_prioqing_store()`, `qeth_dev_bufcnt_store()`, `qeth_dev_layer2_store()`, `qeth_dev_isolation_store()`, `qeth_hw_trap_store()`, and `qeth_dev_blkt_store()`. Integration calls include `qeth_resize_buffer_pool()`, `qeth_schedule_recovery()`, `qeth_clone_netdev()`, `qeth_remove_discipline()`, `qeth_setup_discipline()`, `qeth_setadpparms_set_access_ctrl()`, `qeth_query_switch_attributes()`, and `qeth_hw_trap()`.

Control flow: read-only attributes format card fields with `sysfs_emit()`. Most writes parse user text with `kstrto*()` or `sysfs_streq()`, take `conf_mutex` or `discipline_mutex`, validate the card is down when changing structural parameters, then update cached card state or issue a hardware command if reachable. Layer switching clones a fresh netdev, removes the current discipline, frees the old netdev, and installs the requested discipline.

State and persistence: settings live in `struct qeth_card` fields such as `options.layer`, `options.isolation`, `qdio.do_prio_queueing`, `qdio.default_out_queue`, `qdio.in_buf_pool.buf_count`, `info.hwtrap`, and `info.blkt`. These are runtime kernel settings, not disk-persistent configuration; they persist for the live device instance and are replayed by normal qeth setup paths where relevant.

Dependencies and integration: depends on the qeth core model, ccwgroup device sysfs, netdevice flags/carrier state, qdio queue geometry, diag assist, and adapter parameters. It is the common control plane consumed by qeth L2/L3 modules and by userspace tools writing sysfs.

Risks: accepting changes only while down is critical because queue counts, port numbers, layer mode, and BLKT timing affect allocation and hardware setup. Layer switching is high risk because it swaps disciplines and netdev lifetime under `discipline_mutex`. `performance_stats` resets counters without per-counter locking, which is acceptable for statistics but can race with live updates. Hardware trap and isolation writes must keep cached state aligned with hardware command failures.

Test signals: sysfs read/write tests for accepted and rejected values, down-vs-up enforcement, layer switch between L2 and L3, buffer pool resize boundaries, recovery scheduling, isolation on unsupported card types, hw_trap arm/disarm/capture error paths, and switch attribute formatting for no hardware, unknown capabilities, and multiple capabilities.

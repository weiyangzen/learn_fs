## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.c

Purpose: implements the Adjunct Processor bus core for s390 crypto. It discovers AP cards/queues, exposes bus sysfs policy, schedules queue polling/interrupt processing, manages AP resource reservations, and provides exported services used by zcrypt, pkey, and VFIO AP.

Important APIs/types/functions: exported state includes `ap_domain_index`, `ap_max_msg_size`, `ap_queues`, `ap_perms`, `ap_attr_mutex`, and helpers such as `ap_init_apmsg()`, `ap_release_apmsg()`, `ap_get_qdev()`, `ap_driver_register()`, `ap_bus_force_rescan()`, `ap_parse_mask_str()`, `ap_hex2bitmap()`, `ap_wait_apqn_bindings_complete()`, `ap_owned_by_def_drv()`, `ap_test_config_usage_domain()`, `ap_sb_available()`, and `ap_is_se_guest()`.

Control flow: module init checks AP instruction support, initializes debug, message mempool, permissions, QCI data, bus/root devices, adapter interrupts, scan timer/work, and optional poll thread. Periodic or forced scans refresh QCI, notify drivers, select a default domain, walk adapters, create/remove/update card and queue devices, then emit init-scan and bindings-complete uevents. Queue work is driven by AP adapter interrupts, high-resolution poll timer, or optional poll thread; all call the tasklet, which iterates the queue hash and runs each queue state machine.

State and persistence: persistent global state includes masks, QCI current/old snapshots, scan counters, binding completion, queue hash, timers, tasklet, poll thread, interrupt registration, and root bus device. AP messages may use a preallocated mempool for no-IO allocation paths.

Dependencies and integration: depends on s390 AP instructions, QCI/APFT/QACT facilities, CHSC notifications, airq interrupts, Linux driver core/sysfs, and `ap_card`/`ap_queue` creation helpers.

Risks and test signals: risks are scan/mask races, reservation policy regressions, APQN reference handling, mempool exhaustion, and missed polling after interrupt reset. Test sysfs masks and relative mask parsing, QCI changes, AP hotplug/config changes, default domain selection, bindings completion, interrupt and timer polling modes, and no-memory pkey conversion paths.

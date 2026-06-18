# sources/distributed-fs/ceph-client/drivers/memstick/core/memstick.c

Purpose: This is the Sony MemoryStick core bus driver. It registers the `memstick` bus and host class, manages host IDs, card detection/removal, request dispatch/retry helpers, card identification, PM callbacks, and driver registration APIs used by MemoryStick block/media drivers and host controller drivers.

Important APIs/types/functions: Exported APIs include `memstick_detect_change()`, `memstick_next_req()`, `memstick_new_req()`, `memstick_init_req_sg()`, `memstick_init_req()`, `memstick_set_rw_addr()`, `memstick_alloc_host()`, `memstick_add_host()`, `memstick_remove_host()`, `memstick_free_host()`, `memstick_suspend_host()`, `memstick_resume_host()`, `memstick_register_driver()`, and `memstick_unregister_driver()`. Core objects include the global freezable `workqueue`, `memstick_host_idr`, `memstick_host_lock`, `memstick_bus_type`, and `memstick_host_class`.

Control flow: Module init creates the workqueue, registers the bus, and registers the host class. Host drivers allocate/add hosts, which get an ID, device name, class device, power off, and scheduled detection. `memstick_check()` runs on the workqueue under host lock: power on, stop existing card, allocate/probe a temporary card, set RW register address, read ID, compare with existing card, register new card or unregister removed/changed card, then power off if no card remains. Request processing is callback-driven through `card->next_request`; host drivers call `memstick_next_req()` after each transfer and retries are applied on errors.

State and persistence: Runtime state is in host/card structures, IDR allocation, request retry counters, completions, and the workqueue. Sysfs exposes card `type`, `category`, and `class`; uevents publish the same IDs. No persistent storage is used.

Dependencies and integration: Depends on `linux/memstick.h`, driver core bus/class APIs, IDR, workqueues, completions, runtime PM, and host driver callbacks (`request`, `set_param`). Block drivers bind through `struct memstick_driver` ID tables.

Risks and test signals: Risks include races between removal and detection, request completion timeouts, reference-count imbalance around probe/remove, and data corruption if suspend policy assumes media did not change. Test signals include card insertion/removal churn, request retry behavior, sysfs/uevent ID correctness, runtime PM balance, host remove during pending work, and suspend/resume redetection paths.

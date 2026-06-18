# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ccw.c

Purpose: binds zfcp to the s390 common I/O ccw bus, manages adapter references, handles online/offline/remove/notify/shutdown callbacks, and declares supported FCP device IDs.

Important APIs and functions: `zfcp_ccw_driver` is the registered ccw driver. Adapter reference helpers are `zfcp_ccw_adapter_by_cdev()` and `zfcp_ccw_adapter_put()`. Lifecycle callbacks include `zfcp_ccw_probe()`, `zfcp_ccw_remove()`, `zfcp_ccw_set_online()`, `zfcp_ccw_set_offline()`, `zfcp_ccw_notify()`, and `zfcp_ccw_shutdown()`. `zfcp_ccw_activate()` centralizes reopen, ERP wait, and port scan flush.

Control flow: probe defers allocation. First set-online enqueues an adapter, resets request numbering, activates ERP reopen, waits for random-backoff port scanning, then forces an unconditional scan for no-auto-rescan cases. Set-offline shuts down the adapter through ERP and waits. Remove sets the device offline, detaches unit and port device lists under locks, unregisters child devices, and unregisters the adapter. Notify maps CIO events to adapter shutdown or reopen.

State and persistence: adapter lifetime is tied to ccw device drvdata and kref references guarded by a spinlock. Online/offline transitions update adapter status through ERP helpers rather than directly freeing structures. Child port/unit lists are spliced for safe unregister outside locks.

Dependencies and integration: depends on s390 ccw bus IDs, CIO event types, zfcp ERP, FC port scan work, request-list invariants, and adapter allocation/unregister helpers from `zfcp_aux.c`.

Risks: reference management is central; missing `zfcp_ccw_adapter_put()` can leak adapters, while premature release can race ccw callbacks. `BUG_ON(!zfcp_reqlist_isempty())` assumes no outstanding requests on online. Remove must avoid unregistering child devices while still on shared lists. Notify returns 1 even when handled to indicate event processing to CIO.

Test signals: ccw online/offline cycles, first-online allocation and second-online reuse, CIO_GONE/NO_PATH/OPER/BOXED notifications, remove with populated ports/units, shutdown path, adapter kref under concurrent callbacks, and request-list empty invariant.

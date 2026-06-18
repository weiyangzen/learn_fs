# sources/distributed-fs/ceph-client/drivers/dca/dca-sysfs.c

Purpose: sysfs/class support for DCA providers and requesters.

Important APIs/types/functions: `dca_sysfs_add_req()`, `dca_sysfs_remove_req()`, `dca_sysfs_add_provider()`, `dca_sysfs_remove_provider()`, `dca_sysfs_init()`, `dca_sysfs_exit()`, global `dca_class`, `dca_idr`, and `dca_idr_lock`.

Control flow and state: provider registration allocates an ID from `idr`, creates `/sys/class/dca/dcaN` under the provider device, and stores the class device in `dca->cd`. Requester registration creates `requesterN` child class devices using slot-derived minor numbers. Removal unregisters/destroys class devices and releases IDR entries. Init registers the class after initializing IDR/spinlock.

Dependencies and integration: depends on device class APIs, IDR, spinlocks, DCA core structs, and sysfs helper calls from `dca-core.c`.

Risks and test signals: requester minor collisions, static `req_count` naming, provider ID rollback on device_create failure, and synchronization with DCA core locks are risks. Test provider add/remove loops, requester add/remove slots, class registration failure, ID reuse, and cleanup after core unregisters all providers.

# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i_init.c

## Purpose

`bnx2i_init.c` owns module-level lifecycle and adapter registration for the bnx2i iSCSI offload driver. It registers the libiscsi transport and CNIC ULP, creates per-CPU completion threads, handles CNIC start/stop/init/exit callbacks, tracks adapters globally, and exposes module parameters.

## Important APIs, Types, and Functions

Exported or callback functions include `bnx2i_identify_device()`, `get_adapter_list_head()`, `bnx2i_find_hba_for_cnic()`, `bnx2i_start()`, `bnx2i_stop()`, `bnx2i_ulp_init()`, `bnx2i_ulp_exit()`, and `bnx2i_get_stats()`. Internal helpers include `bnx2i_chip_cleanup()`, `bnx2i_init_one()`, `bnx2i_cpu_online()`, `bnx2i_cpu_offline()`, `bnx2i_mod_init()`, and `bnx2i_mod_exit()`.

Global state includes `adapter_list`, `adapter_count`, `bnx2i_dev_lock`, module parameters for event coalescing, delayed ACK, error masks, SQ/RQ sizes, `iscsi_error_mask`, the per-CPU `bnx2i_percpu` storage, and the CPU hotplug state handle.

## Control Flow

Module init prints the version, normalizes `sq_size`, registers the bnx2i iSCSI transport, registers the CNIC iSCSI ULP callbacks, initializes per-CPU work lists, and registers CPU hotplug callbacks that start `bnx2i_thread/%d` completion threads. Module exit removes adapters, unregisters CNIC devices, frees HBAs, removes CPU hotplug state, and unregisters transport/CNIC driver.

CNIC calls `bnx2i_ulp_init()` for devices; it allocates an HBA, identifies PCI/device state through `bnx2i_init_one()`, registers with CNIC, and links the adapter into `adapter_list`. `bnx2i_start()` sends firmware iSCSI init and polls up to about one second for `ADAPTER_STATE_UP` or init failure. `bnx2i_stop()` sets going-down state, drops all sessions, waits for offload/destroy lists and active connections to drain, performs chip cleanup if needed, and clears adapter up/down bits.

## State and Persistence Behavior

The file stores runtime adapter and module state only. Adapter registration state persists while the module is loaded or the CNIC device remains present. Per-CPU threads persist while CPUs are online. Module parameters persist for the module lifetime and affect firmware init, queue sizing, delayed ACK, coalescing, and error classification.

## Dependencies and Integration Points

It integrates with libiscsi transport registration, CNIC ULP registration, CPU hotplug, kthreads, netdev/CNIC device lifetimes, PCI IDs, HBA allocation/free in `bnx2i_iscsi.c`, and hardware init/cleanup in `bnx2i_hwi.c`. Stats are copied to CNIC-provided stats memory.

## Risks and Edge Cases

The adapter list is global and must remain protected by `bnx2i_dev_lock`. Stop paths must handle absent or slow user-space iSCSI daemon cleanup by forcefully disconnecting hardware endpoints. CPU offline drains queued completion work inline before stopping the thread, but new queueing must be blocked first. Module exit ordering unregisters transport before CNIC driver in init failure paths but the normal exit unregisters CNIC after transport removal, so lifetime assumptions across callbacks need care. Firmware init can fail when downloaded firmware lacks iSCSI support.

## Test Signals

Validate module load/unload, CNIC device hotplug, duplicate registration failures, firmware init success and license/init failure, network down cleanup with active sessions, per-CPU thread creation/removal, CPU hotplug while completions are queued, stats retrieval, module parameter effects, and absence of adapter/HBA leaks after CNIC exit.

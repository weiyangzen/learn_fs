# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/init.c

## Purpose
`init.c` initializes the core `struct ishtp_device` software state and starts post-HBM ISHTP processing. It is the common setup code used after a low-level ISH/IPC device allocates its `ishtp_device`.

## Important APIs, types, and functions
`ishtp_device_init()` initializes device state, lists, locks, wait queues, FIFO cursors, the HBM bottom-half work item, host-client bitmap reservation, and firmware-loader work. `ishtp_start()` waits for HBM startup and sends a system-state subscriber query.

## Control flow and integration points
Initialization sets `dev_state = ISHTP_DEV_INITIALIZING`, prepares `cl_list`, `device_list`, `read_list`, locks, HBM receive FIFO, and wait queues. It reserves host client ID 0 for HBM traffic. It also uses `devm_work_autocancel()` so `work_fw_loader` is canceled automatically with the device. `ishtp_start()` is called after the low-level transport has initiated HBM negotiation; it waits through `ishtp_hbm_start_wait()` and then calls `ishtp_query_subscribers()`.

## State and persistence behavior
All state is in-memory per `ishtp_device`. The function establishes initial list/lock/bitmap state but does not allocate firmware clients or persistent storage. Managed loader work lifetime is tied to `dev->devc`.

## Dependencies
This file depends on HBM work/queries, client constants, loader work, Linux device-managed helpers, lists, spinlocks, wait queues, and workqueues. Low-level IPC drivers call into it after allocating the ISHTP device.

## Risks and edge cases
If `devm_work_autocancel()` fails, the code logs but leaves the device otherwise initialized, so later loader-capable firmware may not load correctly. `ishtp_start()` moves to disabled on HBM timeout. Initialization assumes caller has zeroed or otherwise allocated a valid flexible `struct ishtp_device` and installed low-level ops before HBM traffic starts.

## Test signals
Probe success/failure, HBM start timeout, loader-work managed cleanup, host client ID reservation, repeated init after reset paths, and lockdep/KASAN around early interrupt reception are useful signals.

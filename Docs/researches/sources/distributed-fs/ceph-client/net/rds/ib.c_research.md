# sources/distributed-fs/ceph-client/net/rds/ib.c

## Purpose
`ib.c` registers and manages the RDS InfiniBand transport. It tracks IB devices, allocates protection domains and MR pools, validates local addresses, exposes IB connection info, and registers the `rds_ib_transport` callbacks with the RDS core.

## Important APIs, Types, And Functions
Important globals are `rds_ib_devices`, `rds_ib_devices_lock`, `rds_ib_client`, `ib_nodev_conns`, and `rds_ib_transport`. Main functions include `rds_ib_add_one()`, `rds_ib_remove_one()`, `rds_ib_get_client_data()`, `rds_ib_dev_put()`, `rds_ib_laddr_check()`, `rds_ib_laddr_check_cm()`, `rds_ib_init()`, and `rds_ib_exit()`. Helper paths include nodev reconnect, device shutdown/free, info visitors, and unload state checks.

## Control Flow
When the IB core adds a device, RDS accepts only IB channel adapters with memory-management extensions. It allocates `rds_ib_device`, initializes locks/lists/refcount/free work, records hardware limits and ODP capability, allocates completion-vector load tracking, protection domain, and 1M/8K MR pools, adds the device to the global RCU list, stores IB client data, and retries connections that were waiting without a device.

Device removal drops active connection paths, clears IB client data, removes the device from the global list, waits for RCU readers, and drops references so deferred free tears down MR pools, PD, IP list, vector load, and device state. Address validation restricts RDS/IB to `init_net`, checks IPv4-mapped addresses against known RDS IB devices, otherwise uses RDMA CM bind checks and special IPv6 link-local validation. Init initializes MR support, registers the IB client, sysctls, receive path, transport, and info callbacks; exit reverses this with an unloading flag and RCU grace period.

## State And Persistence
State includes global device list, per-device refcounts, IP address list, connection list, MR pools, PD, hardware limits, vector load counters, and unloading flag. It is volatile and tied to IB device/module lifetimes.

## Dependencies And Integration Points
This file integrates with the RDMA/IB client API, RDMA CM address binding, RDS transport registration, MR pool code, receive/sysctl/stats/info subsystems, and connection management in `connection.c`/`ib_cm.c`.

## Risks
Device removal races with incoming connections and MR fast paths; RCU plus refcounts protect client data and list readers. MR pool sizing depends on device limits and module parameters. Address validation currently treats RDS/IB as not network-namespace aware. Vector load accounting must be balanced by connection setup/teardown. Deferred device free relies on `rds_wq` flushing during unregister.

## Test Signals
Coverage should include unsupported device rejection, MR pool allocation failure unwind, client-data ref behavior during remove, nodev connection retry after device add, laddr checks for IPv4, IPv6, link-local scope, non-init-net rejection, info export for up/down IB connections, and init/exit failure unwind at each stage.

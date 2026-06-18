# sources/distributed-fs/ceph-client/drivers/net/netdevsim/dev.c

## Purpose
This file implements most of the device-level netdevsim/devlink simulation: devlink allocation and registration, resources, parameters, regions, reload, flash update, traps, rate objects, ports, VF/switchdev behavior, debugfs controls, FIB/health/BPF/psample/hwstats integration, and driver probe/remove paths behind the synthetic bus.

## Important APIs, Types, and Functions
Major functions include `nsim_drv_probe()`, `nsim_drv_remove()`, `nsim_dev_reload_create()`, `nsim_dev_reload_destroy()`, `__nsim_dev_port_add()`, `__nsim_dev_port_del()`, `nsim_drv_port_add()`, `nsim_drv_port_del()`, `nsim_drv_configure_vfs()`, `nsim_dev_resources_register()`, `nsim_dev_traps_init()`, `nsim_dev_traps_exit()`, `nsim_dev_flash_update()`, and `nsim_dev_init()/nsim_dev_exit()`. `nsim_dev_devlink_ops` wires devlink callbacks for eswitch mode, reload, info, flash, traps, policers, rates, and drop counters. Debugfs file operations provide snapshot creation, trap flow action cookie injection, and `max_vfs` mutation.

## Control Flow
Probe allocates a devlink instance in the bus device's initial net namespace, initializes `struct nsim_dev`, stores bus drvdata, allocates VF configs, registers devlink, resources, params, dummy region, traps, debugfs, FIB, health, BPF offload device, psample, hwstats, and initial PF ports. Port add registers a devlink port with physical or PCI VF attributes, optional PF resource, debugfs directory, creates the netdevsim netdev via `nsim_create()`, optionally creates a devlink rate leaf, and links it into `port_list`. Switchdev mode creates VF ports for configured VFs; legacy mode destroys VF ports and rate nodes. Reload down destroys the reloadable parts unless debugfs forbids it; reload up recreates them unless debugfs forces failure. Trap work periodically reports generated UDP packets for running ports and enabled traps under the devlink lock. Remove reverses reloadable state, exits BPF/debugfs/params/resources, unregisters devlink, frees VF configs and flow action cookie, and releases the devlink object.

## State and Persistence
State is runtime-only but widely exposed through debugfs and devlink. Persistent-in-memory fields include port list, switch id, eswitch mode, VF configs, reload failure flags, firmware update controls, max MAC/test params, dummy region snapshots, trap action/counter state, flow action cookie, rate parent names and bandwidth values, FIB data, and feature subsystem state. Devlink driverinit parameters can be staged and loaded on reload. Delayed trap work persists while traps are initialized and must be canceled before unregistering trap structures.

## Dependencies and Integration Points
The file integrates with devlink, debugfs, rtnetlink/devlink locking, netdevsim netdev creation in `netdev.o`, FIB resource accounting, health reporters, BPF offload setup, psample, hardware stats, UDP tunnel simulation, flow action cookies, SKB construction, and bus device lifecycle from `bus.c`. It also creates the top-level debugfs directory used by other netdevsim files.

## Risks and Edge Cases
Error unwinding is long and must maintain exact reverse order for devlink, debugfs, delayed work, and subsystem registrations. Trap report work requeues itself and takes the devlink lock; teardown cancels it before unregistering traps. Reload destroy skips work if devlink is in reload-failed state, changing cleanup expectations. `max_vfs` can only change when no VFs are configured and is bounded by the VF port index range. Switching to switchdev with VF creation failures rolls back already-created VF ports. Rate values must be exact 1 Mbps units and under 5000 Mbps. Debugfs-controlled failure knobs intentionally create negative paths for tests.

## Test Signals
Validation should exercise bus probe/remove, devlink resource and parameter visibility, dummy region snapshots, reload success/failure/forbidden paths, flash update status notifications, trap action/group/policer operations and counters, switchdev/legacy mode transitions, VF configuration, PF/VF port add/delete, rate leaf/node operations, max_vfs changes, and subsystem cleanup under module unload. Selftests should check debugfs knobs cause expected extack errors.

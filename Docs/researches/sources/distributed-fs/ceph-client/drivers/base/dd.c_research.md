# sources/distributed-fs/ceph-client/drivers/base/dd.c

## Purpose
`dd.c` owns core driver/device binding and unbinding. It handles deferred probe, async probing, driver override, sysfs bind links, coredump hooks, device links, PM ordering, and cleanup after failed or successful probe/remove paths.

## Important APIs, Types, And Functions
Important exported APIs include `driver_deferred_probe_add()`, `driver_deferred_probe_del()`, `driver_deferred_probe_trigger()`, `device_block_probing()`, `device_unblock_probing()`, `driver_deferred_probe_check_state()`, `device_bind_driver()`, `wait_for_device_probe()`, `device_attach()`, `device_initial_probe()`, `device_driver_attach()`, `driver_attach()`, `device_release_driver()`, `device_driver_detach()`, and `driver_detach()`. State includes deferred pending/active lists, `deferred_probe_work`, `deferred_trigger_count`, `initcalls_done`, `defer_all_probes`, async probe command-line state, and `probe_count`.

## Control Flow, State, And Persistence
Probe moves through match, runtime-PM supplier/parent get, supplier link checks, `device_set_driver()`, pinctrl/DMA setup, sysfs link creation, PM-domain activation, bus or driver probe, driver groups, optional `state_synced`, and final `driver_bound()`. Probe errors unwind sysfs, DMA, links, devres, PM domain, driver data, and runtime PM. Deferred probes are queued on pending lists, promoted to active on successful binds, and retried by workqueue; initcall timeout forces final retries and warnings.

## Dependencies, Integration Points, Risks, And Test Signals
This file integrates buses, drivers, device links, fw_devlink, runtime PM, pinctrl, DMA ops, PM domains, debugfs, async core, kobjects, and devcoredump. Risks include lock ordering with parent locks, asynchronous probe races, deferred trigger races, positive-vs-negative probe errno conventions, cleanup ordering, and deadlock if remove recursively releases its own device. Test signals include deferred probe timeout behavior, async-probe command line, supplier link deferral, failed probe unwind, bind/unbind uevents and links, `CONFIG_DEBUG_TEST_DRIVER_REMOVE`, and suspend-safe probe blocking.

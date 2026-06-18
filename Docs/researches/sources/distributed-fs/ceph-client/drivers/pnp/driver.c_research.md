<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/driver.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/driver.c

Purpose: PnP bus driver matching, probe/remove, suspend/resume, modalias generation, and public driver registration helpers.

Important APIs/types/functions: `compare_pnp_id()` implements wildcard matching with `X` in the last four ID chars and `ANYDEVS`. `pnp_device_attach/detach()` serialize status transitions. `pnp_device_probe/remove/shutdown()`, `pnp_bus_match()`, `pnp_uevent()`, `pnp_bus_dev_pm_ops`, `pnp_bus_type`, `dev_is_pnp()`, `pnp_register_driver()`, `pnp_unregister_driver()`, and `pnp_add_id()` are central.

Control flow: bus match checks driver ID table against device IDs. Probe attaches a ready device, auto-activates it unless driver asks not to change resources, optionally disables active devices for `PNP_DRIVER_RES_DISABLE`, then calls driver probe and records `pnp_dev->driver`. Remove calls driver remove, optionally disables active resources, and detaches. Suspend calls driver PM, driver legacy suspend, stops writable/disable-capable devices, then protocol suspend. Resume reverses via protocol resume, start, driver PM resume, and legacy resume.

State/persistence: `pnp_dev->status` tracks READY vs ATTACHED. `pnp_dev->active` is changed by manager/protocol operations. ID lists persist and feed modalias emission.

Dependencies/integration: Linux driver core, PM core, PnP manager activation APIs, protocol callbacks, and module autoload through `MODALIAS=pnp:d<ID>`.

Risks: probe failure after auto-activation detaches but does not explicitly undo activation in all paths. Suspend comments indicate `can_write` is required to restart on resume; protocol capability mistakes can leave devices stopped. ID comparison expects exactly seven-character PnP IDs.

Test signals: wildcard ID matching, driver flags controlling resource changes, suspend/resume with protocol callbacks, failed probe cleanup, and uevent modalias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/driver.c -->

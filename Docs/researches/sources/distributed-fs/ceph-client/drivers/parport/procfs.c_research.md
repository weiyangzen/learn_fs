# sources/distributed-fs/ceph-client/drivers/parport/procfs.c

Purpose: provides sysctl/proc integration for parport defaults, per-port attributes, active device reporting, per-device timeslice tuning, and IEEE1284 autoprobe data.

Important APIs/types/functions: `parport_proc_register()` and `parport_proc_unregister()` manage `dev/parport/<port>` and `dev/parport/<port>/devices`; `parport_device_proc_register()` and unregister create per-pardevice `timeslice`; default registration is done by `subsys_initcall(parport_default_proc_register)`. Read handlers include `do_active_device()`, hardware base/irq/dma/modes handlers, and `do_autoprobe()` under `CONFIG_PARPORT_1284`.

Control flow/state: templates are duplicated per port/device, populated with port pointers, `spintime`, `timeslice`, and `probe_info` references, then registered with dynamically built sysctl paths. Defaults are backed by global `parport_default_timeslice` and `parport_default_spintime`, bounded by min/max constants. If sysctl or procfs is disabled, stubs return success and only initialize/exit the parport bus.

Dependencies/integration: depends on `CONFIG_SYSCTL`, `CONFIG_PROC_FS`, parport bus init/exit, sysctl registration, and parport core fields. Risks include registration unwind ordering, dynamic path allocation failure, proc handler buffer truncation, and stale pointers if unregister does not clear tables before freeing. Test signals include sysctl tree presence, writable bounded defaults, readable base/irq/dma/modes/autoprobe, and clean unregister on port/device removal.

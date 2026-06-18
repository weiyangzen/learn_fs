# sources/distributed-fs/ceph-client/drivers/scsi/scsi_dh.c

Purpose: implements SCSI device-handler registration and attachment. Device handlers provide array/path-management behavior such as ALUA, EMC, HP active/passive, or RDAC handling and are used by multipath and the SCSI midlayer to activate paths, set handler parameters, and interpret sense.

Important APIs/types/functions: `scsi_dh_blist[]` maps vendor/model prefixes to handler module names; `scsi_dh_find_driver()` prefers ALUA when target port group support is advertised. `scsi_register_device_handler()` and `scsi_unregister_device_handler()` maintain the global `scsi_dh_list`. `scsi_dh_add_device()` auto-attaches a known handler during device setup, while `scsi_dh_attach()`, `scsi_dh_activate()`, `scsi_dh_set_params()`, and `scsi_dh_attached_handler_name()` operate from a `request_queue`.

Control flow: lookup first scans registered handlers under `list_lock`; explicit attach can call `request_module("scsi_dh_%s")` and retry. Attach pins the handler module, calls its `attach()` method, maps `SCSI_DH_*` errors to Linux errno values, and stores `sdev->handler` on success. Release calls handler `detach()` and drops the module reference. Queue-based exported APIs resolve `struct scsi_device` through `scsi_device_from_queue()`, validate device state, call handler methods, then release the device reference.

State and persistence: persistent state is in-memory only: the registered handler list and `sdev->handler` pointers with module references. There is no disk state, but handler attachment changes live path-management behavior for the device.

Dependencies and integration: integrates with `scsi_lib.c` for queue-to-device resolution and with handler modules under `drivers/scsi/device_handler/`. Device handlers are called from request preparation, sense processing, multipath activation, and sysfs/dm paths.

Risks: handler name matching uses `strncmp(tmp->name, name, strlen(tmp->name))`, so prefix ambiguity must be avoided. Unregister removes a handler from the list but live devices rely on module references from attachment. Callback completion for `activate()` may run synchronously, so callers must not hold locks needed by completion.

Test signals: register/unregister each handler module, auto-attach by TPGS and by vendor/model blacklist, explicit attach to an already handled device, invalid handler name, activation on offline/cancelled devices, parameter setting, and module unload while devices are attached.

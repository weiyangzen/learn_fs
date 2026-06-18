# sources/distributed-fs/ceph-client/drivers/tee/optee/core.c

## Purpose
`core.c` provides OP-TEE module initialization, common context lifecycle, device enumeration, RPMB integration, sysfs attributes, revision reporting, and shared removal logic used by both SMC and FF-A transports.

## Important APIs, Types, And Functions
`optee_get_revision()` formats the OP-TEE OS revision stored in `optee->revision`. `optee_open()` allocates per-context session state and has special handling for the privileged supplicant TEE device: only one supplicant context may be active, and first open schedules device enumeration. `optee_release()` and `optee_release_supp()` close all sessions through `optee_release_helper()`, with the supplicant release also aborting pending supplicant RPCs.

`optee_enumerate_devices()` opens a client context, opens the device-enumeration PTA, queries device UUIDs with `PTA_CMD_GET_DEVICES*`, allocates a kernel buffer for the returned UUID list, and registers `tee_client_device` instances on `tee_bus_type`. `optee_unregister_devices()` removes registered `optee-ta-*` devices. `optee_bus_scan_rpmb()` and `optee_rpmb_intf_rdev()` rescan RPMB-dependent devices when RPMB devices appear. `optee_set_dev_group()` attaches sysfs groups showing RPMB routing model.

`optee_remove_common()` performs transport-independent teardown: unregister RPMB notifier, cancel work, unregister TEE client devices, uninitialize notifications and SHM arg cache, close internal context, unregister both TEE devices, free pool, uninit supplicant, destroy call queue/RPMB mutex, and drop the current RPMB device.

`optee_core_init()` avoids kdump kernels, registers an RPMB class interface when reachable, registers SMC and FF-A ABI backends, and keeps the module only if at least one backend succeeds. `optee_core_exit()` unregisters successful backends and RPMB interface.

## Control Flow And State
Global module state records SMC and FF-A registration results and whether the RPMB interface is registered. Per OP-TEE instance, context/session state is initialized by the backend probe and then managed by common open/release paths. Device enumeration is lazy for supplicant-dependent TAs and can also be triggered by RPMB notifier work for RPMB-dependent TAs.

## Dependencies And Integration Points
This file integrates with Linux module init/exit, TEE core devices, TEE client bus, RPMB class interfaces, notifier chains, sysfs device groups, workqueues, and both ABI registration functions. It calls common operations implemented in `call.c`, `notif.c`, `supp.c`, and backend files.

## Risks
`optee_remove_common()` assumes backends initialized fields in the expected order; partial-probe error paths must avoid calling it too early. Device enumeration treats missing PTA as success but propagates registration errors, so one failing client device can abort backend probe. Supplicant singleton enforcement means leaked `optee->supp.ctx` blocks future supplicant opens. RPMB routing model is visible to userspace and must match actual in-kernel versus supplicant routing behavior.

## Test Signals
Probe on systems with only SMC, only FF-A, both, and neither backends. Test kdump-kernel refusal. Verify supplicant open exclusivity and release aborts pending RPCs. Exercise device enumeration PTAs with zero devices, short-buffer retry, storage-not-available, and registration failure. Hot-add RPMB devices and confirm RPMB-dependent device scan work runs once successfully.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.c

## Purpose

`sierra_ms.c` handles Sierra Wireless TRU-Install devices that expose a mass-storage image before modem operation. It decides whether to keep storage mode or switch to modem mode based on a module parameter and device-reported SWoC package information.

## Important APIs, Types, and Functions

`struct swoc_info` models the vendor control response containing revision, Linux SKU, and version. `containsFullLinuxPackage()` classifies SKU ranges that contain a full Linux package. `sierra_set_ms_mode()` sends the vendor SetSwocMode control request. `sierra_get_swoc_info()` reads SWoC info and endian-converts fields. `truinst_show()` exposes current info through a read-only sysfs attribute. `sierra_ms_init()` is the unusual-device init hook.

## Control Flow

Initialization checks `swi_tru_install`. Force-modem mode sends SetSwocMode(Modem) and returns `-EIO` to stop storage binding. Force-mass-storage mode skips switching and creates the `truinst` sysfs file. Normal mode allocates `swoc_info`, retries GetSwocInfo up to three times with 2-second sleeps, logs decoded values, and switches to modem mode if the device lacks a full Linux package. Otherwise it keeps storage mode and creates the sysfs attribute.

## State and Persistence Behavior

The driver keeps no per-device private state after init. The module parameter controls policy. A successful vendor request changes device mode and usually causes re-enumeration. The sysfs file performs fresh control reads on demand rather than returning cached state.

## Dependencies and Integration Points

It depends on USB vendor control messages, usb-storage unusual init flow, module parameters, sysfs device attributes, SCSI includes from the surrounding storage stack, and `sierra_ms.h` for the exported initializer declaration.

## Risks and Test Signals

Risks include no cleanup path for the created `truinst` attribute in this file, fixed SKU policy ranges, returning `-EIO` even after intentional successful modem switching, and sleeping retries during probe. Tests should cover all module parameter modes, SWoC query failures and retries, endian conversion, SKU boundaries, sysfs output after probe, and device re-enumeration after forced or policy-driven switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/sierra_ms.c -->

# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Kconfig

## Purpose
Declares shared guest-side TSM support symbols.

## APIs, Types, and Functions
`TSM_GUEST` is a base bool. `TSM_REPORTS` is a tristate selecting `TSM_GUEST` and `CONFIGFS_FS`. `TSM_MEASUREMENTS` is a bool selecting `TSM_GUEST` and `CRYPTO_HASH_INFO`.

## Control Flow and State
Build-time only. It gates the configfs attestation report frontend and sysfs measurement-register helper.

## Dependencies and Integration
SEV, TDX, and Arm CCA providers select `TSM_REPORTS`; TDX selects measurements.

## Risks and Test Signals
The line `select CONFIGFS_FS` is unusual because Kconfig select targets are typically bare symbol names; build validation should confirm the tree accepts it as intended. Test all vendor providers that depend on this shared layer.

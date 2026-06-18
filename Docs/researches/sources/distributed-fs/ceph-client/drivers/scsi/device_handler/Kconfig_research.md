<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Kconfig

Purpose: declares the SCSI device-handler configuration menu and the individual multipath hardware-handler symbols for RDAC, HP/Compaq MSA, EMC CLARiiON, and generic SPC-3 ALUA devices.

Important APIs/types/functions: Kconfig symbols are `SCSI_DH`, `SCSI_DH_RDAC`, `SCSI_DH_HP_SW`, `SCSI_DH_EMC`, and `SCSI_DH_ALUA`. `SCSI_DH` is a boolean parent depending on `SCSI`; each implementation symbol is tristate and depends on both `SCSI_DH` and `SCSI`.

Control flow: there is no runtime flow. At configuration time, enabling `SCSI_DH` exposes the handler choices; each tristate decides whether the matching `scsi_dh_*.c` object is built in, built as a module, or omitted.

State and persistence: state is the kernel `.config` selection. The chosen symbols persist in build artifacts and determine which handlers can be registered with the SCSI device-handler core.

Dependencies and integration: integrates the device-handler directory into the SCSI Kconfig hierarchy. The handlers are intended for dm-multipath style path management where vendor-specific failover commands and `prep_fn` access-state filtering are needed.

Risks: missing or too-weak dependencies surface as compile failures or handlers that can be configured without the SCSI device-handler core. Since `SCSI_DH` defaults to `n`, distributions must intentionally enable it or multipath hardware handlers will be unavailable.

Test signals: Kconfig coverage with `allmodconfig`, `allyesconfig`, and `SCSI=n`; module build checks for each handler; runtime `scsi_register_device_handler()` success when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Kconfig -->

# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/devlink.c

## Purpose
`devlink.c` implements devlink operations and parameters for the AMD/Pensando core driver. It exposes runtime enablement for supported VIF/client types, firmware flash update, firmware/device version reporting, serial number reporting, and devlink health diagnosis for firmware state.

## Important APIs, Types, And Functions
`pdsc_dl_enable_get`, `pdsc_dl_enable_set`, and `pdsc_dl_enable_validate` back the generic `enable_vnet` devlink parameter. `pdsc_dl_flash_update` delegates devlink firmware flashing to `pdsc_firmware_update`. `pdsc_dl_info_get` reports stored firmware slot versions, running firmware version, ASIC id/revision, and serial number. `pdsc_fw_reporter_diagnose` emits firmware health state, generation, and recovery count. `pdsc_dl_find_viftype_by_id` maps a devlink parameter id to a `pdsc_viftype` entry.

## Control Flow
Devlink parameter get finds a matching VIF type in `pdsc->viftype_status` and returns its enabled state. Set validates support, short-circuits if unchanged, stores the new enablement, then iterates existing VFs to add or delete vDPA auxiliary devices. Validate rejects unsupported or absent VIF types. Firmware flash update is a thin call into `fw.c`.

Info get sends `PDS_CORE_FW_GET_LIST` through the devcmd path while holding `devcmd_lock`, copies the firmware list out of the command data window, reports known slot names (`fw.goldfw`, `fw.mainfwa`, `fw.mainfwb`) or generated slot names, then reports running firmware, ASIC id/rev, and serial. The health reporter takes `config_lock`, classifies state as dead, unhealthy, or healthy using `PDSC_S_FW_DEAD` and `pdsc_is_fw_good`, then appends numeric state, generation, and recovery counters.

## State And Persistence
Runtime state is in `pdsc->viftype_status`, `pdsc->num_vfs`, `pdsc->vfs[]`, `pdsc->dev_info`, firmware command data, `fw_status`, `fw_generation`, and `fw_recoveries`. Devlink parameters are runtime-mode only; this file does not persist settings across reloads.

## Dependencies And Integration Points
It integrates with devlink core, devlink params, devlink info API, devlink health reporters, auxiliary-device creation/deletion from `auxbus.c`, firmware update from `fw.c`, and device command locking from `dev.c`. The actual devlink ops and params are registered by `main.c`.

## Risks
`pdsc_dl_enable_set` updates the enabled flag before iterating VFs; if adding an aux device fails partway through, earlier VFs may have changed while the function returns an error. The function does not explicitly take `config_lock`; auxbus helpers take it per add/delete, so multi-VF transitions are not atomic. Firmware info reads share the devcmd data window and must keep locking discipline. Health diagnosis reads firmware status while holding `config_lock`, which must remain compatible with reset and recovery paths.

## Test Signals
Use `devlink dev info`, `devlink dev param show/set enable_vnet`, `devlink health show/diagnose`, and `devlink dev flash` on supported hardware. Validate unsupported VIF behavior, VF aux-device creation/deletion after toggles, firmware slot list sizes beyond named slots, and health reporter state during forced firmware down/up recovery.

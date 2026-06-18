# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecards.c

## Purpose
`core_linecards.c` is the central line-card manager for modular mlxsw systems. It discovers available slots, parses optional line-card INI bundle firmware, exposes devlink linecard operations, transfers INI data to hardware, tracks provisioned/ready/active state, dispatches active/inactive notifications to other subsystems, and supports firmware flashing of flashable devices on active line cards.

## Important APIs, Types, and Functions
- `struct mlxsw_linecard_ini_file` models one INI blob in the `NVLCINI+` bundle. `struct mlxsw_linecard_types_info` owns the firmware buffer and parsed pointer table.
- Firmware flash support is implemented through `struct mlxsw_linecard_device_fw_info` and `mlxsw_linecard_device_dev_ops`, adapting mlxsw `MDDT` register accesses to the generic `mlxfw` FSM callbacks.
- Public functions include `mlxsw_linecard_flash_update()`, `mlxsw_linecard_devlink_info_get()`, `mlxsw_linecards_event_ops_register()`, `mlxsw_linecards_event_ops_unregister()`, `mlxsw_linecards_init()`, and `mlxsw_linecards_fini()`.
- Devlink linecard callbacks are `mlxsw_linecard_provision()`, `mlxsw_linecard_unprovision()`, `mlxsw_linecard_same_provision()`, `mlxsw_linecard_types_count()`, and `mlxsw_linecard_types_get()`.
- Event listeners use `DSDSC` for slot status and `BCTOE` for INI/BCT operation events, queueing work items that process copied register payloads outside interrupt context.

## Control Flow
Initialization queries `MGPIR` for slot count and exits early on non-modular systems. For modular systems it allocates `struct mlxsw_linecards`, optionally loads `mellanox/lc_ini_bundle_<minor>_<subminor>.bin`, registers traps and IRQ event handling, sets the core linecards pointer, creates one devlink linecard per slot, and enables event delivery per slot. Provisioning erases current INI, transfers the selected INI in `MBCT` chunks, schedules a timeout for the expected provision status event, and activates the image. Hardware status events call `mlxsw_linecard_status_process()`, which serializes on the linecard lock and transitions provisioned, ready, and active flags in order. Active transitions notify registered subscribers such as hwmon, thermal, and the minimal driver.

## State and Persistence
Per-linecard state includes slot index, devlink linecard pointer, `provisioned`, `ready`, `active`, hardware and INI revisions, the selected flashable device info/index, a delayed timeout work item, and a scratch `MBCT` payload. Global linecards state includes count, core/bus pointers, parsed type info, and a list of event-ops subscribers. Persistent hardware effects include INI erase/transfer/activation, firmware flash FSM operations, and ready bit changes through `MDDC`.

## Dependencies and Integration Points
The manager depends on devlink linecard APIs, workqueues, mlxsw core trap/event plumbing, mlxsw register helpers (`MDDQ`, `MDDT`, `MDDC`, `MBCT`, `MCQI`, `MCC`, `MCDA`, `MGIR`), generic `mlxfw`, request_firmware, and auxiliary-device glue in `core_linecard_dev.c`. It is consumed by hwmon, thermal, and minimal port handling through event ops and by core port removal through `mlxsw_core_ports_remove_selected()`.

## Risks
The status process must maintain transition order: provision before ready/active, deactivate before ready/provision clear. A missed status event triggers delayed failure, so timeout scheduling and cancellation must stay balanced. INI bundle parsing mutates copied firmware data by swabbing u32 words; validation must reject truncated or non-4-byte-aligned INIs first. Firmware flashing is allowed only for active line cards under the linecard lock. Event-op unregister calls inactive callbacks after removing the list item, so consumers must tolerate callbacks during teardown.

## Test Signals
Exercise modular and non-modular boots, missing and invalid INI bundle files, devlink type enumeration, provision/unprovision with successful DSDSC events, provision timeout, BCT activation failure, active/inactive notifications to hwmon/thermal/minimal, nested devlink info and flash, and teardown while delayed work or queued status/BCT work exists. Fault injection around register writes should leave devlink linecard state failed rather than partially active.

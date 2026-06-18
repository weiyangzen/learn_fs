# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.h

## Purpose

`cm_volstat.h` defines the public/private ABI for OpenAFS Windows cache-manager volume-status notifications. It declares cache-manager entry points for service, network, volume, DFS mapping, path-to-volume, path-to-DFS-link, redirector delivery, and redirector notification toggling. It also defines the function-table ABI exchanged with optional external volume-status handler DLLs.

The header is the shared contract for `cm_volstat.c`, handler DLLs, pioctl test structures, and redirector volume-status event integration.

## Important APIs, Types, and Functions

Core status type:

- `enum volstatus` describes volume state as `vl_online`, `vl_busy`, `vl_offline`, `vl_alldown`, or `vl_unknown`.

Cache-manager functions:

- `cm_VolStatus_Initialization` and `cm_VolStatus_Finalize` load/unload handler state.
- `cm_VolStatus_Service_Started` and `cm_VolStatus_Service_Stopped` report service lifecycle.
- `cm_VolStatus_Network_Started` and `cm_VolStatus_Network_Stopped` have architecture-dependent signatures: two NetBIOS names on `_WIN64`, one on 32-bit builds.
- `cm_VolStatus_Network_Addr_Change` reports address list changes.
- `cm_VolStatus_Change_Notification` reports cell/volume status updates.
- `cm_VolStatus_Path_To_ID` maps share/path strings to cell ID, volume ID, and volume status.
- `cm_VolStatus_Path_To_DFSlink` maps share/path strings to DFS-link target data.
- `cm_VolStatus_Notify_DFS_Mapping` and `cm_VolStatus_Invalidate_DFS_Mapping` notify or invalidate DFS mappings by scache/path.
- `cm_VolStatus_DeliverNotifications` is the redirector event delivery thread routine.
- `cm_VolStatus_SetRDRNotifications` toggles redirector forwarding.

DLL ABI:

- `DLL_VOLSTATUS_FUNCS_VERSION` is `2`.
- `dll_VolStatus_Funcs_t` contains handler-supplied callbacks for service, network, address-change, volume-state, DFS mapping notify, and DFS mapping invalidate. Version 2 adds DFS mapping functions.
- `CM_VOLSTATUS_FUNCS_VERSION` is `1`.
- `cm_VolStatus_Funcs_t` contains cache-manager callbacks the DLL can call: path-to-ID and path-to-DFS-link.

Test and redirector structures:

- `struct VolStatTest` carries pioctl test flags, fid, cell name, volume name, and state.
- `VOLSTAT_TEST_*` flags request server apply, volume check, network up, or network down behavior.
- `enum rdr_event_type` distinguishes redirector address-change, volume-status, and network-status events.
- `rdr_volstat_evt_t` is a queue element with event type and union payload for volume online state or network status.

## Control Flow

The header defines an ABI flow rather than implementing behavior. During initialization, `cm_volstat.c` passes a `dll_VolStatus_Funcs_t` to the external DLL to be populated and a `cm_VolStatus_Funcs_t` containing callable cache-manager path helpers. Later, cache-manager events call the populated `dll_funcs` entries, while the DLL can call back into `cm_VolStatus_Path_To_ID` or `cm_VolStatus_Path_To_DFSlink`.

Redirector notification control uses `cm_VolStatus_SetRDRNotifications` to enable queueing of `rdr_volstat_evt_t` objects, then `cm_VolStatus_DeliverNotifications` consumes those objects asynchronously.

## State and Persistence Behavior

The header’s structs are runtime ABI data. `VolStatTest` is request/test payload state. `rdr_volstat_evt_t` is transient queued event state. Persistent configuration for enabling handlers or redirector forwarding is outside this header and is read by `cm_volstat.c` from the Windows registry.

No on-disk repository or cache data is declared here.

## Dependencies and Integration Points

This header depends on OpenAFS types (`afs_uint32`, `cm_fid_t`, `cm_scache_t`, `clientchar_t`, `osi_queue_t`), Windows types (`DWORD`, `ULONG`, `BOOLEAN`), and constants such as `CELL_MAXNAMELEN` and `VL_MAXNAMELEN`.

Integration points include:

- External volume-status handler DLLs that must honor `dll_VolStatus_Funcs_t` versioning and calling convention.
- Cache-manager path resolution via `cm_VolStatus_Funcs_t`.
- Redirector event delivery through `rdr_volstat_evt_t`.
- Pioctl or diagnostic code using `VolStatTest` and `VOLSTAT_TEST_*`.

## Risks and Edge Cases

- The architecture-dependent network-start/stop prototypes require matching caller and implementation signatures across 32-bit and 64-bit builds.
- Function-table versioning must remain backward-compatible; adding fields without version bumps can break handler DLLs.
- The `__fastcall` calling convention is part of the ABI and must match external DLL expectations.
- `rdr_volstat_evt_t` uses an anonymous union-style layout; compiler compatibility and C mode assumptions matter.
- The header does not declare `cm_VolStatus_Active`, although `cm_volstat.c` defines it. Callers needing that function rely on another declaration or implicit knowledge.

## Test Signals

- Compile tests for `_WIN64` and non-`_WIN64` prototypes.
- ABI tests that a handler compiled against the header receives the expected version and function pointer layout.
- Unit or integration tests for `VolStatTest` flag handling in pioctl code.
- Redirector queue tests should validate `rdr_volstat_evt_t` layout for address-change, volume-status, and network-status payloads.

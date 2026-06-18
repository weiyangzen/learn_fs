# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_acpi_notify.c

## Purpose
Implements the Surface ACPI Notify (SAN) shim. It translates ACPI GSB OperationRegion requests into SSAM controller requests, relays SSAM battery/thermal events back into ACPI `_DSM` notifications, and exposes a notifier interface for ACPI-originated discrete GPU events.

## Important APIs, Types, And Functions
`struct san_data` stores device, bound SSAM controller, ACPI connection info, and battery/thermal SSAM notifiers. The exported dGPU interface is `san_client_link()`, `san_dgpu_notifier_register()`, and `san_dgpu_notifier_unregister()`. Event helpers include `san_evt_bat_*()`, `san_evt_tmp_*()`, delayed battery work, and `san_acpi_notify_event()`. GSB handlers include `san_opreg_handler()`, `san_rqst()`, `san_rqsg()`, `san_etwl()`, and response helpers. Driver setup uses `san_probe()`, `san_remove()`, and a global `san_wq`.

## Control Flow
Probe binds to the SSAM controller, creates ACPI consumer device links for devices depending on the SAN ACPI node, allocates state, installs a GSBus address-space handler, registers SSAM BAT/TMP event notifiers, exposes the RQSG provider device, and clears ACPI dependencies. ACPI RQST buffers become synchronous SSAM requests with optional response and retry. RQSG buffers become `san_dgpu_event` notifications to registered clients. ETWL buffers log firmware messages. SSAM BAT/TMP events call ACPI DSM functions, with delays for adapter and battery-state updates to avoid stale ACPI battery data.

## State And Persistence Behavior
SAN keeps only runtime state. The dGPU notifier singleton uses an rwsem-protected provider device pointer and blocking notifier chain. Delayed battery work allocates a copy of the event payload and is flushed on remove after notifier unregister. No persistent state is written.

## Dependencies And Integration Points
Depends on ACPI DSM/GSBus APIs, Surface Aggregator controller sync requests, SSAM event notifiers, device links, workqueues, notifier chains, and power-management state. It binds ACPI HID `MSHW0091` and acts as a bridge for ACPI battery, thermal, DPTF, and GPU-related firmware methods.

## Risks
OperationRegion parsing trusts firmware-provided lengths after validation; off-by-one mistakes can affect ACPI communication. `san_set_rqsg_interface_device(NULL)` returns `-EBUSY` because the helper only sets when no device and `dev` is non-null; remove ignores the return, so the global provider pointer may not actually be cleared in this source. Suspended-device fixup special-cases BAS command `0x0d`; other ACPI requests while suspended return an encoded error. Delayed work uses copied flexible event storage and must remain consistent with `struct ssam_event` layout.

## Test Signals
Test ACPI RQST success/error/response truncation behavior, ETWL logging, RQSG notifier registration and client device links, BAT/TMP event DSM calls, delayed ADP/BST behavior, remove/unload clearing global provider state, suspended BAS fixup, and retry behavior on transient SSAM errors.

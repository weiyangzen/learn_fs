# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_hub.c

## Purpose
Implements SSAM subsystem hub drivers for dynamically present device groups, especially KIP keyboard-cover devices and Surface Book base devices. It registers/removes SSAM child devices when hub connection state changes.

## Important APIs, Types, And Functions
Generic hub state is represented by `enum ssam_hub_state`, `enum ssam_hub_flags`, `struct ssam_hub`, and `struct ssam_hub_desc`. Core functions are `ssam_hub_update_workfn()`, `ssam_hub_update()`, `ssam_hub_probe()`, and `ssam_hub_remove()`. Base hub support queries BAS opmode via `ssam_bas_query_opmode()` and handles connection CID `0x0c`. KIP hub support queries KIP state via `__ssam_kip_query_state()` and handles connection CID `0x2c`.

## Control Flow
Probe obtains match-data descriptor, allocates a hub, configures a high-priority event notifier, registers it, and schedules immediate update work. Update work calls the descriptor's `get_state()`, handles hot-remove correction, compares previous and current state, and either registers child clients with `ssam_device_register_clients()` or removes them with `ssam_remove_clients()`. Notifier callbacks validate event command and payload, then schedule update work immediately for disconnect or after a connect delay for attach.

## State And Persistence Behavior
The hub stores current state, hot-removed flag, delayed work, connect delay, and notifier registration. Child-device state lives in the SSAM device core. No persistent storage is used. On disconnect, existing children are marked hot-removed in reverse order before removal so re-added devices can be distinguished.

## Dependencies And Integration Points
Depends on `linux/surface_aggregator/device.h`, SSAM event notifiers, synchronous request helper macros, delayed work, and SSAM child registration/removal helpers. It binds virtual SSAM hub devices via `SSAM_VDEV(HUB, SAM, ...)`.

## Risks
Correctness depends on firmware connection events and query commands agreeing. The hot-remove race mitigation reschedules work when a disconnect/connect pair is collapsed, but unusual event loss can still delay child registration. Base hub notifier deliberately returns unhandled so detachment-system drivers can consume the event; changing that would break event sharing.

## Test Signals
Test initial connected/disconnected query, KIP cover attach/detach, Surface Book base attach/detach, rapid remove/re-add races, resume update scheduling, child devices marked hot-removed before removal, delayed connect registration, and notifier return semantics with other drivers.

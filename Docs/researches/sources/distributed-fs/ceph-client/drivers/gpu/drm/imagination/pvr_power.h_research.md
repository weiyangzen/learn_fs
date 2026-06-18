# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.h

## Purpose
Declares the PowerVR power-management interface shared by probe, PM callbacks, firmware control, MMU recovery, and queue reset code. It also provides small inline wrappers for taking and dropping runtime PM references on a `pvr_device`.

## Important APIs, types, and functions
- Watchdog: `pvr_watchdog_init()` and `pvr_watchdog_fini()`.
- Device loss and state: `pvr_device_lost()` and `pvr_power_is_idle()`.
- PM callbacks: `pvr_power_device_suspend()`, `pvr_power_device_resume()`, and `pvr_power_device_idle()`.
- Reset and references: `pvr_power_reset()`, inline `pvr_power_get()`, and inline `pvr_power_put()`.
- Power domains: `pvr_power_domains_init()` and `pvr_power_domains_fini()`.
- Platform operations: `struct pvr_power_sequence_ops`, `pvr_power_sequence_ops_manual`, and `pvr_power_sequence_ops_pwrseq`.

## Control flow
The header itself only contains inline `pvr_power_get()` and `pvr_power_put()`, which translate a `pvr_device` into its DRM device and call `pm_runtime_resume_and_get()` or `pm_runtime_put()`. The declared sequencing callbacks allow device-data tables to select manual clock/reset control or generic power-sequencer control.

## State and persistence
No standalone state is defined here. The declared APIs operate on persistent `pvr_device` power, firmware, watchdog, and domain fields. `struct pvr_power_sequence_ops` persists in platform/device-data tables as function pointers.

## Dependencies and integration points
Includes `pvr_device.h`, mutex declarations, and runtime PM declarations. It is used by MMU flush recovery, firmware paths, PM ops, probe/remove domain setup, and queue/reset integration. The inline helpers centralize runtime PM reference handling for call sites that need the GPU powered.

## Risks
Because the runtime PM wrappers are inline and minimal, callers must handle errors and balance references correctly. Any signature change affects multiple subsystems. Platform power operation implementations must preserve the `init`, `power_on`, and `power_off` contract or runtime PM and reset recovery will fail.

## Test signals
Build coverage catches declaration drift. Runtime validation comes from balanced PM reference tests, suspend/resume, reset, watchdog initialization/finalization, and platform probe on both manual and pwrseq-backed devices.

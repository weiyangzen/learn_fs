# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c

## Purpose

`amdgpu_ras_nbio_v7_9.c` registers NBIO v7.9 RAS interrupt sources with AMDGPU IRQ handling. The process and set callbacks are intentionally dummy because the relevant BIF-ring interrupt path is disabled due to a known hardware issue.

## Important APIs, Types, And Functions

The exported table is `amdgpu_ras_nbio_sys_func_v7_9`. It installs IRQ source functions for `ras_controller_irq` and `ras_err_event_athub_irq`, then registers IDs `NBIF_7_4__SRCID__RAS_CONTROLLER_INTERRUPT` and `NBIF_7_4__SRCID__ERREVENT_ATHUB_INTERRUPT` under `SOC15_IH_CLIENTID_BIF`.

## Control Flow, State, And Persistence

`nbio_v7_9_init_ras_controller_interrupt` and `nbio_v7_9_init_ras_err_event_athub_interrupt` assign the `amdgpu_irq_src_funcs`, set `num_types = 1`, and call `amdgpu_irq_add_id`. The actual `.set` and `.process` functions return success without programming hardware or dispatching events.

## Dependencies And Integration Points

It depends on AMDGPU IRQ registration, NBIO register/IRQ source headers, and rascore NBIO callback wiring. The manager selects this implementation for NBIO IP versions 7.9.0 and 7.9.1.

## Risks And Test Signals

Risks are dummy handlers hiding future hardware enablement, registering wrong client/source IDs, and assuming BIF-ring interrupts remain disabled. Test signals include IRQ registration during probe, no spurious processing, unsupported-version rejection, and platform validation when NBIO RAS interrupt routing changes.

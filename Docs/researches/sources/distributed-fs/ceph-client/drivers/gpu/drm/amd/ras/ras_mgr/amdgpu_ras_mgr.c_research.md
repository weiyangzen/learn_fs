# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.c

## Purpose

`amdgpu_ras_mgr.c` is the AMDGPU unified RAS manager IP block. It creates and configures `ras_core_context`, wires AMDGPU system callbacks into rascore, initializes software/hardware RAS services, handles interrupts, manages event sequence numbers, dispatches RAS commands, and coordinates reset-time pause/resume behavior.

## Important APIs, Types, And Functions

It exports `ras_v1_0_ip_block`, `amdgpu_ras_mgr_get_context`, `amdgpu_enable_uniras`, `amdgpu_uniras_enabled`, interrupt handlers, ECC update, GPU reset, event sequence generation, EEPROM safety checks, NPS query, retired-address checks, RMA status, command handling, pre/post reset hooks, and bad-page row lookup. Internal configuration helpers install ACA topology, EEPROM I2C, MP1 v13.0, NBIO v7.9, PSP, and UMC config.

## Control Flow, State, And Persistence

Software init disables unified RAS by default, enables it for selected MP0 IP or debug ACA mode, allocates `amdgpu_ras_mgr`, creates rascore with IP versions and callbacks, initializes RAS processing, rascore software state, event manager, and VF virtualization state. Hardware init delegates to VF remote RAS or rascore, marks `ras_is_ready`, and enables unified RAS. Interrupt flow gates on readiness, generates DE/poison-consumption/fatal sequence numbers, and enqueues event work through `amdgpu_ras_process`. Persistent state includes manager readiness, event counters per hive or device, bad-page thresholds, rascore submodules, VF command state, and reset flags.

## Dependencies And Integration Points

The manager depends on AMDGPU reset, XGMI hives, PSP RAS TA context, EEPROM I2C, MP1/NBIO adapters, rascore modules, SR-IOV, UMC bad-page handling, SMU/DPM bad-page threshold controls, and the AMDGPU IP block lifecycle.

## Risks And Test Signals

Risks include enabling on unsupported IP versions, not unwinding all allocations on partial init failure, incorrect hive event-manager ownership, readiness gating differences between VF and PF, bad-page threshold misconfiguration, and command buffer size assumptions. Test signals include probe/remove, VF/PF init, MP1/NBIO unsupported-version handling, interrupt dispatch for UMC and non-UMC blocks, reset pre/post hooks, command submission, EEPROM safety watermark behavior, and XGMI multi-node sequence numbering.

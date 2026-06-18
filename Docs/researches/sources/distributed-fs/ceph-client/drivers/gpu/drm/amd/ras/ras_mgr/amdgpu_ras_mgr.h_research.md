# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.h

## Purpose

`amdgpu_ras_mgr.h` declares the AMDGPU unified RAS manager interface, interrupt metadata, manager state, and IP block descriptor.

## Important APIs, Types, And Functions

`enum ras_ih_type` classifies none, block-controller, consumer-client, and fatal-error interrupt sources. `struct ras_ih_info` carries a block ID plus either an AMDGPU IV entry or PASID/reset callback payload. `struct amdgpu_ras_mgr` stores `adev`, `ras_core`, delayed bad-page work, event manager, VF command state, last poison-consumption sequence number, readiness, pause state, and completion. The header declares manager lifecycle/query, interrupt dispatch, ECC update, reset, command, NPS, retired-address, RMA, and reset hook functions.

## Control Flow, State, And Persistence

The header has no runtime flow, but it defines the manager state machine: `ras_is_ready` gates public operations; `is_paused` and `ras_event_done` coordinate reset with event processing; delayed work periodically retires bad pages; sequence tracking prevents duplicate poison-consumption handling.

## Dependencies And Integration Points

It includes `ras.h` and `amdgpu_ras_process.h`, and is used by RAS manager implementation, NBIO/MP1 adapters, command handlers, sys callbacks, virtualization command code, and interrupt producers.

## Risks And Test Signals

Risks include union misuse in `ras_ih_info`, stale readiness checks, and incorrect lifetime of `virt_ras_cmd` or delayed work. Test signals include compile coverage, interrupt payload tests, reset pause/resume tests, VF/PF path tests, and manager context null checks.

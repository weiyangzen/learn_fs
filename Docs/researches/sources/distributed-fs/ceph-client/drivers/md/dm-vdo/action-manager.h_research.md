# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.h

## Purpose
This header declares the VDO action-manager interface for applying serialized administrative actions to multi-zone VDO components with initiator-thread preambles/conclusions and zone-thread callbacks.

## Important APIs, Types, And Functions
- `vdo_zone_action_fn` runs asynchronously for a zone and reports through a parent completion.
- `vdo_action_preamble_fn` runs on the action manager initiator thread before zone work.
- `vdo_action_conclusion_fn` runs on the initiator thread after zone work and returns a VDO status.
- `vdo_action_scheduler_fn` optionally schedules default work.
- `vdo_zone_thread_getter_fn` maps a zone number to a VDO thread id.
- Public functions allocate a manager, inspect current operation/action context, schedule default actions, schedule generic actions, schedule explicit admin operations, and schedule operations with an action-specific context.

## Control Flow
Callers construct an action manager with zone count, zone-thread resolver, initiator thread id, context, optional scheduler, and owning `struct vdo`. They then schedule actions or operations; implementation serializes them and invokes callbacks in the documented order. At least one of preamble, zone action, or conclusion must be supplied by contract, though the implementation substitutes no-op functions for NULL preamble/conclusion.

## State And Persistence Behavior
The header exposes an opaque `struct action_manager`. Runtime state is internal to the implementation and includes current admin operation and optional current action context. No persistent state is represented here.

## Dependencies And Integration Points
It depends on `admin-state.h` and `types.h`, plus `struct vdo_completion` and `struct vdo`. It is used by VDO components that need coordinated per-zone administrative operations.

## Risks
- The API does not expose queue depth beyond success/failure; callers must handle `false` scheduling and parent `VDO_COMPONENT_BUSY`.
- Callback threading is part of the contract; misuse can create race conditions in zone-owned structures.
- Context lifetime must outlive asynchronous callbacks.

## Test Signals
Compile all callback typedef users, test scheduling return values, operation-code reporting, current action context retrieval, default scheduler behavior, and callbacks running on expected thread ids.

# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.h

Purpose: defines the common VSP1 entity abstraction used by all processing blocks. It provides entity type IDs, routing descriptors, operation callbacks, embedded state fields, and shared helper prototypes.

Important APIs and types: `enum vsp1_entity_type`, `struct vsp1_route`, `struct vsp1_entity_operations`, and `struct vsp1_entity`. The operation table separates stream-invariant setup, per-frame setup, per-partition setup, width limits, and partition construction. Helpers include `to_vsp1_entity()`, `vsp1_entity_init()`, `vsp1_entity_destroy()`, link setup, state lookup, route setup, configure dispatch, color-space adjustment, remote-pad lookup, and generic subdev pad handlers.

Control flow role: every entity constructor fills type, codes, limits, ops, and then calls `vsp1_entity_init()`. Pipeline configuration walks entities and dispatches the callbacks declared here. Media-controller mode relies on the link setup and pad handlers to build legal graphs.

State and persistence: `struct vsp1_entity` persists hardware identity, route pointer, supported bus codes, dimensions, pipeline membership, media pads, source/sink relationships, subdev active state, and a mutex protecting that state.

Dependencies and integration: includes Linux list/mutex and V4L2 subdev APIs; forward-declares VSP1 display-list and pipeline structures to avoid circular includes.

Risks and test signals: changing fields or callback semantics affects all entities. Validate compile coverage, media graph creation, route setup, pipeline partitioning, and subdev state locking after edits.

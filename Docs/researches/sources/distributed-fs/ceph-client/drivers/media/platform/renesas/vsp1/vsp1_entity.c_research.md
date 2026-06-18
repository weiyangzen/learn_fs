# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.c

Purpose: common VSP1 entity infrastructure. It owns media-subdev initialization, default pad format operations, media link bookkeeping, route register setup, entity state allocation, and wrapper dispatch for entity-specific stream/frame/partition callbacks.

Important APIs and functions: `vsp1_entity_init()`, `vsp1_entity_destroy()`, `vsp1_entity_route_setup()`, `vsp1_entity_configure_stream()`, `vsp1_entity_configure_frame()`, `vsp1_entity_configure_partition()`, `vsp1_entity_adjust_color_space()`, `vsp1_entity_link_setup()`, `vsp1_entity_remote_pad()`, and generic pad handlers for format/code/frame-size. `vsp1_routes[]` maps entity type/index to DPR route registers and node IDs.

Control flow: constructors initialize a `vsp1_entity`, allocate pads/sources, bind route entries, initialize subdev ops/state, and attach media entity operations. During media link setup, source fan-out and sink fan-in are enforced in software while ignoring histogram side links for normal pipeline traversal. During hardware configuration, route setup writes the correct DPR routing value, with special handling for HGO/HGT sampling and BRS/IIF selector bits.

State and persistence: `entity->state` stores active pad formats, crops, and compose rectangles. `sources[]`, `sink`, `sink_pad`, `pipe`, and list nodes persist the current graph/pipeline membership. The mutex protects subdev state; route entries are immutable after init.

Dependencies and integration: depends on V4L2 subdev state, media links, V4L2 controls/events, display-list writes, pipeline helpers, and format/color-space helpers from `vsp1_pipe.c`.

Risks and test signals: risks include use of internal `__v4l2_subdev_state_alloc()`, link bookkeeping divergence from media graph flags, route table gaps for new entities, and lock ordering. Test media link enable/disable, invalid fan-in/fan-out, format propagation, route register traces, and all entity constructors.

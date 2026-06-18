# sources/distributed-fs/ceph-client/include/media/media-entity.h

## Purpose
Defines the media-controller graph model: graph objects, entities, pads, links, interfaces, graph traversal, pipeline streaming state, entity operations, and link creation/removal helpers.

## Important APIs, Types, and Functions
Core types are `media_gobj`, `media_entity_enum`, `media_graph`, `media_pipeline`, `media_pipeline_pad`, iterators, `media_link`, `media_pad`, `media_entity_operations`, `media_entity`, `media_interface`, and `media_intf_devnode`. Helpers generate/type-decode graph IDs, test V4L2 entity subclasses, manage entity enums, initialize pads, create pad/interface/ancillary links, setup links, find remote pads, walk graphs, start/stop pipelines, iterate pipeline pads/entities, and remove links. Macros include `media_entity_for_each_pad()`, `media_entity_call()`, and `for_each_media_entity_data_link()`.

## Control Flow
Drivers initialize pads, register entities, create links, and use `media_entity_setup_link()` to enable/disable mutable links. Pipeline start walks enabled links from an origin pad, validates links, assigns a `media_pipeline` to all connected pads, and supports nested starts via `start_count`; stop unwinds the same association. Graph-walk helpers perform depth-first traversal but are deprecated in favor of pipeline iterators.

## State and Persistence Behavior
Entities, pads, interfaces, and links are persistent graph objects owned by a `media_device`. `internal_idx` supports bitmap enumeration and can be reused after unregister. `pad->pipe` and pipeline pad lists are runtime streaming state. `use_count` is signed to catch negative-use bugs.

## Dependencies and Integration Points
Depends on bitmap, fwnode, lists, UAPI media flags, and the media device. Integrates V4L2 subdevices/video devices, firmware endpoints, media ioctls, and pipeline-aware stream validation.

## Risks
Graph mutation must be serialized by the media device graph mutex. Link flags and backlink pairs must remain consistent. `MEDIA_ENTITY_ENUM_MAX_DEPTH` limits traversal stack depth. Pad interdependency defaults to all pads interdependent when no callback exists, which can over-lock configuration. Pipeline start/stop nesting requires identical pipeline pointers.

## Test Signals
Entity/pad/link registration, mutable and immutable link setup, link validation failures, remote-pad uniqueness errors, firmware endpoint pad lookup, pipeline nested start/stop, graph traversal depth, interface link removal, and disabled media-controller builds.

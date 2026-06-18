# sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.h

## Purpose
`rgw_sync_policy.h` defines the serialized data model for RGW multisite sync policies: flows between zones, bucket pipes, source filters, destination transforms, ownership translation, user/system modes, group status, and complete policy info.

## Important APIs, Types, and Functions
Core types include `rgw_sync_symmetric_group`, `rgw_sync_directional_rule`, `rgw_sync_bucket_entity`, `rgw_sync_pipe_filter_tag`, `rgw_sync_pipe_filter`, `rgw_sync_pipe_acl_translation`, source/dest/combined pipe params, concrete `rgw_sync_bucket_pipe`, aggregate `rgw_sync_bucket_entities` and `rgw_sync_bucket_pipes`, `rgw_sync_data_flow_group`, `rgw_sync_policy_group`, and `rgw_sync_policy_info`. Each type has Ceph encode/decode and JSON dump/decode declarations.

## Control Flow
Policies are built as groups. A group can constrain data flow and define pipes from aggregate sources to aggregate destinations. Aggregate entities expand into concrete zone/bucket entities for runtime matching. Filters and destination params refine sync behavior per pipe.

## State and Persistence Behavior
All structs are versioned with Ceph encoding macros and persisted as part of RGW metadata. Optional fields represent absent constraints; empty strings often represent wildcards. `Session`-like runtime state is absent.

## Dependencies and Integration Points
The header depends on `rgw_basic_types.h`, `rgw_tag.h`, Ceph Formatter/JSON/encoding utilities, `rgw_bucket`, `rgw_user`, and `rgw_zone_id`. It is consumed by multisite sync, admin policy manipulation, and metadata persistence code.

## Risks
Because this is a durable encoding contract, field reordering or type changes would break compatibility. Wildcard semantics span `all_zones`, unset optionals, and empty bucket fields. `rgw_sync_policy_group::status` has no default initializer in the declaration, so callers must set it before encoding/dumping.

## Test Signals
Binary encode/decode compatibility, JSON round trips, default-instance generation, group status parsing, pipe specificity, optional user/mode handling, ACL translation equality, and expansion for all wildcard combinations are key signals.

# sources/distributed-fs/ceph/src/rgw/rgw_pool_types.h

## Purpose
`rgw_pool_types.h` defines fundamental serialized pool and data-placement types shared outside RGW-only contexts. The header explicitly avoids dependencies that require radosgw or OSD-only compilation contexts.

## Important APIs, Types, And Functions
`rgw_pool` stores pool `name` and namespace `ns`, with string conversion, initialization, comparison, encoding/decoding, JSON dump, test instances, and stream output. It includes legacy decode compatibility with older `rgw_bucket`-shaped encodings. `rgw_data_placement_target` stores data, data-extra, and index pools, exposes `get_data_extra_pool()`, comparison, dump, and JSON decode declarations.

## Control Flow
`rgw_pool::decode()` uses `DECODE_START_LEGACY_COMPAT_LEN(10, 3, 3)` and decodes only `name` for old versions, adding `ns` for version 10+. `get_data_extra_pool()` falls back to `data_pool` when the extra pool is empty.

## State And Persistence
These are serialized metadata types used in zone/bucket placement configuration. Compatibility behavior is central: old encodings must continue to decode correctly, and string forms are used in configuration and formatting.

## Dependencies And Integration Points
The header depends on core encoding, types, and formatter support. Placement, bucket metadata, period maps, and zone config use these types.

## Risks And Test Signals
Risks include breaking legacy decode, inconsistent `to_str()/from_str()` behavior in implementations, namespace comparison errors, and fallback semantics for data-extra pools. Tests should cover encode/decode across versions, namespace round trips, ordering/equality, JSON decode/dump, and data-extra fallback.

# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.h

## Purpose
This header declares the v1 JSON encoder and decoder wrappers for RGW data-log notifications. It keeps old notification API formatting separate from the generation-aware `rgw_data_notify_entry` type declared in `rgw_datalog.h`.

## Important APIs, Types, and Functions
`rgw_data_notify_v1_encoder` holds a const reference to `bc::flat_map<int, bc::flat_set<rgw_data_notify_entry>>` and is passed to `encode_json()`. `rgw_data_notify_v1_decoder` holds a mutable reference to the same map shape and is passed to `decode_json_obj()`. The API is intentionally tiny and relies on custom overloads rather than changing the core notification entry's normal JSON shape.

## Control Flow
There is no runtime flow in the header beyond wrapper construction by callers. The implementation uses these wrappers to select v1 behavior: encode current entries as shard-to-key-string arrays, or decode those arrays back into entries with zero generation.

## State and Persistence Behavior
The wrappers do not own state; they borrow caller-provided maps. The v1 conversion contract is state-significant because it strips generation information from notifications crossing this compatibility path.

## Dependencies and Integration Points
The header depends on Boost flat containers and `rgw_datalog.h`, forward declares formatter and JSON types, and is consumed by the implementation file plus notification API callers. It is an integration shim between the current datalog notification model and legacy JSON clients.

## Risks and Test Signals
Risks are reference lifetime misuse, accidental use of v1 wrappers where generation-preserving JSON is required, and divergence between declarations and implementation overloads. Compile tests should include this header without the implementation's private wrappers, and API tests should verify v1 decode/encode compatibility with old clients.

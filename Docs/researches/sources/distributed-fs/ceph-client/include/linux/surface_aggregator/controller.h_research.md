<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/controller.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_aggregator/controller.h

## Purpose

`controller.h` is the public SSAM controller API for Microsoft Surface Aggregator Module clients. It sits above the raw Surface Serial Hub protocol and defines event payloads, request/response descriptors, synchronous request helpers, retry wrappers, and event notifier registration. Its main consumers are Surface platform drivers that need to issue EC commands or subscribe to EC-generated events without owning the packet transport implementation.

## Important APIs, types, and functions

Key types are `struct ssam_event`, `struct ssam_request`, `struct ssam_response`, `struct ssam_request_sync`, `struct ssam_request_spec`, `struct ssam_request_spec_md`, `struct ssam_notifier_block`, `struct ssam_event_registry`, `struct ssam_event_id`, and `struct ssam_event_notifier`. The API exports controller lookup/lifetime helpers (`ssam_get_controller()`, `ssam_client_bind()`, `ssam_controller_get()`/`put()`), synchronous request allocation/submission/waiting (`ssam_request_sync_alloc()`, `ssam_request_sync_submit()`, `ssam_request_do_sync*()`), request definition macros (`SSAM_DEFINE_SYNC_REQUEST_*` and `_MD_*`), retry macros, notifier registration, and direct event enable/disable calls.

## Control flow

Typical command flow builds an `ssam_request`, writes SSH command data with `ssam_request_write_data()`, submits through the controller, waits on `struct completion`, and validates the response length when a return value is expected. The generated macros produce small static wrapper functions for no-argument, write-only, read-only, and write/read commands; multi-device variants take `tid` and `iid` at call time. Event flow registers `ssam_event_notifier` objects; the controller enables EC events on first active registration, dispatches matching `ssam_event` instances by category/target/instance mask, and disables events on the last unregister.

## State and persistence behavior

The header itself holds no state, but it defines stateful contracts: request buffers must remain valid until completion/release, `ssam_request_sync.status` becomes authoritative after `ssam_request_sync_wait()`, response length is written by the transport, notifier lists and event usage counts live in the controller, and event enablement persists in the EC until disabled or reset. `ssam_controller_statelock()`/`stateunlock()` expose controller state serialization to clients that need coordinated setup/teardown.

## Dependencies and integration points

It depends on completions, device model types, `linux/types.h`, and `serial_hub.h` for `ssh_request`, `ssam_span`, target IDs, and categories. Integration points are Surface client drivers, the SSAM bus in `device.h`, the lower packet/request transport, and EC command registries (`SSAM_EVENT_REGISTRY_SAM`, `KIP`, and `REG`).

## Risks and test signals

Risks center on lifetime and protocol shape: using stack request buffers after failed submission can deadlock in `ssam_request_sync_wait()`, response-size mismatches are treated as `-EIO`, unsequenced requests must not request responses, notifier callbacks can stop traversal, and hotplug/removal races can make EC communication time out. Tests should compile macro-generated wrappers, exercise sync success/error/timeout paths, verify response-length rejection, register multiple observers and active notifiers, and validate event enable/disable reference counting against controller traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/controller.h -->

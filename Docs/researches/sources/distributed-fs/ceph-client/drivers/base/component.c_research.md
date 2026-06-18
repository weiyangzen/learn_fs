# sources/distributed-fs/ceph-client/drivers/base/component.c

### Purpose
`component.c` implements the component helper for aggregate devices whose logical driver is assembled from multiple independently-probed component devices. This is common for SoC display and media stacks where no single bus-level abstraction captures the hardware relationship.

### Important APIs, Types, And Functions
Internal types are `struct component_match_array`, `struct component_match`, `struct aggregate_device`, and `struct component`. Global state is protected by `component_mutex` and stored in `component_list` and `aggregate_devices`. Exported helpers include `component_match_add_release()`, `component_match_add_typed()`, `component_master_add_with_match()`, `component_master_del()`, `component_master_is_bound()`, `component_bind_all()`, `component_unbind_all()`, `component_add_typed()`, `component_add()`, `component_del()`, and compare/release helpers for OF nodes, devices, and device names.

### Control Flow
Aggregate drivers build a devres-managed match list, then call `component_master_add_with_match()`. Registration trims the match array, creates an `aggregate_device`, adds it to the aggregate list, and tries to bind immediately. Component drivers call `component_add()` or `component_add_typed()`, which adds a `component` to the component list and attempts to bring up any now-complete aggregate. `find_components()` binds match entries to available component objects, `try_to_bring_up_aggregate_device()` calls the aggregate `bind()` once all matches are present, and aggregate `bind()` normally calls `component_bind_all()` to invoke per-component `bind()` callbacks in match order. Removal tears down the aggregate first, unbinding components in reverse order.

### State, Persistence, And Dependencies
State is entirely in-memory and process-lifetime: match records point to compare data and matched components, components point back to an aggregate, and aggregate devices track `bound`. Debugfs optionally exposes aggregate/component status under `device_component`. The file depends on device core devres groups for rollback, OF references, debugfs, mutex/list primitives, and component public headers.

### Integration Points
Drivers integrate by adding match entries from their parent device, registering the aggregate master, and using `component_bind_all()`/`component_unbind_all()` inside master callbacks. Component drivers register from probe and unregister from remove. The helper does not solve runtime PM or suspend dependencies; the file explicitly points users to device links for that behavior.

### Risks
The global mutex must be held across matching and aggregate bind/unbind expectations; `component_bind_all()` and `component_unbind_all()` warn if called without it. Duplicate component matches are tracked and skipped during bind/unbind to avoid double-calling a component. Error rollback relies on devres groups opened on both the aggregate parent and component device. A failed aggregate bind removes only the new aggregate; a failed component add detaches the component from any match and frees it. Compare-data release is tied to parent devres lifetime, so callers must use the release variant for referenced objects such as OF nodes.

### Test Signals
Test aggregate registration before and after components, missing component defer behavior, duplicate match entries, typed subcomponents, bind failure rollback, reverse-order unbind, component removal while bound, master removal while bound, debugfs status, OF node reference release, and concurrent add/remove serialization under `component_mutex`.

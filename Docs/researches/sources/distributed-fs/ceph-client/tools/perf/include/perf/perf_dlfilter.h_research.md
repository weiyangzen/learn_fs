# sources/distributed-fs/ceph-client/tools/perf/include/perf/perf_dlfilter.h

### Purpose
This public header defines the stable C ABI for shared objects loaded by `perf script --dlfilter`. It exposes sample data, resolved address metadata, helper callbacks, and optional plugin entry points.

### Important APIs, Types, And Functions
`struct perf_dlfilter_sample` carries perf sample fields, branch stack/callchain pointers, event name, and virtualization fields `machine_pid` and `vcpu`. `struct perf_dlfilter_al` describes resolved address-location data, including symbol, DSO, build-id, kernel/user flags, command name, and private data. `struct perf_dlfilter_fns` is the helper table exported by perf: `resolve_ip`, `resolve_addr`, `args`, `resolve_address`, `insn`, `srcline`, `attr`, `object_code`, optional `al_cleanup`, and reserved slots. Optional plugin functions are `start`, `stop`, `filter_event`, `filter_event_early`, and `filter_description`.

### Control Flow
Perf loads the shared object, fills `perf_dlfilter_fns`, calls `start()` if present, invokes early and normal filter callbacks per sample, and calls `stop()` at the end. Filters return 0 to keep, 1 to filter, or negative error.

### State And Persistence
The ABI itself has no state. Plugins may store opaque state through `start()`'s `data` pointer. Struct `size` fields support compatibility checks as the ABI grows.

### Dependencies And Integration Points
The header depends on Linux perf event and integer types and is included by out-of-tree dlfilter plugins, sample filters, and perf tests.

### Risks
ABI layout is the major risk. Fields must be appended compatibly, reserved slots managed carefully, and plugins must check optional callbacks before use. Pointers are owned by perf unless explicitly documented otherwise.

### Test Signals
Compile sample filters, run v0/v2/current dlfilter API tests, and verify older plugin binaries still load and receive valid callbacks.

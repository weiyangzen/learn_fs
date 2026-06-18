# sources/distributed-fs/ceph-client/include/media/media-device.h

## Purpose
Defines the top-level media-controller device object, registration API, graph object lists, media-device operations, request hooks, and device-specific initialization helpers.

## Important APIs, Types, and Functions
`struct media_device_ops` provides `link_notify`, request allocation/free/validate/queue callbacks. `struct media_device` owns parent `dev`, `media_devnode`, model/driver/serial/bus info, topology version, graph-object IDs, entity/interface/pad/link lists, notify callbacks, `graph_mutex`, source enable/disable hooks, request queue mutex/counters, debugfs directory, and request ID allocator. APIs include `media_device_init()`, cleanup/register/unregister, entity register/unregister, entity notify register/unregister, iteration macros, PCI/USB init helpers, and `media_set_bus_info()`.

## Control Flow
Drivers initialize `media_device`, register entities and links, then register the media device as the final step. Link changes may call `link_notify` under `graph_mutex`. Request queueing validates under `req_queue_mutex`, queues non-buffer objects before buffers, and must not fail after queue callback starts. Entity registration populates graph lists and invokes notify callbacks.

## State and Persistence Behavior
`media_device` is long-lived per physical media device. It persists graph topology, object IDs, request counters, source ownership hooks, and debugfs state until unregister/cleanup. Topology version is monotonic for graph changes.

## Dependencies and Integration Points
Depends on media devnodes and media entities plus Linux device, PCI, platform, mutex, atomic, and list APIs. Integrates V4L2/DVB/RC/media drivers with `/dev/media*`, media controller ioctls, request API, and board-level source arbitration.

## Risks
Registration ordering matters: exposing the device before the graph is complete can race userspace. Link and source handlers require `graph_mutex`. Request queue ordering is critical because queuing buffers can start hardware processing. Unregistering an unregistered media device is documented unsafe except for the safe wrapper path.

## Test Signals
Media graph enumeration, entity/link add/remove, topology version changes, request allocate/queue/complete, link notifications, source enable/disable arbitration, PCI/USB bus-info formatting, disabled `CONFIG_MEDIA_CONTROLLER` stub builds, and cleanup after partial probe failure.

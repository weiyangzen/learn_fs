# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_mst_helper.h

Purpose: DRM DisplayPort Multi-Stream Transport topology, sideband messaging, connector, and atomic payload-management API for MST-capable DP connectors.

Important APIs/types/functions: `struct drm_dp_mst_port`, `struct drm_dp_mst_branch`, sideband request/reply structs, `struct drm_dp_sideband_msg_tx/rx`, `struct drm_dp_mst_topology_cbs`, `struct drm_dp_mst_atomic_payload`, `struct drm_dp_mst_topology_state`, `struct drm_dp_mst_topology_mgr`, topology manager APIs, HPD IRQ handling, EDID/detect, PBN/slot calculations, payload add/remove, ACT status, suspend/resume, MST DPCD read/write, atomic helpers, DSC enablement, stream encryption query, ref helpers, and state iterators.

Control flow: drivers initialize a topology manager, enable MST after capability detection, process HPD/ESI events, let workqueues probe branches/ports via sideband messages, create connectors through callbacks, and allocate VCPI/time slots through atomic commit phases.

State and persistence: runtime state includes krefs, branch/port lists, cached EDIDs, AUX endpoints, transfer queues, locks, work items, delayed destroy lists, payload IDs, sink count, cached DPCD, atomic payload lists, PBN divisor, slot ranges, and optional ref history.

Dependencies and integration points: DP helper, DRM atomic/private objects, fixed-point math, workqueues, mutexes, waitqueues, krefs, EDID, connectors, GPU drivers, remote DPCD/I2C, DSC, and HDCP stream status.

Risks and test signals: refcount lifetime bugs, lock inversions, sideband timeouts, stale topology, slot conflicts, DSC accounting, and async commit ordering are risks. Test hotplug storms, nested hubs, remote EDID, payload add/remove, suspend/resume, DSC over MST, failed sideband replies, ref-debug builds, and bandwidth rejection.

# sources/distributed-fs/ceph-client/Documentation/netlink/specs/net_shaper.yaml

Purpose: specifies a Generic Netlink API for hardware network rate limiting and scheduler tree manipulation on network devices.

Important APIs/types/functions: definitions include `max-handle-id`, shaper `scope`, and rate `metric`. The `net-shaper` attribute set models one shaper with `handle`, `metric`, `bw-min`, `bw-max`, `burst`, `priority`, `weight`, `ifindex`, optional `parent`, and repeated `leaves`. `handle` nests `scope` and bounded `id`. `leaf-info` carries child handle plus priority/weight. `caps` reports per-device/scope capability flags such as metric support, nesting, min/max bandwidth, burst, priority, and weight.

Control flow: `get` returns a selected shaper or dumps shapers for an ifindex. `set` creates or updates an attached shaper but cannot create node-scope shapers. `delete` clears a shaper and has special topology behavior for node removal and orphaned parents. `group` creates or updates a scheduling group, attaching queue leaves under a node or netdev-scope parent and returning the resulting handle. `cap-get` returns supported capabilities for an ifindex/scope. Write operations use `admin-perm` and named pre/post hooks that distinguish read, write, dump, and capability paths.

State and persistence: the represented state is hardware/driver shaper configuration and scheduler tree topology. Handles identify shapers within a device. Settings may persist only in driver/hardware runtime state and can be reset by device reload or link changes.

Dependencies and integration points: integrates with network device drivers that expose hardware shapers, kernel netlink spec generation, and traffic-control-like userspace tooling. The schema's pre/post hooks imply kernel-side locking and device lookup around each operation.

Risks: tree manipulation has high consistency risk: deleting a node reattaches leaves and may cascade parent deletion. The same operation accepts many optional shaping fields, so userspace must understand capability flags before setting unsupported metrics. Handle id bounds depend on a named constant rather than a literal, so generator support for symbolic checks matters. Hardware support is uneven across devices.

Test signals: validate capability query before set/group, queue/netdev/node scope rules, handle id bounds, bandwidth/packet metric behavior, deletion reparenting, dump consistency during concurrent changes, and privilege enforcement.

# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.h

## Purpose
`glusterd-svc-mgmt.h` defines the common service-management abstractions used by glusterd auxiliary daemons.

## Important APIs, Types, and Functions
The header defines service callback typedefs for build, manager, start, stop, reconfigure, and mux notification functions. `gf_svc_status_t` models mux process lifecycle states: starting, started, stopping, disconnected, and died. `glusterd_svc_proc_t` represents a multiplexed process with a process-list node, attached service list, notify callback, RPC client, opaque data, and status. `glusterd_svc_t` represents an individual service with connection management, callbacks, mux linkage, process metadata, name, online flag, and init flag.

It declares low-level lifecycle APIs implemented in `glusterd-svc-mgmt.c`: run directory creation, service init/start/stop, path builders, reconfigure, RPC notify callbacks, mux connection initialization, pid lookup, and generic service start.

## Control Flow
The header provides the object model that service-specific modules fill in during build/init and later drive through manager/start/stop/reconfigure callbacks. Runtime event flow is from RPC notifications into `online` and mux status updates.

## State and Persistence Behavior
The structs hold runtime process and connection state only. Persistent service configuration is represented indirectly by generated volfiles and glusterd store files outside this header.

## Dependencies and Integration Points
It includes process management, connection management, and RCU/list support. It forward-declares `glusterd_volinfo_t` to avoid pulling all volume internals into every service-management user.

## Risks and Edge Cases
Because `glusterd_svc_t` embeds both callback policy and mutable runtime state, service modules must initialize all fields consistently. Mux process status must remain synchronized with process liveness and RPC events, or attach decisions can target dead or stopping processes.

## Test Signals
Build tests should cover all service modules embedding or using `glusterd_svc_t`. Runtime tests should assert state transitions for standalone and multiplexed services, including connect, disconnect, stop, abnormal death, and reattach decisions.

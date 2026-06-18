# sources/control-plane/mayastor/io-engine/src/grpc/v1/nexus.rs

Purpose: this v1 service implements typed nexus lifecycle, publication, child management, ANA, rebuild control, and rebuild history APIs. It is the main control-plane surface for Mayastor target devices.

Important APIs/types/functions: `NexusService` provides timeout-aware `serialized` locking. Conversion helpers map nexus status, child state/reason, rebuild state/stats/history, NVMe reservation and preemption options, and internal nexus objects to protobuf. Public helpers include `nexus_lookup` and `nexus_destroy`; private `nexus_add_child` validates duplicate URI/device names. RPC methods cover create/destroy/resize/shutdown/list, add/remove/fault child, publish/unpublish, ANA get/set, child operation, rebuild start/stop/pause/resume/state/stats/history/list-history.

Control flow: mutating calls build a `GrpcClientContext`, then `serialized` spawns a Tokio task, optionally takes the global lock, and takes a protected per-nexus lock before reactor submission. `create_nexus` validates name and UUID uniqueness, converts NVMe reservation parameters, stores optional nexus-info key, creates the nexus, generates an event, and returns the converted nexus. List paths can filter by name or UUID. Publish validates 16-byte keys and protocol, then calls `share_ext`.

State and persistence: mutates nexus in-memory/SPDK state, NVMf publication, children, rebuild jobs, ANA state, and rebuild history. `nexus_destroy` removes PTPL files when UUID parsing succeeds but lookup fails.

Dependencies and integration points: integrates internal `nexus`, `ResourceLockManager`, `rpc_submit`, rebuild records, eventing, device-name parsing, `NexusPtpl`, and v1 protobufs.

Risks: repeated lookups after mutation can race if invariants change despite locks; not-found destroy has PTPL side effects; action codes are numeric and invalid actions map to `InvalidKey`; list-history computes a default end time even with empty histories. Test signals should cover duplicate name/UUID rejection, child duplicate detection by URI and device name, publish protocol/key validation, event generation, lock timeout, rebuild history filters, and PTPL cleanup.

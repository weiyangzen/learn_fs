<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_windows.go

Purpose: Windows dataplane implementation for service load balancing through HNS/VFP policy lists.

Important APIs/types/functions: `policyLists`, global `lbPolicylistMap`, `Network.addLBBackend`, `Network.rmLBBackend`, `numEnabledBackends`, no-op `Sandbox.populateLoadBalancers`, and no-op `arrangeIngressFilterRule`.

Control flow: adding a backend finds the load balancer endpoint source VIP, resolves HNS endpoints for enabled backends, deletes any existing policy lists for the load balancer, creates an internal load balancer policy, then creates external policies for published ingress ports while coalescing matching TCP/UDP pairs to wildcard protocol where needed. Removing a backend reprograms policies if enabled backends remain; otherwise it deletes ILB/ELB policy lists and removes the map entry.

State and persistence: process-global map from `*loadBalancer` to HNS policy list handles; actual dataplane state lives in HNS/VFP.

Dependencies and integration points: Microsoft `hcsshim`, service common binding state, network endpoints, and Windows HNS endpoint names.

Risks and test signals: stale policy lists can survive if map state is lost; cleanup order matters because policy lists must be removed before HNS network deletion. Windows integration tests outside this subset provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_common.go

Purpose: shared Linux/Windows service discovery and service binding bookkeeping.

Important APIs/functions: endpoint/container DNS record add/delete helpers, `newService`, `getLBIndex`, `cleanupServiceDiscovery`, `cleanupServiceBindings`, `makeServiceCleanupFunc`, `addServiceBinding`, and `rmServiceBinding`.

Control flow: adding a service binding locks by network ID, creates/reuses a `service`, creates a per-network `loadBalancer` with fwmark, diffs service aliases against prior backend aliases, maintains VIP alias reference counts, records backend IP-to-endpoint mapping, programs network load balancer backend, and adds DNS records. Removal either disables or fully removes a backend, decrements alias refs, removes load-balancer service when last backend leaves, deletes DNS records when requested, and removes the service object only after all load balancers are gone.

State and persistence: in-memory controller maps for service bindings and service records. DNS records are maintained per network.

Dependencies and integration points: calls network `addSvcRecords/deleteSvcRecords`, `addLBBackend/rmLBBackend`, network locker, and `setmatrix`.

Risks and test signals: locking order avoids network deletion races; alias ref-counting prevents DNS flaps during rolling updates. Tests cover service discovery cleanup and alias ref-counting per network/rebind.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_unsupported.go

Purpose: fallback service/load-balancer stubs for platforms other than Linux and Windows.

Important APIs/functions: no-op cleanup functions, `addServiceBinding`/`rmServiceBinding` returning `"not supported"`, no-op `Sandbox.populateLoadBalancers`, and no-op `arrangeIngressFilterRule`.

Control flow: service binding calls fail immediately; cleanup/load-balancer hooks do nothing.

State and persistence: none.

Dependencies and integration points: selected by build tags to satisfy shared code references.

Risks and test signals: unsupported platforms cannot use swarm service binding/load balancing through this implementation. Build coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_unsupported.go -->

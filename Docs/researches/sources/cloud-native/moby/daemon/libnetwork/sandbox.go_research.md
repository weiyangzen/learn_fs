<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox.go

Purpose: core libnetwork `Sandbox`, the container-scoped network object that owns endpoints, resolver, OS namespace, DNS/hosts config, service enablement, and datastore state.

Important APIs/types/functions: `SandboxOption`, `Sandbox`, `containerConfig`, getters, `Delete`, `Rename`, `Refresh`, `UpdateLabels`, JSON marshal/unmarshal, endpoint list management, `populateNetworkResources`, DNS backend methods (`ResolveName`, `ResolveIP`, `ResolveService`, `HandleQueryResp`), `hasExternalAccess`, `EnableService`, `DisableService`, endpoint `Less`, and `NdotsSet`.

Control flow: deletion marks `inDelete`, leaves/deletes endpoints, stops resolver, destroys OS sandbox if owned, deletes store state, and removes controller map entry. Joining/populating resources delegates OS work, updates service records, default gateway, resolver forwarding, cluster driver info, and load balancers. Name resolution tries aliases before real names and, in swarm mode, sorts endpoints by network type.

State and persistence: in-memory guarded by `mu`, `joinLeaveMu`, and `service`; persisted through `sandbox_store.go`. Endpoint ordering affects gateway selection.

Dependencies and integration points: integrates with `osl`, networks/endpoints, service discovery, OpenTelemetry, etchosts, and scope constants.

Risks and test signals: concurrency around delete/join/leave and gateway ordering is subtle. Tests cover sandbox lookup, empty delete, endpoint priority, family-specific gateways, and same-priority ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox.go -->

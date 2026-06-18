<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/scope/scope.go -->
## sources/cloud-native/moby/daemon/libnetwork/scope/scope.go

Purpose: defines libnetwork datastore/network scope constants.

Important APIs/types/functions: constants `Local`, `Global`, and `Swarm`.

Control flow: none.

State and persistence: no state. Values are string labels used throughout libnetwork to classify network and datastore scope.

Dependencies and integration points: `Sandbox.populateNetworkResources` and restore logic use `scope.Swarm` to decide whether service records should be updated locally or handled by swarm/multihost control paths.

Risks and test signals: constants are stable API-like values; changing them would break comparisons and persisted/configured data. Test signal is indirect through network and service behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/scope/scope.go -->

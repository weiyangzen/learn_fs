<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_interfaces.go -->
# sources/cloud-native/moby/client/client_interfaces.go

Purpose: declares the public client interface graph for the Engine API. It groups endpoint methods by domain so callers can depend on narrower interfaces while `Client` satisfies the full `APIClient`.

Important APIs/types: `APIClient`, private `stableAPIClient`, `SwarmManagementAPIClient`, `HijackDialer`, and domain interfaces for checkpoint, container, exec, distribution, registry search, image build, image, network, node, plugin, service, task, swarm, system, volume, secret, and config operations.

Control flow and dependencies: this file has no runtime control flow. It imports `context`, `io`, and `net`, and refers to option/result types implemented throughout the package. `var _ APIClient = &Client{}` in `client.go` makes this file a compile-time contract for endpoint coverage.

State and integration behavior: no state or persistence. Integration risk is high because any method signature drift in endpoint files or generated API types breaks interface satisfaction and downstream compile-time compatibility.

Risks and test signals: the key risk is public API churn. Compile tests across the package are the primary signal; missing methods are caught by the `Client` interface assertion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_interfaces.go -->

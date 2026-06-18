<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor.go

Purpose: provides shared BuildKit executor networking helpers for Docker's libnetwork bridge integration and DNS config conversion.

Important APIs and control flow: `bridgeProvider.New` locates the Docker bridge network and creates an `lnInterface`. `lnInterface.init` creates an endpoint, sandbox, hosts/resolv paths, and joins the endpoint. `Close` asynchronously deletes the sandbox and network state directory. `DialContext` runs dialing inside the sandbox namespace. `getDNSConfig` and `ipAddresses` convert daemon DNS config into BuildKit OCI DNS config.

State and persistence: creates libnetwork endpoints/sandboxes and temporary network state files under the builder root. Cleanup removes sandbox directories asynchronously.

Dependencies and integration: used by Linux executor creation and BuildKit network providers. It integrates BuildKit network interfaces, Docker libnetwork, daemon DNS config, and resource sampling types.

Risks: asynchronous cleanup logs failures but does not block. `Sample` is stubbed. Network initialization happens in a goroutine and callers wait on `ready`, so error propagation depends on the `err` field.

Test signals: no direct tests in this subset; build networking integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor.go -->

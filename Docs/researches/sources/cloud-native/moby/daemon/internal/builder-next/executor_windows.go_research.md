# sources/cloud-native/moby/daemon/internal/builder-next/executor_windows.go

## Purpose
Constructs the Windows BuildKit executor and applies libnetwork endpoint data to OCI runtime specs.

## APIs, Control Flow, and Integration
`newExecutor` builds network providers for default/NAT and none modes, opens a containerd client using `containerdAddr` and namespace, then creates a `containerdexecutor.Executor` with DNS, CDI, proxy, root, network, and Hyper-V isolation options. `lnInterface.Set` waits for network readiness, extracts HNS endpoint IDs and unqualified DNS flags from libnetwork endpoints, and writes them into `specs.Windows.Network`.

## State, Dependencies, and Risks
State is external: containerd connectivity, libnetwork sandbox endpoint data, and runtime spec mutation. Risks include blocking on `iface.ready`, type assertions for driver info values, and missing endpoint metadata causing incomplete network specs. Test signals are indirect through Windows build/run behavior.

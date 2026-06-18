<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/updateunified/updateunified.go -->
# sources/cloud-native/cri-o/test/updateunified/updateunified.go

Purpose: small command-line helper to update cgroup v2 unified resource keys for a container through the CRI `UpdateContainerResources` RPC.

Important flow: validates arguments as `<socket> <container-id> <key=value>...`, parses remaining arguments into a `map[string]string`, creates an insecure Unix gRPC client to the CRI-O socket, constructs a 30-second context, and sends `UpdateContainerResourcesRequest` with `Linux.Unified` set to the parsed map.

State and integration: writes container resource state through CRI-O; no local persistence. Dependencies are CRI API and local Unix socket access. Risks include no validation of unified keys/values beyond `key=value`, no blocking dial, and updates being kernel/cgroup-manager dependent. Test signal is used by cgroup unified integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/updateunified/updateunified.go -->

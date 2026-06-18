<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry.go

Purpose: provides registry reference utilities and authenticated go-containerregistry transports.

Important APIs/types: `Image`, `ConvertToVPCHost`, `ParseImage`, `ParseLabels`, and `AuthnTransport`. `ConvertToVPCHost` inserts `-vpc` into the first DNS label unless already present. `ParseImage` returns registry host and repository path from a Docker reference. `ParseLabels` extracts target ref and target layer digest from containerd snapshot labels. `AuthnTransport` resolves credentials and creates a scoped registry transport with a 10-second timeout wrapper.

Control flow and state: functions are stateless. `AuthnTransport` treats nil or nil-pointer keychains as anonymous auth, resolves otherwise, and runs `transport.NewWithContext` in a goroutine to enforce a coarse timeout.

Dependencies/integration: uses distribution/reference, go-containerregistry name/auth/transport, containerd snapshotter labels, HTTP RoundTripper, and project callers such as transport pool and remote fetch code.

Risks and test signals: `ConvertToVPCHost` assumes a non-empty dotted host. The goroutine timeout in `AuthnTransport` can leave the goroutine running after returning timeout. Tests cover VPC host conversion and image parsing, but not auth transport timeout/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry.go -->

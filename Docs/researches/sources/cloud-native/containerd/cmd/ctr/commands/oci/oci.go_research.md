# sources/cloud-native/containerd/cmd/ctr/commands/oci/oci.go

Purpose: implements `ctr oci spec`, printing the default generated OCI runtime spec for a platform.

Important APIs/functions: `Command` parent and `defaultSpecCommand`.

Control flow: creates app context, chooses the requested platform or the default platform string, calls `oci.GenerateSpecWithPlatform(ctx, nil, platform, &containers.Container{})`, and prints the spec as JSON.

State and persistence: read-only/generated output; no daemon client is required.

Dependencies/integration: containerd OCI spec generator, core container type, platform defaults, shared JSON/context helpers.

Risks: output depends on platform-specific defaults and current OCI generator behavior. Empty container input means this is a baseline spec, not image/container-specific.

Test signals: no local tests.

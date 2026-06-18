# sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer.go

Purpose: connection helper for `nerdctl-container://<container>` URLs, connecting to BuildKit inside a nerdctl-managed container.

Important APIs/types/functions: `init` registers `nerdctl-container`. `Helper` creates a dialer running `nerdctl exec [--namespace <namespace>] -i <container> buildctl dial-stdio`. `Spec` stores container and namespace. `SpecFromURL` extracts hostname and optional `namespace` query value.

Control flow: parser rejects missing container name. Dialer appends namespace arguments only when non-empty, then delegates to `commandconn.New` with background context.

State and persistence: no persistent state except registration. Runtime behavior depends on nerdctl/containerd namespace and target container availability.

Dependencies/integration points: Docker CLI `commandconn`, shared `connhelper`, `nerdctl`, and BuildKit’s `dial-stdio` command.

Risks/test signals: namespace value is not validated and command behavior is external. Cancellation semantics mirror other helpers through background context. Tests currently cover only basic container and missing-container parsing, not namespace extraction or subprocess arguments.

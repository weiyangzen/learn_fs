# sources/cloud-native/containerd/cmd/ctr/commands/images/inspect.go

Purpose: implements `ctr images inspect`, printing an image tree and optional content JSON.

Important APIs/functions: `inspectCommand`.

Control flow: creates client/context, reads the image ref, fetches image metadata from image service, builds display printer options with stdout and optional verbose content, and prints the image tree using the content store.

State and persistence: read-only image/content access.

Dependencies/integration: `pkg/display` image tree printer, image service, content store.

Risks: no explicit empty-ref validation before image lookup, so errors depend on image service behavior.

Test signals: no local tests.

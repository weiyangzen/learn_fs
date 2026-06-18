# sources/cloud-native/containerd/cmd/ctr/commands/install/install.go

Purpose: implements `ctr install`, installing binaries/libs from an image into an opt-style managed path.

Important APIs/functions: `Command` with `--libs`, `--replace`, and `--path`.

Control flow: creates client/context, reads image ref, loads the image, builds install options from flags, and calls `client.Install(ctx, image, opts...)`.

State and persistence: writes files through containerd install implementation, potentially replacing existing binaries/libs and using an alternate path.

Dependencies/integration: containerd client install APIs and shared client helper.

Risks: no command-local validation that ref is non-empty; errors come from image lookup. Replacement/path semantics are delegated to client install implementation.

Test signals: no local tests.

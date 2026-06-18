# sources/cloud-native/containerd/cmd/containerd/main.go

Purpose: process entrypoint for the `containerd` binary.

Important APIs/functions: `main()` constructs `command.App()` and runs it with `os.Args`. The blank import of `cmd/containerd/builtins` registers built-in plugins.

Control flow: errors from the CLI app are printed to stderr as `containerd: <err>` and exit code 1 is returned.

State and persistence: no local state; plugin registration happens through imported package init functions.

Dependencies/integration: integrates daemon command package and builtins plugin registration.

Risks: if builtins import is removed, server plugin graph will be incomplete. Error formatting is intentionally minimal.

Test signals: no local tests; behavior is entrypoint glue.

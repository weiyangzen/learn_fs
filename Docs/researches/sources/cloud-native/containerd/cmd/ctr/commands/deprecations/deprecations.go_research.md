# sources/cloud-native/containerd/cmd/ctr/commands/deprecations/deprecations.go

Purpose: implements `ctr deprecations list`, printing deprecation warnings recorded by the server.

Important APIs/types/functions: `Command`, `listCommand`, `deprecationWarning`, `warnings()`, and `deprecationWarningFromPB()`.

Control flow: command sets `CONTAINERD_SUPPRESS_DEPRECATION_WARNINGS=1` to prevent `NewClient()` from printing warnings automatically, fetches introspection server info, converts protobuf warnings, and prints JSON or a tabular default format.

State and persistence: reads server introspection state; mutates process environment for the command process.

Dependencies/integration: containerd introspection API, shared client/JSON helper, protobuf timestamp conversion, tabwriter.

Risks: setting the environment is process-global and can affect later operations in the same process. Unknown format values fall back to default table behavior.

Test signals: no local tests.

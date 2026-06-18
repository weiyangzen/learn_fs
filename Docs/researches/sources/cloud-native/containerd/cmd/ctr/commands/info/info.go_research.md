# sources/cloud-native/containerd/cmd/ctr/commands/info/info.go

Purpose: implements `ctr info`, printing server introspection info as JSON.

Important APIs/types/functions: `Info` wrapper struct and `Command`.

Control flow: creates client/context, calls `client.IntrospectionService().Server(ctx)`, stores response in `Info.Server`, and prints JSON.

State and persistence: read-only server introspection.

Dependencies/integration: introspection API and shared JSON/client helpers.

Risks: output is directly tied to server protobuf shape.

Test signals: no local tests.

# Research: sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.proto

## sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.proto

Purpose: defines the protobuf schema for Docker plugin runtime specs stored in SwarmKit generic task payloads.

The schema has `PluginSpec` with fields `name`, `remote`, repeated `PluginPrivilege privileges`, `disabled`, and repeated `env`; and `PluginPrivilege` with `name`, `description`, and repeated `value`. This mirrors `swarm.RuntimeSpec` and `swarm.RuntimePrivilege` enough for plugin service creation and controller execution.

There is no runtime state. Integration points are `gen.go`, generated `plugin.pb.go`, `convert.go`, service create/update validation for plugin runtime, and the plugin controller. Risks are backward-compatibility of field numbers and limited schema expressiveness if plugin runtime options expand. Test signal is indirect through generated-code compilation and plugin runtime behavior.

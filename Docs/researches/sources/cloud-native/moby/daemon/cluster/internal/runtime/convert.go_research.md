# Research: sources/cloud-native/moby/daemon/cluster/internal/runtime/convert.go

## sources/cloud-native/moby/daemon/cluster/internal/runtime/convert.go

Purpose: converts Docker API swarm plugin runtime specs to and from the generated internal protobuf `PluginSpec` used as a generic runtime payload.

Important APIs are `FromAPI`, `ToAPI`, `privilegesFromAPI`, and `privilegesToAPI`. Control flow copies name, remote reference, disabled flag, environment values, and repeated runtime privileges between API structs and protobuf structs. The conversion preserves order and does not perform validation or deep normalization.

State is none. Dependencies are `github.com/moby/moby/api/types/swarm` and generated types from `plugin.pb.go`. Integration points are service create/update paths for `RuntimePlugin` and the plugin controller path selected by the container executor. Risks include nil privilege entries causing panics if ever present, lack of validation, and schema drift between API runtime spec and proto fields. No direct tests are in this subset.

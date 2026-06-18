# sources/cloud-native/containerd/api/events/namespace.proto

Purpose: protobuf schema for namespace lifecycle events in containerd.

Important APIs/types/functions: package `containerd.events`, Go package `api/events;events`. Defines `NamespaceCreate`, `NamespaceUpdate`, and `NamespaceDelete`; create/update include `name` and `labels`, delete includes `name`. Enables fieldpath generation with `(containerd.types.fieldpath_all) = true`.

Control flow: declarative schema used by code generation and event serialization. No executable control flow.

State/persistence: persistent API state is the message names and field numbers. Labels are represented as a string map.

Dependencies/integration: depends on `types/fieldpath.proto`; integrates with namespace metadata mutation paths and event subscription/filtering.

Risks/test signals: renaming or renumbering fields would break wire compatibility and event filters. Tests should confirm create/update include label changes and delete events remain minimal.

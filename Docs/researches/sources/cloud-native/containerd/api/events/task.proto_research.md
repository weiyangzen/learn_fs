# sources/cloud-native/containerd/api/events/task.proto

Purpose: source protobuf schema for container task events.

Important APIs/types/functions: package `containerd.events`, Go package `api/events;events`. Defines lifecycle messages for task create/start/delete/exit/OOM/pause/resume/checkpoint plus exec add/start and `TaskIO`. It imports timestamps, fieldpath options, and mount types.

Control flow: declarative API contract; runtime task service code publishes messages as task state changes occur. `TaskDelete` comment defines an important convention: empty `id` matches the init exec for the task.

State/persistence: wire field numbers and message names are the persistent event schema. `rootfs` embeds `containerd.types.Mount`; timestamps encode exit time.

Dependencies/integration: integrates with task runtime implementations, containerd event service, mount type schema, and fieldpath filtering.

Risks/test signals: changing `id` semantics would break exec lifecycle consumers. Tests should cover all event variants, fieldpath generation, timestamp fields, and compatibility with historical task event payloads.

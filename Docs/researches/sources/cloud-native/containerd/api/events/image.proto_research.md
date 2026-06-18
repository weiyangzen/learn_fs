# sources/cloud-native/containerd/api/events/image.proto

Purpose: source protobuf schema for containerd image events. It defines public event payloads for image creation, update, and deletion.

Important APIs/types/functions: package is `containerd.services.images.v1` while the Go package is `github.com/containerd/containerd/api/events;events`. `ImageCreate` and `ImageUpdate` contain `name` and `labels`; `ImageDelete` contains `name`. The file imports `types/fieldpath.proto` and sets `(containerd.types.fieldpath_all) = true` so fieldpath accessors are generated.

Control flow: declarative schema only; flow is event producer populates these messages, the event system serializes them, and consumers decode them by message type/topic.

State/persistence: no local state. The schema defines wire compatibility, so field numbers are persistent API state.

Dependencies/integration: integrates with the images service event stream and generated Go/fieldpath code. The package name differs from the other event protos, tying image events to the images service namespace.

Risks/test signals: wire compatibility depends on not renumbering or changing field types. Label fieldpath lookup joins path segments after `labels`, so dotted label keys are supported by convention. Testing should cover create/update/delete event publication and fieldpath filtering by `name` and labels.

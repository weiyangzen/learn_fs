# sources/cloud-native/containerd/api/events/image.pb.go

Purpose: generated Go protobuf bindings for `events/image.proto`, exporting image lifecycle event payloads in package `events`. It represents `ImageCreate`, `ImageUpdate`, and `ImageDelete` as protobuf messages used by containerd event publishers/subscribers.

Important APIs/types/functions: `ImageCreate` and `ImageUpdate` carry `Name` plus `Labels map[string]string`; `ImageDelete` carries only `Name`. Each type implements generated protobuf methods (`Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`) and nil-safe getters (`GetName`, `GetLabels`). The file-level descriptor `File_events_image_proto`, raw descriptor compression helper, message info table, dependency indexes, and `file_events_image_proto_init` wire the types into `google.golang.org/protobuf`.

Control flow: runtime behavior is limited to protobuf reflection and getters. `ProtoReflect` stores message info when unsafe protobuf support is enabled; `rawDescGZIP` lazily compresses descriptor bytes with `sync.Once`; `init` builds the descriptor once and nils raw metadata after registration.

State/persistence: no durable storage or business state is managed here. State is serialized only when callers marshal event messages; label map entries are encoded as generated map-entry messages.

Dependencies/integration: imports protobuf reflection/runtime packages and blank-imports `github.com/containerd/containerd/api/types` so the fieldpath extension referenced by the proto is linked. Integrates with containerd's event exchange and any code that unmarshals image event topics.

Risks/test signals: this file is generated and should be regenerated from `image.proto` rather than edited. Compatibility risk is field-number drift, especially `labels = 2`; consumer risk is assuming `GetLabels` returns a non-nil map. No direct tests in this subset; confidence comes from protobuf generation and downstream event serialization tests.

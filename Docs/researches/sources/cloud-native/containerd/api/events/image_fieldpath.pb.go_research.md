# sources/cloud-native/containerd/api/events/image_fieldpath.pb.go

Purpose: generated fieldpath helpers for image event messages. These helpers let event filters query selected protobuf fields as strings.

Important APIs/types/functions: `(*ImageCreate).Field`, `(*ImageUpdate).Field`, and `(*ImageDelete).Field` accept a `[]string` path and return `(value, true)` when the field is present. They support `name`; create/update additionally support `labels.<key>` by joining remaining path components with `"."`.

Control flow: each method rejects empty fieldpaths, switches on the first component, performs simple non-empty checks for string fields, and returns map lookup results for labels. Unknown paths return `("", false)`.

State/persistence: no state is stored. Results are computed from the message instance.

Dependencies/integration: imports `strings` only for label key reconstruction. Integrates with containerd event filtering generated from the `fieldpath_all` option in `image.proto`.

Risks/test signals: label lookup is explicitly special-cased and could break if label semantics change. Empty string values are treated as absent for `name`; map entries with empty values still return `true` if the key exists. Tests should exercise dotted label keys and empty message cases.

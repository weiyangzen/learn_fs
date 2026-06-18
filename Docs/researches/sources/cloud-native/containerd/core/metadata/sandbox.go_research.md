# sources/cloud-native/containerd/core/metadata/sandbox.go

Purpose: implements the bbolt-backed sandbox metadata store for create, update, get, list, delete, validation, and serialization of sandbox runtime/spec/extension fields.

Important APIs and types: `sandboxStore`, `NewSandboxStore`, `Create`, `Update`, `Get`, `List`, `Delete`, and internal `write`, `read`, `validate`. The type asserts it implements `sandbox.Store`.

Control flow: public methods require a namespace. `Create` starts a tracing span, stamps timestamps, validates ID/timestamps, creates the sandbox bucket, and writes the sandbox without overwrite. `Update` reads the existing sandbox, defaults to updating labels/extensions/spec/runtime when no fieldpaths are provided, forbids changing runtime name in the no-fieldpaths path, applies selected full or dotted field updates, refreshes `UpdatedAt`, and writes with overwrite. `Get` and `List` read buckets through view transactions, with `List` applying parsed filters. `Delete` deletes the sandbox bucket and maps missing buckets to not found.

State and persistence: each sandbox is a bucket under `v1/<namespace>/sandboxes/<id>`. Timestamps, labels, extensions, and `Any` spec/options use `boltutil`. Runtime data is nested under a runtime bucket, with name and options. `Sandboxer` is stored as a direct key and defaults to empty when absent for compatibility.

Dependencies and integration: depends on `core/sandbox`, `boltutil`, filters, identifiers, namespaces, tracing, errdefs, typeurl, and bbolt. It integrates with metadata GC through sandbox labels and with tracing through `metadata.sandbox.*` spans.

Risks: `Update` does not call `validate` before writing directly, but `write` revalidates. Dotted field updates can set map entries to zero values when the input map lacks the key. Full update without fieldpaths allows replacing runtime options but rejects runtime name changes only in that path; explicit `runtime` fieldpath can replace the runtime struct.

Test signals: `sandbox_test.go` covers create/get, duplicate create, fieldpath update, get missing ID, list, filter list, delete, and comparison ignoring timestamps.

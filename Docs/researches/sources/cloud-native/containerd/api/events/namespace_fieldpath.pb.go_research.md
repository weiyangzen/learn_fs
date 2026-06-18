# sources/cloud-native/containerd/api/events/namespace_fieldpath.pb.go

Purpose: generated fieldpath accessors for namespace events.

Important APIs/types/functions: `Field` methods exist for `NamespaceCreate`, `NamespaceUpdate`, and `NamespaceDelete`. They expose `name` for all messages and `labels.<key>` for create/update by joining remaining path segments.

Control flow: methods guard against empty paths, switch on the first path segment, check non-empty string fields, and perform map lookups.

State/persistence: stateless derived access over message fields.

Dependencies/integration: imports `strings`; produced from `namespace.proto` fieldpath options. Event filter code can use these helpers to match namespaces by name or labels.

Risks/test signals: dotted label keys depend on `strings.Join(fieldpath[1:], ".")`. Empty string names are considered undefined. Tests should cover absent labels, empty label maps, and label keys containing dots.

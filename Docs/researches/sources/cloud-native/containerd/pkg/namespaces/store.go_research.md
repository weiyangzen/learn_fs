# sources/cloud-native/containerd/pkg/namespaces/store.go

Purpose: defines the metadata-store interface for namespace records.

Important APIs/types/functions: `Store` exposes `Get`, `List`, `Create`, `Update`, `Delete`, `SetLabel`, and `Labels`. `DeleteInfo` carries a `Synchronous` flag. `DeleteOpts` mutates `DeleteInfo` during delete operations.

Control flow: interface-only file. Implementations decide persistence, filtering, update semantics, and asynchronous vs synchronous deletion.

State/persistence: the interface represents persisted namespace metadata and labels. This file stores nothing directly.

Dependencies/integration: imports API `types.Namespace` and `filters`. Containerd metadata backends implement this interface; higher-level services use it to manage namespace lifecycle and labels.

Risks: label validation, delete synchronization, and filter semantics are delegated to implementations. Callers must not assume delete completion unless a synchronous option is supported and requested.

Test signals: implementation tests should cover create/update/delete semantics, filtering, labels, and deletion modes. This file is compile-time contract surface.

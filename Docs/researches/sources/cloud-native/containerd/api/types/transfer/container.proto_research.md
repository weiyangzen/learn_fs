<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.proto -->
# sources/cloud-native/containerd/api/types/transfer/container.proto

Purpose: schema for identifying a filesystem path inside an active container as a transfer source or destination.

Important APIs/types/functions: `ContainerPath` defines `container_id`, `path`, `no_walk`, and `preserve_ownership`.

Control flow: schema-only; comments define traversal and extraction ownership behavior.

State/persistence: transfer request metadata only; actual filesystem state lives in the container/snapshot.

Dependencies/integration: `go_package` maps to transfer API types. Transfer service implementations use it to archive/extract container paths.

Risks: schema does not constrain absolute/relative paths, symlink behavior, or uid/gid validity. Consumers must enforce namespace and permission rules.

Test signals: generated binding consistency and transfer integration around directory traversal and ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/container.pb.go

Purpose: generated Go binding for transfer endpoints that refer to paths inside active containers.

Important APIs/types/functions: `ContainerPath` has `ContainerID`, `Path`, `NoWalk`, and `PreserveOwnership` with standard generated methods/getters.

Control flow: no operational flow beyond protobuf descriptor init and getters.

State/persistence: serialized as transfer source/destination metadata for archive-like operations. `NoWalk` changes directory traversal semantics; `PreserveOwnership` affects extraction ownership semantics.

Dependencies/integration: package `transfer`, generated from `container.proto`; consumed by transfer service/proxy layers that copy data to/from container filesystems.

Risks: path interpretation is delegated to transfer implementation and must avoid traversal/symlink surprises. Ownership preservation has privilege and user namespace implications. `ContainerID` must resolve in the active namespace.

Test signals: transfer tests should cover stat-like `NoWalk`, recursive walk, ownership preservation, missing container/path, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.pb.go -->

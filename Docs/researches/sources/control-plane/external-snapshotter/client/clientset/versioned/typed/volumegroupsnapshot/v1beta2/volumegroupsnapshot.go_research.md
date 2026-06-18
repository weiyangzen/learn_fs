# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go

Purpose: real typed client for namespaced v1beta2 `VolumeGroupSnapshot`.
Important APIs/types/functions: standard Kubernetes resource interface with status update and expansion hook; concrete generic client.
Control flow: `newVolumeGroupSnapshots` creates `gentype.ClientWithList` for `volumegroupsnapshots` in a namespace with v1beta2 factories.
State/persistence: Kubernetes API server stores objects; client has only REST endpoint and namespace.
Dependencies/integration: used by `GroupsnapshotV1beta2Client` and controllers that target v1beta2 group snapshot API.
Risks/test signals: v1beta2 is storage version in the CRD; tests should check status subresource, namespace URLs, and server-side schema compatibility.

# sources/control-plane/external-snapshotter/client/clientset/versioned/typed/volumegroupsnapshot/v1beta2/fake/fake_volumegroupsnapshot_client.go

Purpose: fake top-level group client for v1beta2 group snapshot resources.
Important APIs/types/functions: `FakeGroupsnapshotV1beta2`, accessors for namespaced snapshots and cluster-scoped classes/contents, nil `RESTClient`.
Control flow: each accessor constructs its resource fake over the same `testing.Fake`.
State/persistence: shared in-memory fake state.
Dependencies/integration: used by fake versioned clientsets in controller tests.
Risks/test signals: ensure tests use reactors/object tracker rather than REST. Validate accessor versions and root/namespaced split.

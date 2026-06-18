## sources/cloud-native/buildkit/util/leaseutil/manager.go

Purpose: helper layer for containerd leases, including temporary lease creation, adoption into an existing lease, and namespace-scoped lease manager wrapper.

Important APIs/types: `WithLease(ctx,manager,opts...)`, `NewLease`, `LeaseRef{Discard,Adopt}`, `MakeTemporary`, `WithNamespace`, and `Manager` methods implementing lease manager operations with a fixed namespace.

Control flow: `WithLease` is a no-op if the context already carries a lease; otherwise it creates one and returns a delete callback. `NewLease` applies random ID and default one-hour expiration before caller opts. `Adopt` lazily lists resources once, requires a current lease in target context, adds each resource to the current lease, discards empty leases immediately, and asynchronously discards adopted non-empty source leases. `Discard` uses `context.WithoutCancel`.

State/persistence: creates/deletes/adopts real containerd lease records and resources. `LeaseRef` caches listed resources and first error under `sync.Once`. Dependencies: containerd leases/namespaces, `time`, `pkg/errors`.

Integration points: image/content cache lifetime management. Risks: asynchronous discard errors are ignored; resource list is cached even if adoption happens much later; namespace wrapper assumes all calls should be forced into its namespace. Test signals: no local tests in this subset.

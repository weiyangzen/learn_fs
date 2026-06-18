<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/leases.go -->
# sources/cloud-native/moby/daemon/containerd/leases.go

Purpose: centralizes temporary containerd lease creation for image operations that must protect content or snapshots from garbage collection.

Important APIs and flow: constants define an eight-hour expiration, the containerd GC expiration label, a Moby prune label, and a prune filter. `ImageService.withLease` reuses an existing lease in the context when present; otherwise it creates a random lease labeled for prune and expiration, attaches it to the context, and returns a cleanup function. If `cancellable` is true and the operation context was canceled, cleanup intentionally leaves the lease until expiration/prune.

State and persistence: creates and deletes containerd leases. Leases left after cancellation protect partially pulled resources and are later targeted by image prune via `pruneLeaseFilter`.

Dependencies and integration: used by pull and other image operations; prune deletes leases with the Moby prune label. It depends on containerd leases service and logging.

Risks: leaked leases can retain content until expiration or prune. Cleanup logs but does not return delete failures. Expiration is label-based, so correctness depends on containerd/prune respecting that metadata.

Test signals: no direct tests in this subset; cancellation/lease expiry behavior needs integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/leases.go -->

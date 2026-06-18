# sources/control-plane/rook/tests/framework/clients/cosi.go

Purpose: `COSIOperation` wraps COSI test resources for Rook Ceph object storage, including the COSI driver, bucket classes, and bucket claims.

Important APIs/types/functions: constructor `CreateCOSIOperation`; `CreateCOSI`/`DeleteCOSI`; `CreateBucketClass`/`DeleteBucketClass`; `CreateBucketClaim`/`DeleteBucketClaim`.

Control flow: every method renders a manifest from `CephManifests` and calls `K8sHelper.ResourceOperation` with `create` or `delete`. There is no polling or status validation in this layer.

State and persistence behavior: persistent state is Kubernetes CRs for `CephCOSIDriver`, `BucketClass`, and `BucketClaim`. The wrapper itself has no state beyond helper references.

Dependencies and integration points: depends on the objectstorage API manifests emitted by `CephManifestsMaster`, the Rook operator namespace for COSI driver resources, and Kubernetes resource application through kubectl.

Risks: using `create` makes repeated test setup non-idempotent. Delete methods render the same manifest and rely on Kubernetes object identity, so parameter drift can delete or fail unexpectedly. No wait or readiness check means callers must separately verify COSI controller reconciliation.

Test signals: callers should check CR existence, status readiness, bucket provisioning, credentials/secrets, and cleanup of external object state after deletion.

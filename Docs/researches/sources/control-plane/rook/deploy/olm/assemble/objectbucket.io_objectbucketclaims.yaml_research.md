# sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbucketclaims.yaml

Purpose: provides the OLM-assembled CRD for ObjectBucketClaim.

Important APIs/types/functions: `CustomResourceDefinition/objectbucketclaims.objectbucket.io`, group `objectbucket.io`, namespaced scope, kind `ObjectBucketClaim`, short name `obc`, version `v1alpha1`, schema for `spec.storageClassName`, `bucketName`/`generateBucketName`, and status subresource.

Control flow: Kubernetes API server uses the CRD to accept OBC resources; bucket provisioners watch OBCs to create ObjectBuckets and credentials.

State and persistence: OBCs persist claim intent and binding status in etcd.

Dependencies/integration: used by Rook's bucket provisioner and lib-bucket-provisioner semantics.

Risks: OLM assembly must remain aligned with upstream objectbucket schema; overly loose schema can allow invalid claims.

Test signals: CRD installs, OBCs pass validation, and status updates are accepted.

# sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbuckets.yaml

Purpose: provides the OLM-assembled CRD for cluster-scoped ObjectBucket resources.

Important APIs/types/functions: `CustomResourceDefinition/objectbuckets.objectbucket.io`, cluster scope, kind `ObjectBucket`, short name `ob`, version `v1alpha1`, schema for endpoint, claim reference, storage class, reclaim policy, and status.

Control flow: bucket provisioners create/update ObjectBuckets in response to OBCs; the API server validates and stores those cluster-scoped bindings.

State and persistence: ObjectBuckets represent provisioned backend bucket bindings and store status in etcd.

Dependencies/integration: consumed by object bucket provisioner controllers and OBC lifecycle.

Risks: cluster-scoped objects need careful RBAC; schema drift from objectbucket upstream can break OLM installs.

Test signals: CRD install, ObjectBucket creation by OBC provisioning, and status subresource updates.

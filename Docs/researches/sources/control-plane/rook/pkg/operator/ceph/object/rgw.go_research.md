# sources/control-plane/rook/pkg/operator/ceph/object/rgw.go

Purpose: manages RGW Kubernetes deployment lifecycle and supporting CephX/config artifacts for a `CephObjectStore`, plus DNS/TLS helper functions for object-store access.

Important APIs/types: `clusterConfig`, `rgwConfig`, `createOrUpdateStore`, `startRGWPods`, `deleteStore`, `deleteRgwCephObjects`, `instanceName`, `storeLabelSelector`, `validateStore`, `generateSecretName`, `EmptyPool`, `GetStableDomainName`, `getAllDomainNames`, `getAllDNSEndpoints`, `ParseDomainName`, `BuildDNSEndpoint`, `GetTlsCaCert`, and `genObjectStoreHTTPClient`.

Control flow: `createOrUpdateStore` starts RGW pods, creates a multisite context, and enables/disables dashboard integration according to cluster and store settings. `startRGWPods` normalizes gateway instances, checks skip-reconcile labels, generates one RGW deployment/keyring/config set, applies mon config flags, creates or updates the deployment with owner refs and keyring resource-version annotations, generates mime types, and cleans up extra deployments/secrets/Ceph objects if scaling down. `deleteStore` removes RGW CephX/config artifacts, disables dashboard, and calls realm/pool deletion if a multisite context can be built. TLS helpers load certs from referenced Secrets or service-serving CA files.

State and persistence: persists Kubernetes Deployments and Secrets, CephX auth users, centralized mon config, mime type config, dashboard RGW settings, and object-store realm/pool cleanup through objectstore helpers. Reads TLS cert data from Kubernetes Secrets or filesystem.

Dependencies and integration points: integrates deployment generation methods in the same package, Ceph mon deployment update helper, keyring annotations, Rook config and owner refs, Kubernetes apps/core clients, object context creation, dashboard helpers in `objectstore.go`, and S3/Admin Ops HTTP client setup.

Risks: current code forces a single deployment (`desiredRgwInstances := 1`) while gateway instances are used as replica count elsewhere, so scale semantics are subtle. Deletion is best-effort and logs many failures. TLS behavior depends on Secret type/key conventions and optional `insecureSkipVerify`. `createOrUpdateStore` logs and returns nil if `NewMultisiteContext` fails after pods start, which can hide dashboard setup failure.

Test signals: `rgw_test.go` covers deployment creation, basic create/update with and without Keystone/S3 settings, keyring secret naming, empty pool detection, DNS endpoint construction, and TLS CA Secret behavior.

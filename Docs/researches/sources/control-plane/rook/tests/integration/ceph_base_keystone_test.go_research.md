# sources/control-plane/rook/tests/integration/ceph_base_keystone_test.go

Keystone, Swift, and S3 authentication integration support for RGW. It installs an in-cluster Keystone stack with TLS, creates OpenStack client deployments, configures Swift endpoints, and validates authorized and unauthorized object workflows.

Important functions include `InstallKeystoneInTestCluster`, `initializePasswords`, manifest builders for Keystone/cert-manager/trust-manager/OpenStack clients, `CleanUpKeystoneInTestCluster`, `runSwiftE2ETest`, `runS3E2ETest`, `prepareE2ETest`, `cleanupE2ETest`, and `testInOpenStackClient`. Setup installs cert-manager and trust-manager via Helm, applies issuers/certificates/bundles, creates Keystone config/Apache resources, deploys Keystone, waits for readiness, and creates one OpenStack client deployment per test user.

State includes Helm releases, CRDs, certificate resources, TLS secrets, Keystone SQLite data on `emptyDir`, OpenStack client deployments, Keystone users/projects/roles/services/endpoints, CephObjectStores, Swift containers, and S3 objects. Dependencies include external Helm repos/images, OpenStack CLI, AWS CLI, jq, Rook object helpers, and Kubernetes clients.

Risks: large external network/supply-chain footprint, passwords embedded in pod env/YAML for tests, cleanup intentionally leaves cert-manager resources, target client readiness can be missed because command helper waits on the admin client label, and shell output formats are assumed. Test signals are Helm/install success, pod readiness, OpenStack command success/failure, object upload/download/diff, negative Mallory authorization, admin Carol access, endpoint cleanup, AWS S3 operations, and object-store deletion.

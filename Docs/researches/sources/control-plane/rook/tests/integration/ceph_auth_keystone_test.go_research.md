# sources/control-plane/rook/tests/integration/ceph_auth_keystone_test.go

Purpose: this integration suite validates Rook RGW object store authentication through OpenStack Keystone for object-store creation, Swift access, and S3 access.

Important APIs/types/functions: `TestCephKeystoneAuthSuite`; suite type `KeystoneAuthSuite`; lifecycle methods `SetupSuite`, `TearDownSuite`, `AfterTest`; tests `TestObjectStoreOnRookInstalledViaHelmUsingKeystone`, `TestWithSwiftAndKeystone`, `TestWithS3AndKeystone`; helper `cleanUpTLSks`.

Control flow: setup creates Helm-based Rook settings in namespace `keystoneauth-ns`, enables discovery, hostname changes, encrypted connections, and cleanup, starts the test cluster, installs Keystone, creates a `usersecret` with OpenStack auth environment keys from generated test user data, and creates the shared `TestClient`. Tests set `swiftAndKeystone=true`, use non-TLS object stores, and call broader object/Swift/S3 E2E helpers. Teardown cleans Keystone, deletes the user secret with timeout, and uninstalls Rook. `AfterTest` collects operator logs when configured or on failure.

State and persistence behavior: creates a full Rook/Ceph cluster, Keystone deployment, Kubernetes secret with OpenStack credentials, object stores, TLS secrets from called helpers, buckets/containers/objects, and logs. Teardown attempts to remove these resources unless failure cleanup policy keeps them.

Dependencies and integration points: depends on clients, installer, K8s helper, Keystone setup helpers from sibling files, object E2E helpers, OpenStack CLI/AWS client behavior, cert-manager/trust-manager setup, and Yaook Keystone image assumptions.

Risks: heavyweight external integration has many flake points: Helm install, image pulls, Keystone readiness, generated credentials, certificate distribution, object store reconciliation, and client CLIs. `cleanUpTLSks` calls `logger.Fatal` on unexpected secret deletion failure, which can abort abruptly. The namespace/operator namespace are the same, which exercises a specific deployment topology.

Test signals: successful cluster setup, Keystone installation, usersecret creation, RGW object store with Keystone auth, Swift container/object operations, S3 operations with Keystone, invalid credential rejection in called helpers, and clean teardown/log collection.

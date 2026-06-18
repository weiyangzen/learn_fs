<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/caps/caps.go -->
# sources/control-plane/rook/tests/integration/object/user/caps/caps.go

Purpose: integration test for `CephObjectStoreUser.spec.capabilities` reconciliation into RGW user caps. It creates a test namespace and one `CephObjectStoreUser` against a shared object store, then verifies default, configured, and removed capability states.

Important APIs and control flow: `TestObjectStoreUserCaps` uses Rook and Kubernetes clients, creates the namespace and user, polls until `ConditionReady`, builds a go-ceph RGW admin client via `util/admin.NewAdminClient`, reads the RGW user with `adminClient.GetUser`, updates `Spec.Capabilities` to buckets `*` and usage `read`, then sets capabilities back to nil. The comparison uses `go-cmp` against `[]admin.UserCapSpec`.

State, persistence, and integration: persistent state lives in the `CephObjectStoreUser` CR and RGW user record. The test depends on a non-TLS object store, the shared RGW admin credentials, and Rook reconciliation of caps. Risks are order-sensitive cap comparison and polling timeouts against slow RGW/operator startup. Test signals include empty default caps, exact configured caps, return-to-empty behavior, successful CR deletion, empty user list, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/caps/caps.go -->

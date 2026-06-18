# sources/control-plane/rook/tests/integration/ceph_cosi_test.go

COSI integration coverage for Rook's Ceph COSI driver. `testCOSIDriver` installs upstream COSI API/controller kustomize manifests, creates a Ceph object store/user, creates the CephCOSIDriver, BucketClass, and BucketClaim, verifies COSI Bucket readiness and backend RGW bucket creation, then cleans everything up.

State includes cluster-level COSI CRDs/controllers, CephObjectStore, CephCOSIDriver, COSI driver deployment, CephObjectStoreUser/secret, BucketClass, BucketClaim, Bucket, and backend RGW bucket. Dependencies include upstream GitHub kustomize manifests, Rook COSI client, RGW object helpers, Ceph admin cluster info, and shared object helpers.

Risks: the driver readiness retry loop is `for i := 24; i < 24 && ...`, so it never retries before assertions; upstream manifest URLs introduce network/version drift; COSI resources can collide with parallel tests; delete failure messages still say create. Signals include manifest apply/delete success, driver pod/deployment readiness, BucketClass/Claim creation, BucketClaim status bucket name, Bucket `bucketReady=true`, RGW bucket existence, and cleanup.

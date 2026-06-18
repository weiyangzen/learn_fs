<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/admin/admin.go -->
# sources/control-plane/rook/tests/integration/object/util/admin/admin.go

Purpose: shared helper for constructing a Ceph RGW admin API client during object integration tests. It abstracts credential lookup, endpoint discovery, TLS transport setup, and a basic admin API sanity check.

Important APIs and control flow: `NewAdminClient` calls `util/s3.GetS3Credentials` to read dashboard-admin RGW keys, `util/s3.GetS3Endpoint` to derive the object-store service endpoint, optionally installs an `http.Transport` with `InsecureSkipVerify` for test TLS clusters, then calls `admin.New` and verifies the client with `GetInfo`.

State, persistence, and integration: no durable state is created; it reads RGW credentials from `radosgw-admin` and Kubernetes service state. Dependencies include go-ceph RGW admin, Rook installer command execution, K8s helper, and S3 utility functions. Risks include intentionally disabled TLS verification, hard dependency on the dashboard-admin user and realm name, and endpoint port assumptions inherited from the S3 helper. Test signal is the immediate `GetInfo` call, which catches bad credentials or endpoints before callers run deeper assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/util/admin/admin.go -->

# sources/control-plane/rook/pkg/operator/ceph/object/rgw_test.go

Purpose: unit tests for RGW deployment creation and helper functions in `rgw.go`.

Important APIs/tests: `TestStartRGW`, `validateStart`, `TestCreateObjectStore`, `simpleStore`, `TestCreateObjectStoreWithKeystoneAndS3`, `simpleStoreWithKeystoneAndS3`, `TestGenerateSecretName`, `TestEmptyPoolSpec`, `TestBuildDomainNameAndEndpoint`, and `TestGetTlsCaCert`.

Control flow: tests create fake Kubernetes clients and mocked Ceph executors, invoke `startRGWPods` or `createOrUpdateStore`, and assert deployment presence or absence of undesired command flags. TLS tests table through no cert ref, missing Secret, unknown Secret type, Opaque missing key, Opaque with `cert`, and later TLS Secret cases in the same file.

State and persistence: uses fake apps/core clients for Deployments and Secrets, temp config dirs, mocked Ceph command output, and in-memory stores.

Dependencies and integration points: covers integration with Rook deployment generation, keyring generation, Ceph config setting, Kubernetes Secret type handling, DNS endpoint helpers, and object-store specs with Keystone/S3 auth options.

Risks: tests do not deeply inspect generated pod templates, probe scripts, service resources, replica semantics, or deletion paths. They rely on mocked command responses and do not validate live Ceph behavior.

Test signals: good signal for basic deployment creation, helper formatting, and TLS error messages. Changes to cert key names, endpoint URL formatting, or keyring secret naming should fail here.

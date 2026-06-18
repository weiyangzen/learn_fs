# sources/control-plane/rook/pkg/operator/ceph/pool/validate_test.go

Purpose: validates pool-spec guardrails with mock Ceph command output and hand-built pool specs.

Important APIs/types/functions: `TestValidatePool`, `TestValidateCrushProperties`, and `TestValidateDeviceClasses`.

Control flow: `TestValidatePool` exercises local spec validation branches: missing replication/EC settings, missing name/namespace, both replicated and EC settings, safe size-1 replication, known/unknown compression modes, replica count vs replicas per failure domain, unknown subdomain, EC pool with deprecated compression mode, mirroring mode validation, snapshot schedule interval validation, and identical failure/subfailure domain rejection. `TestValidateCrushProperties` mocks `ceph osd crush dump` JSON to test known/unknown failure domains and CRUSH roots. `TestValidateDeviceClasses` mocks `ceph osd crush class ls-osd` output for primary and secondary device classes.

State and persistence behavior: no Kubernetes persistence; tests use in-memory specs and `exectest.MockExecutor` output to simulate Ceph state.

Dependencies/integration: uses `clusterd.Context`, `cephclient.AdminTestClusterInfo`, `exectest.MockExecutor`, Ceph API types, and testify assertions.

Risks: no explicit test for stretch cluster restrictions, warnings-only branches, malformed CRUSH JSON, Ceph command errors, or `ValidatePoolSpec` callers with nil cluster/spec context. A duplicate subtest label says "not a power of 2" although implementation validates divisibility/factor behavior.

Test signals: coverage is broad for expected user-facing validation failures and live Ceph lookup integration, especially CRUSH and hybrid device-class paths.

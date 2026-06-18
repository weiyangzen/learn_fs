# sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile_test.go

Purpose: verifies erasure-code profile creation command construction.

Important test cases: `TestCreateProfile`, `TestCreateProfileWithFailureDomain`, and `TestCreateProfileWithDeviceClass` call `testCreateProfile()` with different optional placement fields. The helper configures a pool spec with 2 data chunks, 3 coding chunks, and `4Ki` stripe unit, mocks `erasure-code-profile get default`, then asserts `set myapp --force` args include `k`, `m`, inherited plugin/technique, optional `crush-failure-domain`, optional `crush-root`, optional `crush-device-class`, and `stripe_unit=4096`.

Control flow and dependencies: uses `resource.MustParse`, `cephv1.PoolSpec`, and `exectest.MockExecutor`. The test asserts exact arg order, documenting the command contract.

Risks and coverage gaps: it covers only successful creation. Missing tests include invalid/default profile JSON, default profile lookup failure, stripe unit conversion failure, algorithm override, `ListErasureCodeProfiles()`, `GetErasureCodeProfileDetails()`, and `DeleteErasureCodeProfile()`.

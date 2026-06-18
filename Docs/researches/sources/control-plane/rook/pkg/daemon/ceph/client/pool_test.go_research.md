# sources/control-plane/rook/pkg/daemon/ceph/client/pool_test.go

This test file validates the pool helper behavior by driving mocked Ceph/RBD commands and checking command arguments, branch decisions, and parsed results. It is the main signal for the pool creation and CRUSH rule logic in `pool.go`.

The tests cover EC pool creation with and without overwrite support, compression property application, application tag idempotency, replicated pool creation with failure domains, crush roots, device classes, and compression modes. `TestUpdateFailureDomain` checks when CRUSH updates are skipped, when stretch clusters bypass updates, and when a new failure-domain rule is created. `TestCleanupUnusedCrushRules` proves cleanup preserves in-use rules and `replicated_rule`, and `TestCleanupUnusedCrushRulesNoPools` protects the initial-cluster case where deleting defaults would be dangerous.

State is represented through mocked command output rather than a real Ceph cluster. The tests verify integration contracts with `ceph osd pool`, `ceph osd crush`, `rbd pool stats`, and `crushtool` where available. `hasCrushtool()` conditionally runs tests that need local CRUSH map compile/decompile binaries.

Risks surfaced include reliance on exact CLI argument order, map iteration differences avoided by targeted assertions, and gaps around real concurrent `crushRuleMutex` behavior. The file is strong at unit-level command construction and parsing but does not simulate real Ceph side effects or rollback from partially applied pool settings.

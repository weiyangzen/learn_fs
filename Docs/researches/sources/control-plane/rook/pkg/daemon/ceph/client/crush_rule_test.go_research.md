# sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule_test.go

Purpose: validates CRUSH rule construction and helper commands.

Important test cases: `TestBuildStretchClusterCrushRule` loads `testCrushMap` and verifies the next generated rule ID. `TestBuildCrushSteps` checks four generated steps and key root/failure-domain values. `TestCompileCRUSHMap`, `TestDecompileCRUSHMap`, `TestInjectCRUSHMapMap`, and `TestSetCRUSHMapMap` verify exact command-line construction for `crushtool` and Ceph CRUSH map mutation helpers. `Test_generateRuleID` covers ordered and unordered existing rule ID lists.

Control flow and dependencies: tests reuse the JSON fixture from `crush_test.go`, `exectest.MockExecutor`, and `AdminTestClusterInfo()`. They assert positional args before standard flags appended by `NewCephCommand()`.

Risks and coverage gaps: coverage is strong for command construction and common ID selection, but it does not cover empty rules, hybrid textual rule output, device class insertion, `getCrushRule()`, or command error wrapping. Tests for ID generation assume starting from the last slice element and incrementing to an unused ID, which documents current behavior even when rules are unsorted.

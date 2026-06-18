# sources/control-plane/rook/pkg/daemon/ceph/client/crush_test.go

Purpose: tests CRUSH map JSON parsing and host/name helper behavior.

Important test cases: `testCrushMap` is a representative CRUSH dump with devices, types, buckets, replicated and hybrid rules, and tunables. `TestGetCrushMap` ensures `GetCrushMap()` parses expected counts. `TestGetOSDOnHost` verifies `ceph osd crush ls <normalized-host>` command shape. `TestCrushName` checks `NormalizeCrushName()` and `IsNormalizedCrushNameEqual()` across hostnames, AWS-style names, workers, masters, zones, and IP-like names. `TestBuildCompiledDecompileCRUSHFileName` validates suffix helpers.

Control flow and dependencies: tests use mock executors and assert command args by index. The name test intentionally compares many similar strings to catch accidental over-normalization.

Risks and coverage gaps: the fixture is large enough to catch broad CRUSH schema mapping issues but does not assert individual bucket/rule fields. Error paths for malformed JSON and command failure are not covered. `GetCompiledCrushMap()` is not directly tested, so temp-file creation and `--out-file` behavior are only indirectly represented by other CRUSH map command tests.

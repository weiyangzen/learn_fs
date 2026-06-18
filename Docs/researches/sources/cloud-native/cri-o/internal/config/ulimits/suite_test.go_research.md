# sources/cloud-native/cri-o/internal/config/ulimits/suite_test.go

Purpose: Ginkgo suite bootstrap for ulimits config tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers failure handler, runs specs named `UlimitsConfig`, and sets up/tears down the CRI-O test framework.

State and persistence behavior: suite framework state only.

Dependencies/integration points: Ginkgo/Gomega and CRI-O `test/framework`.

Risks: harness setup failure blocks ulimits tests.

Test signals: harness only.

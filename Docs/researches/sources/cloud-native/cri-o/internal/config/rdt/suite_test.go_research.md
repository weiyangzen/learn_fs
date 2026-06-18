# sources/cloud-native/cri-o/internal/config/rdt/suite_test.go

Purpose: Ginkgo suite bootstrap for RDT config tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers failure handling, runs framework specs named `RdtConfig`, and manages setup/teardown of the CRI-O test framework.

State and persistence behavior: suite-local framework state and temporary resources.

Dependencies/integration points: Ginkgo/Gomega and CRI-O `test/framework`.

Risks: harness failures block RDT tests.

Test signals: harness only.

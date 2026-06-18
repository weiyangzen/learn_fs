# sources/cloud-native/cri-o/internal/config/seccomp/suite_test.go

Purpose: Ginkgo suite bootstrap for seccomp config tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers Gomega failure handling, runs framework specs named `SeccompConfig`, and manages test framework setup/teardown.

State and persistence behavior: suite-local test state only.

Dependencies/integration points: Ginkgo/Gomega and CRI-O `test/framework`.

Risks: harness failure blocks seccomp tests.

Test signals: harness only; behavior lives in `seccomp_test.go`.

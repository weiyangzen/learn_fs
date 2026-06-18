# sources/cloud-native/cri-o/internal/config/conmonmgr/suite_test.go

Purpose: bootstraps the Ginkgo suite for the conmon manager package.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`. `BeforeSuite` creates a CRI-O `TestFramework`, stores `mockCtrl` from the framework for gomock usage, and calls setup; `AfterSuite` tears it down.

Control flow: Go test calls `TestLibConfig`, which registers Gomega failure handling and runs framework specs named `ConmonManagerConfig`. Suite hooks prepare and clean test framework state.

State and persistence behavior: owns process-local suite state and any temporary framework resources. No package behavior is implemented here.

Dependencies/integration points: integrates Ginkgo/Gomega with `github.com/cri-o/cri-o/test/framework`.

Risks: package tests depend on correct global framework setup; failures here can prevent all conmon manager tests from running.

Test signals: suite harness only; behavioral signal lives in `conmonmgr_test.go`.

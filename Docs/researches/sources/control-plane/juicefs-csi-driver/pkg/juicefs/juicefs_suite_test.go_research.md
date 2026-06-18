# sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_suite_test.go

Purpose: provides the Ginkgo/Gomega test-suite entry point for the `juicefs` package.

Important APIs and functions: `TestService` registers the Gomega fail handler and calls `RunSpecs(t, "juicefs Suite")`.

Control flow: Go's test runner enters this function, then Ginkgo runs package-level specs from `juicefs_test.go`.

State and persistence behavior: no persistent state is created here.

Dependencies and integration points: depends on Ginkgo v2 and Gomega.

Risks and test signals: no direct behavior coverage. It does not isolate package-level config state that individual specs may mutate.

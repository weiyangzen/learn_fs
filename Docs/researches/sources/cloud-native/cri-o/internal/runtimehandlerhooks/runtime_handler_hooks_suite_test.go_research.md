# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_suite_test.go

Purpose: Ginkgo suite entrypoint for runtime handler hook tests.

Important APIs/types/functions: `TestRuntimeHandlerHooks`.

Control flow: registers Gomega's fail handler and runs Ginkgo specs named `RuntimeHandlerHooks`.

State and persistence behavior: no shared CRI-O test framework state in this file; individual tests manage their fixtures.

Dependencies and integration points: uses Go testing, Ginkgo v2, and Gomega.

Risks: package-level state in tested code is reset inside individual tests, not by the suite.

Test signals: enables all runtimehandlerhooks package specs.

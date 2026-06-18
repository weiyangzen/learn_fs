# sources/cloud-native/cri-o/internal/storage/suite_test.go

Purpose: test-suite bootstrap and shared fixture setup for `internal/storage` tests.

Important APIs/types/functions: `TestStorage` runs Ginkgo specs named `Storage`; `BeforeSuite` initializes `TestFramework` and a Docker schema v1-ish `testManifest`; `AfterSuite` tears the framework down.

Control flow: Go test enters the suite, framework setup runs once, tests share `testManifest`, and teardown runs after all specs.

State and persistence: package-level `t` and `testManifest` are in-memory test state only.

Dependencies/integration: depends on CRI-O test framework and Ginkgo/Gomega. The manifest fixture is consumed by runtime image-resolution mocks.

Risks: shared fixture shape must remain compatible with containers/image mock helpers. Framework-level setup can hide dependencies from otherwise unit-style tests.

Test signals: confirms the storage tests are suite-based rather than plain `testing` tests.

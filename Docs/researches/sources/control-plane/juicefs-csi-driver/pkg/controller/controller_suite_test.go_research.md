# sources/control-plane/juicefs-csi-driver/pkg/controller/controller_suite_test.go

Purpose: Ginkgo/Gomega test bootstrap for the controller package.

Important API: `TestService` registers the Gomega fail handler and runs the `Controller Suite`.

Control flow/state: no controller behavior is implemented here. It enables package-level `Describe` specs, notably `mountinfo_test.go`.

Dependencies/integration: imports `github.com/onsi/ginkgo/v2` and `github.com/onsi/gomega`.

Risks: suite-level globals can hide state leakage in specs, though this file has no mutable logic itself.

Test signals: success means Ginkgo specs were discovered and executed; detailed assertions live in spec files.

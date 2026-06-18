## sources/cloud-native/moby/daemon/licensing_test.go

Purpose: Unit test for daemon license population.

Important test: `TestFillLicense` constructs an empty `system.Info`, creates a minimal `Daemon`, calls `fillLicense`, and asserts `ProductLicense` equals `dockerversion.DefaultProductLicense`.

Control flow and state: No external state is used. The daemon `root` field is populated but not used by the tested method.

Dependencies and integration points: Uses `gotest.tools/assert`, `system.Info`, and `dockerversion`.

Risks covered: Protects against dropping or changing the system-info product license assignment. It does not cover nil input handling, which the implementation does not support.

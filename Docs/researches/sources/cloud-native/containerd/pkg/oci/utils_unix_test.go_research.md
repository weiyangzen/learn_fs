# sources/cloud-native/containerd/pkg/oci/utils_unix_test.go

Purpose: tests Unix host-device discovery error handling and success behavior with injectable filesystem/device helpers.

Important APIs/types/functions: `cleanupTest` restores package-level `osReadDir` and `deviceFromPath`. Tests cover `HostDevices` read-dir failure, read-dir failure in user namespace, `DeviceFromPath` failure, failure in user namespace, and all-valid device discovery.

Control flow: tests monkey-patch helper variables to return synthetic directory entries/devices or errors, call `HostDevices`, and assert returned devices or error behavior.

State/persistence: mutates package-level function variables during tests and restores them.

Dependencies/integration: uses Linux user namespace detection paths and OCI device structs.

Risks: package-level monkey-patching makes tests order-sensitive if run in parallel. User namespace behavior depends on environment and may use different expected error tolerance.

Test signals: protects error propagation/ignore policy for host device discovery and confirms valid devices are returned when all injected helpers succeed.

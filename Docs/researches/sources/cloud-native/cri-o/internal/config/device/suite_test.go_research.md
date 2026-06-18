# sources/cloud-native/cri-o/internal/config/device/suite_test.go

Purpose: Ginkgo suite bootstrap for the device configuration tests.

Important APIs/types/functions: `TestDeviceConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers the Gomega fail handler, runs framework specs named `DeviceConfig`, creates the CRI-O test framework before the suite, and tears it down afterward.

State and persistence behavior: owns only test framework lifecycle state.

Dependencies/integration points: integrates Ginkgo/Gomega with CRI-O `test/framework`.

Risks: suite-level setup failure prevents all device tests from executing.

Test signals: harness only; parsing behavior is in `device_test.go`.

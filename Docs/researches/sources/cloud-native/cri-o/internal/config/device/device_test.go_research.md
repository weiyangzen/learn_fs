# sources/cloud-native/cri-o/internal/config/device/device_test.go

Purpose: unit-tests Linux device configuration parsing and annotation allow-list handling.

Important APIs/types/functions: creates `device.Config` with `device.New`, exercises `LoadDevices`, `Devices`, and `DevicesFromAnnotation` using Ginkgo/Gomega examples.

Control flow: tests verify that `invalid:invalid` fails as a malformed destination/mode, `/dev/invalid` fails host device resolution, `/dev/null:/dev/null:w` succeeds, and empty config entries are ignored. Annotation tests add source allow-lists and verify invalid format, invalid host device, successful allowed `/dev/null`, failure when one of multiple devices is invalid, empty annotation no-op, and rejection when the device is not in `allowed_devices`.

State and persistence behavior: test state is local `*device.Config`. Host dependency is `/dev/null` existing and `/dev/invalid` not being a valid device.

Dependencies/integration points: depends on Ginkgo/Gomega and the device package. It indirectly depends on the host device table through `DeviceFromPath`.

Risks: the tests are Linux-specific by package behavior; host device assumptions may not hold in unusual sandboxes. They do not cover destination outside `/dev` with an otherwise valid source, duplicate mode letters, or all permission combinations.

Test signals: good coverage for core parsing and annotation allow-list contract.

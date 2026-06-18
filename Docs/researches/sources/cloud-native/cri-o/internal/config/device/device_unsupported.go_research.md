# sources/cloud-native/cri-o/internal/config/device/device_unsupported.go

Purpose: supplies no-op device configuration behavior for non-Linux builds.

Important APIs/types/functions: empty `Device` and `Config` structs; `New`, `LoadDevices`, `Devices`, and `DevicesFromAnnotation` keep the same public API as Linux. `LoadDevices` always returns nil, `Devices` returns nil, and annotation parsing returns an empty slice.

Control flow: no parsing or validation occurs under the `!linux` build tag.

State and persistence behavior: no state is stored, and no device filesystem access is performed.

Dependencies/integration points: selected by build tags to let shared CRI-O configuration code compile on unsupported platforms without Linux device injection.

Risks: non-Linux builds silently ignore configured or annotated devices, which is appropriate for portability but can surprise callers expecting validation parity.

Test signals: no direct tests in this file; Linux behavior is covered separately.

# sources/cloud-native/cri-o/internal/config/capabilities/capabilities_linux.go

## Purpose
Linux default capability list and validator.

## Important APIs, Types, and Functions
Capabilities []string type, Default returns baseline CHOWN, DAC_OVERRIDE, FSETID, FOWNER, SETGID, SETUID, SETPCAP, NET_BIND_SERVICE, KILL. Validate uppercases/prefixes CAP_ and calls common.ValidateCapabilities.

## Control Flow
Callers get defaults or validate configured list before runtime use.

## State and Persistence
No persistent state.

## Dependencies
Depends on go.podman.io/common/pkg/capabilities and logrus.

## Integration Points
Integrated with CRI-O runtime default capabilities config.

## Risks and Edge Cases
Kernel/libcap support and spelling drive validation; logging shows normalized CAP_ names.

## Test Signals
capabilities_test.go covers default and validation behavior.

# sources/cloud-native/cri-o/internal/config/apparmor/apparmor_linux.go

## Purpose
Linux AppArmor configuration helper for loading and applying CRI-O AppArmor profiles.

## Important APIs, Types, and Functions
Config has default profile state. New initializes DefaultProfile. LoadProfile loads named profile, handles default reload via reloadDefaultProfile, and tracks disabled/enabled. IsEnabled reports host support. Apply maps CRI security context profile strings to OCI AppArmor profile output, including runtime/default/unconfined semantics.

## Control Flow
On startup/config load it checks host AppArmor support and loads configured profile; per-container Apply evaluates security context and returns profile name or empty string.

## State and Persistence
Kernel AppArmor profile state is mutated by loading/reloading; Config holds enabled/profile values.

## Dependencies
Depends on apparmor parser/library, runtimeapi LinuxContainerSecurityContext, host AppArmor filesystem.

## Integration Points
Integrated with CRI-O config and container spec generation.

## Risks and Edge Cases
Host support and parser availability drive behavior; unsupported profiles fail container setup; default reload can affect global host policy.

## Test Signals
apparmor_test.go covers enabled/disabled/load/apply cases on supported platforms.

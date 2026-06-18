# sources/cloud-native/moby/daemon/pkg/oci/caps/utils_linux.go

## Purpose
This Linux-specific file initializes known and currently available kernel capabilities.

## Important APIs, Types, And Functions
`initCaps` uses `sync.Once` to populate `allCaps` and `knownCaps` using containerd capability helpers `cap.Known()` and `cap.Current()`.

## Control Flow
On first call, it reads all known capability names, attempts to read current effective capabilities, logs an error and falls back to known capabilities when current cannot be read, then builds a map where unavailable current capabilities are stored with nil values and available capabilities point to a sentinel struct.

## State, Persistence, And Dependencies
The function mutates package-level cached capability slices/maps once per process. Dependencies include containerd capability package, containerd logging, `context.TODO`, `slices`, and `sync`.

## Integration Points
`utils.go` relies on this initializer for Linux validation and privileged capability enumeration.

## Risks And Edge Cases
If current capability detection fails, all known capabilities are treated as available for backward compatibility; runtime/kernel may still reject unavailable caps later. The nil marker in `knownCaps` is semantically important to distinguish unknown from known-but-unavailable.

## Test Signals
No direct tests in this subset.

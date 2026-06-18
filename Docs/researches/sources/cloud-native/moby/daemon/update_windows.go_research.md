# sources/cloud-native/moby/daemon/update_windows.go

## Purpose
Windows implementation stub for resource updates.

## Important APIs, Types, And Functions
`toContainerdResources(resources container.Resources) (*libcontainerdtypes.Resources, error)` exists for platform parity but returns `nil, nil`.

## Control Flow
The function ignores input and exits immediately because Windows container update resource conversion is not supported here.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Provides the same package-level function name as the Linux implementation so higher-level daemon update code can compile on Windows. It imports Docker container resources and internal libcontainerd resource types only for signature compatibility.

## Risks
Callers must treat a nil resource payload as "unsupported/no-op" rather than a successful concrete update. Adding Windows support later must clarify API behavior for existing callers that currently expect no mutation.

## Test Signals
No direct Windows test is in this subset. Platform compilation and higher-level update tests would be the practical signal.

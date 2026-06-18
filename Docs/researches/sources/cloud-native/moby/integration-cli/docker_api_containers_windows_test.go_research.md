# sources/cloud-native/moby/integration-cli/docker_api_containers_windows_test.go

## Purpose
Windows-specific container API mount tests and helper stub.

## Important APIs and Types
Defines `TestContainersAPICreateMountsBindNamedPipe` and Windows `mountWrapper`.

## Control Flow, State, and Persistence
The test creates a named pipe bind mount configuration and verifies daemon API handling for Windows named-pipe mounts. The Windows `mountWrapper` is a compatibility helper for shared test code and does not perform Unix mounts.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Windows daemon support for named pipes and client mount API types. Risks include Windows path escaping, named-pipe lifecycle, and divergent mount option validation from Linux. The test signals that Windows mount parsing remains compatible.

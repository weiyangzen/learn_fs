# sources/cloud-native/moby/integration-cli/docker_api_build_windows_test.go

## Purpose
Windows-specific build API regression coverage.

## Important APIs and Types
Defines `TestBuildWithRecycleBin`.

## Control Flow, State, and Persistence
The test exercises a Windows build context scenario involving recycle-bin path handling to ensure build operations do not fail on Windows-specific filesystem artifacts.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Windows daemon/image availability and the build API. Risks are platform path semantics, hidden/system directories, and Windows base image differences. The test is a targeted signal for Windows build context filtering.

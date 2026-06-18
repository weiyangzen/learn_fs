# sources/cloud-native/containerd/integration/client/client_windows_test.go

## Purpose
This Windows integration test helper selects test images and platform-specific commands/paths based on host Windows build.

## Important APIs, Types, and Functions
Globals set default root/state under Program Files, test image names, digest image, multilayer image, and short/long commands. `init` maps `osversion.Build()` to Nano Server image tags and panics when no supported image exists.

## Control Flow
At package initialization, the host build is inspected and a compatible image is selected. Newer builds beyond Windows Server 2022 default to `ltsc2022`.

## State and Persistence
Default root and state point into Program Files containerd test directories. Image selection is global process state.

## Dependencies and Integration Points
Uses hcsshim `osversion`, integration images, and shared client tests.

## Risks
Unsupported Windows builds panic during test initialization. Image compatibility is tied to host/container version compatibility rules.

## Test Signals
Provides platform-specific setup for the shared integration suite.

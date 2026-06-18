# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_runsecurity_test.go

## Purpose
This file validates Dockerfile `RUN --security` modes, security entitlements, and insecure device whitelist behavior. It registers `runSecurityTests` into `securityTests` and configures mirrored images for `alpine` and `tonistiigi/hellofs`.

## Important APIs, Types, and Functions
Tests are `testInsecureDevicesWhitelist`, `testRunSecurityInsecure`, `testRunSecuritySandbox`, and `testRunSecurityDefault`. They use `entitlements.EntitlementSecurityInsecure`, sandbox value `security.insecure`, `integration.WithMirroredImages`, `client.New`, `f.Solve`, and local Dockerfile/context mounts.

## Control Flow and Assertions
`testInsecureDevicesWhitelist` skips rootless, installs packages in Alpine, confirms `/dev/fuse` and loop-control are absent without insecure mode, then uses `RUN --security=insecure` to check device nodes, run `dmesg`, mount a FUSE hellofs filesystem, and mount an ext4 loopback image. `testRunSecurityInsecure` compares capability bounding sets under insecure and default RUNs. `testRunSecuritySandbox` checks explicit sandbox mode has the normal capability set. `testRunSecurityDefault` checks default behavior while passing the insecure entitlement, then branches on sandbox policy.

## State, Persistence, and Dependencies
State lives in temp Dockerfiles and image layers. Dependencies include Linux capabilities, `/proc/self/status`, FUSE, loop devices, mirrored external images, and sandbox entitlement configuration. Windows is not explicitly skipped in all tests, but the Dockerfiles use Linux images and proc/device semantics, so matrix selection likely handles platform suitability elsewhere.

## Integration Points
The file integrates Dockerfile `--security` parsing, worker capability/device setup, entitlement authorization, mirrored-image resolution, and privileged filesystem operations.

## Risks and Test Signals
Risks include insecure mode gaining too many or too few devices, entitlement denial not being enforced, default/sandbox capabilities changing unintentionally, rootless unsupported paths running, and external image/tool availability. Signals include capability string equality, successful/failed entitlement branches, and real FUSE/loopback operations under insecure mode.

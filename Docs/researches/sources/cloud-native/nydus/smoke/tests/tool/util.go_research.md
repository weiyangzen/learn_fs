# sources/cloud-native/nydus/smoke/tests/tool/util.go

## Purpose
This file provides shell command wrappers, binary path resolution, and image repository parsing for smoke tests.

## Important APIs, Types, And Functions
`defaultBinary` maps environment keys to default executable names. `RunWithCombinedOutput`, `Run`, `RunWithoutOutput`, and `RunWithOutput` execute shell commands through `sh -c` with different output handling and assertion behavior. `GetBinary` resolves versioned environment variables like `NYDUS_BUILDER_v1_2_3`, falls back to unversioned vars or defaults for `latest`, and fails tests if required binaries are absent. `ImageRepo` strips registry/path and tag to get the repository name used for workload recipes.

## Control Flow
Tests construct command strings and pass them to these helpers. Binary lookup normalizes dots to underscores in version strings and chooses the right environment key before falling back.

## State And Persistence
The helpers execute external commands that can mutate system state, but this file itself stores only the default binary map.

## Dependencies And Integration Points
It integrates all smoke tests with shell commands, Docker, nerdctl, nydusify, nydus-image, nydusd, and environment-based binary selection.

## Risks
All command helpers use `sh -c`, so callers must avoid unsafe strings. `Run` and `RunWithoutOutput` use `assert.Nil`, which records failures but may allow callers to continue. `RunWithOutput` panics on command failure instead of returning a testing assertion.

## Test Signals
Command exit status and captured output are the direct signals. Binary resolution failures are fatal test failures.

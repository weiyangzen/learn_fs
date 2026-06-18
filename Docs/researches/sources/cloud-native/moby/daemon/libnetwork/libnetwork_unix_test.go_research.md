# sources/cloud-native/moby/daemon/libnetwork/libnetwork_unix_test.go

## Purpose
Defines the Unix plugin specification path used by shared libnetwork tests outside Windows.

## Important APIs, Types, And Functions
The only symbol is package-level `specPath = "/etc/docker/plugins"` in `libnetwork_test`.

## Control Flow
There is no executable logic. Other tests in the same package use `specPath` when creating remote network-driver plugin specification files.

## State And Persistence
The value points at the conventional Docker plugin spec directory and causes tests to create/remove files under that path.

## Dependencies And Integration Points
Integrated with remote plugin tests such as `TestInvalidRemoteDriver` and `TestValidRemoteDriver` in the Linux test file.

## Risks
Tests using this path need permissions and must remove the directory/files they create. Because this file is build-tagged `!windows`, Windows uses a different path.

## Test Signals
No direct tests; its correctness is indirectly exercised by remote plugin discovery tests.

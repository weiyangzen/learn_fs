# sources/cloud-native/containerd/integration/pod_hostname_test.go

## Purpose

This test validates pod hostname behavior for regular and host-network pods, including rejection of custom hostnames with host networking.

## Important APIs, Types, And Functions

- `TestPodHostname` table-tests regular custom hostname, host-network default hostname, and host-network custom hostname failure.
- `WithPodHostname`, `WithHostNetwork`, and `WithPodLogDirectory` configure sandbox cases.

## Control Flow

The test gets the host hostname, then for each case creates a sandbox config. Host-network cases skip on Windows. If `RunPodSandbox` errors, the test only accepts that for the expected-error case. Otherwise it starts a BusyBox container that prints `/etc/hostname`, `hostname`, and environment variables, waits for exit, reads the log, and checks `HOSTNAME=` or `COMPUTERNAME=` plus `/etc/hostname=` contain the expected value.

## State And Persistence Behavior

The test observes generated container hostname files and environment variables. Evidence is persisted in the temporary CRI log file.

## Dependencies And Integration Points

It integrates CRI sandbox hostname fields, host network namespace policy, BusyBox shell utilities, Windows environment naming, and log handling.

## Risks And Edge Cases

The Windows branch only applies to non-host-network cases. Host hostnames may contain values requiring exact matching in logs. The failure case asserts only that an error occurs, not a specific validation message.

## Test Signals

Passing confirms hostname propagation and host-network validation behavior are correct.

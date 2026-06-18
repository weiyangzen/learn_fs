# sources/cloud-native/containerd/integration/issue10244_loopback_linux_test.go

## Purpose

This Linux regression test validates that the loopback interface is up inside pods regardless of the CRI CNI `use_internal_loopback` setting. It covers issue 10244 behavior around loopback setup.

## Important APIs, Types, And Functions

- `TestIssue10244LoopbackV2` table-tests `use_internal_loopback=false` and `true`.
- `checkLoopbackResult` writes an isolated containerd config, starts containerd, runs a test container, and executes the loopback helper.

## Control Flow

For each setting, the test writes `config.toml` with the CRI runtime CNI option, starts a new containerd process, registers cleanup, pulls BusyBox, creates a pod/container with `/usr/local/bin/loopback-v2` bind-mounted into the container, runs the helper through `ExecSync`, and asserts stdout contains `UP`.

## State And Persistence Behavior

It creates an isolated temporary containerd work directory and config file. Pods and the containerd process are cleaned up after each subtest.

## Dependencies And Integration Points

It integrates with containerd process management helpers, CRI CNI configuration, the `loopback-v2` helper binary, host bind mounts, and BusyBox.

## Risks And Edge Cases

The helper binary must exist at `/usr/local/bin/loopback-v2`. The config uses the CRI v1 runtime plugin path and assumes the isolated containerd can start with defaults for all other settings.

## Test Signals

Passing confirms pod network namespaces have an operational loopback interface with both internal and external loopback handling paths.

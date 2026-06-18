# sources/cloud-native/containerd/internal/cri/server/podsandbox/types/sandbox_info.go

## Purpose

This file defines the JSON payload shape used for verbose pod sandbox status information.

## Important APIs, Types, and Functions

`SandboxInfo` includes PID, process status, netns closed flag, image, snapshot key/snapshotter, runtime type/options, original CRI config, runtime spec, CNI result, sandbox metadata, and optional overhead/resources.

## Control Flow

There are no functions or control flow.

## State and Persistence Behavior

The struct is serialized into the `info` map returned by sandbox status. It represents observed state but does not persist it directly.

## Dependencies and Integration Points

It depends on CNI result types, OCI runtime spec, CRI runtime API types, and sandbox store metadata.

## Risks and Test Signals

Because `RuntimeOptions` is `any`, JSON shape can vary by runtime option type. Verbose status clients should tolerate absent fields such as `RuntimeSpec` for partially created sandboxes.

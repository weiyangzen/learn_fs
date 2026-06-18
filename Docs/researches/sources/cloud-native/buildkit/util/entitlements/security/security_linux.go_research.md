# sources/cloud-native/buildkit/util/entitlements/security/security_linux.go

## Purpose
Linux insecure container spec mutator. It grants current capabilities, removes readonly/masked path restrictions, clears AppArmor, permits device cgroups, and mounts common host devices outside user namespaces.

## Important APIs, Types, And Functions
Package: `security`. Build tags: `none`. Key declarations observed in the file: `WithInsecureSpec, getFreeLoopID, getCurrentCaps, getAllCaps, linux35Caps`.

## Control Flow, State, And Persistence
WithInsecureSpec calls getAllCaps, appends capabilities to all capability sets, clears restrictions, allows char/block devices, probes /dev/loop-control for free loop id, and adds loop devices around that range. Cap discovery is cached with sync.Once.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/containers, github.com/containerd/containerd/v2/pkg/cap, github.com/containerd/containerd/v2/pkg/oci, github.com/moby/buildkit/util/bklog, github.com/opencontainers/runtime-spec/specs-go, github.com/pkg/errors, golang.org/x/sys/unix`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are intentionally privileged behavior, user namespace differences, loop-control failures, and kernel capability variance. Test signal is integration/security review rather than local unit tests.

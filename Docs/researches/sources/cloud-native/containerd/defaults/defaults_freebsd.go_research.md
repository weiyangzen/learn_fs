# sources/cloud-native/containerd/defaults/defaults_freebsd.go

## Purpose
This FreeBSD-specific file defines the default runtime.

## Important APIs, Types, and Functions
`DefaultRuntime` is set to `wtf.sbk.runj.v1`.

## Control Flow
No executable flow.

## State and Persistence
No state; this is a compile-time constant.

## Dependencies and Integration Points
Combined with Unix non-Linux defaults for addresses, state, root, config, snapshotter, and differ.

## Risks
Changing the runtime affects all FreeBSD default container launches.

## Test Signals
Build coverage on FreeBSD validates this constant composes with other defaults.

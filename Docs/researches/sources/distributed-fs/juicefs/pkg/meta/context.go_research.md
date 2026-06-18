# sources/distributed-fs/juicefs/pkg/meta/context.go

## Purpose

`context.go` defines the metadata package's request context abstraction. It extends Go's `context.Context` with filesystem identity (`uid`, `gid`, supplementary gids, pid), package-specific cancellation helpers, immutable `WithValue` chaining, and a permission-check hook.

## Important APIs And Types

`CtxKey` is a string alias for package context keys. `Context` embeds `context.Context` and adds `Gid`, `Gids`, `Uid`, `Pid`, `WithValue`, `Cancel`, `Canceled`, and `CheckPermission`.

`wrapContext` is the default implementation. It stores an embedded context, cancel function, pid, uid, and gids. `Uid`, `Gid`, `Gids`, and `Pid` expose identity. `Cancel` invokes the stored cancel function when present. `Canceled` returns whether the embedded context has an error. `WithValue` shallow-copies the wrapper, replaces the embedded context with `context.WithValue`, and preserves identity/cancel state. `CheckPermission` currently returns true.

Constructor helpers are `Background`, `NewContext`, `WrapContext`, `WrapWithCancel`, `WrapWithTimeout`, and `WrapWithoutCancel`. `containsGid` checks whether a gid is in the supplementary group list.

## Control Flow

`Background` wraps `context.Background()` as root uid/gid/pid zero. `NewContext` creates a cancelable context with explicit process and user/group identity. `WrapWithCancel` always derives a new cancelable child context from the provided context. `WrapWithTimeout` derives a timed child and copies pid/uid/gids from an existing metadata context. `WrapWithoutCancel` preserves an existing context without installing a cancel function, so calling `Cancel` is a no-op for that wrapper.

## State And Persistence Behavior

The file has no persistent storage. It carries request-local state used by all metadata operations for permission checks, quota attribution, lock ownership context, and cancellation. The `gids` slice is assumed immutable enough for shallow copying; callers that mutate the slice after passing it in could affect existing contexts.

## Dependencies And Integration Points

The only external dependencies are Go `context` and `time`. The interface is used throughout the metadata engines, tests, quota logic, ACL/mode access checks, cleanup tasks, and cancellation-sensitive long operations. `context_cancellation_test.go` specifically validates cancellation behavior through metadata APIs.

## Risks And Test Signals

`Gid` indexes `gids[0]` with no empty-slice guard, so constructors must receive at least one gid. `Canceled` treats deadline exceeded and explicit cancel the same because both set `Err`. `WithValue` preserving the original cancel function is convenient, but canceling either wrapper cancels the shared underlying context. Tests focus on cancellation propagation at higher metadata layers rather than direct unit coverage of this file.

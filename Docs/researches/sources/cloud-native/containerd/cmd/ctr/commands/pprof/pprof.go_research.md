<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof.go

## Purpose
Defines `ctr pprof` subcommands that proxy Go pprof and trace endpoints from containerd debug server to stdout.

## Important APIs, Types, And Functions
Exports `Command`, `Client`, profile helpers for goroutine/heap/profile/trace/block/threadcreate, `getPProfClient`, and `httpGetRequest`.

## Control Flow
Each subcommand builds an HTTP client using the platform dialer, formats a `/debug/pprof/...` path with debug or duration arguments, validates HTTP 200, and streams the response body.

## State And Persistence
Does not persist state; it reads live debug endpoint data and writes raw profile or text output to stdout.

## Dependencies And Integration Points
Depends on `defaults.DefaultDebugAddress`, net/http transport Dial hook, and platform-specific `getPProfDialer`.

## Risks And Test Signals
Long profile/trace calls block until the debug endpoint responds; non-200 responses become errors. Test signal is dependency-injected `Client`, but this file has no direct test. Source size reviewed: 281 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/pprof/pprof.go -->

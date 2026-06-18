# sources/cloud-native/moby/daemon/server/router/container/notify_unsupported.go

## Purpose
`notify_unsupported.go` is the non-Linux stub for connection-close notifications.

## Important APIs, Types, And Functions
It defines `notifyClosed(ctx context.Context, conn net.Conn, notify func())` as a no-op under the `!linux` build tag.

## Control Flow
There is no runtime behavior. Calls compile on unsupported platforms but do not install a close watcher.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The file keeps container stream code portable by satisfying the same function symbol as the Linux implementation.

## Risks
Non-Linux platforms do not get the Linux close-notification behavior, so callers must not rely on this function as the only cleanup path.

## Test Signals
Compilation on non-Linux platforms is the main signal.

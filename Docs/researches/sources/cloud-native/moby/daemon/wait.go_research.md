# sources/cloud-native/moby/daemon/wait.go

## Purpose
Thin daemon API for waiting on a container state condition.

## Important APIs and Types
Defines `(*Daemon).ContainerWait(ctx, name, condition)`.

## Control Flow, State, and Persistence
The method resolves the container by name or ID with `GetContainer`. If lookup fails, it returns nil channel plus the error immediately. Otherwise it delegates to `cntr.State.Wait(ctx, condition)`, returning a receive-only channel of `container.StateStatus`.

## Dependencies, Integration Points, Risks, and Test Signals
Used by API handlers and clients that implement `/containers/{id}/wait`. It depends on container state machinery for synchronization, exit code delivery, and context cancellation. Risks are mostly delegated: waiters must not leak on cancellation, and lookup errors must preserve not-found classification. Integration tests in `docker_api_containers_test.go` exercise wait behavior through the client.

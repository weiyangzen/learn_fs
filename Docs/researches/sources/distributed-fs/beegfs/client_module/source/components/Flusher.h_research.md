# sources/distributed-fs/beegfs/client_module/source/components/Flusher.h

## Purpose
Declares the asynchronous cache flusher component.

## Important APIs and types
`Flusher` embeds `Thread` and stores `App*`. Exports lifecycle functions, request loop, run function, and `__Flusher_flushBuffers`.

## State, dependencies, integration
The component uses `InodeRefStore` through the app at runtime. It exists to keep flush retry delays out of foreground filesystem operations.

## Risks and test signals
The header documents the reason for a dedicated thread: retries while a server is unreachable should not block other threads. Tests should verify thread lifecycle and app/ref-store interactions.

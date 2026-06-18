# sources/distributed-fs/ipfs-kubo/core/shutdown/close.go

Purpose: provides a bounded close helper for subsystems whose `Close` method lacks context. Important API is `CloseWithCtx`.

Control flow: starts the close function in a goroutine, waits for either its result or `ctx.Done`, returns the close error when completed, or logs an error and returns a wrapped context error when the deadline/cancel wins.

State and persistence: no persistence. It may intentionally leave the close goroutine running after timeout because process shutdown is imminent.

Dependencies/integration: context, time, go-log. Used throughout node services: blockservice, pinner, MFS, host, peerstore, resource manager, providers, peering, and routing.

Risks: timed-out close goroutines leak until process exit; this is accepted to honor shutdown deadlines. Tests cover success, error propagation, and timeout.

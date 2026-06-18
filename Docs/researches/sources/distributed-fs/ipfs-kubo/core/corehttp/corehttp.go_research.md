# sources/distributed-fs/ipfs-kubo/core/corehttp/corehttp.go

Purpose: provides generic HTTP serving helpers for Kubo core HTTP interfaces.

Important APIs/types/functions: `ServeOption`, `MakeHandler`, `ListenAndServe`, `Serve`, and `ServeWithReady`; constant `shutdownTimeout`.

Control flow: `MakeHandler` applies serve options in order to a top-level mux and special-cases CONNECT requests with 200 OK because `http.ServeMux` does not handle CONNECT normally. `ListenAndServe` parses a listening multiaddr, listens with manet, prints the actual RPC address, and delegates to `Serve`. `ServeWithReady` closes the listener on exit, builds the handler, checks node context before serving, starts `http.Server.Serve` in a goroutine, closes the ready channel immediately before serving, then waits for server exit or node context cancellation. On node shutdown it logs waiting messages and calls `server.Shutdown` with a 30-second timeout.

State and persistence behavior: manages listener/server lifecycle only. No repo state. It reacts to node context cancellation to stop serving and close listener.

Dependencies and integration points: used by daemon RPC/gateway/webui serve setup through `ServeOption`s. Depends on `core.IpfsNode.Context`, multiaddr network conversion, standard `http.Server`, and Kubo logging.

Risks: `serverError` is written by the serve goroutine and read by the parent without explicit synchronization beyond channel close; channel close provides ordering for reads after `<-serverClosed`. Shutdown waits up to 30 seconds for handlers to respect contexts. Returning `server.Shutdown` error overwrites `server.Serve` error after context shutdown.

Test signals: no direct tests here; daemon lifecycle/integration tests should cover serving and graceful shutdown.

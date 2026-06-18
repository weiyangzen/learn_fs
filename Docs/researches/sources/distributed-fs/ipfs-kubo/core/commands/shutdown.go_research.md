# sources/distributed-fs/ipfs-kubo/core/commands/shutdown.go

Purpose: implements `ipfs shutdown`, a daemon-only command that closes the running node.

Important APIs/types/functions: `daemonShutdownCmd` retrieves the node from command environment and calls `nd.Close()`.

Control flow: if the node cannot be retrieved, the error is returned. If `nd.IsDaemon` is false, it returns a client error "daemon not running". On daemon nodes it invokes `Close`; close errors are logged but not returned to the client.

State and persistence behavior: triggers node shutdown through `IpfsNode.Close`, which cascades through the node stop function and services. It does not directly flush state here, so correctness depends on lower-level close handlers.

Dependencies and integration points: depends on `cmdenv.GetNode`, shared package logger, and `core.IpfsNode` lifecycle.

Risks: close errors are swallowed after logging, so callers may see success even if a component reports shutdown failure. Command is meaningful only when executed against a daemon environment.

Test signals: no direct tests in this file. HTTP/server shutdown behavior is separately represented in `corehttp/corehttp.go`.

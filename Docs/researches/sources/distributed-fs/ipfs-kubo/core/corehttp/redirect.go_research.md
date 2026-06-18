# sources/distributed-fs/ipfs-kubo/core/corehttp/redirect.go

## Purpose
Provides a simple serve option that redirects an HTTP path while applying configured API headers.

## Important APIs, Types, and Functions
Exports `RedirectOption` and defines `redirectHandler`.

## Control Flow and State
The serve option reads repo config, builds a handler with redirect target and `API.HTTPHeaders`, and mounts it either at `/$path/` or `/`. Requests copy configured headers into the response and issue HTTP 302 to the target path.

## Dependencies and Integration Points
Depends on `core.IpfsNode.Repo.Config`, net/http, and the corehttp serve option pattern. It is used for root or alias endpoint behavior in daemon HTTP setup.

## Risks and Test Signals
Risks include unexpected broad root matching, header exposure, and permanent-vs-temporary redirect expectations. Tests should verify configured headers, mounted path behavior, and exact redirect status/location.

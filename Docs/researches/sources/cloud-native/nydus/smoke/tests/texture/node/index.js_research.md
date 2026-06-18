# sources/cloud-native/nydus/smoke/tests/texture/node/index.js

## Purpose
This Node.js texture starts a simple HTTP server used by container smoke tests that wait for a URL readiness signal.

## Important APIs, Types, And Functions
It imports Node's `http` module, creates a server callback that responds with status 200, content type `text/plain`, and body `hello\n`, then listens on port 80.

## Control Flow
When run as `node /src/index.js`, the process starts a long-lived HTTP server. Each request receives the same static response.

## State And Persistence
It keeps in-memory server state and binds port 80. It writes no files.

## Dependencies And Integration Points
`tool/container.go` uses it for the `node` recipe, mounting `tests/texture/node` to `/src` and passing `node /src/index.js` as container args. Readiness is checked by HTTP GET to `http://localhost:80`.

## Risks
Binding port 80 may require container privileges and can conflict with other host-network tests because containers run with `--net=host`. The server has no error handling for listen failures.

## Test Signals
The readiness signal is a successful HTTP response from localhost port 80 after the Nydus-backed container starts.

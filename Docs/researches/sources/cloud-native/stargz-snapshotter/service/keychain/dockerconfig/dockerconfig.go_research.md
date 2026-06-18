<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/dockerconfig/dockerconfig.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/dockerconfig/dockerconfig.go

## Purpose
Provides resolver credentials from the local Docker CLI config file.

## Important APIs, Types, And Functions
- `NewDockerconfigKeychain(ctx)` returns a `resolver.Credential` closure.
- Loads Docker config with `config.Load("")` on every credential request.
- Maps `docker.io` and `registry-1.docker.io` to Docker config's legacy index URL.
- Returns identity token preferentially, otherwise username/password.

## Control Flow
For each host/ref request, the closure loads config, normalizes Docker Hub host if needed, calls `GetAuthConfig`, and returns token or basic credentials.

## State And Persistence
No in-process cache is kept. Persistent state lives in the user's Docker config and credential helpers.

## Dependencies And Integration Points
Used as the default first credential provider in plugin and keychain config paths. Depends on Docker CLI config loading and resolver credential chaining.

## Risks And Edge Cases
Loading on every request can be expensive or blocked by credential helpers. Config load failures are logged and treated as anonymous credentials. Credential helper errors propagate from `GetAuthConfig`.

## Test Signals
Signals are Docker Hub key normalization, identity-token precedence, username/password fallback, anonymous behavior on missing config, and propagated helper errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/dockerconfig/dockerconfig.go -->

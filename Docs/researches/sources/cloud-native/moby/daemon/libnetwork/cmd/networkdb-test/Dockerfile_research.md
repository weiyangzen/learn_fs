# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/Dockerfile

## Purpose
Builds a tiny Alpine-based container image for running a `testMain` binary used by NetworkDB tests or diagnostics.

## Important APIs, Types, And Functions
The Dockerfile starts from `alpine`, installs `curl`, copies `testMain` into `/app/`, sets `WORKDIR app`, and uses `/app/testMain` as the entrypoint.

## Control Flow
Image build installs dependencies and copies the binary. Container start executes the test binary directly.

## State And Persistence
No persistent state beyond image layers. Runtime state depends on `testMain`.

## Dependencies And Integration Points
Requires an external `testMain` build artifact in the Docker build context. `curl` suggests the binary or tests interact with HTTP endpoints.

## Risks And Test Signals
The `WORKDIR app` path is relative and resolves under the current root as `/app` after creation/copy behavior; the absolute entrypoint avoids ambiguity. No tests are included here, and build success depends on the binary existing.

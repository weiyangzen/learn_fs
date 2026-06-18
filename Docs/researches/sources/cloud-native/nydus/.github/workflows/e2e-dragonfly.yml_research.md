# sources/cloud-native/nydus/.github/workflows/e2e-dragonfly.yml

## Purpose
This workflow validates Nydus integration with Dragonfly proxy/cache paths. It runs on pushes, PRs excluding documentation/image-only changes, daily schedule, and manual dispatch.

## Important APIs, Types, and Functions
It sets `DRAGONFLY_VERSION=2.4.3` and `CLIENT_VERSION=1.3.3`. Jobs include `nydus-build`, `dragonfly-download`, matrix `e2e-test` for `http-proxy`, `sdk-proxy`, `sdk-proxy-strict`, and `http-proxy-strict`, and `proxy-error-test`. It uses MySQL, Redis, manager, scheduler, dfdaemon, `crane`, `nydusd`, and Go tests under `smoke/dragonfly`.

## Control Flow
Nydus is built and uploaded. Dragonfly binaries are cached or downloaded and uploaded. The e2e job downloads both artifact sets, installs executables, starts MySQL and Redis with readiness loops, installs Dragonfly configs, installs `crane`, extracts a Nydus bootstrap layer from a matrix image, and runs `go test -run TestDragonflyE2E` with environment variables pointing at binaries, configs, cache/log dirs, and bootstrap. The proxy-error job extracts a bootstrap and runs `TestProxyErrorSimulation`. Both jobs collect logs and cleanup processes/mounts in `always()` steps.

## State and Persistence
Runtime state lives in Docker containers, `/tmp/dragonfly-*`, `/tmp/nydus-*`, `/etc/dragonfly`, and uploaded log artifacts. Artifact state passes Nydus and Dragonfly binaries across jobs.

## Dependencies and Integration Points
The workflow integrates with Dragonfly releases, Dragonfly client releases, GHCR image-service images, Go smoke tests, `misc/dragonfly` configs, and Nydus HTTP proxy/SDK proxy backend configuration.

## Risks and Edge Cases
It depends heavily on external downloads and image availability. Bootstrap extraction uses Python heuristics over image manifest layers and can fail if annotations/media types change. The cleanup kills only the newest process matching names, which may miss multiple stray processes. MySQL/Redis startup and port availability can cause flakiness. It requires privileged operations for mounts and daemon behavior.

## Test Signals
Signals include successful build/download jobs, matrix Go test pass/fail, proxy error simulation pass/fail, and uploaded diagnostic logs for all modes.

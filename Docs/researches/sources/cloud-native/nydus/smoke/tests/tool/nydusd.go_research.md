# sources/cloud-native/nydus/smoke/tests/tool/nydusd.go

## Purpose
This is the central `nydusd` test harness. It generates daemon configs, starts FUSE and UFFD modes, mounts/unmounts images, exercises daemon APIs, fetches metrics/config, and verifies mounted file trees.

## Important APIs, Types, And Functions
Metric structs model daemon JSON responses. `NydusdConfig` contains mount, backend, cache, API, hot-upgrade, overlay, and UFFD fields. `Nydusd` wraps an HTTP client, `exec.Cmd`, wait channel, and config. Config templates cover regular and overlay modes. `makeConfig`, `newNydusd`, `NewNydusd`, `NewNydusdUffd`, `NewNydusdWithOverlay`, and `NewNydusdWithContext` construct daemons. Lifecycle methods include `Run`, `Mount`, `Shutdown`, `Umount`, `MountByAPI`, `UmountByAPI`, `WaitStatus`, `StartByAPI`, `SendFd`, `Takeover`, and `Exit`. Metrics/config methods fetch global, files, backend, latest files, access pattern, blobcache, inflight, and hot-reload config endpoints. `Verify` and `VerifyByPath` walk mounted trees and compare `tool.File` snapshots. Package function `Verify` mounts a context and verifies it.

## Control Flow
Construction writes a config JSON when needed, builds command args, and creates an HTTP client that dials the Unix API socket. `Run` starts the process and waits in a goroutine. Mount paths either start the daemon and wait for `RUNNING`, or post a mount config to the API. Verification walks the mounted directory and performs two-way expected/actual checks.

## State And Persistence
The harness writes config files into workdirs, creates Unix sockets, launches daemon processes, mounts FUSE filesystems, and may unmount lazily. It reads daemon API state and metrics but does not persist them. UFFD mode maps to sockets rather than FUSE mountpoints.

## Dependencies And Integration Points
It integrates tests with `nydusd` CLI, Unix-domain HTTP API, FUSE mount lifecycle, snapshotter hot-upgrade endpoints, UFFD subcommand, overlay config, and JSON metric schemas.

## Risks
`time.Sleep(2s)` after process start is a coarse readiness delay. Several API methods ignore HTTP status codes and only return transport errors. `defer resp.Body.Close()` inside `WaitStatus` loop can accumulate until the function returns. Lazy unmount and process exit timing can be host-sensitive.

## Test Signals
Signals include daemon state transitions, successful API calls, metric JSON decoding, and exact mounted file-tree comparisons. This harness amplifies failures from most smoke suites.

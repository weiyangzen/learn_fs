<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/builder.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/builder.go

Purpose: exposes a Docker build backend implemented on top of an embedded BuildKit controller.

Important APIs and control flow: `New` creates a request-body handler and controller. `DiskUsage` singleflights BuildKit disk usage and maps records to Docker API cache records. `Prune` validates Docker filters, converts them to BuildKit prune info, streams usage records, and returns reclaimed size and cache IDs. `Build` translates Docker build options into BuildKit frontend attrs, handles upload-request synchronization, cache-from, build args, labels, no-cache, pull mode, platform parsing, network mode, extra hosts, shm size, ulimits, exporters, inline cache, entitlements, solve request, status streaming, aux trace messages, and final image ID emission. Helpers implement gRPC stream proxies, upload rendezvous, extra-host conversion, ulimit conversion, and prune filter conversion.

State and persistence: holds build jobs and cancel functions in memory, streams request bodies through an internal HTTP handler, and relies on the controller for persistent cache/export state.

Dependencies and integration: integrates Docker API build options, BuildKit control API, BuildKit sessions/status/progress, Moby exporters, network options, daemon DNS host-gateway config, and cache prune filters.

Risks: build upload rendezvous has short timeouts and requires matching upload/build IDs. Only one output is supported. Filter conversion accepts a narrow set and maps `id` to regex matching. Status streaming uses a background request with `context.TODO`, so solve cancellation and status cancellation are intentionally decoupled.

Test signals: no direct tests in this subset; builder API and BuildKit integration suites cover behavior. Local `go test` could not be run because `go` is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/builder.go -->

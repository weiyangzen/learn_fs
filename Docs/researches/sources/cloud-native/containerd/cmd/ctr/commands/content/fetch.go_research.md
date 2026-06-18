# sources/cloud-native/containerd/cmd/ctr/commands/content/fetch.go

Purpose: implements `ctr content fetch`, which pulls image manifests/configs/layers into the content store without unpacking, plus progress tracking helpers.

Important APIs/types/functions: `fetchCommand`, `FetchConfig`, `NewFetchConfig()`, `Fetch()`, `ShowProgress()`, `Jobs`, `StatusInfoStatus`, `StatusInfo`, and `Display()`.

Control flow: command creates client/context, builds resolver/platform/metadata/progress config from flags, and calls `Fetch()`. `Fetch()` tracks descriptors through an image handler, configures pull labels/resolver/platforms/all-metadata options, starts a progress goroutine polling content store statuses, calls `client.Fetch()`, cancels progress, waits for final display, and returns the image metadata.

State and persistence: stores fetched content and image metadata through containerd fetch. Progress state is in-memory plus content-store active status reads.

Dependencies/integration: shared registry resolver, containerd remote options, content store, image handlers, platform matching, `httpdbg`, progress writer, errdefs.

Risks: progress totals are approximate and comments note restart skew. `metadata-only` sets `AllMetadata` and a matcher of `platforms.Any()` to effectively avoid platform blobs. A suspicious flag check references `max-concurrent-uploaded-layers` in fetch config, likely shared with push/upload options rather than fetch.

Test signals: no local tests for progress/status behavior.

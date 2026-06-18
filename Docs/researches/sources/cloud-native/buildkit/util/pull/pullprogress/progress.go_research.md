<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pullprogress/progress.go -->
# sources/cloud-native/buildkit/util/pull/pullprogress/progress.go

Purpose: wraps content providers and remote fetchers so reads/fetches emit progress based on content ingest or stored content status.

Important APIs and types: `PullManager`, `ProviderWithProgress`, `FetcherWithProgress`, `readerAtWithCancel`, `readerWithCancel`, and `trackProgress`.

Control flow: `ReaderAt` and `Fetch` delegate to the underlying provider/fetcher, then start `trackProgress` in a context detached from caller cancellation but canceled when the returned reader is closed. `trackProgress` ticks every 150ms, checks active ingest status with `remotes.MakeRefKey`, writes progress via `progress.NewFromContext`, and falls back to content `Info` to emit a final completed status when the blob is present.

State and persistence: progress goroutines are bound to reader lifetimes. Content state is read from the provided manager; no new persistent state is created beyond progress messages.

Dependencies and integration: uses containerd content/remotes, BuildKit progress context, BuildKit logging, and errdefs for not-found detection.

Risks: `Close` waits up to one second for the progress goroutine before warning, so leaked readers can leak progress goroutines. `context.WithoutCancel` intentionally keeps progress alive past caller cancellation until reader close.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/pull/pullprogress/progress.go -->

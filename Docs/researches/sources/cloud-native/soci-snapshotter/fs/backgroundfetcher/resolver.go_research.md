# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver.go

Purpose: defines the background fetch resolver contract and the sequential layer resolver that warms layer spans from span 0 upward.

Important APIs and flow: `Resolver` exposes `Resolve(context.Context) (more bool, err error)`, `Close`, and `Closed`. `base` embeds a span manager, layer digest, close state, and start timestamp protected by a mutex. `NewSequentialResolver` returns a `sequentialLayerResolver`. `Resolve` logs the current span, stores the start time on span 0, calls `FetchSingleSpan`, increments success metrics and `nextSpanFetchID` on success, returns `(true, nil)` while more spans might exist, returns `(false, nil)` and records total background-fetch latency on `spanmanager.ErrExceedMaxSpan`, and increments failure metrics plus wraps unexpected errors.

State and persistence: resolver state is the next span ID, closed flag, layer digest, and first-span start time. Actual persistence is delegated to `SpanManager.FetchSingleSpan`, which writes to the configured span cache.

Dependencies and integration: integrates `fs/span-manager`, ztoc compression span IDs, common metrics, containerd/logrus logging, and OCI digests. It is added to `BackgroundFetcher` by `layer.Resolver.Resolve` after the span manager has been initialized.

Risks and test signals: `Closed` and `Close` protect only the closed flag; `Resolve` itself does not check closed, relying on the fetcher to skip closed resolvers. A successful fetch always returns `more=true`, so completion is detected only by trying one span past `MaxSpanID`. Tests verify sequential ID progression and completion against real ztoc data, but they do not cover error metrics or concurrent `Close` while `Resolve` is active.

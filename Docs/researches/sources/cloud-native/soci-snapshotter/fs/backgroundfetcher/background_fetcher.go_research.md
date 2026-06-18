# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher.go

Purpose: implements the filesystem-wide background span fetch loop used after lazy SOCI layers have been mounted. The fetcher drains a bounded work queue of `Resolver` instances and repeatedly asks each resolver to fetch the next span, letting image startup remain lazy while unused spans are warmed into the span cache over time.

Important APIs and flow: `Option` functions configure silence period, fetch period, max queue size, and metric emission period. `NewBackgroundFetcher` builds a `rate.Limiter`, work queue, close channel, pause channel, and default `time.Sleep` pauser. `Add` queues a resolver, `Pause` queues a mount-triggered pause signal, `Close` signals shutdown, and `Run` loops until context cancellation or close. Each loop drains pending pause signals, optionally sleeps for the silence period, checks shutdown, pulls one resolver from `workQueue`, skips closed resolvers, runs `Resolve` in a goroutine, requeues it if more spans remain, and waits on the rate limiter. `emitWorkQueueMetric` periodically records queue depth through common metrics.

State and persistence: state is in-memory only: queue contents, pause signals, close signal, rate limiter, and pauser. It persists fetched bytes indirectly through the resolver/span manager/cache that it invokes. It does not own files or registry handles.

Dependencies and integration: depends on `backgroundfetcher.Resolver`, `golang.org/x/time/rate`, containerd logging, and `fs/metrics/common`. It is constructed by `fs.NewFilesystem` when background fetch is enabled and receives sequential layer resolvers from `layer.Resolver.Resolve`.

Risks and test signals: `Add`, `Pause`, and `Close` are blocking sends; if the queue or close channel has no receiver these calls can block. `Run` launches one goroutine per dequeued resolver and requeues from that goroutine, so queue backpressure can hold resolver goroutines. The tests verify pause coalescing and full cache warming for one and multiple span managers with zero fetch period, but they do not cover blocking shutdown, saturated queues, or metric ticker behavior.

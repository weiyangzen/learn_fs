# sources/cloud-native/containerd/core/events/proxy/remote_events.go

Purpose: remote event service client implementing publish, forward, and subscribe over gRPC or ttrpc.

Important APIs/types: `EventService` combines core event interfaces. `NewRemoteEvents` accepts gRPC/ttrpc clients or connections and returns either `grpcEventsProxy` or `ttrpcEventsProxy`. Both proxies implement `Publish`, `Forward`, and streaming `Subscribe`.

Control flow and state: publish marshals event into typeurl `Any`, wraps it in API request, and translates RPC errors to native. Forward converts envelope timestamp and event payload into API envelope. Subscribe opens a remote stream, starts a goroutine to receive API envelopes, converts timestamps to `time.Time`, forwards envelopes on `evq`, and reports receive/context errors on `errq`.

Dependencies and integration: events service API, API envelope types, typeurl, grpc, ttrpc, errgrpc, protobuf timestamp helpers.

Risks: constructor panics on unsupported client. Subscribe returns remote receive errors directly rather than `errgrpc.ToNative`. Event queue channel is not explicitly closed, only error queue closes; consumers should watch errs/context. gRPC and ttrpc implementations are duplicated and must stay in sync.

Test signals: no direct tests here. Integration tests should cover stream cancellation, error translation, and envelope round-trip.

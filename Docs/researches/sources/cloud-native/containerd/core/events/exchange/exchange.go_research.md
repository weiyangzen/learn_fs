# sources/cloud-native/containerd/core/events/exchange/exchange.go

Purpose: in-process event exchange implementing publisher, forwarder, and subscriber interfaces.

Important APIs/functions: `NewExchange`, `Exchange.Forward`, `Exchange.Publish`, `Exchange.Subscribe`, `validateTopic`, `validateEnvelope`, and `adapt`.

Control flow and state: `Exchange` wraps a docker `go-events` broadcaster. `Publish` requires namespace from context, validates topic, marshals the event, stamps UTC time, and writes an envelope. `Forward` validates a caller-supplied envelope and writes it unchanged. `Subscribe` creates a broadcaster channel/queue, optionally wraps it in a filters matcher, forwards envelopes to an output channel until context cancellation, and reports terminal errors on a buffered error channel.

Dependencies and integration: namespaces, identifiers, filters, errdefs, logging, typeurl, and docker/go-events.

Risks: filters match any provided filter string, with comma syntax used by the filter parser for AND. The subscription goroutine sends a nil error on normal cancellation because it writes `errq <- err`; consumers must handle nil. Invalid non-envelope events should be impossible through public methods but is guarded.

Test signals: `exchange_test.go` covers fan-out, filtering, and topic validation for publish/forward.

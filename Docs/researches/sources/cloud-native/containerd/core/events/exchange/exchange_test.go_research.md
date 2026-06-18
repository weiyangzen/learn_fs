# sources/cloud-native/containerd/core/events/exchange/exchange_test.go

Purpose: unit tests for the in-process event exchange.

Important coverage: `TestExchangeBasic` publishes three container-create events and verifies two subscribers receive all of them. `TestExchangeFilters` creates multiple subscriptions with no filters, topic filters, event field filters, regex filters, OR filters, and an AND topic/id filter. `TestExchangeValidateTopic` verifies publish and forward accept slash-prefixed topics and reject a topic without a leading slash with `ErrInvalidArgument`.

Control flow and state: tests use namespace contexts, async publisher goroutines, subscriber cancellation once expected events are received, and typeurl unmarshal plus protobuf-aware cmp.

Dependencies and integration: API event types, core events, namespaces, prototest comparison helpers, errdefs, typeurl.

Risks: tests can hang if expected events are not received because they wait on channels. They do not cover invalid filter syntax, invalid namespace, empty topic, one-component slash-only topic, forwarded zero timestamp, or unexpected broadcaster event types.

Test signals: strong signal for event fan-out and filter semantics over topic and event fields.

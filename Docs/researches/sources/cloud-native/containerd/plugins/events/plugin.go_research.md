# sources/cloud-native/containerd/plugins/events/plugin.go

## Purpose
Registers the core containerd event exchange plugin.

## Important APIs, Types, And Functions
`init` registers `plugins.EventPlugin` with ID `exchange`; its init function returns `exchange.NewExchange()`.

## Control Flow
Plugin initialization simply constructs an in-memory event exchange without external prerequisites.

## State And Persistence
Event state is in-memory pub/sub only. No event persistence is handled here.

## Dependencies And Integration Points
Services and plugins use the exchange as `events.Publisher` and subscriber hub. Event gRPC/TTRPC services depend on this plugin.

## Risks
Because events are in-memory, subscribers only see events after subscription and daemon restart loses in-flight subscriptions.

## Test Signals
No direct tests here; event service tests and daemon integration cover behavior.

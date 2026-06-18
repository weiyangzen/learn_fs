<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog.go

## Purpose

This internal daemon plugin logs peer connection and identify events when explicitly enabled in plugin config.

## Important APIs, Types, and Functions

`eventType`, `plEvent`, and `peerLogPlugin` model queued events. `extractEnabled` reads boolean `Enabled` from untyped config. `Init` allocates a large buffered event channel and stores enabled state. `Start` sets plugin log level, subscribes to identify events, registers a network connected notifee, and starts event collection. `emit` drops events under backpressure. `collectEvents` logs connected/identified events and reports dropped counts with backoff and queue draining.

## Control Flow, State, and Integration

When disabled, `Start` returns without side effects. When enabled, it creates goroutines tied to node context. State is in memory: event queue, dropped counter, and event subscriptions. It reads agent versions from the peerstore.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p event bus/network/peerstore, Kubo core, zap logging, and atomics. Risks include high memory buffer size, dropped event accounting, event goroutines not being stopped except by node context, and unsupported config shape. `peerlog_test.go` covers config extraction; integration tests should cover event emission under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog.go -->

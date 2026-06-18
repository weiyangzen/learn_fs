# sources/cloud-native/containerd/core/diff/stream.go

Purpose: stream processor registry and default layer decompression pipeline for diff application.

Important APIs/types: `RegisterProcessor`, `GetProcessor`, `Handler`, `StaticHandler`, `StreamProcessorInit`, `RawProcessor`, `StreamProcessor`, `NewProcessorChain`, `BinaryHandler`, and default `compressedHandler`. `ErrNoProcessor` signals missing handlers.

Control flow and state: package init registers `compressedHandler`. Registered handlers are stored globally and searched in reverse registration order so user handlers take precedence. `compressedHandler` uses image media type compression detection to either wrap a decompressor or pass through to a standard processor, both returning OCI uncompressed layer media type. `BinaryHandler` builds handler closures that invoke external processors for selected media types.

Dependencies and integration: core image media type helpers, archive compression package, typeurl payloads, OCI media types, and platform-specific `NewBinaryProcessor`.

Risks: global handler registry is unsynchronized and should be configured during init, not concurrently. Repeated registration affects process-wide behavior. External binary processors introduce process, payload, and error propagation concerns.

Test signals: no direct tests in this file. Coverage depends on diff apply and configured stream processor integration tests.

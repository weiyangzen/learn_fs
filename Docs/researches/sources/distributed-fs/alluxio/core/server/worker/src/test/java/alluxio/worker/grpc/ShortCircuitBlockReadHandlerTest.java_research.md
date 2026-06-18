# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockReadHandlerTest.java

Purpose: tests `ShortCircuitBlockReadHandler` opening local block paths for clients, including promotion and pinning behavior.

Important APIs and helpers: setup creates a real `TieredBlockStore` with two temp tiers, mocked block-master client pool, and a custom response observer. Tests cover nonexistent block access, access without promotion, access with promotion, pinning while open, unpin on error, and rejecting repeated access on the same handler.

Control flow and state: helper `createLocalBlock` creates, writes, and commits a block in a selected tier. `accessBlock` sends `OpenLocalBlockRequest`, completes the stream, and asserts one response with the expected local path. Promotion changes expected location from second tier to first tier.

Dependencies and integration: depends on `ShortCircuitBlockReadHandler`, `TieredBlockStore`, `BlockWriter`, worker tier configuration, `OpenLocalBlockRequest/Response`, and Mockito.

Risks and test signals: strong signal for local-read lifecycle, pin/unpin correctness, and promotion integration. It uses timeouts for error paths and local filesystem state, so slow cleanup could cause flakes.

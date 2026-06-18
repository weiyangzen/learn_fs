# sources/control-plane/mayastor/io-engine/src/grpc/v1/test.rs

Purpose: this v1 test service exposes non-production operations used by tests and diagnostics: feature discovery, streamed replica wiping, and optional fault injection management.

Important APIs/types/functions: `TestService` wraps a `ReplicaService`. `get_features` advertises wipe methods and CRC32C checksums. `wipe_replica` returns a `ReceiverStream<WipeReplicaResponse>`. `TryFrom<&Option<StreamWipeOptions>>` validates stream wipe options and maps protobuf wipe methods to core wipe methods. `WiperStream` adapts wiper notifications to an mpsc stream. Fault-injection RPCs compile only behind the `fault-injection` feature.

Control flow: `wipe_replica` creates a bounded mpsc channel, parses options before spawning work, then `core::spawn`s an async task that takes the replica service shared lock, optionally verifies the pool, finds a replica allowing snapshots, creates a `Wiper`, wraps it in `StreamedWiper`, runs the wipe, and streams progress via nonblocking `try_send`. Errors are sent to the stream unless the client has disconnected.

State and persistence: wiping destructively changes replica/snapshot data according to the selected method. Fault injection mutates global fault-injection state. No durable metadata is written here.

Dependencies and integration points: integrates core wiper types, replica factory/wrapper, pool verification, `tokio_stream`, optional `core::fault_injection`, and v1 test protobufs.

Risks: destructive API is exposed through gRPC when test service is enabled; backpressure drops into `ChunkNotifyFailed` because `try_send` fails if the buffer fills; options allow methods not advertised by `get_features` if core supports them; fault injection availability changes at compile time. Test signals should cover client disconnect, channel saturation, invalid options, pool mismatch, snapshot wiping allowance, checksum progress, and feature-disabled fault-injection statuses.

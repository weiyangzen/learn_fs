## sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider_test.go

Purpose: tests the raw SSH provider transport as a generic bidirectional byte tunnel.

Important APIs/types/functions: `echoServer` accepts net connections and responds to JSON `echoRequest` messages with `echoResponse` counts. `dialerFnToGRPCDialer` adapts a provider dialer into `grpc.WithContextDialer`. `TestRawProvider` wires a `socketProvider`, gRPC server/client, and echo backend over `pipeListener`. `streamWriter` and `streamReader` adapt gRPC `BytesMessage` streams to `io.Writer`/`io.Reader`.

Control flow: the test starts echo and provider services, checks unknown and known agent IDs, opens `ForwardAgent` with metadata ID `test`, sends two small JSON messages and one 10,000 byte payload, then verifies echoed data and incrementing counts.

State and persistence: all test state is in memory. Stream reader buffers partial `BytesMessage` payloads to satisfy arbitrary `Read` sizes.

Dependencies and integration points: covers generated gRPC stubs, `socketProvider`, `sshforward.Copy`, and `pipeListener` together.

Risks and test signals: this is a strong signal for byte-stream correctness, metadata selection, and larger-than-single-small-message handling. It does not test cancellation, EOF half-close, or real SSH-agent semantics.

# sources/control-plane/longhorn-engine/pkg/dataconn/server.go

Purpose: implements the server side of Longhorn's lightweight data connection protocol. It bridges a `net.Conn` carrying `dataconn.Message` records to a `types.DataProcessor` that supplies `ReadAt`, `WriteAt`, `UnmapAt`, and `PingResponse`.

Important APIs/types/functions: `Server` owns a `Wire`, a buffered `responses` channel, a `done` signal channel, and the backend processor. `NewServer` prepares the wire and channels. `Handle` starts the writer goroutine and runs the read loop. `readFromWire` decodes one request and launches a handler goroutine by message type. `handleRead`, `handleWrite`, `handleUnmap`, and `handlePing` invoke the backend. `pushResponse` normalizes backend results into `TypeResponse`, `TypeEOF`, `TypeENOSPC`, or `TypeError`. `write` serializes responses and attempts a best-effort `TypeClose` on stop.

Control flow: `Handle` returns when `read` returns an error or sees `done`. Each read operation is dispatched asynchronously, so multiple backend operations can be in flight and responses can be reordered only by channel scheduling, not by explicit sequencing. `pushResponse` mutates the request message into a response and queues it. The writer goroutine does not exit after receiving `done`; the code intentionally keeps accepting late responses from in-flight handlers after sending a close notification.

State and persistence: no durable state. Runtime state is the response queue and the done channel. Data mutations are delegated to the provided `DataProcessor`, usually a replica server or socket frontend wrapper.

Dependencies and integration points: depends on `Wire` in `wire.go`, message constants in `types.go`, `types.DataProcessor`, and `types.ErrNoSpaceLeftOnDevice`. It is used by the Unix socket frontend and replica data server over TCP or Unix sockets.

Risks: one goroutine is spawned per wire read plus one per operation; sustained high request rates can create many goroutines. `write` never returns on stop, so connection lifetime relies on outer connection close/process shutdown. Unknown message types are silently ignored but still produce `nil` from `readFromWire`, which can leave callers waiting. The shared `done` channel is used both to stop reads and signal from `Handle` defer, making ordering subtle.

Test signals: no direct tests in this file. Behavior is indirectly covered through frontend/replica data paths and dataconn client/server integration if present elsewhere.

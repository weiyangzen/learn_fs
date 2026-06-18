<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/client.go -->
## sources/control-plane/longhorn-engine/pkg/dataconn/client.go

Purpose: asynchronous data-plane client for replica read/write/unmap/ping operations over one or more network connections.

Important APIs/types/functions: `Client` owns request/send/response/end channels, sequence counter, pending message map, wires, peer address, and shared timeout tracker. `NewClient` wraps `net.Conn`s as `Wire`s, starts loop, writer goroutines, and reader goroutines. Public methods implement `TargetID`, `ReadAt`, `WriteAt`, `UnmapAt`, `Ping`, `SetError`, and `Close`. Internal methods include `operation`, `loop`, `nextSeq`, `replyError`, `handleRequest`, `handleResponse`, `write`, and `read`.

Control flow: public operations create a `Message`, enqueue it, and block until completion. The loop assigns sequence IDs, tracks pending journal operations, sends messages to wires, handles responses, and converts transport errors or shared timeout breaches into errors for all in-flight and future requests. A one-second ticker checks elapsed time while I/O is in flight and uses shared timeout accounting.

State and persistence: no persistent state. Maintains in-memory pending message map and operation journal entries via sparse-tools stats. Data persistence occurs in remote replica when messages are processed.

Dependencies and integration points: used by `backend/remote`. Depends on `Wire`, dataconn message constants, Longhorn shared timeout interface, `net.Conn`, and sparse-tools operation journal.

Risks: operations block until completion; channel buffers reduce but do not eliminate deadlock risk if the loop exits unexpectedly. Transport errors poison the client for future requests. Multiple wires share one send channel, so messages are distributed among writer goroutines. Visible duplicate `replyError` in one branch should be validated; duplicate completion could panic or block if real. `Close` closes wires then signals end; reader goroutines stop on read errors.

Test signals: transport tests should cover successful read/write/unmap/ping, timeout, transport error propagation to pending and future requests, close behavior, and multi-connection sequencing.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/client.go -->

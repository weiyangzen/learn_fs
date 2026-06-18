<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/dial.go -->
# sources/cloud-native/buildkit/session/grpchijack/dial.go

Purpose: adapts the BuildKit control service `Session` stream into a `net.Conn` suitable for session gRPC transport.

Important APIs, types, and functions: `Dialer(api)` returns a `session.Dialer` that lowercases headers, attaches them as outgoing metadata, opens `api.Session`, and wraps the stream with `streamToConn`. `conn` implements `net.Conn` over `SendMsg`/`RecvMsg`, buffering partial reads, serializing reads/writes with mutexes, and closing the client send side when possible.

Control flow and state: `Read` reuses leftover bytes before receiving a new `BytesMessage`. `Write` sends one message. `Close` calls `CloseSend` for client streams, drains received messages until EOF, appends leftovers, closes `closeCh`, and reports non-EOF receive errors. Deadline methods are no-ops.

Dependencies and integration: depends on BuildKit control API `BytesMessage`, gRPC metadata, and session dialer contract. Used when clients connect sessions through the control API instead of raw HTTP upgrade.

Risks and test signals: deadline no-ops can affect code expecting timeout semantics. `Close` appends `c.buf` after resetting it from message capacity, which deserves scrutiny for draining correctness. Tests should cover partial reads, concurrent read/write, close-drain behavior, and metadata lowercasing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/dial.go -->

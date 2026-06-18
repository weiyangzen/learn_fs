<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/hijack.go -->
# sources/cloud-native/buildkit/session/grpchijack/hijack.go

Purpose: server-side helper for turning a control service session stream into a `net.Conn` plus incoming metadata.

Important APIs, types, and functions: `Hijack(stream)` reads incoming metadata from stream context, wraps the stream via `streamToConn`, and returns the connection, close channel, and metadata map.

Control flow and state: no persistence beyond stream connection state.

Dependencies and integration: paired with `grpchijack.Dialer` and used by control service session handling to feed session manager connections.

Risks and test signals: metadata is returned even if absent as the zero metadata map. Tests should verify metadata propagation and close channel behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpchijack/hijack.go -->

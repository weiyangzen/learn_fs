<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/manager.go -->
# sources/cloud-native/buildkit/session/manager.go

Purpose: tracks active BuildKit sessions and exposes callers for session-scoped services.

Important APIs, types, and functions: `Caller` interface exposes `Context`, `Supports`, `Conn`, and `SharedKey`. `Manager` stores session clients under a mutex/condition. `NewManager`, `HandleHTTPRequest`, `HandleConn`, internal `handleConn`, `Get`, `client.Context`, `SharedKey`, `Supports`, `Conn`, and `canonicalHeaders` implement session registration and lookup.

Control flow and state: incoming HTTP upgrade requests are hijacked, validated for `h2c`, acknowledged with 101, then passed to `handleConn`. `handleConn` canonicalizes headers, reads session id/shared key/methods, creates a gRPC client over the connection, stores the session, broadcasts waiters, waits for context cancellation, closes the connection, and removes the session. `Get` normalizes prefixed ids, waits on the condition unless `noWait`, and returns a caller or nil.

Dependencies and integration: used by BuildKit daemon session handling, auth/filesync/content/secrets callers, HTTP upgrade paths, and raw/grpchijack connection paths.

Risks and test signals: duplicate session ids are rejected. Missing session ids are not explicitly validated here. Condition waits rely on a cancellation goroutine broadcasting. Tests should cover HTTP upgrade validation, duplicate sessions, method support matching, noWait lookup, and cleanup on close.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/manager.go -->

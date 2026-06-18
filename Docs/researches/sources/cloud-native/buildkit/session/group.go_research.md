<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/group.go -->
# sources/cloud-native/buildkit/session/group.go

Purpose: defines session groups and iteration helpers for trying operations against one of several active sessions.

Important APIs, types, and functions: `ErrNoActiveSessions`, interfaces `Group` and `Iterator`, `NewGroup`, `group.NextSession`, `AllSessionIDs`, and `Manager.Any`. `Any` iterates session ids, waits up to 5 seconds for each session, invokes a callback with the caller, returns on first success, and otherwise returns the last error or `ErrNoActiveSessions`.

Control flow and state: group iteration consumes ids in order on iterator copies. `Any` uses `Manager.Get` and callback errors to advance to the next session.

Dependencies and integration: used by auth helpers and other session-scoped features that can use any active client session in a group.

Risks and test signals: `defer cancel` inside the loop defers all cancels until function return, which is bounded by group size but worth noting. Last-error behavior can hide earlier failures. Tests should cover nil groups, empty groups, session wait timeout, and fallback to later sessions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/group.go -->

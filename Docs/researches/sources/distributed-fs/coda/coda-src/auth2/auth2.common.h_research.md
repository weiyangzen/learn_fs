# sources/distributed-fs/coda/coda-src/auth2/auth2.common.h

Purpose: Defines per-connection auth server state shared by auth2 implementation and helpers.

Important APIs/types: `struct UserInfo` with `RPC2_Handle handle`, `ViceId`, `HasQuit`, `PRS_InternalCPS *UserCPS`, and `LastUsed`.

Control flow and state model: Auth server allocates one `UserInfo` per accepted connection, attaches it as an RPC2 private pointer, updates `LastUsed`, and honors `HasQuit` in service routines.

Persistence and integration: In-memory only. Integrates auth2 server RPC routines with AL CPS and RPC2 connection lifecycle.

Risks and test signals: `LastUsed` is an `int` despite storing `time_t`. `UserCPS` ownership must be released on unbind/termination.

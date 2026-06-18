# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcAcceptedReply.java

Purpose: represents the accepted branch of an ONC RPC reply body.

Important APIs/types/functions: `AcceptState` enum, `getAcceptInstance`, `getInstance`, static `read`, `getAcceptState`, and `write`.

Control flow: read consumes a verifier and accept-state integer from XDR. Write emits xid, message type, reply state, verifier, and accept state. `getAcceptInstance` is a convenience for `SUCCESS`.

State and persistence: immutable fields inherited from `RpcReply` plus `acceptState`; no persistence.

Dependencies and integration: used by `RpcProgram`, `PortmapResponse`, and tests to build success and program/procedure error replies. Depends on `Verifier`.

Risks: enum `fromValue` uses ordinal indexing without bounds checks, so malformed wire values throw array exceptions. Program mismatch replies require callers to append version bounds after this object writes its common body.

Test signals: `TestRpcAcceptedReply` validates serialization and parse round trips.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/PortmapRequest.java

Purpose: helper for parsing and constructing portmap SET/UNSET requests.

Important APIs/types/functions: static `mapping` and `create`.

Control flow: `mapping` deserializes a `PortmapMapping` from the current XDR position. `create` builds an `RpcCall` with a new xid, portmap program/version, `PMAPPROC_SET` or `PMAPPROC_UNSET`, null credentials and verifier, writes it to XDR, then serializes the mapping body.

State and persistence: stateless utility; no persistence.

Dependencies and integration: used by `RpcProgram.register`/`unregister` and `RpcProgramPortmap` request handling. Depends on `RpcUtil.getNewXid`, `CredentialsNone`, and `VerifierNone`.

Risks: only supports SET/UNSET creation. Xid generation is inherited from non-atomic `RpcUtil`. Caller must send over the correct transport.

Test signals: portmap and RPC call tests cover request encoding and mapping parsing.

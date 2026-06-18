# sources/distributed-fs/coda/coda-src/resolution/ruconflict.h

Purpose: declares remove/update conflict detection helpers used by subordinate phase 3 semantic validation.

Important APIs/types: `RUParm` carries the recursive directory conflict walk state: `vlist` for loaded vnodes, `AllLogs` for remote logs grouped by host/object, `srvrid` for the server whose remove is being checked, `vid` for the volume id, and `rcode` as an accumulated nonzero conflict result. Public functions are `RUConflict(rsle *, dlist *, olist *, ViceFid *)`, two `FileRUConf` overloads for log-entry or explicit deleted version vector comparisons, and `NewDirRUConf` for recursive directory entry handling.

Control flow and integration: `subresphase3.cc` calls `RUConflict` from `CheckValidityResOp` for remove and rmdir compensation operations that otherwise look performable. The helper bridges `rsle` log entries, Coda VLE lists, remote parsed logs, and vnode version vectors.

State/persistence: the header owns no state. It describes analysis over persistent vnode/log state and returns a boolean-style conflict code. Risks are tight coupling to `rsle` opcode layout and `Vnode` version-vector semantics. Test signals are consistent conflict decisions from both `FileRUConf` overloads and correct propagation of `RUParm::rcode` through recursive directory enumeration.

# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nlm4.h

Purpose: generated XDR type, procedure, and maximum-size definitions for NLMv4 network lock manager protocol messages.

Important APIs and types: constants define maximum string/object sizes and `NLM4_PROG`. Types include `netobj`, share mode/access enums, scalar aliases, `nlm4_stats`, `nlm4_holder`, `nlm4_testrply`, `nlm4_stat`, `nlm4_res`, `nlm4_testres`, `nlm4_lock`, lock/cancel/test/unlock args, share/shareargs/shareres, notify/notifyargs, and procedure IDs from NULL through lock/share/free-all operations. Size macros compute XDR word counts and `NLM4_MAX_ARGS_SZ`.

Control flow: lock manager XDR code uses these declarations to marshal lock requests, test replies, callbacks, share operations, and status monitor notifications.

State and persistence: no state is owned; structs are transient decoded or encoded protocol messages. Actual lock state lives in NLM/lockd code.

Dependencies and integration points: depends on `_defs.h` and generated XDR primitive definitions. It is generated from `Documentation/sunrpc/xdr/nlm4.x`.

Risks and test signals: risks include generated spec drift, maximum string/object mismatch, lock range width errors, status endian handling because `nlm4_stats` is `__be32`, and procedure ID incompatibility. Test with lockd interoperability, lock/test/cancel/unlock/share RPC vectors, status monitor notify, and malformed oversized netobjs.

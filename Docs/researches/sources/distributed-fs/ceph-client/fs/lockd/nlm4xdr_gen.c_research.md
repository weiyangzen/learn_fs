# sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.c` is generated server-side XDR encode/decode support for NLMv4, produced by `xdrgen` from `Documentation/sunrpc/xdr/nlm4.x`. It decodes service request arguments and encodes service responses for NLMv4 server procedures. The source was read as a complete 724-line generated file.

## Important APIs, Types, and Functions

Public decode wrappers include `nlm4_svc_decode_void`, `nlm4_svc_decode_nlm4_testargs`, `nlm4_svc_decode_nlm4_lockargs`, `nlm4_svc_decode_nlm4_cancargs`, `nlm4_svc_decode_nlm4_unlockargs`, `nlm4_svc_decode_nlm4_testres`, `nlm4_svc_decode_nlm4_res`, `nlm4_svc_decode_nlm4_notifyargs`, `nlm4_svc_decode_nlm4_shareargs`, and `nlm4_svc_decode_nlm4_notify`. Public encoders include `nlm4_svc_encode_void`, `nlm4_svc_encode_nlm4_testres`, `nlm4_svc_encode_nlm4_res`, and `nlm4_svc_encode_nlm4_shareres`.

## Control Flow

Generated leaf decoders parse primitive XDR values, strings, opaque netobjs, stats, holders, locks, share arguments, notify arguments, and discriminated TEST replies. Service wrappers cast `rqstp->rq_argp` to the generated type and call the matching decoder. Encoders perform the reverse from `rqstp->rq_resp`, checking maximum string lengths before writing opaque data and encoding union arms only for statuses that require them.

## State and Persistence Behavior

No state is owned. Data is decoded into SUNRPC per-request argument buffers and encoded from response buffers. Procedure counters and dispatch tables are elsewhere.

## Dependencies and Integration Points

It depends on `nlm4xdr_gen.h`, generated type definitions in `include/linux/sunrpc/xdrgen/nlm4.h`, SUNRPC service request structures, and xdrgen builtin helpers. Server NLMv4 procedure tables consume these wrappers.

## Risks and Edge Cases

Manual edits will be overwritten. The generated code must stay synchronized with the `.x` protocol and generated header/type definitions. Decode functions return boolean failure without rich errno, so callers must map failures correctly. String/netobj length limits are protocol-critical.

## Test Signals

Signals include `make xdrgen` regeneration diff checks, server-side XDR round trips, malformed XDR fuzzing for each NLMv4 argument type, share/notify/test union coverage, and lockd NLMv4 server interoperability tests.

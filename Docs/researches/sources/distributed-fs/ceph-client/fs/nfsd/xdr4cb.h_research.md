# sources/distributed-fs/ceph-client/fs/nfsd/xdr4cb.h

## Purpose

`xdr4cb.h` defines compile-time XDR buffer size estimates for NFSv4 callback RPCs sent by NFSD to clients. It supports sizing callback encode/decode buffers for CB_NULL, CB_SEQUENCE, CB_RECALL, CB_LAYOUTRECALL, CB_NOTIFY_LOCK, CB_OFFLOAD, CB_RECALL_ANY, and CB_GETATTR.

## Important APIs, Types, and Functions

The file is macro-only. Base sizes include `NFS4_MAXTAGLEN`, compound header sizes, session id size, referring call/list sizes, operation encode/decode sizes, filehandle size, and stateid size. Operation sizes are defined as `NFS4_enc_cb_*_sz` and `NFS4_dec_cb_*_sz`, expressed in XDR words. `NFS4_enc_cb_getattr_sz` and `NFS4_dec_cb_getattr_sz` explicitly document the expected attribute bitmap and returned attribute payload fields.

## Control Flow

Callback code uses these constants when constructing `rpc_procinfo` entries or allocating XDR buffers. Each callback compound includes a compound header and, for session-aware callbacks, a CB_SEQUENCE plus one callback operation. Decode sizes account for callback compound response headers and per-operation status fields.

## State and Persistence Behavior

No state is stored here. The constants influence transient RPC buffer allocation. Incorrect sizing can lead to encode reservation failures or truncated decode handling but does not persist data directly.

## Dependencies and Integration Points

The macros depend on NFSv4 constants such as `NFS4_MAX_SESSIONID_LEN`, `NFS4_FHSIZE`, `NFS4_STATEID_SIZE`, `NFS4_OPAQUE_LIMIT`, `NFS4_VERIFIER_SIZE`, and `XDR_QUADLEN`. They integrate with NFSv4 callback client code and callback tracepoints.

## Risks and Edge Cases

Manual XDR word accounting can drift when callback encoding changes. Underestimates cause buffer exhaustion; overestimates waste memory but are safer. `NFS4_MAXTAGLEN` is lower than NFSD compound tag max and must match callback protocol assumptions. CB_GETATTR decode sizing must remain aligned with exactly the attributes NFSD asks clients to return.

## Test Signals

Exercise each callback path with tracing enabled: delegation recall, layout recall, blocked-lock notify, offload completion, recall-any, and callback getattr. Useful signals are absence of `nfserr_resource`/XDR decode failures, successful CB_SEQUENCE handling, and correct callback status propagation under small buffer stress.

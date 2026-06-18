# sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h

Purpose: Defines SUNRPC GSS authentication tracepoints for client and server GSS-API operations, context lifecycle, sequence-number validation, gssd upcalls, context import, pseudoflavor selection, and mechanism lookup failures.

Important APIs/types/functions: Symbolic maps cover RPC GSS services, GSS major status values, and Kerberos pseudoflavors. Event classes include `rpcgss_gssapi_event`, `rpcgss_ctx_class`, `rpcgss_svc_gssapi_class`, and `rpcgss_svc_seqno_class`. Events include `rpcgss_import_ctx`, client `get_mic`/`verify_mic`/`wrap`/`unwrap`, context init/destroy, server wrap/unwrap/mic/get_mic, wrap/unwrap failure, bad sequence events, accept upcall, authenticate, `rpcgss_seqno`, `rpcgss_need_reencode`, `rpcgss_update_slack`, upcall message/result, context details, `rpcgss_createauth`, and `rpcgss_oid_to_mech`.

Control flow: Client and server SUNRPC auth paths emit events while creating credentials, importing contexts, wrapping/unwrapping/verifying messages, checking sequence windows, talking to gssd, and adjusting XDR slack. Trace entries copy task/client IDs, XIDs, principals, remote addresses, status codes, sequence numbers, and auth sizing.

State and persistence: No state is owned. It observes RPC task/auth/context state, server request state, gssd upcall data, and sequence windows. Security context persistence belongs to RPC/GSS caches and userspace gssd.

Dependencies and integration points: Depends on tracepoints and `trace/misc/sunrpc.h`; integrates with NFS/SUNRPC client and server RPCSEC_GSS authentication.

Risks and test signals: Risks include leaking principal/upcall data, status mapping drift, sequence-window race interpretation, and task/request pointer lifetime issues. Test Kerberos krb5/krb5i/krb5p mounts, context expiry/renewal, bad sequence replay, gssd failure, server accept upcalls, wrap/unwrap failures, and trace output permission handling.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h` completely for this pass (688 lines, 14931 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h_research.md`.

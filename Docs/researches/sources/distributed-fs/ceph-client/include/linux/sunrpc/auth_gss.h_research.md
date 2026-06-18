# sources/distributed-fs/ceph-client/include/linux/sunrpc/auth_gss.h

Purpose: defines RPCSEC_GSS wire structures and client credential/context state shared by SUNRPC GSS authentication code.

Important APIs and types: constants include `RPC_GSS_VERSION` and `MAXSEQ`. `enum rpc_gss_proc` covers data, init, continue-init, and destroy control procedures; `enum rpc_gss_svc` covers none, integrity, and privacy services. Wire structs are `rpc_gss_wire_cred`, `rpc_gss_wire_verf`, and `rpc_gss_init_res`. `struct gss_cl_ctx` tracks refcount, procedure, sequence numbers, locking, local GSS context, wire context, acceptor, window, expiry, and RCU teardown. `struct gss_cred` embeds `rpc_cred` and references the active context or pending upcall.

Control flow: credentials marshal a GSS wire cred and verifier, use upcalls to establish `gss_cl_ctx`, then sequence, sign, encrypt, validate, or destroy contexts depending on procedure and service.

State and persistence: GSS client state is runtime-only but long-lived across RPC tasks until expiry: context handles, sequence counters, upcall timestamps, and principal pointers.

Dependencies and integration points: depends on `auth.h`, `svc.h`, and `gss_api.h`; integrates client RPCSEC_GSS with server request handling and the mechanism-independent GSS layer.

Risks and test signals: risks include sequence wrap/replay handling, context expiry, RCU context replacement, upcall races, and incorrect service selection. Test with krb5 `krb5`, `krb5i`, `krb5p`, context renewal, replay windows, and concurrent RPC load.

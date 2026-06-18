## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/auth-glusterfs.c

Purpose: implements the server-side `AUTH_GLUSTERFS-v3` authentication handler. It decodes GlusterFS-specific RPC credentials and populates `rpcsvc_request_t` identity, group, lock-owner, flag, and ctime fields.

Important APIs: `xdr_to_glusterfs_auth_v3` decodes `auth_glusterfs_params_v3` from a fixed `GF_MAX_AUTH_BYTES` XDR buffer. `auth_glusterfs_v3_authenticate` is the main authenticator. It sets `req->pid`, `uid`, `gid`, `lk_owner`, `auxgidcount`, `flags`, and `ctime`. `rpcsvc_auth_glusterfs_v3_init` returns a static `rpcsvc_auth_t` with auth number `AUTH_GLUSTERFS_v3`.

Control flow: authentication decodes credentials, computes maximum allowable group and lock-owner sizes using `GF_AUTH_GLUSTERFS_MAX_GROUPS` and `GF_AUTH_GLUSTERFS_MAX_LKOWNER`, truncates group count if necessary, rejects overlarge lock owners, chooses small embedded auxgid storage or dynamically allocated `auxgidlarge`, copies group IDs and lock-owner bytes, then accepts the request.

State and persistence: state is per request. Large auxgid arrays are heap allocated and later owned by request cleanup. XDR-decoded temporary arrays are freed before return.

Dependencies and integration: depends on XDR definitions from `glusterfs4-xdr.h`, common auth constants, `rpcsvc-auth.c` registration, and client-side credential serialization in `rpc-clnt.c`.

Risks: this is security-sensitive. It authenticates identity values supplied by the RPC credential format; trust depends on the surrounding transport and deployment model. Bounds checks protect header size but truncating group lists can change authorization outcomes. Lock-owner copying assumes destination capacity matches protocol maxima.

Test signals: XDR decode tests, max group/lock-owner boundary tests, large auxgid allocation tests, and end-to-end client/server auth negotiation with v3 credentials.

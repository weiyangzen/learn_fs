# sources/distributed-fs/ceph-client/net/sunrpc/auth_unix.c

Purpose: implements AUTH_UNIX/AUTH_SYS client authentication. It allocates per-credential objects from current task credentials, marshals nodename, fsuid, fsgid, and a bounded supplementary group list, validates server verifiers, and provides a small mempool for async allocation fallback.

Important APIs/types/functions: exported auth table is `authunix_ops`; lifecycle helpers are `rpc_init_authunix()` and `rpc_destroy_authunix()`. Credential ops are `unix_credops` with `unx_lookup_cred`, `unx_destroy_cred`, `unx_match`, `unx_marshal`, `unx_refresh`, and `unx_validate`. State is static `unix_auth` and `unix_pool`.

Control flow: auth creation returns the singleton auth handle. Credential lookup allocates `struct rpc_cred` with the task GFP mask, falling back to `unix_pool` for async lookups. Matching compares fsuid, fsgid, and up to `UNX_NGROUPS` supplementary gids. Marshalling writes AUTH_UNIX flavor, credential length placeholder, zero stamp, client nodename, uid, gid, group array, fixes credential length, and appends an AUTH_NULL verifier. Reply validation accepts NULL, UNIX, or SHORT verifiers up to `RPC_MAX_AUTH_SIZE` and adjusts auth reply slack/alignment to the verifier size.

State and persistence behavior: per-call credentials hold a ref to kernel `struct cred`; destruction runs through RCU and frees via the mempool. Singleton auth state stores dynamic reply verifier sizing after validation. No state is persisted beyond kernel memory.

Dependencies/integration points: plugged into the generic SUNRPC auth framework and used by NFS and other AUTH_SYS clients. It depends on user namespace id mapping from `clnt->cl_cred->user_ns` or `init_user_ns`, group info ordering, XDR stream helpers, and rpc task allocation context.

Risks: AUTH_UNIX is identity assertion rather than cryptographic authentication. Group comparison truncates to `UNX_NGROUPS`, matching wire format limits; callers with more groups can collide after truncation. `unx_validate()` mutates `au_verfsize`, `au_rslack`, and `au_ralign` on the shared auth object based on server verifier size, so concurrent clients using the singleton must tolerate this dynamic sizing. Allocation fallback depends on `rpc_init_authunix()` having created `unix_pool`.

Test signals: marshal users with no groups, exactly `UNX_NGROUPS`, and more than `UNX_NGROUPS`; verify namespace id mapping; validate NULL/UNIX/SHORT reply verifiers and reject oversized or malformed verifiers; stress async credential lookup under allocation pressure; and test RCU credential destruction under repeated client create/release.

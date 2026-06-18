# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-mem-types.h

Purpose: assigns memory accounting IDs for snapview-client allocations.

Important APIs/types: `enum svc_mem_types` starts at `gf_common_mt_end + 1` and defines `gf_svc_mt_svc_private_t`, `gf_svc_mt_svc_fd_t`, and `gf_svc_mt_end`.

Control flow/state: no control flow. The enum is consumed by `GF_CALLOC`, `mem_pool_new`, and `xlator_mem_acct_init` in the implementation.

Dependencies/integration: includes `glusterfs/mem-types.h` and must stay consistent with allocations in `snapview-client.c`.

Risks/test signals: adding allocated structures without adding accounting IDs reduces diagnostic precision. Tests should ensure `mem_acct_init()` succeeds and allocation tags remain below `gf_svc_mt_end`.

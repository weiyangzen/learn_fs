# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-mem-types.h

Purpose: defines memory accounting IDs for `open-behind`.

Important APIs, types, and functions: `enum gf_ob_mem_types_` assigns `gf_ob_mt_fd_t`, `gf_ob_mt_conf_t`, `gf_ob_mt_inode_t`, and `gf_ob_mt_end`.

Control flow: no runtime control flow; IDs are passed to allocation helpers and `xlator_mem_acct_init`.

State and persistence: no state beyond memory-accounting categories.

Dependencies and integration: includes `<glusterfs/mem-types.h>` and is included by `open-behind.c`.

Risks and test signals: `gf_ob_mt_fd_t` appears reserved but not used in this implementation; adding allocations should use or extend this enum before `gf_ob_mt_end`. Successful mem-account initialization validates the header.

# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-mem-types.h

## Purpose
This header assigns memory-accounting IDs for allocations made by the SELinux translator.

## Important APIs and state
`enum gf_selinux_mem_types_` starts at `gf_common_mt_end + 1` and currently defines `gf_selinux_mt_selinux_priv_t` followed by `gf_selinux_mt_end`. `selinux.c` uses this ID when allocating `selinux_priv_t` and passes `gf_selinux_mt_end` to `xlator_mem_acct_init()`.

## Dependencies and integration
The header depends on `glusterfs/mem-types.h` for the common allocation namespace. It integrates with GlusterFS memory accounting through `mem_acct_init()`.

## Risks and test signals
The enum must remain append-only relative to memory-accounting expectations. Adding new SELinux-private allocations should add IDs before `gf_selinux_mt_end` and use them in allocation calls. Tests should include translator initialization with memory accounting enabled and fault injection for `GF_CALLOC`.

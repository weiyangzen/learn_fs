# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mem-types.h

Purpose: Declares daemon-specific memory accounting type IDs used with GlusterFS allocation wrappers.

Important types: `GF_MEM_TYPE_START` begins after `gf_common_mt_end`. `enum gfd_mem_types_` assigns IDs for daemon xlator list entries, xlators, server command-line structures, xlator command-line options, daemon-owned chars, call pools, and `gfd_mt_end`.

Control flow: There is no executable control flow. The enum values are consumed by allocation calls such as `GF_CALLOC(..., gfd_mt_xlator_t)` and by `xlator_mem_acct_init(THIS, gfd_mt_end)` in daemon startup.

State and persistence: No runtime state by itself. Its IDs affect memory accounting counters and diagnostics during a process lifetime.

Dependencies and integration: Depends on `<glusterfs/mem-types.h>`. Integrated by `glusterfsd.c` and any daemon source that uses daemon-specific allocation tags.

Risks: IDs must remain contiguous and after common memory types. Adding an enum after `gfd_mt_end` or failing to update callers can corrupt accounting categories. Renaming values is less risky than reordering if external reports are interpreted by name.

Test signals: Memory-accounting initialization and statedump/mempool reports should show daemon allocation classes. Compile failures catch missing enum names; runtime leak attribution depends on accounting tests or diagnostics.

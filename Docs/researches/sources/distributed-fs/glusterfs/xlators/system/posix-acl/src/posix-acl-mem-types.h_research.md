# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-mem-types.h

Purpose: memory-accounting type declarations for the POSIX ACL translator.

Important APIs, types, and functions: `gf_posix_acl_mem_types_t` starts after `gf_common_mt_end` and defines accounting IDs for ACL inode contexts, ACL/ACE allocation, temporary character buffers, translator configuration, and the end marker.

Control flow: `posix-acl.c` passes `gf_posix_acl_mt_end` to `xlator_mem_acct_init()` and uses individual enum values in `GF_CALLOC` calls for contexts, ACL entries, strings, and configuration.

State and persistence: no persistent state. The enum labels runtime heap allocations for Gluster's memory accounting subsystem.

Dependencies and integration points: includes `glusterfs/mem-types.h` and must remain synchronized with all allocation sites in the translator.

Risks and test signals: adding allocations without new or appropriate memory types reduces diagnostic accuracy. Test signals are translator startup with memory accounting enabled and leak/accounting reports that categorize POSIX ACL allocations correctly.

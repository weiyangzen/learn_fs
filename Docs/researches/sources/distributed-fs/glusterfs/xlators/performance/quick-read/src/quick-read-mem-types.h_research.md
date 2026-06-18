# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-mem-types.h

Purpose: defines memory accounting IDs for `quick-read`.

Important APIs, types, and functions: `enum gf_qr_mem_types_` assigns IDs for `qr_inode`, cached content, priority rules, private config/table, and `gf_qr_mt_end`.

Control flow: no runtime control flow; allocation and memory-account initialization consume the IDs.

State and persistence: no state except category definitions for Gluster memory accounting.

Dependencies and integration: includes `<glusterfs/mem-types.h>` and is included by `quick-read.h`.

Risks and test signals: new allocation classes must be appended before `gf_qr_mt_end`. Validation is successful `qr_mem_acct_init` and useful memory stats during quick-read cache activity.

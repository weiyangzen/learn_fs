# sources/distributed-fs/ceph-client/fs/jffs2/debug.c

## Purpose
`debug.c` implements JFFS2 sanity checks, deeper paranoia checks, and diagnostic dump routines used by the debug macros in `debug.h`. Its checks validate eraseblock accounting, superblock-wide accounting, fragment tree invariants, pre-write erased-state expectations, node-ref chains, block lists, buffers, and raw on-flash nodes.

## Important APIs, Types, And Functions
Sanity functions are `__jffs2_dbg_acct_sanity_check_nolock()` and `__jffs2_dbg_acct_sanity_check()`. Paranoia functions include `__jffs2_dbg_fragtree_paranoia_check[_nolock]()`, `__jffs2_dbg_prewrite_paranoia_check()`, and `__jffs2_dbg_acct_paranoia_check[_nolock]()`. Dump functions include `__jffs2_dbg_dump_node_refs[_nolock]()`, `__jffs2_dbg_dump_jeb[_nolock]()`, `__jffs2_dbg_dump_block_lists[_nolock]()`, `__jffs2_dbg_dump_fragtree[_nolock]()`, `__jffs2_dbg_dump_buffer()`, and `__jffs2_dbg_dump_node()`.

## Control Flow
Sanity checks compare per-block size buckets against sector size and global buckets against flash size. Paranoia checks recalculate counts by walking list membership and node refs, dumping details and BUGing on mismatch. Dump routines print structured information about eraseblock lists, fragment trees, node references, and decoded inode/dirent nodes after CRC checks.

## State And Persistence Behavior
The file does not mutate persistent state except reading flash for verification/dumps. It observes live in-core state under `erase_completion_lock` or `f->sem` where needed and may terminate the kernel via `BUG()` when debug assertions fail.

## Dependencies And Integration Points
It depends on MTD reads, CRC32, JFFS2 endian helpers and structures from `nodelist.h`, and compile-time flags from `debug.h`. Calls are embedded throughout allocation, node-list, write, erase, and GC code as validation hooks.

## Risks And Test Signals
Debug code can be expensive and fatal by design, so false positives or lock misuse can destabilize debug kernels. Tests should run JFFS2 with `CONFIG_JFFS2_FS_DEBUG` levels enabled under write, truncate, unlink, GC, and bad-block simulations, and verify dumps do not dereference invalid refs while reporting corrupted images.

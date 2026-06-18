<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_object.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_object.c

## Purpose
`vvp_object.c` implements VVP `cl_object` and `lu_object` behavior for regular-file inodes. It exposes inode attributes to lower cl layers, reacts to layout invalidation, prunes page cache, provides glimpse data, fills request attributes, and allocates/frees VVP objects.

## Important APIs, Types, And Functions
Important functions include `vvp_object_invariant()`, `vvp_attr_get()`, `vvp_attr_update()`, `vvp_conf_set()`, `vvp_prune()`, `vvp_object_glimpse()`, `vvp_req_attr_set()`, `vvp_req_projid_set()`, `cl_inode2vvp()`, and `vvp_object_alloc()`. Operation tables are `vvp_ops` and `vvp_lu_obj_ops`.

## Control Flow
Object allocation creates a `vvp_object`, initializes a cl object header, installs operation tables, and adds it as the top lu object. Object init allocates the lower object from `vdv_next`, links it into the stack, stores the inode, and initializes cl page slices. Attribute get/update translate between inode fields and `cl_attr`. Config invalidation clears layout generation, invalidates PCC layout state, and unmaps VM mappings. Prune syncs local dirty data then truncates final pages. Freeing is RCU-delayed after lu object/header finalization.

## State And Persistence
`vvp_object` persists with `vob_inode`, `vob_mmap_cnt`, and `vob_discard_page_warned`. It reflects inode uid/gid/time/project-id/block/size state and updates inode version on KMS changes. Request attribute filling stores parent FID, project ID, and job info for downstream OST RPC scheduling and accounting.

## Dependencies And Integration Points
The file integrates with llite inode info, cl object/page/io operations, lower lov/osc devices, PCC layout invalidation, Linux inode version/time helpers, dirty page accounting, and lfsck failpoint support for parent FID mutation.

## Risks And Edge Cases
Only regular files or zero-mode objects satisfy the invariant. Layout invalidation must unmap mmaps because userspace can otherwise read stale installed pages. Prune failures leave dirty data and must be surfaced. Attribute updates cross user-namespace uid/gid conversion boundaries.

## Test Signals
Test object allocation/free under RCU, attr get/update for uid/gid/times/project ID, layout invalidation with active mmap, page-cache prune after writeback failures, glimpse block reporting for dirty sparse files, and request attribute contents on read/write RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_object.c -->

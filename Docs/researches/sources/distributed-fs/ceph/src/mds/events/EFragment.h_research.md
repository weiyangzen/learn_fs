# sources/distributed-fs/ceph/src/mds/events/EFragment.h

Purpose: Declares journal records for directory fragmentation split/merge prepare, commit, rollback, and finish phases.

Important APIs/types: `dirfrag_rollback` stores prior fnode state. `EFragment` stores `metablob`, operation code, inode, base fragment, split/merge bits, original fragments, and rollback buffer. `add_orig_frag` records original frags and optional rollback data.

Control flow: Fragment operations journal phase-specific events; replay uses op code and rollback payload to complete or undo split/merge changes. Positive `bits` means split from basefrag, negative means merge to basefrag.

State and persistence behavior: The event persists metadata changes in `EMetaBlob`, original fragment layout in `orig_frags`, and optional rollback data in a bufferlist.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `CDir::fnode`, `frag_t`, `frag_vec_t`, and MDS dirfrag management.

Risks: Rollback correctness depends on ordering between orig frags and encoded rollback records. Wrong bit sign or basefrag can orphan dirfrags.

Test signals: Split/merge prepare/commit/rollback replay, orphan fragment finish, and dencoder coverage for rollback records.

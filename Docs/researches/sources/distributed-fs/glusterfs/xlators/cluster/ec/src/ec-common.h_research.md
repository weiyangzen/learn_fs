# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.h

Purpose: central declaration header for EC common state-machine, dispatch, lock, inode-size, heal, and quorum helpers.

Important APIs/types/macros: defines transaction indexes `EC_DATA_TXN`/`EC_METADATA_TXN`, internal heal fop ids, config constants, lock flag `EC_FLAG_LOCK_SHARED`, quorum wrapper `QUORUM_CBK`, xattrop flag packing macros, state constants (`EC_STATE_INIT`, `LOCK`, `DISPATCH`, `PREPARE_ANSWER`, `REPORT`, `LOCK_REUSE`, `UNLOCK`, heal states), update/query flags, and `EC_RANGE_FULL`. Prototypes expose dispatch variants, completion, error handling, answer preparation, lock preparation/release, inode size cache access, manager/resume/sleep functions, heal info, fd status updates, and message formatting.

Control flow and integration: all concrete fop files include this header to build managers that move through the shared states. `QUORUM_CBK` enforces user-visible quorum by converting an otherwise successful callback to `EIO` when successful child count is below `ec->quorum_count` for normal client traffic.

State behavior: the macros encode the contract between fop managers and `ec-common.c`: flags indicate data/meta dirtying, minimum dispatch requirements, and whether parent errors propagate. The header itself stores no state. Risks include state-number collisions, incorrect bit packing if more than 16 xattrop flags are added, misusing `EC_FOP_MINIMUM()` with non-minimum flag bits, and forgetting to use `QUORUM_CBK` for mutating fops. Test signals should include compile coverage for every manager state, quorum-count behavior under insufficient good masks, and flag packing/unpacking tests around `EC_FLAG_MAX`.

# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.h

## Purpose
`afr.h` is the primary internal header for the AFR replicate translator. It defines the global private state, per-call local state, inode and fd contexts, transaction types, lock state, reply storage, read/self-heal policy enums, thin-arbiter state enums, stack cleanup macros, utility macros, and cross-file prototypes used by AFR read, write, lock, self-heal, open, lookup, and translator lifecycle code.

## Important APIs, Types, And Functions
Key enums include `afr_read_hash_mode_t`, `afr_favorite_child_policy`, `afr_data_self_heal_type_t`, `afr_child_index`, `afr_ta_fop_state_t`, `afr_transaction_type`, `afr_fd_open_status_t`, and `afr_fop_lock_state_t`. Core structures are `afr_private_t`, `afr_local_t`, `afr_inode_ctx_t`, `afr_lock_t`, `afr_internal_lock_t`, `afr_lockee_t`, `afr_reply`, `afr_fd_ctx_t`, `afr_lk_heal_info_t`, and small split-brain/read helper argument structs.

Important macros include `AFR_COUNT`, `AFR_INTERSECT`, `AFR_CMP`, `AFR_IS_ARBITER_BRICK`, `AFR_SET_ERROR_AND_CHECK_SPLIT_BRAIN`, `AFR_ERROR_OUT_IF_FDCTX_INVALID`, `AFR_STACK_UNWIND`, `AFR_STACK_DESTROY`, `AFR_FRAME_INIT`, `AFR_STACK_RESET`, `AFR_BASENAME`, `AFR_QUORUM_AUTO`, and changelog constants such as `AFR_NUM_CHANGE_LOGS`, `AFR_DIRTY`, `AFR_TA_DOM_NOTIFY`, and `AFR_TA_DOM_MODIFY`. Inline helpers map transaction or inode type to changelog index with `afr_index_for_transaction_type()` and `afr_index_from_ia_type()`.

## Control Flow
Most AFR FOPs allocate an `afr_local_t` through `AFR_FRAME_INIT`, populate the `cont` union fields and transaction callbacks, call read/transaction/self-heal helpers, then unwind with `AFR_STACK_UNWIND` or destroy private frames with `AFR_STACK_DESTROY`. Lock paths fill `afr_internal_lock_t` and `afr_lockee_t`; transaction paths mutate the nested `transaction` member; read paths use `readable`, `read_attempted`, `read_subvol`, and `readfn`; reply interpretation uses `replies` and `afr_reply` arrays.

The private translator state (`afr_private_t`) is initialized in `afr.c`, updated by notifications/reconfigure, consulted by transaction/read/self-heal paths, and cleaned up at translator shutdown. Inode and fd contexts cache state across individual FOP frames, while `afr_local_t` represents one outstanding operation or transaction frame.

## State And Persistence
`afr_private_t` stores long-lived translator state: child count and pointers, child-up/HALO-up/local/anonymous-inode arrays, latency, pending xattr keys, self-heal queues and limits, thin-arbiter identity and queues, quorum/read/eager-lock/durability/metadata consistency options, event generation, volume UUID, SHD state, saved lock-heal queues, and anonymous-inode names. `afr_inode_ctx_t` persists per-inode read/write subvolume choices, split-brain choice, pre-op inheritance counters, eager-lock lists and timers, open fd count, refresh need, and unstable-write witness state. `afr_fd_ctx_t` persists per-fd open status by child, flags, readdir subvolume, and lock-heal information.

`afr_local_t` is per-frame but large: it stores operation identity, event-generation snapshot, child-up snapshot, readable arrays, xattr request/response dicts, pending changelog matrix, dirty counters, replies, continuation arguments for nearly every FOP, transaction fields, thin-arbiter fields, barriers, and lock-owner snapshots. Persistent on-disk representation is not defined here directly, but the constants and structures describe the trusted AFR xattr format `[data, metadata, entry]`.

## Dependencies And Integration Points
The header depends on GlusterFS core types and APIs (`call_frame_t`, `xlator_t`, `inode_t`, `fd_t`, `loc_t`, dicts, locks, timers, syncop, iatt, flock, list heads, mempools) and AFR sibling headers (`afr-mem-types.h`, `afr-self-heald.h`, `afr-messages.h`). Its prototypes connect all AFR implementation files: read subvolume selection, inode refresh, locking, fd cleanup, reply interpretation, matrix allocation, self-heal, split-brain handling, quorum, consistent IO, thin arbiter, domain locks, and private directory handling.

## Risks
This header is a dense shared contract. Layout changes in `afr_local_t`, `afr_private_t`, or inode/fd contexts can affect many asynchronous callbacks and cleanup paths. The stack macros combine unwind/destroy with local cleanup, read-counter decrement, and domain-lock release; misuse can leak locals or double-free frames. Many arrays are sized by `priv->child_count`, but thin-arbiter mode has special indexing at `THIN_ARBITER_BRICK_INDEX`; callers must not blindly iterate into thin-arbiter-only slots. The `cont` union-style struct relies on each FOP reading only its populated fields.

## Test Signals
Any change requires full AFR build coverage and broad runtime tests for read, write, metadata, entry, lock, self-heal, thin-arbiter, arbiter, split-brain, and SHD paths. Memory diagnostics should watch frame cleanup, dict refs, reply wiping, inode/fd context lifetime, and list membership assertions. ABI-like signals include every AFR source compiling without duplicate/missing prototypes and no operation table regression from signature drift.

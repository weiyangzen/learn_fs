# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.h

## Purpose
`glusterd-store.h` defines the durable-store schema constants and public API for glusterd metadata persistence and restore.

## Important APIs, Types, and Functions
It defines `glusterd_volinfo_ver_ac_t` for no-change, increment, and decrement actions on volume versions. It defines store directory and file names such as `vols`, `peers`, `snapd.info`, `info`, `bricks`, `node_state.info`, and `missed_snaps_list`. It also defines the key strings used in volume, brick, snapshot, peer, rebalance, migration, quota, and ganesha store files.

The important type is `glusterd_volinfo_data_store_t`, which carries a `gf_store_handle_t`, current buffer length, key-validation flag, and a fixed serialization buffer for dictionary writes.

The header exports the write and restore APIs implemented in `glusterd-store.c`: volume, snap, peer, brick, global info, options, quota, and missed-snap persistence helpers; `glusterd_restore()`; and utility functions such as `glusterd_replace_slash_with_hyphen()`.

## Control Flow
The header itself has no control flow, but it defines the public surface used by operation-state-machine and utility code to persist metadata after cluster operations and restore metadata during daemon startup.

## State and Persistence Behavior
The constants in this header are the stable on-disk contract. Changing any key or file-name constant can break restore of existing clusters unless migration logic is added.

## Dependencies and Integration Points
It includes `compat-uuid.h`, `logging.h`, and `glusterd.h`, so it exposes store APIs in terms of glusterd core types. It is included by management operations, volume operations, snapshot code, quota code, and startup restore code.

## Risks and Edge Cases
The header mixes public function declarations with a large schema catalog. This makes key reuse convenient but also makes accidental schema changes easy to propagate. The buffer size constant `VOLINFO_BUFFER_SIZE` bounds batched option serialization; callers adding large option values need to account for flush behavior and key/value formatting length.

## Test Signals
Schema tests should verify that every public store key has a writer and reader where appropriate. ABI/build tests should include callers across volume, peer, snapshot, and quota modules.

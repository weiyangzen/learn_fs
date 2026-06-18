# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.h

## Purpose

`data-vio.h` defines the central data-path request object for VDO and declares the APIs used to launch, route, read, write, compress, allocate, update metadata for, and complete user data VIOs. It also provides thread-affinity helper wrappers for moving a `data_vio` between logical, physical, hash, journal, packer, CPU, bio, and acknowledgement queues.

## Important APIs, Types, And Functions

- `enum async_operation_number`: debug/error labels for the last asynchronous stage.
- Lock/location types: `struct lbn_lock`, `struct block_map_tree_slot`, `struct tree_lock`, and `struct zoned_pbn`.
- Compression types: `enum data_vio_compression_stage`, `struct data_vio_compression_status`, and `struct compression_state`.
- Allocation and reference update types: `struct allocation` and `struct reference_updater`.
- `struct data_vio`: embeds `struct vio`, waiters, logical/tree locks, mapped/new/duplicate locations, hash/dedupe state, reference updaters, flags, recovery state, page completion, user bio, discard progress, compression buffers, and pool linkage.
- Pool and lifecycle API: `make_data_vio_pool`, `free_data_vio_pool`, `vdo_launch_bio`, `drain_data_vio_pool`, `resume_data_vio_pool`, `dump_data_vio_pool`, pool stats getters, `complete_data_vio`, and `handle_data_vio_error`.
- Data-path API: compression status helpers, `data_vio_allocate_data_block`, `release_data_vio_allocation_lock`, `uncompress_data_vio`, `update_metadata_for_data_vio_write`, `write_data_vio`, `launch_compress_data_vio`, and `continue_data_vio_with_block_map_slot`.

## Control Flow

The header's inline helpers encode the expected state machine transfers. `continue_data_vio` relaunches the embedded completion. `continue_data_vio_with_error` records a result and relaunches. The `set_data_vio_*_callback` and `launch_data_vio_*_callback` families bind the completion to the relevant zone/thread and then launch it, optionally with a priority.

The public functions declared here are implemented in `data-vio.c` and by peer modules such as hash-zone, packer, physical-zone, and block-map code. Callers should use the thread-specific helpers rather than setting completion thread IDs manually.

## State And Persistence Behavior

`struct data_vio` is the transient carrier for persistent metadata changes. It stores old and new mappings, journal operation descriptors, recovery journal sequence/point, allocation PBN/lock, and page-completion state. Some fields are reset on reuse while fields after the embedded `vio` allocation boundary keep allocated buffers and completions across pool reuse.

The flags (`read`, `write`, `fua`, `is_zero`, `is_discard`, `is_partial`, `is_duplicate`, etc.) drive ordering, acknowledgement, and metadata updates. `recovery_sequence_number` must be cleared only after its journal lock is transferred or released.

## Dependencies And Integration Points

The header includes Linux bio/list/atomic support and VDO modules for block map, completion, constants, dedupe, encodings, logical/physical zones, indexer, VIOs, wait queues, and core VDO types. It is included by modules that need to inspect or continue data-path state, including block-map allocation, hash/dedupe, packer/compression, physical-zone allocation/reference updates, and dump/debug code.

## Risks And Edge Cases

- Many inline assert helpers dereference zone pointers; the corresponding `zoned_pbn` or lock state must be initialized before use.
- `data_vio_has_allocation` treats `VDO_ZERO_BLOCK` as no allocation, matching zero-block reservation.
- The reset boundary in `data-vio.c` depends on `offsetof(struct data_vio, vio)` and `offsetof(struct compression_state, block)`; moving fields across those boundaries changes reuse semantics.
- Completion container casts depend on `vio.type == VIO_TYPE_DATA` and completion type correctness.
- Thread helper misuse can run physical-zone, hash-zone, or journal operations on the wrong queue.

## Test Signals

Compile coverage should catch signature mismatches with peer modules. Runtime tests should validate thread assertions for each launch helper, data_vio reuse/reset behavior, allocation presence handling, compression stage transitions, reference-updater container conversion, and correctness of public continuation points used by block-map, hash, packer, and physical-zone code.

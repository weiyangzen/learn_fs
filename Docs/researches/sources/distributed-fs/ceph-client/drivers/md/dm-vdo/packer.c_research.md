# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.c

## Purpose
`packer.c` batches multiple compressed data VIO fragments into one compressed physical block. It improves space efficiency by only writing compressed form when at least two fragments fit into a block, manages packer bins, writes compressed blocks, shares resulting PBN locks, handles cancellation/rendezvous, and supports flush/drain/resume.

## Important APIs, Types, and Functions
Public APIs include `vdo_get_compressed_block_fragment()`, `vdo_make_packer()`, `vdo_free_packer()`, `vdo_get_packer_statistics()`, `vdo_attempt_packing()`, `vdo_flush_packer()`, `vdo_remove_lock_holder_from_packer()`, `vdo_increment_packer_flush_generation()`, `vdo_drain_packer()`, `vdo_resume_packer()`, and `vdo_dump_packer()`. Key internals include sorted bin insertion, bin allocation, `abort_packing()`, compressed-write completion/error handlers, `remove_from_bin()`, `initialize_compressed_block()`, `pack_fragment()`, `write_bin()`, `select_bin()`, and drain checks.

## Control Flow
Incoming compressed VIOs arrive on the packer thread in `DATA_VIO_COMPRESSING`. The packer increments in-packer stats, rejects VIOs during drain/flush-generation mismatch, selects the first best-fit bin, advances compression state, and enqueues the VIO. Full or overflowed bins are written: the first uncanceled VIO becomes the agent, its scratch block becomes the compressed block, other fragments are copied into slots, and single-fragment batches are aborted to normal write. Successful compressed writes release all client VIOs with a shared compressed write lock and mapping state. Errors reset clients back to normal write. Flush writes all non-empty bins; drain prevents new entries and completes after bins and canceled rendezvous state clear.

## State and Persistence Behavior
Persistent output is the compressed block format: a packed version number and little-endian fragment sizes followed by fragment data. Runtime state includes sorted bins, a canceled bin, admin state, flush generation, and statistics. Packer state is volatile but controls durable mapping state for compressed fragments.

## Dependencies and Integration Points
The packer integrates with admin-state, completions, data VIO compression stages, physical-zone allocation/PBN locks, VIO bio setup, I/O submitter, VDO read-only state, encodings/version packing, constants, statistics, and logging/allocation/assertion helpers.

## Risks and Edge Cases
Correctness depends on packer-thread confinement and compression-stage transitions. Single compressed fragments must not be written because they save no space. Cancellation requires rendezvous through the canceled bin, and lock-holder removal must update slot indexes. Fragment size and version validation protect readers. Flush generation prevents older writes from remaining packed across flush boundaries. Error recovery must avoid leaking PBN locks or leaving waiters in bins.

## Test Signals
Test fragment extraction with valid/invalid versions, slot states, offsets, and oversized sizes; packing two or more fragments; single-fragment abort; bin sorting/overflow; cancellation and lock-holder removal; compressed write success/error; read-only handling; packer flush/drain/resume; stats counters; and flush-generation advancement.

# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-types.h

## Purpose
This header is the central type model for the EC/disperse translator. It defines translator-private configuration, inode/fd contexts, lock structures, per-FOP state, callback aggregation records, coding/matrix structures, self-heal state, and statistics.

## Important APIs, Types, And Functions
Key structs are `ec_config_t` for on-disk EC layout fields, `ec_fd_t` for fd state and per-child open status, `ec_inode_t` for cached config/version/size/dirty state plus stripe cache and read mask, `ec_lock_t` and `ec_lock_link_t` for eager/inode lock ownership and dirty/update tracking, `ec_fop_data_t` for a full operation state machine, `ec_cbk_data_t` for grouped child answers, `ec_matrix_list_t` for coding matrices, `ec_heal_t` and `ec_self_heald_t` for healing, and `ec_t` for translator-wide state. The `ec_cbk_t` union stores callback types for every supported FOP.

## Control Flow
No functions are implemented here, but the fields define control flow elsewhere. `ec_fop_data_t` carries state numbers, quorum minimum, masks (`mask`, `remaining`, `received`, `good`, `healing`), wind/handler/resume callbacks, locks, fd/loc/iovec/xdata payloads, and fragment ranges. `ec_lock_t` owners/waiting/frozen lists drive eager lock reuse. `ec_t` masks and counters drive up/down notification and quorum.

## State And Persistence Behavior
Most structs are in-memory. Persistent EC state is represented indirectly by xattrs decoded into `ec_inode_t` fields: config, versions, dirty flags, and size. The translator private `ec_t` persists for the lifetime of the xlator instance and owns pools, child lists, matrix cache, self-heal threads, and statistics. `ec_fd_t` and `ec_inode_t` are attached to GlusterFS fd/inode contexts.

## Dependencies And Integration Points
The header includes GlusterFS timer, syncop, atomic, and libxlator headers. It is included by nearly every EC source file and acts as the ABI between method coding, helpers, locks, FOP managers, heal logic, and xlator entry points.

## Risks
Because `ec_fop_data_t` is shared by many state machines, field reuse is easy to misread: generic fields such as `int32`, `uint32`, `size`, `offset`, and `str[]` carry operation-specific meanings. Flexible arrays in `ec_fd_t`, `ec_code_builder_t`, and `ec_matrix_t` require exact allocation sizes. Lock flags, dirty flags, and masks must be updated atomically or under the expected locks.

## Test Signals
The best signals are broad FOP suites under failure injection, memory-pool accounting, statedumps for private state, lock contention tests, and ABI-aware compile checks after any struct field or enum change. Sanitizer or valgrind runs are valuable around flexible-array allocations and callback data lifetimes.

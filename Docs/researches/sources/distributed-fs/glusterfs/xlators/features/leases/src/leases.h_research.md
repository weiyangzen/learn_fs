# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.h

## Purpose
Defines macros, private structs, lease state structs, and internal function declarations for the leases translator.

## Important APIs, Types, and Functions
- `EXIT_IF_LEASES_OFF`, `EXIT_IF_INTERNAL_FOP`, `GET_LEASE_ID`, `GET_FLAGS`, and `GET_FLAGS_LK` implement common fop wrapper policy.
- `LEASE_BLOCK_FOP` creates a call stub and records it in the inode lease ctx blocked list.
- `leases_private_t` stores client/recall lists, timer wheel, recall thread, locks, timeout, and enabled/fini flags.
- `lease_inode_ctx_t` stores all active lease entries, aggregate lease counts, blocked fops, timer state, and recall flags for one inode.
- `lease_id_entry_t`, `lease_client_t`, `lease_inode_t`, `lease_fd_ctx_t`, and `fop_stub_t` model client, inode, fd, and blocked operation state.
- Declares `is_leases_enabled()`, `lease_ctx_get()`, `process_lease_req()`, `check_lease_conflict()`, `cleanup_client_leases()`, and `expired_recall_cleanup()`.

## Control Flow
Fop wrappers in `leases.c` use the macros to decide whether to bypass, conflict-check, or block. Internal code in `leases-internal.c` fills and drains the structs declared here.

## State and Persistence
All declared state is memory-resident and scoped to translator, inode, client, fd, or timer lifetime. No persistent lease state is modeled.

## Dependencies and Integration Points
Includes GlusterFS call stubs, logging, locking, timer wheel, and leases-specific mem/message headers. Uses GlusterFS lease constants such as `LEASE_ID_SIZE` and `GF_LEASE_MAX_TYPE`.

## Risks and Edge Cases
`LEASE_BLOCK_FOP` has complex allocation and locking behavior embedded in a macro, so caller `ret`/`err` labels must be compatible. `GET_FLAGS_LK` appears to set `BLOCKING_FOP` when nonblocking flags are present for blocking lock commands, which deserves validation. Struct lock ownership and list membership are subtle and must match the documented lock order in the C file.

## Test Signals
Compile all fop wrappers that use `LEASE_BLOCK_FOP`, run conflict tests for flag classification, and use sanitizer or stress tests for blocked-list and timer lifecycle.

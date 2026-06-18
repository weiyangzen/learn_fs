# File Research: sources/block-storage/kvdo/vdo/index-session.h

Internal session state definitions for UDS index operations.

Key responsibilities:
- Defines cache-line-aligned `struct session_stats` counters for request outcomes and locations.
- Defines `enum index_suspend_status` for load/rebuild coordination: opening, ready, suspending, suspended, freeing.
- Defines `struct index_load_context` with mutex, condition variable, and status.
- Defines `struct uds_index_session`, holding state flags, current `uds_index`, callback queue, parameters, load context, request drain synchronization, request count, and stats.

Dependencies:
- Includes kernel atomics, config, CPU cache-line sizing, UDS threads, and public UDS types.

Notable risks:
- State is an integer bitfield whose valid combinations are enforced by `index-session.c`, not the type system.
- Stats are embedded and aligned, but individual fields are plain `uint64_t`.

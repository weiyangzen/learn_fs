## sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/trove-handle-mgmt.h

Purpose: Declares the public internal handle-management interface used by Trove storage implementations to configure legal handle ranges and allocate/recycle object handles.

Important APIs and definitions: `MAX_NUM_VERIFY_HANDLE_COUNT` bounds the batch size for scanning existing handles during range validation. `TROVE_DEFAULT_HANDLE_PURGATORY_SEC` is the default delayed-reuse timeout. The API includes initialization/finalization, `trove_set_handle_ranges`, `trove_set_handle_timeout`, allocation with or without caller-supplied extent constraints, non-consuming peek with or without extent constraints, `trove_handle_set_used`, `trove_handle_free`, and `trove_handle_get_statistics`.

Control flow: This header defines the contract rather than implementing behavior. Consumers call initialization from Trove startup, configure ranges through collection setinfo, allocate handles during dataspace creation, mark requested handles as used, return handles on dataspace removal failure/success paths as appropriate, and finalize during Trove shutdown.

State and persistence: State is opaque to callers and implemented in `trove-handle-mgmt.c` as a global hash of collection ledgers. No persistence is exposed by this interface. The comments warn that peeked handles must not be stored because later allocation calls can invalidate the preview.

Dependencies and integration points: Requires Trove/PVFS handle and collection types to be visible before inclusion. It is included by `trove-mgmt.c` and DBPF dataspace code, and depends on `struct timeval` for timeout configuration.

Risks: The header says most methods return `-1` on error, but implementation often returns encoded Trove/PVFS negatives. Range-peek ordering is only guaranteed relative to the current allocator state and can be invalidated by any later allocation. The interface exposes no way to persist or audit allocator state beyond statistics.

Test signals: API-level tests should verify documented return semantics, null argument handling, range string setup through setinfo, requested-handle reservation, and that peeked handles are returned by subsequent ordinary allocation when no intervening allocator changes occur.

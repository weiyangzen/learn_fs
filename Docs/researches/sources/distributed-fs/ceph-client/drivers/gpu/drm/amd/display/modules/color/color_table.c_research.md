# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/color/color_table.c

Purpose: Provides static storage and initialization-state tracking for color PQ and de-PQ transfer tables used by `color_gamma.c`.

Important APIs and functions: `mod_color_is_table_init`, `mod_color_get_table`, and `mod_color_set_table_init_state`. Static objects are `pq_table[MAX_HW_POINTS + 2]`, `de_pq_table[MAX_HW_POINTS + 2]`, `pq_initialized`, and `de_pg_initialized`.

Control flow: Callers ask whether a table is initialized, obtain a pointer for the requested `enum table_type`, populate it if needed, then set the init state. Unknown table types return false/NULL or do nothing.

State and persistence: The two static tables and booleans persist for the module lifetime. There is no locking, so initialization is assumed to be serialized by higher-level display color setup or safe under benign duplicate writes.

Dependencies and integration points: Includes `color_table.h`, which defines `MAX_HW_POINTS` and `table_type`. `color_gamma.c` uses this file to cache PQ/de-PQ computations and avoid repeated fixed-point math.

Risks: The `de_pg_initialized` variable name appears to misspell de-PQ but is internally consistent. No concurrency protection exists for first initialization. `mod_color_get_table` can return NULL for invalid types and callers must not dereference it.

Test signals: Repeated PQ/de-PQ precompute calls, invalid table type handling, table size boundary writes through `MAX_HW_POINTS`, and race analysis for concurrent color initialization.

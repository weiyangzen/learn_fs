<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ram.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ram.c

Purpose: Provides a fast in-memory regmap bus for testing regular register read/write behavior.

Important APIs/types/functions: `regmap_ram_write()` stores values and marks `written[reg]`; `regmap_ram_read()` loads values and marks `read[reg]`; `regmap_ram_free_context()` frees fixture buffers; `__regmap_init_ram()` exports map creation.

Control flow: Initialization requires `config->max_register`, allocates read/write tracking arrays sized to `max_register + 1`, and calls `__regmap_init()` with a fast `regmap_bus`. On init failure it frees tracking arrays. Runtime reads/writes directly index `data->vals`.

State and persistence behavior: State is entirely in `struct regmap_ram_data`: backing values and read/write tracking booleans. It persists for the lifetime of the regmap and is freed by the bus `free_context` callback.

Dependencies and integration points: Depends on internal regmap test structures and regmap core. It is used heavily by `regmap-kunit.c` to distinguish cache hits from hardware accesses.

Risks: It assumes callers provide a correctly sized `vals` array and valid register indices. It is intended for tests only and does no bounds checking in callbacks. Missing `max_register` is rejected with `-EINVAL`.

Test signals: Read/write side effects in `read[]` and `written[]`, cache-hit tests that expect no hardware read, and init failure paths for missing max register or allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ram.c -->

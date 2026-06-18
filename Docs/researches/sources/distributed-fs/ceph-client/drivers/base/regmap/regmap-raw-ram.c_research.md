<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-raw-ram.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-raw-ram.c

Purpose: Provides an in-memory raw regmap bus for testing byte-formatted register/value transfers, endian conversion, and no-increment behavior.

Important APIs/types/functions: `decode_reg()` decodes 16-bit register bytes according to configured endian. `regmap_raw_ram_gather_write()`, `regmap_raw_ram_write()`, and `regmap_raw_ram_read()` implement raw bus callbacks. `__regmap_init_raw_ram()` exports initialization.

Control flow: Initialization requires 16-bit register addresses and a nonzero max register, allocates read/write tracking arrays, stores register endian, and calls `__regmap_init()`. Writes validate two-byte register fields and even value lengths, decode the target register, then either copy all bytes into sequential `u16` storage or, for a no-increment register, store only the last value at the fixed register. Reads mirror that behavior, either copying sequential values or repeating the fixed register value through the destination buffer.

State and persistence behavior: Persistent fixture state is the caller-provided `vals` buffer plus allocated tracking arrays and optional `noinc_reg` predicate. The bus frees all of them at context teardown.

Dependencies and integration points: Depends on regmap core raw callbacks, endian helpers, and `struct regmap_ram_data`. It is paired with the KUnit raw tests.

Risks: Allocation failure for `written` after `read` leaks `read` in the current init path. Runtime callbacks assume register ranges fit the backing buffer. Pointer arithmetic on `void *` follows kernel C extensions. It is test-only and unsuitable as a checked production memory transport.

Test signals: Raw KUnit cases validate endian defaults, raw writes vs single reads, no-increment semantics, raw sync from cache-only state, and range window handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-raw-ram.c -->

# sources/distributed-fs/ceph-client/drivers/clk/clk-bulk.c


### Purpose
`clk-bulk.c` implements bulk clock acquisition and bulk prepare/enable/disable/put helpers. It lets device drivers handle arrays of `struct clk_bulk_data` with consistent forward setup and reverse-order unwind.

### Important APIs, Types, And Functions
Exported APIs include `clk_bulk_get()`, `clk_bulk_get_optional()`, `clk_bulk_get_all()`, `clk_bulk_put()`, `clk_bulk_put_all()`, `clk_bulk_prepare()`, `clk_bulk_unprepare()`, `clk_bulk_enable()`, and `clk_bulk_disable()`. OF internals `of_clk_bulk_get()` and `of_clk_bulk_get_all()` populate clock IDs from `clock-names` and retrieve indexed DT clocks.

### Control Flow, State, And Persistence
Bulk get initializes each array entry to a null clock, then obtains clocks left to right. If any required clock fails, it calls `clk_bulk_put()` on the successfully acquired prefix. Optional acquisition suppresses `-ENOENT` per entry and leaves the entry null. Prepare and enable also proceed left to right and unwind the already prepared or enabled prefix in reverse order on failure; disable/unprepare/put always walk backward. The only persistent state is held by the caller's `clk_bulk_data` array and references returned by CCF.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates with OF clock providers, `clk_get()` lookup by con_id, optional clock semantics, `CONFIG_HAVE_CLK_PREPARE`, and exported symbols consumed by drivers. Risks include callers using mismatched counts, expecting optional missing clocks to be real handles, or failing to follow disable-before-unprepare ordering. Test signals include injected failure at each index, optional `-ENOENT` handling, DT `clock-names` population, reverse unwind ordering, null-safe `clk_bulk_put_all()`, and successful bulk prepare-enable/disable-unprepare cycles.

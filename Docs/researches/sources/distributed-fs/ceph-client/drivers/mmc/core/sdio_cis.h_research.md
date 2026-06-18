# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.h

### Purpose
`sdio_cis.h` declares the internal SDIO CIS read/free helpers used by SDIO card setup and function release.

### Important APIs, Types, And Functions
It declares `sdio_read_common_cis()`, `sdio_free_common_cis()`, `sdio_read_func_cis()`, and `sdio_free_func_cis()` for `struct mmc_card` and `struct sdio_func`.

### Control Flow
There is no runtime logic. The read helpers are called during attach before function devices are registered; free helpers are called during card/function teardown.

### State, Persistence, And Dependencies
No state is stored. It forwards opaque MMC/SDIO types and leaves ownership rules to `sdio_cis.c`.

### Integration Points
`sdio.c` reads CIS data, and `sdio_bus.c` releases function CIS allocations. This header keeps tuple parsing private to the core while still exposing lifecycle operations.

### Risks
Callers must pair reads with frees along all error paths. Function CIS can reference the card tuple list, so freeing in the wrong order can corrupt shared tuple tails.

### Test Signals
Compile and attach/remove tests for SDIO function discovery validate correct use of the declarations.

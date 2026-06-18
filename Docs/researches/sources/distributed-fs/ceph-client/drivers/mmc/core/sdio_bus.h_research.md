# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.h

### Purpose
`sdio_bus.h` declares the internal SDIO bus and function-device lifecycle helpers.

### Important APIs, Types, And Functions
It forward declares `struct mmc_card` and `struct sdio_func`, then exposes `sdio_alloc_func()`, `sdio_add_func()`, `sdio_remove_func()`, `sdio_register_bus()`, and `sdio_unregister_bus()`.

### Control Flow
The header has no runtime logic. Callers allocate functions during card initialization, add them after card registration, remove them during teardown, and register/unregister the bus from MMC core init/exit paths.

### State, Persistence, And Dependencies
No state is stored. It is a narrow compile-time interface to `sdio_bus.c`.

### Integration Points
`sdio.c` uses the function lifecycle helpers; MMC core initialization uses bus registration. Keeping this contract small prevents function drivers from depending on private bus internals.

### Risks
Misordered use of these helpers can create device-model lifetime bugs, especially adding function devices before the parent card exists or removing without dropping function/card references.

### Test Signals
Compile coverage and SDIO attach/remove tests validate this header's declarations.

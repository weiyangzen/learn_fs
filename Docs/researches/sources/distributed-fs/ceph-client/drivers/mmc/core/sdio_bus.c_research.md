# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_bus.c

### Purpose
`sdio_bus.c` implements the Linux driver model bus for SDIO functions. It matches `struct sdio_driver` tables to `struct sdio_func` devices, manages probe/remove/shutdown, sysfs/modalias/uevents, function allocation, and function device add/remove.

### Important APIs, Types, And Functions
Public/internal APIs are `sdio_register_bus()`, `sdio_unregister_bus()`, `__sdio_register_driver()`, `sdio_unregister_driver()`, `sdio_alloc_func()`, `sdio_add_func()`, and `sdio_remove_func()`. Core helpers include `sdio_match_one()`, `sdio_match_device()`, `sdio_bus_match()`, `sdio_bus_uevent()`, `sdio_bus_probe()`, `sdio_bus_remove()`, `sdio_bus_shutdown()`, `sdio_release_func()`, `sdio_acpi_set_handle()`, and `sdio_set_of_node()`.

### Control Flow
Bus registration installs a `bus_type` named `sdio`. When a function device is added, matching compares class/vendor/device against the driver's ID table and emits SDIO uevent variables plus modalias. Probe attaches PM domain, increments the card's probed-function count, powers the function when power-off-card is supported, claims the host, sets a default block size, releases the host, and calls the function driver's `probe()`. Remove powers the function, calls driver `remove()`, decrements the probed count, warns and releases leaked IRQ handlers, and drops runtime PM references. Function allocation initializes a device, takes a reference on the parent card because tuples can point there, allocates an aligned tmp buffer, and defers freeing to `sdio_release_func()`.

### State, Persistence, And Dependencies
State is in the device model, `func->dev`, `func->tmpbuf`, `func->info`, `func->tuples`, `func->card`, `func->irq_handler`, `func->present`, OF/ACPI companion data, and `card->sdio_funcs_probed`. Dependencies include device core, PM runtime/domains, ACPI, OF, MMC card/host types, SDIO CIS freeing, and SDIO I/O helpers for block-size setup.

### Integration Points
`sdio.c` allocates and registers function devices through this file. SDIO function drivers register with `sdio_register_driver()` wrappers, bind through this bus, and use modalias `sdio:cXXvXXXXdXXXX` for module autoloading. OF child matching uses function number; ACPI address combines host slot number and function number.

### Risks
Runtime PM usage-count balancing is delicate across probe failure, remove, and card power-off. A driver that forgets `sdio_release_irq()` is repaired with a warning, but IRQ release occurs during remove and can still expose ordering issues. Tuple lifetime depends on the card reference taken during function allocation. `sdio_add_func()` can fail after OF/ACPI association; cleanup must call `sdio_remove_func()`.

### Test Signals
Test driver autoload modaliases, sysfs attributes, OF/ACPI enumeration, probe failure at block-size setup and driver probe, remove with leaked IRQ handler, runtime PM-enabled and disabled hosts, multi-function probed count changes, and function add/remove error paths.

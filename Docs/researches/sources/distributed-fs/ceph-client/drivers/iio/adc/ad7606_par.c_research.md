# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_par.c

Purpose: platform/parallel-bus wrapper for the AD7606 family. It handles memory-mapped 8-bit or 16-bit sample reads and a newer IIO-backend-backed parallel path, then delegates all common ADC behavior to `ad7606_probe()`.

Important APIs, types, and functions: `ad7606_par_probe()` chooses chip info from firmware match data or platform IDs, selects backend bus ops when `io-backends` is present, maps the I/O resource for traditional parallel mode, and calls the core. `ad7606_par16_read_block()` and `ad7606_par8_read_block()` use `insw()`/`insb()` to read channel blocks. `ad7606_par_bus_setup_iio_backend()`, `ad7606_par_bus_update_scan_mode()`, `ad7606_par_bus_reg_read()`, and `ad7606_par_bus_reg_write()` implement backend bus ops.

Control flow: firmware-backed probe with `io-backends` bypasses IRQ/resource mapping and enters core probe with backend bus ops. Otherwise probe requires an IRQ and memory resource, maps it, then chooses 16-bit or 8-bit read ops based on resource size. Traditional reads optionally consume the first word/bytes, validate `adi,first-data` GPIO alignment, reset on mismatch, and read the remaining samples. Backend setup obtains and enables an IIO backend, requests a buffer, enforces PWM presence, sets sign-extension data format on every channel, and uses backend channel enable/disable in scan-mode updates.

State and persistence behavior: no independent persistent state beyond the memory base passed into `struct ad7606_state` and backend pointer stored by the core state. A first-data alignment failure resets the ADC but does not persist error state.

Dependencies and integration points: depends on platform devices, OF matching, memory-mapped I/O, GPIO for first-data validation through common state, IIO backend, `ad7606.h`, and `ad7606_bus_iface.h`. Imports `IIO_AD7606` and `IIO_BACKEND` namespaces.

Risks: backend register callbacks depend on valid `dev->platform_data`. Resource-size based 8-bit versus 16-bit selection is simple and may misclassify unusual mappings. First-data validation reads one sample before checking alignment, so error recovery discards that block. Backend mode requires PWM because conversion timing is not GPIO-driven.

Test signals: probe 8-bit and 16-bit memory resources; verify `frstdata` reset behavior; test backend `io-backends` path with channel scan masks; test missing IRQ/resource failures; test all compatible IDs against exported chip descriptors.

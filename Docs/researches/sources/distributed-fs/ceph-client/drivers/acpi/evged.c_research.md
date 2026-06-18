# sources/distributed-fs/ceph-client/drivers/acpi/evged.c

Purpose: `evged.c` implements the ACPI Generic Event Device driver for `ACPI0013`. GED lets firmware describe interrupt resources in `_CRS` and handle them in AML methods such as `_EVT`, `_Exx`, or `_Lxx`.

Important APIs, types, and functions: key structures are `struct acpi_ged_device` and `struct acpi_ged_event`. Core functions are `acpi_ged_request_interrupt()`, `acpi_ged_irq_handler()`, `ged_probe()`, `ged_shutdown()`, and `ged_remove()`. The driver is registered as a built-in platform driver.

Control flow: probe allocates a GED device container, initializes an event list, and walks `_CRS`. Each IRQ resource is translated to a Linux IRQ using ACPI resource helpers, then the driver chooses a handler method: for GSI 0-255 it first looks for `_E##` or `_L##` based on trigger mode, otherwise it falls back to `_EVT`. It allocates an event object, requests a threaded IRQ, and stores it in the list. The IRQ thread executes the selected AML method, passing the GSI as the argument. Shutdown/remove frees all registered IRQs and clears the list.

State and persistence: state is devm-managed per platform device plus a list of event records containing GSI, IRQ, ACPI handle, and device pointer. There is no persistent storage.

Dependencies and integration: GED depends on ACPI `_CRS` interrupt parsing, Linux IRQ request/free APIs, platform-driver matching, and AML method execution. It bridges platform interrupts into firmware-owned ASL event handlers.

Risks: if firmware advertises an interrupt without a matching method, probe fails for that resource walk. Requesting threaded IRQs with AML execution means handler latency and AML failures matter; failures are logged once. Shutdown must free IRQs before firmware or platform teardown to avoid callbacks into removed state.

Test signals: validate `_EVT`, `_Exx`, and `_Lxx` method selection, shared interrupt flags, IRQ resource parse failures, threaded IRQ execution, shutdown cleanup, and probe behavior with multiple interrupt descriptors.

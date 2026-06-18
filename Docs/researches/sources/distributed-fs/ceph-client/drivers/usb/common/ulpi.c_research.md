# Research: sources/distributed-fs/ceph-client/drivers/usb/common/ulpi.c

Purpose: implements the ULPI PHY bus. USB controller drivers register a ULPI interface with register read/write operations; this code creates a `ulpi` device, reads vendor/product IDs, matches and probes ULPI PHY drivers, emits modaliases for module autoloading, and exposes debugfs register dumps.

Important APIs and types: exported `ulpi_read` and `ulpi_write` call controller-provided ops. `__ulpi_register_driver` and `ulpi_unregister_driver` manage ULPI PHY drivers. `ulpi_register_interface` allocates and registers a `struct ulpi`; `ulpi_unregister_interface` removes debugfs and unregisters the device. The static `ulpi_bus` provides match, uevent, probe, and remove callbacks.

Control flow: registration sets parent, bus, device type, name, and ACPI companion, optionally attaches an OF child named `ulpi`, probes scratch-register access, reads vendor/product registers, requests a matching module by ULPI modalias or OF modalias, then registers the device and creates `debugfs/ulpi/<dev>/regs`. Driver matching prefers OF when no vendor ID or no ID table exists, otherwise matches vendor/product pairs.

State and persistence: runtime state is in `struct ulpi`, its parent ops pointer, device ID fields, optional OF node reference, and the debugfs root. No persistent state. Device release drops the OF node and frees the ULPI object.

Dependencies and integration points: uses Linux device/bus core, module autoloading, OF and ACPI matching, clock defaults via `of_clk_set_defaults`, debugfs, seq_file, and ULPI register definitions. USB controller drivers are producers of ULPI interfaces; PHY drivers are consumers on the ULPI bus.

Risks: controller ops must be valid for all register reads used by debugfs; failed reads abort the register dump. `ulpi_read_id` returns success even when scratch or ID probing fails, relying on OF module request, so probe failures can be deferred to driver matching. `ulpi_register_interface` leaks no registered device on failure, but error paths around device registration and OF references are sensitive. Debugfs register reads can touch live PHY hardware.

Test signals: register a fake or controller-backed ULPI interface, verify modalias content, OF child matching, module autoload request, driver probe/remove, debugfs `regs` output, scratch mismatch fallback, and unregister cleanup under module unload.

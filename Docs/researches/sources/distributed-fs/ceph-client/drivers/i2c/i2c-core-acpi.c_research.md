# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-acpi.c

## Purpose

`i2c-core-acpi.c` is the Linux I2C core's ACPI integration layer. It parses ACPI `I2cSerialBus` resources, enumerates I2C clients behind adapters, resolves IRQs and bus speeds, handles ACPI hotplug/reconfiguration, creates clients for indexed resources, and optionally services ACPI GenericSerialBus operation regions.

## Important APIs, Types, and Functions

Important exported functions include `i2c_acpi_get_i2c_resource()`, `i2c_acpi_client_count()`, `i2c_acpi_find_bus_speed()`, `i2c_acpi_find_adapter_by_handle()`, `i2c_acpi_new_device_by_fwnode()`, and `i2c_acpi_waive_d0_probe()`. Internal work is organized around `struct i2c_acpi_lookup`, `i2c_acpi_do_lookup()`, `i2c_acpi_get_info()`, `i2c_acpi_register_device()`, `i2c_acpi_add_device()`, and notifier `i2c_acpi_notify()`.

## Control Flow

When an adapter with an ACPI companion is registered, `i2c_acpi_register_devices()` walks the ACPI namespace, extracts compatible I2C resources, verifies that the resource points back to the adapter, fills board info, sets modalias and fwnode, and creates I2C clients unless platform quirks skip enumeration. Speed lookup walks all devices on a bus and selects the slowest requested speed, with explicit force-speed workarounds for known touch devices. ACPI reconfig add/remove dynamically registers or unregisters clients and unbinds adapter ACPI associations.

## State and Persistence Behavior

Enumeration marks ACPI devices as enumerated and sets `ignore_parent` power behavior; failed client creation clears that power flag. The file has no long-lived cache except the global notifier. Operation-region installation stores `struct i2c_acpi_handler_data` as ACPI private data on the adapter parent and frees it on removal.

## Dependencies and Integration Points

It depends on ACPI core resource walking, I2C core, device/fwnode matching, IRQ resource translation, GPIO IRQ fallback, DMI/ACPI quirks, and optional `CONFIG_ACPI_I2C_OPREGION`. Operation-region support maps ACPI GSB access attributes to SMBus byte/word/block or raw I2C byte transfers through temporary `i2c_client` objects.

## Risks

ACPI tables are often imperfect; the file contains ignore and force-speed workarounds for known bad firmware. `i2c_acpi_get_info()` rejects already enumerated devices, so hotplug ordering matters. Operation-region handlers allocate temporary clients and buffers per access and report transfer status through `gsb->status`; unsupported accessor types return ACPI parameter errors. Speed forcing can override a slowest-resource result by design.

## Test Signals

Validate I2cSerialBus parsing, client counts, 10-bit flag propagation, IRQ and GPIO IRQ fallback with wake flag, adapter-handle matching, namespace enumeration depth, dependency clearing, force 400 kHz and force 100 kHz device workarounds, ACPI add/remove notifier behavior, indexed resource client creation with `-EPROBE_DEFER`, D0-probe waive logic, and GSB opregion read/write paths for send/receive, byte, word, block, multibyte, and unsupported accessors.

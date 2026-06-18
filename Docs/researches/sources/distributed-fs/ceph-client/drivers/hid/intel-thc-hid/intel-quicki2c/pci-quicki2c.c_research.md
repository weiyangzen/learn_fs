# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/pci-quicki2c.c

## Purpose
`pci-quicki2c.c` is the PCI driver for Intel THC QuickI2C. It enables the PCI device, reads ACPI resources for the HID-over-I2C target and THC platform tuning, configures the THC I2C sub-IP, IRQs, wake-on-touch, DMA, HID descriptors, runtime PM, and full system sleep/hibernate transitions.

## Important APIs, types, and functions
Main entry points are `quicki2c_probe()`, `quicki2c_remove()`, `quicki2c_shutdown()`, and the `quicki2c_pm_ops` callbacks. ACPI helpers are `quicki2c_acpi_get_dsm_property()`, `quicki2c_acpi_get_dsd_property()`, and `quicki2c_get_acpi_resources()`. IRQ/data helpers are `quicki2c_irq_quick_handler()`, `quicki2c_irq_thread_handler()`, `handle_input_report()`, and `try_recover()`. Device/DMA helpers include `quicki2c_dev_init()`, `quicki2c_dev_deinit()`, `quicki2c_dma_init()`, `quicki2c_dma_deinit()`, advanced DMA enable/disable, and report-buffer allocation.

## Control flow and integration points
Probe enables PCI, maps BAR 0, chooses a 64-bit or 32-bit DMA mask, allocates one IRQ vector, initializes `quicki2c_device`, requests a threaded IRQ, reads the HIDI2C descriptor, allocates report buffers, configures THC DMA, unquiesces interrupts, powers the device on, resets the HIDI2C device, reads the report descriptor, registers a HID device, marks the state enabled, and enables autosuspend runtime PM.

ACPI parsing fetches the HID descriptor address and LTR values through DSMs, then gets ICRS/ISUB buffers for slave address, connection speed, timing counters, max frame size, and interrupt delay. Only 7-bit addressing is supported. Speed ranges select standard, fast/fast-plus, or high-speed THC I2C modes.

The IRQ top half disables THC interrupts and wakes the threaded handler. The thread resumes runtime PM, calls `thc_interrupt_handler()`, recovers on fatal/transaction/unknown interrupts, drains RXDMA2 via `thc_rxdma_read()`, handles zero-length reset acknowledgments, sends input data to HID only when enabled, re-enables interrupts, optionally reconfigures DMA, and drops the runtime PM reference.

## State and persistence behavior
`struct quicki2c_device` persists as devm-managed driver data for the PCI device. It stores ACPI-derived bus parameters, THC context, HID descriptor, cached report descriptor, input/report buffers, reset wait state, advanced RX configuration, LTR values, and state enum. No disk persistence is present. Runtime PM switches THC LTR mode between active and low power.

## Dependencies
The file depends on PCI core, ACPI DSM/DSD, GPIO wake-on-touch mappings, PM runtime, HID registration through `quicki2c-hid.c`, HIDI2C protocol helpers from `quicki2c-protocol.c`, and exported THC core functions for port selection, I2C timing, interrupts, DMA, WOT, and LTR.

## Risks and edge cases
The ACPI buffer helper copies returned buffers without validating length against the destination structure, making firmware table correctness critical. Probe error paths after DMA configuration often jump to `dev_deinit` rather than `dma_deinit`, so DMA cleanup ordering should be audited. Interrupts are enabled during initialization before all buffers are available; state gating drops samples but reset interrupts must still be handled. Runtime PM is entered with `pm_runtime_put_noidle()`/`put_autosuspend()` without an explicit enable call in this file, relying on inherited PM state conventions. Advanced RX max-size settings clamp invalid ACPI values but may truncate devices with larger real reports.

## Test signals
Test PCI ID matching for LNL/PTL/WCL/NVL ports, ACPI DSM/DSD missing or malformed data, 7-bit versus 10-bit addressing rejection, all supported I2C speed bands, descriptor read/reset/report-descriptor flow, threaded IRQ RXDMA input, reset ACK fallback, fatal interrupt recovery, DMA allocation/configuration failures, WOT GPIO presence/absence, suspend/resume/freeze/thaw/poweroff/restore, runtime autosuspend LTR switching, and HID raw GET/SET report behavior through runtime PM.

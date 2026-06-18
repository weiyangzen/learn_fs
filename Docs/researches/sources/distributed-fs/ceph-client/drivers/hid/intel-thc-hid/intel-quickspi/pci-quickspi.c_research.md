# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/pci-quickspi.c

## Purpose
`pci-quickspi.c` is the PCI driver for Intel THC QuickSPI. It enables THC hardware in SPI mode, reads HIDSPI/QuickSPI/platform ACPI resources, configures SPI read/write engines, interrupts, wake-on-touch, DMA, HID descriptors, runtime PM, and system sleep/hibernate transitions.

## Important APIs, types, and functions
Main entry points are `quickspi_probe()`, `quickspi_remove()`, `quickspi_shutdown()`, and `quickspi_pm_ops`. ACPI parsing uses `thc_acpi_get_property()` and `quickspi_get_acpi_resources()`. IRQ and recovery functions are `quickspi_irq_quick_handler()`, `quickspi_irq_thread_handler()`, and `try_recover()`. Device/DMA/buffer helpers are `quickspi_dev_init()`, `quickspi_dev_deinit()`, `quickspi_dma_init()`, `quickspi_dma_deinit()`, and `quickspi_alloc_report_buf()`.

## Control flow and integration points
Probe enables PCI, maps BAR 0, sets DMA mask, allocates one IRQ vector, creates and configures `quickspi_device`, requests a threaded IRQ, resets the touch device via `reset_tic()`, allocates report buffers, configures THC DMA, fetches the report descriptor, registers the HID device, marks state enabled, and enables autosuspend runtime PM.

ACPI parsing fetches input header/body/output report addresses, read/write opcodes, read/write IO modes, connection speed, packet-size limit, performance delay, and LTR values through three DSM GUIDs. SPI IO mode bits are decoded into THC read/write mode fields, and packet size is selected from platform driver data unless the device requests limiting.

The IRQ top half disables interrupts and wakes the threaded handler. The thread resumes runtime PM, handles THC fatal/transaction errors through reset and DMA reconfiguration, handles non-DMA interrupts as reset or descriptor-response wakeups, drains RXDMA2 into `input_buf`, and calls `quickspi_handle_input_data()` to parse HIDSPI responses or input reports.

## State and persistence behavior
`struct quickspi_device` is devm-managed per PCI device and stores ACPI-derived SPI parameters, THC/HID pointers, descriptors, report/input buffers, waitqueue flags for reset/non-DMA/report/get/set completion, LTR values, packet-size/performance settings, and state enum. Runtime PM changes THC LTR mode only; no disk persistence exists.

## Dependencies
The driver depends on PCI, ACPI DSMs, GPIO wake-on-touch, PM runtime, HID glue, HIDSPI protocol helpers, and exported Intel THC core functions for port selection, SPI address/config, interrupt handling, DMA, WOT, and LTR.

## Risks and edge cases
ACPI buffer copies assume the returned object is large enough for target fields. Interrupts are enabled during device initialization before every probe-stage buffer exists; state and waitqueue logic must absorb early events. Recovery resets the TIC and reconfigures DMA but disables the device if that fails. System restore must fully reprogram SPI address/read/write settings because hardware may lose state. Shared response flags such as `get_report_cmpl`/`set_report_cmpl` are single-flight and assume serialized HID requests.

## Test signals
Test PCI IDs for MTL/LNL/PTL/WCL/ARL/NVL ports, ACPI resource absence and malformed objects, SPI IO mode decoding, packet-size limit behavior, reset via ACPI `_RST`, non-DMA interrupt handling, RXDMA report parsing, DMA allocation/configuration failure, error recovery, report descriptor retrieval, HID registration, suspend/resume/freeze/thaw/poweroff/restore, runtime autosuspend LTR switching, and raw HID GET/SET report completion waits.

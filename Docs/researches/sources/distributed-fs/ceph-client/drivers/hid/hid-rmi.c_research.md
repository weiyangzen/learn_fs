# sources/distributed-fs/ceph-client/drivers/hid/hid-rmi.c

## Purpose

`hid-rmi.c` implements a HID transport for Synaptics RMI4 devices. It detects HID reports that expose RMI register access, registers an `rmi_transport_dev` with the RMI core, converts HID output/input reports into RMI read/write block operations, and turns HID attention reports into an IRQ-like event path for the RMI function drivers.

## Important APIs, Types, and Functions

- `struct rmi_data`: per-device state for page selection, RMI transport, read wait queue, report buffers, flags, reset work, HID device pointer, device capability flags, and IRQ domain/mapping.
- `rmi_hid_read_block()` and `rmi_hid_write_block()`: RMI transport operations that implement paged register reads and writes using HID reports.
- `rmi_set_page()` and `rmi_set_mode()`: helper operations for RMI page register writes and feature-report mode selection.
- `rmi_raw_event()`, `rmi_read_data_event()`, and `rmi_input_event()`: dispatch incoming HID reports to read-completion or attention handling.
- `rmi_event()`: suppresses generic mouse events from RMI devices and schedules reset-to-RMI-mode work when mouse-emulation reports appear.
- `rmi_input_configured()` and `rmi_input_mapping()`: open HID I/O, switch to attention mode, set page zero, register the RMI transport, and hide normal HID usages for RMI devices.
- `rmi_setup_irq_domain()`: creates a one-entry IRQ domain and maps a virtual IRQ for RMI core attention delivery.
- `rmi_probe()` and `rmi_remove()`: parse/start the HID device, detect RMI report IDs, allocate buffers, configure transport data, and unregister transport on removal.

## Control Flow

Probe allocates `rmi_data`, sets `HID_QUIRK_NO_INIT_REPORTS` and `HID_QUIRK_NO_INPUT_SYNC`, parses reports, and uses `rmi_check_valid_report_id()` to determine whether the device has the RMI feature, attention input, and write output reports. If the reports are missing, probe falls through to `hid_hw_start()` and the device behaves as ordinary HID. If present, it marks `RMI_DEVICE`, allocates a combined output/input buffer, initializes the wait queue and page mutex, creates an IRQ domain, fills `xport` with HID operations and platform data, then starts HID.

After HID input configuration, `rmi_input_configured()` opens HID hardware, starts device I/O, sets attention-report mode, sets RMI page 0, registers the RMI transport, sets `RMI_STARTED`, stops I/O, and closes the device. RMI core calls back into `rmi_hid_read_block()` and `rmi_hid_write_block()` for register access. Reads serialize on `page_mutex`, switch pages when necessary, send a read-address output report, wait up to one second for `RMI_READ_DATA_PENDING`, copy chunks from `readReport`, retry up to five times on timeout, and clear pending flags on exit. Writes serialize similarly, switch pages, fill a write report, and send it.

Incoming raw events are filtered by report ID. Read data reports wake the wait queue if a read is pending. Attention reports call `rmi_set_attn_data()`, then invoke the mapped IRQ with interrupts locally disabled. Generic mouse/pointer events from RMI devices are suppressed; with physical buttons, button usages are allowed and zero X/Y events are filtered. A mouse-emulation event schedules reset work to put firmware back into RMI attention mode.

Suspend calls `rmi_driver_suspend()`. Resume opens the HID device, resets attention mode, calls `rmi_driver_resume()`, and closes HID. Removal clears `RMI_STARTED`, cancels reset work, unregisters the RMI transport, and stops HID hardware.

## State and Persistence Behavior

Persistent state includes the current RMI page, report buffer sizes and pointers, capability flags, pending-read flags, `RMI_STARTED`, the RMI transport registration, and the synthetic IRQ mapping. `page_mutex` serializes page switching and all register I/O. The wait queue and bit flags coordinate asynchronous HID input reports with synchronous RMI register reads. `rmi_hid_pdata` is a static platform-data template; probe mutates its GPIO-disable field for physical-button devices before copying it into `xport.pdata`.

## Dependencies and Integration Points

This file bridges HID core, the Linux RMI4 core (`linux/rmi.h`), input, PM, wait queues, workqueues, IRQ domains, and HID raw report I/O. Device IDs include specific Razer, Lenovo, Primax, Synaptics, and generic `HID_GROUP_RMI` matches. RMI core consumes the `hid_rmi_ops` transport callbacks and receives attention events through the synthetic IRQ.

## Risks and Edge Cases

- `rmi_hid_read_block()` copies `read_input_count` bytes but increments by the unbounded report count even when `min(read_input_count, bytes_needed)` copied less; malformed reports can desynchronize `bytes_read`.
- `rmi_hid_write_block()` copies `len` bytes into `writeReport[4]` without checking that `len + 4 <= output_report_size`.
- `rmi_check_sanity()` reads `data[valid_size - 1]` before checking `valid_size > 0`; a zero-size report would underflow.
- Static `rmi_hid_pdata` is mutated for physical-button devices and then reused for later devices, so `gpio_data.disable` can leak between probes.
- Attention handling calls into generic IRQ handling under `local_irq_save()`, so downstream RMI paths must be IRQ-context safe.
- Missing RMI reports cause a graceful fallback to generic HID, but partial or bogus reports can still allocate buffers and fail later.

## Test Signals

Coverage should include RMI-capable and non-RMI fallback devices, report-ID validation, page switching, successful and timed-out reads, multi-packet reads, oversized write rejection, attention IRQ delivery, physical-button filtering, mouse-emulation reset work, suspend/resume mode restoration, and removal while read/reset work is pending. Static analysis should flag the zero-size sanity check and write-buffer bounds assumptions.

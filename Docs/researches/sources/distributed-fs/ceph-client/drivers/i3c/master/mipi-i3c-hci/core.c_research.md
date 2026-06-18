# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/core.c

## Purpose

`core.c` is the main MIPI I3C HCI platform driver and the integration layer between HCI hardware and the Linux I3C master framework. It probes HCI capabilities, maps table/register sections, parses extended capabilities, selects v1/v2 command descriptors and DMA/PIO I/O mode, implements `i3c_master_controller_ops`, handles top-level interrupts, and provides runtime/system PM flows.

## Important APIs, Types, and Functions

- Register definitions cover HCI version, control, capabilities, reset, DAT/DCT/PIO/RHS/extended-cap sections, interrupt registers, and master dynamic address.
- `i3c_hci_bus_init()` initializes DAT when needed, assigns the master dynamic address, starts the selected I/O backend, applies AMD response-threshold quirks, enables IRQ activity, and enables the bus with Hot-Join disabled.
- `i3c_hci_process_xfer()` queues transfers through `hci->io`, waits for completion, attempts dequeue on timeout, and delegates backend error recovery.
- CCC/private transfer callbacks (`i3c_hci_send_ccc_cmd()`, `i3c_hci_i3c_xfers()`, `i3c_hci_i2c_xfers()`) allocate `hci_xfer` arrays, call command preparation, set `ROC/TOC`, and decode responses.
- Device attach/detach callbacks allocate `struct i3c_hci_dev_data`, manage v1 DAT entries, and configure I2C/static/dynamic address table fields.
- IBI callbacks update DAT SIR/payload flags and delegate pool management to the chosen I/O backend.
- `i3c_hci_init()` validates HCI version, discovers sections, parses ext caps, selects command model, applies quirks, and calls reset/init.
- PM exports `i3c_hci_rpm_suspend()` and `i3c_hci_rpm_resume()` are used by PCI parent glue.

## Control Flow

Probe allocates `struct i3c_hci`, maps base registers either from platform data or a platform resource, records quirk data, initializes the hardware, requests a shared IRQ, configures runtime PM flags, and registers the I3C master. Hardware initialization validates versions 1.0, 1.1, and 2.0, reads capability and table-section registers, computes DAT/DCT entry counts, discovers RHS/PIO/ext-cap offsets, parses extended capabilities, selects command ops from `HC_CAP_CMD_SIZE`, forces PIO for AMD if requested, resets the controller, sets endian mode, and chooses DMA first when RHS exists or PIO otherwise.

During normal transfers, the I3C core callback prepares an `hci_xfer` list. The selected command ops fill descriptors and TIDs. The core adds response and termination flags, queues the list to the selected I/O backend, waits on the last transfer completion, and checks response statuses. The top-level IRQ handler acknowledges HCI core interrupt status under `hci->lock`, filters inactive shared IRQ calls, logs host-controller errors, then calls the backend IRQ handler.

## State and Persistence Behavior

`struct i3c_hci` stores MMIO section pointers, capability/version fields, command and I/O vtables, DAT/DCT metadata, cached DAT entries, current master dynamic address, quirk flags, IRQ active state, and backend private data. DAT entries persist across attached devices and are restored on runtime resume. `irq_inactive` prevents shared IRQ handling while the controller is suspended or not expected to interrupt.

## Dependencies and Integration Points

The file integrates with the Linux platform driver, I3C master framework, runtime PM, IRQ subsystem, HCI PIO/DMA backends, v1/v2 command implementations, DAT support, extended capability parsing, and PCI glue through exported RPM functions. It also uses platform data for multi-instance PCI children that share a parent MMIO mapping.

## Risks and Edge Cases

Transfer length limit is derived from `HC_CAP_MAX_DATA_LENGTH`; callers at or above the limit fail with `-EFBIG`. `i3c_hci_request_ibi()` assumes v1-style DAT-backed device data and would need review for pure v2 DAT-less operation. Runtime resume unconditionally restores v1 DAT state, so future non-v1 paths need care. Shared IRQ handling depends on precise `irq_inactive` updates around suspend/resume. Hardware reset and bus disable failures can leave the backend with stale queue state.

## Test Signals

Probe tests should cover HCI versions, command size values, DMA/PIO selection, endian toggling, and quirk match data. Transfer tests should verify CCC, I3C, I2C, timeout/dequeue, and response error paths on both PIO and DMA. PM tests should suspend/resume with attached devices, restore DAT, keep shared IRQs quiet while inactive, and run DAA after system resume.

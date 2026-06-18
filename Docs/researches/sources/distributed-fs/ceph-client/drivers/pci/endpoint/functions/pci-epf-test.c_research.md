<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-test.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-test.c

## Purpose
Implements the `pci_epf_test` endpoint-function driver used to validate PCI endpoint controller behavior from a root-complex test client. It exposes a BAR-hosted command/status register block and exercises BAR access, outbound memory mapping, DMA transfers, INTx/MSI/MSI-X delivery, platform-MSI doorbells, and dynamic BAR subrange mapping.

## Important APIs, Types, and Functions
`struct pci_epf_test` stores per-function state: BAR virtual addresses, the selected test-register BAR, EPC feature pointer, delayed command work, DMA channels, transfer completion state, configured BAR sizes, and temporary doorbell BAR metadata. `struct pci_epf_test_reg` is the little-endian ABI shared with the host and carries commands, status bits, source/destination PCI addresses, size, checksum, interrupt selection, flags, capabilities, and doorbell metadata.

Core handlers are `pci_epf_test_cmd_handler()`, `pci_epf_test_read()`, `pci_epf_test_write()`, `pci_epf_test_copy()`, `pci_epf_test_raise_irq()`, `pci_epf_test_enable_doorbell()`, `pci_epf_test_disable_doorbell()`, `pci_epf_test_bar_subrange_setup()`, and `pci_epf_test_bar_subrange_clear()`. Lifecycle hooks are wired through `pci_epf_test_event_ops` and `ops`: `.bind`, `.unbind`, `.epc_init`, `.epc_deinit`, `.link_up`, `.link_down`, and `.add_cfs`.

## Control Flow
Probe allocates driver state, assigns `test_header`, initializes default BAR sizes, and installs event ops. Bind gets EPC features, chooses the first free BAR for the control register block, allocates BAR spaces, and records the EPC feature contract. `epc_init` initializes DMA if possible, writes the PCI config header for physical functions or VF1, publishes capabilities in the test register, sets BARs, configures MSI/MSI-X if supported, and starts command polling immediately unless the controller supplies a link-up notifier. Link-up starts the delayed command worker; link-down, deinit, and unbind cancel it and clear hardware mappings.

The command worker polls every 1 ms. It atomically reads and clears `reg->command`, clears status, rejects DMA commands when DMA channels are unavailable, dispatches exactly one command value, updates status, raises the selected interrupt, and requeues itself. Data operations repeatedly call `pci_epc_mem_map()` because controller alignment may map less than the requested host PCI range; each loop unmaps before advancing the PCI address.

## State and Persistence
All state is kernel-resident and tied to the EPF device lifetime. Configfs BAR size attributes persist only while the EPF instance exists and are rejected after the EPF has been bound to an EPC. The host-visible ABI is the BAR register block; status bits are written back there and the host observes command completion by interrupt and memory reads. Doorbell enable temporarily remaps a BAR to an MSI message address and disable restores the BAR mapping to normal EPF memory.

## Dependencies and Integration Points
This file depends on the PCI endpoint core (`pci_epf_*`, `pci_epc_*`), EPC memory mapping (`pci_epc_mem_map()` and `pci_epc_mem_unmap()`), the endpoint MSI-doorbell helper (`pci_epf_alloc_doorbell()`), DMAengine, CRC32, configfs, delayed workqueues, and PCI register definitions. It integrates with userspace through configfs function creation and BAR-size attributes, with the host-side PCI endpoint test driver through the BAR ABI, and with EPC controller drivers through feature flags and operation callbacks.

## Risks and Edge Cases
The command register is polled rather than interrupt-driven, so host writes can be delayed by the workqueue interval and concurrent command writes are not queued. DMA is optional and may silently fall back to CPU copy if channel allocation fails at init; command handling rejects DMA later when unsupported. The copy path must handle partial mappings correctly; a missed unmap would leak outbound windows. Doorbell setup overrides BAR inbound translation and relies on restore in disable/unbind paths. Subrange mapping mutates `bar->submap` and must restore the old mapping on `pci_epc_set_bar()` failure; `-ENOSPC` is surfaced as `STATUS_NO_RESOURCE`. Module exit destroys the workqueue before unregistering the EPF driver, so active instances must have canceled work during unbind/deinit.

## Test Signals
Useful test signals are host-side command completion bits, CRC match/mismatch for read/write, copy data verification by the root complex, successful MSI/MSI-X/INTx delivery, doorbell IRQ handling via `STATUS_DOORBELL_SUCCESS`, subrange signature validation, dmesg throughput logs from `pci_epf_test_print_rate()`, and failure injection on invalid PCI addresses, unsupported DMA, exhausted BAR resources, and controllers with reserved/fixed BARs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-test.c -->

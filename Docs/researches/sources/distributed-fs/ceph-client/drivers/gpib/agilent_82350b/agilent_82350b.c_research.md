# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.c

## Purpose
`agilent_82350b.c` implements GPIB support for HP/Agilent/Keysight 82350A, 82350B, and 82351A PCI or PCIe adapters. It wraps TMS9914 core operations and optionally accelerates transfers through board SRAM/FIFO streaming.

## Important APIs, Types, and Functions
Private state is `struct agilent_82350b_priv` from the companion header. Accelerated paths are `agilent_82350b_accel_read()` and `agilent_82350b_accel_write()`. Wrapper operations delegate to TMS9914 helpers for command, control, addressing, EOS, polling, status, and local/remote operations. Hardware setup is in `agilent_82350b_generic_attach()`, `init_82350a_hardware()`, `test_sram()`, and `agilent_82350b_detach()`. IRQ handling is `agilent_82350b_interrupt()`.

## Control Flow
Module init registers a PCI ID table for discovery and two GPIB interfaces: accelerated `agilent_82350b` and unaccelerated `agilent_82350b_unaccel`. The PCI probe is a stub; actual board selection happens in GPIB `attach()` using `gpib_pci_get_device()` or subsystem matching. Attach enables PCI, requests BAR regions, maps model-specific registers, loads 82350A firmware from `config->init_data` when required, tests SRAM, requests IRQ, enables PCI and TMS9914 interrupts, configures FIFO events if requested, sets T1 delay, resets the TMS9914, and brings the board online.

Accelerated reads disable FIFO briefly, handle a first-byte holdoff corner case, stream blocks through SRAM until transfer count or buffer-end events, then fall back to TMS9914 for final bytes. Accelerated writes send the first byte through the TMS9914, stream even FIFO blocks from host SRAM, and use TMS9914 for final EOI byte. The IRQ reads board event status, dispatches TMS9914 status when present, write-clears FIFO event bits, records them in private state under the board spinlock, and wakes waiters.

## State and Persistence
Runtime state includes mapped register bases, PCI device reference, IRQ number, card mode bits, latched event bits, model, FIFO mode, and TMS9914 private state. There is no persistence except optional firmware passed during attach for 82350A initialization.

## Dependencies and Integration Points
The driver depends on PCI, MMIO accessors, GPIB core registration, PLX9050 registers for 82350A, and the TMS9914 helper.

## Risks and Test Signals
Several attach error paths return without calling detach, so mapped resources or PCI regions can leak after mid-attach failures. The PCI driver exists mainly for ID exposure and has no real binding in probe. Accelerated paths manipulate TMS9914 interrupt masks and holdoff state, so they need race testing with timeouts and device clear. Tests should cover each board model, missing 82350A firmware, SRAM test failure, FIFO and non-FIFO transfers, EOI/EOS behavior, IRQ event wakeups, detach after partial attach, and shared IRQ handling.

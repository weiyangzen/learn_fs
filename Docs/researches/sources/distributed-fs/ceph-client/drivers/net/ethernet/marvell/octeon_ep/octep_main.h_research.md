# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_main.h

## Purpose
This header defines the PF driver's central device model, PCI IDs, queue/interrupt limits, hardware operation vector, mailbox structures, link-state representation, CSR access helpers, and exported internal APIs used by PF source files.

## Important APIs, Types, And Functions
- Device IDs and limits: `OCTEP_PCI_DEVICE_ID_*`, `OCTEP_MAX_QUEUES`, `OCTEP_MAX_VF`, `OCTEP_MAX_MSIX_VECTORS`, `OCTEP_MMIO_REGIONS`, and interrupt masks such as `OCTEP_INPUT_INTR`, `OCTEP_OUTPUT_INTR`, and `OCTEP_MBOX_INTR`.
- Ring space helpers: `IQ_INSTR_PENDING()` and `IQ_INSTR_SPACE()` compute Tx queue occupancy from write and flush indices.
- Hardware abstraction: `struct octep_hw_ops` provides chip-specific hooks for IQ/OQ/mbox register setup, non-IOQ interrupt classes, IOQ interrupt handling, reset/reinit, queue enable/disable, interrupt enable/disable, polling, and register dumps.
- Main state: `struct octep_device` aggregates config, PCI/netdev pointers, BAR mappings, queues, stats, link info, PF/VF mailbox state, control mailbox state, delayed work, and heartbeat state.
- CSR helpers: `octep_write_csr*()`, `octep_read_csr*()`, `OCTEP_PCI_WIN_READ()`, and `OCTEP_PCI_WIN_WRITE()` access direct and windowed hardware registers.

## Control Flow
The header enables source files to treat `struct octep_device` as the context passed from PCI probe to netdev operations, IRQ handlers, workqueue callbacks, and queue helpers. Chip-specific setup fills `octep_hw_ops`; generic PF code calls those function pointers without hard-coding CN9K/CNXK register layouts. Queue helpers receive `struct octep_iq` and `struct octep_oq` pointers stored in `octep_device`, while control and PF/VF mailbox paths reuse the same device-level firmware and VF state.

## State And Persistence
All fields are runtime state. The header defines no persistent storage. Important mutable state includes `caps_enabled`, `caps_supported`, `mac_addr`, `num_iqs`, `num_oqs`, queue pointer arrays, per-queue stats, `link_info`, `vf_info`, `poll_non_ioq_intr`, `hb_miss_cnt`, and control mailbox wait queues/lists. Register writes through the helpers persist only in device hardware until reset or reprogramming.

## Dependencies And Integration Points
It includes `octep_tx.h`, `octep_rx.h`, and `octep_ctrl_mbox.h`, binding the PF main context to Tx/Rx queue formats and control mailbox protocol. It exposes prototypes for `octep_device_setup()`, queue setup/free/processing functions, CN93/CNXK setup functions, and ethtool setup. Source users depend on Linux netdevice, PCI, DMA, workqueue, waitqueue, and MMIO types through included kernel headers.

## Risks And Edge Cases
- `IQ_INSTR_PENDING()` uses masked subtraction, so queue sizes are expected to be powers of two.
- The register access macros assume BAR0 is mapped and valid; callers must not use them after cleanup.
- `struct octep_hw_ops` must be fully populated for the selected chip before open/IRQ paths run.
- Mailbox and control mailbox fields are shared across interrupt and workqueue paths; lifetime must be synchronized by callers.
- `OCTEP_PCI_WIN_READ()` and `OCTEP_PCI_WIN_WRITE()` perform indirect CSR access without explicit locking in the helper, so concurrent callers need external ordering if the window registers are shared.

## Test Signals
Build coverage should catch missing prototypes or incomplete type dependencies. Runtime signals include successful chip setup populating hardware ops, valid queue counts within `OCTEP_MAX_*`, correct CSR reads/writes during register setup, working indirect PCI window reads, and stable link/VF/control-mailbox behavior across open, stop, SR-IOV, and remove.

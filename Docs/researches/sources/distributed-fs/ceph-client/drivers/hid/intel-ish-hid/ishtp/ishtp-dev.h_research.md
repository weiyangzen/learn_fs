# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/ishtp-dev.h

## Purpose
`ishtp-dev.h` defines the central ISHTP provider-device state, hardware operation callbacks, device state enum, core limits, firmware-client representation, and top-level initialization/start declarations. It is the shared private contract between the ISHTP transport, HBM, bus, client, loader, DMA, and low-level IPC driver code.

## Important APIs, types, and functions
Key constants define IPC payload sizes, RX/TX FIFO capacities, maximum client counts, host client IDs, DMA timing, and resume timeout. `enum ishtp_dev_state` covers initialization, client enumeration, enabled, reset, disabled, and power transitions. `struct ishtp_hw_ops` is the hardware abstraction for reset, IPC header generation, writes, reads, firmware status, clock sync, and DMA cache-snooping checks. `struct ishtp_device` anchors PCI/device pointers, suspend/resume wait state, locks, HBM state, workqueues, loader state, client lists, bus devices, message FIFOs, write queues, firmware client tables, DMA buffers, version info, debug counters, hardware ops, MTU, and hardware-private trailing storage.

## Control flow and integration points
The header has simple inline helpers `ishtp_secs_to_jiffies()` and `ish_ipc_reset()`. The rest of its content is structural: low-level IPC code fills hardware ops and transport fields, `init.c` initializes list/lock/wait state, `hbm.c` transitions HBM/device state and firmware-client tables, `client.c` consumes client lists and DMA buffers, and loader code uses fixed-client response storage.

## State and persistence behavior
`struct ishtp_device` is the primary volatile state container for a live ISH device. It contains no persistent disk-backed state; version fields copied from firmware/manifests remain in memory for reporting while the device is live. Lists, bitmaps, DMA buffers, work items, and wait queues exist until driver removal/reset teardown.

## Dependencies
It includes Linux types/spinlocks, the exported Intel ISH client interface, bus declarations, and HBM protocol definitions. It depends on PCI/device types being available to implementation files and on low-level hardware code supplying `struct ishtp_hw_ops`.

## Risks and edge cases
The structure is broad and heavily shared, so initialization ordering is critical. Interrupts before list/lock/FIFO setup, missed state transitions, or low-level ops installed too late can corrupt startup. Several fields are accessed by IRQ, workqueue, PM, and client contexts, making lock discipline and wakeup pairing important. Fixed FIFO sizes (`RD_INT_FIFO_SIZE`, `IPC_TX_FIFO_SIZE`) create overflow behavior under interrupt storms.

## Test signals
Probe/remove, reset recovery, suspend/resume, HBM enumeration, client open/close stress, loader-capable firmware boot, DMA enablement, debug counter sanity, low-level ops fault injection, and allmodconfig builds should cover this contract.

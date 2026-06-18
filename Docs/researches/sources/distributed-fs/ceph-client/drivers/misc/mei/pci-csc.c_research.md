# sources/distributed-fs/ceph-client/drivers/misc/mei/pci-csc.c

## Purpose
This is a PCI MEI backend for Intel discrete graphics CSC platforms. It supports a device exposing multiple HECI blocks but intentionally binds to HECI2 at a fixed BAR offset and wires it into the common MEI ME hardware implementation.

## Important APIs, types, and functions
Key functions are `mei_csc_probe()`, `mei_csc_shutdown()`, `mei_csc_remove()`, system sleep callbacks, runtime-PM callbacks, and `mei_csc_read_fws()`. The PCI ID table uses `PCI_DEVICE_DATA(INTEL, MEI_CRI, MEI_ME_CSC_CFG)`. PM operations are grouped in `mei_csc_pm_ops`.

## Control flow and state
Probe enables the PCI device with managed helpers, maps BAR0, sets a 64-bit DMA mask, creates a MEI ME device from the CSC config, sets `read_fws_need_resume`, points `hw->mem_addr` at `registers + MEI_CSC_HECI2_OFFSET`, registers the MEI char/bus device, allocates one IRQ vector, installs the shared ME IRQ handlers, and calls `mei_start()`. Unlike `pci-me.c`, firmware handshake failure is only warned so userspace can still inspect firmware status. Remove delegates to shutdown then deregisters.

## State and persistence behavior
State is held in the `mei_device` and hardware private `mei_me_hw`. Runtime suspend marks `hw->pg_state = MEI_PG_ON`; resume marks it off and invokes the IRQ thread handler to drain queues waiting for resume. No persistent storage is used.

## Dependencies and integration points
It depends on local ME hardware code (`hw-me.h`, `hw-me-regs.h`), common MEI client/core interfaces, PCI, DMA, threaded IRQs, runtime PM, and tracing. It integrates with sysfs/char-device registration through `mei_register()` and with firmware-status reporting through the custom register-read offset.

## Risks and test signals
Risks include wrong HECI offset, reading firmware-status registers while suspended, IRQ vector cleanup ordering, continuing after failed `mei_start()`, and runtime-PM races with pending writes. Test signals include CSC PCI probe, HECI2 communication, sysfs firmware-status access after failed handshake, suspend/resume, runtime idle rejection when writes are active, and IRQ cleanup on remove/shutdown.

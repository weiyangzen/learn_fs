# sources/distributed-fs/ceph-client/drivers/ipack/carriers/tpci200.c

Purpose: Implements the TEWS TPCI-200 PCI carrier. It maps PCI BAR windows into IPACK slot regions, registers an IPACK bus with four slots, creates child `ipack_device`s, and dispatches carrier interrupts to per-slot handlers.

Important APIs/types/functions: `tpci200_pci_probe()`, `tpci200_register()`, `tpci200_install()`, `tpci200_create_device()`, `tpci200_request_irq()`, `tpci200_free_irq()`, `tpci200_interrupt()`, `tpci200_bus_ops`, and the PCI driver/id table.

Control flow: PCI probe allocates board/info state, maps configuration memory, sets PLX descriptors to preserve big-endian IP module access, requests/maps interface and slot BARs, registers the shared PCI IRQ, registers an IPACK bus, and creates four child devices. Child creation fills each IPACK region from carrier base plus slot interval, then calls `ipack_device_init()` and `ipack_device_add()`. Interrupt handling reads the carrier status register, checks slot bits, and invokes each registered slot handler through an RCU-protected pointer.

State and persistence: Board state includes PCI resources, mapped control registers, slot array, a mutex, a register spinlock, and per-space physical bases. Slot IRQ handlers are installed under the mutex and published with RCU; removal unregisters the IPACK bus, frees the PCI IRQ, unmaps BARs, releases regions, and drops the PCI ref.

Dependencies/integration: Uses PCI, IPACK bus APIs, MMIO accessors, shared IRQ handling, RCU, mutex/spinlock protection, and constants from `tpci200.h`.

Risks and test signals: Test probe unwind at each PCI resource step, concurrent interrupt/free_irq behavior, absent slot handler disabling, clock-rate toggles, timeout/error status helpers, four-slot child enumeration, hot-unplug, and whether failures from individual `tpci200_create_device()` calls should be surfaced.

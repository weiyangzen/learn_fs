# sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.c

Purpose: implements the adapter driver for `fmh_gpib_core`, a custom CB7210/NEC7210-compatible GPIB core with platform MMIO/DMA support and a prototype PCI FIFO variant.

Important APIs and functions: registers `fmh_gpib_unaccel`, `fmh_gpib`, `fmh_gpib_pci_unaccel`, and `fmh_gpib_pci`. Standard GPIB callbacks wrap NEC7210 operations. FMH-specific callbacks implement local parallel-poll mode, serial-poll response mode 2 (`fmh_gpib_serial_poll_response2`), line status, T1 delay, and return-to-local. Accelerated paths include DMA write/read for platform devices and FIFO write/read for PCI devices. `fmh_gpib_internal_interrupt` handles IFC/ATN-related status, delegates NEC7210 interrupts, mirrors extended status into NEC7210 state bits, handles FIFO half-full/half-empty interrupts, and wakes waiters.

Control flow: platform attach finds an unattached matching device by OF path, marks it with `dev_set_drvdata`, allocates private data, maps named resources `gpib_control_status` and `dma_fifos`, requests shared IRQ, optionally acquires DMA channel `"rxtx"`, reads FIFO burst length, initializes hardware, and sets RFD holdoff. PCI attach finds prototype vendor/device IDs, enables PCI, maps BAR resources, requests IRQ, reads FIFO capability, and initializes. Accelerated reads release holdoff, run DMA/FIFO transfers, drain residual FIFO bytes, set END from status/EOI flags, then reassert holdoff when appropriate.

State and persistence: `struct fmh_priv` tracks NEC7210 state, resources, IRQ, DMA channel, DMA buffer, FIFO base, burst length, and FIFO interrupt support. `board->dev` is used to prevent duplicate platform attachment. NEC7210 state bits track data readiness, command readiness, END, bus error, device clear, DMA progress, and RFD holdoff.

Dependencies and integration: depends on `fmh_gpib.h`, `gpibP.h`, NEC7210 helpers, platform/OF APIs, PCI APIs, DMAengine, MMIO, IRQ, waitqueues, and common GPIB registration. User space selects the specific accelerated/unaccelerated board type by name.

Risks: numerous attach failure paths leak prior private allocations, device references, regions, mappings, IRQs, or DMA channels. `fmh_gpib_pci_attach_holdoff_end()` returns `-EIO` after successful attach if FIFO interrupts are unsupported without detaching. DMA mapping errors are logged but not made fatal. FIFO interrupt clearing writes zero to the full control/status register, intentionally disabling other FIFO modes and relying on no concurrent FIFO mode use. Prototype PCI IDs must be patched for real hardware.

Test signals: build/load with platform and PCI configs; run repeated online/offline; fault-inject resource, IRQ, DMA, and registration failures; test PIO, DMA, and FIFO paths; verify RFD holdoff around END bytes, serial-poll request-service transitions, local parallel-poll mode, IFC event delivery, FIFO half interrupt behavior, and fallback to unaccelerated board types.

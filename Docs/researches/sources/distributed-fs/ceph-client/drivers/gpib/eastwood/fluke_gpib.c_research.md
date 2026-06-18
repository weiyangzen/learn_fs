# sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.c

Purpose: implements Fluke CDA/Eastwood GPIB board support for a custom CB7210/NEC7210-compatible core connected to a PL330 DMA channel. It provides unaccelerated, hybrid, and fully accelerated GPIB interfaces.

Important APIs and functions: `fluke_unaccel_interface` uses NEC7210 PIO read/write; `fluke_hybrid_interface` accelerates writes only; `fluke_interface` accelerates both reads and writes. Wrappers delegate standard GPIB operations to NEC7210 helpers. DMA paths include `fluke_config_dma`, `fluke_dma_write`, `fluke_accel_write`, `fluke_dma_read`, and `fluke_accel_read`. Interrupt flow is `fluke_gpib_interrupt` -> `fluke_gpib_internal_interrupt`, which reads CB7210/NEC7210 status, handles IFC events, delegates NEC7210 interrupt handling, updates read-ready state, and wakes waiters.

Control flow: attach requires a probed platform device, allocates private state and a DMA buffer, maps three MMIO resources, requests IRQ, optionally acquires DMA channel 0, resets and configures the CB7210 clock/handshake mode, requests a pseudo IRQ, and enables IFC interrupts. Accelerated writes DMA all but a final EOI byte when needed, waits for source handshake readiness before `AUX_SEOI`, and records transferred bytes from a hardware counter. Accelerated reads release RFD holdoff, start DMA, handle END races, terminate/pause DMA, copy from the bounce buffer, and set `end`.

State and persistence: private state tracks NEC7210 state, MMIO resources, IRQ, DMA channel, DMA bounce buffer, and write-transfer counter mapping. NEC7210 state bits coordinate DMA in progress, read/write readiness, bus errors, END, and device clear. State is only live while the board is online.

Dependencies and integration: depends on `fluke_gpib.h`, `gpibP.h`, NEC7210 helpers, Linux platform bus, OF match `flk,fgpib-4.0`, DMAengine, MMIO, IRQ, waitqueues, and pseudo IRQ support from `gpib_common`.

Risks: many attach failure exits do not unwind already requested regions, mappings, IRQs, or private allocations. `fluke_dma_write()` unmaps `address` even if mapping setup was not valid after an earlier failure, and DMA mapping errors are not checked. The code documents possible DMA-read corruption and offers the hybrid interface as mitigation. Wait logic relies on precise hardware state bits and may return partial transfers after timeout, device clear, or bus error.

Test signals: build/load with matching OF device; test all three interface names; inject missing resources, IRQ failure, and DMA unavailable; run read/write with and without EOI, timeout, IFC/device clear, and bus error; verify pseudo IRQ polling, IFC event delivery, DMA residue/counter correctness, and detach resource release under repeated online/offline cycles.

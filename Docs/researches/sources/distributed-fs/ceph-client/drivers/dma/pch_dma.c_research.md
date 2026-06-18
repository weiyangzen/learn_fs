# sources/distributed-fs/ceph-client/drivers/dma/pch_dma.c

## Purpose
`pch_dma.c` is a PCI dmaengine slave driver for Intel EG20T PCH and LAPIS/ROHM ML7213, ML7223, and ML7831 IOH DMA controllers. It manages up to 12 hardware channels using DMA-pool descriptors and supports private slave SG transfers.

## Important APIs, Types, and Functions
- `struct pch_dma_desc_regs` mirrors per-descriptor hardware fields: device address, memory address, size/width, and next pointer/control.
- `struct pch_dma_desc` wraps descriptor registers, `dma_async_tx_descriptor`, and list nodes for chained descriptors.
- `struct pch_dma_chan` stores one channel's MMIO descriptor window, direction, tasklet, error bit, lock, active/queued/free lists, and allocation count.
- `struct pch_dma` contains the dmaengine device, PCI MMIO base, descriptor pool, saved registers, and channel array.
- `pdc_set_dir()`, `pdc_set_mode()`, `pdc_dostart()`, and `pdc_advance_work()` program channel control and dispatch queued descriptors.
- `pd_prep_slave_sg()` builds one-shot or scatter-gather chains from a `struct pch_dma_slave` supplied through `chan->private`.
- `pd_irq()` reads/clears status registers and schedules per-channel tasklets.
- `pch_dma_probe()` owns PCI enablement, BAR mapping, IRQ request, descriptor pool creation, channel initialization, and dmaengine registration.

## Control Flow
PCI probe allocates controller state, enables the PCI device, requests regions, sets a 32-bit DMA mask, maps BAR 1, requests the shared IRQ, creates a descriptor DMA pool, initializes channel lists/tasklets, registers private slave dmaengine capabilities, and returns. Channel allocation checks the hardware channel is idle, preallocates `init_nr_desc_per_channel` descriptors, initializes cookies, and enables channel IRQ. `pd_prep_slave_sg()` chooses the peripheral register from `pch_dma_slave`, sets channel direction, obtains descriptors, fills hardware size/width/next fields, chains descriptors through physical addresses, and returns the first descriptor. Submission immediately starts the descriptor if no active work exists, otherwise queues it. IRQ status schedules the tasklet; the tasklet handles errors or advances/completes work, invoking callbacks and returning descriptors to the free list.

## State and Persistence
Runtime state is held in active/queued/free descriptor lists, DMA-pool allocations, channel direction, error bit, saved suspend registers, and hardware control/status registers. Suspend saves controller and channel registers; resume restores them. No disk persistence exists.

## Dependencies and Integration Points
The driver integrates with PCI IDs for Intel and ROHM devices, `linux/pch_dma.h` slave metadata, dmaengine private slave APIs, PCI BAR/IRQ management, DMA pools, and simple PM ops. Clients are expected to provide `struct pch_dma_slave` through the channel private pointer.

## Risks and Edge Cases
- `pd_tx_submit()` returns `0` and does not call `dma_cookie_assign()`, which breaks normal dmaengine cookie semantics unless this tree intentionally bypasses cookies for this legacy private driver.
- The control-register mask logic in `pdc_set_dir()`/`pdc_set_mode()` is delicate and appears to use masks in a way that can preserve or clear unintended channel bits.
- Error handling logs a bad descriptor but still calls the normal callback path rather than a result-aware error callback.
- `pd_device_terminate_all()` invokes callbacks while holding the channel lock through `pdc_chain_complete()`, which may be risky if callbacks call back into dmaengine.
- Descriptor size limits are strict and width-dependent; oversized SG entries fail at prepare time after some descriptors may have been allocated and must be returned correctly.

## Test Signals
Validation should include compilation for PCI PCH/ROHM configs, probe for each channel-count PCI id, slave SG with each supported width and boundary sizes, cookie tracking tests, shared IRQ status for channels above and below 8, terminate-all during active and queued transfers, suspend/resume register restoration, and descriptor pool exhaustion/reuse behavior.

# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_lpbfifo.c

## Purpose
`mpc512x_lpbfifo.c` is the platform driver for the MPC512x LocalPlus Bus FIFO/SCLPC block. It lets clients submit one DMA-backed transfer between RAM and a LocalPlus Bus device.

## Important APIs, Types, and Functions
The exported API is `mpc512x_lpbfifo_submit(struct mpc512x_lpbfifo_request *req)`. `mpc512x_lpbfifo_probe()` maps registers, requests DMA channel `"rx-tx"`, parses LocalPlus chip-select ranges, maps the IRQ, and requests the handler. `mpc512x_lpbfifo_kick()` validates alignment, chooses bytes-per-transaction, resolves chip select, maps RAM for DMA, configures DMA slave parameters, resets/configures FIFO registers, starts SCLPC, and submits the DMA descriptor. Completion is coordinated by `mpc512x_lpbfifo_irq()` and `mpc512x_lpbfifo_callback()`.

## Control Flow, State, and Persistence
All runtime state lives in the global `lpbfifo` struct protected by a spinlock. Only one request can be active. Writes wait for both the LPBFIFO success IRQ and DMA callback; reads skip the LPBFIFO success IRQ to avoid disabling DMA reads and complete on DMA callback.

## Dependencies and Integration Points
It depends on the DMAengine slave API, OF platform matching `"fsl,mpc512x-lpbfifo"`, LocalPlus `"ranges"` parsing from `"fsl,mpc5121-localbus"`, MPC512x SCLPC register definitions, and external request producers.

## Risks and Test Signals
Risks include singleton global state, no request queueing, strict alignment/port-size behavior, reliance on localbus ranges with zero bus base, completion races, and read-path IRQ suppression. Tests should cover write and read transfers, invalid alignment, chip-select range rejection, concurrent submit returning `-EBUSY`, DMA mapping failures, module removal during idle/active states, and hardware FIFO error interrupts.

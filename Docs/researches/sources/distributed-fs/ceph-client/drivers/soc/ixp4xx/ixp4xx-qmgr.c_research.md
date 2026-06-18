
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-qmgr.c

## Purpose
Intel IXP4xx Queue Manager driver. It initializes hardware queue SRAM/IRQ registers and exports low-level queue entry, status, IRQ, allocation, and release APIs for dependent IXP4xx drivers.

## Important APIs, Types, and Functions
- Global state includes `qmgr_regs`, two IRQ numbers, `qmgr_lock`, `used_sram_bitmap`, and per-queue IRQ handler/context arrays.
- Exported APIs: `qmgr_put_entry()`, `qmgr_get_entry()`, status helpers, `qmgr_set_irq()`, `qmgr_enable_irq()`, `qmgr_disable_irq()`, `__qmgr_request_queue()` or debug `qmgr_request_queue()`, and `qmgr_release_queue()`.
- IRQ handlers include A0-specific split handlers and generic `qmgr_irq()`.

## Control Flow
Probe maps queue manager registers, gets two IRQs, resets status/IRQ/source/SRAM registers, chooses A0 or generic IRQ handlers based on CPU revision, requests IRQs, reserves initial SRAM pages, initializes the spinlock, and logs readiness.

Queue request validates queue number, queue size, and watermarks, takes a module reference, scans the 128-page SRAM bitmap for contiguous free pages, writes queue SRAM config, records debug description if enabled, and returns. Release drains remaining entries while logging, clears SRAM config and bitmap, nulls IRQ handler, and drops the module reference. IRQ dispatch ACKs status bits and invokes registered handlers.

## State and Persistence
State is global hardware register mapping, queue SRAM allocation bitmap, IRQ callbacks, and module reference counts. Queue contents reside in hardware SRAM and are drained on release. No file persistence.

## Dependencies and Integration Points
Depends on IXP4xx queue register definitions, CPU revision helpers, platform IRQ/resources, and exported consumer APIs under `linux/soc/ixp4xx/qmgr.h`.

## Risks
- Many APIs use `BUG_ON()` for invalid queue or release state, so bad consumers can crash the kernel.
- Queue allocation uses a global bitmap and no owner identity beyond module refs; double release or forgotten release leaks hardware SRAM.
- IRQ callbacks are raw function pointers invoked in IRQ context and must be registered before enabling.
- A0 workaround handlers infer source bits and can differ from newer silicon behavior.

## Test Signals
Queue request size/watermark validation, SRAM exhaustion, release of nonempty queues, IRQ source programming for low/high queues, enable/disable ACK behavior, A0 versus generic IRQ dispatch, and module reference balance.

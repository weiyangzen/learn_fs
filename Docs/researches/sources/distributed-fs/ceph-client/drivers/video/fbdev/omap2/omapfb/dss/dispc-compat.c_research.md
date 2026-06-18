# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.c

## Purpose

`dispc-compat.c` is the legacy DISPC interrupt compatibility layer. The complete 658-line source was read. It multiplexes DISPC IRQs to registered legacy callbacks, tracks optional IRQ statistics, masks and recovers from unhandled DISPC error interrupts, and provides synchronous manager enable/disable and wait-for-IRQ helpers.

## Important APIs, Types, and Functions

`struct omap_dispc_isr_data` stores callback, argument, and mask; `struct dispc_irq_stats` stores debug counters. Global `dispc_compat` holds the IRQ lock, error mask, up to `DISPC_MAX_NR_ISRS` registered clients, pending error bits, error work, and optional stats. Exported functions include `omap_dispc_register_isr()`, `omap_dispc_unregister_isr()`, `dss_dispc_initialize_irq()`, `dss_dispc_uninitialize_irq()`, `dispc_mgr_enable_sync()`, `dispc_mgr_disable_sync()`, and `omap_dispc_wait_for_irq_interruptible_timeout()`.

## Control Flow

Initialization sets lock/stat state, builds the default error mask based on DSS features, clears stale IRQ status, initializes error work, writes IRQ enable bits, and registers a DISPC IRQ handler through `dispc_request_irq()`. The IRQ handler reads status/enable, ignores unrelated IRQs, optionally records stats, acks status, copies registered callbacks, dispatches matching callbacks outside the lock, then masks unhandled error bits and schedules `dispc_error_worker()`. The worker disables underflowing overlays, restarts managers on sync-lost with video overlays disabled, disables all managers on OCP errors, then restores the error mask.

## State and Persistence Behavior

State is volatile global kernel state. Registered ISR slots persist until unregistered. Error bits are held until the workqueue processes them. Optional stats persist until debugfs read resets them. Hardware IRQ enable state is recomputed from error mask plus client masks.

## Dependencies and Integration Points

The file depends on DISPC MMIO wrappers in `dispc.c`, runtime PM, DSS feature flags, overlay/manager lookup and enable/disable operations, debugfs registration from `core.c`, and completion/wait primitives. `apply.c` relies on the ISR registration and wait helpers for VSYNC, GO, and FRAMEDONE synchronization.

## Risks and Edge Cases

Only eight ISR clients can register, and duplicate entries are rejected by exact callback/arg/mask match. Error recovery calls high-level overlay/manager operations from a workqueue after IRQ context, which can interact with apply locks. Digit output disable falls back to VSYNC counting on older hardware without TV framedone IRQ and is explicitly not fully reliable. IRQ masks are recomputed under lock, but callbacks can unregister themselves only because the handler dispatches from a copied array.

## Test Signals

Signals include registering/unregistering duplicate and maximum ISR slots, waiting for IRQ with timeout and signal interruption, injected FIFO underflow/sync-lost/OCP error bits, debugfs IRQ statistics reset on read, LCD and DIGIT synchronous enable/disable paths, and cleanup freeing the DISPC IRQ.

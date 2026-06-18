# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi.h

## Purpose
Provides the private shared interface between OMAP SSI controller and port code.

## Important APIs, Types, and Functions
- Constants: `SSI_MAX_CHANNELS`, `SSI_MAX_GDD_LCH`, `SSI_BYTES_TO_FRAMES()`, and `SSI_WAKE_EN`.
- `struct omap_ssm_ctx` stores shadow context for SST/SSR mode, channels, frame size, timeout, arbitration, and divisor.
- `struct omap_ssi_port` owns per-port MMIO bases, DMA addresses, wake GPIO/IRQ, locks, transfer queues, error work, runtime context, and debugfs entry.
- `struct gdd_trn` binds a GDD logical channel to an active `hsi_msg` and scatterlist.
- `struct omap_ssi_controller` owns controller MMIO, clock, GDD IRQ/tasklet state, GDD transaction table, notifier, max speed, saved GDD context, and port array.
- Declares `omap_ssi_port_update_fclk()` and `ssi_port_pdriver`.

## Control Flow
This header has no executable flow, but its structures define how `omap_ssi_core.c` and `omap_ssi_port.c` coordinate GDD completions, port probing, runtime PM context restore, and clock-rate changes.

## State and Persistence
All state is volatile driver-private state. Shadow fields are used to restore hardware registers after runtime suspend or context loss; they are not persisted across driver unload.

## Dependencies and Integration Points
Depends on Linux device, platform, HSI, GPIO descriptor, IRQ, IO, module, and DMA types. It is tightly coupled to `omap_ssi_regs.h` register definitions and the HSI framework structs.

## Risks and Test Signals
Risks include mismatched assumptions about channel count, GDD logical channel ownership, and wake reference state. Test signals include runtime suspend/resume preserving SST/SSR configuration, GDD DMA completion freeing logical channels, and debugfs compiling under `CONFIG_DEBUG_FS`.

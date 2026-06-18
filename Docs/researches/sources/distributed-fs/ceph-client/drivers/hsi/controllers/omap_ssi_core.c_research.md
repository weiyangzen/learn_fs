# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_core.c

## Purpose
Implements the OMAP SSI controller platform driver, controller registration with the HSI bus, GDD DMA completion handling, controller-level runtime PM, debugfs, and clock-rate change coordination.

## Important APIs, Types, and Functions
- Platform driver `ssi_pdriver` for `ti,omap3-ssi`.
- Module init/exit register both `ssi_pdriver` and `ssi_port_pdriver`.
- `ssi_add_controller()`, `ssi_hw_init()`, `ssi_remove_controller()`, and `ssi_probe()` build the HSI controller.
- `ssi_gdd_isr()`, `ssi_gdd_tasklet()`, and `ssi_gdd_complete()` handle GDD interrupts and complete DMA-backed HSI messages.
- `ssi_clk_event()` pauses ports during functional clock changes and calls `omap_ssi_port_update_fclk()`.
- Exported `ssi_waketest()` drives a legacy wake-line test workaround used by SSI protocol.

## Control Flow
Probe counts available `ti,omap3-ssi-port` child nodes, allocates an HSI controller, maps `sys` and `gdd` resources, requests the GDD IRQ, gets the functional clock, registers a clock notifier, registers the HSI controller, enables runtime PM, resets/configures GDD, creates debugfs, and creates child platform devices for ports. GDD IRQ disables itself and schedules a high-priority tasklet. The tasklet reads pending logical channel bits, calls `ssi_gdd_complete()`, acknowledges status, and either reschedules or re-enables the IRQ. Completion unmaps DMA, releases the GDD logical channel, marks status/error, moves timeout failures to the port error queue, and re-arms the per-port PIO interrupt needed to finish the logical transfer.

## State and Persistence
Uses IDA-assigned controller IDs, saved `gdd_gcr`, cached clock rate in kHz, `max_speed`, and optional context loss counter. Runtime suspend captures context-loss state; resume restores GDD control if needed. State is volatile and reinitialized on probe.

## Dependencies and Integration Points
Integrates HSI core allocation/registration, OF platform children, common clock notifiers, pm_runtime, IRQ/tasklets, DMA mapping, debugfs, and OMAP SSI registers. It coordinates with port code through `struct omap_ssi_controller` and `omap_ssi_port_update_fclk()`.

## Risks and Test Signals
Risks include IRQ/tasklet races on teardown, clock notifier disabling invalid wake IRQs, runtime PM imbalance on GDD error paths, and context restore gaps because `get_loss` is currently NULL. Test signals include probing with multiple ports, GDD DMA timeout recovery, clock-rate transition under traffic, runtime suspend/resume, debugfs register reads, and clean module unload.

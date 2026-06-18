# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mmp-driver.c

## Purpose
This file is the platform-device wrapper for Marvell MMP/Armada 610 camera controllers. It supplies MMP-specific clock handling, MIPI D-PHY calculation, OF sensor discovery, IRQ routing, runtime/system PM, and core registration around the shared MCAM V4L2 implementation.

## Important APIs, Types, And Functions
`struct mmp_camera` contains the platform device, embedded `mcam_camera`, list node, MIPI clock, and IRQ number. `mmpcam_calc_dphy()` computes CSI2 D-PHY register values from platform data and the MIPI clock. `mmpcam_irq()` reads `REG_IRQSTAT` and forwards it to `mccic_irq()`. `mcam_init_clk()` obtains the core clocks named `axi`, `func`, and `phy`. Lifecycle and PM are handled by `mmpcam_probe()`, `mmpcam_remove()`, `mmpcam_runtime_resume()`, `mmpcam_runtime_suspend()`, `mmpcam_suspend()`, and `mmpcam_resume()`.

## Control Flow
Probe allocates `mmp_camera`, initializes the embedded `mcam_camera`, copies platform data for clock source/divider, bus type, D-PHY values, and lane count when available, or falls back to historical parallel-bus defaults. For CSI2 it obtains the `mipi` clock unless an existing DPHY6 value makes it unnecessary. It sets chip ID `MCAM_ARMADA610`, default buffer mode `B_DMA_sg`, bus info, register mapping, and common clocks. It registers the V4L2 device, finds the first OF graph endpoint, creates a V4L2 async notifier connection to the remote sensor, calls `mccic_register()`, adds an OF clock provider for the sensor master clock, requests the shared IRQ, and enables runtime PM.

The IRQ handler holds `mcam.dev_lock`, reads pending CCIC interrupts, and lets the core process frame state. Runtime resume enables the three optional clocks in order; runtime suspend disables them in reverse. System suspend/resume delegates to `mccic_suspend()` / `mccic_resume()` when runtime PM has not already suspended the device.

## State And Persistence
Most capture state is in the embedded core object. Wrapper state includes obtained clocks, MIPI clock, IRQ number, platform D-PHY data, and runtime PM status. D-PHY registers are recalculated on MIPI enable through the core callback. No persistent storage exists.

## Dependencies And Integration Points
The wrapper depends on OF graph endpoints, platform resources, runtime PM, common clock framework, optional board platform data from `mmp-camera.h`, and `mcam-core.h`. It integrates with the core through the `calc_dphy` callback, bus/MIPI fields, clocks, IRQ forwarding, and `mccic_*` lifecycle API.

## Risks
The code assumes valid platform data for CSI2 paths: `mcam->dphy` is dereferenced when checking `mcam->dphy[2]`, so missing platform data for a CSI2 configuration would be dangerous unless DT never sets that path without pdata. Optional clocks are stored even when `devm_clk_get()` fails; PM paths must keep guarding `IS_ERR()`. `of_clk_add_provider()` is not explicitly removed in remove, which should be checked against devres/OF clock provider expectations. Error unwind after adding the clock provider and before PM enable calls `mccic_shutdown()` but does not appear to undo the provider.

## Test Signals
Build with `COMPILE_TEST` and on MMP configs. Runtime tests should cover probe with parallel bus DT, CSI2 platform data, missing optional clocks, absent endpoint, IRQ frame forwarding, runtime PM clock ordering, system suspend/resume while streaming, and MIPI lane/DPHY calculation. Device tree validation should check `clock-output-names`, graph endpoint, and clock names.

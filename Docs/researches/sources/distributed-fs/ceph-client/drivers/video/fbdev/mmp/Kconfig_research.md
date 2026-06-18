# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Kconfig

## Purpose
Defines the top-level Kconfig entry for the Marvell MMP display subsystem and includes submenus for hardware controller, panel, and framebuffer components.

## Important APIs, Types, and Functions
- `menuconfig MMP_DISP` is a tristate option depending on `CPU_PXA910 || CPU_MMP2 || COMPILE_TEST`.
- Includes `mmp/hw/Kconfig`, `mmp/panel/Kconfig`, and `mmp/fb/Kconfig` only when `MMP_DISP` is enabled.

## Control Flow
Kconfig exposes the subsystem root option and conditionally exposes subordinate options inside the `if MMP_DISP` block.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Controls build visibility for MMP display controller, panel, and fbdev drivers.

## Risks
Because component configs are nested under `MMP_DISP`, enabling a framebuffer or panel alone is impossible without the framework root. `COMPILE_TEST` broadens build coverage to non-target architectures but does not make hardware runnable.

## Test Signals
Run Kconfig/build combinations for target CPUs and `COMPILE_TEST`, verifying all nested configs appear only under `MMP_DISP`.

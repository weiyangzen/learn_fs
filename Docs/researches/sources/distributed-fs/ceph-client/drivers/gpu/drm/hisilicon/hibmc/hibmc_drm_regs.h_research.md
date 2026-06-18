# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_regs.h

Purpose: defines the HIBMC non-DP MMIO register map for power, gates, PLLs, CRT scanout/timing, panel/VGA controls, vblank interrupts, palette, and field packing.

Important APIs/types: macros cover power mode and current-gate registers, PLL field builders and fixed PLL magic values, display control/DPMS/format/timing bits, framebuffer address/width/pitch, horizontal and vertical timing registers, auto-centering registers, panel control, vblank raw interrupt/enable, and `HIBMC_FIELD()`.

Control flow: no executable flow, but the definitions are used throughout `hibmc_drm_drv.c`, `hibmc_drm_de.c`, and `hibmc_drm_vdac.c` to program device state.

State and persistence: values written through these definitions persist in device registers until changed, reset, or power-gated. No software storage is declared.

Dependencies and integration points: used by the HIBMC display engine and top-level driver. It assumes register values and masks match HIBMC hardware documentation.

Risks: magic PLL constants and field masks are high-risk hardware contract points. `HIBMC_FIELD()` assumes field macros have matching `_MASK` macros and can silently mask bad values. Resolution support is constrained by tabled PLL values in `hibmc_drm_de.c`.

Test signals: mode timing correctness, supported resolution PLL programming, vblank IRQ enable/ack, framebuffer pitch/address display, power-gate transitions, and palette/gamma output.

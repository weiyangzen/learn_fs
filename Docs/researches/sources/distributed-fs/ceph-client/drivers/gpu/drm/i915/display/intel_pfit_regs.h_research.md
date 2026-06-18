# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit_regs.h

Purpose: register definitions for legacy GMCH panel fitter and CPU/PCH panel fitter windows, controls, scaling ratios, and filter fields.

Important definitions: `PFIT_CONTROL`, `PFIT_ENABLE`, pipe/scaling/filter/interpolation/auto-scale/dither fields; `PFIT_PGM_RATIOS` and `PFIT_AUTO_RATIOS`; `PF_CTL`, `PF_WIN_SZ`, `PF_WIN_POS`, `PF_VSCALE`, and `PF_HSCALE` with size/position/filter/pipe-select fields.

Control flow/state: no executable logic. These macros are used by pfit compute/program/readout code and overlay pfit compensation.

Dependencies/integration: depends on `intel_display_reg_defs.h` MMIO and bitfield helpers. Integrated by `intel_pfit.c`, overlay, LVDS, and display readout paths.

Risks/test signals: wrong masks or register offsets cause broken scaling or readout. Note `PF_FILTER_EDGE_ENHANCE/SOFTEN` reference `PF_FILTER_EDGE_MASK`, which is not defined in this header and should be checked by compile coverage. Hardware tests should verify programmed pfit windows and scaling ratios.

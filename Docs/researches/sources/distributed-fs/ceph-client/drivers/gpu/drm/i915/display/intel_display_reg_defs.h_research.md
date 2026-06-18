# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reg_defs.h

Purpose: provides display-register address helper macros layered on top of generic i915 register definitions. It gives display code concise, typed helpers for pipe, plane, transcoder, port, PLL, PHY, and device-info-offset-based MMIO register selection.

Important APIs, types, and functions: `VLV_DISPLAY_BASE` defines the Valleyview display MMIO base. `_PIPE()`, `_PLANE()`, `_TRANS()`, `_PORT()`, `_PLL()`, and `_PHY()` wrap `_PICK_EVEN()` for evenly spaced register instances. `_MMIO_PIPE()`, `_MMIO_PLANE()`, `_MMIO_TRANS()`, `_MMIO_PORT()`, `_MMIO_PLL()`, and `_MMIO_PHY()` convert those offsets to `i915_reg_t`. `_MMIO_BASE_PIPE3()` and `_MMIO_BASE_PORT3()` support two-range offset layouts. `_MMIO_PIPE2()`, `_MMIO_TRANS2()`, and `_MMIO_CURSOR2()` use per-device offset arrays from display device info.

Control flow: register definition headers include these macros to define symbolic registers. Runtime code passes pipe/transcoder/port/etc. indexes and receives an MMIO register token suitable for `intel_de_read()`, `intel_de_write()`, and `intel_de_rmw()`.

State and persistence: no runtime state is stored. The macros encode address arithmetic, with dynamic offsets coming from `INTEL_DISPLAY_DEVICE_*_OFFSET(display)` accessors when using the `*2` helpers.

Dependencies and integration points: depends on `i915_reg_defs.h` for `_MMIO`, `_PICK_EVEN`, and `_PICK_EVEN_2RANGES`. Integrated across display register headers and all display MMIO code, including the power-management files in this work item.

Risks: incorrect helper selection yields wrong MMIO offsets, which can silently program the wrong pipe/port/PHY register. The `*2` helpers require valid display device-info offset tables. `_MMIO_BASE_PIPE3()` and `_MMIO_BASE_PORT3()` parameter naming is generic and should be reviewed carefully when used for non-pipe selectors.

Test signals: compile-time register definitions catch syntax/type issues, but functional validation comes from platform MMIO read/write behavior, register trace review, and hardware tests that exercise multiple pipes, ports, transcoders, PLLs, and PHYs.

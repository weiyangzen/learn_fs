# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.c

## Purpose

`rcar_cmm.c` implements the Renesas R-Car Color Management Module driver used by R-Car DU CRTCs for gamma/LUT programming. It probes standalone CMM platform devices, maps registers, manages runtime PM, and exports setup/enable/disable/init functions to the DU driver.

## Important APIs, Types, and Functions

- `struct rcar_cmm` stores MMIO base and 1D LUT enabled state.
- `rcar_cmm_lut_write()` converts 16-bit DRM LUT entries to 8-bit hardware RGB fields and writes all `CM2_LUT_SIZE` entries.
- `rcar_cmm_setup()` enables/disables the LUT and writes table entries from `struct rcar_cmm_config`.
- `rcar_cmm_enable()` performs `pm_runtime_resume_and_get()`.
- `rcar_cmm_disable()` disables LUT state and calls `pm_runtime_put()`.
- `rcar_cmm_init()` validates that the CMM platform device has probed by checking driver data.
- `rcar_cmm_probe()` allocates state, maps the MMIO resource, and enables runtime PM.
- `rcar_cmm_remove()` disables runtime PM.

## Control Flow

The platform driver probes CMM nodes matching Gen2/Gen3 compatibles. The DU driver later finds CMM devices from `renesas,cmms`, calls `rcar_cmm_init()`, links device PM ordering, then calls `rcar_cmm_enable()` before a CRTC starts and `rcar_cmm_setup()` during atomic color-management updates. Disable clears LUT control and drops runtime PM.

## State and Persistence Behavior

Persistent driver state is `struct rcar_cmm` in platform driver data. LUT enabled state is cached to avoid redundant control writes. Hardware LUT table contents persist while powered, but `rcar_cmm_disable()` documents that internal processing state is lost and must be restored after the next enable.

## Dependencies and Integration Points

- Uses Linux platform, IO, OF, module, and runtime PM APIs.
- Uses DRM color-management helpers for LUT extraction.
- Exports symbols consumed by `rcar_du_crtc.c` and `rcar_du_kms.c`.

## Risks and Edge Cases

- `rcar_cmm_setup()` assumes the unit is powered and clocked; calling it without `rcar_cmm_enable()` can access suspended hardware.
- LUT updates are not double-buffered, so changing entries while scanning out can affect the current frame.
- Enable/disable calls are explicitly not reference-counted; unbalanced calls can mis-handle runtime PM and cached LUT state.
- `rcar_cmm_init()` returns `-EPROBE_DEFER` until probe sets drvdata; caller must propagate deferral.

## Test Signals

- Probe tests should validate MMIO mapping, runtime PM enable, and OF matching for Gen2/Gen3 compatibles.
- Atomic gamma tests should cover exactly 256-entry LUTs, NULL LUT disable, enable/setup/disable cycles, and suspend/resume ordering with DU.
- Visual tests should verify LUT colors and watch for tearing/artifacts during live LUT updates.

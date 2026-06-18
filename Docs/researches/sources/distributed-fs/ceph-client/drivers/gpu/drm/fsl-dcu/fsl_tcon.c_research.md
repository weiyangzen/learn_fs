<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.c

## Purpose

This file implements optional Freescale TCON support used by the DCU driver. Its only runtime display operation is enabling or disabling TCON bypass mode so the DCU can drive a parallel RGB/LVDS encoder path.

## Important APIs, Types, And Functions

Exported functions are `fsl_tcon_init()`, `fsl_tcon_free()`, `fsl_tcon_bypass_enable()`, and `fsl_tcon_bypass_disable()`. Internal helper `fsl_tcon_init_regmap()` maps the phandle resource and creates a named MMIO regmap. The file defines a 32-bit regmap config named `"tcon"`.

## Control Flow

`fsl_tcon_init()` parses the optional `fsl,tcon` phandle from the DCU node. If missing, it returns `NULL` and the main driver continues without TCON. If present, it allocates `struct fsl_tcon`, maps the resource, creates a regmap, obtains the `ipg` clock, enables it, drops the node reference, logs bypass usage, and returns the object. Bypass helpers update `FSL_TCON_CTRL1_TCON_BYPASS` in `FSL_TCON_CTRL1`. `fsl_tcon_free()` disables and releases the clock.

## State And Persistence

The `struct fsl_tcon` stores regmap and IPG clock. TCON bypass is persistent hardware state while the TCON clock/register block is powered. The allocation and regmap mapping are devm-managed; the explicit free helper only handles the non-devm clock reference path.

## Dependencies And Integration Points

It depends on OF address/resource parsing, clk, regmap MMIO, and local `fsl_tcon.h`. The FSL DCU probe calls `fsl_tcon_init()`, encoder creation and resume call bypass enable, and output operation depends on bypass being set for simple RGB/LVDS routing.

## Risks And Test Signals

Risks include returning `NULL` for both absent and failed TCON init, which lets the main driver continue after mapping/clock errors; no explicit call to `fsl_tcon_free()` in the shown DCU remove path; and clock lifetime asymmetry because `of_clk_get_by_name()` is not devm-managed. Test signals are DT with no TCON, DT with valid TCON, invalid TCON resource, missing `ipg` clock, bypass bit readback, and suspend/resume with TCON present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.c -->

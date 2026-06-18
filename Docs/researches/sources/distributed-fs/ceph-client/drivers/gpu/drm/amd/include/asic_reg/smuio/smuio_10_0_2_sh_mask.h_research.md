# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_sh_mask.h

## Purpose
`smuio_10_0_2_sh_mask.h` defines bit masks and shift counts for the SMUIO 10.0.2 registers listed in the companion offset header. It lets driver code decode identity, pinstrap, scratch, reset, GFX power, TSC, virtual reset, display timer, interrupt, and SVI telemetry fields without hard-coded bit arithmetic.

## Important APIs, Types, And Functions
The API is a macro namespace guarded by `_smuio_10_0_2_SH_MASK_HEADER` via `#ifndef`. It defines `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pairs. Important groups are `SMUIO_MCM_CONFIG` fields for die/package/socket/console IDs; `IP_DISCOVERY_VERSION`; `IO_SMUIO_PINSTRAP` audio strap fields; `SCRATCH_REGISTER0` through `SCRATCH_REGISTER7` full-width scratch pads; `SMUIO_MP_RESET_INTR`; `SMUIO_SOC_HALT` watchdog force controls; `SMUIO_GFX_MISC_CNTL` GFX cold/GFXOFF/RLC clock-gating controls and status; `PWROK_REFCLK_GAP_CYCLES` and `GOLDEN_TSC_*`/shadow fields; `SOC_GAP_PWROK`; `PWR_VIRT_RESET_REQ` VF/PF FLR request bits; `PWR_DISP_TIMER_CONTROL`, `PWR_DISP_TIMER2_CONTROL`, and `PWR_DISP_TIMER_GLOBAL_CONTROL`; `PWR_IH_CONTROL`; and `SMUSVI0_TEL_PLANE0`/`SMUSVI0_PLANE0_CURRENTVID` telemetry fields.

## Control Flow
There is no runtime branch or call flow in the header. At runtime, callers read a register at an offset from `smuio_10_0_2_offset.h`, apply the relevant mask, shift down to extract a logical field, or shift/mask an input value before writing. Control-like hardware workflows represented here include FLR request signaling through `PWR_VIRT_RESET_REQ`, display timer interrupt enable/disable/mask/status-ack programming, power interrupt-handler credit and trigger masking, watchdog halt forcing, and GFXOFF/RLC clock-gating control.

## State And Persistence
The header has no storage. It describes hardware fields whose values may represent strap state, scratch state, reset requests, watchdog force bits, timer configuration, interrupt status/acknowledge state, TSC counters, GFX power state, and SVI voltage/current telemetry. Scratch registers and programmed timer/control fields are stateful hardware registers; status and telemetry fields are read-only or hardware-updated depending on the block.

## Dependencies And Integration Points
This file is designed to be used with `smuio_10_0_2_offset.h` and AMDGPU field helpers/register accessors. It integrates with SMUIO identity discovery, reset/FLR code, GFXOFF/power-management paths, display timer interrupt handling, interrupt-handler throttling/credit code, TSC synchronization, and voltage telemetry consumers. The field names mirror generated hardware documentation, so consistency with firmware and register database generation is the main dependency.

## Risks
Mask/shift errors can corrupt unrelated bits or decode telemetry and status incorrectly. Whole-register scratch and discovery masks are straightforward, but control fields that acknowledge interrupts or request FLR/reset must be used carefully because write-one-to-ack or write-trigger semantics may apply in hardware even though the header does not encode access type. The `_MASK_MASK` names such as `PWR_DISP_TIMER_CONTROL__DISP_TIMER_INT_MASK_MASK` and `PWR_IH_CONTROL__DISP_TIMER_TRIGGER_MASK_MASK` are easy to misread. Like the offset header, this file has an `#ifndef` guard but does not define the guard symbol, so repeated inclusion is not actually suppressed.

## Test Signals
Build coverage catches syntax and duplicate-definition issues. Runtime signals include correct MCM/package decode, audio pinstrap interpretation, reliable scratch register round trips if used by diagnostics, clean VF/PF FLR request behavior, GFXOFF status transitions, display timer interrupts with proper ack/mask behavior, stable golden TSC readings, and plausible SVI0 current/VID telemetry. Hardware register tracing or debugfs reads around the corresponding amdgpu paths are useful validation points.

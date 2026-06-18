<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_regs.h

## Purpose
This header defines the DVO port and source-dimension MMIO registers and bitfields for legacy DVO outputs.

## Important APIs, Types, and Functions
Key macros are `_DVOA`, `_DVOB`, `_DVOC`, `DVO(port)`, `_DVOA_SRCDIM`, `_DVOB_SRCDIM`, `_DVOC_SRCDIM`, and `DVO_SRCDIM(port)`. Bitfields cover enable, pipe select, pipe stall modes, interrupt selection, preserve bits, VGA sync use, data ordering, sync disable/tristate, border, active data order, sync polarity, blank polarity, output C-state/source-size behavior, and source horizontal/vertical dimensions.

## Control Flow
There is no local flow. `intel_dvo.c` reads `DVO(port)` for hardware state and writes `DVO_SRCDIM()` plus `DVO()` during pre-enable/enable/disable.

## State and Persistence Behavior
The macros map persistent hardware registers. Some bits are preserved across programming because the driver does not know the correct active data ordering for all hardware.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` and is consumed by legacy DVO encoder code. It must match older display hardware register layouts.

## Risks
Pipe select is a single bit and only suitable for the hardware generations this DVO code targets. Incorrect preserve masks or data-order bits can produce swapped colors or broken sync. Source dimensions must match adjusted mode programming.

## Test Signals
Signals include correct MMIO programming in DVO pre-enable, readout returning the selected pipe, visible sync polarity correctness, and register dump comparisons on supported legacy systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_regs.h -->

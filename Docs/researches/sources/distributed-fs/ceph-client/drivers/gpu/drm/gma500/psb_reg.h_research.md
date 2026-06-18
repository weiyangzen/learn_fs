
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_reg.h

## Purpose
`psb_reg.h` defines Poulsbo/SGX graphics-core and 2D blitter register offsets, event bits, BIF fault fields, 2D command block encodings, ROP constants, scene/scheduler constants, and power-management register masks used by the GMA500 driver.

## Important APIs, Types, And Functions
The header is macro-only. Important SGX/core registers include `PSB_CR_CLKGATECTL`, `PSB_CR_CORE_ID`, `PSB_CR_CORE_REVISION`, `PSB_CR_SOFT_RESET`, `PSB_CR_EVENT_HOST_ENABLE`, `PSB_CR_EVENT_STATUS`, `PSB_CR_EVENT_HOST_CLEAR`, their second-register variants, BIF registers such as `PSB_CR_BIF_CTRL`, `PSB_CR_BIF_INT_STAT`, `PSB_CR_BIF_FAULT`, and 2D status/control registers such as `PSB_CR_2D_SOCIF` and `PSB_CR_2D_BLIT_STATUS`.

The 2D command definitions include block headers like `PSB_2D_CLIP_BH`, `PSB_2D_CTRL_BH`, `PSB_2D_BLIT_BH`, source/destination/pattern/mask surface blocks, clip and stride/address masks, alpha and color-key controls, rotation/copy-order flags, and ROP constants such as `PSB_2D_ROP3_SRCCOPY`. Power constants include PUNIT/APM registers and masks for video, display, and graphics power gating.

## Control Flow
The header has no executable code. Consumers compose GPU command buffers or register writes using the constants, and interrupt handling reads/writes event status and clear registers using these bit definitions.

## State And Persistence
The definitions describe persistent GPU hardware state: clock gating, core reset, event enables/status, BIF page-fault status and fault address, USE/PDS code base addresses, 2D blitter command state, scene memory cookies, and power-gating status. The header stores no C state.

## Dependencies And Integration Points
`psb_irq.c` uses the SGX event and BIF fault constants to enable, decode, log, and clear SGX interrupts. Other GMA500 acceleration and power-management files use the 2D command and PUNIT definitions. It complements `psb_intel_reg.h`, which covers display-side registers.

## Risks
The register and command encodings are low-level and mostly untyped, so incorrect shifts or masks can corrupt command streams or acknowledge the wrong interrupt. Many addresses are specific to the Poulsbo/SGX block and should not be applied to unrelated GMA500 display generations. Fault interpretation in IRQ code depends on these bit meanings matching the hardware revision.

## Test Signals
Validation includes SGX interrupt enable/clear behavior, correct BIF fault reason and address logging, 2D blit command completion interrupts, successful accelerated copy/fill paths where present, no unexpected GPU resets after clock-gating/power changes, and clean suspend/resume of power-gated display and graphics blocks.

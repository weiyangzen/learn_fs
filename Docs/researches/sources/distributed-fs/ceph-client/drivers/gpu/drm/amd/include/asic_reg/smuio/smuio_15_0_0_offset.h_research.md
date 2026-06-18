# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_0_offset.h

## Purpose

`smuio_15_0_0_offset.h` is the generated SMUIO 15.0.0 register offset map. It exports `reg...` register address constants and matching `reg..._BASE_IDX` constants for AMDGPU SOC15 register helpers. It contains no functions, types, storage, or runtime control flow. The matching `smuio_15_0_0_sh_mask.h` supplies field positions and masks for the registers named here.

This SMUIO 15.0.0 offset file is smaller than the 14.0.2 and 15.0.8 maps. It covers misc, reset, TSC, and software timer blocks only. In the local source tree, `amdgpu/smuio_v15_0_0.c` includes this file and uses the TSC count offsets to implement `get_gpu_clock_counter`.

## Important APIs, types, and macros

The exported API is a list of `#define` constants. The suffixless `reg*` macros provide register offsets suitable for `SOC15_REG_OFFSET(SMUIO, instance, regNAME)` and `RREG32_SOC15(SMUIO, instance, regNAME)`. The `_BASE_IDX` constants select the generated base index for the address block. Most entries in this file use base index 1 for misc/TSC/swtimer registers, except `regSMUIO_MCM_CONFIG` and `regSMUIO_GFX_MISC_CNTL`, which use base index 0.

The misc block has base address comment `0x5a000` and defines `SMUIO_MCM_CONFIG`, `IP_DISCOVERY_VERSION`, eight scratch registers, and `IO_SMUIO_PINSTRAP`. Scratch register offsets run consecutively from `0x01c6` through `0x01cd`, with pinstrap at `0x01ce`.

The reset block has base address comment `0x5a300` and defines only `SMUIO_GFX_MISC_CNTL` at offset `0x00c5`. The companion mask header gives this register fields for GFX cold-vs-gfxoff and GFXOFF status.

The TSC block has base address comment `0x5a8a0` and defines `PWROK_REFCLK_GAP_CYCLES`, golden TSC increment upper/lower, golden TSC count upper/lower, SOC golden TSC shadow upper/lower, and `SOC_GAP_PWROK`. These are the direct inputs for the 64-bit counter read in `smuio_v15_0_0_get_gpu_clock_counter()`.

The software timer block has base address comment `0x5aca8` and defines `PWR_VIRT_RESET_REQ`, display timer 1 and 2 control/debug/elapsed-control registers, global timer control, and `PWR_IH_CONTROL`. Compared with 14.0.2-style timer masks, 15.0.0 adds elapsed-control offsets for both display timers.

## Control flow

The file has no branches or executable operations. It affects control flow only when compiled into AMDGPU register-access paths. The concrete local consumer, `smuio_v15_0_0_get_gpu_clock_counter()`, reads `regGOLDEN_TSC_COUNT_UPPER`, `regGOLDEN_TSC_COUNT_LOWER`, and the upper half again under `preempt_disable()` to avoid returning a torn clock value if the low half rolls between reads.

## State and persistence behavior

All represented state lives in SMUIO hardware registers. Misc registers expose platform identity, IP discovery, scratchpad persistence, and strap state. `SMUIO_GFX_MISC_CNTL` exposes reset/power-state status and control-like bits for GFXOFF handling. TSC registers expose live timebase count/increment/shadow state. Software timer registers expose FLR request, timer interrupt count/config/status/elapsed state, pulse shape, and interrupt-handler credit/trigger control.

The header itself persists nothing and cannot enforce read/write semantics. Consumers must respect whether a register is read-only identity, writable scratch/config, command-like, status, sticky, or acknowledge-on-write. Offset correctness is essential because the same `regNAME` is passed to generic SOC15 helpers that compute final MMIO addresses from the IP block, instance, base index, and offset.

## Dependencies and integration points

This header depends on the generated SMUIO 15.0.0 mask/default headers and AMDGPU SOC15 register helper infrastructure. It is integrated by `amdgpu/smuio_v15_0_0.c` through `#include "smuio/smuio_15_0_0_offset.h"` and by any other SMUIO 15.0.0 code that reads package, TSC, reset, scratch, or timer registers.

The offset definitions are part of the ABI between the driver and the hardware register database. They also integrate with IP discovery: `IP_DISCOVERY_VERSION` can be read to validate discovered IP versions, while base-index values tell SOC15 helper macros which generated base address slot should be used.

## Risks

Wrong offsets or base indices can direct reads and writes to the wrong SMUIO register, which is worse than a wrong field mask because it can corrupt unrelated hardware state. Base-index drift is a specific risk: `SMUIO_MCM_CONFIG` uses base index 0 while many neighboring misc entries use base index 1, so assuming one base index for the whole commented block would be incorrect.

The TSC count registers are order-sensitive in consumers. If the upper/lower offsets are swapped or stale, clock readings can jump, repeat, or appear non-monotonic. The timer offset sequence differs from 15.0.8, where timer 2 and global/IH offsets shift because elapsed-control registers are absent; mixing 15.0.0 and 15.0.8 offset/mask sets would decode or program the wrong timer registers. The reset block has a single register, so a missing include or wrong ASIC match might compile but silently skip expected GFXOFF behavior.

## Test signals

Build coverage should include `amdgpu/smuio_v15_0_0.c` and any table that attaches `smuio_v15_0_0_funcs` to ASIC discovery. Runtime validation should check monotonic GPU clock counter values, correct high/low rollover handling, successful reads of IP discovery and scratch registers, and expected `SMUIO_GFX_MISC_CNTL` status on supported hardware.

Register database validation should compare every `reg...` value and `_BASE_IDX` against the authoritative SMUIO 15.0.0 specification. Hardware timer validation should verify display timer interrupts, elapsed-control behavior, and `PWR_IH_CONTROL` trigger/credit handling if those paths are enabled. A negative test signal is any compile error in `REG_GET_FIELD` or `RREG32_SOC15` consumers after changing names, because these generated names are used directly rather than through wrapper functions.

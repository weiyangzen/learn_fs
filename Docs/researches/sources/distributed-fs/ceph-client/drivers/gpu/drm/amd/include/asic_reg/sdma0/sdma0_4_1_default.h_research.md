# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_1_default.h

## Purpose
`sdma0_4_1_default.h` is the generated default-value header for the SDMA0 4.1 register block. It records reset or baseline values for the SDMA0 4.1 hardware revision and is intended to be used with the matching 4.1 offset map and compatible shift/mask definitions when initializing or validating SDMA state.

## Important APIs, Types, and Functions
There are no callable APIs or types. The file exposes 216 `_DEFAULT` macros. The macro surface covers SDMA microcode, VM context, public/context register classification, MMHUB, power/clock/control, GB address config, status, EDC, atomics, UTCL1, relaxed ordering, physical address, perf, trust/IOV, ULV, EA double-bit address registers, and queue defaults for GFX, RLC0, and RLC1. Compared with the 4.0 default header, this 4.1 file omits `mmSDMA0_VF_ENABLE_DEFAULT`, `mmSDMA0_PHASE2_QUANTUM_DEFAULT`, and the entire `mmSDMA0_PAGE_*_DEFAULT` queue block. It also updates revision-sensitive defaults such as `mmSDMA0_VERSION_DEFAULT` to `0x00000401`, `mmSDMA0_POWER_CNTL_DEFAULT` to `0x4003c050`, and `mmSDMA0_PUB_REG_TYPE2_DEFAULT` to `0x0fc66880`.

## Control Flow and State
The header has no executable logic. Its control significance comes from revision selection: including this file tells the rest of the driver that the SDMA0 instance follows the 4.1 default register contract. Hardware state described here includes initial queue disabled state, default context status values, write-pointer polling defaults, address-zero defaults, UTCL1 watermark/status defaults, and power-management defaults.

## Persistence and Dependencies
The macros persist as compiled constants in whatever ASIC table or init path includes them. The file depends on `sdma0_4_1_offset.h` for register locations and on compatible field definitions, typically the SDMA 4.x shift/mask contract. It integrates with AMDGPU SDMA setup, firmware loading, ring bring-up, GPU reset, power management, and diagnostic register dumps.

## Integration Points, Risks, and Test Signals
Main risks are revision mixups and silent generated-value drift. If 4.0 defaults are applied to 4.1 hardware, code may assume a PAGE queue or `PHASE2_QUANTUM` register that the 4.1 offset/default headers do not define. If 4.1 defaults are applied to 4.0 hardware, SDMA power and public-register type defaults may not match expected reset behavior. Test signals include successful SDMA engine discovery reporting version 4.1, ring tests for GFX/RLC0/RLC1 only, no attempts to program missing PAGE queue defaults, firmware load and queue scheduling success, stable suspend/resume with the 4.1 power default, and clean register-dump diffs against SDMA 4.1 hardware.

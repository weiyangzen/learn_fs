# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_default.h

### Purpose

`sdma1_4_0_default.h` is a generated AMDGPU register default-value header for the SDMA1 engine in the SDMA 4.0 register block. It does not implement executable logic; it publishes reset or expected default 32-bit values as `#define` constants named `mmSDMA1_*_DEFAULT`. Driver code and diagnostic code can use these constants together with the matching offset and shift/mask headers to initialize, compare, dump, or document SDMA1 hardware state.

The file covers the `sdma1_sdma1dec` address block and defines 255 register defaults: 86 core SDMA1 defaults, 43 GFX queue defaults, 42 PAGE queue defaults, and 84 RLC queue defaults for RLC0 and RLC1. The family mirrors `sdma1_4_0_offset.h`, so each default macro is meaningful only when paired with the matching SDMA 4.0 register address map.

### Important APIs, types, and functions

There are no C types or functions. The public API is the preprocessor surface:

- Include guard `_sdma1_4_0_DEFAULT_HEADER`.
- One macro per defaulted register, for example `mmSDMA1_CNTL_DEFAULT`, `mmSDMA1_STATUS_REG_DEFAULT`, `mmSDMA1_UTCL1_CNTL_DEFAULT`, `mmSDMA1_GFX_RB_CNTL_DEFAULT`, `mmSDMA1_PAGE_RB_CNTL_DEFAULT`, `mmSDMA1_RLC0_RB_CNTL_DEFAULT`, and `mmSDMA1_RLC1_RB_CNTL_DEFAULT`.
- Register classification defaults such as `mmSDMA1_CONTEXT_REG_TYPE0_DEFAULT` through `TYPE3` and `mmSDMA1_PUB_REG_TYPE0_DEFAULT` through `TYPE3`, which encode hardware-visible register grouping bitmaps.

The constants are raw literal values. Callers are expected to use the companion `sdma1_4_0_sh_mask.h` field definitions if they need to interpret or modify individual bits.

### Control flow

The header has no runtime control flow. Its compile-time flow is linear: copyright/license, include guard, generated macro list, and closing `#endif`. Runtime behavior emerges only in consumers that select a register offset, read or write the hardware register, and compare or compose values with these defaults.

### State and persistence behavior

The header itself owns no mutable state and persists nothing. It describes hardware reset/default state for SDMA1 registers. Several defaults are operationally important because they seed expected state for persistent GPU engine programming:

- Queue ring controls such as `GFX_RB_CNTL`, `PAGE_RB_CNTL`, `RLC0_RB_CNTL`, and `RLC1_RB_CNTL` default to `0x00040000`, matching the `RPTR_WRITEBACK_TIMER` field placement in the shift/mask header.
- Most base addresses, read/write pointers, indirect buffer registers, CSA addresses, and doorbell offsets default to zero, which is the expected unprogrammed state before queue setup.
- `mmSDMA1_CNTL_DEFAULT` is `0x00000002`, meaning the default is not an all-zero control register.
- Status and configuration defaults such as `STATUS_REG`, `STATUS1_REG`, `UTCL1_*`, `BA_THRESHOLD`, `RELAX_ORDERING_LUT`, `PERFMON_CNTL`, and `CRD_CNTL` document non-zero hardware reset state that debug tooling should not treat as driver-written state.

### Dependencies

This file depends only on the C preprocessor. Semantically, it depends on the generated SDMA 4.0 SDMA1 register model:

- `sdma1_4_0_offset.h` supplies the matching register offsets.
- `sdma1_4_0_sh_mask.h` supplies bit positions and masks for interpreting values.
- Sibling SDMA0 headers must remain consistent where driver code derives SDMA1 addresses from SDMA0 address arithmetic.

### Integration points

The directly observed AMDGPU include users in this tree are mostly offset and mask consumers, but this default header belongs to the same generated hardware interface set used by SOC15/GFX9 SDMA setup. `soc15.c` includes `sdma1_4_0_offset.h`, and `amdgpu_amdkfd_gfx_v9.c` includes the SDMA1 4.0 offset and shift/mask headers for KFD SDMA queue programming. The defaults are suitable for register dump baselines, reset validation, and bring-up comparisons in the same SDMA1 block.

### Risks

- The defaults must not be mixed with a different SDMA generation. SDMA 4.2.2 moves some queue windows and expands RLC queues, so an apparently valid `mmSDMA1_*_DEFAULT` name can describe the wrong hardware if paired with the wrong offset header.
- Non-zero defaults can be misread as driver configuration. Test and debug code should distinguish reset state from values programmed during ring setup.
- Register classification defaults (`CONTEXT_REG_TYPE*`, `PUB_REG_TYPE*`) are compact bitmaps. A stale bitmap can break save/restore, virtualization exposure, or register-access policy even though no C compiler error appears.
- Because these are generated constants, local manual edits are high risk. The source of truth is normally an ASIC register database, not handwritten kernel code.

### Test signals

Useful validation signals are compile-time and hardware-facing:

- Kernel build of AMDGPU/KFD translation units that include the matching SDMA1 4.0 headers.
- Static comparison that every `mmSDMA1_*_DEFAULT` has a matching `mmSDMA1_*` offset in `sdma1_4_0_offset.h`.
- Register dump checks on GFX9/SOC15 hardware after reset or resume, especially non-zero defaults in `CNTL`, `CLK_CTRL`, `STATUS*`, `UTCL1_*`, `RB_CNTL`, and `PERFMON_CNTL`.
- KFD SDMA queue creation and teardown tests for GFX, PAGE, RLC0, and RLC1 paths, verifying that ring pointers and doorbells start from clean defaults.

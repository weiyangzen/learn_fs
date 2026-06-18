# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreend.h

## Purpose

`evergreend.h` is the hardware definition header for Evergreen/Northern Islands-era Radeon ASIC support. It does not implement executable control flow; it supplies register offsets, bit masks, packet constructors, enumerated values, and ASIC-specific constants that C files use to program display, memory controller, graphics, VM, interrupt, DMA, HDMI/audio, thermal, and command processor blocks. The header is included by files such as `evergreen.c`, `evergreen_cs.c`, `evergreen_dma.c`, `evergreen_hdmi.c`, and `cypress_dpm.c`, and many definitions are also conceptually shared with adjacent family headers like `r600d.h`, `rv770d.h`, `nid.h`, `sid.h`, and `cikd.h`.

## Important APIs, types, and macros

- ASIC resource limits and golden values: `EVERGREEN_MAX_*` constants describe shader/GPR/thread/backend/SIMD/pipe limits; `*_GB_ADDR_CONFIG_GOLDEN` constants encode known-good `GB_ADDR_CONFIG` values for Cypress, Barts, Cayman, Juniper, Redwood, Turks, Cedar, Caicos, Sumo, and Sumo2.
- Register field helpers: most definitions follow the local pattern `FIELD(x)`, `FIELD_MASK`, and sometimes `FIELD_SHIFT`, for example `NUM_PIPES(x)`, `PIPE_INTERLEAVE_SIZE(x)`, `DIG_THERM_INTH(x)`, `DC_HPDx_INT_EN`, `ENABLE_CONTEXT`, and `PAGE_TABLE_DEPTH(x)`.
- Command packet helpers: `PACKET0(reg, n)`, `PACKET2(v)`, and `PACKET3(op, n)` construct PM4 command stream packet headers for CP rings; packet opcode constants cover draw, sync, event, register programming, CP DMA, indirect buffer, and clear-state operations.
- DMA helpers: `DMA_PACKET(cmd, sub_cmd, n)`, `GET_DMA_CMD`, `GET_DMA_COUNT`, `GET_DMA_SUB_CMD`, and `DMA_PACKET_*` opcode constants encode Evergreen async DMA packet headers.
- Display/audio definitions: DCE/AFMT/HDMI/AZ register families cover HDMI control/status/infoframes, audio clock DTOs, codec pin capabilities, hotplug status/control, vblank/vline interrupts, FMT dithering/clamping, and graphics page-flip interrupt bits.
- Graphics/VM/memory definitions: `GB_ADDR_CONFIG`, `CC_RB_BACKEND_DISABLE`, `VM_CONTEXT0_CNTL`, `VM_L2_CNTL*`, `MC_VM_*`, `SQ_*`, `DB_*`, `CB_COLOR*`, `SQ_TEX_RESOURCE_*`, and `SQ_VTX_CONSTANT_*` describe tiling, render target, depth, shader, texture, vertex, and virtual memory programming fields.
- Power/clock/thermal definitions: `SMC_MSG`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, `MCLK_PWRMGT_CNTL`, SPLL/MPLL/UPLL registers, `CG_THERMAL_CTRL`, `CG_THERMAL_INT`, `CG_MULT_THERMAL_STATUS`, `TN_CG_THERMAL_INT_CTRL`, and related masks drive power-management and temperature code.

## Control flow

There is no runtime control flow inside the header. Its macros become inline constants and expressions in the caller's control flow. Typical flows using this header are:

1. ASIC initialization chooses a golden `GB_ADDR_CONFIG` value from the family constants and writes it with `WREG32`.
2. VM setup writes `VM_CONTEXT0_CNTL`, page-table base/start/end/default registers, and `VM_L2_CNTL*` bits.
3. Ring setup and command submission build PM4 packets through `PACKET3` and DMA packets through `DMA_PACKET`.
4. Interrupt handling uses status/control offsets such as `DISP_INTERRUPT_STATUS*`, `DC_HPDx_INT_STATUS`, `VBLANK_STATUS`, `GRPH_INT_STATUS`, and CP/IH interrupt registers.
5. Thermal and DPM code reads/writes `CG_THERMAL_*`, clock, and power-management registers.

## State and persistence behavior

The header itself has no mutable state, allocation, or persistence. It defines the ABI between driver code and hardware MMIO/command-stream layouts. The state affected by its constants lives in GPU registers, ring buffers, writeback memory, and command buffers built by other files. Because these macros encode hardware-visible bit positions, any incorrect value persists until the register is rewritten or the GPU block is reset.

## Dependencies and integration points

- Depends on common Radeon packet type definitions and helpers, including `RADEON_PACKET_TYPE0`, `RADEON_PACKET_TYPE3`, and `REG_SET`, which are provided by broader Radeon headers.
- Integrated by Evergreen core bring-up (`evergreen.c`), command parser validation (`evergreen_cs.c`), DMA engine code (`evergreen_dma.c`), HDMI/audio setup (`evergreen_hdmi.c`), and DPM/thermal paths (`cypress_dpm.c`, plus neighboring family DPM files for shared register concepts).
- Shares naming and register-family conventions with `nid.h`, `sid.h`, and `cikd.h`; callers must include the header matching the active ASIC generation to avoid programming wrong offsets or packet formats.

## Risks and edge cases

- Register drift across ASIC families is the main risk. Some names recur in multiple generation headers with different offsets or packet arities.
- Packet constructors do not validate `n`, register ranges, or opcode legality. Callers and command parsers must enforce packet lengths and register whitelists.
- Bitfield helpers generally shift without masking the input except for generated `S_*/G_*/C_*` style macros. Out-of-range inputs can set adjacent fields.
- Duplicated concepts such as thermal registers, `GB_ADDR_CONFIG`, and DMA packet formats differ between R600/RV770/Evergreen/NI/SI/CIK, so copy-paste changes can silently target the wrong generation.
- The header includes generated-style register macros alongside hand-written aliases. Inconsistent use can obscure whether a field is fully masked, clear-masked, or simply shifted.

## Test signals

- Build coverage: all Radeon files including `evergreend.h` must compile for Evergreen/Northern Islands configs.
- Ring tests: successful CP and DMA ring tests validate `PACKET3`, DMA packet constants, ring control registers, and fence/trap packet encodings.
- Display tests: hotplug, vblank, page-flip, HDMI audio, and mode-setting exercises validate DCE, AFMT, HPD, FMT, and interrupt offsets.
- VM/IB tests: GPU VM enable/disable, indirect buffer submission, and command parser validation exercise `VM_CONTEXT*`, `VM_L2*`, and PM4 packet range constants.
- Thermal/DPM debugfs and temperature reporting validate `CG_THERMAL_*` encodings.

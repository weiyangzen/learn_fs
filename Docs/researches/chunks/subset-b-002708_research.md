# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h lines 9361-14179

## Purpose

This chunk is a generated AMD GFX 7.2 shader/graphics-core register field mask header range. It contains C preprocessor constants for bit masks and shifts in GCA/GFX 7.2 registers, covering compute-unit clock-throttling controls, shader processor interface state, shader queue/debug/resource descriptors, thread trace packet formats, export/SX diagnostics, texture/cache performance counters, and texture processor controls. The header is declarative hardware metadata; it has no runtime logic, but it is part of the source-level ABI used by AMDGPU and KFD driver code to compose and decode 32-bit register values.

The range starts in the middle of the `CGTS_CU0_*` per-compute-unit clock-throttling definitions and ends inside the `TCP_EDC_COUNTER` family. The preceding chunk contains the beginning of the CGTS section, and the next lines contain the missing `TCP_EDC_COUNTER__DED_COUNT__SHIFT` plus later TCP/TC cache policy masks. Merge/reconciliation should treat this as a large middle slice of `gfx_7_2_sh_mask.h`, not as a complete semantic section by itself.

## Major Register Areas Covered

The opening section defines `CGTS_CU0` through `CGTS_CU15` masks for compute-unit clock-throttling and light-sleep control. Each CU has repeated control registers for SP0/SP1, LDS/SQ, TA or TA/SQC, and TD/TCP blocks. The fields are mostly per-block enable/override/busy-override/light-sleep/SIMD-busy controls, using low and high 16-bit lanes for paired units such as `SP00`/`SP01`, `LDS`/`SQ`, and `TD`/`TCP`.

The next section covers clock gating and SPI state. `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, and `CGTT_BCI_CLK_CTRL` provide on-delay, off-hysteresis, and soft override fields. `SPI_WF_LIFETIME_*` exposes wavefront lifetime limit/status controls. `SPI_SLAVE_DEBUG_BUSY`, `SPI_LB_*`, `SPI_PG_ENABLE_STATIC_CU_MASK`, `SPI_GDS_CREDITS`, `SPI_SX_*`, `SPI_CSQ_WF_ACTIVE_*`, `BCI_DEBUG_READ`, trap screen registers, shader trap base/memory address registers, shader program address registers, and shader resource registers describe SPI wave dispatch, debugging, trap handling, static CU masks, GDS/SX buffering, and active wave accounting.

The shader-programming block covers PS, VS, GS, ES, HS, and LS stages. It defines trap base/address and trap memory address low/high registers, program base low/high registers, `SPI_SHADER_PGM_RSRC1/2/3_*` fields for VGPR/SGPR usage, priority, float mode, privilege, DX10 clamp, debug/IEEE mode, CU enable, wave limits, LDS size, scratch/trap/user-SGPR setup, stream-out enables, exception enables, and stage-specific allocation controls. The same section defines `SPI_SHADER_USER_DATA_*_0` through `_15` payload registers for each stage, all as full-width data fields.

The SQ/SQC section covers shader queue configuration, cache configuration, random wave priority, register credits, FIFO sizes, interrupt auto-mask/message control, performance counter control/masking/select/readback, SQC bank disable masks, clock controls, power throttling, shader time registers, thread trace buffer programming, SQ low-bandwidth counters, SEC/DED error counters, buffer/image resource descriptors, sampler descriptors, flat scratch descriptors, indirect SQ register access, SQ commands, wave register snapshots, debug status, local memory configuration, and SQC policy/volatile controls.

Thread-trace and decode metadata are a large part of the middle of the chunk. `SQ_THREAD_TRACE_*` programming registers describe trace buffer address, size, masks, userdata, mode, token masks, write pointer, status, counter, and high-water state. `SQ_THREAD_TRACE_WORD_*` masks describe emitted trace packet layouts for common, instruction, PC, userdata, timestamp, wave, misc, wave-start, register, event, issue, and perf packets. The `SQ_INTERRUPT_WORD_*` groups define SQ interrupt packet layouts, while `SQ_SOP2`, `SQ_VOP1`, `SQ_MTBUF`, `SQ_EXP`, `SQ_MUBUF`, `SQ_INST`, `SQ_VOP3`, `SQ_SOPP`, `SQ_FLAT`, `SQ_MIMG`, `SQ_SMRD`, `SQ_SOP1`, `SQ_SOPC`, `SQ_DS`, `SQ_SOPK`, `SQ_VOPC`, and `SQ_VINTRP` describe instruction encoding fields.

The SX/export block defines clock controls `CGTT_SX_CLK_CTRL0` through `_4`, extensive `SX_DEBUG_BUSY*` status fields for export path, scoreboard, column-buffer, bank, FIFO, and DBIF busy/valid state, `SX_DEBUG_1`, and four SX performance counters with select/select1 and low/high readback registers.

The final cache/texture section covers TCC/TCA/TCS/TD/TA/TCP controls and counters. `TCC_CTRL`, `TCC_EDC_COUNTER`, `TCC_REDUNDANCY`, and `TCC_CGTT_SCLK_CTRL` describe cache sizing, rate, writeback/invalidate behavior, EDC counts, redundancy, and clock controls. `TCC`, `TCA`, `TCS`, `TD`, `TA`, and `TCP` performance counter families provide select, secondary select, mode, and low/high counter fields. `TD_CNTL`, `TD_STATUS`, debug, scratch, and performance counters define texture data pipe behavior. `TA_CNTL`, `TA_CNTL_AUX`, broadcast base addresses, status, debug, scratch, and performance counters define texture address/control behavior. `SH_HIDDEN_PRIVATE_BASE_VMID`, `SH_STATIC_MEM_CONFIG`, `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, channel steering, address configuration, credits, buffer address hash control, and the first `TCP_EDC_COUNTER` fields define shader memory/TCP cache behavior.

## Important APIs, Types, and Functions

There are no C functions, structs, enums, or inline helpers in this chunk. The exposed API surface is the macro namespace:

- `REGISTER__FIELD_MASK` constants identify the field bits within a 32-bit register value.
- `REGISTER__FIELD__SHIFT` constants identify the right shift for the field.
- Full-width data, address, counter, and scratch fields use `0xffffffff` masks, while high address halves commonly use 8-bit or narrower masks.
- Repeated register families rely on exact spelling and numbering, for example `CGTS_CU15_TD_TCP_CTRL_REG__TCP_SIMDBUSY_OVERRIDE_MASK` or `SPI_SHADER_USER_DATA_PS_15__DATA_MASK`.

The file is consumed together with the matching GFX 7.2 offset header `gfx_7_2_d.h`, which provides corresponding `mm*` and `ix*` register addresses such as `mmCGTS_CU0_LDS_SQ_CTRL_REG`, `mmSPI_SHADER_PGM_LO_PS`, `mmSQ_CONFIG`, `mmTCC_CTRL`, `mmTD_CNTL`, `mmTA_STATUS`, and `mmTCP_CNTL`. Callers normally use AMDGPU helpers such as `REG_SET_FIELD`, direct shifts/masks, `RREG32`, `WREG32`, and indexed SQ reads.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time and caller-driven:

1. AMDGPU, KFD, SDMA, or power-management code includes `gfx_7_2_sh_mask.h` with the matching offset definitions.
2. The caller selects a register field macro for a hardware programming or decode path.
3. Register helper macros or direct bit operations shift and mask the field value.
4. The caller reads or writes the associated MMIO/indexed register, or decodes a register/status/trace value returned by hardware.

In-tree examples include `gfx_v7_0_enable_mgcg()` using CGTS mask fields to configure `mmCGTS_SM_CTRL_REG`, `gfx_v7_0_ring_soft_recovery()` composing `SQ_CMD` with `REG_SET_FIELD`, and `wave_read_ind()`/`wave_read_regs()` using `SQ_IND_INDEX` shifts and masks before reading `SQ_IND_DATA`. This chunk also supports code that writes shader memory registers, SQ configuration, `TA_CNTL_AUX`, and wave/debug register snapshots.

## State and Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe lives in GFX 7.2 hardware registers and persists according to GPU lifecycle rules, not C object lifetime.

CGTS/CGTT fields describe clock-gating, throttling, and light-sleep state that can remain active until driver reconfiguration, power management changes, suspend/resume, GPU reset, or firmware/RLC sequences overwrite it. SPI shader program, trap, resource, and user-data fields describe per-stage programming state used during draw and dispatch setup. SQ/SQC fields describe shader queue control, cache policy, register-credit state, performance counter selection, thread-trace buffers, interrupt packet formats, wave debug state, memory aperture/base behavior, and shader resource descriptors. SX, TCC, TCA, TCS, TD, TA, and TCP fields describe export/cache/texture status, performance counters, cache invalidation/hash/channel behavior, address steering, EDC counts, debug selection, and busy/status signals.

Many described registers are control or status registers with hardware side effects. This header does not encode access mode, reset value, read-only/write-only semantics, sticky status behavior, write-one-to-clear behavior, or required sequencing. Callers must apply the hardware specification and driver synchronization rules around GRBM/SRBM indexing, SQ indirect access, power-gating transitions, cache invalidation, and performance counter programming.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor but must stay synchronized with AMD's generated GFX 7.2 register database and companion files under `include/asic_reg/gca/`, especially `gfx_7_2_d.h` and `gfx_7_2_enum.h`. The numeric masks are only meaningful for the GFX 7.2 register layout; mixing them with another ASIC generation's offsets can silently target wrong fields.

Known source integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`, which includes this header for GFX v7 initialization, clock-gating setup, SQ commands, shader memory configuration, wave debug reads, and status handling.
- `drivers/gpu/drm/amd/amdgpu/cik.c`, `cik_sdma.c`, and power-management files under `pm/legacy-dpm` and `pm/powerplay`, which include the GFX 7.2 masks for CIK-era ASIC setup and power features.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c` and `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_cik.c`, which integrate GFX v7/KFD queue and shader-memory state with HSA/KFD operation.
- Performance tooling and debug paths that program SQ/SX/TCC/TCA/TCS/TD/TA/TCP counters or decode SQ thread traces, wave state, and busy/status registers.

The field names are source contracts. Token-pasting helpers such as `REG_SET_FIELD(value, SQ_CMD, VM_ID, vmid)` depend on exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names, so renaming a macro is a source break even if its numeric value remains the same.

## Risks and Edge Cases

The primary risk is generated bitfield drift. A wrong mask or shift can misprogram clock gating, enable the wrong CU override, corrupt shader resource descriptors, point a shader program/trap base at the wrong address, mis-size SGPR/VGPR/LDS resources, select the wrong performance event, decode thread trace packets incorrectly, miss ECC/EDC signals, or change TCP/texture cache behavior. These failures typically appear as hangs, GPU faults, missed interrupts, bad debug data, performance counter nonsense, or subtle rendering/compute corruption.

The chunk contains many highly repetitive families. Per-CU `CGTS_CU*` registers, shader stage resource/user-data registers, SQ performance counters 0-15, SX/TCC/TCA/TCS/TCP performance counters, and TA/TD counter groups differ mostly by index and stage. Generator errors, copy/paste mistakes, or partial edits are difficult to review manually and should be checked mechanically against the authoritative register database.

Partial chunk boundaries are important. The first line starts after `CGTS_CU0_SP0_CTRL_REG`, so `CGTS_CU0` is not fully covered here. The last listed line contains `TCP_EDC_COUNTER__DED_COUNT_MASK` without its matching `__SHIFT`, which appears after this chunk. A consumer or merger should not infer that `TCP_EDC_COUNTER` is complete from this document alone.

Full-width masks require careful handling in C expressions. The header uses unsigned-looking constants but not uniformly `U` or `UL` suffixes, so callers should keep operations in unsigned 32-bit types where appropriate. Address split fields also require pairing low and high registers correctly; using only the low 32 bits of shader program, trap, broadcast, or resource addresses can produce invalid GPU virtual addresses.

The header cannot tell whether a field is reserved, read-only, write-only, debug-only, or side-effecting. This matters for busy/status fields, invalidate controls, EDC/DED counters, debug index/data registers, SQ indirect access, thread-trace control/status, cache/TCP controls, clock/power-gating override bits, and performance counter select/readback registers.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Build the AMDGPU tree with CIK/GFX v7 and KFD support enabled to catch syntax errors, duplicate definitions, missing macros, and token-pasting mismatches.
- Compare lines 9361-14179 against the authoritative AMD GFX 7.2 register database and the matching `gfx_7_2_d.h` offsets to verify field names, shifts, masks, widths, and register grouping.
- Exercise CIK/GFX v7 hardware initialization, clock-gating enable/disable, suspend/resume, GPU reset, and power transitions to catch CGTS/CGTT/TCC/TCA/TCS/TD/TA/TCP programming mistakes.
- Run graphics and compute workloads that cover PS/VS/GS/ES/HS/LS shader programming, scratch, traps, user SGPRs, LDS sizing, stream-out, texture sampling, buffer/image descriptors, and cache policy.
- Validate KFD/HSA queue operation and shader-memory configuration, especially `SH_MEM_*`, `SQ_CMD`, SQ indirect wave reads, and VMID-sensitive behavior.
- Use debug/perf tests for SQ thread trace, SQ/SX/TCC/TCA/TCS/TD/TA/TCP performance counters, wave register dumps, busy/status decoding, EDC/SEC/DED counters, and cache/TCP invalidation where supported by hardware.

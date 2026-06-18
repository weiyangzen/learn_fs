# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 19702-22065

## Purpose

This chunk is generated-style register field metadata for the AMD GC 9.4.2 graphics core. It contains C preprocessor constants that define bit shifts and bit masks for hardware register fields. The definitions are not executable code; they are the symbolic contract used by AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_KIQ`, and SOC15 offset wrappers to read, compose, and update 32-bit graphics-core registers without open-coding bit positions.

The range starts in the middle of `CGTT_SX_CLK_CTRL4`, covers multiple clock-gating and clock-throttling control registers, then crosses into the `gc_rbdec` address block for depth buffer, render backend, graphics backend, tile/macro-tile, color buffer, and DCC controls. It then enters the `gc_rlcpdec` address block for RLC control, status, safe-mode handshakes, timers, load balancing, clock-gating/power-gating controls, and RLC SERDES access fields. The chunk ends partway through `RLC_SERDES_WR_CTRL`, so the following chunk owns the remaining fields for that register.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or runtime variables in this chunk. The API surface is a large set of macros following the generated AMD ASIC register naming pattern:

- `REGISTER__FIELD__SHIFT` gives the low bit index of a field.
- `REGISTER__FIELD_MASK` gives the unshifted mask for the field in a 32-bit register word.
- Full-register fields use masks such as `0xFFFFFFFFL`, for example timer values, CU masks, clock counters, and SERDES read data.
- Comments such as `// addressBlock: gc_rbdec` and `// addressBlock: gc_rlcpdec` mark hardware register decode blocks, not C namespaces.

The first group covers CGTT clock-gating and clock-throttling controls for graphics sub-blocks:

- `CGTT_SX_CLK_CTRL4`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `CGTT_TCP_TCR_CLK_CTRL`, `CGTT_TCI_TCR_CLK_CTRL`, `TCX_CGTT_SCLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL2`, `TCC_CGTT_SCLK_CTRL3`, `TCA_CGTT_SCLK_CTRL`, `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, `CGTT_RLC_CLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_CGTT_CLK_CTRL`, and `GRBM_CGTT_CLK_CNTL`.
- Common fields include `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, `SOFT_OVERRIDE_DYN`, `SOFT_OVERRIDE_REG`, `SOFT_OVERRIDE_PERFMON`, and block-specific bits such as `MGLS_OVERRIDE`, `TCC_LS_ENABLE`, `BLK_CLKEN_MASK`, and `SOFT_OVERRIDE_DIDT_REG`.
- `RLC_GFX_RM_CNTL` is a small register with `RLC_GFX_RM_VALID`, used to represent validity of RLC graphics resource-management state.

The `gc_rbdec` group covers DB/RB/GB/CB rendering backend configuration:

- Depth buffer debug and cache/control registers: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1`, `DB_FIFO_DEPTH2`, `DB_EXCEPTION_CONTROL`, `DB_RING_CONTROL`, `DB_MEM_ARB_WATERMARKS`, `DB_RMI_CACHE_POLICY`, `DB_DFSM_CONFIG`, `DB_DFSM_WATERMARK`, `DB_DFSM_TILES_IN_FLIGHT`, `DB_DFSM_PRIMS_IN_FLIGHT`, `DB_DFSM_WATCHDOG`, `DB_DFSM_FLUSH_ENABLE`, and `DB_DFSM_FLUSH_AUX_EVENT`.
- Render backend redundancy and disable masks: `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GC_USER_RB_REDUNDANCY`, and `GC_USER_RB_BACKEND_DISABLE`.
- Graphics backend topology registers: `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `GB_BACKEND_MAP`, `GB_GPU_ID`, and `CC_RB_DAISY_CHAIN`. These describe pipe count, interleave size, bank count, shader-engine count, RBs per SE, compressed-fragment capacity, packed pipes, and related topology fields.
- Tile and macro-tile modes: `GB_TILE_MODE0` through `GB_TILE_MODE31` define `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE`, and `SAMPLE_SPLIT`; `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` define `BANK_WIDTH`, `BANK_HEIGHT`, `MACRO_TILE_ASPECT`, and `NUM_BANKS`.
- Color buffer and DCC controls: `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, and `CB_DCC_CONFIG` describe blend/fast-clear behavior, cache tag and FIFO sizing, memory arbitration weights, NACK handling, clock-gating bypasses, DCC overwrite-combiner behavior, and DCC cache sizing.

The `gc_rlcpdec` group covers RLC microcontroller, timer, load-balancing, clock-counting, and power-management state:

- Core RLC control/status: `RLC_CNTL`, `RLC_STAT`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_INT_STAT`, and `RLC_UCODE_CNTL`.
- RLC memory sleep and clock counters: `RLC_MEM_SLP_CNTL`, `RLC_REFCLOCK_TIMESTAMP_LSB/MSB`, `RLC_GPU_CLOCK_COUNT_LSB/MSB`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_GFXCLK_LSB/MSB`, `RLC_CLK_COUNT_REFCLK_LSB/MSB`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32`.
- GPM timers and threads: `RLC_GPM_TIMER_INT_0` through `RLC_GPM_TIMER_INT_3`, `RLC_GPM_TIMER_CTRL`, `RLC_GPM_TIMER_STAT`, `RLC_GPM_THREAD_RESET`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_CP_DMA_COMPLETE_T0`, `RLC_GPM_CP_DMA_COMPLETE_T1`, and `RLC_GPM_STAT`.
- Load balancing and dynamic CU power gating: `RLC_LB_CNTR_MAX`, `RLC_LB_CNTL`, `RLC_LB_CNTR_INIT`, `RLC_LOAD_BALANCE_CNTR`, `RLC_PG_DELAY_2`, `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_DELAY`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_LB_PARAMS`, `RLC_THREAD1_DELAY`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, and `RLC_AUTO_PG_CTRL`.
- Clock-gating policy: `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` define memory-gating intervals, override bits for MGCG/CGCG/CGLS/MGLS/FGCG, idle thresholds, sleep modes, and CGCG ramp timing.
- RLC SERDES access: `RLC_SERDES_WR_NONCU_MASTER_MASK_1`, `RLC_SERDES_NONCU_MASTER_BUSY_1`, `RLC_SERDES_RD_PENDING`, `RLC_SERDES_RD_MASTER_INDEX`, `RLC_SERDES_RD_DATA_0..2`, `RLC_SERDES_WR_CU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK`, and the beginning of `RLC_SERDES_WR_CTRL`.

## Control Flow

This header chunk has no runtime control flow. Its effect is entirely through preprocessing and compilation: consumers include the GC 9.4.2 register headers, then use the macros to construct register values or extract field values during device initialization, power management, debug, reset, and status reporting.

Typical consumer flow is:

1. Select the GC 9.4.2 offset and mask headers for devices whose `amdgpu_ip_version(adev, GC_HWIP, 0)` is `IP_VERSION(9, 4, 2)`.
2. Read a 32-bit register through a SOC15 accessor, or start from a known golden/default value.
3. Use these `__SHIFT` and `_MASK` constants directly or through `REG_GET_FIELD`/`REG_SET_FIELD`.
4. Write the updated register back, or cache decoded topology/status values in driver state.

Visible consumers in the surrounding AMDGPU tree show these patterns. `gfx_v9_0.c` handles the GC 9.4.2 case by reading `mmGB_ADDR_CONFIG`, applying a GC 9.4.2 topology value, and decoding fields such as `NUM_PIPES`, `NUM_BANKS`, `MAX_COMPRESSED_FRAGS`, `NUM_RB_PER_SE`, `NUM_SHADER_ENGINES`, and `PIPE_INTERLEAVE_SIZE` into `adev->gfx.config`. The same file programs and queries RLC CGCG/CGLS state with `RLC_CGTT_MGCG_OVERRIDE__GFXIP_CGCG_OVERRIDE_MASK`, `RLC_CGTT_MGCG_OVERRIDE__GFXIP_CGLS_OVERRIDE_MASK`, `RLC_CGCG_CGLS_CTRL__CGCG_GFX_IDLE_THRESHOLD__SHIFT`, `RLC_CGCG_CGLS_CTRL__CGCG_EN_MASK`, and `RLC_CGCG_CGLS_CTRL__CGLS_EN_MASK`. It also reads `DB_DEBUG2` into `adev->gfx.config.db_debug2` for relevant ASICs.

The line range itself is purely declarative, but the implied runtime sequencing is important for several register families. RLC safe-mode and clock-gating updates must be sequenced so the RLC is in a stable state before changing CGTT/MGCG/CGCG bits. GB address configuration must be decoded before surface tiling and backend layout decisions depend on it. DB/CB debug and cache controls must be programmed consistently with golden settings and hardware workarounds before rendering workloads rely on compression, fast clear, HTILE, DCC, or cache arbitration behavior.

## State And Persistence Behavior

The macros do not store state. The state they describe lives in hardware registers or in driver fields populated from those registers.

State categories in this chunk include:

- Persistent hardware configuration until reset, power transition, or explicit reprogramming: most `CGTT_*`, `*_CGTT_*`, `DB_*`, `CB_*`, `GB_ADDR_CONFIG`, `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, `RLC_MEM_SLP_CNTL`, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_PG_*`, and `RLC_AUTO_PG_CTRL` fields.
- Driver-cached topology: fields decoded from `GB_ADDR_CONFIG` become `adev->gfx.config.gb_addr_config` and `adev->gfx.config.gb_addr_config_fields`, which persist in memory for later GFX setup and resource decisions.
- Status and observation state: `RLC_STAT`, `RLC_GPM_TIMER_STAT`, `RLC_SERDES_NONCU_MASTER_BUSY_1`, `RLC_INT_STAT`, `RLC_CLK_COUNT_STAT`, `RLC_GPM_STAT`, `RLC_DYN_PG_STATUS`, `RLC_CU_STATUS`, `DB_DFSM_TILES_IN_FLIGHT`, `DB_DFSM_PRIMS_IN_FLIGHT`, and SERDES read data expose transient hardware status.
- Command or handshake state: `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_GPM_THREAD_RESET`, `RLC_JUMP_TABLE_RESTORE`, `RLC_DYN_PG_REQUEST`, and `RLC_SERDES_WR_CTRL` are intended to drive hardware-side actions or select a read/write transaction.
- Counters and timestamps: RLC reference-clock, GPU-clock, GFXCLK, REFCLK, GPM timer, load-balance, and 32-bit GPU-clock fields are read to measure or synchronize hardware behavior.

No filesystem state, kernel heap allocation, locks, or reference counts are implemented here. Persistence risk comes from programming sticky hardware registers incorrectly, failing to restore them after suspend/resume/reset, or interpreting status fields as writable policy fields.

## Dependencies

This chunk depends on the rest of the generated GC 9.4.2 register header set:

- `gc_9_4_2_offset.h` supplies matching register offsets such as `mmGB_ADDR_CONFIG`, `mmDB_DEBUG2`, and `mmRLC_CGCG_CGLS_CTRL`.
- Other portions of `gc_9_4_2_sh_mask.h` define adjacent fields outside this chunk, including the start of `CGTT_SX_CLK_CTRL4` before line 19702 and the remainder of `RLC_SERDES_WR_CTRL` after line 22065.
- AMDGPU SOC15 access helpers and field macros provide the C-level read/modify/write operations that combine these shifts and masks with register values.
- `gfx_v9_0.c`, SDMA setup, power-management code, virtualization paths, XGMI/RAS handling, and firmware-loading conditionals depend on GC 9.4.2 identification and the associated register layout.

The data is a hardware specification contract. Macro names can look very similar across GC 9.x, 10.x, 11.x, and 12.x, but field widths and even field meanings can differ. Consumers must include the header for the active ASIC generation and use the matching offset header.

## Integration Points

Important integration points include:

- GFX topology setup: `GB_ADDR_CONFIG` and `GB_ADDR_CONFIG_READ` fields feed pipe, bank, SE, RB-per-SE, compressed-fragment, and interleave calculations in GFX initialization. These values affect memory tiling and render-backend assumptions.
- Golden settings and hardware workarounds: `DB_DEBUG2`, `CB_DCC_CONFIG`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ` appear in GFX golden-setting tables and initialization paths. The masks must match hardware so masked writes alter only intended bits.
- Clock gating and power management: CGTT controls, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_MEM_SLP_CNTL`, and `RLC_PG_*` integrate with `adev->cg_flags`, RLC safe-mode entry/exit, SR-IOV restrictions, suspend/resume, and runtime power-management code.
- Rendering backend operation: DB fields influence depth/stencil compression, fast-Z/stencil, HTILE synchronization, cache miss behavior, subtile grouping, DFSM flushing, watermarks, FIFO depths, and RMI cache policy. CB fields influence blending, fast clear, DCC, cache tags, FIFO sizing, arbitration, NACK handling, and color-cache prefetch.
- Surface layout and metadata: `GB_TILE_MODE*` and `GB_MACROTILE_MODE*` describe tile/macro-tile layouts that must stay consistent with userspace-visible tiling, kernel buffer metadata, SDMA settings, display usage, and firmware/golden values.
- RLC diagnostics and control: `RLC_STAT`, safe-mode fields, GPM timers, clock counters, SERDES master masks, SERDES busy/read-data fields, and interrupt status integrate with debug, bring-up, validation, and low-level power-gating flows.
- RAS and virtualization: GC 9.4.2-specific paths in the tree branch on `IP_VERSION(9, 4, 2)`. Incorrect field metadata can affect VF restrictions, RAS enablement, XGMI behavior, and firmware/ucode handling even when the macros are used indirectly.

## Risks

- A wrong shift or mask silently changes the wrong hardware bits. For this chunk, likely symptoms include broken clock gating, unstable RLC safe-mode transitions, incorrect render-backend topology, surface tiling corruption, depth/stencil rendering errors, or DCC/HTILE/cache behavior regressions.
- The range contains many debug and override fields with negative names such as `DISABLE_*`, `FORCE_*`, and `*_OVERRIDE`. Setting or clearing one bit with inverted semantics can turn off compression, bypass synchronization, force cache misses, disable clock gating, or mask a hardware workaround.
- `GB_ADDR_CONFIG`, `GB_TILE_MODE*`, and `GB_MACROTILE_MODE*` are topology/layout fields. Mismatches can compile cleanly but cause cross-engine disagreement between GFX, SDMA, display, firmware, and userspace about memory layout.
- RLC state is sensitive to ordering. Writes to `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_MEM_SLP_CNTL`, power-gating request registers, or SERDES controls should be done only in the expected safe-mode or idle context.
- Status fields and command fields are mixed in the same generated header. Treating status such as `RLC_STAT`, `RLC_GPM_STAT`, `RLC_DYN_PG_STATUS`, or SERDES busy/data registers as ordinary configuration can lead to meaningless writes or missed handshakes.
- Reserved and spare masks occupy many high or middle bits. Consumers doing raw writes instead of masked read/modify/write can disturb reserved bits and create ASIC-specific failures.
- The chunk starts and ends mid-register. The previous chunk owns the beginning of `CGTT_SX_CLK_CTRL4`; the next chunk owns the remainder of `RLC_SERDES_WR_CTRL`. Any merged per-file analysis must account for those split registers before making complete-register claims.
- Generated register headers should not be hand-edited casually. Updates should normally come from regenerated ASIC register specifications so offsets, masks, defaults, and comments remain synchronized.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU configurations that include GC 9.4.2 headers and `gfx_v9_0.c`, ensuring every referenced field macro resolves with the expected offset header.
- Static consistency checks that registers represented here have corresponding `mm*` entries in `gc_9_4_2_offset.h` and, where applicable, matching default/golden-setting coverage.
- Boot smoke tests on GC 9.4.2 hardware that initialize GFX, load RLC firmware, apply golden settings, read `GB_ADDR_CONFIG`, and populate `adev->gfx.config` without register access faults.
- Clock-gating tests that toggle MGCG/CGCG/CGLS/MGLS/FGCG support and verify `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_MEM_SLP_CNTL`, and CGTT controls report expected state through the driver clock-gating query path.
- Suspend/resume, GPU reset, and SR-IOV VF tests, because these paths stress whether persistent RLC, CGTT, DB, CB, and GB registers are restored or masked correctly.
- Rendering workloads that stress depth/stencil compression, fast-Z/stencil, HTILE, MSAA/EQAA, DCC, blending, fast clear, and tiled/macro-tiled surfaces. Visual corruption, VM faults, hangs, or performance cliffs are strong signals for bad DB/CB/GB field handling.
- SDMA and graphics interop tests that copy or render tiled buffers, because `GB_ADDR_CONFIG` and tile-mode fields must agree across engines.
- RLC diagnostic tests that read busy/status fields, capture GPU clock counts, exercise GPM timers/threads, and perform SERDES read sequences while checking `RLC_SERDES_RD_PENDING` and read-data registers.

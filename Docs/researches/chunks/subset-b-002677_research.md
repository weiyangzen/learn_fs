# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 24624-27042

## Purpose

This chunk is generated register-field metadata for the AMD GC 9.4.2 graphics core, used by the Linux AMDGPU driver for Aldebaran-class hardware. It contains `#define` constants for field shifts and bit masks, not executable code. Consumers combine these definitions with the matching `gc_9_4_2_offset.h` register offsets and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

The range starts at the tail of `SPI_WF_LIFETIME_LIMIT_9`, covers SPI wave lifetime/status, load-balance, trap, arbitration, compute-queue, and compute-unit reservation fields, then enters the `gc_sqdec` address block. The SQ portion defines shader-queue configuration, SQC cache/DSM/error counters, timeout/debug/indirect wave access registers, shader instruction word layouts, SQ load-balance counters, EDC/RAS fields, thread-trace token layouts, write-exec address words, and the beginning of buffer/image resource descriptor formats through `SQ_IMG_RSRC_WORD1`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or variables in this chunk. The public surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's low bit.
- `REGISTER__FIELD_MASK` gives the unshifted bit mask within a 32-bit register or descriptor word.
- Full-width masks such as `SQ_IND_DATA__DATA_MASK`, `SQ_TIME_HI__TIME_MASK`, `SQ_TIME_LO__TIME_MASK`, `SQ_BUF_RSRC_WORD0__BASE_ADDRESS_MASK`, and `SQ_BUF_RSRC_WORD2__NUM_RECORDS_MASK` mark whole-word payloads.
- The `// addressBlock: gc_sqdec` comment marks a hardware decode block boundary, not a C namespace.

Important register groups in this range include:

- SPI wave and scheduling state: `SPI_WF_LIFETIME_STATUS_0..20`, `SPI_LB_CTR_CTRL`, `SPI_LB_CU_MASK`, `SPI_LB_DATA_*`, `SPI_CSQ_WF_ACTIVE_STATUS`, `SPI_CSQ_WF_ACTIVE_COUNT_0..7`, and `SPI_COMPUTE_WF_CTX_SAVE` expose wave lifetime, active wave counters, load-balance snapshots, and compute wave context-save status.
- SPI debug/trap and arbitration: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_GDBG_WAVE_CNTL3`, `SPI_GDBG_TRAP_DATA0/1`, and `SPI_ARB_CNTL_0` define trap enablement, per-VMID debug controls, wave launch/control fields, and arbitration weighting.
- SPI resource reservation: `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15` define per-CU reservations for VGPR, SGPR, LDS, waves, barriers, enabled resource types, queue masks, and reserve-space-only behavior.
- SQ/SQC configuration and status: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, `SQ_FIFO_SIZES`, `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL*`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_TIMEOUT_CONFIG`, `SQ_TIMEOUT_STATUS`, `SH_CAC_CONFIG`, `SP_MFMA_PORTD_RD_CONFIG`, `CC_GC_SHADER_RATE_CONFIG`, and `GC_USER_SHADER_RATE_CONFIG`.
- DSM/error-injection and EDC counters: `SQ_DSM_CNTL*`, `SQC_DSM_CNTL*`, `SQC_EDC_FUE_CNTL`, `SQC_EDC_CNT2/3`, `SQC_EDC_PARITY_CNT3`, `SQC_EDC_CNT`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_EDC_CNT`, and `SQ_EDC_FUE_CNTL`.
- UTCL1 and interrupt controls: `SQ_UTCL1_CNTL1`, `SQ_UTCL1_CNTL2`, `SQ_UTCL1_STATUS`, `SQ_FED_INTERRUPT_STATUS`, and `SQ_CGTS_CONFIG` describe shader-side translation-cache controls, fault/status bits, fed interrupt status, and clock-gating/test fields.
- Wave debug and commands: `SQ_HOSTTRAP_STATUS`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CONFIG1`, and `SQ_CMD` define the indirect wave/register access path and SQ command encoding.
- Shader instruction layouts: `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_INST`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP3*`, `SQ_VOP_DPP`, and `SQ_VOP_SDWA*` define bit positions for ISA instruction words.
- Thread-trace and descriptors: `SQ_THREAD_TRACE_WORD_*` macros define trace token fields for events, instructions, issue, perf, register writes, timestamps, wave IDs, PCs, and userdata. `SQ_WREXEC_EXEC_HI/LO`, `SQ_BUF_RSRC_WORD0..3`, and `SQ_IMG_RSRC_WORD0..1` define write-exec addressing and the start of shader buffer/image descriptor layouts.

## Control Flow

This header has no runtime control flow. Its only behavior is preprocessor substitution at compile time.

Runtime control flow appears in consumers:

1. GC 9.4.2-specific source includes `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h`.
2. Driver code selects a register instance, shader engine, shader array, CU, VMID, or XCC as needed.
3. It reads or writes a 32-bit register through SOC15 helpers.
4. It uses these shift/mask macros through `REG_SET_FIELD`, `REG_GET_FIELD`, or direct shifts to encode or decode individual hardware fields.

Concrete integration examples include `gfx_v9_4_2_init_sq()`, which sets `SQ_CONFIG1__DISABLE_XNACK_CHECK_IN_RETRY_DISABLE` when MEC firmware supports chained XNACK handling; `gfx_v9_4_2_debug_trap_config_init()`, which programs `SPI_GDBG_PER_VMID_CNTL` and clears `SPI_GDBG_TRAP_DATA0/1`; and `wave_read_ind()`, which constructs `SQ_IND_INDEX` from `WAVE_ID`, `SIMD_ID`, `INDEX`, and `FORCE_READ` before reading `SQ_IND_DATA`.

## State And Persistence Behavior

The macros themselves are stateless and persist only as compiled constants. The state they describe lives in GPU registers, shader descriptors, trace buffers, and status counters.

State categories represented here:

- Configuration state that persists until reprogrammed, reset, or power-cycled: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_CONFIG1`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_UTCL1_CNTL*`, `SPI_ARB_*`, `SPI_RESOURCE_RESERVE_*`, and trap-control registers.
- Volatile command/debug access: `SQ_CMD`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_TIME_HI/LO`, and `SQ_HOSTTRAP_STATUS`.
- Hardware counters and snapshots: `SPI_WF_LIFETIME_STATUS_*`, `SPI_CSQ_WF_ACTIVE_*`, `SPI_LB_DATA_*`, `SQ_LB_DATA*`, `SQC_EDC_*`, `SQ_EDC_*`, and `SQ_TIMEOUT_STATUS`.
- Fault and interrupt status: `SQ_UTCL1_STATUS`, `SQ_FED_INTERRUPT_STATUS`, EDC/FUE fields, host-trap pending status, and SQ timeout fields.
- Validation/destructive test controls: `SQ_DSM_CNTL*` and `SQC_DSM_CNTL*` contain stall, irritator, single-write, and error-injection fields. These are not ordinary performance tuning knobs.

Several consumer paths are explicitly stateful. `gfx_v9_4_2_enable_watchdog_timer()` programs `SQ_TIMEOUT_CONFIG` per shader engine under `grbm_idx_mutex`. `gfx_v9_4_2_query_sq_timeout_status()` iterates SE/SH/CU selections, reads `SQ_TIMEOUT_STATUS`, logs wave state through `SQ_IND_INDEX`/`SQ_IND_DATA`, then writes zero to clear old status. Debug trap setup is VMID-scoped and protected by `srbm_mutex` while GRBM selection changes.

## Dependencies

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h` for matching `reg*` register offsets.
- AMDGPU SOC15 accessors and field helpers that know how to combine these masks with register values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which includes this header for Aldebaran golden settings, SQ initialization, trap setup, RAS/EDC handling, watchdog timeout handling, and wave inspection.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, which routes GC 9.4.2 initialization and shared GFX v9 paths, including SQ command and wave debug patterns.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c`, which includes the same GC 9.4.2 offset/mask headers for KFD-facing Aldebaran behavior.

The definitions are hardware-contract data. Similar macro names exist in other GC generations, but layouts are not interchangeable; including the wrong ASIC header can compile and still program the wrong bits.

## Integration Points

Primary integration points are:

- Golden-register and ASIC initialization paths in `gfx_v9_4_2.c`; while not every register in this chunk is programmed by golden tables, the same generated header family supplies the field names and register layout for GC 9.4.2 setup.
- SQ initialization, especially `SQ_CONFIG1` XNACK-related fields gated on MEC firmware version.
- VMID-scoped debug trap setup through `SPI_GDBG_PER_VMID_CNTL`, `SPI_GDBG_TRAP_DATA0`, and `SPI_GDBG_TRAP_DATA1`.
- Wave timeout/RAS diagnostics through `SQ_TIMEOUT_CONFIG`, `SQ_TIMEOUT_STATUS`, `SQ_IND_INDEX`, and `SQ_IND_DATA`.
- RAS and EDC accounting through SQC and SQ EDC counter masks, including SEC/DED/FUE fields and per-block counter extraction.
- Thread-trace tooling and trace decoders that must interpret `SQ_THREAD_TRACE_WORD_*` token fields consistently with the hardware.
- Shader tooling, firmware, debuggers, and descriptor builders that use SQ instruction and resource descriptor field definitions to decode or construct GC 9.4.2 words.

## Risks

- Incorrect shift or mask values silently target wrong hardware bits. In this chunk that can break wave debug, SQ command execution, trap delivery, shader descriptor interpretation, watchdog handling, or RAS accounting.
- Some fields are write-sensitive or status-clear fields. For example, SQ timeout status is cleared by writes in consumer code; changing the field interpretation can hide real watchdog failures or leave stale status.
- DSM and error-injection fields are hazardous if used accidentally in production paths. Enabling inject/stall/single-write controls can create artificial faults or severe performance anomalies.
- Per-CU and per-VMID fields require correct instance selection and locking. Consumers already use `grbm_idx_mutex` and `srbm_mutex`; new users must preserve that pattern when programming selected shader engines, CUs, or VMIDs.
- Thread-trace records mix 16-bit-style and 32-bit-style token layouts and split fields across `1_OF_2`/`2_OF_2` words. Decoders must not assume a single flat token width.
- Instruction encoding and resource descriptor macros look like ordinary register masks but may describe ISA or memory descriptor words. Treating those as MMIO registers would be a category error.
- This file is generated metadata. Manual edits are likely to diverge from AMD register specifications and sibling generated headers.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU configurations that include GC 9.4.2 headers, especially `gfx_v9_4_2.c`, `gfx_v9_0.c`, and `amdgpu_amdkfd_aldebaran.c`.
- Static consistency checks that each register name in this chunk has a matching offset in `gc_9_4_2_offset.h`.
- Boot and GFX initialization on Aldebaran/GC 9.4.2 hardware, including golden-register programming and SQ initialization without invalid-register warnings.
- KFD compute queue smoke tests that exercise SQ command paths, trap setup, and VMID-scoped debug behavior.
- Watchdog/RAS tests that enable `SQ_TIMEOUT_CONFIG`, trigger or simulate timeout reporting, read wave state through `SQ_IND_INDEX`/`SQ_IND_DATA`, and verify `SQ_TIMEOUT_STATUS` clearing.
- RAS/EDC validation that reads SQC/SQ SEC, DED, and FUE counters and confirms values are decoded into the expected block names and counts.
- Shader debugger/profiler tests that decode `SQ_THREAD_TRACE_WORD_*` records and wave/instruction words into stable PC, timestamp, CU/SIMD/wave, register, event, and perf-counter data.
- Graphics/compute workloads that stress global memory, LDS, image/buffer descriptors, GDS interactions, trap handling, and XNACK retry behavior, since these paths depend on SQ/SPI fields covered by this chunk.

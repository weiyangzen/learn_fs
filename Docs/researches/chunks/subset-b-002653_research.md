# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 9633-12147

## Purpose

This chunk is generated-style register field metadata for AMD GC 9.2.1 graphics hardware. It defines preprocessor `__SHIFT` and `_MASK` constants for fields in several GC register address blocks: the tail of GCEA arbitration/priority controls, the `gc_tcdec` texture/cache block, the `gc_shdec` shader/compute context block, and the beginning of the `gc_cppdec` command processor block.

The header does not implement algorithms directly. Its purpose is to let AMDGPU code use symbolic field names with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and table-driven golden-register writes instead of embedding raw bit positions. The requested range starts in the middle of `GCEA_IO_WR_PRI_URGENCY_MASK` and ends in the middle of `CP_FATAL_ERROR`, so the merge lane must reconcile those partial register groups with adjacent chunks.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or runtime object types in this range. The exported API surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field lsb.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask, normally with an `L` suffix.
- Register block comments such as `// addressBlock: gc_tcdec`, `// addressBlock: gc_shdec`, and `// addressBlock: gc_cppdec` align the masks with offset definitions in the companion `gc_9_2_1_offset.h`.

Major data groups in this chunk are:

- `GCEA_*`: graphics client/event arbitration fields for IO read/write urgency masks, read/write priority quantization thresholds, SDP arbitration limits, DRAM/GMI/IO priority, virtual-channel credit reservations, request override bits, latency sampling selectors, and two configurable performance counters.
- `TCP_*`, `TC_CFG_*`, `TCI_*`, `TCC_*`, and `TCA_*`: texture/cache control fields for invalidation, status, channel steering, address configuration, credits, L1/L2 load/store/atomic policy, volatile behavior, TCC redundancy/execution disable, DSM controls, L2 writeback/invalidate, soft reset, and cache-array burst controls.
- `SPI_SHADER_*`: per-stage shader program register fields for pixel, vertex, geometry/export, hull/local, and common user data state. The resource masks cover scratch, SGPR/VGPR allocation, priority, float mode, DX10 clamp, debug mode, exception masks, CU group enable/disable, LDS and user-SGPR sizing, TGID/TIDIG component counts, and address fields.
- `COMPUTE_*`: compute dispatch state fields for dispatch dimensions, start/restart coordinates, thread counts, pipeline/perf count enable, program addresses, AQL dispatch packet and scratch base addresses, compute program resource registers, VMID, resource limits, static thread management per shader engine, temporary ring sizing, thread trace, dispatch ID, relaunch, wave restore addresses, checksum, and 16 compute user-data registers.
- `CP_*`, `CPG_*`, `CPC_*`, and `CPF_*`: command processor debug, interrupt, virtual status, graphics error, UTCL1, ring-buffer, and priority/fatal-error fields. The range includes `CP_DFY_*` debug-data fields, `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CPC_INT_*`, `CP_VIRT_STATUS`, `CP_GFX_ERROR`, `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CP_AQL_SMM_STATUS`, ring base/control/read-pointer/write-pointer-poll fields, `CP_INT_CNTL`, `CP_INT_STATUS`, device ID, pipe/ring priority counters, pipe/ring priority selectors, and the first three `CP_FATAL_ERROR` masks.

## Control Flow

This header fragment has no runtime control flow. It participates in control flow only after inclusion by GC 9.2.1-specific drivers or PowerPlay headers:

- Setup paths write register values by composing fields with `REG_SET_FIELD` and the masks from this header.
- Polling paths read status fields such as `TCP_STATUS`, `TCI_STATUS`, `CP_INT_STATUS`, `CP_VIRT_STATUS`, or `CP_DFY_STAT` and branch in the caller.
- Draw/dispatch paths program `SPI_SHADER_*` and `COMPUTE_*` context registers through packets or register writes, after which GPU microcode and hardware execute the actual shader or compute work.
- Ring setup paths program `CP_RB0_BASE`, `CP_RB0_CNTL`, `CP_RB_RPTR_ADDR*`, and `CP_RB_WPTR_POLL_ADDR*`; the CP then consumes indirect buffers and doorbell/write-pointer state asynchronously.
- Interrupt handlers and enable/disable paths use `CP_INT_CNTL` and `CP_INT_STATUS` masks to arm and interpret CP events such as VM doorbell writes, ECC, GPF, timeout, context busy/empty, GFX idle, privileged access, opcode errors, timestamp events, reserved-bit errors, and generic interrupts.

The nearby AMDGPU source tree shows this register family being integrated through `pm/powerplay/hwmgr/vega12_inc.h`, which includes `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h`, and through GC 9.x runtime code that uses the same macro families for ring buffer control and CP interrupt programming.

## State And Persistence Behavior

The macros are compile-time constants and store no state. The state they describe is hardware-owned, mostly volatile, and reset by GPU reset, power-gating, suspend/resume, or ASIC initialization sequences.

Important state classes described by this chunk:

- Arbitration and credit state: `GCEA_*` fields tune priority, burst limits, virtual-channel credits, request chaining, and latency/perf sampling. Bad settings affect request ordering and fairness but are not persisted by this header.
- Cache state: `TCP_INVALIDATE`, `TCC_WBINVL2`, `TCC_SOFT_RESET`, TCC/TCA DSM controls, and L1/L2 policy registers affect cache validity and coherency. Cache contents are hardware state; software must issue the right invalidation/writeback sequence around VM, memory, and shader changes.
- Shader context state: `SPI_SHADER_*` and `COMPUTE_*` fields describe current graphics/compute program addresses, resource allocation, user data, and dispatch parameters. These are context/register state programmed per workload or saved/restored by command processor mechanisms, not by this header.
- Ring state: `CP_RB*_BASE`, `CP_RB*_CNTL`, read-pointer addresses, write-pointer poll addresses, and buffer-size masks bind CP execution to ring buffers in GPU-visible memory. The pointer memory can outlive a register programming sequence, but the register fields are reinitialized by the driver after reset and resume.
- Interrupt/error state: `CP_INT_CNTL` enables events, while `CP_INT_STATUS`, `CP_GFX_ERROR`, and `CP_FATAL_ERROR` report transient hardware conditions. Status and fatal bits must be interpreted with the matching generation's register semantics.

No disk persistence, software serialization, or explicit lifetime management is implemented here.

## Dependencies

This chunk depends on the GC 9.2.1 generated register corpus staying internally synchronized:

- `gc_9_2_1_offset.h` supplies the register offsets for the masks in this file.
- Other generated GC 9.2.1 headers provide defaults and additional address spaces where present.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and golden-register table macros depend on these exact field names.
- The C preprocessor include path must select the GC 9.2.1 header for the target ASIC; using a nearby GC 9.x generation's masks can compile while programming the wrong bits.
- Power-management and graphics initialization code for Vega12/Raven2-class GC 9.x hardware include this header through generation-specific include wrappers, while generic `gfx_v9_0` style code uses matching field families for CP rings, interrupts, cache policy, and shader setup.

## Integration Points

Primary integration points are in the AMDGPU driver tree:

- PowerPlay/SMU include glue: `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h` includes this mask header together with the matching offset header for GC 9.2.1 register programming tables.
- GFX hub and VM/cache integration: GC 9.x GFX hub code uses GC 9.2.1 register masks for address translation, cache, and related register operations on matching ASICs.
- Graphics ring initialization: `CP_RB0_CNTL`, `CP_RB_CNTL`, pointer-address, write-pointer-poll, and buffer-size masks are the field definitions used when the kernel initializes graphics rings and HQD-like queue controls.
- Interrupt integration: `CP_INT_CNTL` and `CP_INT_STATUS` masks connect CP hardware events to AMDGPU interrupt enablement and interrupt-source decoding.
- Shader and compute programming: `SPI_SHADER_*` and `COMPUTE_*` fields line up with command stream state packets and kernel scheduling paths that launch graphics and compute workloads.
- Diagnostics and telemetry: `GCEA_PERFCOUNTER*`, `GCEA_LATENCY_SAMPLING`, `CP_DFY_*`, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, and status masks provide low-level observability for performance, virtualization, and fault handling.

## Risks

- Field drift is high impact: a wrong shift or mask can silently set unrelated hardware bits, especially in dense registers such as `CP_INT_CNTL`, `COMPUTE_PGM_RSRC*`, `SPI_SHADER_PGM_RSRC*`, and `CPF_UTCL1_CNTL`.
- Cross-generation reuse is unsafe. GC 9.2.1 is close to other GC 9.x headers, but offsets, valid bits, and reserved fields can differ across ASIC revisions.
- The chunk boundaries are partial. `GCEA_IO_WR_PRI_URGENCY_MASK` begins before line 9633, and `CP_FATAL_ERROR` continues after line 12147 with additional masks; standalone consumers of this chunk document should not treat those two groups as complete.
- Cache and coherency fields are sensitive. Misprogramming invalidation, volatility, or TCC writeback/invalidate controls can cause stale data, memory-ordering bugs, or GPU hangs.
- Ring-buffer fields encode sizes, alignment, and pointer-address split fields. Errors in `RB_BUFSZ`, `RB_BLKSZ`, `RB_RPTR_ADDR`, or write-pointer poll addresses can make the CP read invalid commands.
- Interrupt masks can create noisy IRQs or hide real faults if status and enable bits are mismatched.
- Shader resource masks control scratch, LDS, SGPR/VGPR allocation, exception behavior, and wave limits; invalid combinations can fail only under specific shader workloads.
- UTCL1 and VM-related fields can affect translation, snooping, invalidation, and dirty-state behavior. These are risky to alter outside known ASIC initialization sequences.

## Test Signals

Useful validation signals for changes touching these definitions are mostly compile-time and hardware/runtime oriented:

- Build coverage for AMDGPU configurations that include `gc_9_2_1_sh_mask.h` through Vega12/GC 9.2.1 include paths.
- Static consistency checks that every register field in this mask header has a matching register offset in `gc_9_2_1_offset.h` and that adjacent generated headers for defaults/offsets agree on register names.
- Boot smoke tests on supported GC 9.2.1 hardware with clean AMDGPU initialization, no invalid register-access warnings, and no early CP/GFX fatal errors.
- Graphics ring tests showing `CP_RB0_CNTL` setup, read/write pointers, doorbells, and fence signaling work after cold boot, GPU reset, and suspend/resume.
- Graphics and compute workload tests that exercise `SPI_SHADER_*` and `COMPUTE_*` state, including scratch-enabled shaders, LDS-heavy kernels, wave limits, and user-data registers.
- VM/cache coherency tests that combine buffer updates, TCC/TCP invalidation/writeback, atomics, and CPU/GPU synchronization.
- Interrupt tests that enable CP context, idle, timestamp, opcode, and fault-related events and confirm `CP_INT_STATUS` bits map to the expected interrupt sources.
- Performance/diagnostic checks for `GCEA_LATENCY_SAMPLING`, `GCEA_PERFCOUNTER*`, CP debug data, and fatal/error status paths where hardware access is available.

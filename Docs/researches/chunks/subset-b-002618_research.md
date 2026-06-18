# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 7181-9637

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains only C preprocessor constants: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit graphics-core register values. There are no functions, structs, enums, includes, local variables, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin inside the tail of `VM_CONTEXT4_CNTL`, then cover most of the GPUVM context-control and invalidate-engine field definitions, UTCL2/VM memory-aperture controls, TCP/TCI/TCC/TCA cache and coherency controls, and the start of shader-program state for pixel and vertex shaders. The chunk ends in the middle of `SPI_SHADER_PGM_RSRC2_VS`; the remaining VS resource masks continue in a later chunk. Although the path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies the bit layouts for GC 9.0 graphics IP registers. AMDGPU code pairs these masks with register addresses from the matching GC 9.0 offset header and uses common helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET` to avoid hard-coded bit positions in VM setup, TLB invalidation, shader setup, cache configuration, reset, diagnostics, and hang analysis.

This chunk describes several major hardware surfaces:

- GPUVM contexts 4 through 15, including context enablement, page-table depth and block size, retry behavior, and protection-fault interrupt/default controls for range, dummy page, PDE0, valid, read, write, and execute faults.
- `VM_CONTEXTS_DISABLE`, which provides per-context disable and preserve-mode controls for contexts 0 through 15.
- Invalidate engines 0 through 17, including semaphore state, invalidate request fields, acknowledge fields, and optional invalidate address-range low/high halves.
- VM page-table base, start, and end addresses for contexts 0 through 15.
- VM shared/decode controls for MMIO, PCI, DRAM, framebuffer, system aperture, HBM aperture, virtual reset, memory low-power, steering, and L1 TLB behavior.
- TCP/TCI/TCC/TCA cache hierarchy controls, status, invalidation, channel steering, address hashing, load/store/atomic policy fields, volatile markers, EDC counters, DSM controls, redundancy, execution disable, writeback/invalidate, soft reset, and burst controls.
- Shader processor interface state for PS and VS: program resource descriptors, program-address low/high fields, user-data dword windows, CU masks, wave limits, late allocation, SGPR/VGPR sizing, float/debug/trap/exception controls, scratch, stream-out, and draw/dispatch enable bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for that field.
- Register address macros live in the companion GC 9.0 offset header and are consumed alongside these field definitions.

Important macro families in this chunk include:

- `VM_CONTEXT4_CNTL` tail and `VM_CONTEXT5_CNTL` through `VM_CONTEXT15_CNTL`: repeated per-VMID context controls. Fields include `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry controls, and interrupt/default enables for protection-fault classes.
- `VM_CONTEXTS_DISABLE`: `DISABLE_CONTEXT0` through `DISABLE_CONTEXT15` plus matching `PRESERVE_CONTEXT*` fields, used to gate or preserve VM contexts across programming sequences.
- `VM_INVALIDATE_ENG*_SEM`: one-bit semaphore fields for invalidate engines 0 through 17.
- `VM_INVALIDATE_ENG*_REQ`: invalidate-request fields for each engine, including `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0/1/2`, `INVALIDATE_L1_PTES`, and `CLEAR_PROTECTION_FAULT_STATUS_ADDR`.
- `VM_INVALIDATE_ENG*_ACK`: per-VMID invalidate acknowledge masks.
- `VM_INVALIDATE_ENG*_ADDR_RANGE_LO32/HI32`: range-invalidation address fragments, with low dword fields split into a 12-bit reserved/alignment field and a 20-bit base field, and high dword fields carrying the upper address bits.
- `VM_CONTEXT*_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `VM_CONTEXT*_PAGE_TABLE_START_ADDR_LO32/HI32`, and `VM_CONTEXT*_PAGE_TABLE_END_ADDR_LO32/HI32`: context page-table roots and aperture boundaries.
- `MC_VM_*`, `MC_SHARED_VIRT_RESET_REQ`, and `MC_MEM_POWER_LS`: VM shared aperture, PCI/DRAM/framebuffer, HBM, steering, reset, and memory low-power register fields.
- `MC_VM_MX_L1_TLB_CNTL`: L1 TLB enable, system-access, request, arbitration, invalidation, fragment, and policy fields.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CHAN_STEER_LO/HI`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, `TCP_BUFFER_ADDR_HASH_CNTL`, and `TCP_EDC_CNT`: texture cache invalidation, status, control, steering, address, credit, hash, and EDC fields.
- `TC_CFG_L1_LOAD_POLICY*`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY*`, `TC_CFG_L2_STORE_POLICY*`, `TC_CFG_L2_ATOMIC_POLICY`, `TC_CFG_L1_VOLATILE`, and `TC_CFG_L2_VOLATILE`: cache policy and volatile-state layouts for L1/L2 load, store, and atomic behavior.
- `TCI_STATUS`, `TCI_CNTL_1`, and `TCI_CNTL_2`: texture cache interface status and control fields.
- `TCC_CTRL`, `TCC_CTRL2`, `TCC_EDC_CNT`, `TCC_EDC_CNT2`, `TCC_REDUNDANCY`, `TCC_EXE_DISABLE`, `TCC_DSM_CNTL*`, `TCC_WBINVL2`, and `TCC_SOFT_RESET`: L2 cache control, counters, redundancy/repair, data-share module policy, writeback/invalidate, and reset fields.
- `TCA_CTRL`, `TCA_BURST_MASK`, `TCA_BURST_CTRL`, `TCA_DSM_CNTL*`, and `TCA_EDC_CNT`: texture cache arbiter control, burst behavior, DSM control, and EDC fields.
- `SPI_SHADER_PGM_RSRC3_PS`, `SPI_SHADER_PGM_LO_PS`, `SPI_SHADER_PGM_HI_PS`, `SPI_SHADER_PGM_RSRC1_PS`, `SPI_SHADER_PGM_RSRC2_PS`, and `SPI_SHADER_USER_DATA_PS_0` through `SPI_SHADER_USER_DATA_PS_31`: pixel-shader program address, resources, CU/wave controls, scratch/trap/exception controls, LDS sizing, and 32 dword user-data windows.
- `SPI_SHADER_PGM_RSRC3_VS`, `SPI_SHADER_LATE_ALLOC_VS`, `SPI_SHADER_PGM_LO_VS`, `SPI_SHADER_PGM_HI_VS`, `SPI_SHADER_PGM_RSRC1_VS`, and the visible beginning of `SPI_SHADER_PGM_RSRC2_VS`: vertex-shader CU/wave controls, program address, resource sizing, VGPR component count, CU group enable, scratch, user SGPR, trap, on-chip LDS, stream-out base enable, exception, PC-base, dispatch/draw, and user-SGPR packing fields.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the detected ASIC.
2. Obtain a register address from the matching offset header or an IP-specific register table.
3. Use these `__SHIFT` and `_MASK` constants, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract fields.
4. Read or write the register via MMIO helpers, SOC15 address helpers, indexed access, command packets, firmware-mediated programming, debugfs, or register-dump paths.

For GPUVM setup, driver code programs per-context page-table base/start/end registers and context control fields, then uses invalidate engine request and acknowledge registers to flush stale PTE/PDE/TLB state. The visible `gmc_v9_0_get_invalidate_req()` consumer pattern builds `VM_INVALIDATE_ENG0_REQ` values by setting per-VMID invalidate, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and protection-fault-status clear fields. `gfxhub_v1_0` style setup also derives per-context and per-engine register distances from the context and invalidate register families, so the repeated layouts in this chunk are part of an array-like hardware programming model.

For the MC, TCP, TCI, TCC, and TCA sections, initialization, golden-register, power-management, reset, and diagnostic code read or write cache, TLB, steering, coherency, EDC, DSM, burst, redundancy, and reset controls. The macros define bit positions only; they do not encode ordering constraints such as cache idle waits, writeback/invalidate completion, soft-reset pulse sequencing, or reserved-bit preservation.

For the SPI shader-program registers, graphics pipeline setup writes program base addresses, per-stage resource descriptors, user SGPR counts, scratch/trap/exception controls, stream-out enables, CU masks, wave limits, and user-data registers before shader waves are launched. These fields are normally driven by command streams, compiler metadata, firmware, or driver state setup rather than by standalone logic in this header.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware-visible register state whose lifetime is controlled by GPU reset, power management, context programming, firmware, command submission, and driver reinitialization.

GPUVM context control, page-table base/start/end, VM aperture, and L1 TLB control registers persist until reprogrammed or reset. They define which VMIDs are enabled, how deep their page tables are, which address ranges are legal, where their page tables live, and how protection faults are surfaced. Bad values can prevent address translation, misroute faults, disable contexts, point VMIDs at the wrong page tables, or hide faults behind default behavior.

Invalidate request, acknowledge, semaphore, and address-range fields are synchronization surfaces. Request bits can be written to initiate flushes, acknowledge bits report completion, and semaphore fields coordinate invalidate engine ownership. These registers are volatile and side-effecting from the driver's perspective; stale polling, wrong VMID masks, or incorrect range packing can leave stale translations active or make the driver wait on the wrong completion bits.

MC shared/aperture and cache hierarchy controls are persistent hardware policy. TCP/TCI/TCC/TCA status and EDC counters are live or sticky observation state, while invalidate, writeback, reset, DSM, redundancy, and execution-disable fields can have immediate side effects. Full-register writes are risky because many controls share registers with reserved or unrelated policy bits.

Shader program registers are persistent graphics pipeline state for the current draw or context. Program address low/high halves, resource descriptors, CU/wave limits, VGPR/SGPR sizing, scratch enablement, trap/exception settings, stream-out enables, late allocation, and user-data dwords must match the compiled shader and command stream. A single shifted field error can allocate the wrong resources, corrupt user SGPR mapping, launch the wrong code address, enable the wrong stream-out bases, or make traps and exceptions unobservable.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` supplies matching register offsets and base-index metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h`, where present for related registers, supplies generated reset/default values.
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` consume the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming pattern.
- MMIO and SOC15 helpers such as `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and IP-version dispatch tables provide the register access path around these constants.

Concrete integration points include:

- `gmc_v9_0` VM invalidation code, which composes `VM_INVALIDATE_ENG0_REQ` fields for per-VMID TLB/PTE/PDE flushes.
- `gfxhub_v1_0` setup code, which maps GC VM context, page-table, invalidate request, and acknowledge registers into the generic AMDGPU VM hub abstraction and relies on the repeated register spacing.
- GART/VMID setup, fault interrupt configuration, page-table programming, context disable/preserve handling, and GPU reset recovery.
- Golden-register and power-management paths that program MC aperture, TCP/TCC/TCA cache, TLB, low-power, EDC, redundancy, or soft-reset controls.
- Register dump, debugfs, hang triage, and performance diagnostics that decode TCP/TCC/TCA status/counters, invalidate acknowledgements, and shader resource state.
- Graphics command submission and shader setup paths that program PS/VS `SPI_SHADER_PGM_*` and `SPI_SHADER_USER_DATA_*` registers from compiler output and command stream state.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes or decodes the wrong hardware bit.
- The chunk starts and ends mid-family. It begins after the `VM_CONTEXT4_CNTL` marker and early fields, and it ends before the remaining `SPI_SHADER_PGM_RSRC2_VS` masks. Adjacent chunks are required for complete family-level documentation.
- The VM context controls are highly repetitive. Copy/paste or generator errors in one context can affect only specific VMIDs, making failures workload- or process-dependent.
- Invalidate engine fields are synchronization-critical. Mispacking `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, L1/L2 invalidation bits, or acknowledge masks can leave stale translations active, clear the wrong fault address status, or hang invalidate waits.
- Address fields are split into low/high halves and may have alignment or unit constraints not represented by full masks. `0xFFFFFFFFL` or broad address masks do not mean arbitrary byte addresses are valid.
- Context disable/preserve bits can interact badly with reset, suspend/resume, SR-IOV, or VM fault recovery if callers treat them as passive state.
- Cache/TLB/DSM/EDC/redundancy/reset fields can be volatile, sticky, write-one-to-clear, pulse-style, or side-effecting depending on hardware semantics not encoded here.
- TCP/TCC/TCA policy registers affect coherency and performance. Wrong load/store/atomic policy, volatile, hash, credit, burst, or DSM fields may cause subtle data hazards or severe performance regressions rather than immediate crashes.
- Shader resource descriptors must match compiler metadata. Incorrect VGPR/SGPR counts, float mode, exception bits, scratch enable, LDS sizing, user SGPR count, or stream-out enables can corrupt execution, lose traps, or break draws only for specific shader stages.
- Reserved bits appear throughout these dense registers. Consumers should preserve reserved bits during read-modify-write unless a documented programming sequence requires a full-register value.

## Test Signals

Useful validation combines generated-data checks, build coverage, and hardware runtime behavior:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h` and `gc_9_0_offset.h`; missing or renamed macros should fail at compile time.
- Mechanically compare this line range against AMD's authoritative GC 9.0 register database. Every visible field should have aligned `__SHIFT` and `_MASK` entries.
- Cross-check registers in this chunk against `gc_9_0_offset.h` for matching address definitions and expected repeated spacing for VM contexts, invalidate engines, and shader user-data windows.
- Static sanity checks for repeated families: VM contexts 5-15 should share the same control layout, invalidate engines 0-17 should share request/ack/semaphore layouts, context page-table base/start/end pairs should have consistent low/high fields, and `SPI_SHADER_USER_DATA_PS_0` through `_31` should remain full-width data fields.
- GPUVM tests should cover GART enable/disable, VMID setup, per-VMID invalidate request/ack polling, range invalidation where supported, protection-fault reporting, and reset/suspend/resume recovery.
- Memory stress tests should verify no stale translations or coherency failures after PTE/PDE updates, context disable/preserve transitions, and cache/TLB invalidations.
- Cache and coherency validation should exercise TCP/TCC/TCA invalidation, writeback/invalidate, EDC counter readout, DSM policy, volatile policy, and soft reset paths while watching for stuck busy/status bits or repeated GPU resets.
- Shader execution tests should cover PS and VS resource programming, user SGPR/user-data mapping, scratch usage, trap/exception behavior, stream-out paths, CU masks, wave limits, late allocation, and program-address packing.
- Debug and hang-triage signals include correct decode of invalidate acknowledgements, VM fault status, TCP/TCC/TCA status/counters, shader resource registers, and absence of unexpected protection-fault storms, rendering corruption, shader launch failures, cache incoherency, or reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002618`. It covers lines 7181-9637 of `gc_9_0_sh_mask.h`. The previous chunk owns the beginning of `VM_CONTEXT4_CNTL`, and a later chunk owns the remainder of `SPI_SHADER_PGM_RSRC2_VS` plus following shader/register definitions. The final per-file research should reconcile those artificial boundaries before describing the complete generated GC 9.0 shift/mask map.

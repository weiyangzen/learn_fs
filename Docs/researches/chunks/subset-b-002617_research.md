# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 4815-7180

## Scope

This chunk is a generated bitfield slice from the AMD GC 9.0 register shift/mask header. It starts at the tail of `GDS_EDC_GRBM_CNT`, covers the remainder of the GDS diagnostics block, all of the visible `gc_rbdec` and `gc_rmi_rmidec` blocks in this range, the `gc_utcl2_atcl2dec` block, most of the `gc_utcl2_vml2pfdec` block, and begins the `gc_utcl2_vml2vcdec` VM context-control block through the first fields of `VM_CONTEXT4_CNTL`.

The file contains preprocessor constants only. There are no C functions, structs, variables, allocation paths, locks, I/O routines, or executable branches in this chunk. Its exported interface is the conventional AMD register-field pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used by `REG_SET_FIELD`, `REG_GET_FIELD`, and direct bit operations.

Major register families covered here include GDS EDC/error-injection fields, DB depth-buffer debug and DFSM controls, CB/color-buffer hardware controls, GB address and tile-mode topology fields, RB disable/redundancy fields, RMI crossbar/UTCL1/scoreboard/status controls, ATC L2 cache/translation controls, GCVM L2 cache and protection-fault controls, ECC/parity counters, and VM context 0-4 control fields.

## Purpose

The purpose of this chunk is to publish the bit-level ABI between GC 9.0 hardware registers and AMDGPU driver code. The sibling `gc_9_0_offset.h` file defines the register addresses; this header defines how to compose and decode the 32-bit register values once the driver has selected an address.

The covered fields fall into several functional groups:

- GDS diagnostics: `GDS_EDC_OA_DED`, `GDS_DSM_CNTL`, `GDS_EDC_OA_PHY_CNT`, `GDS_EDC_OA_PIPE_CNT`, `GDS_DSM_CNTL2`, and `GDS_WD_GDS_CSB` describe GDS on-array/pipe ECC status, single-write/error-injection controls, injection delay selection, and watchdog counter fields.
- DB/CB/RB render backend controls: `DB_DEBUG*`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH*`, `DB_RMI_CACHE_POLICY`, `DB_DFSM_*`, `CB_HW_CONTROL*`, `CB_HW_MEM_ARBITER_*`, and `CB_DCC_CONFIG` define depth/stencil compression, HiZ/HiS, cache, FIFO, arbitration, DCC, fast-clear, and debug/erratum control bits.
- Graphics backend topology: `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `GB_TILE_MODE0`-`31`, `GB_MACROTILE_MODE0`-`15`, `CC_RB_*`, and `GC_USER_RB_*` encode pipe counts, shader engines, render-backend counts, interleave sizes, tile/macro-tile mode tables, backend maps, and harvested/disabled RB state.
- RMI path controls: `RMI_GENERAL_*`, `RMI_SUBBLOCK_STATUS*`, `RMI_XBAR_*`, `RMI_UTCL1_*`, `RMI_TCIW_FORMATTER*_CNTL`, `RMI_SCOREBOARD_*`, `RMI_CLOCK_CNTRL`, `RMI_XNACK_DEBUG`, and `RMI_SPARE*` describe the render-memory interface, UTCL1 probe behavior, XNACK handling, TCIW formatting, crossbar arbitration, scoreboard flush/invalidation state, clock controls, and status/error reporting.
- Translation and VM L2 controls: `ATC_L2_*`, `VM_L2_CNTL*`, `VM_L2_STATUS`, `VM_DUMMY_PAGE_FAULT_*`, `VM_L2_PROTECTION_FAULT_*`, identity aperture registers, MM group return classes, bank-selection reservations, parity controls, clock-gating controls, ECC index/count registers, and `VM_CONTEXT0_CNTL` through the start of `VM_CONTEXT4_CNTL` define address translation cache, VM L2 cache, invalidation, page-fault policy, VMID/context enablement, and fault-interrupt behavior.

Although this repository path is under a `ceph-client` source tree, the content is AMD GPU register metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

This chunk's "API" is the macro namespace consumed by AMDGPU and KFD source files. Typical consumers include:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)`, which expand through the `__SHIFT` and `_MASK` definitions in this file.
- `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, and `SOC15_REG_ENTRY_OFFSET`, which perform the actual MMIO accesses to addresses from `gc_9_0_offset.h`.
- GC 9.0 hub setup code in `amdgpu/gfxhub_v1_0.c` and `amdgpu/mmhub_v1_0.c`, which programs VM page-table base registers, system apertures, TLB/cache registers, VMID context control, invalidation, fault-default policy, and clock/power gating.
- GC 9.0 memory-controller and fault paths in `amdgpu/gmc_v9_0.c`, including VM fault interrupt state, processing, TLB flush, PASID mapping, and page-table entry/PDE flag handling.
- KFD GC 9 queue paths such as `amdkfd/kfd_mqd_manager_v9.c` and `amdgpu/amdgpu_amdkfd_gfx_v9.c`, which include this header for compute-queue and VM-related register field definitions.
- Topology save/restore and compatibility code in older generation files such as `amdgpu/cik.c`, where similar `GB_ADDR_CONFIG`, tile-mode, and macro-tile-mode tables illustrate how these hardware tables are saved, restored, or exposed.

The highest-value field groups for runtime integration are:

- `GB_ADDR_CONFIG__NUM_PIPES`, `PIPE_INTERLEAVE_SIZE`, `MAX_COMPRESSED_FRAGS`, `NUM_SHADER_ENGINES`, and `NUM_RB_PER_SE`, because later GFX code reads these fields to derive graphics topology.
- `GB_TILE_MODE*` and `GB_MACROTILE_MODE*`, because they define the hardware tiling table that surface-addressing code and firmware-visible register state depend on.
- `VM_L2_CNTL*`, `VM_L2_PROTECTION_FAULT_CNTL*`, and `VM_CONTEXT*_CNTL`, because hub setup code uses these fields to enable VM contexts, configure page-table depth/block size, classify faults, select retry/default behavior, and enable or suppress fault interrupts.
- `ATC_L2_*` and `RMI_UTCL1_*`, because they sit on the translation/cache path used by ATS, UTCL1 probes, XNACK, VMID invalidation, and memory-system status reporting.
- `GDS_*_EDC*` and `VM_L2_*ECC*`, because RAS paths can use them for SEC/DED counters, ECC index selection, and error-count reporting.

## Control Flow

The header has no direct control flow. Runtime sequencing is imposed by driver code and the hardware blocks that consume the composed register values.

Typical VM hub setup driven by these macros follows this pattern:

1. `gfxhub_v1_0` or `mmhub_v1_0` writes page-table base, aperture, and default page registers using offsets from the matching offset header.
2. The driver composes `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_CNTL4` values to enable the L2 cache, select cache/invalidation behavior, set bank selection, and configure page-cache sizing.
3. It programs `VM_CONTEXT0_CNTL` and later contexts with `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry policy, default-fault behavior, and interrupt enables.
4. It programs `VM_L2_PROTECTION_FAULT_CNTL` and related registers to decide which faults default, which generate interrupts, whether subsequent status-address updates are allowed, and where default fault addresses point.
5. TLB invalidation and fault processing code later reads status registers, writes invalidation requests, and uses the configured masks to interpret protection-fault status and VM context state.

Typical render-backend and topology flow is more static:

1. Firmware, BIOS, or early driver init establishes `GB_ADDR_CONFIG`, tile-mode, macro-tile-mode, backend-map, and harvested RB state.
2. Driver code reads those registers and decodes field values to populate ASIC topology and surface-addressing decisions.
3. DB/CB/RMI tuning or golden-register programming may write selected debug, cache-policy, FIFO, arbitration, DCC, and clock-control fields during init, resume, reset, or workaround setup.
4. Rendering, depth/stencil, compression, fast-clear, and memory-interface behavior then follows the programmed hardware state.

Error and diagnostic flows use the same constants to poll or clear status fields. Examples include RMI busy/error bits, ATC/VM L2 parity information, VM protection-fault status/address registers, and GDS/VM L2 ECC counters.

## State And Persistence Behavior

This header stores no software state. It defines encodings for hardware state that may be persistent across a GPU power state, reset domain, or driver save/restore boundary depending on the owning block.

Important hardware state represented by this chunk includes:

- Persistent or semi-persistent configuration: GB address topology, tile/macro-tile mode tables, RB redundancy/backend-disable masks, DB/CB hardware-control tuning, RMI crossbar/arbitration settings, ATC/VM L2 cache policy, VM context enablement, page-table depth/block size, and protection-fault defaults.
- Transient status: DB/RMI FIFO/busy signals, RMI scoreboard and flush progress, ATC L2 busy/parity status, VM L2 busy/context-domain status, fault status, and XNACK/UTCL1 detection bits.
- Latched or counted diagnostics: GDS EDC SEC/DED counters, VM L2 ECC counts, parity error information, and protection-fault status/address registers.
- Command-like bits: cache/TLB invalidation bits, fault-status clear/update-control bits, error-injection controls, clock-gating overrides, and RMI configuration-update bits.

Consumers must treat status, counter, and strobe fields differently from durable configuration fields. For example, `VM_L2_PROTECTION_FAULT_CNTL__CLEAR_PROTECTION_FAULT_STATUS_ADDR` is a control action, while `VM_L2_PROTECTION_FAULT_STATUS` reports a captured event; `VM_CONTEXT*_CNTL` fields persist as context policy until reprogrammed; and `VM_L2_MEM_ECC_CNT` is a hardware-maintained count read through the selected ECC index.

## Dependencies And Integration Points

This chunk depends on the AMD generated-register-header convention and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which supplies matching GC 9.0 register addresses.
- Any GC 9.0 default/golden-register tables that assume these fields retain the generated layout.
- Core AMDGPU MMIO helpers and field helpers, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.
- `amdgpu/gfxhub_v1_0.c` and `amdgpu/mmhub_v1_0.c`, where hub initialization programs `VM_L2_*`, `VM_CONTEXT*_CNTL`, fault handling, invalidation, and clock/power-related fields.
- `amdgpu/gmc_v9_0.c`, which owns GC 9 memory management, page fault interrupts, TLB flushes, PASID mappings, VM PDE/PTE flag generation, ECC interrupt handling, and hub selection.
- `amdgpu/gfx_v9_0.c`, KFD GC 9 code, and SOC15 discovery/setup paths that include `gc_9_0_sh_mask.h` for queue, graphics, compute, and topology register work.
- Hardware or firmware programming of GB tile/macro-tile tables and RB harvest state. The driver-side masks must match the values loaded by firmware/BIOS and the expectations of surface-address calculations.

The chunk is source-tree-aligned to one generated header. It should be merged with adjacent chunks for whole-file conclusions because it starts with only the final `GDS_EDC_GRBM_CNT__UNUSED_MASK` line and ends partway through the `VM_CONTEXT4_CNTL` field list.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly but write the wrong hardware bits. The most severe cases are VM L2/context/fault fields, where misprogramming can cause page faults, lost interrupts, bad fault attribution, VMID isolation failures, or GPU hangs.
- Repeated register families are mechanically fragile. `GB_TILE_MODE0`-`31`, `GB_MACROTILE_MODE0`-`15`, and `VM_CONTEXT0_CNTL`-`4` have near-identical layouts; a one-register drift is easy to miss in review.
- Tile and topology fields must match the ASIC's actual fuse/harvest layout. Incorrect `GB_ADDR_CONFIG`, RB disable/redundancy, or backend map values can break surface addressing, compression, render backend routing, or user-visible topology reporting.
- Debug and workaround fields are not harmless. `DB_DEBUG*`, `CB_HW_CONTROL*`, `DB_DFSM_*`, RMI arbitration, and cache-policy fields can disable optimizations, force cache misses, alter compression/decompression, or change memory-request behavior.
- VM fault fields combine default action and interrupt behavior. Enabling defaults without interrupts can hide faults; enabling interrupts without correct status-clear/update sequencing can flood or lose fault records.
- Status and strobe bits require sequencing. Invalidation, fault-status clear, RMI config update, and error-injection controls need the polling/ordering rules from the owning driver code and hardware spec; the macros do not encode those rules.
- RAS counters and ECC index fields can be read from the wrong register bank or instance if the consumer uses the wrong hub, xcc/instance, or SOC15 block index.
- The chunk boundary hides neighboring definitions. The final report must connect this chunk to the previous GDS fields and the following remainder of `VM_CONTEXT4_CNTL` plus subsequent VM context registers before claiming complete coverage.

## Test Signals

Useful validation signals are mostly integration and hardware bring-up tests:

- Build AMDGPU and KFD with GC 9 support enabled. Missing or renamed macros should fail in `gfxhub_v1_0.c`, `mmhub_v1_0.c`, `gmc_v9_0.c`, `gfx_v9_0.c`, and GC 9 KFD queue-management files.
- Boot GC 9 hardware and verify GART/VM initialization succeeds: VM contexts enable, page-table depth/block size match expectations, GPU virtual memory mappings work, and TLB flush paths complete without timeout.
- Exercise VM fault handling through invalid, permission, read, write, execute, dummy-page, and range faults. Check that `VM_L2_PROTECTION_FAULT_STATUS` and address registers identify the expected VMID/client/fault type and that interrupts/default handling follow policy.
- Run graphics rendering with tiled, compressed, MSAA, depth/stencil, fast-clear, and DCC surfaces. Incorrect GB/DB/CB/RB masks would show as corruption, hangs, failed clears, bad compression, or mismatched topology.
- Validate suspend/resume and GPU reset paths, because tile-mode/topology tables, VM L2 controls, context controls, and fault policy must be restored consistently after reset-domain loss.
- Run RAS/ECC diagnostics where available, including GDS EDC and VM L2 ECC count queries, and verify SEC/DED counters move in the expected fields.
- Check RMI/UTCL1/XNACK behavior under compute memory pressure and page migration/retry scenarios. Relevant signals include RMI busy/error status, scoreboard flush state, UTCL1 fault/retry/PRT detection, and XNACK-per-VMID reporting.

## Cross-Chunk Notes

This chunk starts in the middle of the GDS EDC area at `GDS_EDC_GRBM_CNT__UNUSED_MASK`, so complete GDS analysis needs the previous chunk. It ends after the first seven `VM_CONTEXT4_CNTL` shift definitions and before the corresponding masks and later VM context registers, so complete VM context-control analysis needs the next chunk. The merge/reconciliation lane should join those boundaries before producing the final per-file research document.

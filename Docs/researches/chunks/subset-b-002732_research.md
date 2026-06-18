# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_0_sh_mask.h lines 5144-6116

## Scope

This chunk is the final section of the generated AMD GMC 7.0 shift/mask header. It contains preprocessor constants only and ends with the header guard close. The range starts in the tail of `GMCON_MISC` stutter-control fields, then covers complete field-mask families for GMC stutter/power control, VM L2 and VM context control, page-table and fault registers, PRT aperture control, MC arbitration, fused DRAM aperture and bank mapping, Garlic/isoc arbitration, clock-gating dataport, and CHUB ATC L1 debug/status registers.

The file is hardware metadata, not executable logic. There are no functions, structs, enums, variables, allocations, locks, or local control-flow constructs in this chunk.

## Purpose

The purpose of this section is to publish the bit-level ABI for GMC 7.0 MMIO registers. Each hardware field is represented with the generated AMD convention:

- `<REGISTER>__<FIELD>_MASK`, used to isolate or clear the field.
- `<REGISTER>__<FIELD>__SHIFT`, used to position a field value.

Consumers pair these definitions with register offsets from `gmc/gmc_7_0_d.h` and helper macros such as `REG_SET_FIELD(value, reg, field, field_val)` and `REG_GET_FIELD(value, reg, field)`. Those helpers paste `reg` and `field` into the `__SHIFT` and `_MASK` names, so the spelling and exact masks in this file are a compile-time contract with the rest of AMDGPU.

Although the repository path is under a `ceph-client` source mirror, this chunk describes AMD GPU memory-controller and virtual-memory hardware. It has no Ceph or distributed-filesystem behavior.

## Important Macro Families

### GMC Stutter, Power, Save/Restore, and PGFSM

The opening `GMCON_*` fields cover memory-controller stutter and power behavior:

- `GMCON_MISC` tail fields include disabling GMC offline, locking critical registers, deep-sleep mode selection, and forced stutter-refresh allowance.
- `GMCON_MISC2` exposes render-engine memory power-control overrides, non-display idle and stutter-refresh hold thresholds, LPT target, ignore-arbitration-busy, extended offline, and timer-pulse override fields.
- `GMCON_STCTRL_REGISTER_SAVE_RANGE0..2` and `GMCON_STCTRL_REGISTER_SAVE_EXCL_SET0..1` define register save/restore ranges and exclusions for stutter-control state preservation.
- `GMCON_PERF_MON_CNTL0/1` and `GMCON_PERF_MON_RSLT0/1` define start/stop thresholds, trigger modes, monitor IDs, wrap behavior, and result counters for GMC-local performance monitoring.
- `GMCON_PGFSM_CONFIG`, `GMCON_PGFSM_WRITE`, and `GMCON_PGFSM_READ` describe an indirect power-gating FSM access path with address, power-up/down, read/write, select, SRBM override, readback, selected PGFSM, and busy status fields.
- `GMCON_MISC3`, `GMCON_MASK`, and `GMCON_DEBUG` expose MCC/MCD disable masks, forced PGFSM completion, stutter-handshake and busy masks for ACP/VCE clients, GFX stall/clear, and miscellaneous debug flags.

These fields represent low-level power-management and debug controls. Some are durable configuration fields; others, such as PGFSM read/write and forced command-done behavior, are sequencing-sensitive hardware commands or status bits.

### VM L2 Cache and Invalidation

`VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_STATUS` define the GPU virtual-memory L2 cache contract:

- L2 enable, fragment processing, PTE/PDE endian-swap modes, PDE0 tag generation, LRU update-by-write behavior, default-page-out-to-system-memory, PDE0 split mode, effective queue size, PDE fault classification, context1 identity access, identity fragment size, and 4K/bigK tag-index swaps.
- TLB/cache invalidation command bits, per-domain invalidation disable, bigK cache optimization disable, bigK VMID mode, invalidate cache mode, and PDE cache effective size.
- Bank select, update mode, wildcard reference value, bigK fragment size, associativity, effective 4K/bigK/PDE sizes, and force-miss debug fields.
- `VM_L2_STATUS` busy and per-context-domain busy bits.

Same-generation GMC setup code in `amdgpu/gmc_v7_0.c` programs these fields during GART enable: it enables L2 cache and fragment processing, enables PTE/PDE LRU updates, sets effective queue size and identity-access mode, requests L1/L2 invalidation, and configures bank/fragment fields from `adev->vm_manager.fragment_size`.

### VM Contexts, Page Tables, Faults, and PRT

The VM context section covers VMID/context enablement, page-table shape, fault policy, invalidation, and fault reporting:

- `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` define context enable, page-table depth, fault interrupt/default/save policy for range, dummy-page, PDE0, valid, read, write, and privileged faults, plus page-table block size.
- `VM_DUMMY_PAGE_FAULT_CNTL` and `VM_DUMMY_PAGE_FAULT_ADDR` define dummy-page fault behavior and address matching.
- `VM_CONTEXT0_CNTL2` and `VM_CONTEXT1_CNTL2` define fault-status-address clearing, subsequent fault interrupt/update behavior, and wait-for-idle-on-invalidate.
- `VM_CONTEXT0..15_PAGE_TABLE_BASE_ADDR` provide 28-bit physical page-number fields for page-directory base programming. Contexts 0-7 appear later in the chunk; contexts 8-15 appear earlier.
- `VM_INVALIDATE_REQUEST` and `VM_INVALIDATE_RESPONSE` provide one bit per domain/context 0-15 for invalidation request and completion.
- `VM_PRT_APERTURE0..3_LOW_ADDR/HIGH_ADDR` and `VM_PRT_CNTL` define partially resident texture aperture bounds and unmapped-access fault suppression/caching behavior.
- `VM_CONTEXTS_DISABLE` exposes a disable bit for each context 0-15.
- `VM_CONTEXT0/1_PROTECTION_FAULT_STATUS`, `MCCLIENT`, `ADDR`, and `DEFAULT_ADDR` expose protection bits, memory client ID/name, read/write direction, VMID, logical fault page, and default physical page.
- `VM_FAULT_CLIENT_ID` defines client matching and mask fields.
- `VM_CONTEXT0/1_PAGE_TABLE_START_ADDR` and `END_ADDR` define logical page-number ranges.
- `VM_DEBUG`, `VM_L2_CG`, `VM_L2_BANK_SELECT_MASKA/B`, context1 identity aperture low/high, and identity physical offset fields provide debug, clock-gating, bank-mask, and identity-mapping support.

Direct usage of this exact header appears in `amdgpu/gfx_v7_0.c`, which includes `gmc/gmc_7_0_d.h` and `gmc/gmc_7_0_sh_mask.h`. That file emits `mmVM_INVALIDATE_REQUEST` into an SDMA/GFX command stream and decodes `MC_FUS_DRAM*_BANK_ADDR_MAPPING` with `REG_GET_FIELD`. The broader CIK GMC implementation in `amdgpu/gmc_v7_0.c` uses the same GMC 7-era field names from the 7.1 header to initialize VM L2, context0 GART, context1-15 GPUVM, PRT, invalidation, and VM fault reporting.

### MC Arbitration and Fused DRAM Addressing

The `MC_ARB_HARSH_*` family defines read/write arbitration tuning for groups 0-7:

- `MC_ARB_HARSH_EN_RD/WR` selects transaction, bandwidth, fixed, and stutter priority enable masks.
- `TX_HI`, `TX_LO`, `BWPERIOD`, `BWCNT`, and `SAT` registers pack 8-bit values for four groups per register, split into group 0-3 and group 4-7 halves and read/write variants.
- `MC_ARB_HARSH_CTL_RD/WR` defines force-highest group masks, harsh round-robin, bank-age-only, legacy harsh mode, bandwidth counter catch-up, stutter mode, forced stall, and perf monitor selection.

The `MC_FUS_DRAM*` and related fields describe fused system/DRAM mapping:

- `MC_FUS_DRAM0/1_CS0..CS3_BASE` expose chip-select enable and split base address fields.
- `MC_FUS_DRAM0/1_BANK_ADDR_MAPPING` expose DIMM address map, bank swizzle, and bank swap.
- `MC_FUS_DRAM0/1_CTL_BASE`, `CTL_LIMIT`, `CTL_HIGH_01/23`, and `MODE` expose DCT selection, interleave enable/address, base/limit, DRAM hole validity/offset, high-address offsets, and GDDR5 enable.
- `MC_FUS_DRAM_APER_BASE/TOP`, `C6SAVE_APER_BASE/TOP`, and `APER_DEF` define DRAM aperture bounds, C6-save aperture bounds, default aperture behavior, and a lock bit for fused DRAM registers.

`gfx_v7_0.c` directly reads `MC_FUS_DRAM0_BANK_ADDR_MAPPING` and `MC_FUS_DRAM1_BANK_ADDR_MAPPING` and extracts `DIMM0ADDRMAP`/`DIMM1ADDRMAP`; this ties the generated masks to runtime topology/addressing decisions.

### Garlic, Clock-Gating Dataport, and CHUB ATC L1

The tail of the chunk covers additional memory-client and translation controls:

- `MC_FUS_ARB_GARLIC_ISOC_PRI` enables token-urgent, priority-urgent, and isochronous read behavior for DMIF, UVD, VCE, MCIF, UMC, VCEU, and ACP clients; it also defines request-priority override enables/values, promotion/token/priority override values, Garlic request credits, and late multimedia release behavior.
- `MC_FUS_ARB_GARLIC_CNTL` defines read/write response FIFO pointer initialization, 64-byte write enable, EDC response enable, and outstanding read/write response limits.
- `MC_FUS_ARB_GARLIC_WR_PRI` and `WR_PRI2` define 2-bit write priority fields for graphics, display/media, DMA, firmware, semaphore, shader, SMU, SAM, and ACP clients.
- `MC_CG_DATAPORT` exposes a raw 32-bit data field for clock-gating data access.
- `CHUB_ATC_L1_DEBUG_TLB` defines TLB debug controls: fragment disable, invalidate-by-address-range disable, effective CAM/work-queue size, L1-to-L2 and L1-to-RPB credits, ECO debug bits, invalidate-all, and disable caching of untranslated returns.
- `CHUB_ATC_L1_STATUS` exposes busy, deadlock-detection, and bad `NEED_ATS` status bits.

These fields are integration points for display/media memory QoS, clock/power debug, and APU CHUB address-translation behavior.

## Control Flow

There is no runtime control flow in this header. Runtime behavior is supplied by the AMDGPU driver:

1. A C file includes `gmc_7_0_d.h` for register addresses and this file for field masks/shifts.
2. Code reads or composes a 32-bit register value with `RREG32`, `WREG32`, `amdgpu_ring_write`, `amdgpu_ring_emit_wreg`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
3. Hardware observes the MMIO or ring write and changes VM, cache, fault, arbitration, aperture, power, or debug state.
4. Driver code polls or decodes status where required, such as invalidation response, L2 busy bits, fault-status registers, PGFSM busy/readback, or CHUB ATC L1 status.

The macros do not encode ordering, polling, or timeout policy. Consumers must still follow the sequencing in the owning IP block code and hardware specification.

## State and Persistence Behavior

This chunk stores no software state. The persistent state it describes is hardware state in GMC registers.

Configuration-style state includes VM L2 cache enable/mode, VM context enable/page-table shape, default fault-page behavior, PRT apertures, context base/start/end addresses, context-disable masks, clock-gating enable/memory light-sleep fields, MC arbitration thresholds, fused DRAM apertures and mappings, Garlic client priorities, response limits, and CHUB ATC L1 sizing/credit controls.

Status or event state includes L2 busy and context-domain busy flags, invalidation completion bits, VM protection fault status/client/address fields, PGFSM readback and busy state, performance monitor result counters, CHUB ATC L1 busy/deadlock/bad-ATS bits, and debug flags.

Some fields are likely self-clearing or command-like hardware inputs rather than durable settings, especially VM invalidation request bits, PGFSM read/write and power-up/down commands, forced PGFSM command-done bits, forced stall/debug fields, and TLB invalidate-all. The header does not distinguish read-only, write-one-to-clear, sticky, or self-clearing behavior; that behavior comes from hardware documentation and the runtime driver paths.

## Dependencies and Integration Points

Required matching files and helpers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_0_d.h` supplies the `mm...` register offsets for this mask namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h` defines `REG_SET_FIELD` and `REG_GET_FIELD`, which consume the generated `__SHIFT` and `_MASK` names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c` directly includes `gmc/gmc_7_0_d.h` and `gmc/gmc_7_0_sh_mask.h`; in this file, the chunk's `VM_INVALIDATE_REQUEST` and `MC_FUS_DRAM*_BANK_ADDR_MAPPING` definitions are directly relevant.

Important same-generation integration patterns are visible in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`, even though that implementation includes the closely related 7.1 generated header. It demonstrates how this field namespace is meant to be used for GART enable/disable, VM context programming, TLB invalidation, PRT setup, VM fault default policy, fault decoding, and `VM_L2_CG` clock-gating enable/light-sleep arrays.

Other integration points include command submission and DMA paths that write `mmVM_INVALIDATE_REQUEST` through rings, VM fault IRQ paths that decode protection status and client fields, power-management paths that touch GMC clock-gating and stutter registers, and topology or memory-addressing code that reads fused DRAM mapping registers.

## Risks and Edge Cases

- Bitfield drift is high impact. A wrong mask or shift can compile cleanly but program unrelated hardware bits, causing VM faults, stale TLBs, hangs, incorrect DRAM mapping, broken client QoS, or power-management instability.
- The repeated VM context and invalidate-domain fields are easy to corrupt mechanically. Contexts 0-15 span multiple register families, and contexts 8-15 page-table base fields appear before context 0-7 in this chunk.
- `REG_SET_FIELD`/`REG_GET_FIELD` rely on exact token names. Renaming a field, changing the double-underscore convention, or mixing `gmc_7_0_d.h` with the wrong mask header can break builds or silently target the wrong generation's layout.
- VM fault controls have policy implications. Enabling default-page redirection, disabling PRT faults, or saving/interrupting fault classes incorrectly can hide invalid memory accesses or flood fault interrupts.
- VM invalidation must be sequenced with page-table writes. Missing the request bit, using the wrong domain bit, or ignoring response/busy state can leave stale translations visible to GPU clients.
- Power, stutter, PGFSM, and clock-gating fields are timing-sensitive. Incorrect overrides or forced-done/stall bits can interfere with suspend/resume, idle entry, memory light sleep, or hardware power-gating state machines.
- MC arbitration and Garlic priority fields affect multiple memory clients. Bad priority, saturation, outstanding limit, or isochronous settings can produce display/media underruns, compute starvation, or hard-to-reproduce bandwidth regressions.
- Fused DRAM address and aperture fields describe physical topology. Wrong decoding or writes to lockable fused DRAM registers can produce invalid address routing or make later correction impossible until reset.
- The final `#endif` is included in this chunk. Merge tooling should treat this as the end of `gmc_7_0_sh_mask.h`, not as the end of a logical register family.

## Test and Validation Signals

Useful validation is mostly build coverage plus hardware behavior:

- Build AMDGPU with CIK/GFX7 support enabled so `gfx_v7_0.c` includes `gmc/gmc_7_0_d.h` and `gmc/gmc_7_0_sh_mask.h`; this catches missing or renamed generated macros used by `REG_GET_FIELD` and ring writes.
- Mechanically compare this header against AMD's generated GMC 7.0 register database and verify each field has a coherent `_MASK`/`__SHIFT` pair, especially repeated context, arbitration, DRAM, and Garlic priority families.
- Exercise VM/GART bring-up on supported GFX7/CIK hardware: context0 GART access, user VMIDs 1-15, page-table base updates, TLB invalidation, dummy/default page handling, and suspend/resume restoration.
- Trigger and inspect VM faults to validate `VM_CONTEXT*_PROTECTION_FAULT_STATUS`, `MCCLIENT`, `ADDR`, `DEFAULT_ADDR`, and fault-default/interrupt policy bits.
- Test PRT paths by enabling/disabling PRT fault suppression and verifying aperture low/high bounds and unmapped-access behavior.
- Run memory bandwidth, display, UVD/VCE/ACP, SDMA, and graphics workloads together to expose regressions in MC arbitration, Garlic isochronous/priority, and outstanding response limits.
- Validate power-management paths with clock-gating, memory light sleep, stutter entry/exit, deep sleep, and suspend/resume; watch for hangs around PGFSM busy/readback and stutter-control overrides.
- On APU/CHUB systems, monitor CHUB ATC L1 status for stuck busy, deadlock detection, bad ATS signaling, and TLB invalidation behavior.

## Cross-Chunk Notes

Earlier chunks of `gmc_7_0_sh_mask.h` define the preceding GMC, MC, VM, ATC, and clock/power field families. This chunk starts mid-register at `GMCON_MISC__STCTRL_DISABLE_GMC_OFFLINE__SHIFT` and ends the file. The final per-file report should merge this with prior chunks before making complete claims about all GMC 7.0 registers or all VM/GMC power-management fields.

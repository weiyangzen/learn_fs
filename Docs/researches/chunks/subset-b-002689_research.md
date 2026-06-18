# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 9541-11973

## Scope

This chunk covers the GC 9.4.3 shift/mask definitions from the tail of `UTCL2_CE_ERR_STATUS_HI` through the beginning of `TCC_CTRL2`. It is generated hardware-description data, not executable C logic. The definitions describe bit positions and bit masks for several GC address blocks:

- `xcd0_gc_utcl2_vml2vcdec`: VM context control registers, VMID context-disable bits, VM invalidation engines, invalidation ACKs, invalidation address ranges, and per-context page-table base/start/end addresses.
- `xcd0_gc_utcl2_vmsharedpfdec`: VM shared memory-controller aperture, PCI, power, HBM, XGMI local-frame-buffer, steering, and clock-gating controls.
- `xcd0_gc_utcl2_vmsharedvcdec`: framebuffer, AGP, system aperture, and L1 TLB controls.
- `xcd0_gc_utcl2_l2tlbdec`: L2 TLB status and GPUVA/VMID translation-assist request/response fields.
- `xcd0_gc_tcdec`: texture/cache pipeline controls including TCP invalidate/status/control, channel steering, cache policy registers, EDC/RAS reporting, TCI controls, and the start of TCC controls.

The line range begins inside a register definition: only the remaining masks for `UTCL2_CE_ERR_STATUS_HI` are present here, while its shifts and earlier masks are in the preceding chunk. The range also ends inside `TCC_CTRL2`: the first three masks are in this chunk and the remaining `TCC_CTRL2` masks continue in the next chunk. Merge/reconciliation should account for those boundary splits.

## Purpose

`gc_9_4_3_sh_mask.h` supplies symbolic bitfield metadata for the AMDGPU GC 9.4.3 IP block. These macros let driver code build and decode MMIO register values without hard-coding numeric bit offsets at each call site. For example, AMDGPU code can use `REG_SET_FIELD(tmp, VM_CONTEXT0_CNTL, ENABLE_CONTEXT, 1)` and rely on this header to provide `VM_CONTEXT0_CNTL__ENABLE_CONTEXT__SHIFT` and `VM_CONTEXT0_CNTL__ENABLE_CONTEXT_MASK`.

For this chunk, the main purpose is to expose the programmable surface for graphics-hub virtual memory and cache-control hardware:

- VM context setup for VMIDs 0 through 15, including context enablement, page-table depth, page-table block size, retry policy for invalid-page/protection faults, and interrupt/default handling for range, dummy-page, PDE, valid, read, write, execute, and secure protection faults.
- VM invalidation machinery for engines 0 through 17. The macros define semaphore bits, request payloads, acknowledge fields, and optional address range registers used to flush page-table and translation caches after GPU page-table changes.
- VM aperture and memory-controller controls for AGP, framebuffer, system aperture, default page addresses, HBM-local ranges, XGMI local frame buffer regions, cacheable DRAM ranges, host mapping, low-power state, and local/shared virtual reset.
- TLB and translation-assist fields for checking L2 TLB busy/parity state and for representing address, VMID, VFID, permissions, memory type, NACK/ACK, and related metadata in GPUVA translation-assist request/response registers.
- TCP/TCI/TCC cache controls and status fields, including L1/L2 load/store/atomic policy encodings, channel steering, buffer address hashing, volatile policy, cache invalidation, busy status, clock-gating bits, error injection, and EDC error-reporting fields.

These constants are infrastructure for device initialization, VM updates, fault handling, cache-policy setup, suspend/resume restore, debugfs/register dumps, and RAS error collection on GC 9.4.3 devices.

## Important APIs, Types, And Data

There are no functions, structs, enums, or exported variables in this chunk. The API surface is a set of preprocessor macros following the AMD ASIC register convention:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the pre-shifted bit mask for the field.

Important register families in the chunk include:

- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL`: each context has the same 21 fields and 21 masks. Key fields are `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry controls, and fault interrupt/default controls for range, dummy page, PDE0, valid, read, write, execute, and secure faults.
- `VM_CONTEXTS_DISABLE`: one disable bit per context 0 through 15. This gives software a compact way to disable selected VM contexts.
- `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`: single `SEMAPHORE` bit per invalidation engine.
- `VM_INVALIDATE_ENG0_REQ` through `VM_INVALIDATE_ENG17_REQ`: per-engine request fields. Each request has a 16-bit `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, flags for invalidating L2 PTEs, PDE0, PDE1, PDE2, and L1 PTEs, plus `CLEAR_PROTECTION_FAULT_STATUS_ADDR` and `LOG_REQUEST`.
- `VM_INVALIDATE_ENG0_ACK` through `VM_INVALIDATE_ENG17_ACK`: per-engine `PER_VMID_INVALIDATE_ACK` status bits.
- `VM_INVALIDATE_ENG<n>_ADDR_RANGE_LO32` and `_HI32`: optional invalidation range bounds. Low registers include `ADDR` and `SYSTEM_ACCESS_MODE`; high registers expose the upper `ADDR`.
- `VM_CONTEXT<n>_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `START_ADDR_LO32/HI32`, and `END_ADDR_LO32/HI32`: 32-bit halves for page-table base and valid virtual-address range programming.
- `MC_VM_*` registers: aperture and mapping fields including `MC_VM_NB_MMIOBASE`, `MC_VM_NB_MMIOLIMIT`, PCI control/arbitration, DRAM top registers, `MC_VM_FB_OFFSET`, system aperture default addresses, steering, shared reset, memory power, cacheable DRAM ranges, `MC_VM_APT_CNTL`, local HBM ranges and locks, XGMI LFB controls, cacheable DRAM control, host mapping, framebuffer and AGP locations, system aperture low/high, and `MC_VM_MX_L1_TLB_CNTL`.
- `UTCL2_CGTT_CLK_CTRL`: UTCL2 clock-gating and frequency-gating delay/override fields such as `SOFT_OVERRIDE`, `DS_OVERRIDE`, `REG_OVERRIDE`, `TCP_OVERRIDE`, `FGCG_DLY`, and `FGCG_DIS`.
- `L2TLB_TLB0_STATUS`: `BUSY` and `FOUND_PARITY_ERRORS`.
- `UTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*` and `RESPONSE_*`: address, VMID, VFID, VF/GPA mode, permissions, client ID, request, fragment size, snoop, SPA/IO/TMZ, no-PTE, memory type, memlog, LLC no-alloc, NACK, and ACK fields.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CHAN_STEER_0/1`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, and `TCP_BUFFER_ADDR_HASH_CNTL`: texture-cache pipeline invalidation, busy/status, cache sizing/force-hit/miss, channel steering, address geometry, credits, and hashing.
- `TC_CFG_L1_LOAD_POLICY0/1`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY0/1`, `TC_CFG_L2_STORE_POLICY0/1`, and `TC_CFG_L2_ATOMIC_POLICY`: four 2-bit policy fields per 32-bit register for L1/L2 load, store, and atomic cache policies.
- `TC_CFG_L1_VOLATILE` and `TC_CFG_L2_VOLATILE`: volatile policy nibbles.
- `TCP_*_EDC_*` and `TCI_*_EDC_*`: corrected and uncorrected EDC reporting fields. High registers indicate ECC/parity class, error-info validity, error information, UE/CE counters, fatal-event-detected or poison bits, and reserved bits. Low registers indicate status/address validity, error address, and memory ID.
- `TCI_MISC`, `TCI_CNTL_1/2/3`, `TCI_DSM_CNTL`, `TCI_DSM_CNTL2`, and `TCI_STATUS`: TCI clock gating, bandwidth/combining behavior, debug/error-injection controls, busy status, FIFO/RAM depths, L1 invalidation-on-WBINVL2, and TCA credit fields.
- `TCC_CTRL` and partial `TCC_CTRL2`: TCC cache sizing, rate, FIFO size, set hashing, multiple clock-mode fields, shared 128-byte-read disable, probe FIFO size, NaN/Inf clamp, probe-filter control, wait-stable count, and several fine-grained clock-gating disable fields. `TCC_CTRL2` continues after the chunk boundary.

The consumer-side helper APIs are defined elsewhere in AMDGPU, but this chunk is designed for them. The most relevant patterns are `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_OFFSET`, with register addresses coming from the paired `gc_9_4_3_offset.h`.

## Control Flow

This header chunk has no runtime control flow. Its control-flow role is indirect: it parameterizes register programming sequences in AMDGPU and KFD code.

Typical VM initialization flow using these fields is visible in `amdgpu/gfxhub_v1_2.c`:

1. The driver includes `gc/gc_9_4_3_offset.h` for register addresses and this file for field metadata.
2. VMID page-table base registers are written through `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` plus a context address stride. The corresponding `_ADDR` masks in this chunk document that the full 32-bit low/high words carry address bits.
3. VMID0 aperture start/end registers are programmed with `VM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `END_ADDR_*` fields.
4. System aperture registers such as `MC_VM_AGP_BASE`, `MC_VM_AGP_BOT`, `MC_VM_AGP_TOP`, `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, and default-address registers are set from `adev->gmc` ranges and scratch/dummy pages.
5. `MC_VM_MX_L1_TLB_CNTL` is read, modified with `REG_SET_FIELD`, and written back to enable the L1 TLB, select system access behavior, enable the advanced driver model, set unmapped access behavior, select `MTYPE`, and enable ATC.
6. `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` are read/modified/written to enable contexts and choose page-table depth, block size, retry handling, and protection-fault response behavior.
7. Invalidation engine addresses and distances are recorded from `regVM_INVALIDATE_ENG0_*`, `regVM_INVALIDATE_ENG1_*`, and context register spacing so common VM hub code can invalidate VMIDs without hard-coding per-engine register numbers.

VM invalidation itself is a hardware handshake represented by the `VM_INVALIDATE_ENG<n>` register families:

1. Software claims or observes the engine semaphore.
2. Software writes an invalidation address range when range invalidation is used.
3. Software writes a request word selecting VMIDs and PTE/PDE/L1/L2 flush behavior.
4. Hardware reports completion in the ACK register.
5. Higher-level VM code can poll or wait until the ACK bits match the requested VMID mask.

The translation-assist request/response registers define another hardware protocol. Request fields encode a GPU virtual address, VMID/VFID context, access permissions, GPA/VF attributes, client ID, and a request bit. Response fields encode translated address bits, permissions, fragment size, cache/memory attributes, NACK/ACK state, and no-PTE or TMZ information. The header does not implement the protocol; it makes the request/response words decodable and constructible.

For cache and RAS controls, driver flow is similarly external. `gfx_v9_4_3.c` includes this header and registers TCP/TCI/TCC memory blocks in RAS tables using paired low/high EDC registers. EDC collection logic can read the registers and use these masks to decode status validity, address validity, memory ID, error information, and corrected/uncorrected counters. Cache-policy and invalidate code can use `TCP_INVALIDATE`, `TCP_STATUS`, `TC_CFG_*`, and TCI/TCC fields to configure or observe cache behavior.

## State And Persistence Behavior

The macros themselves are compile-time constants and carry no state. The state represented by this chunk lives in GPU MMIO registers and is persistent at hardware scope until reset, power-gating loss, suspend/resume reinitialization, driver reprogramming, or firmware/hardware side effects.

Important state categories are:

- Per-VMID state: `VM_CONTEXT<n>_CNTL`, page-table base, start, and end registers define which address spaces are active and which GPU virtual ranges are legal for each VMID.
- Fault behavior state: context control bits decide whether range, dummy-page, PDE0, valid, read, write, execute, and secure faults interrupt, use defaults, or retry. Incorrect persistence across reset/resume can change user-visible GPU fault behavior.
- Invalidation state: invalidation semaphores, request words, ACK words, and address ranges are transient hardware synchronization state. They should not be treated as durable configuration; stale request/ACK interpretation can cause missed TLB flushes or hangs.
- Aperture state: MC VM registers define framebuffer, AGP, HBM, system aperture, cacheable DRAM, host mapping, XGMI LFB, and default fault addresses. These are core memory-routing state and must match `adev->gmc` topology, virtualization mode, XGMI setup, and VRAM/GART placement.
- TLB/cache state: `MC_VM_MX_L1_TLB_CNTL`, L2 TLB status, TCP/TCI/TCC controls, policy registers, and invalidation controls shape caching, translation, and busy status. Some values are configuration, while status bits such as `BUSY`, `TCP_BUSY`, and `TCI_BUSY` are live hardware observations.
- RAS/EDC state: EDC low/high registers expose latched error status, address information, memory ID, error info, counters, and poison/fatal flags. Reads may be part of a wider RAS flow that logs, clears, or escalates errors.
- Debug/error-injection state: `TCI_DSM_CNTL` and `TCI_DSM_CNTL2` expose write-RAM irritator and error-injection controls. These should remain tightly controlled because they intentionally perturb hardware behavior.

Because this is a kernel driver header, no file-system persistence is involved. Persistence concerns are register programming order, reset-domain behavior, XCC instance replication, and whether suspend/resume or GPU reset paths restore the same values consistently across all active GC instances.

## Dependencies And Integration Points

This file depends conceptually on AMD's generated register database for GC 9.4.3. It must stay consistent with:

- `gc_9_4_3_offset.h`, which provides the `reg...` address symbols for the fields described here.
- SOC15 access helpers and field macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_OFFSET`.
- AMDGPU VM hub structures such as `struct amdgpu_vmhub`, which store context and invalidation-engine base addresses and distances derived from GC register offsets.
- `adev->gmc` memory topology state, including framebuffer, GART, AGP, VRAM, HBM, XGMI, dummy page, scratch page, and page-directory base values.
- KFD VM and queue management policy, especially retry/XNACK behavior and per-process memory policy.
- RAS infrastructure, which maps GC memory blocks to low/high EDC status register pairs.

Known direct includes of this header in the GC 9.4.3 path are:

- `amdgpu/gfxhub_v1_2.c`: programs VM context registers, page-table bases/ranges, system aperture registers, L1 TLB control, invalidation-engine addresses, and XGMI LFB discovery. This is the strongest direct consumer for the VM and MC fields in this chunk.
- `amdgpu/gfx_v9_4_3.c`: uses GC register metadata for graphics setup, TCP/TCI/TCC block naming, RAS register registration, and related GC debug/error-handling paths.
- `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`: KFD/AMDGPU bridge for GC 9.4.3; it uses the same generated register namespace for queue, watchpoint, and compute-facing configuration.
- `amdkfd/kfd_device_queue_manager_v9.c`: includes this header for GFX9-era KFD queue/process memory configuration fields, though many of the fields it uses are outside this exact line range.

The chunk is also integrated indirectly by common VM hub code. `gfxhub_v1_2.c` records addresses for `regVM_INVALIDATE_ENG0_SEM`, `REQ`, `ACK`, `regVM_CONTEXT0_CNTL`, context distance, invalidation request distance, and invalidation address-range distance. Common code can then operate over multiple VM hubs and XCC instances using those offsets while relying on these masks to preserve field layout.

## Risks And Edge Cases

The highest risk is a silent bitfield mismatch. These macros are trusted by register field helpers; if a mask or shift is wrong, the driver can write a valid-looking 32-bit value that programs the wrong hardware bit. For VM context control this can disable address spaces, select the wrong page-table depth, break invalid-page retry/XNACK behavior, or convert recoverable GPU page faults into hangs or unexpected interrupts.

The repeated register families create copy/paste and generation risks. `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` are expected to have identical field layouts. The same is true for invalidation engines 0 through 17 and for repeated page-table base/start/end register pairs. A single divergent mask in one instance could affect only one VMID or one invalidation engine, making the bug highly workload-specific.

Invalidation request and ACK fields are correctness-critical. Missing `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE*`, or `INVALIDATE_L1_PTES` bits can leave stale translations resident after page-table updates. Wrong `PER_VMID_INVALIDATE_REQ` or ACK decoding can make software believe a VMID flush completed when it did not, or spin forever waiting for the wrong bit.

Address field units differ by register family and call site. Some driver writes shift addresses by 12, 18, 24, or 44 before programming low/high registers. The masks in this chunk usually describe the register payload width, not the semantic address granularity. Reviewers must check the programming code and hardware spec rather than assuming all `_ADDR` fields use byte units.

Virtualization and partitioning add integration risk. GC 9.4.3 systems can have multiple XCC instances, SR-IOV VF mode, XGMI-connected memory, and GART-for-framebuffer translation. `gfxhub_v1_2.c` loops over instance masks and sometimes disables conventional FB/AGP aperture windows. A field mismatch may only appear on multi-XCC, XGMI, VF, or partitioned configurations.

RAS fields have diagnostic and availability impact. EDC high/low masks decide how software interprets corrected/uncorrected counts, poison/fatal flags, memory IDs, and error addresses. Incorrect decoding can under-report real hardware faults, over-report reserved bits as errors, or attribute an error to the wrong GC memory block.

The chunk boundaries are partial. `UTCL2_CE_ERR_STATUS_HI` is already in progress at line 9541 and `TCC_CTRL2` continues after line 11973. Chunk-local tooling should not assume each commented register block is complete. The merge lane should reconstruct this file with adjacent chunks before doing whole-register completeness checks.

Manual edits are fragile because this header is generated. Any change should be checked against the corresponding AMD register specification or regeneration source. Local fixes to only the mask header can be overwritten and can also desynchronize offset, enum, and mask headers for the same IP.

## Test Signals

Useful verification signals for this chunk include:

- Compile the AMDGPU driver with GC 9.4.3 enabled and warnings treated seriously. This catches missing macro names, duplicate definitions, and obvious field-helper integration breakage.
- Boot or initialize a GC 9.4.3 device and confirm `gfxhub_v1_2.c` VM setup succeeds across all active XCC instances. Relevant signals are successful GART setup, VMID0 context enablement, page-table base/range programming, and no early VM faults.
- Exercise GPU VM updates that require invalidation. Page-table updates followed by command submission should complete without stale mappings, VM fault storms, or invalidation timeout messages.
- Test KFD/HSA workloads with XNACK/retry enabled and disabled. The `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` and related context-fault fields should produce expected recoverable fault or no-retry behavior.
- Run suspend/resume and GPU reset paths. After resume or reset recovery, aperture, context, TLB, and invalidation-engine programming should be restored and command submission should resume without VM faults.
- Validate multi-XCC and XGMI configurations. The same VM and aperture programming should be applied to each intended `GET_INST(GC, i)` instance, and XGMI LFB size/region fields should decode to plausible ranges.
- Exercise SR-IOV VF and bare-metal paths if hardware is available. Aperture programming differs by virtualization mode, and `VF`, `VFID`, and translation-assist fields are particularly relevant to virtualized deployments.
- Check RAS paths by reading/injecting supported corrected and uncorrected errors for TCP and TCI blocks. Expected signals are correct low/high EDC status decoding, memory block attribution, CE/UE counter handling, and no reserved-bit false positives.
- Use register dumps or debugfs comparisons against known-good hardware traces. The decoded `MC_VM_MX_L1_TLB_CNTL`, `VM_CONTEXT<n>_CNTL`, `VM_INVALIDATE_ENG<n>_*`, TCP/TCI/TCC control, and EDC fields should match expected boot-time and workload-time values.
- For merge validation, verify that adjacent chunk documents cover the missing start of `UTCL2_CE_ERR_STATUS_HI` and the remainder of `TCC_CTRL2`, then run a whole-file scan for every `__SHIFT` having a matching `_MASK` where the register database expects both.

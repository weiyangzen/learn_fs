# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 42639-45068

## Scope And Purpose

This chunk is the final range of the generated MMHUB 9.4.1 shift/mask header. It contains no executable C code, types, or functions. Instead, it publishes preprocessor constants that describe bit positions and bit masks for late MMHUB virtual-memory, virtualization, aperture, ATS, XGMI, clock-gating, and performance-counter registers.

The covered range starts in the `mmhub_utcl2_vml2pfdec:1` address block with the tail of `VML2PF1_VM_L2_CNTL`, then completes the `VML2PF1` L2 control/status/fault register field macros. It then defines the `VML2VC1` VM-context block for contexts 0 through 15, invalidation engines 0 through 17, page-table base/start/end address registers, shared PF/VC/HV aperture and virtualization controls, and the final ATC/L2 and VM/L2 perf-counter controls. The file ends with the `_mmhub_9_4_1_SH_MASK_HEADER` include-guard close.

The purpose is to let AMDGPU code write and read named register fields through helper macros such as `REG_SET_FIELD`, paired with register offsets from `mmhub_9_4_1_offset.h` and reset defaults from `mmhub_9_4_1_default.h`. The direct in-tree consumer for this ASIC generation is `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes all three MMHUB 9.4.1 generated headers.

## Important APIs, Types, And Macro Families

The `VML2PF1_VM_L2_*` family describes physical-function L2 VM controls. Key fields include L2 cache enablement, fragment processing, PTE/PDE endian swap modes, LRU update behavior, default-page routing, PDE cache split/effective size, invalidation controls, bank selection, cache force-miss bits, parity status, dummy-page fault matching, identity aperture bounds, identity physical offset, and cache parity/clock-gating knobs.

The protection fault macros define both policy and observability. `VML2PF1_VM_L2_PROTECTION_FAULT_CNTL` and `CNTL2` provide clear/update controls, per-fault-class default-page enable bits, no-retry/retry crash bits, client interrupt masks, active page-migration PTE behavior, and retry fault interrupt enable. The status and address registers expose `MORE_FAULTS`, `WALKER_ERROR`, permission/mapping flags, `CID`, read/write and atomic attributes, `VMID`, VF/VFID identity, logical fault address, and default physical address fields.

The `VML2VC1_VM_CONTEXT0_CNTL` through `VML2VC1_VM_CONTEXT15_CNTL` families are repeated VMID context controls. Each context has fields for `ENABLE_CONTEXT`, page-table depth, page-table block size, retry-on-fault behavior, interrupt/default enable bits for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The later `VML2VC1_VM_CONTEXTS_DISABLE` register provides one disable bit for each context 0 through 15.

The invalidation macros define 18 invalidation engines. Each engine has a semaphore register, request fields for per-VMID invalidate bits, `FLUSH_TYPE`, `FLUSH_UTCL2`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and a 4-bit `INVALIDATE_L2_PTES` field. Each engine also has an ack bit and low/high logical page range fields. In `mmhub_v9_4.c`, these offset distances populate `amdgpu_vmhub` fields used by common VM invalidation code.

The page-table address families publish 32-bit low and 4-bit high fields for each VM context's page-table base, start, and end addresses. AMDGPU writes these from GART and VM-manager state by shifting GPU addresses/PFNs into the register's page-number format.

The `VMSHAREDPF1_*`, `VMSHAREDVC1_*`, and `VMSHAREDHV1_*` blocks describe shared MMHUB controls. They include NB MMIO/PCI and top-of-DRAM controls, framebuffer offset, system aperture default address, steering, reset, memory power light-sleep, cacheable DRAM, local HBM, XGMI LFB controls, framebuffer/AGP/system aperture bounds, L1 TLB controls, per-VF framebuffer size/offset, MARC base/relocation/length windows, IOMMU/ATS controls, per-VF ATS enable bits, hypervisor-side UTCL2 clock-gating, active function ID, and XGMI GPUIOV enable bits for VF0-VF15 plus PF.

The final `ATCL2PFCNTR1`, `ATCL2PFCNTL1`, `VML2PL1`, and `VML2PR1` blocks define performance-counter data and control fields. They expose low/high counter values, compare value fields, event selection ranges, perf modes, enable/clear bits, global result-counter selection, start/stop triggers, enable-any, clear-all, and stop-on-saturate behavior.

## Control Flow And Runtime Use

There is no runtime control flow inside this header. Its behavior is entirely preprocessing: a consumer names a register block and field, and build-time macro expansion supplies the shift and mask constants for bit manipulation.

The usual runtime path is visible in `mmhub_v9_4.c`. GART enablement programs MMHUB instances by writing page-table base/start/end registers, system aperture registers, L1 TLB control, L2 cache control, VMID context control, and invalidation address ranges. Calls like `REG_SET_FIELD(tmp, VML2PF0_VM_L2_CNTL, ENABLE_L2_CACHE, 1)` rely on the same generated naming scheme as this chunk's `VML2PF1_*` macros. Instance and function-number variants are selected through matching offset names and per-hub register offsets.

Fault handling uses these field layouts when `mmhub_v9_4_set_fault_enable_default()` toggles protection-fault default-page routing and crash behavior. The `amdgpu_vmhub` initialization stores register offsets for context0 control, invalidation semaphore/request/ack, and L2 fault status/control so common GPUVM code can later drive invalidations and inspect fault state without hard-coding MMHUB register addresses.

Performance-counter and virtualization fields in this chunk are mostly register-interface surface. They may be used by diagnostics, firmware-oriented flows, SR-IOV/hypervisor setup, or future performance tooling even when not directly touched by the narrow `mmhub_v9_4.c` initialization path.

## State And Persistence Behavior

This header itself has no storage, allocation, persistence, I/O, or side effects. The constants become part of compiled driver code wherever included.

The hardware registers described here are persistent device state until reset or reprogramming. Important state includes VM context enable/depth/block-size configuration, page-table base/start/end ranges, L2 cache and TLB enablement, protection-fault policy, fault status/address latches, invalidation sem/request/ack state, aperture bounds, per-VF virtualization windows, ATS enablement, clock-gating controls, and perf-counter selection/counter values.

Some fields are clearly write-to-control or latch-clearing state, such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, invalidation request bits, perf-counter `CLEAR`, and `CLEAR_ALL`. Others represent status sampled from hardware, such as L2 busy/parity bits, invalidation ack bits, fault status, active function ID, and counter values. The masks in this header do not encode access type, so callers must know from the register specification and driver sequence which fields are safe to write, read, or preserve.

## Dependencies And Integration Points

The header depends on its sibling generated register headers for complete use. `mmhub_9_4_1_offset.h` supplies the register addresses and base indices, while `mmhub_9_4_1_default.h` supplies reset/default values. This shift/mask file supplies the field-level layout used to preserve unrelated bits during read-modify-write operations.

The primary C integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`. That file uses SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`, plus `REG_SET_FIELD`, to initialize MMHUB instances, VM contexts, apertures, L2 cache, invalidation ranges, and fault policies.

The macros integrate indirectly with broader AMDGPU subsystems: GMC/GART setup provides page-table and aperture values; GPUVM uses the `amdgpu_vmhub` register offsets for invalidations and VMID management; SR-IOV paths branch around PF-only programming; RAS and debug flows may inspect MMHUB status/counter/error registers; power-management and clock-gating code uses related UTCL2/MMHUB fields.

The generated naming convention is also an integration contract. `REG_SET_FIELD` expects symbols shaped as `<register>__<field>_MASK` and `<register>__<field>__SHIFT`; if either name or bit range drifts from the offset/default headers or from the ASIC register spec, register programming compiles but can program the wrong hardware bits.

## Risks And Edge Cases

Manual edits are high risk because the file is generated register metadata. A single wrong mask or shift can corrupt MMHUB address translation, invalidate the wrong VMIDs, route faults incorrectly, break SR-IOV isolation, or make perf/RAS/debug information misleading.

This chunk uses the `*1` register namespace, while the visible `mmhub_v9_4.c` initialization often programs `*0` registers plus a per-instance offset. That makes naming consistency important: users must select the register namespace that matches the offset being used rather than assuming all similarly named fields are interchangeable across PF/VC/HV blocks.

Repeated context and invalidation-engine macros are easy to misuse. Contexts 0-15 and engines 0-17 have similar field layouts but different address strides. Driver code must use the correct `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance`; otherwise a VMID or invalidate engine update can hit the wrong register.

Address split fields are narrow in their high half, commonly 4 bits after page-number shifts. Incorrect shifting, using byte addresses where page numbers are expected, or truncating high bits can silently constrain the GART/VM aperture or page-table address range.

Fault-control fields mix default-page routing, interrupt policy, retry behavior, active page migration, and crash-on-fault behavior in adjacent bits. Preserving unrelated bits during read-modify-write is essential, especially when toggling `CRASH_ON_NO_RETRY_FAULT`, `CRASH_ON_RETRY_FAULT`, or retry fault interrupts.

SR-IOV and hypervisor fields, including per-VF framebuffer sizing, per-VF ATS control, active function ID, and XGMI GPUIOV enablement, are security-sensitive. Wrong masks can expose memory apertures to the wrong function or leave translation/cache behavior inconsistent between PF and VFs.

Perf-counter fields include selection ranges and trigger controls. Incorrect mode, trigger, or clear handling can return plausible but wrong telemetry and can interfere with concurrent diagnostic users if counters are shared.

## Test Signals

Build coverage should compile the AMDGPU driver paths that include `mmhub_9_4_1_sh_mask.h`, especially `mmhub_v9_4.c`, with warnings treated seriously. Macro-name drift usually appears as compile failures in `REG_SET_FIELD` or SOC15 register references.

Static validation should compare this generated header against the corresponding ASIC register source used to produce `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`. A useful check is that every field macro pair has both a `_MASK` and `__SHIFT`, and that masks align with their shifts and expected widths.

Runtime smoke tests should cover MMHUB GART enable/disable on supported hardware: page-table base programming, system aperture setup, L1 TLB/L2 cache enablement, VMID context setup, and invalidation request/ack completion across both MMHUB instances.

VM fault tests should deliberately trigger invalid, permission, read/write, and execute faults and verify status decoding, default-page routing, crash/no-crash policy, and interrupt behavior. Tests should include both normal PF paths and SR-IOV VF/PF configurations where PF-only registers are skipped or hypervisor fields apply.

Addressing tests should exercise high framebuffer/GART/VM addresses to catch low/high split mistakes in page-table base/start/end, aperture default address, identity aperture, and protection fault default address fields.

Invalidation tests should verify all 18 invalidation engines can program full-range and targeted-range invalidations, set the intended VMID bits, and observe the matching ack without disturbing neighboring engine registers.

Performance and diagnostic tests should program the ATC L2 and VM L2 perf counters, clear them, select events, run a known MMHUB workload, and verify counters increment and saturate/stop according to the control bits.

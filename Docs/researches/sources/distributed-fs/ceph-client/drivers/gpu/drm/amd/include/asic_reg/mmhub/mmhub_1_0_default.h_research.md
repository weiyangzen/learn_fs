# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_default.h

## Purpose

`mmhub_1_0_default.h` is a generated AMDGPU default-value header for MMHUB 1.0 registers. It maps many `mm..._DEFAULT` macros to reset or recommended initialization values for MMHUB DAGB, MMEA, PCTL, L1 TLB, ATC L2, VM L2, VM context, invalidate engine, shared VM, and performance counter blocks. It contains no executable logic, but its constants seed hardware initialization paths that start from generated defaults and then override selected fields.

## Important APIs, Types, And Macros

The file exports default-value macros only. There are no functions, structs, or enums.

Address block groups:

- `mmhub_dagbdec`: duplicated DAGB0/DAGB1 read and write client defaults, read/write control, GMI control, address/data DAGB burst and lazy timers, virtual channel controls, TLB/data/misc credits, pending-state defaults, FIFO empty/full defaults, credit-full defaults, performance counter defaults, and reserve registers.
- `mmhub_ea_mmeadec`: MMEA0/MMEA1 DRAM and IO client-to-group maps, group-to-VC maps, lazy timers, CAM controls, page burst, priority age/queue/fixed/urgency/quantum values, address normalization, DRAM address decode base/mask/config/select/column mappings, hash registers, harvest enable, SDP arbitration/credits/reserves, latency/performance/EDC/DSM/clock/error defaults.
- `mmhub_pctldec`: PCTL and PCTL0-2 defaults for deep sleep, power-gating ignore, DAGB power gating, RENG RAM index/data/execute, miscellaneous values, and state-control save ranges/exclusion sets.
- `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, and `mmhub_l1tlb_vml1prdec`: L1 TLB status and L1 performance counter default values.
- `mmhub_utcl2_atcl2dec`: ATC L2 control, cache data, status, clock-gating, and memory power defaults.
- `mmhub_utcl2_vml2pfdec`: VM L2 control/status, dummy page fault, protection fault, identity aperture, bank select, parity, and clock defaults.
- `mmhub_utcl2_vml2vcdec`: VM context control for contexts 0-15, context disable, invalidate semaphores, invalidate requests and acknowledgements for engines 0-17, invalidate address ranges, and page table base/start/end address defaults for contexts 0-15.
- `mmhub_utcl2_vml2pldec` and `mmhub_utcl2_vml2prdec`: VM L2 performance counter config/result defaults.
- `mmhub_utcl2_vmsharedhvdec`: SR-IOV/hypervisor-facing FB size offsets for VFs 0-15, IOMMU control, MARC base/relocation/length windows, PCIe ATS controls including per-VF controls, and UTCL2 clock-gating default.
- `mmhub_utcl2_vmsharedpfdec`: PF shared NB MMIO, PCI, top-of-DRAM, FB offset, system aperture default address, steering, shared reset, memory power, cacheable DRAM range, APT control, and local HBM range defaults.
- `mmhub_utcl2_vmsharedvcdec`: FB/AGP/system aperture defaults and `mmMC_VM_MX_L1_TLB_CNTL_DEFAULT`.
- `mmhub_utcl2_atcl2pfcntrdec` and `mmhub_utcl2_atcl2pfcntldec`: ATC L2 performance counter data and config defaults.

Notable direct-use defaults in the local driver include `mmVM_L2_CNTL3_DEFAULT` and `mmVM_L2_CNTL4_DEFAULT`, which `mmhub_v1_0.c` reads into a temporary value before applying field overrides.

## Control Flow

There is no local control flow. Runtime consumers include `amdgpu/mmhub_v1_0.c`, which initializes MMHUB by reading and writing registers through SOC15 helpers. Most initialization paths read the current register value and set fields with masks from `mmhub_1_0_sh_mask.h`; for some registers the driver starts from defaults in this file, modifies selected fields, then writes the result. For example, `mmhub_v1_0_init_cache_regs()` uses `mmVM_L2_CNTL3_DEFAULT` and `mmVM_L2_CNTL4_DEFAULT` as baseline values before programming bank select, fragment size, and TAP request behavior.

## State And Persistence Behavior

The header itself is stateless. The macros describe default register contents for hardware state. At runtime those defaults influence persistent-in-register settings for GPU VM translation, TLB/cache behavior, protection fault handling, invalidate engines, apertures, address decode, arbitration, credits, clock/power controls, and performance counters. The values remain in hardware registers until reset or reprogrammed by the driver, firmware, power management, virtualization flows, or fault handling.

Many defaults are zero, indicating disabled, empty, unmapped, no pending work, or no programmed aperture at reset. Non-zero defaults encode policy: DAGB client and VC weights, credit depths, FIFO empty masks, PCTL save ranges, VM L2 enable/control baselines, invalidate request templates, local HBM address end, and clock/memory power settings.

## Dependencies

Consumers depend on:

- Matching offset definitions in `mmhub_1_0_offset.h`.
- Matching field definitions in `mmhub_1_0_sh_mask.h`.
- SOC15 MMIO helpers and AMDGPU register field helpers.
- ASIC-specific driver logic in `mmhub_v1_0.c` that knows when to use defaults directly and when to read/modify/write live register values.

The include guard is `_mmhub_1_0_DEFAULT_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c` includes this header.

Functional integration areas:

- GART and VM page-table setup use MMHUB context and page table registers whose reset defaults are listed here.
- System/AGP/framebuffer aperture setup overwrites shared VM aperture defaults.
- TLB/cache initialization uses L1 and L2 control defaults and masks.
- Protection fault setup uses default address and fault control registers.
- VM invalidation uses semaphore/request/ack/range registers for engines 0-17.
- SR-IOV paths skip selected PF-only programming, so default values can remain visible longer in virtual-function contexts.
- Power/clock management interacts with PCTL, ATC L2, UTCL2, MC memory power, and CGTT defaults.

## Risks

- Defaults are ASIC-version-specific. Reusing MMHUB 1.0 defaults for a different MMHUB generation can misprogram memory translation, arbitration, or power behavior.
- The file is broad and repetitive; copy/paste or generation errors can be hard to notice, especially across MMEA0/MMEA1, DAGB0/DAGB1, contexts 0-15, and invalidate engines 0-17.
- Some defaults are safe only as reset baselines. Driver code must still program runtime-specific apertures, page-table bases, fault addresses, and VM context ranges before enabling translation.
- Virtualization paths can intentionally avoid programming some PF-only registers. Tests must distinguish expected default retention from missed initialization.
- Default values for protection fault handling, ATS, IOMMU, local HBM range, and cache/TLB controls are high impact; stale or mismatched constants can produce VM faults, hangs, or security/isolation issues.

## Test Signals

- Build coverage for `amdgpu/mmhub_v1_0.c` verifies that directly referenced default macros exist.
- MMHUB initialization tests should verify programmed VM L2/L1 TLB values after driver init, especially values seeded from `mmVM_L2_CNTL3_DEFAULT`, `mmVM_L2_CNTL4_DEFAULT`, and `mmMC_VM_MX_L1_TLB_CNTL_DEFAULT`.
- GART/VM tests should allocate GPU virtual memory, exercise page-table base/start/end programming, and confirm no unexpected MMHUB protection faults.
- Fault-path tests should validate dummy page/protection fault default address programming and fault status behavior.
- SR-IOV test lanes should compare PF and VF initialization, checking that skipped PF-only programming leaves only expected defaults.
- Hardware bring-up should diff this header against the register database used to generate `mmhub_1_0_offset.h` and `mmhub_1_0_sh_mask.h`, focusing on non-zero defaults and repeated per-context/per-engine arrays.

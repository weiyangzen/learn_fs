# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 25972-28443

## Scope

This chunk is part of AMDGPU's generated ASIC register bitfield header for the MMHUB 9.4.1 block. It contains C preprocessor constants only: each register field has a `__SHIFT` macro and a matching `_MASK` macro using the hardware register name as the prefix. There are no functions, structs, enums, allocations, or executable control flow in this chunk. Runtime behavior comes from driver code that includes this header and uses these masks with register addresses from the companion `*_offset.h`/`*_d.h` headers and AMDGPU register access helpers.

## Purpose

The chunk documents bit layouts for several MMHUB sub-blocks:

- `VML2VC0` virtual-channel 0 invalidation and context page table registers.
- `VMSHAREDPF0`, `VMSHAREDVC0`, and `VMSHAREDHV0` shared PF/VC/HV memory aperture, virtualization, ATS, IOMMU, and XGMI controls.
- `ATCL2PFCNTR0`/`ATCL2PFCNTL0` and `VML2PL0`/`VML2PR0` performance counter programming and result fields.
- `DAGB5` read/write data-arbitration gateway controls for clients, virtual channels, bandwidth windows, outstanding request limits, TLB credits, pending-status bits, and clock-gating overrides.

The constants let C code compose and decode 32-bit MMIO register values without embedding raw bit positions or masks in driver logic.

## Important Macro Families

`VML2VC0_VM_INVALIDATE_ENG7_REQ` through `ENG17_REQ` define per-engine invalidate requests. Each request register exposes `PER_VMID_INVALIDATE_REQ` in bits 0-15, `FLUSH_TYPE` in bits 16-17, and individual invalidation selectors for L2 PTEs, PDE0/PDE1/PDE2, L1 PTEs, and protection-fault status address clearing. The chunk begins with the final mask from `ENG6_REQ`, so line 25972 is a boundary from the prior chunk.

`VML2VC0_VM_INVALIDATE_ENG0_ACK` through `ENG17_ACK` define acknowledgement status fields: `PER_VMID_INVALIDATE_ACK` and `INVALIDATE_ALL_ACK`. Code using the request fields should poll or inspect these acknowledgements to know whether the corresponding invalidate engine has completed.

`VML2VC0_VM_INVALIDATE_ENG*_ADDR_RANGE_LO32/HI32` provide optional logical-page address range fields for engines 0-17. The low register has a full 32-bit `LOGICAL_ADDR_LO32` mask and an `ENABLE` bit at bit 31; the high register carries a 30-bit `LOGICAL_ADDR_HI32` field. These fields pair with invalidate requests when callers need ranged invalidation rather than whole-context invalidation.

`VML2VC0_VM_CONTEXT0..15_PAGE_TABLE_BASE/START/END_ADDR_LO32/HI32` describe VM context page table base and logical range registers. Low halves are full 32-bit page-number fields, while high halves are 4-bit `*_HI4` fields. These define the base page table pointer and valid logical address window for each VM context.

`VMSHAREDPF0_*` covers PF-shared host bridge and memory mapping controls: NB MMIO base/limit, PCI MMIO enable, VGA hole, top-of-DRAM slots, framebuffer offset, default system aperture address, steering, PF/VF reset request, memory light-sleep timing, cacheable DRAM aperture, local HBM aperture with lock control, and XGMI local framebuffer region/size fields. It also includes shorter unprefixed `MC_VM_XGMI_LFB_CNTL/SIZE` aliases with slightly narrower masks than the `VMSHAREDPF0` versions.

`VMSHAREDVC0_*` defines shared VC framebuffer, AGP, and system aperture bounds plus `MC_VM_MX_L1_TLB_CNTL`. The L1 TLB control fields enable the L1 TLB, select system access mode, configure unmapped aperture behavior, enable advanced driver model behavior, set ECO/MTYPE bits, and enable ATC.

`VMSHAREDHV0_*` is the hypervisor-facing virtualization block. It includes per-VF framebuffer size/offset registers for VF0-VF15, IOMMU MMIO/control/performance enables, four MARC base/relocation/length register groups, PF and VF PCIe ATS enable controls, UTCL2 clock-gating overrides, active function ID reporting, and per-PF/VF XGMI GPU IOV enable bits.

`ATCL2PFCNTR0` and `ATCL2PFCNTL0` define ATC L2 performance counter result and configuration fields. Config registers have `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`; result control has counter select, start/stop trigger fields, enable-any, clear-all, and stop-on-saturate.

`VML2PL0` and `VML2PR0` define VM L2 performance counter control/result fields. `VML2PL0_MC_VM_L2_PERFCOUNTER0_CFG` through `7_CFG` mirror the ATC counter config shape, while `VML2PR0_MC_VM_L2_PERFCOUNTER_LO/HI` expose 48-bit counter result pieces plus a high-register compare value.

`DAGB5_RDCLI0..15` and `DAGB5_WRCLI0..15` repeat the same client arbitration layout for 16 read clients and 16 write clients: virtual channel selection, TLB-credit checking, high/low urgency thresholds, max/min bandwidth enable and value fields, OSD limiter enable, and maximum outstanding request count. The repeated layout is likely consumed by indexed setup code or table-driven initialization even though this header does not provide arrays.

`DAGB5_RD_CNTL/WR_CNTL`, `*_GMI_CNTL`, `*_ADDR_DAGB`, `*_OUTPUT_DAGB_MAX_BURST`, and `*_OUTPUT_DAGB_LAZY_TIMER` configure global read/write arbitration policy: SCLK frequency bucket, client/VC bandwidth windows, IO level override and compliance VC, shared VC count, EA credit, GMI burst and lazy timer, DAGB enable/jump-ahead/self-init/identity, and per-VC output burst/timer nibbles.

`DAGB5_RD_VC0..7_CNTL`, present for read-side VCs in this chunk, configures per-VC storage credit, EA credit, max/min bandwidth, OSD limiting, and max outstanding requests. The write-side VC-specific section is not fully present before line 28443, so cross-chunk reconciliation should check subsequent chunks for matching `DAGB5_WR_VC*` definitions.

`DAGB5_*_CGTT_CLK_CTRL`, `DAGB5_L1TLB_*_CGTT_CLK_CTRL`, and `DAGB5_ATCVM_*_CGTT_CLK_CTRL` provide clock-gating and light-sleep override fields for read/write DAGB, L1 TLB, and ATC VM sub-blocks. They define on delay, off hysteresis, soft-stall override, and LS override bits for write/read/return/register paths.

## Control Flow and State

This chunk has no executable flow. Its implicit flow is the hardware protocol encoded by the fields:

1. Driver code programs VM context page table base/start/end values.
2. It enables shared apertures, L1 TLB/ATC/IOMMU/ATS, PF/VF mappings, XGMI IOV, and arbitration policy as appropriate for the ASIC and virtualization mode.
3. On mapping changes, it writes a `VML2VC0_VM_INVALIDATE_ENG*_REQ` value, optionally with address range registers, then observes the matching `*_ACK` bits.
4. Diagnostic or profiling code programs `ATC_L2` or `VM_L2` perf counter config registers, starts/stops counting through result-control fields, and reads low/high result registers.

The state represented here persists in GPU hardware registers until reset, power management transitions, or later driver writes change it. Some fields are explicit transient controls (`CLEAR`, `CLEAR_ALL`, reset request bits, invalidate request bits), while others are durable configuration (`PAGE_TABLE_BASE`, aperture bounds, ATS enable, DAGB bandwidth controls). Because this is a generated mask header, persistence and ordering requirements must be enforced by the callers, not by this file.

## Dependencies and Integration Points

The macros depend only on the C preprocessor and fixed-width register semantics. They are typically paired with:

- register address headers for MMHUB 9.4.1, such as companion `mmhub_9_4_1_offset.h` or similar generated files;
- AMDGPU helpers/macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32`, `RREG32`, and indirect register accessors;
- MMHUB/GMC VM setup paths that program page tables, invalidation engines, apertures, ATS/IOMMU controls, and SR-IOV/XGMI virtualization;
- debugfs, perf, or tracing paths that read/write performance counter fields;
- power-management code that sets CGTT and light-sleep override controls.

The source path under `drivers/gpu/drm/amd/include/asic_reg/mmhub` indicates this is a Linux AMD GPU driver hardware-description dependency, not Ceph client logic despite the repository's broader `distributed-fs/ceph-client` tree.

## Risks

Bitfield correctness is critical. A wrong mask or shift in this file would silently write the wrong hardware bits, causing VM faults, stale TLB translations, broken ATS/IOMMU behavior, bad VF isolation, XGMI aperture exposure, arbitration starvation, or power-management hangs.

The chunk contains highly repetitive families. Copy-generation mistakes are especially plausible around numeric suffixes (`ENG*`, `CONTEXT*`, `VF*`, `RDCLI*`, `WRCLI*`) and boundary chunks. This chunk starts inside `ENG6_REQ` and ends inside the `DAGB5_WR_ADDR_DAGB_LAZY_TIMER0` block, so merge validation must preserve adjacent definitions from neighboring chunks.

Several register names encode privilege or isolation boundaries: `VMSHAREDHV0`, per-VF framebuffer offset/size, `ACTIVE_FCN_ID`, `PCIE_ATS_CNTL_VF_*`, and `MC_VM_XGMI_GPUIOV_ENABLE`. Incorrect usage by caller code can affect SR-IOV partitioning and address-translation isolation.

The `DAGB5` arbitration fields control credit, bandwidth, urgency, and outstanding request limits. Bad values may not fail immediately; they can surface as throughput regressions, latency spikes, starvation, or hangs under memory pressure.

The perf counter `CLEAR`, `CLEAR_ALL`, `ENABLE`, and stop-on-saturate bits are stateful hardware controls. Callers must avoid accidentally clearing counters while sampling and must account for split low/high reads.

## Test and Validation Signals

Useful validation signals are mostly integration-level because this header has no functions to unit test:

- Build coverage for AMDGPU code that includes MMHUB 9.4.1 register headers; missing or renamed macros should fail at compile time.
- Register readback tests or debug traces confirming that VM context base/start/end, aperture, ATS, XGMI IOV, and DAGB values land in expected bit positions after initialization.
- GPU VM stress tests that map/unmap buffers and verify `VML2VC0` invalidate request/ack behavior under multiple VMIDs and ranged invalidations.
- SR-IOV validation for VF framebuffer size/offset isolation, per-VF ATS enable, active function selection, PF/VF reset request handling, and XGMI GPU IOV enablement.
- IOMMU/ATS tests with PCIe ATS enabled/disabled and ATC/L1 TLB controls toggled according to platform support.
- Perf counter smoke tests that program ATC L2 and VM L2 event selectors, clear/start/stop counters, and verify monotonically plausible low/high result reads.
- Bandwidth and latency tests that exercise read/write DAGB client and VC settings, including OSD limiter, TLB-credit checking, urgency thresholds, max/min bandwidth windows, and clock-gating override behavior.

## Cross-Chunk Notes

This report covers only lines 25972-28443. Earlier chunks contain the beginning of the `VML2VC0_VM_INVALIDATE_ENG*` request family and likely broader VM L2 fault/control definitions. Later chunks should be checked for the remainder of `DAGB5_WR_ADDR_DAGB_LAZY_TIMER0`, write-side client 8-15 burst/timer registers, write VC controls, and subsequent DAGB or MMHUB blocks before producing the final per-file research document.

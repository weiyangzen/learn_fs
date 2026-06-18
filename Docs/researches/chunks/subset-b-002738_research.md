# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 1-5155

## Purpose

This chunk is the opening portion of the generated GMC 8.1 register field mask header for the AMDGPU DRM driver. It contains only preprocessor constants: each hardware register field is represented as a `<REGISTER>__<FIELD>_MASK` value and a matching `<REGISTER>__<FIELD>__SHIFT` value. The companion address/header files provide register offsets; this file supplies the bit layout used by register read-modify-write helpers, initialization tables, debug dumps, and ASIC-specific memory-controller programming paths.

The range covers the license/header guard and the first 5,129 lines of field definitions. The definitions are source-of-truth-like hardware contract data for the GMC 8.1 memory controller, not executable logic.

## Major Register Families Covered

- `MC_CONFIG`, `MC_CONFIG_MCD`, `MC_CG_CONFIG`, and `MC_CG_CONFIG_MCD`: select/index memory-controller dies or channels, enable MCD write paths, configure MC read access, and support indexed access modes.
- `MC_ARB_*`: memory-controller arbitration controls. This includes atomic/snoop grouping, aging, return credits, GECC/ECC status and injection fields, bank/rank/row/column mapping, DRAM timing, write timing/watermarks, refresh, power management, replay behavior, latency monitoring, real-time/urgent GRUB arbitration, client grouping, and busy/idle status fields.
- `MC_CITF_*`: client interface controls and credits. These fields map graphics/display/system clients to local or hub arbitration paths, configure read/write credits, return ordering, DAGB behavior, WTM decrementing, per-client throttling, clock gating, and performance-monitor status.
- `MC_RD_*`, `MC_WR_*`, `MC_RD_GRP_*`, and `MC_WR_GRP_*`: per-client read/write knobs and group assignments for CB, DB, TC, HUB, GFX, SYS, OTH, and EXT clients. The repeated field pattern is `ENABLE`, `PRESCALE`, `BLACKOUT_EXEMPT`, `STALL_MODE`, `STALL_OVERRIDE`, `MAX_BURST` or `MAXBURST`, `LAZY_TIMER`, and WTM override bits.
- `MC_HUB_MISC_*`, `MC_HUB_RDREQ_*`, `MC_HUB_WDP_*`, and `MC_HUB_WRRET_*`: hub-side read request, write datapath, write return, status, idle, blackout, deadlock-warning, credit, and client-specific flow-control fields. This chunk includes many repeated client blocks for MCDW/MCDX/MCDY/MCDZ/MCDS/MCDT/MCDU/MCDV plus SIP, SDMA, RLC, HDP, SMU, VCE, UVD, MCIF, VMC, IH, SH, SEM, VP8, ISP, XDMA/XDMAM, ACPG/ACPO, and related clients.
- `MC_RPB_*`: request packet buffer configuration, BIF ordering/credits, read/write switching, write combining, client-ID queue assignment, performance counters, and TCI policy/VMID/credit controls.
- `MC_SHARED_*`: shared channel map/remap fields, virtualization enable/reset/active-function identifiers, and blackout controls.
- `MC_VM_*`: frame-buffer and AGP apertures, system aperture default address fields, display-controller write hit regions, L1 TLB control/debug/status, and virtualization-related VM fields. These fields integrate with GPUVM setup and TLB invalidation/debug flows.
- `MC_XPB_*`: crossbar/peer/P2P bridge fields. The range includes P2P BAR configuration, peer system BARs, XDMA peer BARs, clock gating, interface credits/status, pipe status, sub-block reset/stall controls, sticky bits, misc config, and CLG configuration entries through the start of `MC_XPB_CLG_CFG29`.

## Important APIs, Types, and Functions

This header declares no C functions, structs, enums, or variables. Its API surface is the macro namespace itself:

- `*_MASK` constants isolate a field inside a 32-bit register value.
- `*__SHIFT` constants state how far to shift a caller-supplied value before combining it with the mask, or how far to shift a masked register value after reading it.
- The expected calling pattern in AMDGPU code is a register helper such as `WREG32`, `RREG32`, `WREG32_FIELD`, or local equivalents that combine register offsets from adjacent GMC 8.1 headers with these mask/shift definitions.

Because the definitions are macros, consumers get no type checking. Correctness depends on using the exact register-family macro for the matching ASIC generation and register offset.

## Control Flow

There is no runtime control flow in this file. At compile time, including the header exposes constants under the `GMC_8_1_SH_MASK_H` include guard. Runtime behavior emerges only in downstream code that reads, modifies, and writes hardware registers using these constants.

The logical flow enabled by this chunk is:

1. Select a register address from the GMC 8.1 register offset definitions.
2. Read the current 32-bit register value if only one field is being changed.
3. Clear the relevant `*_MASK` bits.
4. Shift a field value by the matching `*__SHIFT`.
5. Mask and OR the field back into the register value.
6. Write the final value to the hardware register.

Status fields invert that pattern: read the register, mask the field, shift it down, then interpret the resulting integer or bit.

## State and Persistence Behavior

The header itself has no mutable state and persists no data. The constants describe persistent hardware state held in GPU registers while the device is powered and initialized. Many fields control long-lived memory-controller behavior: arbitration weights, credit counts, channel maps, TLB enables, aperture bounds, peer BAR windows, clock gating, and blackout modes. Other fields expose transient hardware state such as busy bits, outstanding request counts, deadlock warnings, buffer fullness, interrupt/status flags, and performance counter values.

Several definitions represent clear or reset semantics in hardware, for example GECC clear bits, TLB invalidation bits, sticky/W1C XPB status, and XPB sub-block resets. Callers must follow the hardware programming sequence; this header does not encode whether a bit is write-one-to-clear, write-one-to-set, self-clearing, or read-only.

## Dependencies and Integration Points

- Depends only on the C preprocessor and include guard discipline.
- Integrates with adjacent generated AMD ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/gmc/`, especially files that define GMC 8.1 register offsets and default values.
- Used by AMDGPU GMC, VM, hub, memory-controller, power-management, interrupt, and debug/performance paths that program GMC 8.1 hardware.
- Register client names tie this file to other GPU blocks: graphics/color/depth (`CB`, `DB`, `TC`, `SH`), DMA (`SDMA`, `XDMA`), display/media (`DMIF`, `MCIF`, `UVD`, `VCE`, `VP8`, `ISP`), host/system paths (`HDP`, `IH`, `SMU`, `RLC`, `VMC`), and virtualization/peer paths.
- The file is generated-style data. Any hand edit must stay synchronized with AMD hardware documentation and the matching register-offset header; otherwise helper macros can silently program the wrong bits.

## Risks and Edge Cases

- Mask/shift mismatch is high impact: a one-bit error can corrupt memory-controller arbitration, VM apertures, peer BAR routing, or TLB behavior.
- Register family reuse is easy to confuse. Many blocks have near-identical field layouts for read vs write, hub vs CITF, and MCDW through MCDV variants, but not all masks are identical.
- Some masks cover reserved/debug fields. Writing non-reset values to reserved bits can cause undefined hardware behavior.
- Status and control fields are mixed in the same namespace. Callers must know which fields are read-only, write-only, write-one-to-clear, or self-clearing from hardware docs or driver sequencing.
- Address fields such as VM aperture, frame-buffer, AGP, P2P BAR, and peer BAR masks are truncated/encoded hardware values, not raw byte addresses. Incorrect units or shifts can misroute GPU memory traffic.
- The chunk boundary ends mid-family at `MC_XPB_CLG_CFG29`; downstream research chunks must cover the rest of the CLG table and later GMC 8.1 fields before producing a final per-file report.

## Test Signals

- Build coverage: any consumer include or macro spelling break should surface as kernel/driver compile errors.
- Register programming review: changes should be checked against AMD GMC 8.1 register documentation or generated header provenance, especially for repeated MCD, hub, VM, and XPB families.
- Hardware smoke signals: GPU bring-up, display scanout, SDMA transfers, VM fault handling, suspend/resume, and multi-GPU/P2P paths exercise these fields indirectly.
- Debug signals: readback of `MC_HUB_MISC_STATUS`, `MC_HUB_*_STATUS`, `MC_ARB_BUSY_STATUS`, GECC status, RPB performance counters, XPB pipe/interface/sticky status, and VM TLB status can validate that configured masks align with hardware behavior.
- Negative signals: hangs during memory-controller init, VM faults after aperture/TLB programming, deadlock-warning bits, stuck outstanding-request bits, incorrect channel-map behavior, or failed peer/XDMA traffic suggest a field definition or caller usage mismatch.

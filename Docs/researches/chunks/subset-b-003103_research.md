# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 85507-88072

## Scope

This chunk covers lines 85507-88072 of the generated AMDGPU NBIO 7.0 shift/mask register header. The range contains C preprocessor constants only: `#define` names ending in `__SHIFT` or `_MASK`, plus generated address-block comments. It has no functions, structs, enums, executable statements, allocation, locking, or direct runtime side effects.

The slice starts in the middle of the `SMMU_IDR0` field definitions, continues through SMMU identification/control and stream-table masks, then covers four generated address blocks:

- `nbio_iohub_nb_ioagrcfg_ioagr_cfgdec`
- `nbio_sst0_sst_core_sstcorecfg`
- `nbio_sst1_sst_core_sstcorecfg`
- `nbio_iohub_iommu_l2mmio_l2mmiocfg`
- the beginning of `nbio_iohub_nb_nbcfg_nb_cfgdec`
- the beginning of `nbio_iohub_iommu_l2_iommul2cfg`

The range ends inside the first fields of `IOMMU_L2_2_IOMMU_COMMAND`, so the later merge lane should reconcile that split with the next chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield companion to the NBIO 7.0 offset/default/SMN headers. This chunk gives AMDGPU code symbolic bit positions and masks for interpreting or constructing register values in NBIO/SMMU/IOMMU, IOAGR, SST, and NB configuration blocks.

Major hardware responsibilities represented here:

- SMMU identity and control discovery: `SMMU_IDR*`, `SMMU_IIDR`, `SMMU_AIDR`, `SMMU_CR0`, `SMMU_CR0ACK`, `SMMU_CR2`, `SMMU_GBPA`, and stream-table base/config fields.
- IOAGR clock gating, request/response decode overrides, user-bit bypass, SDP port behavior, performance counters, power-gating controls, SION scheduling/credit tables for clients 0-3, and live-lock watchdog threshold.
- SST core 0 and SST core 1 clock/enable/RSMU identity/statistics, SION scheduling tables, credit allocations, wrapper clock-gating controls, and backdoor registers.
- IOMMU L2 MMIO programming: device table, command/event/PPR/GA log bases, control and status fields, exclusion windows, extended feature reporting, SMI filters, MSI capability/address/data, MARC relocation windows, queue head/tail pointers, overflow/auto-response controls, and IOMMU performance counter banks.
- NB configuration space for `NB_NBCFG2_*`: PCI identity/header fields, command/status, subsystem IDs, PCI control, SMN indexed access windows, scratch registers, arbitration/PME fields, DRAM base/top registers, mutex registers, and NB performance control.
- The initial fields of `IOMMU_L2_2_*`, beginning with vendor/device ID and command bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public surface is generated macro metadata. Each register field normally has a pair:

- `REGISTER__FIELD__SHIFT`: zero-based bit position.
- `REGISTER__FIELD_MASK`: contiguous or single-bit mask for the encoded field.

Important macro groups in this range:

- `SMMU_IDR0` through `SMMU_IDR5`: capability discovery masks for SMMU stage support, translation table formats, coherency, broadcast TLB maintenance, HTTU, dormant hints, hypervisor support, ATS/PRI/MSI/SEV/ATOS support, ASID/VMID width, endianness, stall/termination models, stream table levels, RAS, output address size, supported granules, and stall maximum.
- `SMMU_CR0` and `SMMU_CR0ACK`: enable and acknowledgement bits for SMMU, PRI queue, event queue, command queue, ATS check, and VMW mode. These paired fields are important because software typically programs `CR0` and waits for `CR0ACK` to match enabled state.
- `SMMU_STRTAB_BASE_HI`, `SMMU_STRTAB_BASE_LO`, and `SMMU_STRTAB_BASE_CFG`: stream-table address, read-allocate hint, log2 size, split, and format fields.
- `IOAGR_GLUE_CG_LCLK_CTRL_{0,1}`: clock-gating hysteresis and per-clock soft overrides.
- `IOAGR_REQDECODE_OVERRIDE` and `IOAGR_RSPDECODE_OVERRIDE`: eight 4-bit client override slots for request and response decode routing.
- `IOAGR_PERF_CNTL` and `IOAGR_PERF_COUNT{0..3}{,_UPPER}`: four event selectors and 56-bit-style counters split into lower 32-bit and upper 24-bit fields.
- `IOAGR_PGMST_CNTL` and `IOAGR_PGSLV_CNTL`: power-gating hysteresis, enable, idleness counting, firmware power-gating exit, and slave idle hysteresis fields.
- `IOAGR_SION_*`: repeated 32-bit lower/upper SION scheduling and credit-allocation words for clients 0-3, covering S0/S1 request, read-response, write-response burst targets and time slots, plus request/data/read-response/write-response pool credit allocation.
- `SST_CORE{0,1}_*`: duplicated SST core field masks for clock control, enable control, RSMU host/client identity, statistics, SION burst/slot tables, wrapper clock-gating controls, credit allocation, and backdoor/debug words.
- `IOMMU_MMIO_*`: extensive IOMMU L2 MMIO fields. Notable subgroups include base-address high/low fields for device tables and queues, `IOMMU_MMIO_CNTRL_0` feature enables, `IOMMU_MMIO_STATUS_0` queue/overflow/interrupt state, MSI capability and MSI address/data fields, MARC base/relocation/length windows 0-3, queue head/tail pointers, PPR auto-response and overflow thresholds, and performance counter configuration/match/report fields.
- `NB_NBCFG2_*`: PCI config fields for a second NB config instance, including command enables, target/master abort status, class/header/subsystem values, PCI control bits (`PMEDis`, `SErrDis`, `MMIOEnable`, `HPDis`), SMN index/data windows 0-6, index-data mutex unlock bits, DRAM slot base/top fields, and global NB performance counter controls.

## Address-Block Layout

Generated comments in this chunk divide the range into hardware blocks:

- The opening lines continue an SMMU MMIO/register section from the previous chunk, beginning mid-`SMMU_IDR0` and then defining complete SMMU ID, architecture ID, control, global bypass/abort, and stream-table fields.
- `nbio_iohub_nb_ioagrcfg_ioagr_cfgdec` covers IO aggregator control. It begins with clock gating and decode override registers, then expands into performance/power controls and a large matrix of SION scheduling and credit allocation registers for clients 0-3.
- `nbio_sst0_sst_core_sstcorecfg` and `nbio_sst1_sst_core_sstcorecfg` are almost parallel SST core blocks. They expose clock/enable, RSMU HCID/SIID identity, statistics, SION scheduling, credit allocation, wrapper clock-gating, and backdoor registers.
- `nbio_iohub_iommu_l2mmio_l2mmiocfg` is the largest block in the chunk. It defines masks and shifts for IOMMU L2 MMIO setup, queues, interrupts, feature reporting, MARC windows, status, and performance counters.
- `nbio_iohub_nb_nbcfg_nb_cfgdec` starts the `NB_NBCFG2_*` PCI/NB config block and is complete through `NB_NBCFG2_NB_SMN_DATA_6`.
- `nbio_iohub_iommu_l2_iommul2cfg` starts at the end with `IOMMU_L2_2_IOMMU_VENDOR_ID`, `IOMMU_L2_2_IOMMU_DEVICE_ID`, and part of `IOMMU_L2_2_IOMMU_COMMAND`.

## Control Flow

This header has no direct control flow. Runtime control flow is in AMDGPU and platform driver code that includes the generated register metadata and uses it with register access helpers.

Typical consumer flow is:

1. Code includes `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and sometimes `nbio_7_0_default.h`/`nbio_7_0_smn.h`.
2. Driver code computes a register address from the offset/SMN header.
3. It reads or writes the value through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or related NBIO indexed-access paths.
4. It extracts or updates fields using these `__SHIFT` and `_MASK` constants, usually through `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent mask/shift expressions.

The flow is especially sequencing-sensitive for IOMMU/SMMU setup. For example, code that enables queues in `SMMU_CR0` or `IOMMU_MMIO_CNTRL_0` must respect acknowledgement/status fields such as `SMMU_CR0ACK`, queue head/tail pointers, overflow bits, and interrupt enables. This header only supplies the bit encodings; it does not enforce ordering, polling, reserved-bit preservation, or write-one-to-clear behavior.

## State And Persistence Behavior

The macros are compile-time constants and hold no mutable state. The state they describe lives in hardware registers, MMIO windows, PCI configuration registers, and queue-memory pointers.

State represented by this chunk includes:

- SMMU capability and enable state, including ID registers, stream-table base/configuration, control acknowledgements, and global bypass/abort fields.
- IOAGR runtime control state: clock-gating overrides, decode overrides, SDP early clock request behavior, performance counter selections/counts, power-gating hysteresis, SION scheduling tables, pool credits, and live-lock threshold.
- SST core state for both core instances: clock and enable controls, RSMU identity fields, statistics counters, SION scheduling and credits, and backdoor/debug words.
- IOMMU L2 state: device-table and queue base addresses, command/event/PPR/GA log queue head/tail pointers, IOMMU feature enables, exclusion windows, SMI filter registers, MSI routing, MARC relocation windows, overflow/active/status bits, and performance counter filters/matches/reports.
- NB config state: PCI command/status, subsystem and class/header fields, MMIO enablement, hot-plug/PME controls, indexed SMN access registers, scratch registers, mutex unlock bits, DRAM base/top fields, and global counter reset/shadow controls.

Persistence is external to this header. Across GPU reset, BACO, runtime suspend/resume, hot reset, or firmware handoff, these registers may reset, retain values, or require explicit restore depending on power domain and ASIC behavior. Driver code must preserve reserved bits and reinitialize hardware-visible state using the companion offset/default metadata and runtime policy.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and include ordering. Semantic dependencies include:

- `nbio_7_0_offset.h` for register offsets corresponding to these bitfields.
- `nbio_7_0_default.h` for reset/default values that use the same register names.
- `nbio_7_0_smn.h` for SMN-accessible address definitions.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, SOC15 setup code, and SMU include bundles that pull in NBIO 7.0 generated headers.
- AMDGPU register helper macros and field helpers used to apply these shifts/masks.
- Linux/AMDGPU integration paths for PCIe/NBIO discovery, doorbells, reset, BACO, power management, IOMMU/SMMU queue programming, MSI/AER-like interrupt routing, and performance counter diagnostics.

Cross-reference searching in the AMDGPU tree shows many direct matches are generated headers rather than handwritten code. That is expected for AMD register catalogs: handwritten consumers often refer to a smaller subset through generic helper patterns, while the generated headers preserve the complete silicon register description for build-time availability and diagnostics.

## Risks And Edge Cases

- Generated register metadata drift is the primary risk. A wrong shift or mask can silently corrupt neighboring fields during `REG_SET_FIELD` operations or decode the wrong status bit during polling.
- The chunk begins and ends mid-register-family. `SMMU_IDR0` starts in the previous chunk, and `IOMMU_L2_2_IOMMU_COMMAND` continues in the next chunk. The final per-file document must avoid treating those partial boundaries as complete register definitions.
- Reserved-bit handling is critical. Many IOMMU and PCI/NB fields include explicit `Reserved*` masks. Consumers should preserve reserved bits on read-modify-write unless the hardware specification says otherwise.
- IOMMU/SMMU queue and base-address fields are high impact. Incorrect masks for device-table bases, command/event/PPR/GA queues, or head/tail pointers can break DMA translation, lose events, or hang command processing.
- Control/status ordering is not encoded here. `SMMU_CR0`/`SMMU_CR0ACK`, IOMMU enable bits, queue run bits, overflow bits, and MSI enables need correct runtime sequencing outside this header.
- IOAGR and SST repeated SION table fields are easy to mis-index. Client, stream (`S0`/`S1`), request/read-response/write-response, burst-target/time-slot, and lower/upper naming must match the intended hardware register.
- Clock and power controls are platform-sensitive. Incorrect use of `SOFT_OVERRIDE_CLK*`, power-gating hysteresis, early clock request, or SST clock enable fields can cause idle-power regressions or access timeouts.
- PCI/NB SMN indexed access and mutex fields are shared-access hazards. Code using `NB_SMN_INDEX_*`, `NB_SMN_DATA_*`, or `NB_INDEX_DATA_MUTEX*` must coordinate access and respect unlock semantics.
- Performance counters and match registers may affect observability rather than functional state, but bad masks can make diagnostics misleading or break counter bank ownership/locking.

## Test Signals

Useful validation signals for changes touching this chunk:

- Compile AMDGPU/SOC15 code with NBIO 7.0 headers included; malformed generated lines, renamed macros, or collisions should fail at build time.
- Regenerate `nbio_7_0_sh_mask.h` from the authoritative AMD register database and compare the generated diff, especially around split boundaries and repeated IOAGR/SST/IOMMU counter blocks.
- Static-check mask/shift consistency: each mask should align with its shift and field width; repeated client/core/counter blocks should differ only by intended index/name.
- Boot/probe NBIO 7.0 hardware and watch AMDGPU, PCIe, and IOMMU logs for translation, queue, MSI, AER, or NBIO access errors.
- Exercise GPU reset, suspend/resume, BACO entry/exit, and PCIe hot/reset flows while checking that SMMU/IOMMU control/status bits reach expected states.
- Run workloads that stress DMA translation and queue activity, including graphics, SDMA, video, and KFD/compute where applicable; monitor IOMMU event/PPR/GA logs and overflow status fields.
- Validate doorbell, HDP, and SMN-indexed paths indirectly through normal queue submission and through debug tooling that reads NBIO/IOMMU counters.
- For power-management validation, compare idle/resume behavior with IOAGR/SST clock-gating and power-gating controls, watching for access timeouts and unexpected clock residency.

## Cross-Chunk Notes

This is a chunk-level report only. Later reconciliation should merge it with adjacent `nbio_7_0_sh_mask.h` chunk reports, preserving the full source path. The merge should stitch the partial `SMMU_IDR0` definition from the previous range and the partial `IOMMU_L2_2_IOMMU_COMMAND` definition from the next range, and should deduplicate repeated descriptions of IOMMU L2 MMIO families where adjacent chunks cover earlier/later instances.

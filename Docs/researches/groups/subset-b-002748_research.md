# subset-b-002748 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_0_0_sh_mask.h

## Purpose

`lsdma_7_0_0_sh_mask.h` is an AMDGPU generated register bitfield contract for LSDMA 7.0.0. It defines `__SHIFT` and `_MASK` macros for fields in the `lsdma0_lsdma0dec` address block so driver code can build, update, and inspect 32-bit LSDMA MMIO register values using the common `REG_SET_FIELD`/`REG_GET_FIELD` family. It contains no executable C logic, but it is part of the executable contract between `amdgpu/lsdma_v7_0.c`, the SOC15 MMIO helpers, and the hardware register layout.

## Important APIs, Types, And Macros

The file exports preprocessor constants only. There are no functions, structs, enums, or persistent objects.

Important macro groups:

- Firmware/microcode and register typing: `LSDMA_UCODE_ADDR`, `LSDMA_UCODE_DATA`, `LSDMA_PROGRAM`, `LSDMA_UCODE_CHECKSUM`, `LSDMA_PUB_REG_TYPE0`, and `LSDMA_PUB_REG_TYPE3`.
- Error injection and ECC/EDC: `LSDMA_ERROR_INJECT_CNTL`, `LSDMA_ERROR_INJECT_SELECT`, `LSDMA_EDC_COUNTER`, `LSDMA_EDC_COUNTER2`, `LSDMA_ECC_CNTL`, `LSDMA_ERROR_LOG`, `LSDMA_EXCEPTION_STATUS`, and `LSDMA_EA_DBIT_ADDR_*`.
- Engine status and scheduling: `LSDMA_STATUS_REG`, `LSDMA_STATUS1_REG`, `LSDMA_STATUS2_REG`, `LSDMA_STATUS3_REG`, `LSDMA_STATUS4_REG`, `LSDMA_FREEZE`, `LSDMA_CONTEXT_GROUP_BOUNDARY`, `LSDMA_SEM_WAIT_FAIL_TIMER_CNTL`, and `LSDMA_ATOMIC_*`.
- UTCL1 address translation and invalidation: `LSDMA_UTCL1_CNTL`, `LSDMA_UTCL1_WATERMK`, `LSDMA_UTCL1_RD_STATUS`, `LSDMA_UTCL1_WR_STATUS`, `LSDMA_UTCL1_INV0`, `LSDMA_UTCL1_INV1`, `LSDMA_UTCL1_INV2`, read/write `XNACK` registers, `LSDMA_UTCL1_TIMEOUT`, and `LSDMA_UTCL1_PAGE`.
- Power, clock, and low-voltage controls: `LSDMA_POWER_GATING`, `LSDMA_PGFSM_CONFIG`, `LSDMA_PGFSM_WRITE`, `LSDMA_PGFSM_READ`, `LSDMA_MEM_POWER_CTRL`, `LSDMA_CLK_CTRL`, `LSDMA_ULV_CNTL`, `LSDMA_DCC_CNTL`, and `LSDMA_HBM_PAGE_CONFIG`.
- PIO copy/fill path: `LSDMA_PIO_SRC_ADDR_LO/HI`, `LSDMA_PIO_DST_ADDR_LO/HI`, `LSDMA_PIO_COMMAND`, `LSDMA_PIO_CONSTFILL_DATA`, `LSDMA_PIO_CONTROL`, `LSDMA_PIO_STATUS`, and `LSDMA_PF_PIO_STATUS`.
- Queue programming: repeated `LSDMA_QUEUE0_*` and `LSDMA_QUEUE1_*` groups for ring buffer control/base/read/write pointers, write pointer polling, read pointer writeback, indirect buffer control/base/size, skip control, CSA address, AQL control, preemption, context status, doorbells, watermarks, dummy registers, and mid-command save/restore data.
- Performance and tuning: `LSDMA_PERFCNT_*`, `LSDMA_PERFCNT_MISC_CNTL`, `LSDMA_CRD_CNTL`, `LSDMA_BA_THRESHOLD`, `LSDMA_RD_BURST_CNTL`, `LSDMA_RELAX_ORDERING_LUT`, `LSDMA_CHICKEN_BITS`, `LSDMA_CHICKEN_BITS_2`, and `LSDMA_CE_CTRL`.

The PIO command layout is version-specific: 7.0.0 exposes `BYTE_COUNT`, `SRC_LOCATION`, `DST_LOCATION`, `SRC_ADDR_INC`, `DST_ADDR_INC`, `OVERLAP_DISABLE`, and `CONSTANT_FILL`. This differs from 7.1.0, where the command field is reduced to `COUNT`, `RAW_WAIT`, and `CONSTANT_FILL`.

## Control Flow

There is no local control flow. Runtime flow appears in `amdgpu/lsdma_v7_0.c`, which includes this header and the matching 7.0.0 offset header. The copy/fill path writes PIO source/destination address registers, clears `LSDMA_PIO_CONTROL`, reads `regLSDMA_PIO_COMMAND`, applies these bit masks through `REG_SET_FIELD`, writes the command register, and polls `LSDMA_PIO_STATUS__PIO_IDLE_MASK | LSDMA_PIO_STATUS__PIO_FIFO_EMPTY_MASK`. Memory power gating uses `LSDMA_MEM_POWER_CTRL__MEM_POWER_CTRL_EN_MASK` through `REG_SET_FIELD`.

## State And Persistence Behavior

The header itself is stateless and read-only at compile time. The macros describe hardware state persisted in LSDMA MMIO registers while the GPU is powered and the block is active. Queue registers hold ring/IB addresses, pointers, doorbell offsets, context state, and mid-command data. Status/error registers expose transient execution state, FIFO state, page fault/XNACK state, ECC/EDC observations, and interrupt causes. Power and clock control fields can change hardware block residency or memory power state. None of this state is persisted by the header; persistence is in device registers and driver-managed GPU memory.

## Dependencies

This header depends only on C preprocessing and the convention used by AMDGPU generated register headers. Consumers depend on:

- Matching offset definitions, especially `lsdma_7_0_0_offset.h`, for register addresses.
- SOC15 MMIO helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.
- AMDGPU bitfield helpers such as `REG_SET_FIELD`, which derive field names from `<register>__<field>_MASK` and `<register>__<field>__SHIFT`.

The include guard is `_lsdma_7_0_0_SH_MASK_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_0.c` includes this file and uses PIO status, command, and memory power control masks.

Broader integration is through the ASIC register include hierarchy under `drivers/gpu/drm/amd/include/asic_reg/lsdma`, where each supported LSDMA version has paired offset and shift/mask headers. The queue, ECC, interrupt, UTCL1, and performance definitions are available to future or indirect consumers even when the current local 7.0.0 C file only uses a small subset.

## Risks

- Register drift is the primary risk: if the generated mask/shift values do not match the silicon or firmware expectations, `REG_SET_FIELD` can write valid-looking but wrong MMIO values.
- Version confusion is high impact. The 7.0.0 PIO command field names and status error bit positions differ from 7.1.0, so sharing code between versions without checking field names can silently break copy/fill or error handling.
- Several macros describe power, clock, ECC, interrupt, queue, and VM invalidation state. Incorrect use can cause hangs, missed interrupts, stale translations, or data corruption.
- Some fields are named `RESERVED` or expose dummy registers; production code should not infer semantics beyond the generated register contract.
- The file provides no range validation. For example, byte counts, VMIDs, queue sizes, offsets, and watermarks must be constrained by callers before being shifted into registers.

## Test Signals

- Build coverage that compiles `amdgpu/lsdma_v7_0.c` with this header is the first signal, because renamed fields fail at compile time.
- Runtime copy/fill validation should exercise `lsdma_v7_0_funcs.copy_mem` and `.fill_mem`, checking that PIO status reaches idle and FIFO-empty and that destination memory matches expectations.
- Power-management tests should toggle the 7.0.0 memory power control path and confirm no register access failures or copy/fill regressions.
- Hardware bring-up should compare key register programming against the ASIC register specification or generated-header source, especially `LSDMA_PIO_COMMAND`, `LSDMA_PIO_STATUS`, queue pointer fields, and `LSDMA_MEM_POWER_CTRL`.
- RAS/diagnostic tests can observe ECC/EDC and exception status fields if a platform exposes LSDMA error injection or fault logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_offset.h

## Purpose

`lsdma_7_1_0_offset.h` defines the LSDMA 7.1.0 MMIO register offsets used by the AMDGPU LSDMA PIO copy/fill implementation. It is a compact generated offset header for the PIO register window. The values are consumed by SOC15 register helpers to compute actual MMIO addresses for source address, destination address, command, constant-fill data, control, and status registers.

## Important APIs, Types, And Macros

The file exports only `#define` constants. There are no functions or types.

PIO register offsets:

- `regLSDMA_PIO_SRC_ADDR_LO` at `0x0080` and `regLSDMA_PIO_SRC_ADDR_HI` at `0x0081`.
- `regLSDMA_PIO_DST_ADDR_LO` at `0x0082` and `regLSDMA_PIO_DST_ADDR_HI` at `0x0083`.
- `regLSDMA_PIO_COMMAND` at `0x0084`.
- `regLSDMA_PIO_CONSTFILL_DATA` at `0x0085`.
- `regLSDMA_PIO_CONTROL` at `0x0086`.
- `regLSDMA_PIO_STATUS` at `0x008a`.

Each register has a matching `_BASE_IDX` macro set to `0`, matching the SOC15 helper convention for selecting a register base segment.

## Control Flow

There is no local control flow. At runtime, `amdgpu/lsdma_v7_1.c` passes these constants to `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`. The typical sequence is: write source and destination address halves, write control, update command fields using the matching 7.1.0 shift/mask header, write the command register, then poll the status register until `PIO_IDLE` and `PIO_FIFO_EMPTY` are set.

## State And Persistence Behavior

The header is stateless. The offsets identify hardware registers whose contents are transient device state. Source/destination address and command/control registers are programmed per PIO operation. Constant-fill data persists in the register until rewritten or reset. Status reports in-flight command/FIFO/error state and is not persisted by this file.

## Dependencies

Consumers require:

- `lsdma_7_1_0_sh_mask.h` for the bit layout inside the registers defined here.
- SOC15 register access macros and base-index conventions.
- Driver code that knows the LSDMA instance and register block name, currently `LSDMA, 0` in `amdgpu/lsdma_v7_1.c`.

The include guard is `_lsdma_7_1_0_OFFSET_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c` includes this header and uses every defined register except that the copy path does not write `PIO_CONSTFILL_DATA`, while the fill path does.

This file also defines the version boundary between 7.0.0 and 7.1.0: 7.1.0 places the PIO window at offsets `0x80` through `0x8a`, whereas 7.0.0 uses a different offset set.

## Risks

- Any incorrect offset directs MMIO writes to the wrong register, which can corrupt unrelated LSDMA state or leave PIO operations stuck.
- The sparse gap between `regLSDMA_PIO_CONTROL` (`0x0086`) and `regLSDMA_PIO_STATUS` (`0x008a`) must be preserved; code should not infer contiguous register coverage.
- The `_BASE_IDX` values are part of the SOC15 address calculation. Changing them without a matching register-base update would break access.
- Pairing this offset header with the wrong shift/mask header can compile but program incompatible bitfields.

## Test Signals

- Compile `amdgpu/lsdma_v7_1.c` to catch missing register names.
- Runtime smoke tests for 7.1.0 should call copy and fill operations and verify that the wait path sees `PIO_IDLE` and `PIO_FIFO_EMPTY` in `regLSDMA_PIO_STATUS`.
- Hardware register traces can confirm writes land at offsets `0x80` to `0x86` and status reads at `0x8a`.
- Regression comparison against 7.0.0 should verify that each version uses its own offset header and does not share PIO offset constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_sh_mask.h

## Purpose

`lsdma_7_1_0_sh_mask.h` defines the bit shifts and masks for the small LSDMA 7.1.0 PIO register set. It is the companion to `lsdma_7_1_0_offset.h`: offsets identify the registers, while this header defines how to encode and decode fields in those registers.

## Important APIs, Types, And Macros

The file exports preprocessor constants only.

Register field groups:

- `LSDMA_PIO_STATUS`: command FIFO depth (`CMD_IN_FIFO`), command processing count/state (`CMD_PROCESSING`), error bits for invalid address, zero count, DRAM ECC, SRAM ECC, write/read return NACK general errors, write/read return NACK protection errors, request drop, FIFO empty/full, and PIO idle.
- `LSDMA_PIO_SRC_ADDR_LO` and `LSDMA_PIO_SRC_ADDR_HI`: 64-bit source address split into 32-bit halves.
- `LSDMA_PIO_DST_ADDR_LO` and `LSDMA_PIO_DST_ADDR_HI`: 64-bit destination address split into 32-bit halves.
- `LSDMA_PIO_CONTROL`: VMID plus destination/source memory attributes such as GPA, system memory, GCC, snoop, reuse hint, and compression enable.
- `LSDMA_PIO_COMMAND`: `COUNT` in bits 0-25, `RAW_WAIT` at bit 30, and `CONSTANT_FILL` at bit 31.
- `LSDMA_PIO_CONSTFILL_DATA`: 32-bit fill payload.

The command mask shape matters for callers: the count field is `0x03ffffff`, so any caller-provided size must fit the 26-bit field before `REG_SET_FIELD` is used.

## Control Flow

There is no local control flow. The runtime consumer is `amdgpu/lsdma_v7_1.c`. In copy mode, the driver writes source and destination address registers, sets `LSDMA_PIO_COMMAND.COUNT`, clears `RAW_WAIT`, clears `CONSTANT_FILL`, and writes the command register. In fill mode, it first writes `LSDMA_PIO_CONSTFILL_DATA`, writes the destination address, sets `COUNT`, clears `RAW_WAIT`, sets `CONSTANT_FILL`, and writes the command register. Both paths then poll status for `PIO_IDLE | PIO_FIFO_EMPTY`.

## State And Persistence Behavior

The header has no state. The described hardware registers carry transient command programming and status. Address, command, control, and fill-data values persist only as hardware register contents until overwritten or reset. Status bits reflect queue occupancy, in-flight processing, idle state, and sticky or transient error conditions depending on hardware behavior.

## Dependencies

Consumers require:

- `lsdma_7_1_0_offset.h` for register offsets.
- SOC15 register access helpers.
- AMDGPU bitfield helper naming conventions: `REG_SET_FIELD(tmp, LSDMA_PIO_COMMAND, COUNT, size)` expands using `LSDMA_PIO_COMMAND__COUNT_MASK` and `LSDMA_PIO_COMMAND__COUNT__SHIFT`.

The include guard is `_lsdma_7_1_0_SH_MASK_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c` includes this file and uses `LSDMA_PIO_STATUS__PIO_IDLE_MASK`, `LSDMA_PIO_STATUS__PIO_FIFO_EMPTY_MASK`, and `LSDMA_PIO_COMMAND` fields `COUNT`, `RAW_WAIT`, and `CONSTANT_FILL`.

The fields are a streamlined 7.1.0 PIO contract. Compared with 7.0.0, source/destination location, address increment, and overlap-disable command fields are absent; status error bits also shift upward for the early error fields and include `ERROR_REQ_DROP`.

## Risks

- Code ported from 7.0.0 must not use `BYTE_COUNT`, `SRC_LOCATION`, `DST_LOCATION`, `SRC_ADDR_INC`, `DST_ADDR_INC`, or `OVERLAP_DISABLE`; those fields are not present in this header.
- `COUNT` is 26 bits. Oversized copy/fill requests can be truncated by field insertion unless callers split or validate sizes.
- Error handling in the current direct consumer only waits for idle/empty and logs a generic failure on wait error; these masks expose more detailed error bits that can be missed if diagnostics do not read status on failure.
- Pairing these masks with a mismatched offset header can produce valid writes to the wrong register layout.

## Test Signals

- Compile coverage for `amdgpu/lsdma_v7_1.c` verifies field names expected by the driver.
- Runtime copy/fill tests should validate both `CONSTANT_FILL=0` and `CONSTANT_FILL=1` command paths.
- Negative or fault-injection testing should inspect `LSDMA_PIO_STATUS` error bits, especially invalid address, zero count, ECC, NACK, and request-drop fields.
- Boundary tests should exercise maximum legal `COUNT` and confirm larger operations are rejected or split by higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_default.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_default.h -->

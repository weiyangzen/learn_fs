# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_offset.h

## Purpose

This header is a generated AMDGPU register-offset map for the `SDMA6` engine in the `sdma6_sdma6dec` address block. It defines the symbolic `mmSDMA6_*` register offsets and matching `*_BASE_IDX` selectors used by the SOC15 register access helpers to locate SDMA6 registers in the device register aperture. The file is data-only: it has no functions, structs, enums, or runtime logic.

The comment at the top of the register list identifies the SDMA6 block base address as `0x7c000`. The exported offsets are relative register indices, not standalone CPU virtual addresses. Runtime code combines these offsets with IP block base tables, for example `SDMA6_BASE` from `arct_ip_offset.h`, through macros such as `SOC15_REG_OFFSET`.

## Important API Surface

The public interface is the macro namespace:

- `mmSDMA6_<REGISTER>`: relative register offsets for SDMA6, beginning with common engine registers such as `mmSDMA6_UCODE_ADDR`, `mmSDMA6_VM_CNTL`, `mmSDMA6_POWER_CNTL`, `mmSDMA6_CNTL`, status registers, UTCL1 controls, error logs, performance counters, and GPU IOV violation logs.
- `mmSDMA6_<REGISTER>_BASE_IDX`: base segment selectors for each register. In this file every listed base index is `1`, so consumers rely on the second base segment for the addressed SDMA6 register space.
- Queue register groups:
  - `GFX` queue registers at `0x0080` through the mid-command area ending at `mmSDMA6_GFX_MIDCMD_CNTL`.
  - `PAGE` queue registers at `0x00d8` through `mmSDMA6_PAGE_MIDCMD_CNTL`.
  - `RLC0` through `RLC7` queue registers from `0x0130` through `0x03e1`.

Each queue group exposes the same functional pattern: ring-buffer control and base registers, read/write pointers, write-pointer polling addresses, indirect-buffer control/base/size, skip/context/doorbell/status registers, watermark and doorbell-offset registers, context-save-area addresses, preemption, AQL control, minor pointer update, and mid-command data/control registers.

There are no C types or callable APIs in this header. Its API contract is preprocessor-level compatibility with AMDGPU code and with the paired field-definition header `sdma6_4_2_2_sh_mask.h`.

## Dependencies

This header has only a local include guard and no direct `#include` dependencies. It is intended to be included by driver source alongside:

- `sdma6/sdma6_4_2_2_sh_mask.h`, which defines bit shifts and masks for the registers named here.
- SOC15 register helpers from `soc15.h` / `soc15_common.h`, which combine hardware IP identifiers, instances, base indices, and register offsets.
- SDMA IP base definitions from generated IP-offset headers such as `arct_ip_offset.h`.

Direct include sites found in this tree are `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c` and `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`.

## Integration Points

`sdma_v4_0.c` includes this file with the other SDMA engine offset and mask headers. It uses `mmSDMA6_CHICKEN_BITS`, `mmSDMA6_GB_ADDR_CONFIG`, `mmSDMA6_GB_ADDR_CONFIG_READ`, and `mmSDMA6_UTCL1_TIMEOUT` in the SDMA golden-settings table for the SDMA6 engine. The same source routes sequence number 6 to `SDMA6_HWIP` register bases and to the `SOC15_IH_CLIENTID_SDMA6` interrupt client ID.

`amdgpu_amdkfd_arcturus.c` includes this file to derive the SDMA6 RLC queue register base for KFD/HSA queue handling. In `get_sdma_rlc_reg_offset`, engine id 6 computes `SOC15_REG_OFFSET(SDMA6, 0, mmSDMA6_RLC0_RB_CNTL) - mmSDMA6_RLC0_RB_CNTL`, then applies a per-queue stride based on the difference between adjacent RLC ring-buffer-control offsets.

The file also aligns with the generated SDMA0 through SDMA7 offset headers used for multi-engine devices. That symmetry matters because shared code often selects an SDMA engine by numeric id and then expects equivalent register names and equivalent queue layout.

## Control Flow

There is no runtime control flow in this header. At compile time, inclusion makes the `mmSDMA6_*` macros available to C sources. At runtime, consumers follow this pattern:

1. Select a hardware IP block, usually `SDMA6` or `SDMA6_HWIP`, based on engine id or ASIC-specific setup.
2. Combine the selected IP base with one of this header's relative offsets through SOC15 helpers.
3. Read or write the resulting MMIO register using AMDGPU register access helpers.
4. Use the paired mask header when individual fields within a register need to be encoded or decoded.

The queue register layout is regular enough for consumers to calculate offsets for RLC queues rather than spelling every queue register directly. The RLC queue blocks use a `0x58` offset stride from `RLC0_RB_CNTL` to `RLC1_RB_CNTL` and onward through `RLC7`.

## State and Persistence Behavior

The header itself stores no state and persists no data. It names hardware registers that represent or control SDMA6 hardware state. Important state categories include:

- Firmware loading and verification through `UCODE_ADDR`, `UCODE_DATA`, and `UCODE_CHECKSUM`.
- VM and virtualization state through `VM_CNTL`, `VM_CTX_*`, `ACTIVE_FCN_ID`, `VF_ENABLE`, `VIRT_RESET_REQ`, and GPU IOV violation logs.
- Engine power, clock, control, status, freeze, quantum, EDC, and error-log registers.
- Ring-buffer and indirect-buffer state for GFX, PAGE, and RLC queues, including base addresses, read/write pointers, polling addresses, doorbells, preemption, and context-save-area addresses.
- Performance and diagnostic counters through `PERFMON_CNTL`, `PERFCOUNTER*_RESULT`, `F32_COUNTER`, and EDC counters.

Persistence is hardware-defined. Register contents may survive until reset, power transition, firmware reinitialization, GPU reset, or explicit driver writes. Driver code must not treat the macros as owning state; they are addresses into state owned by the SDMA engine.

## Risks

The highest risk is offset drift against the ASIC register specification. A wrong value can silently direct reads or writes to the wrong MMIO register, causing queue hangs, firmware load failures, GPU reset paths, virtualization breakage, or corrupted diagnostics.

The all-`1` base-index convention is also important. If the generated base index does not match the IP base table used by `SOC15_REG_OFFSET`, the numeric offset can be correct but the final address can still target the wrong register segment.

Queue-stride assumptions are another risk. KFD code derives per-queue RLC offsets from the distance between `RLC0` and `RLC1` queue blocks. A future generated header with nonuniform queue spacing would break callers that assume a constant stride.

Because this file is generated and broad, manual edits are risky. Local changes can desynchronize it from the paired `sdma6_4_2_2_sh_mask.h` field definitions or from sibling SDMA engine headers, creating compile-time success with runtime hardware misprogramming.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for `sdma_v4_0.c` and `amdgpu_amdkfd_arcturus.c` confirms that all referenced `mmSDMA6_*` names are present and do not collide with sibling SDMA headers.
- Static comparison against generated SDMA6 register specifications should confirm each offset and base index, especially common registers, GFX/PAGE queues, and `RLC0` through `RLC7`.
- Cross-header consistency checks should verify that every register with bitfields in `sdma6_4_2_2_sh_mask.h` has a corresponding offset macro here.
- Runtime SDMA initialization should apply SDMA6 golden settings without MMIO faults and should leave SDMA status registers in expected idle/runnable states.
- KFD queue tests on Arcturus-class hardware should create, doorbell, preempt, and tear down SDMA RLC queues for engine id 6 without queue-base miscalculation.
- GPU reset, SR-IOV, VM, and interrupt tests should include SDMA6 paths because this header defines registers for virtual-function control, reset requests, active function id, GPU IOV violation logs, and SDMA6 interrupt client routing.

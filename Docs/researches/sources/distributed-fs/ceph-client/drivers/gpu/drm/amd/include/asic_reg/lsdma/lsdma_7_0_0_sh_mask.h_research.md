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

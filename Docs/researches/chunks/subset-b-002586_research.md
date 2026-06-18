# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 1-2452

## Scope

This chunk covers the opening section of the generated GC 12.1.0 register offset header. It starts with the AMD MIT-style license and include guard, then defines SDMA-related register address macros for:

- `SDMA0` public/control decode block `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmadec`, base address `0x4980`.
- `SDMA0` hypervisor decode block `sdmahypdec`, base address `0x3e200`.
- `SDMA0` PSP, performance-select, performance-data, and power decode blocks.
- The beginning of `SDMA1` public/control decode block `sdmadec:1`, base address `0x6180`.

The range contains 2,399 `#define reg...` lines: 1,268 for `regSDMA0...` and 1,131 for `regSDMA1...`. Each real register offset is paired with a `<register>_BASE_IDX` macro. Lines 1-2452 end in the middle of the `regSDMA1_SDMA_QUEUE9_MIDCMD_DATA*` family; the next chunk continues that queue block.

## Purpose

This header is a hardware register ABI map for AMD GC 12.1.0 SDMA engines. It supplies register offsets, not field encodings. Driver code combines these offsets with:

- `gc/gc_12_1_0_sh_mask.h` for field shifts and masks.
- SOC15 access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `SOC15_REG_ENTRY_STR`, and `REG_SET_FIELD`.
- Per-instance offset logic in SDMA, KFD, and debug paths.

The values are offsets in the generated AMD register namespace. The `_BASE_IDX` macro chooses the register aperture/base table index used by SOC15 accessors: most SDMA0/SDMA1 public queue/control registers in this chunk use base index `0`, while hypervisor, PSP, performance, and power sub-blocks use base index `1`.

## Important Macro Families

The first SDMA0 public block begins at line 28. It defines global SDMA engine registers including decode start, microcode revision, global timestamp, power/control/chicken/cache controls, status registers, watchdog, queue status, SDMA ID/version, atomic controls, DCC, UTCL1 controls and status, freeze controls, error logs, dummy registers, RLC clock-gating control, IOV violation logs, interrupt status, invalid address reporting, scratch RAM access, queue reset/dequeue requests, CE control, RAS/poison status, and MEMHUB control.

The largest part of the chunk is the repeated SDMA queue register layout. For `SDMA0`, queues 0 through 9 are fully present. Each queue has a regular stride: `regSDMA0_SDMA_QUEUE1_RB_CNTL - regSDMA0_SDMA_QUEUE0_RB_CNTL == 0x3c`. The per-queue family includes:

- Ring buffer control/base/read pointer/write pointer registers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
- Read-pointer writeback address registers: `RB_RPTR_ADDR_LO/HI`.
- Indirect buffer state: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Doorbell state: `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`.
- Context save area and scheduling/preemption state: `CSA_ADDR_LO/HI`, `SCHEDULE_CNTL`, `PREEMPT`, `CONTEXT_SWITCH_STATUS`, and `CONTEXT_STATUS`.
- Write-pointer polling and AQL controls: `RB_WPTR_POLL_ADDR_LO/HI`, `RB_AQL_CNTL`, and `MINOR_PTR_UPDATE`.
- Mid-command resume state: `MIDCMD_CNTL` and `MIDCMD_DATA0` through `MIDCMD_DATA10`.
- Utilization and wait-threshold registers, MQD base/control registers, and dummy registers.

After the SDMA0 public queue block, the hypervisor decode section provides VM and virtualization-facing SDMA0 registers: `SDMA_VM_CTX_LO/HI`, `SDMA_ACTIVE_FCN_ID`, `SDMA_VM_CTX_CNTL`, `SDMA_VIRT_RESET_REQ`, context/public register type maps, `SDMA_VM_CNTL`, `SDMA_MCU_CNTL`, and instruction-cache base/control registers. These are the privileged engine-control offsets used when the PF/hypervisor side needs to manage SDMA context, virtual reset, register exposure, or SDMA MCU state.

The PSP decode section in this range has `regSDMA0_SDMA_MCU_DM_FROM_RST_ADDR_OFFSET`. The performance select/data blocks define selector/configuration and result registers for six SDMA performance counters, including `SDMA_PERFCNT_PERFCOUNTER*_CFG`, `SDMA_PERFCOUNTER*_SELECT`, `SDMA_PERFCOUNTER*_SELECT1`, and `SDMA_PERFCOUNTER*_LO/HI`. The power decode section contains `regSDMA0_GFX_ICG_SDMA_CTRL`.

The SDMA1 public block mirrors SDMA0 with an offset delta of `0x600` for the public `BASE_IDX 0` region. For example, `regSDMA0_SDMA_CNTL` is `0x000d`, while `regSDMA1_SDMA_CNTL` is `0x060d`; `regSDMA0_SDMA_QUEUE0_RB_CNTL` is `0x0200`, while `regSDMA1_SDMA_QUEUE0_RB_CNTL` is `0x0800`. Within this chunk, SDMA1 global public registers and queues 0 through most of queue 9 are present, ending at `regSDMA1_SDMA_QUEUE9_MIDCMD_DATA3`.

## APIs, Types, and Functions

This file defines no C types, functions, variables, or inline helpers. Its public API is the generated macro namespace:

- `regSDMA0_*` and `regSDMA1_*` register-offset constants.
- Matching `regSDMA0_*_BASE_IDX` and `regSDMA1_*_BASE_IDX` base-index constants.

The API contract is compile-time name stability and numeric accuracy. Higher-level code assumes these macros can be used directly in SOC15 register helpers and in arithmetic that depends on register layout regularity.

## Control Flow and State Behavior

There is no executable control flow in this header. Runtime behavior appears only in consumers that use these constants to read or write MMIO registers.

The hardware state described by this chunk is substantial. It includes SDMA firmware/control state, queue ring base and pointer state, indirect-buffer state, doorbell routing, context-save addresses, scheduling/preemption state, mid-command replay state, MQD state, utilization counters, VM context state, virtual reset state, performance counter setup/results, interrupt/status/error reporting, UTCL1 translation/cache state, RAS and poison status, and power/clock-gating state.

Several covered registers represent persistent engine or queue configuration until reset or reprogramming, such as ring base addresses, doorbell offsets, VM context, MQD base, performance counter select registers, and watchdog settings. Others are volatile status/counter registers, such as timestamp, queue status, UTCL1 read/write status, error logs, utilization registers, performance counter result registers, RAS status, and poison info. Some are command-like control points where write sequencing matters, such as queue reset/dequeue request, virtual reset request, freeze trigger, minor pointer update, preempt, and MCU control.

## Dependencies and Integration Points

Observed includes of this header in the source tree include `amdgpu/sdma_v7_1.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gfxhub_v12_1.c`, `amdgpu/imu_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/soc_v1_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`. These files include the companion `gc_12_1_0_sh_mask.h` when they need field-level composition.

`amdgpu/sdma_v7_1.c` is the clearest consumer. It includes this header, defines `SDMA1_REG_OFFSET 0x600`, and builds an SDMA register dump list with `SOC15_REG_ENTRY_STR(GC, 0, regSDMA0_...)`. The SDMA v7.1 resume/stop paths read and write `regSDMA0_SDMA_QUEUE0_RB_CNTL`, `IB_CNTL`, pointer registers, polling-address registers, doorbell registers, `MINOR_PTR_UPDATE`, `WATCHDOG_CNTL`, `UTCL1_CNTL`, `UTCL1_PAGE`, and `MCU_CNTL` through `sdma_v7_1_get_reg_offset()`.

`amdgpu/sdma_v7_1.c` also initializes SDMA MQD images using the same register family: it composes `sdmax_rlcx_rb_cntl`, ring base, polling address, read-pointer writeback address, IB control, doorbell offset, doorbell enable, AQL control, dummy register, and CSA address fields. That MQD data later becomes firmware-visible queue state rather than direct MMIO writes.

`amdgpu/amdgpu_amdkfd_gfx_v12_1.c` depends on regular register spacing. Its `get_sdma_rlc_reg_offset()` computes the SDMA engine base with `SOC15_REG_OFFSET(..., regSDMA0_SDMA_QUEUE0_RB_CNTL)` or `regSDMA1_SDMA_QUEUE0_RB_CNTL`, then computes an RLC queue offset with `queue_id * (regSDMA0_SDMA_QUEUE1_RB_CNTL - regSDMA0_SDMA_QUEUE0_RB_CNTL)`. Its SDMA HQD dump code assumes a contiguous dump range from `regSDMA0_SDMA_QUEUE0_RB_CNTL` to `regSDMA0_SDMA_QUEUE0_CONTEXT_STATUS`.

`amdkfd/kfd_mqd_manager_v12_1.c` uses the sibling shift/mask definitions for fields in registers whose offsets are defined here. Its SDMA MQD update path programs queue size, VMID, read-pointer writeback enable/timer, MCU write-pointer polling, queue base, rptr/wptr backing addresses, doorbell offset, and schedule quantum. This ties the generated offset namespace to KFD compute queue creation and update.

## Risks

- Numeric drift in any `regSDMA*_...` value can route MMIO reads/writes to the wrong hardware register. The likely results include engine hangs, broken queue submission, lost doorbells, invalid context save/restore, bad performance data, or failed reset/recovery.
- The repeated queue layout invites arithmetic dependencies. Consumers assume queue stride `0x3c` and SDMA1 public offset delta `0x600`; changing one queue macro without preserving the pattern would break KFD queue dumps and RLC queue offset calculation.
- Base-index drift is subtle. A correct offset with the wrong `_BASE_IDX` can use the wrong SOC15 aperture, especially around the split between public `BASE_IDX 0` registers and hypervisor/performance/power `BASE_IDX 1` registers.
- The chunk ends mid-family at `regSDMA1_SDMA_QUEUE9_MIDCMD_DATA3`. Any final merged per-file report must connect this chunk with the following chunk before making complete claims about SDMA1 queue9 or later SDMA1 hypervisor/performance blocks.
- Queue pointer and doorbell registers have strict sequencing requirements in consumers. For example, SDMA v7.1 sets `MINOR_PTR_UPDATE` before reducing write pointers and toggles doorbell enable/offset based on ring mode. The offsets alone do not encode these ordering constraints.
- Virtualization-related registers such as VM context, active function ID, virtual reset request, public/context register-type maps, and MCU controls are privilege-sensitive. Misuse can affect PF/VF isolation or leave SDMA state inconsistent across reset paths.
- Performance counter selector/result offsets must match the companion masks. A mismatch between `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h` can silently program one counter while decoding another.

## Test and Validation Signals

Useful validation is mostly compile, bring-up, and hardware integration coverage:

- Build AMDGPU and KFD paths that include `gc/gc_12_1_0_offset.h`; this catches missing or renamed macros used by SDMA v7.1, GFX 12.1, MES, GFXHUB, IMU, SOC, and KFD code.
- Exercise SDMA v7.1 ring bring-up and shutdown. The path should disable/enable `RB_CNTL` and `IB_CNTL`, program RB/IB base and pointer registers, configure read-pointer writeback and write-pointer polling, set `MINOR_PTR_UPDATE`, program doorbells, and unhalt `MCU_CNTL`.
- Run KFD SDMA queue creation/update and SDMA HQD dump tests. These validate that queue stride and SDMA0/SDMA1 engine offset arithmetic still match the generated register layout.
- Validate bare-metal and SR-IOV VF behavior. SDMA v7.1 uses different write-pointer/doorbell behavior for VF mode, and the hypervisor decode offsets in this chunk are part of virtualized SDMA management.
- Check SDMA reset, preemption, watchdog, UTCL1, and error-reporting paths through GPU reset/recovery and memory fault tests.
- Use performance/debug tests that select and read SDMA performance counters to ensure the selector/result offsets in this header match the companion field definitions.

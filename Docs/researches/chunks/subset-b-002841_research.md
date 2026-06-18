# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 1-2367

## Scope

This chunk covers the opening 2,367 lines of the generated AMDGPU MMHUB 9.4.1 shift/mask header. The range starts the include guard `_mmhub_9_4_1_SH_MASK_HEADER`, then defines bit-field shift and mask macros for the `mmhub_dagb_dagbdec0` address block and the beginning of `mmhub_dagb_dagbdec1`. It contains the complete `DAGB0` field surface and cuts off in the first `DAGB1_RD_CNTL_MISC` fields; later lines continue that partially captured register.

Within this chunk there are 2,177 `#define` lines: one include guard define, 1,089 `__SHIFT` definitions, and 1,087 `_MASK` definitions. The shift/mask mismatch is expected because the chunk boundary lands inside `DAGB1_RD_CNTL_MISC`.

## Purpose

The file is a machine-generated hardware register field map. It does not implement executable logic; it gives the AMDGPU driver symbolic names for MMHUB 9.4.1 DAGB register bit positions and masks so C code can safely construct read-modify-write values with register helper macros such as `REG_SET_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

The `DAGB` blocks covered here describe arbitration, credits, virtual channels, outstanding request limits, pending status, clock gating, snoop override, FIFO/credit status, and performance counter controls for MMHUB data/address gateway blocks. These fields matter because MMHUB owns GPU memory-management traffic routing between clients, TLBs, memory fabric, and cache/coherency paths.

## Important Macro Families

The chunk is dominated by repeated register-field pairs:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI15` and `DAGB0_WRCLI0` through `DAGB0_WRCLI15` define per-client read/write arbitration fields: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, urgency thresholds, max/min bandwidth controls, OSD limiter enable, and max OSD.
- `DAGB0_RD_CNTL`, `DAGB0_WR_CNTL`, `DAGB0_RD_GMI_CNTL`, and `DAGB0_WR_GMI_CNTL` define global read/write timing and fabric-control fields such as SCLK frequency, bandwidth windows, IO level override, EA credit, level, max burst, and lazy timer.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB` define DAGB enable, jump-ahead, self-init disable, and `WHOAMI` identity fields for address/data paths.
- `DAGB0_*_MAX_BURST*` and `DAGB0_*_LAZY_TIMER*` define packed 4-bit nibbles for VC0-VC7 or CLIENT0-CLIENT15 burst/timer tuning.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL` define per-virtual-channel storage credit, EA credit, bandwidth, and OSD limit fields.
- `DAGB0_RD_TLB_CREDIT` and `DAGB0_WR_TLB_CREDIT` define six packed TLB credit fields.
- `DAGB0_*_PENDING` registers expose full-width busy bitmaps for read/write client ask/go/global-send/TLB/OARB/OSD states, plus write DBUS pending states.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose full-width enable/value bitmaps used by the driver to force coherency behavior for selected write clients.
- `DAGB0_CNTL_MISC` and `DAGB0_CNTL_MISC2` define VC remapping, bandwidth cycle timing, urgency boost/halt, clock-gating disable bits for request/return/TLB paths, busy behavior disables, swap control, and read-return FIFO deadlock credits.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL` expose status bitmaps.
- `DAGB0_PERFCOUNTER_*` defines low/high counter values, compare value, counter selection/configuration, triggers, enable, clear, and stop-on-saturate controls.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE13` reserve full 32-bit register fields.
- `DAGB1_RDCLI0` through `DAGB1_RD_VC7_CNTL` repeat the read-side DAGB0 pattern for the next DAGB decoder instance; `DAGB1_RD_CNTL_MISC` begins at the chunk boundary.

## APIs, Types, and Functions

There are no C functions, structs, enums, or storage objects in this chunk. The exported API is the preprocessor namespace itself:

- `<REGISTER>__<FIELD>__SHIFT` macros provide bit offsets.
- `<REGISTER>__<FIELD>_MASK` macros provide the corresponding register masks.

Consumers are expected to combine these macros with the matching MMHUB 9.4.1 offset header (`mmhub_9_4_1_offset.h`) and AMDGPU register access helpers. The naming convention is part of the interface: register names here match `mmDAGB...` register address macros from the offset header and field names used by AMDGPU register helper macros.

## Control Flow

This header contributes no runtime branches or sequencing. Control flow appears only in consumers that use the masks during MMHUB setup and power-management transitions.

The directly relevant consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes this header with `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`. Two visible call paths use fields from this chunk:

- `mmhub_v9_4_init_snoop_override_regs()` computes the distance between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates DAGB instances across the two MMHUB instances, and sets bit 15 in both override and override-value registers so SDMA writes probe-invalidate RW lines.
- `mmhub_v9_4_update_medium_grain_clock_gating()` computes the distance between `mmDAGB1_CNTL_MISC2` and `mmDAGB0_CNTL_MISC2`, then clears or sets the `DAGB0_CNTL_MISC2__DISABLE_*_CG_MASK` bits across DAGB instances depending on `AMD_CG_SUPPORT_MC_MGCG` and the requested clock-gating state. `mmhub_v9_4_get_clockgating()` reads related masks when reporting clock-gating state.

## State and Persistence Behavior

The macros themselves are compile-time constants and hold no state. They describe persistent MMIO register state in the GPU. Writes using these masks affect hardware configuration until overwritten by later driver actions, GPU reset/reinitialization, power management transitions, or firmware/hardware reset behavior.

State represented by this chunk includes client-to-VC mapping, per-client and per-VC bandwidth/credit limits, outstanding request controls, pending/busy status, snoop override state, clock-gating disable state, FIFO/credit status, and performance counter programming. Status-style registers such as `*_PENDING`, `*_FIFO_*`, `*_CREDITS_FULL`, and perf counter result registers should be treated as live hardware observations, not durable software state.

## Dependencies and Integration Points

This header depends on inclusion from AMDGPU ASIC-specific code that already knows the MMHUB 9.4.1 register addresses. It is paired with:

- `mmhub_9_4_1_offset.h` for register addresses such as `mmDAGB0_CNTL_MISC2` and `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE`.
- `mmhub_9_4_1_default.h` for default register values.
- AMDGPU SOC15 register helpers in `soc15.h` / `soc15_common.h`.
- Higher-level MMHUB logic in `amdgpu/mmhub_v9_4.c`.

The DAGB0/DAGB1 spacing assumptions are important integration details. `mmhub_v9_4.c` derives per-DAGB register offsets by subtracting DAGB0 addresses from DAGB1 addresses, then applying that distance in loops. Field masks from this header must remain aligned with those address macros, or read-modify-write operations may alter the wrong bits in repeated DAGB instances.

## Risks

- Because this is generated hardware metadata, a single incorrect mask or shift can silently corrupt unrelated register fields during read-modify-write operations.
- Full-width masks such as `0xFFFFFFFFL` for pending, reserve, perf low, and snoop override registers require consumers to know which bits are meaningful for a specific ASIC and client topology.
- Repeated DAGB0/DAGB1 patterns make copy-generation errors hard to detect by review. DAGB instance spacing used by consumers depends on consistent register layout across instances.
- Clock-gating masks in `DAGB0_CNTL_MISC2` are power-management sensitive. Reversed semantics or stale masks can leave memory-controller clock gating disabled, or gate paths that must remain active.
- The chunk boundary splits `DAGB1_RD_CNTL_MISC`; research or reconciliation that treats this chunk as a complete file-level view could miss the remaining masks and shifts.

## Test Signals

Useful validation signals are mostly compile-time and hardware bring-up oriented:

- Build AMDGPU with `mmhub_v9_4.c` enabled and confirm all referenced `DAGB0_*` and `DAGB1_*` masks resolve against this header.
- On MMHUB 9.4.1 ASICs, exercise driver init and confirm SDMA coherency-sensitive workloads pass after `mmhub_v9_4_init_snoop_override_regs()` sets SDMA client bit 15.
- Toggle medium-grain clock gating and verify `AMD_CG_SUPPORT_MC_MGCG` reporting changes as expected without memory faults, hangs, or RAS noise.
- Use register dumps before/after clock-gating transitions to confirm only `DAGB*_CNTL_MISC2` clock-gating disable bits change.
- Run GPU memory stress, VM fault, SDMA copy, suspend/resume, and reset tests; failures in these areas can indicate bad MMHUB routing, credit, snoop, or clock-gating field definitions.

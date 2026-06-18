# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 35136-37567

## Scope

This chunk is a generated AMDGPU GC 11.0.0 shift/mask header segment. It contains C preprocessor constants only: for each hardware register field, `REGISTER__FIELD__SHIFT` gives the bit position and `REGISTER__FIELD_MASK` gives the encoded mask. The matching register offsets are in `gc_11_0_0_offset.h`, and defaults are in the generated GC default header. Driver code combines these masks with `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and firmware/golden-register tables to program or inspect GC 11 hardware.

The range starts in the shader profiling processor area with `RLC_SPP_SSF_THRESHOLD_1` and ends at the first field group for `ICG_GL1C_CLK_CTRL`. It spans three generated address-block areas: the tail of the main RLC block, the complete `gc_rlcsdec` RLC sequencer/control block, the compact `gc_pfvfdec_rlc` PF/VF RLC block, and the beginning of `gc_pwrdec` graphics power/clock-gating controls.

## Purpose

The purpose of this header slice is to define the bitfield contract for GC 11 RLC, RLC sequencer, firmware messaging, interrupt, residency, doorbell, IMU, SPM, and clock-gating registers. These macros are not optional documentation; they are the source-level ABI used by AMDGPU, KFD, MES, IMU, display, gfxhub, SDMA, and SOC initialization code when writing packed MMIO values.

The main covered register families are:

- RLC SPP profiling and capture fields: shader-type thresholds, inflight read address/data, shader IDs, CAM hit/lock/conflict state, PVT counters, stall updates, PBB override info, reset bits, and SPP CAM access.
- RLC doorbell interfaces: `RLC_RLCP_DOORBELL_*` and `RLC_XT_DOORBELL_*` range, mode, ID enable, valid-status, and data fields for four doorbells each.
- RLC residency counters: power, clock, deep-sleep, ultra-low-voltage, PCC, and general counter reset/enable/ack/overflow fields plus event/reference data counters.
- RLC graphics interrupt client status: SE, SDMA, UTCL2, and PMM interrupt masks, clear bits, buffer levels, loading, overflow, and protocol-error latches.
- RLC SPM and microcontroller support: global/SE delay indirect address/data, SPM thread trace interrupt enable, GPU clock counter LSB/MSB, LX6 run/reset/debug controls, XT interrupt vectors, and XT fault/status fields.
- RLC/SMU/IMU firmware communication: safe-mode command/message/response fields, RLCV and SMU command/message registers, SMU response and arguments, IMU bootload address/size/misc/reset-vector fields, RLCS IMU/RLC message mailboxes, telemetry, mutex, RAM access, and doorbell fence fields.
- `gc_rlcsdec` sequencing and power management: CGCG request/status, SOC/GFX deep-sleep masks, GPM power/clock/light-sleep/power-gating status, aborted power-down sequence, DIDT stall, IOV state, soft reset, WGP status, CP/SPM/SDMA interrupt controls, bootload status, power brake controls, GRBM idle/busy latches, general scratch registers, GCR data/status, UTCL2 override controls, PMM CGCG, and graphics memory/power-management controls.
- `gc_pfvfdec_rlc` PF/VF-facing RLC fields: `RLC_SAFE_MODE`, SPM sample/memory-controller configuration, SPM interrupt state, CSIB address/length, CP scheduler bits, EOF/spare/PACE/RLCV spare interrupt fields.
- `gc_pwrdec` graphics clock/power controls: TCC disable masks, CGTT controls for GS/NGG, PA, SC, SQG, TA, DB, CB, CP/CPF/CPC, SQ ALU/TEX/LDS WGP force bits, ICG controls for SP/GCEA/GL1H/GL1C, and MGCG overrides for GL1I/GL1R and CHI/CHR.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or persistent variables. Its API is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` is the low bit for a packed field.
- `REGISTER__FIELD_MASK` is the full field mask after shifting.
- Full-register data fields such as `*_DATA_MASK`, `*_CMD_MASK`, `*_ARG_MASK`, and many scratch/general registers use `0xFFFFFFFFL`.
- Reserved fields are named and masked, which lets register-generation tools and driver reviewers see which bits must be preserved or avoided.

The macros are consumed through common AMDGPU register helpers. `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` depends on both the shift and mask names. `REG_GET_FIELD(value, REGISTER, FIELD)` uses the same pair to decode status bits. Raw writes use masks directly where only a bit needs setting; for example `gfx_v11_0_set_safe_mode()` writes `RLC_SAFE_MODE__CMD_MASK` and `1 << RLC_SAFE_MODE__MESSAGE__SHIFT`, then polls `REG_GET_FIELD(..., RLC_SAFE_MODE, CMD)`.

Important direct include consumers for `gc_11_0_0_sh_mask.h` in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, KFD queue/MQD managers, display plane/display code, gfxhub, SDMA, and SOC21 initialization. This chunk also pairs with register-offset macros such as `regRLC_SAFE_MODE`, `regRLC_RLCS_*`, `regCGTT_*`, and `regICG_*`.

## Control Flow

There is no executable control flow in the header. Runtime control flow appears in the consumers that build, write, read, poll, or preserve register values:

- Safe-mode entry/exit writes the `RLC_SAFE_MODE` command/message fields and waits for the command bit to clear. Wrong masks here can make safe-mode handshakes time out or make later register programming race active RLC firmware.
- Firmware and IMU bring-up paths write IMU/RLC RAM, bootload, reset-vector, mailbox, and message-control fields. The `RLC_IMU_*` and `RLC_RLCS_IMU_*` groups define the bit layout for bootload addresses, firmware size, cold-boot and voltage-change exits, request/done/change toggles, RAM request/ack toggles, and telemetry.
- RLC/RLCS power sequencing uses CGCG request/status, deep-sleep allow/busy masks, GPM status, GRBM idle/busy status, WGP status, power brake, and memory-power-control fields. Control flow is usually poll-and-wait: request a transition, read status, and only proceed when busy/changing bits settle.
- Interrupt handling and diagnostic paths use the RLC graphics interrupt client status fields, CP/SPM/SDMA interrupt ack/status/info registers, EOF/spare interrupts, and legacy GPM interrupt disable/status fields. The masks distinguish pending, ack, auto-ack-active, last-client, buffer overflow, and protocol-error state.
- Doorbell control flow programs lower/upper doorbell address ranges, per-doorbell modes, optional doorbell IDs, and valid/status/data latches. These registers are part of firmware/microcontroller command delivery rather than normal user queue doorbells.
- SPP profiling flow enables capture/threshold/state in earlier lines and this chunk provides threshold pairs, PVT histogram counters, CAM/tag access, profile information, stalls, and resets used by profiling/debug code.
- Clock-gating and power-control flow sets or clears soft overrides, stall overrides, on-delay/off-hysteresis controls, force-WGP-on bits, TCC disable masks, and MGCG/ICG override bits. These fields are typically used during ASIC initialization, golden-register setup, power-management transitions, or hardware workarounds.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware state they describe is volatile MMIO state with several persistence scopes:

- Safe-mode, RLCV, SMU, and mailbox registers represent handshakes between the kernel driver, RLC firmware, SMU, IMU, and microcontrollers. Values are transient but can block boot, reset, gfxoff, or power-management transitions if a request/done/ack bit is misencoded.
- Residency event/reference counters and GPU clock counters accumulate hardware activity until reset, overflow, or device reset. Their `RESET`, `ENABLE`, `RESET_ACK`, `ENABLE_ACK`, and `COUNTER_OVERFLOW` bits are part of the measurement protocol.
- SPP CAM, PVT histogram, profiling, global shader ID, and stall/reset fields expose debug/profiling state that can persist until explicit reset bits or profiling disable paths clear it.
- Interrupt status, buffer overflow, protocol error, pending, and changed bits are latched diagnostic state. Some are cleared by writing the matching clear/ack mask; others are sampled by firmware or debug code.
- RLCS general registers and auxiliary registers are scratch or address fields visible to firmware and driver diagnostics. They may survive until overwritten by firmware, reset recovery, or explicit initialization.
- IMU/RLC RAM data/address/control fields represent firmware-accessible memory windows. Their contents and toggles matter across bootload and runtime firmware messaging sequences.
- Clock-gating, deep-sleep, memory light-sleep/deep-sleep, and power-gating override bits affect persistent device operating mode until a later power-management operation or reset changes them.

## Dependencies and Integration Points

This chunk depends on the generated GC 11 register ecosystem: `gc_11_0_0_offset.h` for register addresses, `gc_11_0_0_default.h` for reset/default values, SOC15 register access helpers, firmware binaries for RLC/MES/IMU behavior, and AMDGPU/KFD code that chooses when each field is programmed.

Important integration points include:

- `amdgpu/gfx_v11_0.c` for RLC safe-mode handshakes, graphics initialization, power-management, clock-gating, and reset flows.
- `amdgpu/imu_v11_0.c` for IMU firmware loading and RLC RAM/golden-setting programming that relies on IMU/RLC register fields.
- `amdgpu/mes_v11_0.c` and KFD queue management for compute/MES operation that runs alongside RLC, SPM, interrupt, doorbell, and scheduler state.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c` and KFD MQD/device queue manager code for GC 11 compute setup, debug, and queue lifecycle paths that include RLC-safe operations and status polling.
- Display, gfxhub, SDMA, and SOC21 initialization code, which include this header because GC 11 masks are shared across VM, display plane, SDMA, and SOC-level setup paths.
- Firmware-mediated features: RLC/SMU messages, IMU/RLC message mailboxes, RLCV commands, SRM/GPM commands, power-brake notifications, graphics memory power controls, and IOV status.

Because the field macros are generated, many integration failures are indirect. A bad field may compile cleanly, then surface only as a firmware timeout, unacknowledged interrupt, broken gfxoff/deep-sleep transition, failed IMU bootload, or invalid diagnostic counter.

## Risks

The main risk is silent bitfield drift. Shift and mask constants are plain preprocessor numbers, so incorrect values usually do not cause compile failures if the macro names still exist. A wrong mask can clear reserved bits, fail to set a request bit, sample the wrong status bit, or write a value into an adjacent control field.

High-risk areas in this chunk are:

- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, and `RLC_SMU_SAFE_MODE`, because safe-mode sequencing gates register programming during initialization, reset, and power transitions.
- IMU bootload and IMU/RLC message fields, because incorrect request, done, change, ack, RAM address, bootload size, or reset-vector fields can prevent firmware startup or block IMU/RLC communication.
- RLCS CGCG, deep-sleep, GPM, WGP, GRBM idle/busy, and power-brake fields, because incorrect masks can leave the device stuck in a power transition, falsely report idle, or disable important clock/power gating.
- Interrupt and status groups, because bad ack/clear masks can lose interrupts or leave latched overflow/protocol-error state uncleared.
- Doorbell range/control/status/data groups, because mode, ID enable, and address-range fields control microcontroller-visible doorbell delivery.
- Clock-gating and MGCG/ICG override registers, because forcing or stalling the wrong clock domain can cause hangs, performance regressions, excessive power, or missed workaround behavior.
- Reserved masks, especially in generated control registers, because writing through an imprecise mask may modify undocumented hardware bits.

Manual edits to this file are especially risky. The correct source of truth is the AMD register database/generator that produced the offset, default, and shift/mask headers together. If one header is regenerated without the others, `REG_SET_FIELD` and `REG_GET_FIELD` can address the correct register but encode the wrong field layout.

## Test Signals

Compile-time signals are limited to missing or renamed macros in AMDGPU/KFD/MES/IMU consumers. Successful compilation does not validate numeric masks.

Runtime validation should focus on GC 11 hardware or a hardware-backed test environment. Strong signals include successful GPU probe, RLC and IMU firmware load, safe-mode enter/exit without timeout, MES startup, KFD process and queue creation, suspend/resume, GPU reset recovery, and stable gfxoff/deep-sleep transitions.

Power and clock-gating signals include no regressions in golden-register application, no hangs during CGCG/MGCG/ICG enablement, sane residency counters, expected counter reset/enable acknowledgements, and stable performance/power telemetry. Firmware signals include successful IMU/RLC mailbox exchange, bootload status reaching completion, no stuck request/done/ack toggles, and valid telemetry fields.

Interrupt and diagnostic signals include correct CP/SPM/SDMA interrupt acknowledgement, no unexpected RLC graphics IH buffer overflow or protocol-error latches, sensible GRBM idle/busy and GPM status under workload and idle transitions, and working SPM/thread-trace/profiling paths. Doorbell-specific signals include valid RLCP/XT doorbell status transitions and no firmware command-delivery timeouts.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 4720-7085

## Scope

This chunk covers the middle of the generated MMHUB 1.8.0 shift/mask header for AMD GPU register programming. The range starts inside the `aid_mmhub_dagb_dagbdec2` address block, completes the later write-side `DAGB2_*` field definitions, covers almost the entire `aid_mmhub_dagb_dagbdec3` block, and begins the `aid_mmhub_dagb_dagbdec4` block through `DAGB4_RDCLI2` field definitions.

The source is a register-description header, not executable C. It defines preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. These constants describe bit positions and bit masks for MMHUB DAGB registers; companion register addresses live in `mmhub_1_8_0_offset.h`, and the values are consumed by AMDGPU register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

## Purpose

The purpose of this chunk is to give the driver exact symbolic names for programming and decoding MMHUB DAGB arbitration, credit, virtual-channel, clock-gating, fatal-error, FIFO-status, performance-counter, and L1 TLB control registers on the MMHUB 1.8.0 IP block. The DAGB blocks appear as repeated hardware decoder instances. This chunk completes instance 2, defines instance 3 in detail, and starts instance 4.

The mask/shift pairs keep register manipulation centralized and mechanically checkable. Driver code can compose a register value with named fields instead of hard-coding bit positions. Diagnostic code can also decode hardware status registers, especially fatal-error and counter registers, using the same definitions.

## Important APIs, Types, And Macro Families

There are no functions, structs, enums, or callable APIs in this range. The important interface is the macro namespace exported by the header.

`DAGB2_WR_*` macros at the start of the chunk complete the write path for DAGB instance 2. The range includes write address/data DAGB burst and lazy-timer fields, write data DAGB control fields, write virtual-channel controls `DAGB2_WR_VC0_CNTL` through `DAGB2_WR_VC7_CNTL`, write miscellaneous credit controls, pending-bit status registers, GPU snoop override masks, DAGB delay/misc controls, fatal-error controls/status, FIFO/credit-full status, performance counters, and `DAGB2_L1TLB_REG_RW`.

`DAGB3_RDCLI0` through `DAGB3_RDCLI15` define the repeated read-client configuration layout for DAGB instance 3. Each client has fields for virtual channel selection, TLB credit checking, high/low urgency thresholds, maximum and minimum bandwidth controls, OSD limiter enable, and maximum outstanding depth. The same layout later appears for `DAGB3_WRCLI0` through `DAGB3_WRCLI15` on the write side and begins again for `DAGB4_RDCLI0` through the visible portion of `DAGB4_RDCLI2`.

`DAGB3_RD_CNTL`, `DAGB3_WR_CNTL`, `DAGB3_RD_GMI_CNTL`, and `DAGB3_WR_GMI_CNTL` describe global read/write arbitration windows, SCLK frequency encoding, IO-level override, shared virtual-channel selection, fixed jump behavior, EA credits, GMI level, maximum burst size, and lazy timers.

`DAGB3_RD_ADDR_DAGB`, `DAGB3_WR_ADDR_DAGB`, and `DAGB3_WR_DATA_DAGB` describe DAGB enable and policy fields, including `DAGB_ENABLE`, `ENABLE_JUMP_AHEAD`, `DISABLE_SELF_INIT`, `WHOAMI`, and read/write address `JUMP_MODE`. Per-client maximum burst and lazy-timer registers split clients 0-7 and 8-15 into separate 32-bit registers with 4-bit lanes.

`DAGB3_RD_OUTPUT_DAGB_MAX_BURST`, `DAGB3_RD_OUTPUT_DAGB_LAZY_TIMER`, `DAGB3_WR_OUTPUT_DAGB_MAX_BURST`, and `DAGB3_WR_OUTPUT_DAGB_LAZY_TIMER` use 4-bit lanes for virtual channels 0-7. These fields tune output burst lengths and timer behavior per virtual channel.

`DAGB3_RD_CGTT_CLK_CTRL`, `DAGB3_WR_CGTT_CLK_CTRL`, `DAGB3_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB3_L1TLB_WR_CGTT_CLK_CTRL`, `DAGB3_ATCVM_RD_CGTT_CLK_CTRL`, and `DAGB3_ATCVM_WR_CGTT_CLK_CTRL` expose clock-gating/timing controls: on delay, off hysteresis, light-sleep assert hysteresis, light-sleep override, and soft override.

`DAGB3_RD_VC0_CNTL` through `DAGB3_RD_VC7_CNTL` and `DAGB3_WR_VC0_CNTL` through `DAGB3_WR_VC7_CNTL` define virtual-channel credit and bandwidth controls. The shared layout includes storage credit, EA credit, max bandwidth enable/value, min bandwidth enable/value, OSD limiter enable, and max OSD.

`DAGB3_RD_TLB_CREDIT`, `DAGB3_RD_RDRET_CREDIT_CNTL`, `DAGB3_WR_TLB_CREDIT`, `DAGB3_WR_DATA_CREDIT`, `DAGB3_WR_MISC_CREDIT`, `DAGB3_WR_OSD_CREDIT_CNTL1`, `DAGB3_WR_OSD_CREDIT_CNTL2`, and `DAGB3_WR_ATOMIC_FIFO_CREDIT_CNTL1` define TLB, read-return, data, atomic, OSD, and miscellaneous credit fields used to bound request flow through the DAGB pipelines.

`DAGB3_RDCLI_*_PENDING` and `DAGB3_WRCLI_*_PENDING` macros decode per-client pending bitmaps for ask/go/global-send/TLB/OARB/OSD stages and, on the write side, DBUS ask/go stages. These are status fields, not configuration fields.

`DAGB3_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB3_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose 16-bit masks that let software override GPU snoop behavior per write client. `mmhub_v1_8.c` has a concrete integration point for the same register family: `mmhub_v1_8_init_snoop_override_regs()` computes the distance between DAGB instances and sets SDMA client bit 15 in the DAGB write-client snoop override registers across the available DAGB instances.

`DAGB3_CNTL_MISC` and `DAGB3_CNTL_MISC2` cover cross-cutting DAGB controls, including EA virtual-channel remapping, bandwidth initialization/gap cycles, urgency boost/halt controls, clock-gating disable bits, EA busy disables, swap control, RDRET FIFO performance control, HDP client ID, and RDRET FIFO deadlock credits.

`DAGB3_FATAL_ERROR_CNTL`, `DAGB3_FATAL_ERROR_CLEAR`, and `DAGB3_FATAL_ERROR_STATUS0` through `DAGB3_FATAL_ERROR_STATUS3` define fatal-error filtering, clearing, and captured error fields. The status registers expose validity, client ID, low/high address bits, transaction tag, VFID/VF, address space, IO, size, debug mask, FED, allocation state, unit ID, operation, security level, TMZ read/write bits, snoop, invalid, NACK, read-only, memory-log, and end-of-packet state.

`DAGB3_FIFO_EMPTY`, `DAGB3_FIFO_FULL`, `DAGB3_WR_CREDITS_FULL`, and `DAGB3_RD_CREDITS_FULL` are status bitmap definitions for FIFO and credit saturation. `DAGB3_PERFCOUNTER_LO`, `DAGB3_PERFCOUNTER_HI`, `DAGB3_PERFCOUNTER0_CFG`, `DAGB3_PERFCOUNTER1_CFG`, `DAGB3_PERFCOUNTER2_CFG`, and `DAGB3_PERFCOUNTER_RSLT_CNTL` describe a small performance-counter block with select ranges, mode, enable, clear, start/stop triggers, enable-any, clear-all, and stop-on-saturate fields.

`DAGB3_L1TLB_REG_RW` describes indirect L1 TLB control access bits: write/read control strobes, VMID exception interrupt control, write-data parity checking, read-return check disable, and a reserved high-bit mask.

## Control Flow

This header chunk has no local control flow. It does not branch, call functions, allocate memory, or update state by itself. Control flow is introduced only when driver code includes the header and uses these macros in register programming or status decode paths.

The typical downstream flow is:

1. Include `mmhub_1_8_0_offset.h` for register addresses and `mmhub_1_8_0_sh_mask.h` for field positions.
2. Read a 32-bit MMHUB register with `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, or a related access helper.
3. Modify one or more fields with `REG_SET_FIELD` or decode them with `REG_GET_FIELD`, using the masks and shifts in this header.
4. Write the updated value back with `WREG32_SOC15` or `WREG32_SOC15_OFFSET`.

The visible `mmhub_v1_8.c` integration follows that pattern for DAGB snoop override registers. It uses offset-header symbols to address repeated DAGB instances and writes the SDMA client override bit. The masks in this chunk make equivalent field-aware writes possible for DAGB2, DAGB3, and DAGB4 fields even when this particular C file does not reference every field directly.

## State And Persistence Behavior

The macros themselves have no runtime state and no persistence. They are compile-time constants.

The hardware state represented by this chunk is persistent MMIO register state inside the GPU's MMHUB while the device is powered and configured. Writes to the corresponding registers can affect request arbitration, read/write client routing, virtual-channel credit accounting, clock-gating behavior, snoop behavior, fatal-error latching, performance-counter selection, and L1 TLB control. Reads from status registers expose transient pipeline state such as pending bits, FIFO empty/full status, credit-full status, fatal-error captures, and performance-counter values.

Driver-level persistence depends on how the consuming code applies these fields during device initialization, reset, suspend/resume, SR-IOV mode transitions, RAS handling, and debug collection. The header does not save or restore register values; callers must decide when to reprogram them.

## Dependencies And Integration Points

This chunk depends on `mmhub_1_8_0_offset.h` for the matching `regDAGB*` register address definitions. For example, the companion offset file maps `regDAGB3_RDCLI0` at `0x0180`, `regDAGB3_WR_VC0_CNTL` at `0x01d1`, `regDAGB3_L1TLB_REG_RW` at `0x01ff`, and `regDAGB4_RDCLI0` at `0x0200`. The masks here are only meaningful when paired with those addresses.

The primary C integration point for this header is `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which includes both the offset and shift/mask headers. That file initializes MMHUB VM page-table registers, aperture registers, TLB controls, and DAGB write-client snoop overrides for all active AID/MMHUB instances. Other AMDGPU infrastructure provides the register access macros, the `REG_SET_FIELD` and `REG_GET_FIELD` helpers, and SOC15 instance addressing.

The definitions are also structurally aligned with neighboring ASIC/IP headers such as `mmhub_1_7_sh_mask.h` and `mmhub_9_4_1_sh_mask.h`. That alignment matters because AMDGPU code often carries similar initialization patterns across IP versions while selecting different offset/mask headers for each hardware generation.

## Risks And Edge Cases

Because this is generated hardware-interface data, the main risk is register-layout drift. A wrong shift or mask can corrupt unrelated bits in the same 32-bit register, which is especially risky for credit, clock-gating, TLB, and fatal-error control registers.

The chunk boundary begins in the middle of a DAGB2 register family and ends in the middle of `DAGB4_RDCLI2`. A final merged per-file analysis must reconcile adjacent chunks before drawing conclusions about complete DAGB2 and DAGB4 coverage.

Many fields are repeated across clients, virtual channels, and DAGB instances. Copy-generation mistakes are easy to miss visually: a single instance number, client number, mask width, or shift nibble could be wrong while the surrounding pattern still looks valid.

Several registers expose status or clear semantics rather than ordinary read/write configuration. For example, fatal-error clear, pending-bit, FIFO-full, and performance-counter clear fields should not be treated as stable configuration fields. Calling code must preserve hardware-defined write-one-to-clear or latch behavior from the register spec.

The `DAGB*_L1TLB_REG_RW` fields include read/write control strobes and a broad reserved mask. Software should avoid writing reserved bits unless the hardware programming guide explicitly requires a value.

Virtualization and partitioning are relevant. Fatal-error status includes VFID/VF fields, while `mmhub_v1_8.c` skips some programming in SR-IOV VF mode. Code using these masks must respect PF/VF ownership of MMHUB registers.

## Test Signals

Build-time coverage should include compiling AMDGPU with `mmhub_v1_8.c` so the generated header, include guard, and macro names remain valid with the offset header and common SOC15 register helpers.

Static validation should compare this header against the authoritative register database or against adjacent generated headers for the same IP family. High-signal checks include verifying that each `*_MASK` width matches its corresponding `*_SHIFT`, that client/VC lane masks advance by the expected 4-bit or 5-bit increments, and that DAGB3 offsets in `mmhub_1_8_0_offset.h` line up with the DAGB3 mask block in this file.

Runtime validation should focus on consumers rather than this header alone. For snoop override programming, read back `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` after `mmhub_v1_8_init_snoop_override_regs()` and verify that SDMA client bit 15 is set only when the driver is allowed to program those registers.

Hardware/debug tests can exercise fatal-error capture and decode using `DAGB*_FATAL_ERROR_STATUS*` fields, performance-counter programming through the `DAGB*_PERFCOUNTER*_CFG` and result-control masks, and FIFO/credit/pending status collection under load.

Regression signals should include suspend/resume and GPU reset paths, because MMHUB register programming often needs to be restored after power or reset events. SR-IOV PF and VF tests are also important because some registers are not safe for guest-side programming.

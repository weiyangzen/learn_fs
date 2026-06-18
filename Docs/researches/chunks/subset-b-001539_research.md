# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 4962-7315

## Scope And Purpose

This chunk is part of AMDGPU's generated DCE 12.0 register shift/mask header. It contains no executable code; it is compile-time hardware register metadata for the display controller engine. Each pair of `__SHIFT` and `_MASK` macros describes how a named bitfield is packed inside a 32-bit display MMIO or indirect register.

The requested range starts in the middle of `DMCU_INTERRUPT_TO_UC_EN_MASK`, then covers DMCU interrupt routing, DMCU scratch/communication registers, BL1 PWM backlight and ABM controls, ABM histogram/luma-statistics registers, DMCU perfmon interrupt routing, Azalia display-audio controller and codec-function registers, audio port-connectivity overrides, GTC group offsets, and the beginning of the DAC/analog output block. It ends inside `DAC_FIFO_STATUS`, before the following `DC_I2C_CONTROL` block.

The path is under a Ceph source mirror, but this file is AMDGPU Linux kernel display-driver metadata. There is no Ceph filesystem logic in this chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime variables in this range. The API surface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for the field in the register.
- Consumers combine these with matching address macros from `dce_12_0_offset.h` and register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_FIELD()`, `REG_GET_FIELD()`, `set_reg_field_value()`, and `get_reg_field_value()`.

The DMCU and ABM-related macros dominate the first half of the chunk. `DMCU_INTERRUPT_TO_UC_EN_MASK` and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL` describe whether ABM, MCP, DSI/DCFE power, static-screen, external software, and VBLANK events are sent to the display microcontroller and how they map to XIRQ selection bits. The `_1` variants and `DMCU_DPRX_*` families add more interrupt status, enable, and XIRQ-selection layouts for extra static-screen, DPRX, HPD RX, AUX, GPIO, timer, software, and command-complete events. `DMCU_INT_CNT`, `DC_DMCU_SCRATCH`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, and `DMCU_UC_CLK_GATING_CNTL` define counters, scratch storage, firmware-checksum byte sampling, and microcontroller IRAM/ERAM read-delay or clock-gating fields.

The master/slave communication-port registers are byte-sliced. `MASTER_COMM_DATA_REG1` through `REG3`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `SLAVE_COMM_DATA_REG1` through `REG3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG` expose four byte fields per data/command register plus interrupt and "message to host in progress" control bits. These fields back firmware/driver mailbox-style communication with the display microcontroller.

The backlight and ABM families include `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `BL1_PWM_USER_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_FINAL_DUTY_CYCLE`, `BL1_PWM_MINIMUM_DUTY_CYCLE`, `BL1_PWM_ABM_CNTL`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, and `BL1_PWM_GRP2_REG_LOCK`. They describe ambient/user/target/current/final/minimum brightness levels, ABM PWM enable, graduated-step timing, update-sample rate, and group register locking.

`DC_ABM1_*` fields describe the adaptive backlight module's control, coefficient selection, ambient contrast enhancement offsets/slopes/thresholds, luma-statistics and histogram outputs, sample rates, shift metadata, overscan pixel value, master lock, and read-progress state. The chunk includes luma sum, min/max, filtered min/max, pixel count, overscan-bin, threshold, min/max pixel-value counts, and 24 histogram result registers.

The Azalia block covers display audio control and codec metadata. `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, `AZALIA_SOCCLK_CONTROL`, several DMA-control registers, `AZALIA_RIRB_AND_DP_CONTROL`, cyclic-buffer position/sync, global capabilities, payload capabilities, stream-arbiter control, input/output CRC controls/results, and memory power-control/status define the controller-side audio transport, clocking, DMA, CRC, and memory power-gating layout. `AZALIA_F0_CODEC_*` macros define vendor/device/revision IDs, channel count, resync FIFO control, supported rates and formats, power states, power-state control, reset, subsystem ID response, and converter synchronization for codec function 0.

The final portion starts the DAC/analog-output register set. `DAC_ENABLE`, `DAC_SOURCE_SELECT`, CRC control/signature registers, sync tristate control, stereosync select, autodetect controls/status/interrupt, forced output data, powerdown and control bits, comparator enable/output, power control, DFT config, and the first `DAC_FIFO_STATUS` fields describe analog-output enablement, test/CRC diagnostics, load detect, forced output, per-channel power, comparator state, and FIFO calibration/status fields.

## Control Flow

This chunk has no local control flow. Runtime behavior is determined by distant display-driver code that includes `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`, builds ASIC-specific register tables, and then reads or writes hardware registers through the DAL/DC register helper layer.

A typical consumer sequence is:

1. Select the DCE 12.0 register offset from `dce_12_0_offset.h`.
2. Read a register with `REG_READ`, direct MMIO helpers, or an indirect accessor such as the Azalia endpoint path.
3. Extract a field with the generated mask and shift, or through `REG_GET`/`get_reg_field_value`.
4. Update one or more fields with the generated mask and shift, usually through `REG_SET`, `REG_UPDATE`, `REG_SET_FIELD`, or `set_reg_field_value`.
5. Write the packed value back to the hardware register in the ordering required by the display block, firmware mailbox, audio endpoint, or power-management path.

Observed integration patterns in the tree include DCE 12.0 code including this header in `dce120_timing_generator.c`, `dce120_hwseq.c`, `dce120_resource.c`, `irq_service_dce120.c`, and DCE 12.0 GPIO translation/factory code. The common audio implementation in `display/dc/dce/dce_audio.c` uses register/mask/shift tables and indirect Azalia endpoint reads/writes, while DCE 12.0 resource construction provides the corresponding mask/shift values for newer ASIC-specific instances.

Because the file is macro-only, a wrong definition does not fail locally. It changes the behavior of later driver flows: interrupt routing to DMCU, backlight/ABM programming, firmware communication, Azalia audio setup, audio DMA/CRC/memory power behavior, codec capability exposure, analog DAC load detection, and DAC diagnostic reads.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It describes state held in display-controller hardware registers, firmware-visible mailboxes, counters, or status latches. The persistence lifetime is controlled by hardware, firmware, suspend/resume, display reinitialization, power gating, hotplug events, link/audio stream setup, and ASIC reset.

State categories in this chunk include:

- DMCU interrupt routing and status: enable, XIRQ selection, and status bits decide which display events are delivered to the microcontroller and host-visible paths.
- DMCU communication state: scratch, master/slave data bytes, command bytes, interrupt bits, and host-message progress bits carry mailbox payloads and synchronization status.
- Backlight and ABM state: PWM brightness levels, final/minimum duty, ABM enable, step timing, sample rates, locks, ambient/contrast coefficients, luma statistics, pixel counts, histogram bins, and overscan values represent both programmed policy and measured display content.
- Perfmon and DPRX interrupt state: per-monitor interrupt status, mask, and routing fields report and gate performance, AUX/HPD, GPIO, timer, software, and command-completion events.
- Azalia audio state: clock gating, DTO phase/module values, SOCCLK control, DMA engine status, RIRB/DP control, cyclic buffer position/sync, capabilities, stream payload limits, CRC captures, memory power state, and codec function identity/capability/power/reset fields.
- DAC state: analog source selection, CRC mode/results, sync tristate, autodetect mode/status/interrupt, forced output, per-channel powerdown, comparator references/outputs, power-control mode, DFT config, and FIFO calibration/status.

The macros do not encode access semantics. Field names alone do not say whether a bit is read-only, sticky, write-one-to-clear, self-clearing, firmware-owned, safe only while a block is disabled, or latched on specific frame boundaries. Consumers must rely on ASIC programming guides and existing display-driver sequencing.

## Dependencies And Integration Points

This header depends on the generated AMD register-header layout. The matching DCE 12.0 address definitions live in `dce_12_0_offset.h`; this `*_sh_mask.h` file supplies the field layout inside those addresses.

Primary integration points are:

- DCE 12.0 resource initialization, where register addresses, masks, and shifts are assembled into per-block tables for timing generators, link encoders, audio objects, memory input, IRQ service, GPIO, and hardware sequencing.
- The display register helper layer in `reg_helper.h`, which expects the `__SHIFT` and `_MASK` naming convention used here.
- DMCU firmware loading and control paths, including DMCU ERAM/IRAM firmware IDs tracked by AMDGPU firmware and PSP/SMU code, and DMCU mailbox-style master/slave communication registers.
- Backlight and adaptive backlight management paths that consume BL1 PWM and `DC_ABM1_*` fields to program brightness policy, content statistics, histogram reading, and lock/update behavior.
- IRQ service and static-screen/DPRX/AUX/HPD paths that consume interrupt status, mask, and XIRQ-selection fields.
- Display audio resource and codec programming. DCE audio code uses Azalia endpoint index/data registers for indirect codec-function programming, and DCE 12.0 resources provide compatible field masks for Azalia DTO, DMA, capabilities, CRC, memory power, and codec metadata.
- Analog output and diagnostic paths for DAC enable/source selection, CRC signatures, autodetect/load-detect, forced output, comparator state, powerdown, DFT, and FIFO calibration.

The DMCU, ABM, audio, and DAC blocks cross subsystem boundaries. DMCU settings interact with firmware, ABM interacts with panel/backlight policy, Azalia interacts with DRM audio/HDMI/DP stream setup, and DAC fields interact with legacy analog encoder and load-detection behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A one-bit mask or shift error can corrupt adjacent fields during read-modify-write, route interrupts to the wrong destination, misread sticky status, or expose incorrect audio/display capabilities.

High-risk fields include DMCU interrupt enables and XIRQ selections, master/slave communication interrupt and progress bits, ABM group locks, backlight target/current/final/minimum duty fields, histogram/luma result fields, Azalia DMA controls, cyclic-buffer sync, memory power control/status, codec power/reset fields, and DAC autodetect/powerdown/forced-output controls. Errors in these areas can present as missed display firmware events, stuck mailbox transactions, flickering or incorrect backlight levels, failed ABM updates, missing HDMI/DP audio, DMA/RIRB failures, incorrect codec enumeration, failed analog load detection, or damaged diagnostics.

Repeated byte-sliced and interrupt-family definitions are vulnerable to generated-copy mistakes. The communication registers repeat four byte fields at shifts `0x0`, `0x8`, `0x10`, and `0x18`; status/mask/XIRQ families repeat the same event ordering across several registers. A suffix or bit-position mismatch would compile cleanly and only fail when that event or byte lane is used.

Some fields have paired enable/value semantics. Examples include clock gating enable/state, ABM enable plus timing/level fields, DAC CRC enable plus control and signature masks, autodetect mode plus status/ack/interrupt enable, and connectivity override-enable plus connectivity value. Writing the value field without the enable field, or enabling an override with stale data, can produce misleading behavior.

Firmware and hardware ownership boundaries are important. DMCU scratch/communication, ABM statistic/result, perfmon status, Azalia DMA/status, and DAC FIFO/autodetect fields may be updated asynchronously by hardware or firmware. Callers need appropriate polling, locking, interrupt acknowledgement, and frame/update ordering; this generated header does not provide those rules.

The requested range starts after the first `DMCU_INTERRUPT_TO_UC_EN_MASK` shift definitions have already begun and ends immediately before the next register block after `DAC_FIFO_STATUS`. The merge lane should treat both as chunk-boundary artifacts, not as absent definitions in the full file.

## Test Signals

Useful validation is mostly build-time plus hardware/display behavior:

- AMDGPU display builds that include DCE 12.0 headers should compile without unresolved mask/shift names in DCE 12.0 timing generator, hardware sequencing, resource, IRQ, GPIO, and GMC/display paths.
- Register table initialization should populate DCE 12.0 mask/shift structures with the expected field names for audio, IRQ, timing, link, and memory-input code.
- DMCU firmware loading and mailbox communication should complete without stuck master/slave interrupt or "message in progress" states.
- ABM/backlight testing should show stable brightness transitions, correct minimum/final duty behavior, correct ambient/user/target/current levels, and plausible luma/histogram statistics across static and changing content.
- Static-screen, VBLANK, DPRX, AUX, HPD, GPIO, timer, software, perfmon, and command-complete interrupt tests should show expected status, mask, and routing behavior without missed or spurious events.
- HDMI/DP audio testing should enumerate the expected codec identity/capabilities, program supported formats/rates, keep audio DMA/cyclic-buffer state sane, and preserve audio across modeset, hotplug, suspend/resume, and clock/power-gating transitions.
- Azalia CRC and memory-power tests should produce stable CRC results and avoid underflow, RIRB/CORB, or BDL DMA faults when streams start and stop.
- Analog DAC tests, where hardware supports them, should validate source selection, forced output, CRC signatures, autodetect/load status, comparator outputs, per-channel powerdown, and FIFO calibration/status behavior.

Regression symptoms from incorrect constants include black screens after firmware/display setup, no backlight or unstable brightness, missed DMCU/ABM interrupts, stuck firmware mailboxes, missing HDMI/DP audio devices, audio stream underflows, incorrect codec power state, false DAC connect status, failed analog detection, wrong CRC diagnostics, or FIFO calibration status being read from the wrong bits.

## Cross-Chunk Notes

Earlier lines in `dce_12_0_sh_mask.h` define preceding display-controller fields and the beginning of the first DMCU interrupt mask register. Later lines continue from `DAC_FIFO_STATUS` into the DCE I2C and subsequent display register families. The final per-file report should describe this file as generated AMDGPU DCE 12.0 register metadata rather than algorithmic driver code.

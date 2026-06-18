# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h

Chunk: `subset-b-001573`
Covered source range: lines 8157-11923 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 8.0 register field mask header section. It provides C preprocessor constants for bit masks and shifts used by the AMDGPU display stack to encode and decode hardware registers. It is not executable logic; its contract is the register-field naming scheme consumed by register helper macros and per-generation register tables.

The covered range spans several display, link, legacy VGA, power, and audio areas:

- the tail of DMCU slave mailbox fields, including `SLAVE_COMM_DATA_REG1..3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG`;
- DMCU test/debug and a large DMCU perfmon interrupt matrix covering status/clear bits, interrupt-to-uC enables, uC XIRQ selection, and interrupt-to-host masks for DCI, DCO, DCCG, DCFE0..5, and scan-in perfmon counters;
- DisplayPort link, stream, MSA, DPHY, CRC, fast-training, secondary-data-packet, MST, and AUX/GTC sync fields;
- DVO output control, CRC, and FIFO error status;
- frame buffer compression (`FBC_*`) control, mode, debug, LUT, CSR, error, and status fields;
- formatter (`FMT_*`) clamp, pixel encoding, forced data, bit depth, dithering, CRC, and debug fields;
- line buffer (`LB_*`) data format, memory sizing, vline/vblank interrupts, keyer colors, buffer urgency/status, and sync-reset fields;
- multi-video plane (`MVP_*`) control, FIFO, AFR flip, CRC, debug, receive counter, and async FIFO fields;
- scaler (`SCL_*`) coefficient RAM, filter ratios/init, update, viewport, overscan, mode-change detection, and debug fields;
- legacy VGA sequencer, CRTC, graphics, attribute, palette/DAC, render/source/memory/cache/HDP, per-display `D1VGA_CONTROL` through `D6VGA_CONTROL`, and VGA interrupt/status controls;
- analog DAC PHY calibration and white-level controls;
- display pipe generator (`DPG_*`) arbitration, watermark, urgency, DPM, stutter, NB p-state, repeater, and debug fields;
- Azalia/HDA HDMI/DP audio root/function/pin/converter/controller fields, CORB/RIRB DMA rings, immediate command/status, stream descriptors, DMA position buffers, audio descriptors, and early multichannel pin control.

The range starts mid-register: `SLAVE_COMM_DATA_REG1__SLAVE_COMM_DATA_REG1_BYTE0_*` is just before line 8157. It also ends mid-register: line 11923 defines `AZALIA_F2_CODEC_PIN_CONTROL_MULTICHANNEL01_ENABLE__MULTICHANNEL01_CHANNEL_ID_MASK`, while the matching `__SHIFT` and later multichannel/lipsync/HBR fields are in the next chunk. The merge lane should reconcile these boundary splits when producing the final per-file document.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this source range. The public interface is the macro naming contract:

- `<REGISTER>__<FIELD>_MASK` gives the 32-bit bit mask for a register field.
- `<REGISTER>__<FIELD>__SHIFT` gives the shift needed to pack or unpack the field.
- The companion address header `dce_8_0_d.h` provides matching `mm<REGISTER>` and indexed `ix<REGISTER>` address constants.
- Consumers combine these macros through AMDGPU helpers such as `REG_SET_FIELD`, `set_reg_field_value`, `REG_GET`, `REG_UPDATE`, `REG_UPDATE_N`, `RREG32`, `WREG32`, and DC table constructors such as `DMCU_SF`.

Important macro families in this chunk include:

- `SLAVE_COMM_*`: byte lanes for DMCU slave data/command registers plus `SLAVE_COMM_INTERRUPT` and `COMM_PORT_MSG_TO_HOST_IN_PROGRESS`. These represent firmware-to-host mailbox state.
- `DMCU_PERFMON_INTERRUPT_STATUS1..4`: per-counter interrupt occurred/clear bits. Status groups cover DCI/DCO/DCCG, DCFE0..5, and scan-in counters, with counter-off interrupt bits packed at high positions.
- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..4`, `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..4`, and `DMCU_PERFMON_INTERRUPT_TO_HOST_EN_MASK1..4`: routing and masking controls that decide whether perfmon events signal the microcontroller, which uC interrupt line is used, and whether the host sees those interrupts.
- `DP_*`: link training complete/status, embedded panel mode, pixel encoding/dynamic range/component depth, MSA colorimetry and timing, stream enable/disable/status, steering FIFO overflow/TU overflow, DPHY training/symbol/8b10b/PRBS/scrambler/CRC/fast-training, secondary packet audio M/N/N-readback/timestamp/framing, MST allocation timing/rate/slot update, and test debug.
- `AUX_*`: AUX software transaction fields, arbitration request/done state, interrupt/status bits, line-status error capture, low-speed data FIFOs, DPHY TX/RX timing/status controls, GTC sync control/error/status/data, and phase-offset override.
- `DVO_*`: DVO enable, source/stereo sync selection, output mode, clocking, data width, FIFO reset, polarity, color format, CRC, and FIFO calibration/error status.
- `FBC_*`: frame buffer compression enable/source/coherency, idle masks, start/stop delay, compression methods and depth enables, indirect LUT entries, CSM region offsets, client region mask, CSR debug access, decompress error handling, reset behavior, slow request interval, and enable status.
- `FMT_*`: clamp limits, dynamic expansion, source and pixel encoding, forced output data, truncation/spatial/temporal dithering, random seeds, programmable dithering matrices, clamp color format, CRC control/result/masks, and debug registers.
- `LB_*`: line buffer pixel data format, memory configuration/status, desktop height, vline windows/counters/status, interrupt masks, keyer colors, buffer urgency and levels, buffer status, sync reset, and debug.
- `MVP_*`: multi-video-plane sync/AFR/FIFO/control path fields, black keyer, slave status, CRC, receive error counters, swap-lock/flow-control debug, and async FIFO debug data.
- `SCL_*`, `VIEWPORT_*`, and `EXT_OVERSCAN_*`: scaler coefficient RAM selection/data/conflict status, tap/filter/ratio/init controls, update lock/pending/complete bits, sharpening, viewport start/size, overscan extents, mode-change detection/masks, and debug.
- Legacy VGA groups `GEN*`, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, `DAC_*`, `VGA_*`, and `D1VGA_CONTROL..D6VGA_CONTROL`: VGA register emulation/control fields for boot console, legacy modes, palette, memory aperture, page addressing, render timing, source selection, per-CRTC VGA routing, interrupts, status, and test/debug.
- `BPHYC_DAC_*`: DAC macro white-level, fine-control, bandgap, analog monitor, core monitor, calibration enable/wait/mask, and calibration completion fields.
- `DPG_*`: pipe arbitration weights, urgency and stutter watermarks, DPM/MCLK change controls, NB p-state change controls, non-latched stutter controls, repeater programming, and debug.
- `AZALIA_*`, `GLOBAL_*`, `CORB_*`, `RIRB_*`, `IMMEDIATE_*`, `OUTPUT_STREAM_DESCRIPTOR_*`, and `AUDIO_DESCRIPTOR*`: HDA controller and codec fields for audio capabilities, power/reset/subsystem ID, channel counts, clock/GTC offsets, command/response rings, immediate verb interface, DMA position, stream format/control/status, converter stream/format/digital controls, pin widget capabilities, pin sense/configuration/speaker allocation/channel allocation/downmix, and per-format ELD-style audio descriptors.

## Control Flow

This header chunk has no local control flow. Runtime control flow is introduced when driver code uses the constants to build register values or register tables:

1. A DCE 8 consumer includes `dce_8_0_d.h` for register addresses and this file for masks/shifts.
2. The driver reads a 32-bit MMIO or indexed register, clears a field using `_MASK`, inserts a value shifted by `__SHIFT`, and writes the result back.
3. For status and interrupt fields, the driver often polls until a field reaches an expected value, writes acknowledge/clear bits, or routes interrupts to host/uC handlers.
4. For indexed spaces such as Azalia codec endpoint registers, the driver writes an index register and then reads/writes the paired data register while holding the relevant lock.

Concrete integration examples in this tree:

- `amdgpu/dce_v8_0.c` includes this header and uses `VGA_HDP_CONTROL__VGA_MEMORY_DISABLE_*`, `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_*`, and `FMT_BIT_DEPTH_CONTROL__*` fields to control VGA memory visibility, VGA status source, truncation, and dithering.
- `amdgpu/dce_v8_0.c` also accesses Azalia endpoint registers through `mmAZALIA_F0_CODEC_ENDPOINT_INDEX` and `mmAZALIA_F0_CODEC_ENDPOINT_DATA`; the codec/control/audio descriptor field patterns in this chunk match the same HDA-style indexed register model.
- `display/dc/dce/dce_dmcu.h` defines DMCU register lists and mask/shift table constructors. It references `MASTER_COMM_*` and `SLAVE_COMM_CNTL_REG__SLAVE_COMM_INTERRUPT_*` patterns used by the DMCU mailbox path.
- `display/dc/dce/dce_dmcu.c` waits on `MASTER_COMM_CNTL_REG.MASTER_COMM_INTERRUPT`, writes `MASTER_COMM_DATA_REG1..3`, sets `MASTER_COMM_CMD_REG_BYTE0`, and raises `MASTER_COMM_INTERRUPT` to notify firmware. The slave-side fields in this chunk represent the reverse direction and host-visible firmware messages.
- DCE/DC link encoder and AUX implementations in later generations use the same field model for `DP_LINK_*`, `DP_AUX0_AUX_*`, `AUX_DPHY_*`, and `AUX_GTC_SYNC_*` controls; DCE 8 consumers use the uninstanced DCE 8 names plus per-block address offsets.

No function in this header sequences operations. Ordering constraints such as waiting for DMCU readiness, locking Azalia endpoint access, acknowledging interrupts, programming scaler coefficients before update, or enabling DP streams after link training are owned by the call sites and hardware specifications.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, perform I/O, mutate data, or persist anything beyond compiled constants.

The hardware fields represented here are persistent GPU register state until changed by driver writes, firmware writes, display block reset, ASIC reset, hotplug/link events, power-gating transitions, suspend/resume, or mode set reprogramming. Important state categories include:

- DMCU mailbox state: slave data/command bytes, slave interrupt latch, and message-in-progress status. These fields coordinate host/firmware command exchange and can be shared with microcontroller firmware.
- Perfmon interrupt state: occurred/clear latches, host/uC masks, and uC XIRQ routing. Some clear fields likely have write-one-to-clear or acknowledge semantics even though access type is not represented in the macro name.
- DP/AUX link state: link training completion, stream enable/status, M/N timing generation, DPHY training/test/CRC/scrambler state, MST slot allocation, secondary-packet framing, AUX software transaction buffers, arbitration ownership, error latches, and GTC sync lock/error state.
- DVO/FBC/FMT/LB/MVP/SCL pipeline state: compression enable/mode/LUTs, formatter color and dithering behavior, CRC capture, line-buffer allocation and interrupt windows, scaler coefficient RAM and update lock state, viewport/overscan geometry, multi-video-plane synchronization, and DVO FIFO/polarity/CRC state.
- VGA state: legacy sequencer/CRTC/graphics/attribute/palette registers, DAC index/data state, VGA memory aperture/base/page mappings, cache/HDP controls, per-display VGA routing, render controls, interrupt enables/status, and test/debug state.
- Power and memory timing state: DPG urgency/stutter/p-state watermarks, MCLK/NB p-state controls, and BPHYC DAC calibration state.
- Azalia/HDA state: controller capabilities/control/status, command/response ring addresses and pointers, immediate command status, stream descriptor run/reset/format/BDL state, codec power/reset, pin/converter capabilities, pin sense/configuration, audio descriptors, channel/speaker/downmix setup, and presentation-time/GTC embedding state.

Because this header only defines raw fields, it does not document which bits are read-only, write-only, write-one-to-clear, sticky, indexed, latched, double-buffered, or hardware-owned. Consumers must preserve reserved bits and follow the access pattern for each register block.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. Practical dependencies are the DCE 8 address and enum/register helper ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_d.h` for matching `mm*` and `ix*` register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c`, the legacy DCE 8 display implementation that includes this header and programs VGA, formatter, Azalia audio, interrupt, CRTC, pageflip, and mode-set state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.c`, which show the mailbox register-table and mask/shift table integration pattern for DMCU communication.
- DCE 8 display/DC files that include `dce_8_0_sh_mask.h`, including DCE 8 timing generator, IRQ service, hardware sequencer, GPIO factory/translation, and power-management paths.
- Generic AMD register helper macros in the display and amdgpu layers, which assume the exact `_MASK` and `__SHIFT` spelling generated here.

The field names also align with newer DCE/DCN headers. That cross-generation consistency is useful for shared code patterns but creates a migration hazard: the same field name may have generation-specific addresses, prefixes, masks, or access behavior.

## Risks And Edge Cases

The largest risk is silent hardware misprogramming. These macros are untyped numeric constants; the compiler cannot prove that a field belongs to the register being written, that a value fits inside the mask, that a mask is paired with the correct shift, or that a read/modify/write is legal for the register's access type.

Boundary splits are real in this chunk. The first `SLAVE_COMM_DATA_REG1` field is incomplete because `BYTE0` appears before line 8157, and `AZALIA_F2_CODEC_PIN_CONTROL_MULTICHANNEL01_ENABLE` is incomplete because the `MULTICHANNEL01_CHANNEL_ID__SHIFT` appears after line 11923. Chunk-level validation should not treat these as missing data; final file-level reconciliation should verify full pairs across adjacent chunks.

Repeated block layouts are easy to confuse. Perfmon groups repeat across `STATUS1..4`, uC enable/mask/XIRQ groups, host mask groups, DCFE instances, and counter-off bits. VGA has repeated display instance controls `D1VGA_CONTROL..D6VGA_CONTROL`. Audio descriptors repeat from `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`. Copying the wrong prefix can build cleanly while programming a different counter, display pipe, audio descriptor, or interrupt route.

Several fields have status/ack/control pairs packed into the same register family. Examples include DP steering FIFO overflow/TU overflow, AUX/GTC sync errors, FBC decompression error clear, scaler coefficient conflict ack, VGA interrupt clear/status, DVO FIFO error ack, CORB/RIRB status, and stream descriptor error/status bits. Incorrect write values can clear diagnostic evidence, leave stale latches set, or cause interrupt storms.

High-bit masks such as `0x80000000` appear in many places, including AUX, DVO, FBC, LB, MVP, FMT, VGA, and Azalia pin-sense fields. Consumers should use fixed-width unsigned values and existing helper macros instead of signed arithmetic.

Hardware timing and ordering risks are significant:

- DMCU mailbox fields require readiness waits and firmware ownership discipline.
- DP link, stream, DPHY, secondary-packet, and MST fields must be programmed in link-training and stream-enable order.
- AUX software transaction, arbitration, line-status, and GTC sync fields are protocol-sensitive and can break DPCD/EDID reads, MST traffic, or CP IRQ handling if acknowledged or reset at the wrong time.
- SCL coefficient RAM fields require careful index/phase/filter selection and update synchronization; conflict status must be handled before assuming coefficients were loaded.
- FBC and DPG stutter/p-state controls interact with memory bandwidth, self-refresh, and display underflow behavior.
- Azalia CORB/RIRB, stream descriptors, and codec pin/converter controls interact with DMA, audio clocking, ELD programming, and HDMI/DP audio enumeration.

Generated-header drift is another risk. If `dce_8_0_sh_mask.h` and `dce_8_0_d.h` are regenerated from different register databases, a correct-looking mask can be paired with a stale address or indexed register. This is hard to detect at compile time and often only appears as hardware-specific display, audio, or power-management failures.

## Test Signals

Useful validation signals include:

- compile coverage for DCE 8 paths that include `dce_8_0_sh_mask.h`, especially `amdgpu/dce_v8_0.c`, DCE 8 timing generator, DCE 8 IRQ service, DCE 8 hardware sequencer, GPIO factory/translation, and CI/CIK power-management code;
- generated-header consistency checks across the complete file, ensuring each `_MASK` has a matching `__SHIFT`, while allowing the known chunk-boundary splits in this range;
- consistency checks between `dce_8_0_sh_mask.h` and `dce_8_0_d.h`, confirming that every used register field has a matching `mm*` or `ix*` address and that indexed Azalia fields are not confused with MMIO registers;
- build or static-analysis checks for `REG_SET_FIELD`, `REG_GET`, `REG_UPDATE`, and direct shift/mask uses that pass values wider than the target field;
- display mode-set tests covering DP link training, stream enable/disable, MSA timing, pixel encoding/range/depth, secondary data packets, MST slot allocation, and DPHY CRC/test modes where supported;
- AUX transaction tests covering EDID/DPCD reads, timeouts, NACK/defer/error paths, HPD disconnect during AUX, MST sideband traffic, CP IRQ propagation, and GTC sync lock/lost/error paths;
- VGA compatibility tests for boot console handoff, VGA memory aperture enable/disable, palette/DAC access, per-CRTC VGA routing disable, VGA interrupt/status behavior, and suspend/resume restoration;
- FBC and DPG power tests covering compression enable/disable, decompression error clearing, idle masks, stutter/self-refresh, MCLK/NB p-state changes, watermarks, and underflow-free operation under bandwidth stress;
- formatter/scaler/line-buffer tests covering truncation/dithering, CRC readback, viewport/overscan programming, scaler coefficient upload/update, vline/vblank interrupts, and line-buffer urgency/status;
- HDMI/DP audio tests covering Azalia endpoint indexed access, codec power/reset, ELD-derived audio descriptor programming, channel/speaker allocation, stream descriptor DMA setup, CORB/RIRB or immediate command paths, pin sense/configuration, HBR/compressed channel settings, and audio across hotplug and suspend/resume;
- hardware readback tests after safe representative writes, verifying that shifted values land only inside intended masks and that adjacent fields are preserved.

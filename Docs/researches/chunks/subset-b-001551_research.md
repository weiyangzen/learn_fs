# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h

Chunk: `subset-b-001551`
Covered source range: lines 34821-37188 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 12.0 register field mask header section. It contains C preprocessor constants for bit positions and masks in display controller registers; it is not executable driver logic.

The covered range spans several display hardware areas:

- the tail of `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL`, then `CRTCV1` external timing sync, static-screen, 3D-structure, and genlock/swaplock control fields;
- `HPD0` through `HPD5` hot-plug detect interrupt/status/control, fast-train, and toggle-filter fields;
- `DC_PERFMON2` performance counter and monitor control/status/value fields;
- `DP_AUX0` through `DP_AUX5` DisplayPort AUX controller fields, including software transaction control, arbitration, interrupts, line-status data, DPHY TX/RX tuning/status, and GTC sync status;
- the beginning of the `DIG0` stream encoder front-end fields: `DIG_FE_CNTL`, `DIG_OUTPUT_CRC_CNTL`, and the first `DIG_OUTPUT_CRC_RESULT` shift macro.

The chunk starts mid-register: the comment and most field definitions for `CRTCV1_CRTCV_EXT_TIMING_SYNC_LOSS_INTERRUPT_CONTROL` begin before line 34821. It also ends mid-register: `DIG0_DIG_OUTPUT_CRC_RESULT__DIG_OUTPUT_CRC_RESULT__SHIFT` appears at line 37188, while its matching mask and later DIG0 registers are in the next chunk. The final file-level report should reconcile these boundary splits.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The public interface is the macro naming contract used throughout AMDGPU display code:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift used to encode or decode a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register address macros live in the companion `dce_12_0_offset.h` header as `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX`.

Important macro families in this chunk include:

- `CRTCV1_CRTCV_EXT_TIMING_SYNC_*`: interrupt enable/status/clear/type fields for external timing sync loss, sync, and sync-signal events.
- `CRTCV1_CRTCV_STATIC_SCREEN_CONTROL`: static screen event mask, frame count, status, CPU interrupt enable/status/clear/type fields.
- `CRTCV1_CRTCV_3D_STRUCTURE_CONTROL`: stereo/3D enable, double-buffer enable, vertical update mode, stereo override, frame-count reset/status, and frame count.
- `CRTCV1_CRTCV_GSL_*`: genlock/swaplock vsync gap limits, source selection, mode, clear/status, window start/end, check line, forced delay, and all-fields check.
- `HPD0..HPD5_DC_HPD_*`: hot-plug interrupt status, HPD sense and delayed sense, HPD RX interrupt status, interrupt acknowledge/polarity/enable, RX interrupt acknowledge/enable, connection/RX timers, HPD enable, fast-train delays/enables, and connect/disconnect debounce filter delays.
- `DC_PERFMON2_*`: event selection, counted value selection/type, increment/run/stop modes, interrupt enables/status/clear, counter state machine fields, 64-bit counter high/low values, and current-value interrupt comparison controls.
- `DP_AUX0..DP_AUX5_AUX_*`: AUX enable/reset/reset-done, HPD selection, mode detection, software transaction start/write-byte/index/data fields, arbitration request/done state, software done/timeout/error statuses, line-status protocol errors, DPHY timing controls, DPHY TX/RX status, and GTC sync error/status fields.
- `DIG0_DIG_FE_CNTL`: source select, stereo sync select/gate, digital start, symbol-clock state, TMDS pixel encoding, and TMDS color format.
- `DIG0_DIG_OUTPUT_CRC_CNTL`: output CRC enable, link select, and data select.

## Control Flow

This header chunk has no internal control flow. The preprocessor exposes constants that compile into display driver register tables and read/modify/write operations.

Runtime control flow appears in consumers:

1. DCE 12 code includes `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`.
2. Macro tables combine `mm*` addresses, `*_BASE_IDX` values, and this chunk's `_MASK`/`__SHIFT` constants.
3. Register helper code reads a 32-bit register, clears fields with `_MASK`, shifts values by `__SHIFT`, writes the result, and sometimes polls status bits.

Concrete integration examples in the tree:

- `display/dc/irq/dce120/irq_service_dce120.c` builds HPD and HPD RX interrupt source entries from `HPD0..5_DC_HPD_INT_CONTROL` enable/ack masks and `HPD0..5_DC_HPD_INT_STATUS` status registers.
- `display/dc/dce/dce_aux.h` defines `DCE12_AUX_MASK_SH_LIST`, which maps `DP_AUX0_AUX_CONTROL`, `DP_AUX0_AUX_ARB_CONTROL`, `DP_AUX0_AUX_SW_CONTROL`, `DP_AUX0_AUX_SW_DATA`, `DP_AUX0_AUX_SW_STATUS`, and `DP_AUX0_AUX_INTERRUPT_CONTROL` fields into the AUX engine's register-field tables.
- `display/dc/dce120/dce120_timing_generator.c` programs static-screen control through register helper macros, clamping the frame count to 8 bits before writing the static-screen frame-count field.
- `display/dc/dce/dce_stream_encoder.h` includes `DIG0_DIG_FE_CNTL` fields in stream encoder field maps used to start the DIG front end, select the source, and configure TMDS/stereo behavior.
- `display/dc/resource/dce120/dce120_resource.c` includes this header while constructing DCE 12 resource objects for timing generators, stream encoders, link encoders, AUX, I2C, IRQ, clocks, and related display blocks.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, perform I/O, or persist data. Its only persistence is as compiled constants in driver objects.

The hardware fields represented here are persistent GPU register state until changed by driver writes, firmware, a display block reset, ASIC reset, hot-plug activity, suspend/resume, or link retraining. Important state categories include:

- HPD line state, delayed sense state, HPD/RX interrupt latches, interrupt polarity, and debounce timers;
- AUX controller enable/reset state, software transaction buffers, arbitration ownership, timeout/error bits, reply byte counts, line-status capture, DPHY tuning, and GTC sync error latches;
- timing-generator static-screen detection state, external sync interrupt state, 3D frame count/reset state, and genlock/swaplock window/gap state;
- DC perfmon counter configuration, active state, interrupt state, comparison values, and high/low counter values;
- DIG front-end start/source/TMDS/stereo configuration and output CRC enable/result state.

Many status and interrupt bits use write-one-to-clear or acknowledge-style fields in nearby control registers. These macros do not encode access type, ordering, locking, or ownership; consumers must follow the register specification and existing register helper conventions.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. The practical dependency is the companion DCE 12.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`

The offset header defines matching register addresses, including `mmCRTCV1_CRTCV_GSL_CONTROL`, `mmHPD0_DC_HPD_INT_STATUS` through `mmHPD5_DC_HPD_TOGGLE_FILT_CNTL`, `mmDC_PERFMON2_*`, `mmDP_AUX0_AUX_CONTROL` through `mmDP_AUX5_AUX_GTC_SYNC_STATUS`, and `mmDIG0_DIG_FE_CNTL` through `mmDIG0_DIG_OUTPUT_CRC_RESULT`.

Known local DCE 12 consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The chunk also shares field names and patterns with generic DCE/DC helper headers such as `display/dc/dce/dce_aux.h` and `display/dc/dce/dce_stream_encoder.h`, where `AUX_SF` and `SE_SF` macros construct per-generation mask/shift tables.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are untyped preprocessor values, so the compiler cannot verify that a mask is paired with the intended register address, that a field value fits before shifting, or that a status/ack/control field is used with the correct access semantics.

Boundary split risks matter for this chunk. The first register family is incomplete at the start, and `DIG0_DIG_OUTPUT_CRC_RESULT` is incomplete at the end. Chunk-local checks for complete mask/shift pairs must allow these boundaries; file-level reconciliation should verify that the pairs exist across adjacent chunks.

Repeated instance blocks are easy to mix up. `HPD0..5` and `DP_AUX0..5` have nearly identical field layouts with different register addresses. Copying the wrong instance prefix can compile cleanly while acknowledging the wrong HPD interrupt, selecting the wrong AUX engine, or reading stale status from another physical connector path.

Several field groups are timing-sensitive or protocol-sensitive:

- HPD polarity, enable, acknowledge, debounce, and fast-train fields affect connector detection and IRQ storms/loss.
- AUX software transaction, arbitration, timeout, and data-index fields affect DPCD/EDID reads, DP link training, and MST/sideband reliability.
- AUX DPHY fields affect electrical receive/transmit windows and can cause intermittent AUX failures if copied across ASIC generations without validation.
- CRTC external sync and GSL fields affect genlock/swaplock timing and can cause multi-display synchronization faults.
- DIG front-end source/start/TMDS fields affect visible display output, HDMI/DVI encoding, and CRC/debug capture.

High-bit masks such as `0x80000000L` depend on unsigned 32-bit treatment in consumers. Callers should use the existing register helper macros and fixed-width `uint32_t` values instead of ad hoc signed arithmetic.

Generated headers can drift from register specs or offset headers. A stale mask with a correct address, or a correct mask with a stale shift, usually still builds and may only fail on hardware.

## Test Signals

Useful validation signals include:

- compile coverage for DCE 12 translation units that include `dce_12_0_sh_mask.h`, especially `irq_service_dce120.c`, `dce120_timing_generator.c`, `dce120_hwseq.c`, `dce120_resource.c`, GPIO factory/translation files, and `gmc_v9_0.c`;
- generated-header consistency checks across the complete file, ensuring each `_MASK` has a matching `__SHIFT` and each field macro has a matching `mm*` address in `dce_12_0_offset.h`;
- duplicate-definition checks to ensure repeated HPD/AUX instance macros are identical where intended and uniquely prefixed by instance;
- hot-plug tests across all supported connectors, checking HPD connect, disconnect, delayed sense, RX IRQ, debounce behavior, interrupt ack/reenable, suspend/resume, and rapid cable-toggle cases;
- DisplayPort AUX transaction tests, including EDID/DPCD reads, link training, AUX timeout/error handling, HPD disconnect during AUX, MST sideband traffic, and CP IRQ handling;
- timing-generator tests for static-screen detection, vblank/vactive waits, external sync loss/sync/signal interrupts, 3D stereo modes, and genlock/swaplock operation where hardware supports it;
- DC perfmon tests that program event selection, start/stop counters, read low/high values, and verify interrupt/compare behavior without corrupting adjacent counter controls;
- stream encoder tests for DIG source selection, DIG start/stop, TMDS pixel encoding/color format, stereo sync gating, and output CRC enable/result readback;
- hardware readback tests after representative safe writes, using the register helper APIs to confirm that shifted values occupy only the intended masked bits.

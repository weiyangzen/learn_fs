# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 14787-17309

## Purpose

This chunk is part of AMD DCN 3.0.0's generated ASIC register shift/mask header. It does not implement executable logic; it defines bit positions (`__SHIFT`) and bit masks (`_MASK`) for display pipe processor (DPP) registers used by the AMDGPU display driver. The line range covers the tail of DPP0 converter configuration, DPP0 cursor/scaler/color/performance-monitor blocks, and the beginning of DPP1 top/converter/cursor/scaler blocks.

The macros provide the hardware layout contract consumed by DCN display code. Runtime code builds `dcn3_dpp_shift` and `dcn3_dpp_mask` tables from these definitions, then uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related helper macros to encode/decode hardware register fields safely.

## Address Blocks Covered

- `dce_dc_dpp0_dispdec_cnvc_cfg_dispdec` tail: floating-point converter bias/scale, color keyer, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp0_dispdec_cnvc_cur_dispdec`: cursor enable/mode/color/FP scale-bias fields for DPP0.
- `dce_dc_dpp0_dispdec_dscl_dispdec`: DPP0 display scaler fields for coefficient RAM, tap control, scale ratios, initial phases, overscan, blanking, recout/MPC sizes, line buffer format/memory, memory power control/status, and output buffer power control.
- `dce_dc_dpp0_dispdec_cm_dispdec`: DPP0 color-management fields for CM control, post-CSC, gamut remap, gamma correction RAM A/B, blend gamma RAM A/B, HDR multiplier, dealpha, coefficient format, shaper LUT RAM A/B, memory power state, 3D LUT, and test debug access.
- `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: performance counter and performance monitor fields for `DC_PERFMON12`.
- `dce_dc_dpp1_dispdec_dpp_top_dispdec`: DPP1 top control, soft reset, CRC readout/control, and host-read throttle fields.
- `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec` and `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`: DPP1 equivalents of the converter and cursor fields.
- `dce_dc_dpp1_dispdec_dscl_dispdec` beginning: DPP1 scaler fields through `DSCL1_LB_MEMORY_CTRL`.

## Important APIs, Types, and Macros

- Field macros follow `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming. For example, `DSCL0_SCL_MODE__DSCL_MODE__SHIFT` and `DSCL0_SCL_MODE__DSCL_MODE_MASK` define where the scaler mode field lives in `DSCL0_SCL_MODE`.
- DPP register lists in `display/dc/dpp/dcn30/dcn30_dpp.h` use `SRI(...)` entries such as `SRI(SCL_MODE, DSCL, id)` and `SRI(FORMAT_CONTROL, CNVC_CFG, id)` to bind per-instance register addresses.
- The same header's `DPP_REG_LIST_SH_MASK_DCN30*` macros use field selectors such as `TF_SF(DSCL0_SCL_MODE, DSCL_MODE, mask_sh)` to populate `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask`.
- `display/dc/resource/dcn30/dcn30_resource.c` instantiates `dpp_regs[]`, `tf_shift`, and `tf_mask` from these macro lists, making the generated masks available to live DPP objects.
- DPP implementation code in `display/dc/dpp/dcn30/dcn30_dpp.c` and `dcn30_dpp_cm.c` consumes these tables through register helper macros, not by spelling numeric masks directly.

## Functional Areas

- CNVC pixel conversion: `CNVC_CFG{0,1}_CNVC_SURFACE_PIXEL_FORMAT`, `FORMAT_CONTROL`, FP bias/scale, color keying, alpha LUT, pre-dealpha/realpha, pre-CSC matrix banks A/B, pre-degamma ROM select, and coefficient format. These fields control input format expansion, alpha handling, channel crossbar mapping, clamping, and pre-scaler color transforms.
- Cursor conversion: `CNVC_CUR{0,1}_CURSOR0_*` fields control cursor enable, expansion/inversion/ROM mode, cursor pixel format mode, update-pending status, packed RGB colors, and FP scale/bias.
- DSCL scaler: `DSCL{0,1}_SCL_*`, `DSCL_CONTROL`, `DSCL_AUTOCAL`, `RECOUT_*`, `MPC_SIZE`, `LB_*`, and memory-power fields define filter coefficient RAM access, horizontal/vertical/chroma ratios, phase initialization, tap counts, overscan/blanking geometry, line-buffer allocation, and scaler memory power state.
- CM color management: `CM0_CM_*` fields define CM bypass, post-CSC and gamut-remap double-buffered matrix banks, gamma correction LUTs, blend gamma LUTs, shaper LUTs, HDR multiplier, dealpha, memory power, 3D LUT indexing/data, output normalization/offset, and debug register access.
- DPP top/CRC/perfmon: `DPP_TOP1_*` fields provide DPP enable/reset, CRC value/control selection, and host-read rate control. `DC_PERFMON12_*` fields expose counter selection, counter state, monitor state, interrupt status/ack bits, and low/high counter-value readout.

## Control Flow

There is no direct control flow in this header. Runtime control flow is created by consumers:

- Resource construction includes this header and expands the mask/shift macros into static tables during compilation.
- Plane programming paths call DPP functions such as converter setup, pre-degamma programming, post-CSC programming, scaler setup, gamma/LUT programming, and state-readback helpers.
- Register helpers combine a field value with its shift and mask before writing a 32-bit register, or apply mask/shift extraction after reading one.
- Double-buffered color blocks use current-state fields such as `*_MODE_CURRENT` and `*_SELECT_CURRENT` to choose the inactive bank, program RAM A or RAM B, then switch mode/select fields so hardware applies changes on the intended boundary.
- Memory-power flows use control/status fields such as `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `DSCL_MEM_PWR_CTRL`, and `DSCL_MEM_PWR_STATUS`; consumers may wait for status fields before accessing LUT or line-buffer RAM.

## State and Persistence

The macros themselves are compile-time constants and have no persistence. The persistent state is in display hardware registers and SRAM/LUT memories:

- CNVC and DSCL configuration persists in DPP instance registers until reprogrammed, reset, or power-gated.
- CM LUT state persists in gamma/blend/shaper/3D LUT RAMs; the A/B RAM convention allows preparing one bank while the other is live.
- Update-pending/current fields expose whether hardware has latched or is still waiting to latch programmed state.
- Perfmon counter value/status fields represent live hardware counter state and interrupt status. Acknowledge fields are write-sensitive and must be treated as side-effecting hardware bits.
- Memory power control fields can invalidate assumptions about LUT/LB availability if clients write data while the corresponding memory is off or forced into low power.

## Dependencies and Integration Points

- Paired offset definitions in `dcn_3_0_0_offset.h` provide register addresses; this file provides per-field positions and masks.
- `display/dc/dpp/dcn30/dcn30_dpp.h` maps these register fields into the DPP abstraction used by the display core.
- `display/dc/resource/dcn30/dcn30_resource.c` constructs per-pipe DPP register objects for instances 0 through 5 and initializes the shared shift/mask tables from this header.
- `display/dc/dpp/dcn30/dcn30_dpp.c` uses CNVC, DSCL, and DPP top fields for state readback, converter setup, pre-degamma, scaler geometry, and power-state handling.
- `display/dc/dpp/dcn30/dcn30_dpp_cm.c` uses CM fields for gamma correction, post-CSC, gamut remap, blend gamma, shaper LUT, 3D LUT, CM bypass, and CM memory-power sequencing.
- The broader AMDGPU display stack includes this header from DCN30 resource, IRQ, clock, GPIO, and DMUB-related code, but the fields in this chunk primarily integrate through DPP construction and programming.

## Risks and Edge Cases

- Register layout drift is the main risk. A wrong mask or shift silently writes the wrong bit field and can corrupt unrelated hardware control bits.
- Instance duplication increases maintenance risk: DPP0 fields are referenced by generic DPP mask lists and then reused for all instances, while the file also contains explicit DPP1 definitions. Any mismatch between corresponding `0` and `1` fields is suspicious unless documented by hardware.
- Packed two-field and four-field registers require exact masks. CSC matrix registers, region registers, blanking registers, recout size/start, and line-buffer partition registers pack independent values into one 32-bit word.
- Current/pending fields such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `CNVC_UPDATE_PENDING`, `CUR0_UPDATE_PENDING`, and `SCL_UPDATE_PENDING` are readback/status-sensitive; treating them as ordinary writable configuration can break frame-boundary synchronization.
- LUT programming depends on RAM select, host select, write color mask, index auto-increment, and memory power state. Incorrect masks here can produce color corruption that only appears under HDR, color-management, or multi-plane blending workloads.
- Perfmon interrupt status and ack masks are side-effecting. Mixing status and ack bits, or writing a full register without masking, can drop events or leave interrupts asserted.
- Many masks are hardware-width limited, such as 13/14-bit geometry fields and 27-bit scale ratios. Callers must still validate values before encoding; masks truncate but do not make invalid modes safe.

## Test Signals

- Build coverage: compile AMDGPU DCN30 code with this header included; struct initializers for `dcn3_dpp_shift` and `dcn3_dpp_mask` catch missing or renamed fields.
- Display bring-up: enabling a DCN30 GPU display exercises DPP top enable/reset, CNVC format setup, DSCL geometry, and CM bypass/default programming.
- Plane format tests: RGB/YUV, alpha plane, cursor, color key, and FP16/HDR-like paths exercise CNVC format, alpha, crossbar, FP bias/scale, and cursor fields.
- Scaling tests: non-native modes, underscan/overscan, chroma scaling, and multi-plane composition exercise DSCL ratios, taps, coefficient RAM, line-buffer allocation, recout/MPC sizing, and update-pending behavior.
- Color-management tests: gamma, degamma, CSC, gamut remap, shaper LUT, blend gamma, and 3D LUT validation exercise the large CM0 register region and double-buffered RAM bank selection.
- Power-management tests: display idle/active transitions, low-power memory settings, and IPS-related flows should verify `CM_MEM_PWR_*` and `DSCL_MEM_PWR_*` status waits before LUT or scaler memory access.
- Diagnostics: CRC readback, perfmon counter programming, and debugfs or driver state dumps can reveal incorrect DPP top, CRC, perfmon, recout, scaler, and CM state decoding.

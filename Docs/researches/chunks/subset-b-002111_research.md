# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 53402-53464

## Purpose

This chunk is the tail of the generated DCN 3.5.1 shift/mask header for AMD display hardware. It defines bit positions and bit masks for Azalia/HDA function 0 endpoint registers on endpoints 4, 5, 6, and 7, then closes the header include guard. The covered registers are:

- `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`
- `AZF0ENDPOINT4..7_AZALIA_F0_ENDPOINT_FGCG_REP_DIS`

The `ACP_DATA` fields describe the HDA codec pin Audio Content Protection/Audio Info capability data. Each endpoint exposes the same layout: `ACP_INDEX` in bits 0-5, `SUPPORTS_AI` at bit 6, `ACP_PACKET_ENABLE` at bit 7, `ACP_TYPE` in bits 8-9, and two type-dependent bytes in bits 16-23 and 24-31. The `ENDPOINT_FGCG_REP_DIS` register has a single bit at bit 0 used to disable fine-grain clock-gating reporting for that endpoint.

## Important APIs, Types, And Macros

This file does not define callable APIs or C types. Its exported interface is preprocessor symbols consumed by AMD display register helper macros:

- `*_SHIFT` constants provide the low bit index for a field.
- `*_MASK` constants provide the already-positioned 32-bit field mask.
- The symbols are intended for use through AMD's `set_reg_field_value`, `get_reg_field_value`, `REG_UPDATE`, and related register access macros rather than open-coded shifts.
- The matching address/index definitions live in `dcn_3_5_1_offset.h`. For these endpoints, `ixAZF0ENDPOINT4..7_AZALIA_F0_ENDPOINT_FGCG_REP_DIS` is index `0x0070`; the matching ACP data index is the HDA pin control ACP data node register used by the endpoint indirect access path.

The main integration type is `struct dce_audio` from `display/dc/dce/dce_audio.h`, which owns `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`. Resource files such as `display/dc/resource/dcn351/dcn351_resource.c` allocate per-instance audio register tables for DCN 3.5.1 audio objects, while common DCE audio code uses those tables to access endpoint registers.

## Control Flow

There is no runtime control flow inside this generated header. At build time, including DCN 3.5.1 resource and hardware headers makes these constants available to the display core. Runtime control flow is in the audio path:

1. DC resource construction creates audio objects for available audio endpoints and assigns register, shift, and mask tables.
2. Display mode/connector commits propagate sink audio information into `struct audio_info`.
3. `dce_aud_az_configure()` programs Azalia/HDA pin-control registers through `AZ_REG_READ()` and `AZ_REG_WRITE()`.
4. For ACP data, the common audio implementation reads `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`, updates `SUPPORTS_AI` from `audio_info->flags.info.SUPPORT_AI`, and writes the value back.
5. The endpoint-specific generated symbols allow the same logical operation to target endpoint instances without hard-coding endpoint-specific bit arithmetic.

The `FGCG_REP_DIS` bit is part of the hardware control surface for clock-gating reporting. This chunk only exposes the field encoding; any policy that toggles clock gating lives in DC hardware sequencing/resource code.

## State And Persistence

These macros are compile-time constants and do not hold state. The state they describe is hardware register state:

- `ACP_DATA` persists in the HDA/Azalia endpoint register until reprogrammed or reset by the device/power-management path.
- `SUPPORTS_AI` reflects sink capability programming for audio info packets.
- `ACP_PACKET_ENABLE`, `ACP_TYPE`, and type-dependent bytes are available for packet/capability configuration even though the common code path observed in `dce_audio.c` primarily updates `SUPPORTS_AI`.
- `ENDPOINT_FGCG_REP_DIS` affects endpoint clock-gating reporting behavior until hardware reset or explicit rewrite.

Because these are MMIO or indirect codec endpoint fields, persistence is hardware-lifetime persistence rather than filesystem or kernel-object persistence.

## Dependencies And Integration Points

This chunk depends on generated register naming consistency across:

- `dcn_3_5_1_offset.h` for register indices/offsets.
- DCN 3.5.1 resource files for selecting the right register block for each audio instance.
- `display/dc/dce/dce_audio.c` for common Azalia endpoint configuration.
- `display/dc/dce/dce_audio.h` for the audio register/shift/mask table structures and common audio register-list macros.
- DRM audio component integration in `display/amdgpu_dm/amdgpu_dm.c`, which binds GPU display audio state to the kernel audio component and updates ELD/audio instance notifications.

The endpoint numbering is significant: these macros cover high endpoint instances 4-7, matching GPUs that expose multiple display audio pins. Endpoint table size and resource-pool `audio_count` must stay aligned with the generated register namespace.

## Risks

- Generated mask drift can silently corrupt HDA endpoint programming. For example, an incorrect `SUPPORTS_AI` mask would make sink audio info capability reporting wrong without a compile error.
- Endpoint copy/paste symmetry hides errors. Endpoints 4-7 intentionally share identical field layouts; one endpoint with a mismatched shift or mask would only fail on that audio instance.
- The final `#endif` means this chunk closes the entire generated header. Accidental edits around this range can break every DCN 3.5.1 consumer at compile time.
- These constants are hardware-contract data. Driver tests can catch compilation and some behavioral regressions, but incorrect values may only appear on affected ASICs, connectors, audio sinks, or power-management states.
- Clock-gating reporting fields are power/diagnostic sensitive. Wrong `FGCG_REP_DIS` semantics can interfere with clock-gating debug/telemetry and may mask power-management issues.

## Test Signals

Useful validation signals include:

- Kernel build coverage for AMDGPU DC with DCN 3.5.1 enabled; missing or renamed macros should fail compile in resource/register initialization code.
- Display audio enumeration across endpoints 4-7, especially systems with enough connectors/audio pins to exercise high endpoint instances.
- HDMI/DP audio playback after hotplug and mode set, with ELD visible to the audio component and `audio_inst` updates delivered through `amdgpu_dm_audio_eld_notify()`.
- Sink capability behavior for Audio Info support, since `dce_aud_az_configure()` writes `SUPPORTS_AI` into `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA`.
- Suspend/resume and runtime power-management tests that verify audio returns and clock-gating state does not regress.
- Register-dump comparison against the ASIC register specification for endpoint ACP data and `ENDPOINT_FGCG_REP_DIS` bit placement.

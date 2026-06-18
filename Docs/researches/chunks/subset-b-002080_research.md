# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 53413-53485

## Purpose

This chunk is the tail of the generated DCN 3.5.0 shift/mask header for AMD display/audio hardware registers. It defines bit masks for Azalia/HDA function-0 endpoint pin-control ACP data and a fine-grain clock-gating repeat-disable bit for output endpoints 3 through 7. These are not executable routines; they are compile-time register field descriptors used by AMDGPU display/audio code when constructing or decoding register values.

The covered lines begin in the middle of endpoint 3's `AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` field set and then repeat the complete field layout for endpoints 4, 5, 6, and 7. The final line closes the `_dcn_3_5_0_SH_MASK_HEADER` include guard.

## Important macros and register fields

- `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA__SUPPORTS_AI_MASK` through `...__ACP_TYPE_DEPENDENT_BYTE1_MASK` expose the endpoint 3 ACP data masks at bits 6, 7, 8-9, 16-23, and 24-31. The corresponding shifts for endpoint 3 are immediately before this chunk, at lines 53406-53411.
- `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA__*`, `AZF0ENDPOINT5_...`, `AZF0ENDPOINT6_...`, and `AZF0ENDPOINT7_...` define both shifts and masks for five ACP data fields:
  - `ACP_INDEX`: shift 0, mask `0x0000003f`, a 6-bit ACP payload/index selector.
  - `SUPPORTS_AI`: shift 6, mask `0x00000040`, a one-bit capability flag for audio information support.
  - `ACP_PACKET_ENABLE`: shift 7, mask `0x00000080`, a one-bit enable for ACP packet emission/reporting.
  - `ACP_TYPE`: shift 8, mask `0x00000300`, a 2-bit ACP type selector.
  - `ACP_TYPE_DEPENDENT_BYTE0` and `ACP_TYPE_DEPENDENT_BYTE1`: shifts 16 and 24, masks `0x00ff0000` and `0xff000000`, two 8-bit payload bytes whose interpretation depends on `ACP_TYPE`.
- `AZF0ENDPOINT3_AZALIA_F0_ENDPOINT_FGCG_REP_DIS__ENDPOINT_FGCG_REP_DIS_{SHIFT,MASK}` through endpoint 7 define a single bit at bit 0 for the endpoint fine-grain clock-gating repeat-disable register.

The companion DCN 3.5.0 offset header places each endpoint's `AZALIA_F0_ENDPOINT_FGCG_REP_DIS` indirect register at offset `0x0070` for endpoints 3-7. The same offset header's endpoint blocks around `0x0025`-`0x0028` do not expose an `ixAZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` macro in this tree, although newer/neighboring generated headers such as DCN 4.1.0 do expose the ACP data register at `0x0027`. That makes this chunk mostly a field-definition surface until paired with a valid address macro or indirect access path.

## Control flow and usage model

There is no runtime control flow in this header. Consumers include it through ASIC-specific register packs, combine the `_MASK` and `__SHIFT` constants with register access helpers, and then read/modify/write the underlying MMIO or indexed endpoint registers. Typical generated-register usage in this driver family is:

1. Select the ASIC-specific offset and shift/mask headers during display/audio IP initialization.
2. Use the offset macro to locate an indexed Azalia endpoint register.
3. Use the field mask/shift macro to encode a field value or extract one from a hardware register value.
4. Submit the final value through AMDGPU/DC register access wrappers.

For the `ENDPOINT_FGCG_REP_DIS` bit, the flow is a normal one-bit hardware control: the driver can read the current endpoint clock-gating repeat behavior, set or clear bit 0, and write it back. For `ACP_DATA`, the flow is a packed metadata operation: the endpoint's ACP index, support flag, enable bit, type, and dependent bytes share one 32-bit register value.

## State and persistence behavior

The macros do not hold state. The persistent state is in GPU hardware registers for each endpoint. Values written through these masks can persist for the lifetime of the display/audio hardware context and may be reset by GPU reset, display IP reset, suspend/resume, modeset reinitialization, or audio endpoint reprogramming. Because endpoints 3-7 use identical field layouts, state must be tracked by endpoint selection/addressing, not by field encoding.

`ACP_PACKET_ENABLE`, `ACP_TYPE`, and the type-dependent bytes are especially stateful from the hardware perspective: stale values could leave a pin advertising or sending the wrong ACP metadata. `ENDPOINT_FGCG_REP_DIS` affects clock-gating behavior and can influence power/performance state rather than externally visible packet contents.

## Dependencies and integration points

- Depends on `dcn_3_5_0_offset.h` or another generated offset source to provide the register address/index. In this tree, `ENDPOINT_FGCG_REP_DIS` offsets exist for endpoints 3-7 at `0x0070`.
- Integrates with AMDGPU/DC register helper macros that know how to apply generated `*_MASK` and `*__SHIFT` symbols.
- Sits under `drivers/gpu/drm/amd/include/asic_reg/dcn`, so it is ASIC/IP-version-specific data rather than reusable business logic.
- Aligns with adjacent generated headers (`dcn_3_5_1_sh_mask.h`, `dcn_4_1_0_sh_mask.h`) that repeat the same endpoint ACP field encodings, indicating the layout is stable across nearby DCN versions.
- The endpoint registers are part of the Azalia/HDA display-audio path, tying display connector/audio pin programming to the AMDGPU DRM display stack and, indirectly, Linux HDA/HDMI/DP audio behavior.

## Risks and edge cases

- Generated-header mismatch: this chunk defines `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` masks, but the DCN 3.5.0 offset header search did not find corresponding `ix...ACP_DATA` offsets. Code using these masks needs a verified address source; otherwise the masks are orphaned or require indirect addressing not represented by the expected offset macro.
- Endpoint copy/paste drift: endpoints 3-7 should remain bit-identical. A single shifted mask or endpoint-number typo would silently target the wrong register field.
- Reserved-bit corruption: packed ACP writes must preserve bits outside the declared masks. Blind full-register writes could alter undocumented/reserved hardware state.
- Width truncation: `ACP_INDEX` is only 6 bits, `ACP_TYPE` is 2 bits, and dependent bytes are 8 bits. Callers must clamp or validate before shifting.
- Power-management impact: changing `ENDPOINT_FGCG_REP_DIS` can disable clock-gating repeat behavior and increase power draw or mask timing bugs.
- Hardware-visible audio regressions: incorrect ACP data can affect audio/content-protection/info packet behavior on HDMI/DP endpoints and may appear only with specific sinks.

## Test signals

- Build coverage: compile AMDGPU/DC with DCN 3.5.0 enabled and treat missing register or field macro references as a generated-header integration failure.
- Header consistency checks: compare endpoint 3-7 field masks/shifts against endpoint 0-2 in the same header and against `dcn_3_5_1_sh_mask.h` for unchanged layouts.
- Offset/mask reconciliation: verify every field group used by code has a matching offset macro or documented indirect-access path; specifically check whether `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA` should have an offset at `0x0027` for DCN 3.5.0.
- Runtime register tests on supported hardware: read endpoint `ENDPOINT_FGCG_REP_DIS` before and after display/audio init, suspend/resume, and modeset to confirm bit preservation expectations.
- Audio functional tests: validate HDMI/DP audio enumeration, channel layouts, and sink behavior across endpoints 3-7 when ACP packet programming is exercised.
- Power-management tests: compare idle/display-audio power behavior before and after any code path that writes `ENDPOINT_FGCG_REP_DIS`.

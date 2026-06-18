# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen2.c

## Purpose
Defines second-generation Iris platform data for SM8550, SM8650, SM8750, and QCS8300. It adds AV1 decode support, gen2 HFI property mappings, richer decoder/encoder firmware capability tables, UBWC configuration, subscribe/config property arrays, and VPU3/VPU33/VPU35 generation choices.

## Important APIs, Types, And Data
- `platform_fmts_sm8550_dec` supports H.264, HEVC, VP9, and AV1 decoder input.
- `inst_fw_cap_sm8550_dec` maps gen2 decoder caps such as profiles, levels, AV1 tier/DRAP/film grain/super block, host max counts, stage, pipe, POC, coded frames, bit depth, and RAP start to `HFI_PROP_*` IDs.
- `inst_fw_cap_sm8550_enc` maps encoder profile/level, stage, header mode, SPS/PPS prepend flag, bitrate/peak bitrate, bitrate mode, frame skip, frame RC, GOP, entropy, QP ranges and explicit frame QPs, host max counts, rotation, flips, and intra-refresh controls.
- `platform_inst_cap_sm8550` and `platform_inst_cap_qcs8300` define SoC limits; QCS8300 is reduced to 4096 dimensions and lower firmware cycle coefficients.
- `iris_set_sm8550_preset_registers()` writes the same preset register as gen1.
- Tables cover SM8550 ICC, reset, bandwidth, PM domains, OPP domains, clocks, OPP clocks, UBWC config, TZ CP region, HFI config parameters, HFI subscribed properties, and internal buffer tables.
- Exported descriptors: `sm8550_data`, `sm8650_data`, `sm8750_data`, and `qcs8300_data`.

## Control Flow And Integration Points
`iris_probe.c` selects these descriptors for `"qcom,sm8550-iris"`, `"qcom,sm8650-iris"`, `"qcom,sm8750-iris"`, and `"qcom,qcs8300-iris"`. The descriptors initialize gen2 HFI command/response ops and feed V4L2 format enumeration, control setup, stream-on property programming, HFI subscriptions, internal buffer creation, power scaling, VPU firmware boot, and runtime PM. SM8650 mostly reuses SM8550 tables but swaps VPU ops, buffer sizing, reset tables, controller resets, and firmware. SM8750 swaps VPU35 ops, reset and clock tables, and firmware. QCS8300 reuses SM8550 logic with QCS8300 session caps, two VPP pipes, lower throughput, and a different firmware name.

## State And Persistence Behavior
The platform tables are static and module-lifetime. Per-instance firmware caps are copied from the const platform arrays into each instance, where controls mutate values. Config and subscription arrays are immutable and determine the firmware properties negotiated during stream-on and event handling.

## Dependencies
Depends on gen2 HFI defines, Iris control setters, VPU buffer sizing, common VPU ops, and board-specific headers `iris_platform_qcs8300.h`, `iris_platform_sm8650.h`, and `iris_platform_sm8750.h`.

## Risks
- Gen2 capability arrays are large and couple V4L2 control values, HFI property IDs, setter functions, port flags, and dynamic flags. A wrong setter or flag can expose unsupported dynamic controls or program the wrong port.
- SM8650/SM8750/QCS8300 inherit most SM8550 tables; changes to shared arrays affect multiple SoCs.
- AV1-specific caps and internal buffers must stay consistent with buffer sizing and HFI response parsing.
- `num_vpp_pipe`, `max_core_mbpf`, and `max_core_mbps` are used for admission and sizing, so bad values become stream-on failures or insufficient allocation.

## Test Signals
- Probe and firmware boot for all four compatible strings.
- V4L2 format enumeration includes AV1 decode on gen2 platforms.
- Control enumeration/default validation for dynamic bitrate, QP, rotation/flip, intra-refresh, and AV1 caps.
- Decode stream-on for H.264/HEVC/VP9/AV1 and encoder stream-on for H.264/HEVC on SM8550-family hardware.
- HFI subscription events for no-output/source-change and AV1 compression/complexity properties.

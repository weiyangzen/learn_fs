# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen1.c

## Purpose
Provides first-generation Iris/Venus platform data for SM8250 and SC7280. It binds HFI gen1 command/response operations, VPU2 power/frequency operations, decoder formats, encoder firmware controls, interconnect bandwidth tables, PM domains, clocks, reset names, firmware names, TrustZone carveout data, and internal buffer requirements into `sm8250_data` and `sc7280_data`.

## Important APIs, Types, And Data
- `platform_fmts_sm8250_dec` exposes decoder input formats H.264, HEVC, and VP9.
- `inst_fw_cap_sm8250_dec` supports gen1 decoder `PIPE` and `STAGE` controls.
- `inst_fw_cap_sm8250_enc` defines gen1 encoder controls for stage, H.264/HEVC profile and level, header mode, bitrate, bitrate mode, frame skip, frame RC, GOP size, entropy mode, and QP ranges.
- `platform_inst_cap_sm8250` sets session resolution and throughput limits.
- `iris_set_sm8250_preset_registers()` writes a fixed preset register at `reg_base + 0xB0088`.
- SM8250 tables describe ICC paths, reset IDs, decoder bandwidth points, power domains, OPP power domains, clocks, OPP clock, TZ CP carveout, HFI config-property arrays, and internal buffer types.
- `sm8250_data` and `sc7280_data` are exported platform descriptors.

## Control Flow And Integration Points
`iris_probe.c` selects this data for `"qcom,sm8250-venus"` or `"qcom,sc7280-venus"` when the legacy Venus driver is not enabled. Probe initializes gen1 HFI ops, resources from the table names, V4L2 capabilities from `inst_iris_fmts`, and session capability tables from `inst_fw_caps_*`. Stream-on uses the config-property lists and internal buffer tables; power scaling uses `sm8250_bw_table_dec` or `sc7280_bw_table_dec`; VPU control uses `iris_vpu2_ops`.

## State And Persistence Behavior
All descriptors and tables are static/global and persist for the module lifetime. The decoder fw-cap array is non-const because `PIPE` max/min/value are adjusted by platform data elsewhere. Per-session copies are created during decoder/encoder instance initialization.

## Dependencies
Depends on gen1 HFI defines and setters, common platform definitions, resource helpers, VPU buffer sizing, VPU common ops, and SC7280 supplemental tables from `iris_platform_sc7280.h`.

## Risks
- SC7280 reuses SM8250 caps and many tables but changes clocks, OPP power domain, bandwidth, pipe count, firmware name, and core throughput. Regression risk is high if shared tables are edited assuming one SoC.
- `inst_fw_cap_sm8250_enc` HFI IDs are gen1-specific; using gen2 IDs would break property programming.
- `num_vpp_pipe` directly affects buffer-size math and frequency calculations.
- The `dma_mask` upper bound and TZ CP region must stay compatible with firmware/IOMMU layout.

## Test Signals
- Boot/probe on SM8250 and SC7280 with the intended compatible string.
- Decoder stream-on for H.264/HEVC/VP9 and encoder stream-on for H.264/HEVC.
- V4L2 control tests for profile/level, bitrate, header mode, entropy, and QP controls.
- Runtime PM suspend/resume and firmware boot using `qcom/vpu-1.0/venus.mbn` or `qcom/vpu/vpu20_p1.mbn`.

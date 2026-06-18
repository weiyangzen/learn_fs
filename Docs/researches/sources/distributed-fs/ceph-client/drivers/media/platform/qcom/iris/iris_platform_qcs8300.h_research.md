# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_qcs8300.h

## Purpose
Supplies QCS8300-specific instance capability limits for inclusion by `iris_platform_gen2.c`.

## Important APIs And Data
- `platform_inst_cap_qcs8300` sets min/max dimensions, max macroblocks per frame, VPP/FW cycle coefficients, COMV count, and max frame/operating rate.
- Limits are narrower than SM8550: max frame width/height are 4096 and `max_mbpf` is based on 4096x2176.

## Control Flow And Integration Points
`qcs8300_data` in `iris_platform_gen2.c` references this struct through `.inst_caps`. Admission checks in `iris_vb2.c`, frame-size enumeration in `iris_vidc.c`, core throughput checks in `iris_utils.c`, and AV1 persistent buffer sizing all consume these caps.

## State And Persistence Behavior
The struct is static platform data. It is not mutated at runtime.

## Dependencies
Depends on `struct platform_inst_caps` and `MAXIMUM_FPS` from `iris_platform_common.h`, which must be included before this header.

## Risks
- Because this is a header with a static definition, it should only be included where intended; multiple inclusions in different C files would create separate private copies.
- Incorrect cap values can expose unsupported resolutions or reject valid QCS8300 workloads.

## Test Signals
- `VIDIOC_ENUM_FRAMESIZES` on QCS8300 reports 96 to 4096 limits.
- Stream-on rejects resolutions above QCS8300 capacity and accepts supported 4K-class workloads.

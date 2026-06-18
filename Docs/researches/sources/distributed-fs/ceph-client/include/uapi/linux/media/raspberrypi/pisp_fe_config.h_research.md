# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_fe_config.h

## Purpose
Defines Raspberry Pi PiSP front-end configuration UAPI for input acquisition, decompression/decompanding, black-level correction, defect correction, lens shading, stats generation, and two output branches.

## Important APIs, Types, And Functions
Primary exports are `pisp_fe_config`, `pisp_fe_global_config`, input/output AXI configs, input/output buffer configs, stats buffer config, decompand LUT, DPC/LSC/RGBY/AGC/AWB/CDAF/floating stats configs, crop/downscale configs, and `pisp_fe_output_branch_config`. Enable masks are in `pisp_fe_enable`; extra dirty bits are in `pisp_fe_dirty`.

## Control Flow
Userspace fills `pisp_fe_config`, sets global enable bits and dirty flags, provides DMA addresses, and configures stats/output branches. Drivers parse enabled blocks in pipeline order: input, optional decompress/decompand, correction blocks, stats windows, and per-branch crop/downscale/compress/output programming.

## State, Persistence, And Dependencies
The struct captures per-request hardware state. It persists only through the driver queue and DMA buffers; statistics output is written to the configured stats buffer. It depends on `pisp_common.h` and `pisp_fe_statistics.h`.

## Integration Points
Used by RP1 PiSP front-end media drivers and camera control algorithms. Statistics configuration must match the layout consumed through `pisp_fe_statistics.h`; output branches feed later pipeline stages or capture nodes.

## Risks
Packed layout, LUT sizes, stats window bounds, output buffer addresses, branch index macros, and enable/dirty consistency are the key ABI risks. Misconfigured stats weights or output dimensions can produce bad auto-exposure/autofocus feedback rather than immediate failures.

## Test Signals
Assert struct sizes/offsets, two-output branch handling, enable macro shifts, stats buffer sizing, decompand LUT length, AGC/AWB/CDAF window validation, and rejection of invalid DMA addresses or downscale ratios.

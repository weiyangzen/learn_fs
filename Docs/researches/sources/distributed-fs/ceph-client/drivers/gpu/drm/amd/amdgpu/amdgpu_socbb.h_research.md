## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_socbb.h

Purpose: defines firmware/UAPI-style structures for SoC bounding-box data used by display and power calculations, including voltage-scaling states and memory/display latency/bandwidth parameters.

Important APIs and types: `struct gpu_info_voltage_scaling_v1_0` stores per-state clocks and DRAM speed. `struct gpu_info_soc_bounding_box_v1_0` stores self-refresh times, urgent latencies, writeback latency, ideal bandwidth percentages, request size, downspread, DRAM timing/channel parameters, fabric/DCN return widths, VCO data, urgent out-of-order return sizes, VM page size, clock-change latencies, XFC timing, urgent burst flag, number of states, and up to eight clock-limit entries.

Control flow: no functions. The structures are data contracts for code that parses or reports GPU info bounding-box data.

State and persistence: no runtime state here; instances are populated elsewhere from firmware/BIOS or query data.

Dependencies and integration points: uses fixed-width integer types and integrates with display mode validation, DCN bandwidth calculations, and KMS GPU-info query paths.

Risks: struct layout is ABI/data-format sensitive. One field uses a C++-style comment with a long descriptive name, harmless for C99 kernels but notable. Consumers must respect `num_states` and not overrun the fixed `clock_limits[8]` array.

Test signals: display bring-up with firmware-provided bounding boxes, KMS info queries, and bandwidth/latency validation across supported ASICs.

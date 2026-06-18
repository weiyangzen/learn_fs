# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn4_soc_bb.h

## Purpose
`dcn4_soc_bb.h` defines static DML2.1 SoC and IP bounding boxes for DCN401/DCN4. It supplies clock tables, memory and fabric topology, DCN4x QoS parameters, power-management latencies, MALL/mcache settings, and IP resource caps.

## Important APIs, types, and functions
Key constants are `dml_dcn4_variant_a_soc_qos_params`, `dml2_socbb_dcn401`, and `dml2_dcn401_max_ip_caps`. The SoC table includes multi-entry fclk/dcfclk/dispclk/dppclk/dtbclk/socclk values, uclk and per-uclk DPM QoS latency arrays, GDDR-like DRAM topology, 64 MB MALL allocation, 512 outstanding requests, 64-byte return paths, GPUVM minimum page size, and DCN4x QoS margins. IP caps define four pipes/OTGs/DSC units, larger ROB/config return buffer values than DCN42, flip limits, SubVP margins, and FAMS2 timing constants.

## Control flow
The file has no executable control flow. Its constants are consumed during native SoC/IP construction for DCN4.01 and then guide mode support and programming calculations.

## State and persistence behavior
All state is static constant data in the compiled image. It is copied into DML initialization structures and not persisted elsewhere.

## Dependencies and integration points
It depends on `dml_top_soc_parameter_types.h`. It integrates with DML2.1 initialization selected by `dml21_dcn_revision_to_dml2_project_id()` for `DCN_VERSION_4_01` and with downstream clock/watermark/register calculations.

## Risks and edge cases
The multi-entry clock tables make off-by-one max-clock indexing particularly important. QoS arrays contain several per-uclk DPM entries with `minimum_uclk_khz = 0`, so selection logic must rely on surrounding translator/core semantics. Power-management latencies are much higher than DCN42 for DRAM clock change and stutter, so cross-project reuse would be risky.

## Test signals
DCN401 validation vectors, multi-clock-table bounds checks, UCLK/FCLK p-state support, SubVP/FAMS2 scheduling, MALL/mcache allocation, high-bandwidth four-pipe cases, and comparisons against hardware characterization are the main signals.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_structs.h

## Purpose
This header defines the data model used by the Display Mode Library and its VCS-DPI heritage. It contains the SoC/IP bounding boxes, pipe input/output structures, request/dialog calculation structures, hardware register field containers, watermark/latency structs, and DML helper pipe snapshots.

## Important APIs, Types, And Functions
Key typedefs alias `_vcs_dpi_*` structs to shorter names such as `voltage_scaling_st`, `soc_bounding_box_st`, `ip_params_st`, `display_pipe_source_params_st`, `display_output_params_st`, `display_e2e_pipe_params_st`, `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st`. `Watermarks`, `Latencies`, `DmlPipe`, and `SOCParametersList` provide higher-level DML calculation containers. Major structs include `_vcs_dpi_soc_bounding_box_st`, `_vcs_dpi_ip_params_st`, source/output/scaler/destination pipe params, RQ sizing/misc/dialog params, DLG/TTU/RQ register structs, DLG system params, and arbitration params.

## Control Flow And State
There is no executable flow. These structs are mutable state containers passed through DML validation, recalculation, RQ/DLG packing, FPU bounding-box update, and resource programming. Many fields are arrays or scalar hardware parameters whose units are implied by field name and calling convention.

## Dependencies And Integration Points
Includes `dc_features.h` and `display_mode_enums.h`. ASIC-specific FPU files populate `_vcs_dpi_ip_params_st` and `_vcs_dpi_soc_bounding_box_st`; resource code populates `display_e2e_pipe_params_st`; DML utility functions read and write these fields; RQ/DLG code emits `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st` for hardware programming.

## Risks
The file is a shared contract with little type-level unit safety. Fields mix MHz, MT/s, bytes, kbytes, microseconds, nanoseconds-derived values, fixed-point register encodings, booleans, and enum-backed ints. Many newer fields are appended for DCN32+ behavior, so older generation code may ignore them. Incorrect initialization, stale values, or partial struct copies can cause validation failures or hardware underflow.

## Test Signals
Tests should focus on end-to-end struct population rather than this header alone: bounding-box dumps, pipe parameter logs, RQ/DLG register dumps, validation statuses, and DML2 translation output. Static checks should verify new fields are initialized by relevant ASIC bounding boxes and pipe population paths.

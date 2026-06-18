# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_smu.c

Purpose: implements AIE2 SMU power sequencing and DPM clock programming for NPU1 and NPU4-derived devices.

Important APIs/functions: internal `aie2_smu_exec()` writes SMU argument and command registers, toggles interrupt, polls response, optionally reads output, and returns errors on timeout or non-OK response. `aie2_smu_init()` powers the device off then on. `aie2_smu_fini()` sets DPM level 0 and powers off. `npu1_set_dpm()` programs MP-NPU and H clocks separately and computes TOPS using returned frequency. `npu4_set_dpm()` sets hard and soft DPM levels and computes max/current TOPS from total columns and H clock.

Control flow: `aie2_hw_start()` initializes SMU before PSP firmware startup. `aie2_pm` calls generation-specific `set_dpm()` callbacks during init, power-mode changes, XRS default-DPM changes, and shutdown.

State and persistence: updates `npuclk_freq`, `hclk_freq`, `max_tops`, and `curr_tops` in `amdxdna_dev_hdl`; SMU hardware holds the actual power/clock state until changed or reset.

Dependencies: relies on per-generation SMU register offsets, DPM tables, `total_col` from firmware metadata, and `readx_poll_timeout()`.

Risks: DPM index bounds are assumed to have been validated by PM initialization. A failed power-off in init is treated as unrecoverable. TOPS formulas differ by generation and need hardware documentation alignment.

Test signals: SMU timeout/error paths, all DPM levels for NPU1 and NPU4 tables, power-cycle sequences during probe/remove and runtime PM, and resource-query values for current/max TOPS after DPM changes.

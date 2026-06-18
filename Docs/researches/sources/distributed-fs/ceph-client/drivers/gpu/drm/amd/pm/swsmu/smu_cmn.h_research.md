# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.h

## Purpose

`smu_cmn.h` declares the shared SWSMU helper API implemented in `smu_cmn.c` and defines metrics initialization/macrogen helpers used by SMU code layers. It also publishes SMU interrupt context IDs, PWM mode constants, PCIe speed helpers, and the v1 message-ops instance.

## Important APIs, Types, And Functions

Important declarations cover SMC message send/wait, debug message send, mapping translation, feature support/enabled queries, feature masks, table transfer, VRAM copy, metrics table reads, PPT/table writes, MP1 state programming, audio-function detection, policy description, backend workload-mask conversion, DPM/PCIe level printing, custom-level reset, PCIe generation/width indexes, and firmware version checks. Macros such as `smu_cmn_init_soft_gpu_metrics`, `smu_cmn_init_partition_metrics`, `smu_cmn_init_baseboard_temp_metrics`, and `smu_cmn_init_gpuboard_temp_metrics` initialize exported metric structures with headers and default `0xff` contents.

## Control Flow, State, And Persistence

The header itself has no runtime control flow except the inline `pcie_gen_to_speed()` lookup. Its macros impose initialization behavior on metrics objects by typechecking the expected revisioned structure, clearing to `0xff`, and filling header metadata. Persisted state is owned by callers: SMU contexts, firmware tables, feature masks, and exported metrics buffers.

## Dependencies And Integration Points

It includes `amdgpu_smu.h` and is gated for SWSMU code layers L2 through L4. It integrates with PPT implementations, sysfs power/feature controls, GPU metrics export, firmware table transfer, fan/PWM handling, SMU interrupt handling, and common SMU message transport.

## Risks And Test Signals

Risks include declaration/implementation drift, incorrect code-layer guards, metric revision mismatch, and PCIe helper indexing outside the `link_speed` table if callers pass invalid generations. Test signals are allmodconfig or AMDGPU builds, sparse/typecheck coverage for metrics macros, sysfs feature mask read/write, metrics initialization revision checks, and DPM/PCIe output tests.

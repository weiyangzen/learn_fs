# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_power.c

## Purpose
`a5xx_power.c` programs A5xx GPMU, limits management, thermal/power configuration, and GPMU firmware upload command buffers for A530/A540-class GPUs.

## Important APIs, Types, And Functions
Exported functions are `a5xx_power_init` and `a5xx_gpmu_ucode_init`. Private helpers include `_get_mvolts`, `a530_lm_setup`, `a540_lm_setup`, `a5xx_pc_init`, `a5xx_gpmu_init`, and `a5xx_lm_enable`. Static data includes the A530 sequence register table and AGC/GPMU message offsets.

## Control Flow
`a5xx_gpmu_ucode_init` validates GPMU firmware format, checks firmware ID 2, extracts the command stream region, creates a GPU-readonly BO, and writes a sequence of type4 packets that load instruction RAM in chunks bounded by `TYPE4_MAX_PAYLOAD`. `a5xx_power_init` exits on chips without GPMU, runs A530 or A540 limits-management setup, initializes SP/TP power collapse registers, calls `a5xx_gpmu_init`, then enables LM interrupts/throttling for A530.

`a5xx_gpmu_init` submits the prepared GPMU firmware BO as an indirect buffer with protected mode disabled, waits for idle, optionally programs A530 WFI config, releases CM3 reset, and polls `GPMU_GENERAL_0` for the `BABEFACE` handshake. A540 also checks `GPMU_GENERAL_1` for firmware failure.

## State And Persistence
Persistent state is stored in `a5xx_gpu->gpmu_bo`, `gpmu_iova`, `gpmu_dwords`, and `lm_leakage`. Hardware state includes AGC message RAM, power-collapse controls, voltage/frequency payloads derived from OPP data, thermal sensor configuration, GPMU interrupt masks, and throttle controls.

## Dependencies And Integration Points
The file depends on PM OPP APIs for voltage lookup, A5xx register definitions, ring packet macros through `a5xx_gpu.h`, common firmware data in `adreno_gpu->fw[ADRENO_FW_GPMU]`, and `a5xx_flush`/`a5xx_idle` from the runtime file.

## Risks
Firmware parsing is intentionally conservative; invalid firmware silently disables GPMU microcode preparation. Power setup is only implemented for A530/A540 and uses hardcoded thresholds. If the GPMU handshake times out, the code logs but does not always fail hard, so advanced power behavior may be absent while the GPU remains usable. The IB upload must run with protected mode disabled and then restored.

## Test Signals
Signals include `gpmufw` BO creation, nonzero `gpmu_dwords`, successful type4 command construction, `GPMU_GENERAL_0 == 0xBABEFACE`, no nonzero A540 failure code, voltage payload matching OPP data, A530 LM interrupts configured, and GPU workloads remaining stable across power collapse.

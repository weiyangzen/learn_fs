# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_gmu.xml

## Purpose
`a6xx_gmu.xml` describes the register map for the A6xx-generation GMU and related GMU/RSCC address space, with variant annotations extending through A7xx and A8xx offsets where the same logical register moved. The generated header `a6xx_gmu.xml.h` is used directly by GMU, HFI, preemption, GPU state capture, catalog, and A8xx code paths.

## Important definitions
The file imports `freedreno_copyright.xml` and `adreno_common.xml`, then defines one 32-bit domain named `A6XX` with `prefix="variant"` and `varset="chip"`. It contains 171 registers and 41 explicit bitfields.

The register set covers GMU boot and memory windows (`GMU_CM3_ITCM_START`, `GMU_CM3_DTCM_START`, `GMU_CM3_SYSRESET`, `GMU_CM3_BOOT_CONFIG`, `GMU_CM3_FW_BUSY`, `GMU_CM3_FW_INIT_RESULT`), firmware/version state (`GMU_CORE_FW_VERSION` with `MAJOR`, `MINOR`, and `STEP` fields), cache and bus configuration (`GMU_ICACHE_CONFIG`, `GMU_DCACHE_CONFIG`, `GMU_SYS_BUS_CONFIG`, `GMU_MRC_GBIF_QOS_CTRL`), DCVS votes/settings (`GMU_GX_VOTE_IDX`, `GMU_MX_VOTE_IDX`, `GMU_DCVS_*`), power counters and always-on counters, power collapse/nap/RPMh controls, HFI queue registers (`GMU_HFI_*`), GMU-to-host and host-to-GMU interrupts, AO interrupt status/control, CX/GX busy status, OOB request/ack/clear registers, watchdog, fence ranges, idle status, and RSCC sequence/TCS/timestamp registers.

Variant-specific entries are central. Examples include `GMU_CX_GMU_POWER_COUNTER_ENABLE` at an A6xx/A7xx offset and a separate A8xx offset, `GMU_SPTPRAC_PWR_CLK_STATUS` with A6xx and A7xx bit layouts, `GMU_PWR_CLK_STATUS` for A8xx+, and `GMU_ALWAYS_ON_COUNTER_*` / keepalive registers moving between A6xx-A7xx and A8xx+. Several RSCC registers also carry A740-specific or A8xx+ variants.

## Control flow and generation behavior
The XML is converted to `generated/a6xx_gmu.xml.h` during the msm build. Runtime code calls inline helpers such as `gmu_read()`, `gmu_write()`, `gmu_rmw()`, and `gmu_read64()` with generated register constants. The practical control flow is visible in `a6xx_gmu.c`: initialize clocks/memory/IRQs, load firmware, configure power/RPMh, start HFI, manage out-of-band requests, set frequencies/bandwidth, read idle and power status, and shut down or force off the GMU. `a6xx_hfi.c` uses the HFI registers for queue setup and messaging. `a6xx_gpu_state.c` uses generated constants for crash/state capture. `a8xx_gpu.c` and `a8xx_preempt.c` also include this generated header for shared/newer GMU controls.

## State and persistence
The XML itself is static, but it names registers controlling persistent device state while the GPU is powered: firmware boot state, HFI queues, interrupt masks/status, RPMh votes, power-collapse policy, OOB ownership, watchdog/fault state, performance-counter OOB access, and RSCC sequences. Incorrect values can survive until GMU reset, GPU suspend/resume, or full device power cycle.

## Dependencies and integration points
The generated header is listed in the msm Makefile and included by `a6xx_gmu.c`, `a6xx_hfi.c`, `a6xx_gpu.c`, `a6xx_gpu_state.c`, `a6xx_preempt.c`, `a6xx_catalog.c`, `a8xx_gpu.c`, and `a8xx_preempt.c`. It integrates with firmware HFI protocols, devfreq/OPP frequency setup, RPMh power-vote programming, GPU state capture, IRQ handling, and preemption. The `chip` varset from `adreno_common.xml` is required for variant selection.

## Risks
This is a high-risk hardware-control map. Wrong offsets or variant guards can write power, interrupt, OOB, or firmware-control values to the wrong register, causing boot failures, hangs, spurious interrupts, broken suspend/resume, or power-collapse instability. The A8xx remaps are especially sensitive because the same logical names can exist at different offsets. Bitfield layout changes in `GMU_SPTPRAC_PWR_CLK_STATUS`, `GMU_PWR_CLK_STATUS`, and RPMh controls can invert readiness or power-state checks.

## Test signals
Validation starts with XML schema validation, generated-header compilation, and successful inclusion by all GMU/HFI/A8xx objects. Runtime signals include GMU firmware boot, HFI init and message acknowledgments, successful devfreq changes, suspend/resume cycles, OOB set/clear for GPU/perfcounter/boot-slumber states, interrupt handling without storms, GPU state capture after a fault, and A6xx/A7xx/A8xx smoke tests that exercise both legacy and variant-remapped offsets.

# subset-b-003647 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.c

### Purpose
`adreno_gpu.c` is the shared implementation layer for Qualcomm Adreno GPUs in the MSM DRM driver. It handles secure zap-shader loading, IOMMU GPUVM setup, firmware lookup and BO creation, common hardware initialization, ringbuffer flushing/idling, fault capture, userspace parameter plumbing, power-level discovery, OCMEM allocation, and common debug/devcoredump formatting.

### Important APIs, Types, And Functions
The exported helpers include `adreno_zap_shader_load()`, `adreno_create_vm()`, `adreno_iommu_create_vm()`, `adreno_private_vm_size()`, `adreno_fault_handler()`, `adreno_get_param()`, `adreno_set_param()`, `adreno_request_fw()`, `adreno_load_fw()`, `adreno_fw_create_bo()`, `adreno_hw_init()`, `adreno_flush()`, `adreno_idle()`, `adreno_gpu_state_get()`, `adreno_gpu_state_put()`, `adreno_show()`, `adreno_dump_info()`, `adreno_dump()`, `adreno_wait_ring()`, OCMEM helpers, `adreno_read_speedbin()`, `adreno_gpu_init()`, and `adreno_gpu_cleanup()`. The file also defines the `address_space_size` module parameter and a process-wide `zap_available` cache.

### Control Flow
Zap shader loading first checks Qualcomm architecture support and a `zap-shader` reserved-memory child node, then chooses device-tree `firmware-name`, gpulist firmware through `adreno_request_fw()`, or fails for newer targets with no explicit signed image. It sizes and maps the reserved memory, loads the MDT image with the correct legacy or `qcom/` path, and asks SCM to authenticate/reset the PAS ID. GPUVM creation wraps `msm_iommu_gpu_new()`, obtains aperture geometry, starts at at least 16 MiB, and creates an `msm_gem_vm_create()` GPU VM. Hardware init resets ring software pointers, memptr read pointers, and bad fence values before generation-specific code continues.

### State, Persistence, And Dependencies
Persistent driver state is stored in `struct adreno_gpu` and `struct msm_gpu`: firmware pointers, `fwloc`, UBWC config references, fault completion, ringbuffer memptrs, fast OPP rate, and pm-runtime autosuspend configuration. Fault handling mutates `priv->stall_enabled` and `stall_reenable_time`, temporarily disables SMMU stall-on-fault, captures crashstate when the fault was stalled, and completes `fault_coredump_done` for concurrent GMU traffic. Dependencies include Linux firmware APIs, reserved memory, Qualcomm SCM/MDT loader, OPP/nvmem, OCMEM, MSM GEM/MMU/GPUVM helpers, pm-runtime, debugfs/devcoredump printers, and Adreno generation hooks from `adreno_gpu_funcs`.

### Integration Points
`adreno_get_param()` and `adreno_set_param()` implement DRM UAPI parameters for GPU ID, GMEM, chip ID, timestamps, priorities, fault/suspend counters, per-process VA ranges, UBWC fields, ray tracing, PRR, AQE, context command names, sysprof, and VM_BIND enablement. Firmware helpers are used by generation-specific GPU init paths before uploading microcode. Ringbuffer helpers feed command submission paths, while `adreno_show()` and dump helpers integrate with debugfs, devcoredump, hangcheck, and crash analysis tools.

### Risks
Zap firmware path selection is stateful through `fwloc` and `zap_available`; an early unsupported/failed platform path can suppress later zap attempts. `adreno_fw_create_bo()` assumes firmware blobs have a four-byte header and would underflow if handed a too-small blob. Fault handling depends on correct SMMU stall semantics and crashstate serialization. `adreno_private_vm_size()` depends on TTBR1 IAS data when available and falls back to 4 GiB otherwise. Ringbuffer free-space and idle waits are busy jiffies loops, so incorrect rptr/wptr reporting can cause stalls or false timeouts.

### Test Signals
Useful signals include probe on targets with new, legacy, and helper firmware paths; zap shader reserved-memory sizing failures; SCM unavailable and `-EOPNOTSUPP` paths; GPUVM aperture sizing with and without the 4 GiB quirk; UAPI `MSM_PARAM_*` queries including per-process VA rejection on global VM; fault injection with and without `adreno_smmu_fault_info`; ringbuffer wrap-around flush/idling; debugfs/devcoredump output containing ring, BO, VM-log, fault, and register sections; OPP fallback on old a2xx/a320 device trees; and cleanup releasing all loaded firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.h

### Purpose
`adreno_gpu.h` is the common Adreno interface shared by generation-specific MSM GPU drivers. It declares GPU identity tables, quirk bits, firmware slots, common runtime state, generation predicates, ringbuffer packet emitters, register-protection encoders, and prototypes implemented by `adreno_gpu.c`.

### Important APIs, Types, And Functions
Key types are `enum adreno_family`, `struct adreno_gpu_funcs`, `struct adreno_info`, `struct adreno_gpulist`, `struct adreno_protect`, register-list wrapper structs, `struct adreno_gpu`, `struct adreno_ocmem`, and `struct adreno_platform_config`. Important macros include `ADRENO_FW_*`, `ADRENO_QUIRK_*`, `ADRENO_CHIP_IDS()`, `DECLARE_ADRENO_GPULIST()`, `ADRENO_SPEEDBINS()`, `DECLARE_ADRENO_PROTECT()`, `ADRENO_IDLE_TIMEOUT`, `spin_until()`, `ADRENO_VM_START`, PM4 packet helpers, `PKT4()`, `PKT7()`, and `gpu_poll_timeout()`.

### Control Flow
The header is primarily declarative. Generation-specific drivers fill `struct adreno_info` tables with chip IDs, firmware names, GMEM size, quirks, function tables, zap firmware, inactive period, optional a6xx metadata, speedbins, and preemption record sizing. Probe passes `struct adreno_platform_config` to common init, and runtime code uses inline predicates such as `adreno_is_a650_family()`, `adreno_is_a7xx()`, and `adreno_has_rgmu()` to select generation-specific behavior.

### State, Persistence, And Dependencies
`struct adreno_gpu` embeds `struct msm_gpu` and persists chip identity, firmware location and firmware handles, UBWC configuration, register offset tables, GMU wrapper state, ray-tracing capability, UCHE trap base, and fault-coredump completion. The header depends on Linux firmware/iopoll/UBWC headers, `msm_gpu.h`, and generated Adreno XML packet/register definitions.

### Integration Points
Generation drivers include this header to bind their `msm_gpu_funcs` into `adreno_gpu_funcs`, emit CP packets into ringbuffers, define protected register ranges, identify GPU revisions, and call common firmware, VM, fault, OCMEM, debug, and initialization helpers. UAPI-facing code uses `ADRENO_CHIPID_FMT` and `ADRENO_CHIPID_ARGS()` to expose chip IDs in the format expected by crash/debug tools.

### Risks
Many inline predicates compare only `info->revn` or the first chip ID; table mistakes can route a GPU through the wrong generation path. `spin_until()` is a busy loop with a one-second timeout, so it should stay on short hardware waits. Packet helpers call `adreno_wait_ring()` before writing but assume correct dword counts. The `ADRENO_PROTECT_RDONLY()` macro appears to lack an operator between `(1 << 29)` and the following shifted size expression, making compile coverage important if that macro is used.

### Test Signals
Compile tests across all enabled Adreno generations are essential because this header is macro-heavy. Runtime signals include correct GPU family detection for chip IDs, PM4 packet parity values for type4/type7 packets, ring space waits under wrap-around, register-protection encodings for aligned ranges, firmware-slot selection for pre-a6xx and a6xx+ devices, and UAPI chip/revision reporting for speedbin-based entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_10_0_sm8650.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_10_0_sm8650.h

### Purpose
This header describes the DPU 10.0 hardware catalog for SM8650. It exports static catalog data for a high-end display controller with wide 8192-line support, source split, dim layer, idle power collapse, 3D merge, DSC, writeback, concurrent writeback, and DP/DSI interfaces.

### Important APIs, Types, And Functions
The file defines `sm8650_dpu_caps`, `sm8650_mdp`, `sm8650_ctl`, `sm8650_sspp`, `sm8650_lm`, `sm8650_dspp`, `sm8650_pp`, `sm8650_merge_3d`, `sm8650_dsc`, `sm8650_wb`, `sm8650_cwb`, `sm8650_intf`, `sm8650_perf_data`, `sm8650_mdss_ver`, and the exported `sm8650_dpu_cfg`. The topology is 6 CTLs, 10 SSPPs, 6 layer mixers, 4 DSPPs, 10 pingpongs, 5 merge-3D blocks, 6 DSC blocks, 1 WB block, 4 CWB entries, and 4 external interfaces.

### Control Flow
There is no executable control flow. At probe, DPU catalog selection points to `sm8650_dpu_cfg`; DPU core code walks each array and programs matching register bases, interrupt indices, block features, and performance limits. Interfaces include DP0, DSI0, DSI1, and a second DP0 entry paired for MST, all with 24 worst-case programmable-fetch lines.

### State, Persistence, And Dependencies
All state is compile-time constant. The catalog depends on shared DPU structures, block IDs, feature masks such as `VIG_SDM845_MASK_SDMA`, sub-block descriptors such as qseed/LM/DSPP/pingpong/DSC/WB data, and IRQ/controller ID constants. Runtime persistence comes from DPU driver objects initialized from these tables, not from this header.

### Integration Points
The `dpu_mdss_cfg` integrates with DRM modeset resource discovery, atomic plane allocation, mixer/pingpong/DSC pairing, writeback exposure, interrupt setup, and bandwidth/performance voting. `max_bw_high = 27000000` and `min_prefill_lines = 35` tune bandwidth admission and prefill calculations for SM8650.

### Risks
Register base, IRQ, and pairing mistakes can silently misroute interrupts or break dual-pipe/DSC/MST topologies. CWB and WB entries must agree with the hardware paths exposed by the driver. Because the catalog uses generic SDM845-era masks and shared sub-block descriptors, SoC-specific deltas can be missed unless validated against hardware documentation.

### Test Signals
Signals include successful display probe on SM8650, DP MST using paired DP0 interfaces, dual DSI modes, DSC enablement across 6 encoders, writeback and CWB enumeration, atomic bandwidth validation near 27 GB/s units used by the catalog, interrupt delivery for all CTLs/pingpongs, and suspend/resume with idle PC enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_10_0_sm8650.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_0_sm8750.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_0_sm8750.h

### Purpose
`dpu_12_0_sm8750.h` defines the SM8750 DPU 12.0 catalog. It models a flagship display block with 8192 maximum linewidth, 0xb blend stages, source split, dim layer, idle PC, 3D merge, DSC, writeback, CWB, and DP/DSI/MST output paths.

### Important APIs, Types, And Functions
The header provides `sm8750_dpu_caps`, top MDP data, CTL/SSPP/LM/DSPP/pingpong/merge3d/DSC/WB/CWB/interface arrays, performance data, version data, and `sm8750_dpu_cfg`. Its resource counts are 6 CTLs, 10 SSPPs, 8 mixers, 4 DSPPs, 12 pingpongs, 6 merge-3D blocks, 8 DSC blocks, 1 WB, 4 CWB entries, and 4 interfaces.

### Control Flow
The tables are consumed by the common DPU resource manager rather than executed. The selected `dpu_mdss_cfg` lets the driver enumerate block counts, map register offsets, attach IRQ starts for CTLs, and match interface controllers: DP0, DSI0, DSI1, and a paired DP0 MST interface, each with 24 programmable-fetch lines.

### State, Persistence, And Dependencies
The catalog is immutable kernel data. It depends on DPU catalog types, shared feature masks, sub-block descriptors, block enum IDs, and MSM DP/DSI controller IDs. Runtime state is created by the DPU core from these constants during device initialization.

### Integration Points
SM8750's `core_major_ver = 12`, `core_minor_ver = 0` lets version-sensitive DPU code choose appropriate programming paths. `max_bw_high = 28500000` and `min_prefill_lines = 35` feed DPU performance calculations. The large DSC/pingpong/merge topology integrates with high-resolution dual-pipe and compressed-display modes.

### Risks
The larger mixer and DSC count increases the risk of inconsistent pairings between LM, pingpong, merge3d, and DSC arrays. MST reusing controller 0 requires the encoder/connector code to understand paired interfaces. Incorrect performance limits can cause either rejected valid modes or under-voted bandwidth.

### Test Signals
Probe should expose the expected plane, mixer, DSC, WB, CWB, DSI, and DP resources. Useful tests include dual DSI, DP MST, DSC on multiple pipes, writeback capture, high-linewidth atomic modes, IRQ-driven vblank/CTL completion, and bandwidth validation around the 28.5M high threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_0_sm8750.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_2_glymur.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_2_glymur.h

### Purpose
This file describes the Glymur DPU 12.2 catalog, a high-end multi-output display topology. It extends the DPU 12 family with 8 CTLs, 8 DSPPs, many DP interfaces, DSC, CWB, and 8192-line capability.

### Important APIs, Types, And Functions
The exported catalog pieces are `glymur_dpu_caps`, `glymur_mdp`, arrays for CTL, SSPP, LM, DSPP, pingpong, merge3d, DSC, WB, CWB, and interfaces, plus `glymur_perf_data`, `glymur_mdss_ver`, and `glymur_dpu_cfg`. Counts are 8 CTLs, 10 SSPPs, 8 LMs, 8 DSPPs, 10 pingpongs, 4 merge-3D blocks, 8 DSC blocks, 1 WB, 4 CWB entries, and 9 interfaces.

### Control Flow
The common DPU catalog code indexes this static topology to instantiate resources. Interface entries include DP0, DSI0, DSI1, paired DP0 MST, DP1, DP3, DP2, paired DP2 MST, and paired DP1 MST, each with 24 worst-case programmable-fetch lines. CTL interrupt starts cover TOP0_INTR2 bits 9 through 15 plus 23.

### State, Persistence, And Dependencies
All fields are static constants. Dependencies are the DPU catalog ABI, shared sub-block descriptors, DPU IRQ macros, and MSM display controller IDs. The data persists in `.rodata`; mutable display state is allocated elsewhere from these tables.

### Integration Points
`glymur_dpu_cfg` feeds resource allocation for multi-display systems, including many DP controller routes and concurrent DSC pipelines. `max_bw_high = 28500000` and `min_prefill_lines = 35` integrate with bandwidth and latency admission, while version 12.2 gates hardware-version-specific paths.

### Risks
The 9-interface topology is the main risk: controller IDs and MST pairing comments must match the physical output routing. Any mismatch between 8 DSPPs and mixer/display paths can break color processing assignment. The four merge-3D entries with eight DSC blocks require careful resource-manager validation for split/compressed modes.

### Test Signals
Validate probe counts, simultaneous DP/DSI enumeration, DP1/DP2/DP3 routing, MST on paired DP entries, DSC allocation across eight blocks, CWB/WB availability, CTL interrupt delivery for all 8 CTLs, and high-bandwidth atomic tests near the configured limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_2_glymur.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_4_eliza.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_4_eliza.h

### Purpose
`dpu_12_4_eliza.h` defines a smaller DPU 12.4 catalog for Eliza-class hardware. It keeps the modern DPU features of source split, dim layer, idle PC, 3D merge, DSC, WB, and CWB, but with fewer pipes and a lower bandwidth ceiling than SM8750/Glymur.

### Important APIs, Types, And Functions
The header exports `eliza_dpu_caps`, `eliza_mdp`, `eliza_ctl`, `eliza_sspp`, `eliza_lm`, `eliza_dspp`, `eliza_pp`, `eliza_merge_3d`, `eliza_dsc`, `eliza_wb`, `eliza_cwb`, `eliza_intf`, `eliza_perf_data`, `eliza_mdss_ver`, and `eliza_dpu_cfg`. Counts are 4 CTLs, 6 SSPPs, 4 mixers, 3 DSPPs, 8 pingpongs, 4 merge-3D blocks, 3 DSC blocks, 1 WB, 4 CWB entries, and 4 interfaces.

### Control Flow
The DPU core consumes the static `dpu_mdss_cfg` and walks each array to publish resources. The interface list is DP0, DSI0, DSI1, and a paired DP0 MST interface with 24 programmable-fetch lines. The CTL interrupt starts use TOP0_INTR2 bits 9-12.

### State, Persistence, And Dependencies
There is no mutable state in this header. It depends on shared DPU catalog structures, sub-block descriptors, and controller IDs. The constants are copied or referenced by runtime DPU resource objects created during probe.

### Integration Points
Version 12.4 and `max_bw_high = 14200000` place this catalog in the modern DPU programming family while reflecting a reduced resource/bandwidth envelope. WB/CWB and DSC entries integrate with writeback and compressed display paths, and the DP/DSI interfaces feed encoder creation.

### Risks
The asymmetric DSC count of 3 relative to 4 mixers and 8 pingpongs makes resource allocation edge cases likely for split DSC modes. CWB entries must not advertise impossible concurrent capture routes. Lower bandwidth means perf-data mistakes can produce visible underruns or unnecessarily reject modes.

### Test Signals
Probe should expose the expected reduced counts. Exercise single and dual DSI, DP MST pairing, DSC resource exhaustion cases, writeback/CWB, high-resolution modes near the 14.2M bandwidth ceiling, and CTL/pingpong interrupt paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_4_eliza.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_13_0_kaanapali.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_13_0_kaanapali.h

### Purpose
This header defines the Kaanapali DPU 13.0 catalog. It is a newer flagship-style display configuration with 8192-line support, source split, dim layer, idle PC, 3D merge, DSC, WB, CWB, and DP/DSI/MST interfaces.

### Important APIs, Types, And Functions
Static exports include `kaanapali_dpu_caps`, `kaanapali_mdp`, resource arrays for CTL/SSPP/LM/DSPP/pingpong/merge3d/DSC/WB/CWB/interface blocks, `kaanapali_perf_data`, `kaanapali_mdss_ver`, and `kaanapali_dpu_cfg`. The topology has 6 CTLs, 10 SSPPs, 8 mixers, 4 DSPPs, 12 pingpongs, 6 merge-3D blocks, 8 DSC blocks, 1 WB, 4 CWB entries, and 4 interfaces.

### Control Flow
No functions execute here. Probe selects `kaanapali_dpu_cfg`, then the DPU catalog/resource code maps each block by array order, base, length, ID, pair links, and IRQ start. Interfaces are DP0, DSI0, DSI1, and paired DP0 MST, all with 24 programmable-fetch lines.

### State, Persistence, And Dependencies
The file contributes immutable catalog data. It depends on shared DPU feature masks, sub-block descriptors, IRQ macros, and controller enums. Runtime resources persist in DPU driver structures initialized from the constants.

### Integration Points
`core_major_ver = 13` identifies the newest programming family in this subset. `max_bw_high = 30200000` and `min_prefill_lines = 35` feed DPU bandwidth and prefill calculations. The resource tables integrate with atomic plane allocation, DSC compression, CWB/WB, and DP/DSI encoder setup.

### Risks
As a high-resource catalog, errors in mixer-pingpong-merge3d-DSC relationships can break only complex modes and be missed by basic boot tests. The very high bandwidth ceiling must match interconnect capabilities. Version 13.0 paths need compile/runtime coverage in the DPU core.

### Test Signals
Validate resource counts at probe, high-bandwidth 8192-line display modes, DP MST on the paired interface, dual DSI, DSC across eight encoders, CWB and WB capture, interrupt delivery across all CTLs, and suspend/resume with idle power collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_13_0_kaanapali.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_14_msm8937.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_14_msm8937.h

### Purpose
`dpu_1_14_msm8937.h` describes an older, compact DPU 1.14 display block for MSM8937. It provides the resource map needed for DSI-only mobile display support with source split, dim layer, idle PC, and modest bandwidth.

### Important APIs, Types, And Functions
The file defines `msm8937_dpu_caps`, an MDP array, CTL/SSPP/LM/pingpong/DSPP/interface arrays, `msm8937_perf_data`, version data, and `msm8937_dpu_cfg`. The topology is 3 CTLs, 4 SSPPs, 2 mixers, 1 DSPP, 2 pingpongs, and 2 DSI interfaces.

### Control Flow
The header is pure data. During probe, catalog selection supplies register bases and counts to common DPU code. Interface entries map DSI0 and DSI1 with 14 worst-case programmable-fetch lines, and the performance table sets a low `max_bw_high = 3100000` and `min_prefill_lines = 14`.

### State, Persistence, And Dependencies
All data is static and immutable. Dependencies are shared DPU catalog definitions, older DPU block IDs, feature masks, and MSM DSI controller IDs. Runtime state is allocated by the DPU core from these constants.

### Integration Points
The catalog integrates older MSM8937 display hardware into the same resource manager used by newer DPU versions. Its version 1.14 data and array counts constrain plane/mixer allocation, DSI encoder setup, and bandwidth admission.

### Risks
Older DPU v1 catalogs often use arrays and legacy sub-block assumptions that differ from newer single-struct MDP catalogs. Wrong DSI controller IDs or mixer/pingpong pairings can break dual-panel or split-display modes. Low bandwidth and prefill values make underrun testing important.

### Test Signals
Boot/probe on MSM8937, DSI0 and DSI1 panel modes, source-split configurations, vblank/CTL interrupts, bandwidth rejection near 3.1M, underrun counters, and suspend/resume with idle PC are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_14_msm8937.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_15_msm8917.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_15_msm8917.h

### Purpose
This header provides the DPU 1.15 catalog for MSM8917, a minimal single-display configuration. It supports a compact DSI-only path with dim layer and idle PC but without the multi-pipe resources present in larger SoCs.

### Important APIs, Types, And Functions
It defines `msm8917_dpu_caps`, MDP data, CTL/SSPP/LM/DSPP/pingpong/interface arrays, `msm8917_perf_data`, `msm8917_mdss_ver`, and `msm8917_dpu_cfg`. Counts are 3 CTLs, 4 SSPPs, 1 mixer, 1 DSPP, 1 pingpong, and 1 DSI interface.

### Control Flow
The common DPU driver reads the `dpu_mdss_cfg` to instantiate one primary display path. The single interface is DSI0 with 14 programmable-fetch lines; `max_bw_high = 1800000` and `min_prefill_lines = 21` tune the low-end bandwidth and latency envelope.

### State, Persistence, And Dependencies
The header has no mutable state. It depends on DPU catalog structures, shared old-generation sub-block descriptions, and MSM DSI controller constants. The static data persists in the kernel image and is referenced during DPU probe.

### Integration Points
This catalog constrains DRM plane/mixer allocation to a single-mixer topology and exposes the DSI encoder path for MSM8917 device trees. Version 1.15 lets code distinguish it from related MSM8937/MSM8953 v1 variants.

### Risks
Because only one mixer and pingpong exist, resource-manager fallback paths for split or secondary displays must reject cleanly. The `min_prefill_lines` differs from MSM8937/MSM8953, so copy/paste perf errors would directly affect underrun behavior.

### Test Signals
Validate single DSI panel probe, no accidental secondary-output exposure, atomic modeset with only one mixer, underrun-free operation at expected panel clocks, bandwidth rejection near 1.8M, and suspend/resume through idle PC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_15_msm8917.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_16_msm8953.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_16_msm8953.h

### Purpose
`dpu_1_16_msm8953.h` describes the DPU 1.16 catalog for MSM8953. It is close to MSM8937 but with MSM8953-specific versioning and performance limits for a dual-DSI capable, two-mixer mobile display block.

### Important APIs, Types, And Functions
The header defines `msm8953_dpu_caps`, MDP, CTL, SSPP, LM, pingpong, DSPP, interface, performance, version, and `msm8953_dpu_cfg` data. The topology is 3 CTLs, 4 SSPPs, 2 mixers, 1 DSPP, 2 pingpongs, and 2 DSI interfaces.

### Control Flow
There is no runtime code. Probe consumes `msm8953_dpu_cfg`, maps register blocks, and exposes DSI0/DSI1 interfaces with 14 programmable-fetch lines. The performance table sets `max_bw_high = 3400000` and `min_prefill_lines = 14`.

### State, Persistence, And Dependencies
Catalog data is immutable. It depends on shared DPU structs and old-generation sub-block descriptors, DPU block IDs, and MSM DSI controller IDs. Runtime state is in DPU core objects derived from the catalog.

### Integration Points
The catalog integrates MSM8953 into the common DPU resource manager, atomic modeset paths, DSI encoder creation, and perf calculations. Its version tuple 1.16 distinguishes it from the sibling MSM8937/MSM8917 catalogs.

### Risks
Because the file resembles MSM8937, the main risks are SoC-specific register/perf drift and accidental reuse of wrong resource counts. Dual DSI requires correct interface/controller mapping. Missing DSC/WB resources must be reflected by callers that request those features.

### Test Signals
Probe on MSM8953, DSI0 and DSI1 panel attachment, dual-pipe/source-split paths, bandwidth around 3.4M, underrun counters under memory pressure, and suspend/resume are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_16_msm8953.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_7_msm8996.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_7_msm8996.h

### Purpose
This file defines the DPU 1.7 catalog for MSM8996. It models an older high-end display block with source split, multiple mixers, DSC, dual DSI, HDMI, and a placeholder interface.

### Important APIs, Types, And Functions
It exports `msm8996_dpu_caps`, MDP array data, 5 CTLs, 10 SSPPs, 4 mixers, 2 DSPPs, 4 pingpongs, 2 DSC blocks, 4 interfaces, performance data, version data, and `msm8996_dpu_cfg`. Interfaces include an `INTF_NONE` entry, DSI0, DSI1, and HDMI, with 25 programmable-fetch lines.

### Control Flow
The common DPU code uses the static arrays to construct resources and route encoders. No control flow is present in the header. `max_bw_high = 9600000` and `min_prefill_lines = 21` feed bandwidth and prefill calculations for this older high-end target.

### State, Persistence, And Dependencies
State is static read-only catalog data. Dependencies include DPU v1 block definitions, DSC catalog descriptors, interface type enums, DSI controller IDs, and HDMI integration constants.

### Integration Points
`msm8996_dpu_cfg` connects MSM8996 hardware to DRM plane/resource allocation, DSI/HDMI encoder setup, DSC assignment, and interrupt/performance handling. The use of an MDP array rather than a single MDP struct reflects older catalog conventions.

### Risks
The `INTF_NONE` slot and HDMI path are legacy-specific and can confuse generic interface iteration if not handled correctly. DSC and split-display resources must match mixer/pingpong wiring. Older register offsets are less similar to newer SDM845+ catalogs.

### Test Signals
Validate DSI0, DSI1, HDMI, and the ignored/none interface behavior; DSC modes; source split; plane allocation across 10 SSPPs; vblank and CTL interrupts; bandwidth near 9.6M; and suspend/resume on MSM8996 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_1_7_msm8996.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_0_msm8998.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_0_msm8998.h

### Purpose
`dpu_3_0_msm8998.h` describes the MSM8998 DPU 3.0 catalog. It provides a high-end but pre-SDM845 topology with source split, idle/dim features, DSC, DP, dual DSI, and HDMI.

### Important APIs, Types, And Functions
The catalog defines `msm8998_dpu_caps`, `msm8998_mdp`, 5 CTLs, 8 SSPPs, 4 mixers, 2 DSPPs, 4 pingpongs, 2 DSC blocks, 4 interfaces, performance data, version data, and `msm8998_dpu_cfg`. Interfaces are DP0, DSI0, DSI1, and HDMI with 21 programmable-fetch lines.

### Control Flow
There is no executable logic. At probe, DPU code traverses the arrays to create resources and configure register/interrupt ranges. The performance table uses `max_bw_high = 6700000` and `min_prefill_lines = 25`.

### State, Persistence, And Dependencies
All fields are immutable catalog constants. Dependencies include DPU catalog structures, feature masks, DSC descriptors, DPU IRQ macros, and MSM DP/DSI/HDMI interface identifiers.

### Integration Points
The catalog integrates MSM8998 with the shared DRM resource manager, output encoder creation, DSC support, and bandwidth voting. It bridges older DPU v3 hardware into the same table-driven infrastructure as newer targets.

### Risks
DP/DSI/HDMI interface mix needs exact controller mapping. The two-DSC/four-mixer ratio must reject unsupported compressed split modes cleanly. Incorrect bandwidth values may cause underruns because this target has a relatively tight perf envelope.

### Test Signals
Probe count checks, DP and HDMI hotplug/modes, DSI panels, DSC modes, split-display allocation, interrupt delivery, and bandwidth/underrun tests around 6.7M are strong validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_0_msm8998.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_2_sdm660.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_2_sdm660.h

### Purpose
This header defines the DPU 3.2 catalog for SDM660. It models a mid-range display block with source split, dim/idle/3D-merge capability, DP, dual DSI, and DSC.

### Important APIs, Types, And Functions
The file provides `sdm660_dpu_caps`, `sdm660_mdp`, 5 CTLs, 5 SSPPs, 4 mixers, 2 DSPPs, 4 pingpongs, 2 DSC blocks, 3 interfaces, `sdm660_perf_data`, `sdm660_mdss_ver`, and `sdm660_dpu_cfg`. Interfaces are DP0, DSI0, and DSI1, all with 21 programmable-fetch lines.

### Control Flow
DPU probe selects `sdm660_dpu_cfg` and common resource code walks each static array. There are no functions or branches in the header itself. `max_bw_high = 6600000` and `min_prefill_lines = 25` shape performance admission.

### State, Persistence, And Dependencies
The catalog is read-only static state. It depends on shared DPU structs, feature masks, DSC descriptors, and MSM DP/DSI controller definitions. Runtime resource state is created outside the header.

### Integration Points
SDM660 resource data feeds atomic plane allocation, DP/DSI encoder setup, DSC routing, and bandwidth calculations. Version 3.2 lets common DPU code distinguish this mid-range layout from MSM8998 and SDM630.

### Risks
With only 5 SSPPs and 2 DSCs, complex split/DSC modes must be rejected accurately. DP support on a mid-range target requires correct controller binding. Perf values close to MSM8998 should still reflect SDM660-specific interconnect limits.

### Test Signals
Validate DP0 and both DSI controllers, DSC on supported modes, resource exhaustion for too many planes, split display, vblank/CTL completion, and bandwidth/underrun behavior near 6.6M.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_2_sdm660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_3_sdm630.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_3_sdm630.h

### Purpose
`dpu_3_3_sdm630.h` describes the smaller SDM630 DPU 3.3 catalog. It supports source split, dim layer, idle PC, 3D merge capability, one DP output, one DSI output, and a reduced two-mixer topology.

### Important APIs, Types, And Functions
The header defines `sdm630_dpu_caps`, `sdm630_mdp`, 5 CTLs, 4 SSPPs, 2 mixers, 1 DSPP, 2 pingpongs, 2 interfaces, performance data, version data, and `sdm630_dpu_cfg`. Interfaces are DP0 and DSI0 with 21 programmable-fetch lines.

### Control Flow
The file is declarative. The DPU core reads `sdm630_dpu_cfg` during probe and constructs the matching resource pools. `max_bw_high = 4100000` and `min_prefill_lines = 25` limit atomic bandwidth decisions.

### State, Persistence, And Dependencies
All state is immutable catalog data. It depends on DPU catalog structs, sub-block descriptors, DPU IRQ constants, and MSM DP/DSI controller IDs.

### Integration Points
The catalog drives DRM plane allocation for a reduced SDM630 hardware block and exposes exactly DP0 and DSI0 output resources. It shares common DPU v3 code paths with SDM660/MSM8998 while reducing block counts.

### Risks
Resource-manager code must handle the mismatch between the advertised `has_3d_merge` capability and the absence of a local merge3d array in this file. Low bandwidth requires accurate mode rejection. Single DSI and DP routes must not be confused with SDM660's dual DSI topology.

### Test Signals
Probe resource counts, DP0 and DSI0 modes, rejection of unsupported DSI1/extra-plane paths, split-display constraints, bandwidth tests near 4.1M, and underrun/vblank interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_3_sdm630.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_0_sdm845.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_0_sdm845.h

### Purpose
This file defines the SDM845 DPU 4.0 catalog, a major shared baseline for later Qualcomm DPU descriptions. It supports source split, dim layer, idle PC, 3D merge capability, DSC, DP, dual DSI, and DP MST pairing.

### Important APIs, Types, And Functions
The header exports `sdm845_dpu_caps`, `sdm845_mdp`, 5 CTLs, 8 SSPPs, 4 mixers, 4 DSPPs, 4 pingpongs, 4 DSC blocks, 4 interfaces, `sdm845_perf_data`, `sdm845_mdss_ver`, and `sdm845_dpu_cfg`. Interfaces are DP0, DSI0, DSI1, and a paired DP0 MST interface with 24 programmable-fetch lines.

### Control Flow
No functions execute here. Probe and resource-manager code consume the static `dpu_mdss_cfg`, map block arrays, and use counts to expose DRM resources. Perf data sets `max_bw_high = 6800000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
Catalog data is static read-only state. Dependencies include shared DPU structs, SDM845 sub-block descriptors, feature masks, DPU IRQ macros, DSC data, and MSM DP/DSI controller IDs.

### Integration Points
Many later headers reuse SDM845 arrays, masks, or perf data, so this file is both a hardware catalog and a baseline dependency for related targets. It integrates with atomic resource assignment, DSC, DP MST, DSI encoders, and bandwidth voting.

### Risks
Because other catalogs reuse `sdm845_*` data, changes here can affect multiple SoCs. The paired DP MST interface must be interpreted correctly. Four DSC blocks must align with pingpong and mixer topology for split/compressed modes.

### Test Signals
Validate SDM845 probe counts, DP0 and DP MST, dual DSI, DSC modes, high-plane atomic tests, bandwidth near 6.8M, CTL/pingpong interrupts, and regression tests for any SoC reusing SDM845 arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_0_sdm845.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_1_sdm670.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_1_sdm670.h

### Purpose
`dpu_4_1_sdm670.h` defines the SDM670 DPU 4.1 catalog as a derivative of SDM845. It supplies SDM670-specific MDP, SSPP, mixer, DSPP, and DSC arrays while reusing SDM845 caps, CTLs, pingpongs, interfaces, and performance data.

### Important APIs, Types, And Functions
The file defines `sdm670_mdp`, `sdm670_sspp`, `sdm670_lm`, `sdm670_dspp`, `sdm670_dsc`, `sdm670_mdss_ver`, and `sdm670_dpu_cfg`. `sdm670_dpu_cfg` references `sdm845_dpu_caps`, `sdm845_ctl`, `sdm845_pp`, `sdm845_intf`, and `sdm845_perf_data`; local counts are 5 SSPPs, 4 mixers, 2 DSPPs, and 2 DSC blocks, with inherited 5 CTLs, 4 pingpongs, and 4 interfaces.

### Control Flow
The catalog is static data only. Probe uses the mixed local/inherited table pointers to instantiate SDM670 resources. Output interfaces and CTL/pingpong arrays follow the SDM845 layout even though plane/DSPP/DSC capacity is reduced.

### State, Persistence, And Dependencies
No mutable state exists. This header directly depends on symbols from the SDM845 catalog being visible in the same inclusion context, plus the shared DPU catalog structs and sub-block descriptors.

### Integration Points
The derivative catalog integrates SDM670 without duplicating unchanged SDM845 resources. This saves maintenance but ties SDM670 behavior to SDM845 definitions for caps, CTLs, pingpongs, output interfaces, and perf limits.

### Risks
The main risk is hidden coupling: SDM845 changes can alter SDM670. Reusing SDM845 interface data may over-advertise outputs if SDM670 routing differs. Resource-manager paths must handle inherited counts and local reduced DSC/DSPP counts consistently.

### Test Signals
Compile-order coverage is important because this file references SDM845 symbols. Runtime validation should check actual SDM670 output exposure, reduced plane/DSPP/DSC capacity, inherited DP/DSI/MST behavior, and bandwidth behavior from reused SDM845 perf data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_1_sdm670.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_0_sm8150.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_0_sm8150.h

### Purpose
This header defines the SM8150 DPU 5.0 catalog. It is a high-end mobile display topology with source split, dim/idle/3D merge features, 4096 max linewidth, DSC, merge3d, writeback, DP, dual DSI, and DP MST.

### Important APIs, Types, And Functions
The file exports `sm8150_dpu_caps`, `sm8150_mdp`, 6 CTLs, 8 SSPPs, 6 mixers, 4 DSPPs, 6 pingpongs, 3 merge-3D blocks, 4 DSC blocks, 1 WB block, 4 interfaces, performance data, version data, and `sm8150_dpu_cfg`.

### Control Flow
There is no executable code. DPU probe consumes `sm8150_dpu_cfg` and resource-manager code walks the block arrays. Interfaces are DP0, DSI0, DSI1, and paired DP0 MST, all with 24 programmable-fetch lines. Perf data sets `max_bw_high = 12800000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
All catalog state is constant. Dependencies include DPU catalog structures, shared masks/sub-blocks, WB/DSC descriptors, DPU IRQ macros, and MSM DP/DSI controller IDs.

### Integration Points
SM8150 integrates with atomic resource allocation for six mixers, compressed display paths through DSC/merge3d, writeback, and DP/DSI encoders. It is also a pattern for related SM8xxx DPU 5/6 catalogs.

### Risks
The six-mixer/four-DSC topology requires careful resource allocation for multi-pipe compressed modes. DP MST pairing uses the same controller ID as DP0. Bandwidth tuning at 12.8M must be validated for high-refresh modes.

### Test Signals
Validate probe counts, DP MST, dual DSI, DSC and merge3d allocation, writeback, high-plane atomic modes, CTL/pingpong interrupt delivery, and bandwidth/underrun behavior near 12.8M.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_0_sm8150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_1_sc8180x.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_1_sc8180x.h

### Purpose
`dpu_5_1_sc8180x.h` describes the SC8180X DPU 5.1 catalog, a multi-output laptop/tablet-oriented display block. It supports source split, dim/idle/3D merge, 4096 linewidth, DSC, writeback, dual DSI, and several DP interfaces.

### Important APIs, Types, And Functions
The header defines `sc8180x_dpu_caps`, `sc8180x_mdp`, 6 CTLs, 8 SSPPs, 6 mixers, 4 DSPPs, 6 pingpongs, 3 merge-3D blocks, 6 DSC blocks, 1 WB block, 6 interfaces, `sc8180x_perf_data`, version data, and `sc8180x_dpu_cfg`. Interfaces include DP0, DSI0, DSI1, a DP entry with controller ID 999, DP1, and DP2.

### Control Flow
The file is declarative. At probe, the DPU core uses the arrays to expose resources and encoder routes. All interface entries use 24 programmable-fetch lines. Perf data sets `max_bw_high = 9600000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
Catalog data is immutable. Dependencies are shared DPU descriptors, DSC/WB support, DPU IRQ macros, and MSM display controller IDs. The unusual controller ID 999 is a data dependency that consuming code must tolerate or intentionally ignore.

### Integration Points
SC8180X's six interfaces make this catalog important for multi-display DP routing. It integrates with DRM encoder creation, DSC allocation across six blocks, writeback, and bandwidth voting.

### Risks
The `controller_id = 999` entry is a prominent risk and likely represents a placeholder or special route; it must not create an invalid external controller binding. Multi-DP routing requires exact ID mapping. Six DSC blocks across six mixers need allocation validation for multi-monitor compressed modes.

### Test Signals
Probe should expose the intended DP/DSI outputs only, with special attention to the controller 999 entry. Exercise DP0/DP1/DP2, dual DSI, DSC on multiple outputs, writeback, bandwidth near 9.6M, and hotplug/modeset across simultaneous displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_1_sc8180x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_2_sm7150.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_2_sm7150.h

### Purpose
This file defines the SM7150 DPU 5.2 catalog. It is a mid-range DPU 5 family layout with source split, dim/idle/3D merge, DSC, writeback, DP, dual DSI, and paired DP MST.

### Important APIs, Types, And Functions
The header exports `sm7150_dpu_caps`, `sm7150_mdp`, 6 CTLs, 5 SSPPs, 4 mixers, 2 DSPPs, 4 pingpongs, 2 merge-3D blocks, 2 DSC blocks, 1 WB block, 4 interfaces, performance data, version data, and `sm7150_dpu_cfg`.

### Control Flow
No executable logic is present. Probe walks `sm7150_dpu_cfg` to create resource pools. Interfaces are DP0, DSI0, DSI1, and paired DP0 MST with 24 programmable-fetch lines. Perf data sets `max_bw_high = 7100000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
All data is static. Dependencies include common DPU structures, feature masks, DSC/WB descriptors, DPU IRQ macros, and MSM DP/DSI IDs.

### Integration Points
The catalog connects SM7150 hardware to atomic plane allocation, DSC/merge3d compressed display, writeback, DP/DSI encoder setup, and DPU performance voting.

### Risks
Only two DSC and merge3d blocks are available for four mixers, so split compressed modes must be constrained. Reusing DP0 for MST pairing requires correct encoder handling. Mid-range bandwidth limits can expose underruns if perf constants are too optimistic.

### Test Signals
Validate resource counts, DP0/MST, DSI0/DSI1, DSC allocation and rejection paths, writeback, high-plane modes, CTL interrupts, and bandwidth near 7.1M.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_2_sm7150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_3_sm6150.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_3_sm6150.h

### Purpose
`dpu_5_3_sm6150.h` describes the SM6150 DPU 5.3 catalog, a reduced DPU 5 family layout. It supports source split/dim/idle features, writeback, one DSI path, DP, and paired DP MST but omits local DSC resources.

### Important APIs, Types, And Functions
The catalog defines `sm6150_dpu_caps`, `sm6150_mdp`, 6 CTLs, 5 SSPPs, 3 mixers, 1 DSPP, 3 pingpongs, 1 WB block, 3 interfaces, `sm6150_perf_data`, `sm6150_mdss_ver`, and `sm6150_dpu_cfg`.

### Control Flow
The DPU core consumes the arrays at probe. Interfaces are DP0, DSI0, and paired DP0 MST with 24 programmable-fetch lines. Performance data sets `max_bw_high = 4800000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
The header is immutable catalog data. Dependencies include shared DPU structures, feature masks, writeback descriptors, DPU IRQs, and MSM DP/DSI controller IDs.

### Integration Points
SM6150's catalog integrates a lower-resource SoC into common DRM modeset, resource-manager, writeback, DP/DSI, and bandwidth code. The absence of DSC data should cause compressed-output requests to be rejected or routed elsewhere.

### Risks
The odd count of 3 mixers/pingpongs can expose assumptions that resources come in even pairs. DP MST pairing exists despite a reduced interface set. Missing DSC resources must not be implied by inherited capability names.

### Test Signals
Probe counts, DP0/MST, DSI0, writeback, rejection of DSC modes, three-mixer allocation behavior, bandwidth around 4.8M, and underrun/vblank interrupt checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_3_sm6150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_4_sm6125.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_4_sm6125.h

### Purpose
This header defines the SM6125 DPU 5.4 catalog, a compact DPU 5 display block. It supports source split/dim/idle features, writeback, one DP path, and one DSI path with low-to-mid bandwidth limits.

### Important APIs, Types, And Functions
The file provides `sm6125_dpu_caps`, `sm6125_mdp`, 6 CTLs, 3 SSPPs, 2 mixers, 1 DSPP, 2 pingpongs, 1 WB block, 2 interfaces, performance data, version data, and `sm6125_dpu_cfg`. Interfaces are DP0 and a DSI entry with controller ID 0, both with 24 programmable-fetch lines.

### Control Flow
The header has no runtime branches. Probe consumes the static arrays to create resource pools and output encoders. `max_bw_high = 4100000` and `min_prefill_lines = 24` guide bandwidth and latency calculations.

### State, Persistence, And Dependencies
All catalog state is read-only. Dependencies include DPU catalog structs, common feature masks/sub-blocks, WB support, and DP/DSI interface constants.

### Integration Points
The catalog integrates SM6125 with atomic plane allocation, a two-mixer display path, writeback support, DP/DSI encoder setup, and performance voting. It provides a smaller sibling to SM6150/SM7150 in the DPU 5 family.

### Risks
Only three SSPPs and no DSC make resource exhaustion common. The DSI controller is specified as raw `0` rather than `MSM_DSI_CONTROLLER_0`, which should be verified against consumer expectations. Six CTLs for a small topology may include unused/compatibility resources that need correct handling.

### Test Signals
Validate DP0 and DSI panel modes, writeback, resource exhaustion with multiple planes, rejection of DSC paths, bandwidth near 4.1M, and interrupt behavior for the advertised CTLs/pingpongs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_5_4_sm6125.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_0_sm8250.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_0_sm8250.h

### Purpose
`dpu_6_0_sm8250.h` defines the SM8250 DPU 6.0 catalog. It is a high-end DPU 6 topology with source split, dim/idle/3D merge, DSC, writeback, DP, dual DSI, and paired DP MST.

### Important APIs, Types, And Functions
The file exports `sm8250_dpu_caps`, `sm8250_mdp`, 6 CTLs, 8 SSPPs, 6 mixers, 4 DSPPs, 6 pingpongs, 3 merge-3D blocks, 4 DSC blocks, 1 WB block, 4 interfaces, performance data, version data, and `sm8250_dpu_cfg`.

### Control Flow
There is no executable control flow. The common DPU core consumes `sm8250_dpu_cfg` during probe. Interfaces are DP0, DSI0, DSI1, and paired DP0 MST with 24 programmable-fetch lines. Perf data sets `max_bw_high = 16600000` and `min_prefill_lines = 35`.

### State, Persistence, And Dependencies
All data is constant. Dependencies include DPU catalog structures, shared sub-block descriptors, DSC/WB data, IRQ macros, and MSM DP/DSI controller IDs.

### Integration Points
SM8250 integrates high-end resource allocation, DSC/merge3d compressed display, writeback, DP MST, DSI, and DPU bandwidth voting into the common DRM driver. Version 6.0 selects the proper hardware programming family.

### Risks
The transition from SM8150 to DPU 6.0 changes prefill from 24 to 35 and raises bandwidth; perf mistakes may cause underruns. Mixer/pingpong/merge3d/DSC relationships must be correct for split DSC modes. DP MST pairing needs explicit validation.

### Test Signals
Validate high-resolution DP/DSI modes, MST, DSC, writeback, resource counts, CTL/pingpong interrupts, bandwidth near 16.6M, and suspend/resume with idle PC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_0_sm8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_2_sc7180.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_2_sc7180.h

### Purpose
This header defines the SC7180 DPU 6.2 catalog, a compact display topology for a DP plus DSI system. It includes dim/idle features, writeback, and a limited two-mixer/two-pingpong resource set.

### Important APIs, Types, And Functions
It provides `sc7180_dpu_caps`, `sc7180_mdp`, 3 CTLs, 4 SSPPs, 2 mixers, 1 DSPP, 2 pingpongs, 2 interfaces, 1 WB block, performance data, version data, and `sc7180_dpu_cfg`. Interfaces are DP0 and DSI0 with 24 programmable-fetch lines.

### Control Flow
The DPU driver consumes the static catalog at probe. No code executes in the header. Performance data sets `max_bw_high = 6800000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
The header only stores immutable constants. Dependencies include DPU catalog definitions, writeback support, DPU IRQ macros, and MSM DP/DSI controller identifiers.

### Integration Points
SC7180 data feeds DRM plane allocation, DP/DSI encoder creation, writeback exposure, interrupt setup, and DPU bandwidth voting. It gives DPU 6 family handling a lower-resource ChromeOS/mobile-class target.

### Risks
Only three CTLs and two mixers limit complex display combinations; resource-manager rejection paths are important. The catalog lacks DSC, so compressed modes must not be exposed. Writeback must coexist with limited mixer/pingpong resources.

### Test Signals
Probe resource counts, DP0 and DSI0 modes, writeback, rejection of DSC and unsupported multi-output combinations, bandwidth near 6.8M, and suspend/resume with idle PC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_2_sc7180.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_3_sm6115.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_3_sm6115.h

### Purpose
`dpu_6_3_sm6115.h` describes the SM6115 DPU 6.3 catalog, a very small single-display DSI topology. It supports dim layer and idle PC with one CTL, two source pipes, one mixer, one DSPP, one pingpong, and one DSI interface.

### Important APIs, Types, And Functions
The file defines `sm6115_dpu_caps`, `sm6115_mdp`, `sm6115_ctl`, `sm6115_sspp`, `sm6115_lm`, `sm6115_dspp`, `sm6115_pp`, `sm6115_intf`, `sm6115_perf_data`, `sm6115_mdss_ver`, and `sm6115_dpu_cfg`. The single interface is DSI0 with 24 programmable-fetch lines.

### Control Flow
The catalog is static. Probe uses it to instantiate one display pipeline and no optional DSC/WB resources. `max_bw_high = 4000000` and `min_prefill_lines = 24` bound performance calculations.

### State, Persistence, And Dependencies
State is immutable catalog data. Dependencies include common DPU structures, DPU IRQ IDs, and MSM DSI controller constants.

### Integration Points
This catalog integrates low-end SM6115 hardware into the same DPU core as larger DPU 6 targets. It exercises single-resource code paths for CTL, mixer, DSPP, pingpong, and interface allocation.

### Risks
Single-resource catalogs expose assumptions that arrays have at least two entries or support split-display fallback. No DP, DSC, or WB resources should be advertised. Bandwidth headroom is limited, so prefill and interconnect votes matter.

### Test Signals
Validate single DSI panel probe, one-CTL modeset, rejection of unsupported outputs/features, resource exhaustion with multiple planes, bandwidth near 4.0M, underrun counters, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_3_sm6115.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_4_sm6350.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_4_sm6350.h

### Purpose
This header defines the SM6350 DPU 6.4 catalog. It is a compact DP plus DSI topology with source split, dim/idle features, one DSC block, writeback, and 35-line prefetch tuning.

### Important APIs, Types, And Functions
The file exports `sm6350_dpu_caps`, `sm6350_mdp`, 4 CTLs, 4 SSPPs, 2 mixers, 1 DSPP, 1 DSC block, 1 WB block, 2 interfaces, performance data, version data, and `sm6350_dpu_cfg`. Interfaces are DP0 and DSI0 with 35 programmable-fetch lines.

### Control Flow
There is no executable logic. DPU probe reads `sm6350_dpu_cfg` to create resources. Perf data sets `max_bw_high = 5100000` and `min_prefill_lines = 35`.

### State, Persistence, And Dependencies
All data is static and immutable. Dependencies include DPU catalog types, DSC/WB descriptors, DPU IRQ macros, and MSM DP/DSI controller IDs.

### Integration Points
SM6350 integrates DP, DSI, a single DSC encoder, writeback, and bandwidth voting into the DPU 6 resource manager. It is useful coverage for reduced DPU 6 targets with DSC present but limited.

### Risks
Only one DSC block limits compressed mode combinations and must be handled by resource allocation. The absence of a local pingpong count in the final config despite local display pipeline blocks should be validated against the actual table contents and consuming code expectations. The 35-line prefetch value differs from many smaller catalogs.

### Test Signals
Probe counts, DP0 and DSI0 modes, DSC on supported single-pipe modes, DSC rejection for unsupported split modes, writeback, bandwidth near 5.1M, and underrun/vblank interrupt checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_4_sm6350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_5_qcm2290.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_5_qcm2290.h

### Purpose
`dpu_6_5_qcm2290.h` describes the QCM2290 DPU 6.5 catalog, a very small DSI-only display controller. It supports dim layer and idle PC with a single display pipeline and low bandwidth.

### Important APIs, Types, And Functions
It defines `qcm2290_dpu_caps`, `qcm2290_mdp`, one CTL, two SSPPs, one mixer, one DSPP, one pingpong, one DSI interface, `qcm2290_perf_data`, version data, and `qcm2290_dpu_cfg`.

### Control Flow
The file is declarative. Probe uses `qcm2290_dpu_cfg` to instantiate the single DSI0 pipeline with 24 programmable-fetch lines. Perf data sets `max_bw_high = 2700000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
All state is constant catalog data. Dependencies include shared DPU structs, DPU IRQ macros, and MSM DSI controller IDs.

### Integration Points
The catalog integrates QCM2290 into DPU core probing, atomic plane allocation, DSI encoder creation, and performance voting. It exercises minimal DPU 6 resource paths similar to SM6115 but with a lower bandwidth ceiling.

### Risks
Single-pipeline assumptions must be explicit; extra outputs, DSC, WB, or split modes should not be exposed. Low bandwidth makes mode validation and prefill values sensitive. Shared code must tolerate one-element resource arrays.

### Test Signals
Validate single DSI panel operation, rejection of unsupported resources/features, bandwidth near 2.7M, underrun behavior, vblank/CTL interrupt delivery, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_5_qcm2290.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_9_sm6375.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_9_sm6375.h

### Purpose
This header defines the SM6375 DPU 6.9 catalog, a compact DSI-only display controller with one DSC block. It supports dim layer, idle PC, 2160 max linewidth, and a single display pipeline.

### Important APIs, Types, And Functions
The file exports `sm6375_dpu_caps`, `sm6375_mdp`, one CTL, two SSPPs, one mixer, one DSPP, one pingpong, one DSC block, one DSI interface, `sm6375_perf_data`, `sm6375_mdss_ver`, and `sm6375_dpu_cfg`.

### Control Flow
There is no executable control flow. Probe consumes `sm6375_dpu_cfg` and creates the DSI0 path with 24 programmable-fetch lines. Performance data sets `max_bw_high = 6200000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
The catalog is immutable. Dependencies include common DPU catalog structs, DSC descriptors, DPU IRQ macros, and MSM DSI controller IDs. Runtime DPU state is allocated from these constants during probe.

### Integration Points
SM6375 integrates a single-pipeline DPU 6.9 target with DSC into common DRM resource allocation, compressed display handling, DSI encoder setup, and bandwidth voting.

### Risks
One DSC block must be matched to the single DSI pipeline and not over-allocated. The single CTL/pingpong/mixer topology must reject split and multi-output modes. The 2160 linewidth cap should be checked against panel modes to avoid accepting unsupported widths.

### Test Signals
Validate DSI0 panel modes, DSC enablement on supported formats, rejection of unsupported split/multi-output modes, max-linewidth validation near 2160 pixels, bandwidth near 6.2M, and underrun/vblank interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_6_9_sm6375.h -->

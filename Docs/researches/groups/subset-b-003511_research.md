# subset-b-003511 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_ip_offset.h

## Purpose
`vega10_ip_offset.h` is a generated-style AMDGPU register-base map for Vega10-family ASIC IP blocks. It defines a shared two-dimensional `struct IP_BASE` layout and then publishes both static `IP_BASE` instances and matching preprocessor macros for instance/segment base addresses. Consumers use these constants to compose register offsets for NBIF/NBIO, display, media, graphics, memory hub, SDMA, SMU-adjacent, thermal, clock, fuse, and other IP blocks.

## Important APIs, Types, and Constants
The file exports `MAX_INSTANCE` as `5` and `MAX_SEGMENT` as `5`, then declares `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }` and `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; }`. The static base tables are marked `__maybe_unused`, which allows inclusion in register headers without forcing every translation unit to reference every table. Important base tables include `NBIF_BASE`, `NBIO_BASE`, `DCE_BASE`, `DCN_BASE`, `MP0_BASE`, `MP1_BASE`, `MP2_BASE`, `DF_BASE`, `UVD_BASE`, `VCN_BASE`, `DBGU_BASE`, `DBGU_NBIO_BASE`, `DBGU_IO_BASE`, `DFX_DAP_BASE`, `DFX_BASE`, `ISP_BASE`, `SYSTEMHUB_BASE`, `L2IMU_BASE`, `IOHC_BASE`, `ATHUB_BASE`, `VCE_BASE`, `GC_BASE`, `MMHUB_BASE`, `RSMU_BASE`, `HDP_BASE`, `OSSSYS_BASE`, `SDMA0_BASE`, `SDMA1_BASE`, `XDMA_BASE`, `UMC_BASE`, `THM_BASE`, `SMUIO_BASE`, `PWR_BASE`, `CLK_BASE`, and `FUSE_BASE`.

The macro block mirrors those tables as `IP_BASE__INSTn_SEGm` constants. Notable active base ranges include graphics at `GC_BASE__INST0_SEG0` `0x00002000` and segment 1 `0x0000A000`, memory hub at `0x0001A000`, SDMA0/SDMA1 at `0x00001260` and `0x00001460`, UVD/VCN at `0x00007800` and `0x00007E00`, VCE at `0x00007E00`/`0x00048800`, SMUIO/PWR/CLK/FUSE near `0x00016800` through `0x00017400`, and NBIO/NBIF segments spanning low, indirect, and high windows.

## Control Flow and State
There is no executable control flow. The header is a pure compile-time data source. State is static, immutable, and embedded into object files only when referenced. Zeros represent absent instances or unused segments and are semantically meaningful because register access macros may index into the table.

## Dependencies and Integration Points
The table shape is shared with AMD register access code in the DRM driver and is normally included by ASIC register headers or IP-specific code. It depends on the compiler seeing `__maybe_unused` from kernel attributes. Integration is by symbol naming convention: downstream code expects names like `GC_BASE` or macros like `GC_BASE__INST0_SEG0` to match generated register definitions.

## Risks
The main risk is silent register misaddressing if a segment value, instance count, or macro name drifts from the hardware register database. The header duplicates data in static structs and macros, so edits must keep both forms consistent. Reusing this file for non-Vega10 ASICs is unsafe because many later families add segments or relocate blocks. The `MAX_INSTANCE`/`MAX_SEGMENT` sizes are part of the ABI expected by any table-indexing helper.

## Test Signals
Build coverage should include AMDGPU objects that include Vega10 register headers with warnings enabled, catching malformed initializers or missing attributes. Runtime signals are indirect: successful ASIC initialization, register reads from GFX/MMHUB/SDMA/SMUIO, power management bring-up, display/media block discovery, and absence of invalid MMIO accesses on Vega10 hardware. Diff-based validation against the AMD register database is the strongest unit-level signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega20_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega20_ip_offset.h

## Purpose
`vega20_ip_offset.h` provides the Vega20 ASIC IP-base offset map used by AMDGPU register definitions. It is structurally similar to the Vega10 map but expands the table dimensions to match Vega20's register segment layout and selected additional windows. It is consumed as read-only data for building MMIO offsets for power, graphics, display, media, memory, and fabric IPs.

## Important APIs, Types, and Constants
The header sets `MAX_INSTANCE` to `6` and `MAX_SEGMENT` to `6`, and defines the same `IP_BASE_INSTANCE` and `IP_BASE` table types used by other AMD generated offset headers. Static tables include `ATHUB_BASE`, `CLK_BASE`, `DCE_BASE`, `DF_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `SDMA0_BASE`, `SDMA1_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `UVD_BASE`, `VCE_BASE`, `XDMA_BASE`, and `RSMU_BASE`.

The macro block exposes every instance/segment cell as `*_BASE__INSTn_SEGm`. Important non-zero offsets include `CLK_BASE` six segments from `0x00016C00` through `0x0001B200`, `GC_BASE` at `0x00002000` and `0x0000A000`, `MMHUB_BASE` at `0x0001A000`, `SDMA0_BASE` at `0x00001260`, `SDMA1_BASE` at `0x00001860`, `SMUIO_BASE` at `0x00016800`/`0x00016A00`, `UVD_BASE` including an instance 1 segment at `0x00009000`, `VCE_BASE__INST0_SEG0` at `0x00008800`, and `RSMU_BASE` at `0x00012000`.

## Control Flow and State
The file contains no functions or runtime branches. All state is compile-time constant address data. The table initializer order is the only "flow": downstream macros index by IP, instance, and segment to derive a final register address. Zero-filled cells mark unavailable windows and must not be interpreted as valid block bases unless the corresponding hardware really maps at zero.

## Dependencies and Integration Points
The header integrates with AMDGPU ASIC register include files and code paths that select Vega20 offsets by including this header. It depends on Linux kernel C types/attributes being available in the including translation unit. It also integrates with driver code that expects VCE/UVD, NBIO, SMUIO, clock, and data-fabric base names to exist consistently across ASIC families.

## Risks
Because this file defines hardware addresses, incorrect constants can cause invalid MMIO, failed firmware handshakes, power-management failures, or misleading debug output. Vega20 differs from Vega10 in segment count and some block bases, so copy/paste between the two files is high risk. The apparent VCE initializer comment and macro value should be treated carefully during updates because comments and macro values must match the generated hardware source of truth.

## Test Signals
Compile tests should catch struct-dimension mismatches and duplicate/missing symbols. Hardware validation should exercise boot, SMU communication, SDMA engines, UVD/VCE media init, clock/fuse/thermal reads, and register dumps on Vega20 boards. Automated comparison against the generated register database should verify that the static `IP_BASE` tables and `*_BASE__INST*_SEG*` macros are identical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega20_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vi_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vi_structs.h

## Purpose
`vi_structs.h` defines binary queue and preemption metadata layouts for VI-era AMDGPU engines. The structures describe SDMA MQDs, compute MQDs, MQD allocation backing storage, CE/DE indirect-buffer save state, chained-IB variants, and 4 KiB graphics metadata pages. These definitions are hardware-facing ABI layouts rather than general-purpose in-memory models.

## Important APIs, Types, and Structures
`struct vi_sdma_mqd` maps SDMA ring and IB state fields such as ring base, read/write pointers, polling addresses, IB base/size, skip/context status, doorbell, and virtual address. Most of the 128 dwords are reserved to preserve hardware layout, with the final two repurposed for driver-internal `sdma_engine_id` and `sdma_queue_id`.

`struct vi_mqd` is the large compute queue descriptor. It includes compute dispatch dimensions, program/TBA/TMA addresses, resource limits, static thread-management masks, restart and wave-restore fields, user data registers, counters and timestamps, GDS/context-save state, HQD queue controls, EOP and context-save controls, IQ timer packet storage, resource packet storage, doorbell IDs, and a trailing `reserved_t[256]`. `struct vi_mqd_allocation` wraps a `vi_mqd` with `wptr_poll_mem`, `rptr_report_mem`, `dynamic_cu_mask`, and `dynamic_rb_mask` backing slots.

The graphics metadata section defines CE and DE IB state payloads (`vi_ce_ib_state`, `vi_de_ib_state`) plus chained-IB variants. `vi_gfx_meta_data` and `vi_gfx_meta_data_chained_ib` combine these payloads with alignment padding and saved PFP IB base fields into fixed 4 KiB layouts.

## Control Flow and State
There is no executable control flow. The state behavior is entirely structural: the driver writes these fields into memory shared with GPU command processors and SDMA engines, and hardware or firmware reads/writes them during queue execution, context save/restore, and preemption. Reserved fields are persistent padding and must retain layout positions even if not actively interpreted by the driver.

## Dependencies and Integration Points
The header depends on fixed-width `uint32_t` definitions from the including kernel environment. Integration points are AMDGPU gfx/compute queue setup, SDMA queue initialization, KFD/compute scheduling, context save/restore, preemption, and IB chaining logic. Any code allocating these objects must satisfy documented alignment requirements, especially 4 KiB for CE metadata and 64-byte alignment for DE payloads inside the metadata page.

## Risks
The primary risk is ABI drift: reordering, resizing, or changing types breaks the hardware-visible descriptor format. The file intentionally includes many reserved dwords, so cleanup refactors are dangerous. The field name `cp_mqd_connect_endvi_sdma_mqd_pq_wptr` appears unusual and should not be "fixed" without confirming generated source compatibility. Endianness, packing, and alignment assumptions matter because these structures are consumed by GPU hardware, not just C code.

## Test Signals
Compile-time signals include `sizeof`/offset assertions in any queue code that uses these structs. Runtime signals include successful SDMA ring bring-up, compute queue creation, dispatch, preemption, context save/restore, chained IB execution, and KFD workloads on VI ASICs. Hardware tests should include queue reset and recovery paths because MQD layout mistakes often surface during resume, preemption, or fault handling rather than simple dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vi_structs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/yellow_carp_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/yellow_carp_offset.h

## Purpose
`yellow_carp_offset.h` is the AMDGPU register-base map for Yellow Carp APUs. It defines generated IP base tables and matching macros for a more integrated SoC layout than the Vega discrete GPU headers, including ACP, FCH, PCIE, IOHC, DCN/DPCS, VCN, UMC, SMUIO, and multiple fabric or SoC register windows.

## Important APIs, Types, and Constants
The header defines `MAX_INSTANCE` as `7` and `MAX_SEGMENT` as `6`, then declares `IP_BASE_INSTANCE` and `IP_BASE`. Static tables include `ACP_BASE`, `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO_BASE`, `DCN_BASE`, `DPCS_BASE`, `DF_BASE`, `FCH_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `IOHC0_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `MP2_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `PCIE_BASE`, `SDMA0_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and `VCN_BASE`.

The macro block provides all `*_BASE__INSTn_SEGm` constants. Notable SoC/APU-specific bases include ACP at `0x02403800` and `0x00480000`, ATHUB windows at `0x00000C00`, `0x00013300`, and `0x02408C00`, DCN/DPCS at legacy display offsets plus `0x00009000` and `0x02403C00`, DF spanning `0x00007000`, `0x0240B800`, `0x02447800`, `0x00C00000`, and `0x03640000`, FCH at `0x0240C000`, `0x00B40000`, and `0x11000000`, GC/SDMA0 sharing visible bases at `0x00001260`, `0x0000A000`, and `0x02402C00`, NBIO including `0x0241B000` and `0x04040000`, PCIE instances from `0x02411800`/`0x04440000` upward, and UMC instance 0/1 memory controller windows.

## Control Flow and State
This file has no runtime execution. It is static SoC address data used by register macros and low-level MMIO helpers. State is immutable after compilation. The many non-zero secondary segments reflect Yellow Carp's split register address spaces; consumers must select the correct segment for the generated register definition.

## Dependencies and Integration Points
The header integrates with AMDGPU Yellow Carp register headers and ASIC initialization code. It is especially relevant to display core, multimedia, PCIe/NBIO, audio co-processor, power/thermal/SMU-facing registers, and memory-controller code. It relies on exact naming compatibility with generated register files.

## Risks
Yellow Carp has more active segment windows than older discrete GPU maps, increasing the risk of using the wrong segment or instance. Because GC and SDMA0 share listed segment bases, consumers must rely on the generated register definitions rather than assuming unique IP base ownership. A wrong SoC window can affect integrated platform devices beyond graphics, including FCH/PCIE/ACP. Edits should be generated from the hardware database, not hand-adjusted.

## Test Signals
Build tests should compile all Yellow Carp register consumers. Runtime signals include successful APU boot, display bring-up, VCN operation, SDMA operation, ACP visibility where enabled, PCIe/NBIO access, thermal/fuse/clock reads, and clean suspend/resume. Register-dump comparison against known Yellow Carp hardware is the most direct validation of offset correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/yellow_carp_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/Makefile

## Purpose
The PM `Makefile` wires AMDGPU power-management sources into the kernel build. It establishes include search paths for common AMD headers, SMU firmware interfaces, SW SMU generations, PowerPlay managers, and legacy DPM code, then includes the sub-Makefiles for the PM libraries and adds the top-level PM manager objects to `AMD_POWERPLAY_FILES`.

## Important Build Variables
`subdir-ccflags-y` appends include directories rooted at `$(FULL_AMD_PATH)`, covering `include/asic_reg`, `include`, `pm/inc`, `pm/swsmu`, `pm/swsmu/inc`, `pm/swsmu/inc/pmfw_if`, SMU generation folders `smu11` through `smu15`, PowerPlay include/SMU/HW manager folders, and `pm/legacy-dpm`. `AMD_PM_PATH` is `../pm`. `PM_LIBS` is `swsmu powerplay legacy-dpm`. `AMD_PM` expands those library paths to included Makefiles. `PM_MGR` lists `amdgpu_dpm.o`, `amdgpu_pm.o`, and `amdgpu_dpm_internal.o`, and `AMD_PM_POWER` prefixes them with `$(AMD_PM_PATH)`.

## Control Flow and State
Build control flow is declarative: include flags are accumulated, subordinate Makefiles are included through `include $(AMD_PM)`, and object names are appended to `AMD_POWERPLAY_FILES`. Persistent state is the Kbuild variable graph; no runtime state is created.

## Dependencies and Integration Points
This file depends on the parent AMDGPU build defining `FULL_AMD_PATH` and consuming `AMD_POWERPLAY_FILES`. It integrates the SW SMU, PowerPlay, and legacy DPM subtrees into a single power-management build surface. Source files in this directory rely on the include flags to find `hwmgr.h`, `amdgpu_smu.h`, PM firmware interfaces, and ASIC register headers.

## Risks
Include path ordering can affect which generation-specific headers are found. Adding a new SMU generation or PM subtree requires updating these flags and `PM_LIBS` consistently. Removing legacy paths can break older ASIC support. Because the file includes nested Makefiles, missing or misspelled paths can fail builds far from the edit location.

## Test Signals
The direct signal is a successful kernel or module build with AMDGPU PM enabled across configurations that include SW SMU, PowerPlay, and legacy DPM. Incremental build tests should verify that `amdgpu_dpm.o`, `amdgpu_pm.o`, and `amdgpu_dpm_internal.o` are included exactly once. Cross-ASIC build coverage is important because different PM subtrees consume different include directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm.c

## Purpose
`amdgpu_dpm.c` is the public AMDGPU dynamic power-management dispatch layer. It exposes driver-facing helpers for clocks, power gating, BACO and reset flows, power profiles, sensors, fan and power limits, display clock requests, metrics, overdrive, multimedia block enablement, and SMU-specific maintenance operations. Most functions validate support, lock `adev->pm.mutex`, call an operation from `adev->powerplay.pp_funcs` or a SW SMU helper, and translate unsupported paths into standard negative errno values.

## Important APIs and Functions
Clock and DPM state helpers include `amdgpu_dpm_get_sclk`, `amdgpu_dpm_get_mclk`, `amdgpu_dpm_compute_clocks`, `amdgpu_dpm_get_dpm_freq_range`, `amdgpu_dpm_set_soft_freq_range`, clock-level emit/force helpers, overdrive SCLK/MCLK getters/setters, and display clock functions such as `amdgpu_dpm_get_display_mode_validation_clks`, `amdgpu_dpm_set_watermarks_for_clocks_ranges`, `amdgpu_dpm_display_clock_voltage_request`, `amdgpu_dpm_set_min_deep_sleep_dcefclk`, hard-min DCEFCLK/FCLK setters, UCLK DPM state retrieval, and DPM clock table retrieval.

Power and reset APIs include `amdgpu_dpm_set_powergating_by_smu`, `amdgpu_dpm_set_gfx_power_up_by_imu`, BACO enter/exit/reset/capability functions, mode1/mode2/link reset support and execution, `amdgpu_dpm_set_mp1_state`, SDMA/VCN reset support and execution, XGMI/DF C-state setters, GFX state change notification, and multimedia enable wrappers for UVD, VCN, VCE, JPEG, and VPE. User and policy APIs include performance-level get/force, UMD state entry/exit, PM policy get/set, power profile switch/pause/get/set, ppfeature status, pp table get/set, and PowerPlay task dispatch.

Telemetry and controls include sensor read, APU thermal limit get/set, thermal throttling counter, ECC and RAS SMU driver access, GPU/PM/temp/XCP metrics, fan mode and speed controls, power limit get/set, overdrive support/enabled probes, CPU core count, SMU private buffer details, STB debugfs init, and debugfs performance-level printing.

## Control Flow and State
The dominant control flow is guarded dispatch. Functions first check feature support through `pp_funcs`, `is_support_sw_smu(adev)`, SR-IOV state, APU flags, `adev->scpm_enabled`, or device family. Supported paths take `adev->pm.mutex`, call the backend, release the mutex, and return the backend result. Unsupported legacy paths usually return `0`, `-EOPNOTSUPP`, `-ENOENT`, `-EINVAL`, or `-ENOSYS` depending on the interface contract.

Local state updates are narrow but important. `amdgpu_dpm_set_powergating_by_smu` tracks per-IP power state in `adev->pm.pwr_state`. `amdgpu_dpm_set_mp1_state` disables DPM for SR-IOV VFs on FLR. ACPI events update `adev->pm.ac_power` and notify BAPM/SW SMU AC-DC state. SI-family UVD/VCE enable paths update `adev->pm.dpm.uvd_active`, `vce_active`, `vce_level`, and power state before recomputing clocks. Forced performance-level changes update `adev->pm.dpm.forced_level` and may gate or ungate GFX around UMD profile modes. `amdgpu_dpm_set_power_state` stores the user-selected PM state for non-SW-SMU legacy dispatch.

## Dependencies and Integration Points
The file includes core AMDGPU headers, AtomBIOS, I2C, display, PowerPlay `hwmgr.h`, Linux power supply APIs, and SW SMU helpers. It integrates with `struct amd_pm_funcs` backends, `struct smu_context`, DRM display mode state, AMDGPU rings and fences, SR-IOV handling, reset paths, debugfs, sysfs-facing PM controls, multimedia IP power management, and RAS. `amdgpu_dpm_compute_clocks` also waits for ready rings to drain before invoking backend clock recomputation.

## Risks
The biggest risk is backend contract mismatch: many wrappers assume `adev->powerplay.pp_funcs` and `pp_handle` are valid, and some call members without checking the top-level `pp_funcs` pointer. Locking must remain consistent because these operations touch firmware, MMIO, and shared PM state. Some helpers return success when unsupported while others return an error, so callers must preserve existing semantics. Power-gating cache logic is special for multi-instance VCN and could incorrectly skip operations if generalized. UMD profile transitions must undo GFX gate changes if backend forcing fails. SR-IOV, S3/BACO, APU, and legacy SI paths all have explicit exceptions that are easy to regress.

## Test Signals
Build with AMDGPU PM enabled and exercise sysfs/debugfs PM controls. Runtime tests should cover SW SMU and legacy PowerPlay ASICs, SR-IOV VF behavior, BACO and mode1/mode2/link resets, UVD/VCN/VCE/JPEG/VPE power gating, AC/DC power supply events, display reconfiguration and watermark updates, overdrive table read/write where supported, fan and power-limit controls, sensor/metrics reads, and suspend/resume. Lockdep and fault-injection around backend failures are valuable because most code paths are lock-wrapped firmware dispatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm_internal.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm_internal.c

## Purpose
`amdgpu_dpm_internal.c` contains an internal helper, `amdgpu_dpm_get_display_cfg`, that snapshots active DRM display configuration into `adev->pm.pm_display_cfg` for use by PM backends. It derives active display count, pixel clocks, minimum vblank time, first active refresh rate, selected CRTC index, line time, and default display clock.

## Important APIs and Data
The sole exported function in this file is `amdgpu_dpm_get_display_cfg(struct amdgpu_device *adev)`. It uses `adev_to_drm`, `struct amd_pp_display_configuration`, `struct single_display_configuration`, DRM CRTC lists, `struct amdgpu_crtc`, and `struct amdgpu_connector`. It writes `cfg->min_vblank_time`, `cfg->vrefresh`, `cfg->crtc_index`, `cfg->line_time_in_us`, per-display `controller_id` and `pixel_clock`, `cfg->display_clk`, and `cfg->num_display`.

## Control Flow and State
The helper initializes `min_vblank_time` to `0xffffffff`, then only scans CRTCs when CRTC support exists and mode configuration has been initialized. It skips disabled CRTCs, converts each active DRM CRTC to AMDGPU types, records one display entry, and computes refresh/vblank timing when `hw_mode.clock` is non-zero. For refresh rates above 120 Hz on the legacy non-DC path, it forces `vblank_time_us` to zero to disable memory-clock switching. It tracks the lowest vblank time and first active refresh rate, selects the lowest CRTC id as `crtc_index`, records its line time, and finally stores the default display clock and active display count.

The function mutates only `adev->pm.pm_display_cfg`. It does not take `adev->pm.mutex` or DRM mode locks itself, so callers must invoke it from a context where display state is stable enough for PM consumption.

## Dependencies and Integration Points
Includes cover core AMDGPU, display, PowerPlay manager, SW SMU, and the internal DPM header. The function integrates display mode state with PM clock-selection logic, especially memory-clock switching decisions and backend display-configuration-change hooks. It depends on active CRTCs having a valid `connector` pointer and usable `pixelclock_for_modeset`.

## Risks
The active-display array is filled by incrementing `num_crtcs`; safety depends on the array being sized for the maximum possible active displays. Missing locking can be risky if callers use it during concurrent modeset changes. The high-refresh workaround intentionally disables mclk switching above 120 Hz on legacy paths; removing it could reintroduce display instability. Calculating vblank time from mode totals assumes sane mode fields and non-zero clock.

## Test Signals
Useful tests include display hotplug and modeset changes, multiple active CRTCs, high-refresh modes above 120 Hz, zero-clock or disabled CRTC cases, suspend/resume, and PM clock changes after display reconfiguration. Runtime validation should inspect `pm_display_cfg` consumers for correct display count, min vblank, refresh, CRTC index, line time, and pixel clock values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm_internal.c -->

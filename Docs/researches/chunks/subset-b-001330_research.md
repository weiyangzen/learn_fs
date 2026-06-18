# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c lines 1-3706

## Scope And Purpose

This chunk is the front matter and hardware-configuration base of the AMDGPU GFX10 IP implementation. It covers the include set, local register aliases, firmware declarations, debug register lists, golden register-setting tables, shader-memory defaults, and forward declarations for functions implemented later in `gfx_v10_0.c`.

The covered range does not contain the main executable function bodies for GFX10 bring-up, ring operation, reset, power management, or interrupt handling. Instead, it provides the static data and declarations those later functions depend on. The final per-file report should merge this chunk with later chunks before describing full initialization, suspend/resume, ring emit, compute queue, RLC, and power-gating behavior.

At a high level, the data here supports several generations and ASIC families in the GFX10 line: Navi10/Navi12/Navi14, Sienna Cichlid and related GC 10.3 parts, Vangogh, Dimgrey Cavefish, Beige Goby, Yellow Carp, Cyan Skillfish, and GC 10.3.6/10.3.7. The large golden-setting tables encode ASIC-specific register masks and values that later initialization paths apply through SOC15 register helpers.

## Important APIs, Types, And Tables

The file depends on AMDGPU and SOC15 driver infrastructure through `amdgpu.h`, `amdgpu_gfx.h`, `amdgpu_psp.h`, `soc15.h`, `soc15_common.h`, `gfx_v10_0.h`, generated GC/SMUIO offset and mask headers, Navi enums, and GFX IRQ source IDs. Those headers provide the important local types used in this chunk: `struct amdgpu_device`, `struct amdgpu_ring`, `struct amdgpu_ip_block`, `struct amdgpu_cu_info`, `struct amdgpu_hwip_reg_entry`, `struct soc15_reg_golden`, and SOC15 register accessor/encoding macros.

The local register `#define`s fill gaps or provide ASIC-specific aliases for registers and fields not coming directly from the generated headers. Examples include Sienna Cichlid-specific RLC, SPI, VGT, GCR, doorbell, throttle, and TCC-disable registers; Vangogh-specific VGT/SPI/GCR/TSC locations; hypervisor CP microcode loading registers; PSP debug GPA override bits; shader-array disable masks; PBB mode control bits; and GC 10.3.6 TSC register locations.

`MODULE_FIRMWARE()` entries declare the firmware blobs this driver may request at runtime. The chunk covers CE, PFP, ME, MEC, MEC2, and RLC firmware for Navi10, Navi12, Navi14 including workstation Navi14 variants, Sienna Cichlid, Navy Flounder, Vangogh, Dimgrey Cavefish, Beige Goby, Yellow Carp, Cyan Skillfish 2, GC 10.3.6, and GC 10.3.7. These declarations affect kernel module firmware dependency metadata; actual selection and loading occur later through firmware initialization code.

`gc_reg_list_10_1[]` is the general GFX debug snapshot list. It names GRBM status registers, CP stalled/busy/status registers, ring buffer registers, IB base/size registers, UTCL1/UTCL0 status registers, GDS protection-fault registers, GCVM L2 fault registers, CP instruction pointers, RLC/SMU registers, RLC debug registers, MES header dump, and per-SE GRBM status registers.

`gc_cp_reg_list_10[]` is the compute queue/HQD debug list. It covers HQD VMID, persistent state, priority, quantum, PQ base/read/write/poll/doorbell/control fields, IB state, dequeue request/status, EOP state, context-save state, GDS resource state, error, and repeated MEC header-dump entries.

`gc_gfx_queue_reg_list_10[]` is the graphics queue debug list. It covers GFX HQD active/priority/base/offset/read/write/dequeue/mapped/manager/control/status fields, CE poll/offset/read/write fields, MQD base, RB write-pointer poll addresses, and repeated CE/PFP/ME header dump entries.

The golden-setting arrays are `static const struct soc15_reg_golden` tables. Each entry is a register, mask, and programmed value consumed later by common SOC15 golden-register programming helpers. Covered regular GC tables include `golden_settings_gc_10_1`, `golden_settings_gc_10_1_1`, `golden_settings_gc_10_1_2`, `golden_settings_gc_10_3`, `golden_settings_gc_10_3_2`, `golden_settings_gc_10_3_vangogh`, `golden_settings_gc_10_3_3`, `golden_settings_gc_10_3_4`, `golden_settings_gc_10_3_5`, `golden_settings_gc_10_0_cyan_skillfish`, `golden_settings_gc_10_3_6`, and `golden_settings_gc_10_3_7`. Empty placeholder tables are present for `golden_settings_gc_10_0_nv10`, `golden_settings_gc_10_1_nv14`, `golden_settings_gc_10_1_2_nv12`, and `golden_settings_gc_10_3_sienna_cichlid`.

The large RLC SPM golden tables are `golden_settings_gc_rlc_spm_10_0_nv10`, `golden_settings_gc_rlc_spm_10_1_nv14`, and `golden_settings_gc_rlc_spm_10_1_2_nv12`. These tables repeatedly program `mmGRBM_GFX_INDEX` to select broadcast or per-shader-engine contexts, then write RLC SPM global and per-SE sample-delay, mux-select, sample-skew, mux-skew, and deserializer-start-skew registers. They are long because each counter/mux lane gets explicit calibration values and selected SEs are addressed separately.

`DEFAULT_SH_MEM_CONFIG` defines the default shader memory mode later used for compute/graphics queue setup: 64-bit addressing, unaligned alignment mode, all retry mode, and an initial instruction prefetch value of `3`. `CYAN_SKILLFISH_GB_ADDR_CONFIG_GOLDEN` is a temporary hard-coded GB address config value with a TODO noting that the golden value is pending.

The forward declarations at the end expose the major implementation areas that later chunks define: ring/IRQ/GDS/RLC/MQD function-table setup, CU discovery, clock counter reads, SE/SH selection, active WGP bitmap discovery, RLC backdoor autoload buffer lifecycle and enable/wait paths, CE/DE/frame-control packet emission, disabled shader-array discovery, PBB mode programming, power brake sequencing, TLB invalidation, SPM VMID update, and power-gating state changes.

## Control Flow And Runtime Use

There is very little runtime control flow in this chunk. The active behavior is compile-time and link-time setup:

1. Kernel and AMDGPU headers provide register definitions, bitfield macros, firmware APIs, SOC15 helpers, and local driver types.
2. `MODULE_FIRMWARE()` statements make firmware names visible to the kernel build/module metadata.
3. Static register lists and golden-setting tables are compiled into read-only data.
4. Later functions, outside this chunk, select the appropriate table according to `adev->asic_type`, IP version, or family-specific conditions and apply entries through SOC15 masked-register writes.
5. Debug and reset paths later reference the `amdgpu_hwip_reg_entry` lists to collect hardware state for diagnostics.

The regular golden tables configure clocks, cache/GL2 behavior, shader and geometry frontend settings, DB/PA/SPI/SQ/TA/TCP/UTCL1 controls, performance counter select defaults, and known workaround registers. Some entries are explicitly documented as hang fixes, such as `mmLDS_CONFIG` workarounds for Navy Flounder and Vangogh.

The RLC SPM tables are ordered register-programming scripts. Their repeated `mmGRBM_GFX_INDEX` writes matter because following indirect RLC SPM writes target global broadcast, SE0, SE1, or all-SE contexts depending on the selected value. A later consumer must preserve ordering; these are not independent key-value settings that can be freely sorted.

The declarations near lines 3677-3706 signal the subsequent control-flow areas but do not define them in this chunk. For example, RLC autoload buffer initialization and `gfx_v10_0_wait_for_rlc_autoload_complete()` are declared here, but allocation, polling, timeout, and error handling are in later code.

## State And Persistence Behavior

All tables and constants in this chunk are static driver data. They live in the kernel module or built-in kernel image, are read-only after load, and have no direct allocation, I/O, locking, or persistence side effects.

Firmware declarations are persistent only as module metadata and as build/runtime dependency hints. They do not load firmware by themselves. Later firmware loading state will reside in `adev` and related firmware/RLC/CP structures.

The golden tables encode persistent hardware policy for each supported ASIC family. Applying them later mutates device registers, not the tables. Because hardware registers retain values only while powered/reset state allows, these settings must be reapplied during initialization and relevant resume/reset paths by code outside this chunk.

The debug register lists also do not store snapshots. They describe what later diagnostic paths should read. Captured values, if any, are stored by the caller or emitted through driver diagnostics elsewhere.

`DEFAULT_SH_MEM_CONFIG` and the shader-array/PBB/register field macros are stateless compile-time constants. Their persistence risk is semantic: changing them changes the default state later programmed into queue or graphics hardware.

## Dependencies And Integration Points

This chunk is tightly coupled to generated register headers under `gc/`, `smuio/`, and `ivsrcid/gfx/`. The register names, offsets, base indices, masks, and shifts must match the GFX10 hardware generation. Several locally defined aliases exist because the generated headers are incomplete or because ASIC-specific offsets differ from the base GC 10.1 definitions.

The SOC15 integration point is central. `SOC15_REG_ENTRY_STR()` converts register names into debug-readable hardware IP register descriptors. `SOC15_REG_GOLDEN_VALUE()` converts register/mask/value triples into golden-setting data consumed by shared SOC15 code.

The firmware integration point is Linux firmware loading via AMDGPU. Later code chooses blob prefixes and requests the files declared in this chunk. Mismatches between `MODULE_FIRMWARE()` declarations and actual runtime firmware names can cause missing firmware packaging or request failures.

The debug integration point is AMDGPU device-state capture. The three `amdgpu_hwip_reg_entry` lists are intended for general GC, compute queue, and graphics queue diagnostics. They include repeated header-dump registers because repeated reads can expose successive dump words through the same register address.

The hardware bring-up integration point is later GFX10 initialization code, which selects golden settings by ASIC. Tables for Navi10/Navi14/Navi12 and GC 10.3 variants must align with the ASIC switch logic outside this chunk. Placeholder empty tables indicate that some ASIC-specific golden programming was pending or intentionally delegated to other table combinations.

The RLC SPM tables integrate with RLC performance monitoring, SPM sampling, and shader-engine selection. Their use depends on `GRBM_GFX_INDEX` selection semantics and RLC SPM indirect address/data register behavior.

The forward-declared functions integrate with the broader AMDGPU IP-block model: ring function tables for scheduler/ring operations, IRQ callbacks, GDS initialization, RLC function hooks, MQD programming, CU-info reporting, power management, VM/TLB invalidation, and IP-block power-gating callbacks.

## Risks And Edge Cases

The biggest risk in this chunk is table drift. Golden settings are hardware workarounds and tuning values; changing a mask or value can cause hangs, degraded performance, bad cache behavior, broken shader/geometry behavior, or regressions limited to a single ASIC family.

The RLC SPM tables are especially fragile because ordering is meaningful. Reordering entries around `mmGRBM_GFX_INDEX`, dropping a broadcast reset, or using an incorrect SE selector can silently program the wrong shader engine or leave calibration asymmetric.

Locally defined register offsets can diverge from generated headers or hardware documentation. They are useful when generated headers lag, but they bypass the stronger consistency provided by generated register metadata.

Firmware declarations must track runtime firmware naming exactly. A new ASIC table without matching firmware declarations, or renamed firmware without updating `MODULE_FIRMWARE()`, can break distribution packaging even if the source compiles.

Placeholder golden-setting arrays are easy to misinterpret. Empty tables such as `golden_settings_gc_10_0_nv10` or `golden_settings_gc_10_3_sienna_cichlid` do not mean the ASIC needs no programming; later selection logic may combine common tables, rely on firmware, or still need future fill-in.

Debug register lists contain repeated entries for header-dump registers and one apparent duplicate `mmCP_RB2_WPTR`. These may be intentional for successive readback semantics, but generic duplicate-removal refactors would be risky without checking the hardware read behavior.

The chunk uses ASIC names in symbol names, including mixed-case `Sienna_Cichlid` local register names. Style-only normalization could break references or obscure which values are ASIC-specific overrides.

The forward declarations create dependency pressure between later code sections. Signature changes must update declarations and all function-table assignments consistently, especially for callbacks like power-gating state changes and TLB invalidation packet emission.

## Test Signals

Build coverage should compile this file with the relevant AMDGPU configuration enabled and with warnings treated seriously enough to catch stale forward declarations, missing register symbols, or invalid firmware macro use.

ASIC-specific smoke tests should boot or initialize representative GFX10 devices: Navi10, Navi12, Navi14, Sienna Cichlid/Navy Flounder class GC 10.3 parts, Vangogh, Cyan Skillfish, and GC 10.3.6/10.3.7 if available. The expected signal is successful firmware load, GFX IP bring-up, ring test, and no early GPU hang.

Golden-setting validation should compare applied register writes against expected masks and values for each selected ASIC path. This is most valuable around `mmLDS_CONFIG`, `mmGB_ADDR_CONFIG`, GL2 address masks, clock-gating controls, `mmSQ_CONFIG`, and Vangogh/Sienna-specific aliases.

RLC SPM validation should confirm that later code applies the RLC SPM tables in order and that SPM sampling works per shader engine. Failures may show as bad counter data rather than immediate boot failure.

Debug-dump tests should exercise GPU reset/hang capture paths and verify the general GC, compute HQD, and graphics queue register lists produce sane output without invalid register access on supported ASICs.

Firmware packaging tests should verify every declared firmware name exists in the target firmware package or is intentionally optional for the built kernel/device matrix.

Power-management and reset tests should include suspend/resume, runtime power transitions, GPU reset, and power-gating toggles, because the static golden settings from this chunk must be replayed correctly by later runtime paths after hardware loses state.

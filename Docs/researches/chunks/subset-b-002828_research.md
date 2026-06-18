# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 9628-9790

## Scope And Purpose

This chunk is the closing range of the generated AMDGPU MMHUB 9.1 shift/mask header. It finishes the `UTCL2_CGTT_CLK_CTRL` mask definitions, defines the shared PF and virtual-channel VM aperture fields, defines the L1 TLB control fields, defines ATC L2 performance-counter fields, and ends the include guard. The source file is declarative hardware metadata: it contains preprocessor constants only, with no C functions, structs, variables, branches, loops, allocation, locking, or direct MMIO access.

The effective purpose is to provide bit-accurate field locations for SOC15 MMHUB 9.1 registers. Consumers pair these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching register offsets from `mmhub_9_1_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

Although this repository path is under a local Ceph client source import, this file belongs to the Linux AMDGPU DRM hardware interface. It has no Ceph filesystem behavior.

## Important APIs, Types, And Register Families

There are no callable APIs or local types in this chunk. The public surface is the macro namespace for the following register groups:

- `UTCL2_CGTT_CLK_CTRL`: clock-gating timing and override fields for the UTCL2 block. The chunk contains masks for `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE_EXTRA`, `MGLS_OVERRIDE`, `SOFT_STALL_OVERRIDE`, and `SOFT_OVERRIDE`; the matching shifts start just before this chunk and are visible in nearby context.
- `MC_VM_NB_MMIOBASE` and `MC_VM_NB_MMIOLIMIT`: full-width MMIO aperture base/limit fields for the shared PF decoder.
- `MC_VM_NB_PCI_CTRL` and `MC_VM_NB_PCI_ARB`: PCI-side enable and VGA-hole fields. `MMIOENABLE` lives at bit 23, and `VGA_HOLE` at bit 3.
- `MC_VM_NB_TOP_OF_DRAM_SLOT1`, `MC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MC_VM_NB_UPPER_TOP_OF_DRAM2`: top-of-memory registers for DRAM slot/TOM2 layout. `LOWER_TOP_OF_DRAM2` includes an enable bit plus a high-address field.
- `MC_VM_FB_OFFSET`: 24-bit framebuffer offset field.
- `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB` and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_MSB`: default physical page address fields used when aperture handling redirects to a default page.
- `MC_VM_STEERING`: two-bit default steering selector.
- `MC_SHARED_VIRT_RESET_REQ`: virtualization reset request bitmap, with 16 VF bits and a PF bit at bit 31.
- `MC_MEM_POWER_LS`: memory light-sleep setup and hold timing fields.
- `MC_VM_CACHEABLE_DRAM_ADDRESS_START` and `MC_VM_CACHEABLE_DRAM_ADDRESS_END`: cacheable DRAM range fields.
- `MC_VM_APT_CNTL`: aperture controls for forcing uncacheable memory type and enabling direct system access.
- `MC_VM_LOCAL_HBM_ADDRESS_START`, `MC_VM_LOCAL_HBM_ADDRESS_END`, and `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`: local HBM range and one-bit lock control.
- `MC_VM_FB_LOCATION_BASE` and `MC_VM_FB_LOCATION_TOP`: 24-bit framebuffer aperture base/top fields.
- `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, and `MC_VM_AGP_BASE`: 24-bit AGP aperture registers.
- `MC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`: 30-bit logical system-aperture low/high fields.
- `MC_VM_MX_L1_TLB_CNTL`: main L1 TLB control register, including `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, `MTYPE`, and `ATC_EN`.
- `ATC_L2_PERFCOUNTER_LO` and `ATC_L2_PERFCOUNTER_HI`: low/high performance-counter words. The high word also packs a 16-bit compare value.
- `ATC_L2_PERFCOUNTER0_CFG` and `ATC_L2_PERFCOUNTER1_CFG`: ATC L2 counter event-range, mode, enable, and clear controls.
- `ATC_L2_PERFCOUNTER_RSLT_CNTL`: counter result selection, start/stop trigger fields, enable-any, clear-all, and stop-on-saturate controls.

The companion offset chunk in `mmhub_9_1_offset.h` maps these same register names to offsets: `mmUTCL2_CGTT_CLK_CTRL` at `0x0808`, shared PF registers beginning at `mmMC_VM_NB_MMIOBASE` `0x0810`, shared VC registers beginning at `mmMC_VM_FB_LOCATION_BASE` `0x082c`, ATC L2 counter result registers at `0x0840` and `0x0841`, and ATC L2 counter controls at `0x0848` through `0x084a`.

## Control Flow And Runtime Use

This chunk has no local runtime control flow. All sequencing is in consumer code that includes the header and uses the constants during device initialization, VM/GART setup, power management, SR-IOV handling, debug, or performance-counter access.

The closest AMDGPU consumers in this tree show how these fields are expected to be used:

- `mmhub_v1_7.c` and `mmhub_v1_8.c` include generation-specific MMHUB headers with the same `MC_VM_*` macro names. Their `get_fb_location` paths read `regMC_VM_FB_LOCATION_BASE` and `regMC_VM_FB_LOCATION_TOP`, mask them with `MC_VM_FB_LOCATION_*__FB_*_MASK`, shift by 24, and store `adev->gmc.fb_start` / `adev->gmc.fb_end`.
- Their system-aperture setup writes `MC_VM_AGP_*`, `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, `MC_VM_FB_LOCATION_BASE`, `MC_VM_FB_LOCATION_TOP`, and default-address registers according to `adev->gmc` aperture state and whether `pdb0_bo` squeezes VRAM into the GART aperture.
- Their TLB setup reads `regMC_VM_MX_L1_TLB_CNTL`, uses `REG_SET_FIELD` with the `MC_VM_MX_L1_TLB_CNTL` masks from the included shift/mask header, enables the L1 TLB, selects system access mode 3, enables the advanced driver model, disables unmapped system-aperture access, programs `MTYPE`, and enables ATC. Disable paths clear `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`.
- `mmhub_v1_8.c` additionally handles multi-instance MMHUB programming through `adev->aid_mask`, and can route L1 TLB programming through PSP (`psp_reg_program_no_ring`) when SR-IOV requires indirect access.
- `vcn_v1_0.c` directly includes `mmhub/mmhub_9_1_offset.h` and `mmhub/mmhub_9_1_sh_mask.h`, making the MMHUB 9.1 register definitions visible to VCN 1.0 code and register checking infrastructure.

The version-selection path in `gmc_v9_0.c` routes MMHUB versions to concrete function tables. IP version `9.1.0` uses Raven client information and, for older MMHUB generations, falls back to the v1.0-style MMHUB implementation unless a newer explicit version is selected. The key integration point for this chunk is still the generated register namespace: any translation unit that includes the matching MMHUB 9.1 offset and shift/mask headers can compose these specific registers.

## State And Persistence Behavior

The header stores no software state. It describes fields in MMIO-backed GPU hardware registers. When consumer code writes these fields, values persist in MMHUB hardware until reset, power transition, firmware reinitialization, driver reprogramming, or another register writer changes them.

The state represented by this chunk includes:

- Physical and logical memory aperture state: NB MMIO base/limit, framebuffer aperture base/top, AGP aperture base/bottom/top, system aperture low/high, default physical page address, framebuffer offset, and cacheable/local memory ranges.
- Virtualization state: PF/VF reset request bits and SR-IOV-visible aperture controls. Callers must respect VF restrictions; related MMHUB setup code often returns early in SR-IOV VF mode for privileged aperture programming.
- Translation state: L1 TLB enablement, advanced driver model mode, ATC enablement, memory type selection, and unmapped-system-aperture behavior.
- Power-management state: UTCL2 clock-gating delay/override bits and memory light-sleep timing.
- Performance/debug state: ATC L2 counter values, counter compare value, event select range, mode, enable/clear controls, start/stop triggers, and global clear/stop-on-saturation controls.
- Lock state: `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL__LOCK` protects or freezes the programmed local HBM address range according to hardware semantics; this header only defines the bit, not the locking protocol.

The masks do not encode access permissions, side effects, reset values, or required ordering. Status/counter fields, clear bits, lock bits, and reset-request bits may be read-only, write-one-to-clear, self-clearing, sticky, privileged, or sequencing-sensitive depending on the hardware specification and firmware state.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU register-header convention:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h` provides the matching `mm*` register offsets and base indices for the registers described here.
- Consumer C files use SOC15 helpers from `soc15.h` / `soc15_common.h` plus AMDGPU register helpers to read/modify/write the fields.
- Generation-specific MMHUB implementations such as `mmhub_v1_7.c`, `mmhub_v1_8.c`, and older/newer MMHUB files show the common programming model for the same `MC_VM_*` and `ATC` field names, even when they include different generated headers.
- GMC initialization code owns broader routing: it initializes MMHUB client IDs, selects MMHUB function tables, drives GART enable/disable, and calls the selected MMHUB callbacks.
- VCN 1.0 includes the MMHUB 9.1 headers directly, so macro changes in this file can affect media-engine register-list or register-check compilation even if the main MMHUB setup path is elsewhere.

The chunk also mirrors names and layouts present in related generated GC/MMHUB 9.x headers, such as `gc_9_1_sh_mask.h`, but those should be treated as separate hardware contracts. Offsets, base indices, and prefixing differ between IP blocks and generations.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong mask or shift can silently program the wrong bits while compiling successfully.
- Aperture field widths vary: many address fields are 24-bit or 30-bit page/logical-address fields, while default-address LSB fields are full 32-bit and MSB fields are narrow. Callers must apply the same page shifts expected by hardware (`>> 12`, `>> 18`, `>> 24`, or high-address extraction in observed consumers) before using these masks.
- `MC_VM_FB_LOCATION_BASE/TOP`, AGP, and system-aperture fields control address decoding. Incorrect values can expose the wrong memory range, disable valid apertures, route accesses to the default page, or cause VM faults.
- `MC_VM_MX_L1_TLB_CNTL` packs several operational mode bits into one register. Read-modify-write is required so enabling `ATC_EN` or `ENABLE_L1_TLB` does not clobber `SYSTEM_ACCESS_MODE`, `MTYPE`, or ECO bits.
- `MC_SHARED_VIRT_RESET_REQ` can target VFs and PF state. Accidentally setting these bits in the wrong privilege context may reset virtual functions or affect PF-owned state.
- `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL` is a one-bit lock; once set, later writes to local HBM range fields may be ignored or require reset/firmware intervention depending on hardware behavior.
- Clock-gating override fields are not passive diagnostics. Forcing `SOFT_OVERRIDE`, `SOFT_STALL_OVERRIDE`, `MGLS_OVERRIDE`, or related UTCL2 controls can change power behavior and mask real idle/busy transitions.
- ATC L2 counter control has clear bits and global result controls. `CLEAR`, `CLEAR_ALL`, and stop-on-saturate operations can lose performance evidence if used by concurrent debug code.
- Macro names do not reveal access type. Full-width masks such as `0xFFFFFFFFL` and single-bit control masks have the same shape, so code review must rely on hardware docs and offset context, not naming alone.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are compile-time, static, and hardware-observation based:

- Build AMDGPU translation units that include `mmhub_9_1_sh_mask.h`, especially `vcn_v1_0.c`, to catch missing or renamed macros.
- Cross-check every register group in this chunk against `mmhub_9_1_offset.h` for a matching `mm*` offset and base index.
- Run static mask/shift checks: single-bit masks should match their shift, multi-bit masks should be contiguous, fields in each register should not overlap, and full-width fields should have shift zero.
- Compare the generated masks against the authoritative AMD MMHUB 9.1 register database, with special attention to address field widths, `MC_VM_MX_L1_TLB_CNTL__MTYPE_MASK` width, PF/VF reset bits, and ATC L2 counter clear/control semantics.
- On Raven/MMHUB 9.1 hardware or a simulator, inspect register dumps after GART/MMHUB initialization and after suspend/resume or GPU reset. Expected signals include correct FB/AGP/system aperture values, L1 TLB enabled during normal operation, and disabled/cleared VM context state during GART shutdown.
- For performance-counter users, validate that `ATC_L2_PERFCOUNTER*_CFG` enable/clear behavior, high/low counter reads, compare value, start/stop triggers, and stop-on-saturate behavior match the hardware specification.

## Chunk Notes For Merge Lane

This is the final chunk of `mmhub_9_1_sh_mask.h`; it closes the include guard after the ATC L2 performance-counter control definitions. The final per-file report should merge this with earlier chunks covering DAGB, VM context, VM L2, protection-fault, ATS, and other UTCL2 registers before making whole-file statements about all MMHUB 9.1 register families.

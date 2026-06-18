# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.c lines 9020-9807

## Scope

This chunk is the tail of the CIK Radeon driver source. It covers DCE8 display-watermark bandwidth math, the public `dce8_bandwidth_update()` mode/display update entry point, GPU clock counter sampling, UVD/VCE clock divider programming, PCIe gen2/gen3 link-speed enablement, and PCIe ASPM/power-down programming. The code is highly hardware-facing: most effects are register writes through Radeon MMIO, SMC, PCIe port, and PCI config helpers, with persistent state also cached in `struct radeon_crtc`.

## Purpose and Major Responsibilities

- Finish the DCE8 watermark model by computing display DMIF request bandwidth, available bandwidth, average display bandwidth, latency watermark, and latency-hiding feasibility from `struct dce8_wm_params`.
- Program per-CRTC display watermarks for high and low power states, using current/DPM-derived memory and shader clocks, display timings, line-buffer size, vertical scaling state, interlace state, and DRAM channel count.
- Expose `dce8_bandwidth_update()` as the CIK display bandwidth recalculation path. It counts enabled CRTCs, updates display priority, adjusts line buffers for each CRTC, and pushes watermarks into DPG registers.
- Expose `cik_get_gpu_clock_counter()` for synchronized 64-bit RLC GPU clock counter snapshots.
- Expose `cik_set_uvd_clocks()` and `cik_set_vce_clocks()` for video decode/encode clock divider updates using ATOM BIOS clock divider calculations and SMC clock-control/status registers.
- Configure PCIe link speed in `cik_pcie_gen3_enable()` when the platform and module parameters allow gen2/gen3 operation.
- Configure ASPM/link power management in `cik_program_aspm()` by programming link inactivity timers, PIF PLL power-down states, dynamic lane power state, CLKREQ-dependent deep-sleep clocks, and PCIe memory light-sleep bits.

## Important Functions and APIs

- `dce8_dmif_request_bandwidth(struct dce8_wm_params *wm)` converts display clock to a fixed-point GHz-ish unit, multiplies by a 32-byte request width and 0.8 efficiency, and returns MB/s for DMIF request capacity.
- `dce8_available_bandwidth(struct dce8_wm_params *wm)` returns the minimum of DRAM bandwidth, data-return bandwidth, and DMIF request bandwidth. It depends on earlier chunk helpers `dce8_dram_bandwidth()` and `dce8_data_return_bandwidth()`.
- `dce8_average_bandwidth(struct dce8_wm_params *wm)` calculates mode bandwidth from source width, bytes per pixel, vertical scale ratio, and line time.
- `dce8_latency_watermark(struct dce8_wm_params *wm)` derives a nanosecond watermark from memory-controller latency, worst chunk/cursor return time, DC pipe latency, other-head return time, DMIF fill bandwidth, and line-buffer fill time.
- `dce8_average_bandwidth_vs_dram_bandwidth_for_display()`, `dce8_average_bandwidth_vs_available_bandwidth()`, and `dce8_check_latency_hiding()` are boolean guards used to detect modes that cannot fit comfortably in the current display/memory bandwidth model.
- `dce8_program_watermarks(struct radeon_device *rdev, struct radeon_crtc *radeon_crtc, u32 lb_size, u32 num_heads)` builds high-clock and low-clock watermark parameter sets, writes watermark sets A and B through `DPG_WATERMARK_MASK_CONTROL`/`DPG_PIPE_LATENCY_CONTROL`, restores the original mask, and caches computed values in the CRTC.
- `dce8_bandwidth_update(struct radeon_device *rdev)` is the external display update hook for this chunk. It exits until mode config is initialized, calls `radeon_update_display_priority()`, counts enabled heads, then runs `dce8_line_buffer_adjust()` and `dce8_program_watermarks()` for every CRTC.
- `cik_get_gpu_clock_counter(struct radeon_device *rdev)` serializes access with `rdev->gpu_clock_mutex`, triggers `RLC_CAPTURE_GPU_CLOCK_COUNT`, reads LSB/MSB counter registers, and returns a 64-bit counter snapshot.
- `cik_set_uvd_clock()` is the shared helper for UVD VCLK/DCLK. It calls `radeon_atom_get_clock_dividers()`, writes the post divider into the selected SMC control register after clearing direct-control/divider bits, and polls the selected status register for `DCLK_STATUS`.
- `cik_set_uvd_clocks()` applies `cik_set_uvd_clock()` to `CG_VCLK_CNTL`/`CG_VCLK_STATUS` and `CG_DCLK_CNTL`/`CG_DCLK_STATUS`.
- `cik_set_vce_clocks()` calculates a divider for `ecclk`, waits for `CG_ECLK_STATUS`, writes `CG_ECLK_CNTL`, then waits again. The `evclk` parameter is present in the public signature but is not used by this implementation.
- `cik_pcie_gen3_enable()` gates link-speed changes by bus topology, module parameter `radeon_pcie_gen2`, ASIC flags, root-port speed capability, current GPU data rate, and PCIe capability presence. For gen3-capable roots it may retry equalization, renegotiate link width, then set target link speed and initiate a software speed change.
- `cik_program_aspm()` gates ASPM by `radeon_aspm`, IGP/PCIe flags, then programs PCIe LC/PIF/SMC registers for L0s/L1 inactivity, PLL power-down, dynamic lane power state, CLKREQ-enabled reference/deep-sleep clocks, memory light sleep, and a reverse-link L0s workaround.

## Control Flow

The display watermark flow starts in `dce8_bandwidth_update()`. Once mode configuration is initialized, it updates display priority, counts enabled CRTCs, then iterates all CRTCs. For each CRTC, the earlier `dce8_line_buffer_adjust()` helper returns a line-buffer allocation, and `dce8_program_watermarks()` computes/registers watermarks even for disabled CRTCs; disabled CRTCs keep zero line time and zero watermark values.

`dce8_program_watermarks()` has two internal calculation passes when the CRTC is enabled and at least one head is active. The high-clock pass uses DPM high clocks via `radeon_dpm_get_mclk(..., false)` and `radeon_dpm_get_sclk(..., false)` when DPM is active, otherwise current PM clocks. The low-clock pass mirrors the same parameters but requests low DPM clocks with the `true` argument. Both passes populate `struct dce8_wm_params`, account for interlace and rmx scaling, assume 4 bytes per pixel, query `cik_get_number_of_dram_channels()`, clamp latency watermarks to 16 bits, and only log "force priority to high" if any fit/latency-hiding check fails or `rdev->disp_priority == 2`.

Register programming uses a select-write-restore pattern. The original `DPG_WATERMARK_MASK_CONTROL` is saved. The function selects latency watermark set A, writes low watermark A and `line_time` as high watermark, then selects set B and writes low watermark B plus the same high watermark. It finally restores the original selection and stores `line_time`, `wm_high`, and `wm_low` into `radeon_crtc` for DPM/display reuse.

The video-clock flow first asks ATOM BIOS for a post divider using `COMPUTE_GPUCLK_INPUT_FLAG_DEFAULT_GPUCLK`. UVD updates one clock at a time through SMC control/status registers and aborts the second update if VCLK fails. VCE checks readiness before and after programming ECLK. All polling loops are bounded at 100 iterations with 10 ms delays and return `-ETIMEDOUT` on failure.

`cik_pcie_gen3_enable()` is invoked from earlier device setup code after CIK initialization reaches PCIe configuration. It avoids root-bus devices, disabled PCIe gen2/gen3 module settings, IGPs, non-PCIe ASICs, unknown or unsupported root speed caps, and already-enabled links. On gen3 roots, it may set hardware autonomous width disable, request max-width renegotiation, loop up to ten equalization retries with 100 ms sleeps, save/restore LNKCTL/LNKCTL2 fields around quiesce/redo-equalization toggles, then set target speed and trigger `LC_INITIATE_LINK_SPEED_CHANGE`.

`cik_program_aspm()` performs mostly straight-line read-modify-write programming. The local disable booleans default to false, so the active path enables L0s/L1 inactivity values, allows PLL power-down in L1, checks root-port `PCI_EXP_LNKCAP_CLKPM` before CLKREQ-dependent deep-sleep clock changes, enables PCIe memory light sleep bits, then conditionally disables L0s inactivity if N_FTS and reverse link status indicate the documented workaround condition.

## State and Persistence Behavior

- Display state persists in hardware registers under each CRTC offset: `DPG_WATERMARK_MASK_CONTROL` selects which watermark slot is being updated, while `DPG_PIPE_LATENCY_CONTROL` receives the low/high latency values for slots A and B.
- Derived display state is cached in `struct radeon_crtc`: `lb_vblank_lead_lines`, `line_time`, `wm_high`, and `wm_low`. These cached values are later relevant to DPM and display update decisions.
- The watermark calculations are transient stack state in `struct dce8_wm_params`, but they depend on persistent PM state (`rdev->pm.pm_method`, `dpm_enabled`, `current_mclk`, `current_sclk`) and mode state (`drm_display_mode`, CRTC enabled flag, scaling fields).
- `cik_get_gpu_clock_counter()` protects the capture/read sequence with `rdev->gpu_clock_mutex`, preventing interleaved counter captures from corrupting the returned LSB/MSB pair.
- UVD/VCE clock changes persist in SMC clock control registers (`CG_VCLK_CNTL`, `CG_DCLK_CNTL`, `CG_ECLK_CNTL`) and are confirmed through SMC status registers.
- PCIe link-speed changes persist in GPU PCIe port registers and PCIe capability space (`PCI_EXP_LNKCTL2` target link speed). The function does not surface a failure if `LC_INITIATE_LINK_SPEED_CHANGE` remains set after the timeout loop; it simply stops polling.
- ASPM changes persist in PCIe LC/PIF registers and several SMC clock-selection registers. They affect link power-state behavior after function return and may interact with platform/root-port CLKREQ support.

## Dependencies and Integration Points

- Register access depends on Radeon macros/helpers such as `RREG32`, `WREG32`, `RREG32_SMC`, `WREG32_SMC`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`, plus register/mask definitions for DPG, RLC, CG, PCIE LC, PIF, THM, MISC, and MPLL blocks.
- Fixed-point display math depends on `fixed20_12` and helpers `dfixed_const()`, `dfixed_div()`, `dfixed_mul()`, and `dfixed_trunc()`.
- Display integration uses DRM mode state (`struct drm_display_mode`, `DRM_MODE_FLAG_INTERLACE`), Radeon mode/CRTC structures (`rdev->mode_info`, `struct radeon_crtc`, `crtc_offset`, `vsc`, `rmx_type`), and earlier CIK helpers `dce8_line_buffer_adjust()` and `cik_get_number_of_dram_channels()`.
- Power-management integration uses `PM_METHOD_DPM`, `radeon_dpm_get_mclk()`, `radeon_dpm_get_sclk()`, current PM clocks, and `radeon_update_display_priority()`.
- ATOM BIOS integration for media clocks is through `radeon_atom_get_clock_dividers()` and `struct atom_clock_dividers`.
- PCI integration uses Linux PCIe helpers and constants: `pci_is_root_bus()`, `pci_is_pcie()`, `pcie_get_speed_cap()`, `pcie_capability_read_word()`, `pcie_capability_read_dword()`, `pcie_capability_set_word()`, and `pcie_capability_clear_and_set_word()`.
- Global/module parameters `radeon_pcie_gen2` and `radeon_aspm` control whether PCIe link-speed and ASPM programming run.
- Earlier declarations for `cik_pcie_gen3_enable()` and `cik_program_aspm()` are matched by earlier call sites in CIK startup/setup code, so these static tail functions are integrated into initialization rather than exported.

## Risks and Edge Cases

- Several bandwidth and latency helpers divide by values that must be nonzero: `available_bandwidth`, `wm->disp_clk`, `wm->num_heads`, `wm->src_width`, and computed `lb_fill_bw`. `dce8_latency_watermark()` returns early for zero heads, but other helpers divide by `wm->num_heads` only after callers currently guard `num_heads`; invalid or partially initialized modes/clocks could still be hazardous.
- Watermark calculations hard-code `bytes_per_pixel = 4` with a comment noting it should come from framebuffer config. Modes using other effective bytes-per-pixel may get conservative or inaccurate watermarks.
- `dce8_program_watermarks()` computes `mode = &radeon_crtc->base.mode`, so the `mode` pointer itself is always non-NULL; the runtime guard mainly checks enabled state and `num_heads`. It still writes zero watermarks for disabled/uninitialized CRTCs.
- The priority checks only emit `DRM_DEBUG_KMS("force priority to high")`; this chunk does not actually raise priority. The comment says this should happen at mode validation time, so there may be a mismatch between detection and enforcement.
- VCE `evclk` is unused, so callers requesting both EVCLK and ECCLK updates may only get ECCLK programming here.
- UVD/VCE polling uses blocking `mdelay(10)` loops up to roughly one second per status wait. That is acceptable only in contexts where sleeping/busy waiting during clock programming is expected.
- `cik_set_uvd_clock()` checks `DCLK_STATUS` for both VCLK and DCLK status registers. This assumes the status bit layout is shared; if not, clock-ready detection can be wrong.
- PCIe gen3 equalization alters root-port and endpoint PCIe capability fields and GPU link-control registers. Platform quirks, pending transactions, poor signal integrity, or unexpected root capabilities can make this sensitive.
- The final PCIe speed-change poll has no error return and no log if the link-speed-change bit never clears. Link training failure may only be visible through later status/debugging.
- ASPM defaults all local disable booleans to false and lacks board-specific quirk handling in this chunk. Enabling L0s/L1, PLL-off, CLKREQ-related clock changes, or dynamic lane power state can expose platform compatibility problems if upstream policy did not already filter them.
- `cik_program_aspm()` reads `rdev->pdev->bus->self` only inside a non-root-bus branch for CLKREQ detection, but the rest of ASPM programming assumes the device is PCIe and non-IGP after the early guards.

## Test Signals

- Build the radeon driver with CIK enabled; missing register masks, PCIe helper availability, ATOM divider APIs, or function prototype mismatches should surface at compile time.
- Exercise display mode set, hotplug, and multi-monitor transitions on CIK hardware and confirm `dce8_bandwidth_update()` runs after mode config initialization without divide-by-zero warnings or register access faults.
- Validate watermark register programming by comparing `DPG_WATERMARK_MASK_CONTROL` restoration and `DPG_PIPE_LATENCY_CONTROL` values for single-head, multi-head, interlaced, scaled, and low-clock DPM states.
- Run suspend/resume and DPM clock transitions with active display outputs; check that cached `radeon_crtc->wm_high`, `wm_low`, `line_time`, and `lb_vblank_lead_lines` remain coherent after modeset and power-state changes.
- Exercise UVD playback and VCE encode paths while changing requested media clocks; expected signals are successful `cik_set_uvd_clocks()`/`cik_set_vce_clocks()` returns, no `-ETIMEDOUT`, stable video playback/encode, and correct SMC clock status.
- Read GPU clock counters concurrently from any debug/performance paths using `cik_get_gpu_clock_counter()` and verify monotonic 64-bit snapshots with no torn MSB/LSB reads.
- Boot CIK discrete PCIe cards behind gen2 and gen3 capable root ports with `radeon.pcie_gen2=0` and enabled settings; verify log messages, target link speed, negotiated width/speed, and absence of link training errors.
- Test ASPM with `radeon_aspm=0` and enabled settings across platforms with and without root-port CLKPM support. Signals include stable suspend/resume, no PCIe AER/link errors, expected L0s/L1 residency, and no display/video regressions under load.

## Chunk Notes for Merge Lane

This is the final line chunk for `sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.c`. The merged per-file report should connect these tail routines to earlier CIK initialization, MC/GFX/CP/SDMA/UVD/VCE/display setup, interrupt, power-management, and mode-setting chunks. In particular, merge should note that `cik_pcie_gen3_enable()` and `cik_program_aspm()` are declared near the top and called by earlier initialization code, while `dce8_bandwidth_update()`, `cik_get_gpu_clock_counter()`, `cik_set_uvd_clocks()`, and `cik_set_vce_clocks()` are externally visible integration points from this tail section.

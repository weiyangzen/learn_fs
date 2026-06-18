# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.c

## Purpose
Implements the Qualcomm DPU KMS platform driver and MSM KMS backend: probing, MMIO/clock/ICC setup, hardware init, global atomic state, DRM object creation, display initialization, commit hooks, runtime PM, debugfs, snapshots, and driver registration.

## Important APIs, types, and functions
- Platform entry points: `dpu_dev_probe()`, `dpu_dev_remove()`, `msm_dpu_register()`, and `msm_dpu_unregister()`.
- KMS lifecycle: `dpu_kms_init()`, `dpu_kms_hw_init()`, `dpu_kms_destroy()`, `_dpu_kms_hw_destroy()`, `_dpu_kms_mmu_init()`, and `_dpu_kms_mmu_destroy()`.
- DRM object/display setup: `_dpu_kms_setup_displays()`, `_dpu_kms_initialize_dsi()`, `_dpu_kms_initialize_displayport()`, `_dpu_kms_initialize_hdmi()`, `_dpu_kms_initialize_writeback()`, and `_dpu_kms_drm_obj_init()`.
- Atomic/global state: `dpu_kms_get_global_state()`, duplicate/create/destroy/print state funcs, and `kms_funcs`.
- PM/debug: runtime suspend/resume, debugfs danger/register helpers, and `dpu_kms_mdp_snapshot()`.

## Control flow
Probe validates component binding, allocates `dpu_kms`, sets OPP/clock metadata, maps MDP/VBIF regions using either mdp5 or DPU resource names, parses interconnect paths, then calls `msm_drv_probe()`. KMS init sets max OPP rate, initializes the MSM KMS base, stores the DRM device, and enables runtime PM.

Hardware init creates the global private object, resumes runtime PM, reads core revision, obtains catalog data from OF match, initializes the GPU VM/MMU, fetches UBWC config, initializes resource manager, MDP TOP, VBIF, performance state, optional SC8180X DP PHY mapping, interrupts, mode config limits, DRM planes/CRTCs/encoders/connectors, and VBIF memory types. Commit hooks wrap runtime PM, kickoff active CRTCs, wait for encoder commit completion, and complete CRTC commits.

DRM object init first creates display encoders/connectors for DSI, DP, HDMI, and WB_2 writeback, then creates real or virtual planes from catalog SSPPs, assigns primary/cursor plane arrays, creates CRTCs, and marks every encoder compatible with every CRTC. Runtime suspend disables clocks and ICC bandwidth; resume reenables clocks, reinitializes VBIF memtypes, and notifies encoders.

## State and persistence
`struct dpu_kms` owns MMIO pointers, catalog and UBWC data, regulators, clocks, ICC paths, resource manager, hardware wrappers, interrupt wrapper, performance state, global atomic private object, bandwidth refcount, platform device, and runtime-PM state. Hardware register state is reprogrammed during init/resume and commits; atomic resource state persists in `dpu_global_state` snapshots.

## Dependencies and integration points
Integrates with the MSM DRM core (`msm_kms`, `msm_drv_probe`, `msm_mmu`, GEM VM), DRM atomic/vblank/writeback frameworks, DSI/DP/HDMI subdrivers, DPU CRTC/encoder/plane/resource-manager/perf/IRQ/VBIF modules, Linux runtime PM, clocks, OPP, interconnect, OF matching, and debugfs/snapshot infrastructure.

## Risks
This is high blast-radius initialization code. Error paths must release runtime PM and destroy partially initialized MMU/global state. Virtual-plane behavior is module-parameter controlled and changes resource allocation semantics. Display setup assumes WB_2 for DPU writeback. The SC8180X DP PHY mapping is hard-coded. Runtime resume must restore enough VBIF/encoder state after clocks return. Debugfs register reads require PM get/put to avoid reading powered-off MMIO.

## Test signals
Signals include probe success across every OF compatible, clean runtime suspend/resume, vblank enable/disable, atomic commits on DSI/DP/HDMI, writeback connector jobs, debugfs `hw_log_mask`, danger/safe status, SSPP register dumps, display snapshot contents, ICC bandwidth release on suspend, and absence of PM ref leaks on init failures.

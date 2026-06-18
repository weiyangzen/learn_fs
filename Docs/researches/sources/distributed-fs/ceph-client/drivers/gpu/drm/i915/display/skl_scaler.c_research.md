# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_scaler.c

### Purpose
`skl_scaler.c` manages Skylake-style pipe scalers for CRTC panel fitting, plane scaling, YUV planar conversion/upsampling, CASF, scaling filters, hardware detach/readback, ECC workaround masking, and prefill/downscale limits.

### Important APIs, Types, And Functions
Public APIs include `skl_scaler_mode_valid()`, `skl_update_scaler_crtc()`, `skl_update_scaler_plane()`, `intel_atomic_setup_scalers()`, `skl_scaler_setup_casf()`, `skl_pfit_enable()`, `skl_program_plane_scaler()`, `skl_detach_scalers()`, `skl_scaler_disable()`, `skl_scaler_get_config()`, `adl_scaler_ecc_mask()`, `adl_scaler_ecc_unmask()`, and scaler prefill/max-scale helpers. Internal helpers calculate phases, source/destination size limits, allocate scaler IDs, choose scaler mode, validate scale factors, and program nearest-neighbor coefficients.

### Control Flow
Atomic plane/CRTC check calls `skl_update_scaler_*()` to stage users in `crtc_state->scaler_state.scaler_users` after checking interlace, source/destination limits, pipe source limits, and whether scaling or planar YUV requires a scaler. `intel_atomic_setup_scalers()` counts users, ensures enough hardware scalers, includes planes not otherwise in the transaction when necessary, allocates scaler IDs, chooses modes such as NV12, planar, normal, HQ, dynamic, or CASF-specific scaler 1, and validates h/v scale factors. Commit programming binds a scaler to the pipe or plane, programs phase/window/size/filter registers, or detaches unused scalers. Readback finds pipe-bound scalers and reconstructs pfit/CASF state.

### State, Persistence, And Dependencies
Staged state lives in `intel_crtc_scaler_state`, `intel_scaler`, per-plane `scaler_id`, and `pch_pfit`/CASF state. Persistent state is the `SKL_PS_*` MMIO register set and GLK coefficient tables. Dependencies include CASF, display register definitions, tracepoints, workarounds, framebuffer format helpers, universal plane state, DSB writes, and DRM rectangle scaling helpers.

### Integration Points
Plane check/commit, CRTC panel fitting, CASF sharpness, display readback, ADL scaler ECC workaround paths, VRR/CDCLK prefill calculations, and mode validation for YCbCr420 use this module. `skl_prefill.c` consumes scaler prefill/max-scale helpers.

### Risks
Scaler allocation is a shared scarce resource; stale `scaler_id` or missing existing-plane state can overcommit hardware. Platform limits vary by display version and scaler ID, especially display version 14 where only scaler 0 supports vertical downscale above 1.0. Planar YUV phase and binding must match linked planes. Nearest-neighbor coefficient programming is GLK-style and assumes coefficient table layout. Several max-scale/prefill helpers contain FIXME approximations, so guardband/CDCLK estimates may be conservative or incomplete.

### Test Signals
Useful tests cover simultaneous plane scaling and pfit, CASF needing scaler 1, NV12/planar formats, nearest-neighbor filter programming, downscale limit rejection by platform/scaler ID, scaler detach after plane disable, readback of pfit/CASF state, ADL ECC mask/unmask, and underrun-free operation with VRR prefill.

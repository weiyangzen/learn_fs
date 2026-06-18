<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_vec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_vec.c

## Purpose
`vc4_vec.c` implements the VC4 VEC SDTV encoder component for composite PAL/NTSC/SECAM output. It exposes a DRM encoder and connector, creates TV mode properties, validates analog timing constraints, programs VEC/WSE/DAC registers during atomic enable, and integrates the platform device into the VC4 componentized DRM driver.

## Important APIs, Types, and Functions
Key types are `struct vc4_vec_variant`, `struct vc4_vec`, `enum vc4_vec_tv_mode_id`, and `struct vc4_vec_tv_mode`. Important functions include `vc4_vec_tv_mode_lookup()`, connector property handlers, `vc4_vec_connector_init()`, `vc4_vec_encoder_enable()`, `vc4_vec_encoder_disable()`, `vc4_vec_encoder_atomic_check()`, `vc4_vec_late_register()`, `vc4_vec_bind()`, and platform probe/remove. Register macros cover VEC config, color subcarrier frequency, DAC power, status, and debugfs register exposure.

## Control Flow
Platform probe registers a component. Bind creates DRM TV properties, allocates the VEC object, maps registers, resolves the SoC variant and clock, enables runtime PM, initializes the TVDAC encoder, then initializes the composite connector. Atomic check maps connector TV mode plus adjusted `htotal` to a VEC mode table entry and rejects unsupported horizontal/vertical timing shapes. Atomic enable enters the DRM device, resumes power, sets the VEC clock to 108 MHz, enables it, resets hardware blocks, writes mode-common and mode-specific registers, programs custom subcarrier frequency when needed, powers the DAC, and enables the VEC. Disable clears enable bits, powers down DAC/LDO/bias blocks, disables the clock, and releases runtime PM.

## State and Persistence Behavior
Persistent state is the `struct vc4_vec` instance, register mapping, clock pointer, TV mode property pointer, SoC variant DAC configuration, connector state, and debugfs regset. Hardware state persists in VEC registers while the encoder is active and is reset/reprogrammed on each enable. Runtime PM and clock state are tied to encoder active state.

## Dependencies and Integration Points
The file uses DRM atomic helpers, TV mode properties, connector helper TV mode generation, component framework, platform OF matching, VC4 register/debugfs helpers, clocks, runtime PM, and KUnit register-access guards. It integrates with VC4 encoder routing and with downstream userspace modesetting through standard DRM connector properties plus a legacy `mode` enum property.

## Risks
Mode selection depends on `htotal` to distinguish PAL-60/monochrome variants sharing DRM TV mode IDs. Register programming is hardware-specific and has few readback checks. `vc4_vec_connector_detect()` returns unknown, so userspace relies on virtual/probed modes. Clock rate sharing with HDMI requires enable-time rate setting. Timing validation is conservative and must track analog standard requirements. Error paths during enable must balance runtime PM and clock state.

## Test Signals
Tests should cover connector property set/get mapping, all supported TV modes, invalid timing rejection, enable/disable PM and clock balancing, debugfs register exposure, device-tree matches for BCM2835 and BCM2711 DAC settings, KUnit paths that must not touch registers, and atomic modesets switching between 50 Hz and 60 Hz standards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_vec.c -->

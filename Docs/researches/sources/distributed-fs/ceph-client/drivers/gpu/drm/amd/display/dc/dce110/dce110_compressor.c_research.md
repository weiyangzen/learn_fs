# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.c

Purpose: implements the DCE110 framebuffer compression compressor object, including FBC power-up, enable/disable, compressed surface address/pitch programming, invalidation triggers, hardware state query, and object lifecycle.

Important functions: `dce110_compressor_power_up_fbc()` enables FBC, coherency mode, compression modes, min compression ratio, and indirect LUT defaults. `dce110_compressor_enable_fbc()` attaches FBC to a CRTC source, toggles `FBC_GRPH_COMP_EN` for a hardware bug workaround, configures misc invalidation/decompress behavior, then waits for enabled status. `dce110_compressor_disable_fbc()` turns off compression, clears software attachment state, waits for disabled status, and resets the line buffer on vblank for DCE100/110. `dce110_compressor_program_compressed_surface_address_and_pitch()` writes high address first, then low address and aligned pitch. `dce110_compressor_set_fbc_invalidation_triggers()` programs region masks and force-clear events.

Control flow: per-CRTC DCP/DMIF offsets are selected from a three-entry offset table before register access. Status waits poll FBC status up to 1000 times with 100 us delay. Line-buffer reset checks that CRTC position is moving, arms reset, waits for frame count change up to about 100 ms, then clears reset selection.

State and persistence: `struct dce110_compressor` embeds `struct compressor` and current offsets. The base compressor tracks options, min compression ratio, attached CRTC, enabled flag, memory bus width, and compressed surface address. Hardware state persists in global FBC registers and per-DCP compressed-surface registers.

Dependencies and integration: depends on DCE11/GMC register headers, `dm_services` raw register helpers, logger interface, and `compressor_funcs`. It is built by the DCE110 Makefile and consumed through the generic compressor interface.

Risks: offset table covers three pipes only; invalid `params->inst` would index out of bounds. Enable state mixes hardware status with software `attached_inst`. Pitch calculation assumes 1:1 compression ratio and logs otherwise. Wait timeouts log warnings but do not fail callers. Test signals include FBC support gating, enable/disable status polling, compressed address high-before-low order, pitch alignment for varied widths, vblank reset on active/inactive CRTC, and invalidation trigger masks.

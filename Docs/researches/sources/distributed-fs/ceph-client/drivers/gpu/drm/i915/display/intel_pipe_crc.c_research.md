# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.c

Purpose: implements debugfs/DRM CRTC CRC source selection and pipe CRC enable/disable for many display generations. It translates source names into generation-specific `PIPE_CRC_CTL` bits, validates supported sources, applies workarounds, and synchronizes IRQ teardown.

Important functions: `intel_crtc_crc_init()`, `intel_crtc_get_crc_sources()`, `intel_crtc_verify_crc_source()`, `intel_crtc_set_crc_source()`, `intel_crtc_enable_pipe_crc()`, and `intel_crtc_disable_pipe_crc()`. Generation helpers include i8xx/i9xx/VLV/ILK/IVB/SKL source validation and control-register builders, `i9xx_pipe_crc_auto_source()`, `vlv_undo_pipe_scramble_reset()`, and `intel_crtc_crc_setup_workarounds()`.

Control flow: source strings map to `enum intel_pipe_crc_source`; verification checks whether a source is valid for the platform and reports five CRC values. Setting a source obtains the pipe power domain if enabled, enables CRC-related workarounds when turning CRC on, builds the generation-specific control word, writes `PIPE_CRC_CTL`, resets skipped count, undoes VLV scramble reset on disable, disables workarounds when turning off, and drops the wakeref. Enable/disable functions support modeset transitions when the debugfs CRC file is open; disable sets `skipped = INT_MIN`, clears the register, posting reads, and synchronizes parent IRQs.

State and persistence: initializes and uses `crtc->pipe_crc.lock`, `source`, and `skipped`. It writes PIPE CRC MMIO, VLV/G4X symbol reset bits, and may commit internal atomic state to toggle PSR/CRC workarounds.

Dependencies/integration: depends on debugfs CRC hooks in `intel_crtc`, display power domains, display IRQ handlers, parent IRQ sync, atomic commits, PSR state, platform register definitions, DP/TV encoder inspection, and modeset locks for auto-source detection.

Risks/test signals: risks include enabling CRC while pipe off, auto-source with concurrent modesets, generation-specific unsupported tap points, VLV scramble reset cleanup, workaround atomic commit deadlocks, and IRQs arriving after disable. Test debugfs CRC on gen2, gen3/4 TV, VLV/CHV DP, ILK/SNB, IVB/HSW, and SKL+ plane sources; include source `auto`, invalid source names, pipe-off error, PSR-enabled panels, and open CRC across modesets.

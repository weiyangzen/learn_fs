# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hda.c

Purpose: Implements HD analog/component output as a DRM bridge and connector attached to the DAC encoder created by TVOUT. It programs supported video modes, AWG microcode, sampler/scaler coefficients, DAC clocks, and optional video DAC control registers.

Important APIs/functions: `sti_hda_probe()` allocates the bridge, maps `hda-reg` and optional `video-dacs-ctrl`, gets `pix` and `hddac` clocks, and adds the bridge/component. `sti_hda_bind()` finds the DAC encoder, attaches the bridge, creates a Component connector, and disables DACs at startup. `sti_hda_set_mode()` validates a mode against `hda_supported_modes`, sets `hddac` rate to 2x or 4x pixel clock based on category, and sets formatter pixel clock. `sti_hda_pre_enable()` enables clocks, selects filters/coefficients, enables DACs, writes scaler/sampler/AWG registers, and enables AWG. `sti_hda_disable()` disables AWG/DACs and clocks.

Control flow: Modes are fixed in a static table; connector mode enumeration duplicates those modes and marks the first preferred. Mode validation checks both table membership and rounded clock tolerance.

State/persistence: `struct sti_hda` stores current mode, register bases, clocks, bridge, DRM device, and enabled flag. Static AWG instruction arrays and coefficient tables encode supported timing categories.

Dependencies/integration: Uses DRM bridge/connector helpers, component framework, clocks, IO resources, TVOUT DAC encoder, and debugfs. TVOUT programs shared VIP routing while this file programs the analog formatter itself.

Risks/test signals: Several pre-enable error paths return after clocks are enabled without unwinding. Supported modes are narrow and interlaced support is explicitly absent in the chain. Test each advertised mode, clock tolerance, DAC power transitions, bridge enable/disable, debugfs AWG/register output, and probe without `video-dacs-ctrl`.

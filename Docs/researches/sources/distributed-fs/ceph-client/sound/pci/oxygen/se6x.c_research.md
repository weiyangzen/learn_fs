
# sources/distributed-fs/ceph-client/sound/pci/oxygen/se6x.c

Purpose: standalone PCI module for Studio Evolution SE6X built on the shared Oxygen core with a minimal custom `oxygen_model`.

Important functions: `se6x_init` configures GPIO outputs and registers PCM1792A/PCM1804 components; `se6x_control_filter` removes generic master playback volume/mute controls; `set_pcm1792a_params`/`set_pcm1804_params` are no-ops because external hardware/microcontroller handles clocks; `se6x_adjust_dac_routing` mirrors one stereo pair to both DAC0 and DAC1; `se6x_probe` delegates to `oxygen_pci_probe`.

Control flow/state: module parameters follow ALSA card slot conventions. Probe selects `model_se6x`; shared code creates PCM/mixer using device_config for I2S playback and three capture inputs.

Dependencies/integration: depends on `oxygen_lib`, `oxygen_pcm`, `oxygen_mixer`, and register helpers. No persistent private model_data is used.

Risks: broad PCI subdevice ID overlaps generic CMI8788 ID; module selection/config must avoid conflicts. Tests: module probe, no generic DAC master controls, stereo playback routing, three analog capture PCMs, suspend/resume via shared PM, and GPIO setup.

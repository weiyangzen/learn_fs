
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg_mixer.c

Purpose: ALSA mixer controls and `oxygen_model` definition for Xonar DG/DGX.

Important functions: output select control applies CS4245 aux/DAC output and GPIO rear-jack relay; headphone volume/mute controls write CS4245 DAC volume/control registers; capture volume controls store per-source PGA values and apply current source; capture source selects CS4245 analog input; ADC HPF control toggles HPF freeze. `dg_control_filter` removes generic master playback controls. `dg_mixer_init` initializes routing and adds DG controls. `model_xonar_dg` wires all callbacks and capabilities.

Control flow/state: mixer callbacks lock `chip->mutex`, update `struct dg`, write CS4245 via helpers, and call shared `oxygen_update_dac_routing` for output changes. Shared mixer still adds SPDIF and monitor controls based on model device_config.

Dependencies: `xonar_dg.c`, CS4245 constants, Oxygen mixer/PCM core. Risks: several controls return negative SPI errors as changed values; headphone volume uses bitwise complement storage; output mode affects both CS4245 and Oxygen routing. Test signals: `amixer` control validation/range errors, output transition audio routing, capture source/volume persistence, HPF, SPDIF coexistence, resume shadow reload.


# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen.c

Purpose: module entry and model selection for generic C-Media CMI8788/CMI8787 boards plus Xonar DG/DGX. It defines PCI IDs, board-specific `oxygen_model` variants, codec setup for AK4396/WM8785/AK5385, and ALSA controls unique to these reference-style cards.

Important functions/types: `generic_data` caches AK4396 and WM8785 registers. `ak4396_write*`, `wm8785_write`, register init/resume helpers, `set_ak4396_params`, `set_wm8785_params`, and `set_ak5385_params` implement codec programming. Mixer hooks add DAC rolloff, ADC HPF, and Meridian/Claro digital-source controls. `get_oxygen_model` clones `model_generic` then patches callbacks, device_config, clocks, names, and channel counts by PCI `driver_data`. `generic_oxygen_probe` delegates to `oxygen_pci_probe`.

Control flow: PCI probe checks module slot enablement, calls shared library probe, which invokes `get_oxygen_model`; shared init then calls this file's model callbacks. Playback/capture hw_params later call the model rate-setting callbacks; mixer writes update cached register state; resume replays codec registers.

State/persistence: AK4396/WM8785 shadow arrays store mutable codec state and support cached writes and resume. GPIO state is manipulated for digital source selection and Claro headphone amplifier enable/disable.

Dependencies/integration: depends on `oxygen_lib.c`, `oxygen_io.c`, `oxygen_mixer.c`, `oxygen_pcm.c`, AK4396/WM8785 headers, and `model_xonar_dg`. Risks include wrong PCI subdevice mapping, SPI codec index mismatches, long anti-pop delays, and sample-rate DFS/MCLK mismatches. Test signals: probe each model, ALSA mixer controls, 2/8-channel playback, SPDIF input source controls, suspend/resume, proc codec dumps, and DG fallback path.

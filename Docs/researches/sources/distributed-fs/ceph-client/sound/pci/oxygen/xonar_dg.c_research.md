
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_dg.c

Purpose: low-level Xonar DG/DGX board support around CS4245 SPI codec, GPIO output routing, and model callbacks.

Important functions: `cs4245_write_spi`, `cs4245_read_spi`, and `cs4245_shadow_control` maintain the CS4245 shadow register array. `cs4245_init` saves initial state, programs power, async mode, DAC/ADC formats, PGA behavior, and headphone volume. `dg_init/cleanup/suspend/resume` manage output GPIO and anti-pop delay. `set_cs4245_dac_params` and `set_cs4245_adc_params` update functional mode and MCLK ratio by sample rate. `adjust_dg_dac_routing` swaps Oxygen DAC pair mapping and mutes inactive groups by selected output. `dump_cs4245_registers` refreshes interrupt status and prints cached registers.

State/persistence: `struct dg` owns CS4245 shadow state, output selection, input volumes, and input selection; resume reloads the shadow.

Dependencies/integration: used by `model_xonar_dg` in `xonar_dg_mixer.c`, selected from `oxygen.c` for DG/DGX PCI IDs. Risks include long 2.5-second output enable, SPI failures causing shadow/device mismatch, and non-obvious channel remapping. Test signals: DG/DGX probe, output modes, playback channel routing, capture rates, resume, and proc dump.

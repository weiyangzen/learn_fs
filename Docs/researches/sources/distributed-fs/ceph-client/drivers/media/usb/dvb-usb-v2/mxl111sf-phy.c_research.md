# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.c

Purpose: physical-layer and port-configuration helpers for MxL111SF chips. It programs reset, device mode, tuner/demod default patches, USB output, MPEG TS input, I2S input, SPI mode, and IDAC antenna switching current settings.

Important APIs/types/functions: exported helpers include `mxl111sf_init_tuner_demod()`, `mxl1x1sf_soft_reset()`, `mxl1x1sf_set_device_mode()`, `mxl1x1sf_top_master_ctrl()`, `mxl111sf_disable_656_port()`, `mxl111sf_enable_usb_output()`, `mxl111sf_config_mpeg_in()`, `mxl111sf_init_i2s_port()`, `mxl111sf_disable_i2s_port()`, `mxl111sf_config_i2s()`, `mxl111sf_config_spi()`, and `mxl111sf_idac_config()`.

Control flow: frontend attach and per-frontend init in `mxl111sf.c` use this file to reset the chip, apply initialization register sequences, choose tuner versus SoC mode, power the top master, enable USB output, and configure endpoint-specific data paths. EP6 ATSC paths configure MPEG input, EP5 mobile paths configure I2S and optional SPI, and antenna hunting calls IDAC configuration to switch internal/external RF paths.

State and persistence: the helper mutates `state->device_mode` after a successful mode write. All other persistence is in chip registers, including page register 0x00, reset, top master, MPEG/I2S/SPI port state, and IDAC values. Some routines temporarily switch register pages and must return to page 0.

Dependencies and integration: depends on shared MxL111SF register helpers and the register constants in `mxl111sf-reg.h`. It is not an independent subsystem; it is a hardware-programming layer for the main bridge and tuner modules.

Risks: many routines call `mxl_fail(ret)` but continue after intermediate failures, which can cause later writes to run against partially configured hardware. `mxl111sf_config_mpeg_in()` does not stop after the first pin-mux write failure. `mxl111sf_config_spi()` must restore page 0; a failure before the final page write can strand subsequent accesses on page 2. Magic register sequences depend on silicon revisions and board wiring.

Test signals: reset and chip-info probe after attach; DVB-T, ATSC, and MH frontend init sequencing; EP4/EP5/EP6 stream start/stop; SPI toggle on v8 Mercury paths; antenna path switching through IDAC; register trace confirming page returns to 0 after SPI and init patch programming.

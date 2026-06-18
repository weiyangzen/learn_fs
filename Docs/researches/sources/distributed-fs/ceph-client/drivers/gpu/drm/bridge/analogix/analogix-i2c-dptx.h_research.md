# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.h

Purpose: Register definitions and exported prototype for the TX_P0 DP transmitter page used by Analogix I2C bridge drivers.

Important APIs/types/functions: Defines HDCP status/control/key/timer registers, DP system-control bits, video/audio controls, packet send controls, link bandwidth/lane/training registers, polling/debug controls, AUX address/control/status/data registers, downspread and M calculation controls, and `ssize_t anx_dp_aux_transfer(...)`.

Control flow: No executable logic. The constants drive control flows in `analogix-anx78xx.c` and `analogix-i2c-dptx.c`: AUX setup, HDCP disabling/timer setup, link bandwidth/lane configuration, enhanced framing, training enable, downspread, packet send updates, and analog power-down.

State and persistence: The header names chip registers whose values persist only as hardware state while the chip is powered. Software persistence is handled by callers.

Dependencies and integration: Consumed with `regmap` accessors and DRM DP helpers. It pairs with `analogix-i2c-txcommon.h` and device-specific headers to cover all I2C pages.

Risks: Some field names encode chip-specific behavior such as hardware link training error codes and AUX status bits; incorrect interpretation can break link training or hide AUX failures. The prototype exposes only a regmap, so caller-side locking and power management are mandatory.

Test signals: Build coverage, AUX transfer behavior, link training register writes, downspread/DPCD compatibility, and HDCP register sequence validation are key signals.

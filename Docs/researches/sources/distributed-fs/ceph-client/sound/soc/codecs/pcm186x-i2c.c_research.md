# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-i2c.c

Purpose: provides the I2C transport wrapper for the TI PCM186x universal audio ADC common driver.

Important APIs, types, and functions: `pcm186x_i2c_probe()` obtains the matched `enum pcm186x_type`, creates an I2C regmap with exported `pcm186x_regmap`, passes the device, type, IRQ, and regmap to `pcm186x_probe()`, and registers the I2C driver. OF compatibles map `ti,pcm1862`, `ti,pcm1863`, `ti,pcm1864`, and `ti,pcm1865` to type constants; I2C IDs mirror those names.

Control flow: matching supplies chip type through `i2c_get_match_data()`. Probe does transport setup only; the common core owns ADC controls, DAI registration, IRQ behavior, and device-specific feature handling.

State and persistence: no wrapper-private state. Regmap is device-managed, and common state is allocated by `pcm186x_probe()`.

Dependencies and integration points: depends on I2C and the common `pcm186x.h` declarations. It integrates board descriptions through OF/I2C IDs and forwards the physical IRQ to the common ADC driver.

Risks: if match data is absent or mismatched for non-OF I2C IDs, the cast result must still be a valid `enum pcm186x_type`; this depends on I2C core match-data behavior. All bus-specific register IO assumptions are captured by the shared regmap config. Probe returns raw regmap errors without contextual logging.

Test signals: probe each compatible/ID variant, verify type passed into common probe, test IRQ and no-IRQ configurations, validate regmap creation failure handling, and run common PCM186x ADC capture tests through the I2C wrapper.

# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-i2c.c

## Purpose

`tlv320aic23-i2c.c` is the I2C transport wrapper for the shared TLV320AIC23 codec core. It checks adapter capability, creates an I2C regmap with the common AIC23 regmap configuration, and delegates all codec registration to `tlv320aic23_probe()`.

## Important APIs, Types, and Functions

The only executable entry point is `tlv320aic23_i2c_probe()`. The file also defines `tlv320aic23_id`, `tlv320aic23_of_match` with `ti,tlv320aic23`, and `tlv320aic23_i2c_driver`.

## Control Flow

I2C core calls probe, probe verifies `I2C_FUNC_SMBUS_BYTE_DATA`, initializes `devm_regmap_init_i2c()`, and passes the device plus regmap to the shared core. Driver registration is handled by `module_i2c_driver()`.

## State and Persistence Behavior

This wrapper owns no private state. The regmap and ASoC component state are owned by the common probe and devm-managed resources.

## Dependencies and Integration Points

It depends on Linux I2C, OF, regmap, and ASoC headers plus `tlv320aic23.h`. It integrates the common codec with board descriptions that instantiate an I2C `tlv320aic23` device.

## Risks and Edge Cases

The SMBus byte-data check may reject adapters that could support the raw regmap transfer format by other means. Error handling is intentionally delegated: `tlv320aic23_probe()` receives an ERR_PTR regmap and returns the failure.

## Test Signals

Probe with a supported I2C adapter, OF modalias matching, failure injection for missing adapter functionality, and common AIC23 playback/capture tests through an I2C-connected board.

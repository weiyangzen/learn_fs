# sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-spi.c

## Purpose

`cs530x-spi.c` is the SPI transport wrapper for the CS530x/CS430x/CS4282 codec family driver. It mirrors the I2C wrapper: match a supported device, allocate `struct cs530x_priv`, create an SPI regmap with the shared CS530x SPI regmap configuration, record the matched device type and device pointer, and call the shared `cs530x_probe()`.

## Important APIs, Types, and Functions

- `cs530x_of_match[]` maps OF compatible strings to CS4282/CS4302/CS4304/CS4308/CS5302/CS5304/CS5308 type constants.
- `cs530x_spi_id[]` provides equivalent SPI modalias entries.
- `cs530x_spi_probe()` allocates private state, associates it with the SPI device by `spi_set_drvdata()`, creates `cs530x->regmap` with `devm_regmap_init_spi(spi, &cs530x_regmap_spi)`, stores `devtype` from `spi_get_device_match_data()`, stores `dev`, and delegates to `cs530x_probe()`.
- `module_spi_driver()` registers the SPI driver.

## Control Flow

The SPI core calls `cs530x_spi_probe()` after matching the OF table or SPI ID table. The wrapper performs only transport setup and then hands control to the common CS530x probe. Regmap allocation failures are logged with `dev_err()` and returned directly.

## State and Persistence Behavior

The wrapper's state is devm-managed and bound to the SPI device lifetime. All durable codec behavior is in the shared CS530x core and in hardware registers accessed through the SPI regmap.

## Dependencies and Integration Points

- Linux SPI driver model, OF matching, module tables, regmap SPI transport, devm allocation.
- Local `cs530x.h` for common private structure, device type constants, shared regmap config, and `cs530x_probe()`.
- Imports the `SND_SOC_CS530X` namespace for the shared core symbols.

## Risks and Edge Cases

- The OF match table appears to list `cirrus,cs5304` twice, with the second entry carrying `CS5308` data. That likely prevents an OF-described `cirrus,cs5308` SPI device from matching correctly and can misclassify a second `cs5304` match depending on lookup behavior.
- Unlike the I2C wrapper, regmap creation uses `dev_err()` rather than `dev_err_probe()`, so deferred probe diagnostics are less standardized.
- There is no explicit remove function; this is safe only if all shared-core registrations are devm-managed or otherwise need no SPI-wrapper teardown.
- `spi_get_device_match_data()` must return non-null meaningful data for all binding paths. A mismatch between OF and SPI ID matching can pass an unintended device type.

## Test Signals

Validation should cover SPI module autoload, OF and SPI ID matching for every supported chip name, correct `devtype` propagation, SPI regmap access, and successful shared `cs530x_probe()` completion. A specific test should verify `cirrus,cs5308` OF binding because the current OF table entry looks suspicious.

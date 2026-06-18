# sources/distributed-fs/ceph-client/sound/soc/codecs/cs530x-i2c.c

## Purpose

`cs530x-i2c.c` is the I2C transport wrapper for the CS530x/CS430x/CS4282 codec family driver. It matches device-tree and I2C IDs, allocates the shared private structure, creates an I2C regmap using the shared CS530x regmap configuration, records the matched device type, and delegates the actual codec initialization to `cs530x_probe()`.

## Important APIs, Types, and Functions

- `cs530x_of_match[]` maps `cirrus,cs4282`, `cirrus,cs4302`, `cirrus,cs4304`, `cirrus,cs4308`, `cirrus,cs5302`, `cirrus,cs5304`, and `cirrus,cs5308` to enum-like device type values from `cs530x.h`.
- `cs530x_i2c_id[]` provides the same set of names for non-DT I2C matching.
- `cs530x_i2c_probe()` allocates `struct cs530x_priv` with `devm_kzalloc()`, stores it with `i2c_set_clientdata()`, creates `cs530x->regmap` with `devm_regmap_init_i2c(client, &cs530x_regmap_i2c)`, stores `devtype` from `i2c_get_match_data()`, stores `dev`, and calls `cs530x_probe(cs530x)`.
- `module_i2c_driver()` registers the I2C driver.

## Control Flow

The Linux I2C core matches the device by OF compatible or I2C ID and calls `cs530x_i2c_probe()`. Probe does transport-specific allocation and regmap creation only; all codec-specific register initialization, ASoC registration, power handling, and controls live in the shared CS530x core. Regmap initialization errors are returned through `dev_err_probe()` for deferred-probe-friendly diagnostics.

## State and Persistence Behavior

This wrapper owns no independent persistent state beyond the devm-managed `struct cs530x_priv` and its I2C regmap pointer. The lifetime of the allocation and regmap is tied to the I2C device. Runtime codec state is in the shared CS530x core and hardware registers.

## Dependencies and Integration Points

- Linux I2C driver model, OF matching, module tables, regmap I2C transport, devm allocation.
- Local `cs530x.h` for `struct cs530x_priv`, device type constants, `cs530x_regmap_i2c`, and `cs530x_probe()`.
- Imports the `SND_SOC_CS530X` namespace, making the wrapper depend on symbols exported by the shared CS530x module.

## Risks and Edge Cases

- The device type is derived from match data. If a board uses an unsupported or misspelled compatible, probe will not bind or will pass wrong type data.
- There is no explicit remove function because devm and the shared core presumably own cleanup; this is correct only if `cs530x_probe()` registers resources with devm or otherwise has no transport-specific teardown.
- Transport regmap configuration must match the device's I2C protocol. Any mismatch is hidden from this wrapper and would appear as core register access failures.

## Test Signals

Validation should include module autoload from OF and I2C ID tables, successful I2C regmap creation, correct `devtype` selection for each supported compatible/name, and successful delegation into the shared CS530x codec probe. Probe deferral and error logging should be checked by temporarily withholding bus/regmap prerequisites.

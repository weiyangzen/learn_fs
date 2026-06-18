# sources/distributed-fs/ceph-client/drivers/iio/adc/sd_adc_modulator.c

## Purpose
This is a generic sigma-delta modulator representation. It can either register a legacy one-channel hardware-buffer IIO voltage device or, when `#io-backend-cells` is present, register as an IIO backend for another frontend ADC/DFSDM-style consumer.

## Important APIs, types, and functions
`struct iio_sd_backend_priv` stores optional VREF regulator state and cached millivolt scale. Backend operations are `iio_sd_mod_enable()`, `iio_sd_mod_disable()`, and `iio_sd_mod_read()`, exported through `sd_backend_ops` and `sd_backend_info`. Legacy registration uses `iio_sd_mod_register()` with a one-bit unsigned voltage channel.

## Control flow
`iio_sd_mod_probe()` checks whether the firmware node declares backend cells. Without backend cells, it allocates and registers a legacy IIO device with one hardware-buffer channel. With backend cells, it allocates backend private data, obtains optional `vref`, caches the regulator voltage without enabling it, and registers the backend. Backend enable/disable toggles the optional regulator; backend `read_raw` returns scale or zero offset.

## State and persistence
The only persistent state is the cached VREF millivolt value and regulator pointer. Regulator power is intentionally not enabled at probe and is controlled by backend lifecycle callbacks. The legacy path has no private state.

## Dependencies and integration points
It depends on the IIO backend framework, regulator consumer API, platform device matching, and compatibles `sd-modulator` and `ads1201`. It imports the `IIO_BACKEND` namespace. In backend mode it is not the sampling engine; it supplies enable and scale/offset services to a consumer.

## Risks
If no VREF regulator is provided in backend mode, scale defaults to zero, which may be acceptable for board-specific consumers but is easy to misinterpret. The legacy `iio_info` is an empty declaration, so the legacy device is primarily a buffer endpoint and does not provide raw read callbacks. The source uses trailing semicolons after function definitions, harmless but unusual.

## Test signals
Test backend and legacy probe paths, optional VREF absent and present, regulator enable/disable balancing, scale and offset reads from a backend consumer, compatible fallback behavior for `ads1201`, and cleanup when regulator voltage read fails.

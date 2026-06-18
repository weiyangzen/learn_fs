# sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-adi-util-sigma-delta.c

Purpose: Minimal Analog Devices util-sigma-delta SPI offload trigger provider. It models the hardware block as a data-ready trigger source for SPI offload consumers and registers it with the generic SPI offload trigger registry.

Important APIs, types, and functions: `adi_util_sigma_delta_match()` accepts only `SPI_OFFLOAD_TRIGGER_DATA_READY` with zero fwnode arguments. `adi_util_sigma_delta_ops` supplies that match callback. `adi_util_sigma_delta_probe()` gets and enables the device clock with `devm_clk_get_enabled()` and registers a `spi_offload_trigger_info` using `devm_spi_offload_trigger_register()`. The platform driver matches `adi,util-sigma-delta-spi`.

Control flow: probe obtains the functional clock first so the trigger hardware is live, then registers the trigger against the device fwnode. Later, SPI offload consumers resolving a `trigger-sources` reference can match this provider only for data-ready trigger requests. There are no validate, enable, disable, request, or release callbacks, so the core registry handles lifetime while the provider exposes only identity matching.

State and persistence: no private state is stored. The enabled devm clock and registered trigger are tied to device lifetime. On removal or probe failure, devm unwinds the clock and unregisters the trigger.

Dependencies and integration points: integrates with the SPI offload provider API, fwnode references, platform bus, module OF matching, and clock framework. It relies on `spi-offload.c` to manage references and reject consumers after provider unregister.

Risks: because there are no enable/disable/validate hooks, any hardware configuration is presumed external or static once the clock is enabled. If the underlying block needs acknowledgement or edge selection, this driver does not expose it. The match callback ignores the trigger object and only validates type/nargs.

Test signals: probe with/without clock, fwnode trigger lookup from a consumer, rejection of periodic or argument-bearing trigger requests, module unload while a consumer holds a reference, and deferred clock/provider probing.

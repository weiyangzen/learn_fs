# sources/distributed-fs/ceph-client/drivers/spi/spi-offload.c

Purpose: Generic SPI offload support library. It provides devm allocation/get helpers for offload providers and consumers, a global fwnode-keyed trigger registry, trigger validation/enable/disable wrappers, and DMA channel request helpers for offloaded TX/RX streams.

Important APIs, types, and functions: exported provider/consumer APIs include `devm_spi_offload_alloc()`, `devm_spi_offload_get()`, `devm_spi_offload_trigger_get()`, `spi_offload_trigger_validate()`, `spi_offload_trigger_enable()`, `spi_offload_trigger_disable()`, `devm_spi_offload_tx_stream_request_dma_chan()`, `devm_spi_offload_rx_stream_request_dma_chan()`, `devm_spi_offload_trigger_register()`, and `spi_offload_trigger_get_priv()`. Internal `struct spi_offload_trigger` has list linkage, `kref`, fwnode, lock, ops, and private pointer. A `spi_controller_and_offload` resource pairs `get_offload()` with balanced `put_offload()`.

Control flow: consumers call `devm_spi_offload_get()` on a `spi_device`; the controller's `get_offload()` supplies an instance and devm cleanup calls `put_offload()`. Trigger consumers read the provider device fwnode's `trigger-sources` reference, search the global list by fwnode and provider-specific `match()`, optionally call `request()`, then hold a kref until devm release. Enable first calls optional offload `trigger_enable()`, then trigger `enable()`, rolling back offload enable if trigger enable fails. Disable calls offload `trigger_disable()` and then trigger `disable()`.

State and persistence: global trigger list is protected by `spi_offload_triggers_lock`; each trigger has its own lock protecting ops/priv during calls and unregister. Unregister removes the list entry, nulls ops/priv, and drops the provider reference; outstanding consumers see `-ENODEV` through wrappers.

Dependencies and integration points: depends on SPI controller offload hooks, `linux/spi/offload/*` public types, fwnode reference args, devm actions, DMAEngine, mutexes, krefs, and exported namespace `SPI_OFFLOAD`.

Risks: `spi_offload_trigger_get()` calls provider `match()` while holding the global list lock and before taking the per-trigger lock, so provider unregister ordering depends on list removal and devm lifetimes. Enable/disable ordering is asymmetric: disable invokes offload disable before checking trigger ops. Consumers must balance trigger enable/disable and validate any mutated trigger config. DMA helpers assume provider returns channels that can be released with `dma_release_channel()`.

Test signals: controller without `get_offload`, invalid null args, provider probe deferral via unresolved trigger, request/release callbacks, provider unregister while consumer reference remains, enable rollback when trigger enable fails, unsupported DMA stream callbacks, and concurrent trigger lookup/register/unregister.

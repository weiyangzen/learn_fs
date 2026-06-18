<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/provider.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/offload/provider.h

Purpose: This header exposes the provider-side SPI offload API for controllers or companion devices that can supply offload engines and triggers.

Important APIs/types/functions: `devm_spi_offload_alloc()` allocates an offload with private storage. `spi_offload_trigger_ops` defines match, request, release, validate, enable, and disable callbacks. `spi_offload_trigger_info` binds a provider fwnode, ops, and private state. Providers register triggers with `devm_spi_offload_trigger_register()` and retrieve private trigger state with `spi_offload_trigger_get_priv()`.

Control flow: Provider drivers allocate offload instances, register trigger providers, match consumer requests by firmware node/type/args, validate runtime configs, and enable/disable hardware triggers.

State and persistence: Provider-private state hangs from offload and trigger info. Devres controls allocation/registration lifetime; hardware trigger state persists until disabled or device removal.

Dependencies/integration: Depends on SPI offload types, fwnode matching, module namespace import, and device-managed resource cleanup.

Risks and test signals: Risks include weak match semantics, trigger reference leaks, accepting invalid frequencies/offsets, and disabling callbacks not restoring hardware. Test multiple consumers, fwnode matching, validation bounds, enable/disable cycles, and provider removal with active consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/provider.h -->

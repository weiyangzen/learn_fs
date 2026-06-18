<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/offload/consumer.h

Purpose: This header exposes the consumer-side SPI offload API for peripheral drivers that want controller/provider hardware to execute SPI transfers triggered by external events or DMA streams.

Important APIs/types/functions: `devm_spi_offload_get()` acquires an offload instance for a `spi_device` and config. Trigger APIs acquire, validate, enable, and disable `spi_offload_trigger` objects. DMA helpers request managed TX/RX stream DMA channels. The module imports the `SPI_OFFLOAD` namespace.

Control flow: A consumer requests an offload, obtains a matching trigger, validates a trigger configuration, enables it around prepared transfers, and disables it during teardown or stop. Stream DMA requests are optional based on provider capabilities.

State and persistence: Managed devres lifetime controls offload, trigger, and DMA channel references. Runtime trigger enable state is held by provider implementations.

Dependencies/integration: Depends on SPI offload types, module namespaces, device-managed resources, DMA engine, and provider callbacks linked through `spi_controller.get_offload()`.

Risks and test signals: Risks include capability mismatch, enabling invalid trigger configs, DMA channel lifetime leaks, and leaving triggers enabled after device stop. Test devm cleanup, trigger validate failures, TX/RX stream transfers, provider absence, and suspend/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/consumer.h -->

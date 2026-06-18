<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/types.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/offload/types.h

Purpose: This header defines shared SPI offload data structures, capability flags, transfer flags, trigger configuration types, and provider operation callbacks.

Important APIs/types/functions: Transfer flags `SPI_OFFLOAD_XFER_TX_STREAM` and `SPI_OFFLOAD_XFER_RX_STREAM` identify transfers backed by external streams. Capability flags describe trigger support, static TX playback, and TX/RX stream DMA. `spi_offload_config` requests required capabilities. `spi_offload` holds provider device, provider-private pointer, ops, and supported transfer flags. Trigger config supports data-ready and periodic modes with frequency/offset. `spi_offload_ops` includes trigger enable/disable and optional TX/RX DMA channel request callbacks.

Control flow: Consumers request offloads by capabilities, configure triggers, then message transfers can mark offload-specific stream behavior using `spi_transfer.offload_flags`. Providers implement callbacks to arm hardware and expose DMA channels.

State and persistence: Offload instance state persists for the consumer/provider lifetime. Trigger runtime state is external but controlled through ops.

Dependencies/integration: Depends on `bits.h`, integer types, device references, DMA channels, and SPI core fields that reference `spi_offload`.

Risks and test signals: Risks include capability flag drift, using stream flags without matching DMA support, provider device reference leaks, and periodic trigger overflow/precision issues. Test capability negotiation, message optimization with offload, DMA channel request/release, periodic trigger timing, and inactive-provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/offload/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_spi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_spi.h

Purpose: defines the virtio SPI controller ABI for advertising controller capabilities and describing individual SPI transfers.

Important APIs and types: mode bits cover CPHA, CPOL, active-high chip select, LSB-first, and loopback. `struct virtio_spi_config` reports chip-select count, cs-change support, dual/quad/octal TX/RX widths, bits-per-word mask, supported mode functions, maximum frequency, and timing delays. `struct spi_transfer_head` describes chip select, bits per word, cs-change behavior, bus widths, mode, frequency, and delay timings. `struct spi_transfer_result` returns OK, parameter error, or transfer error.

Control flow, state, and persistence: the guest validates transfer parameters against config and submits transfer descriptors with data buffers; the device returns a per-transfer result. Bus/device state is held in the controller and attached SPI device.

Dependencies and integration points: depends on virtio config/IDs/types and integrates with Linux SPI controller APIs.

Risks and test signals: risks include invalid bus widths, unsupported mode combinations, timing-unit mistakes, chip-select toggling semantics, and result handling. Test single and multi-transfer messages, CPOL/CPHA modes, dual/quad/octal, frequency limits, and parameter rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_spi.h -->

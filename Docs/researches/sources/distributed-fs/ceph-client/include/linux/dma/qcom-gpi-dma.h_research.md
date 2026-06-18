<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom-gpi-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/qcom-gpi-dma.h

## Purpose
Defines Qualcomm GPI DMA peripheral configuration records for SPI and I2C transfers.

## Important APIs, Types, And Functions
SPI uses `enum spi_transfer_cmd` and `struct gpi_spi_config` with loopback, polarity, packing, word length, clock, chip select, fragmentation, config flag, command, and RX length fields. I2C uses `enum i2c_op` and `struct gpi_i2c_config` with packing, clock counts, address, stretch, config flag, RX length, operation, and multi-message flag.

## Control Flow
Peripheral drivers attach these configs to DMA descriptors so the GPI engine can perform protocol-aware SPI or I2C transactions. `set_config` indicates when static peripheral configuration should be emitted along with a transfer.

## State And Persistence
State is descriptor-level protocol configuration. No persistence exists beyond queued DMA transactions.

## Dependencies And Integration Points
Integrates Qualcomm SPI/I2C controller drivers with the GPI DMAengine.

## Risks And Edge Cases
Clock and polarity fields must match the peripheral controller setup. RX length and command/op fields must match buffer descriptors. Multi-message I2C transfers need correct repeated-start/sequence semantics.

## Test Signals
Tests should cover SPI TX/RX/duplex, chip-select fragmentation, packing, loopback, I2C read/write, multi-message transfers, clock-count programming, and invalid RX length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom-gpi-dma.h -->

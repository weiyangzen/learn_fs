# sources/distributed-fs/ceph-client/include/dt-bindings/dma/qcom-gpi.h

## Purpose
Defines Qualcomm GPI DMA protocol IDs for DT bindings.

## Important APIs, Types, and Constants
Exports `QCOM_GPI_SPI` 1, `QCOM_GPI_UART` 2, and `QCOM_GPI_I2C` 3. These values identify the peripheral protocol used by a GPI DMA channel.

## Control Flow and State
No local flow or state. Runtime protocol handling is implemented by the Qualcomm GPI DMA driver and firmware/hardware.

## Dependencies and Integration Points
Self-contained header included by Qualcomm DTS files for SPI, UART, and I2C DMA channel configuration.

## Risks and Test Signals
Wrong protocol ID can make the DMA engine interpret descriptors incorrectly. Test signals include DT schema validation and DMA-backed SPI, UART, and I2C transfer tests.

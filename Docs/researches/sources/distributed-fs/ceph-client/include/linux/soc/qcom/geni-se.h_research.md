# sources/distributed-fs/ceph-client/include/linux/soc/qcom/geni-se.h

Purpose: This Qualcomm header is the shared API/register definition for GENI/QUP Serial Engines used by SPI, I2C, I3C, UART, and related serial drivers.

Important APIs/types/functions: It defines transfer modes, protocol types, ICC paths, `struct geni_se`, common register offsets, IRQ/status/control bit masks, FIFO and DMA fields, hardware-version helpers, bandwidth constants, inline helpers for protocol reads, command setup/cancel/abort, FIFO depth/width reads, and exported functions for SE init, mode selection, packing, resources on/off, clock table/frequency matching, DMA prep/unprep, interconnect get/set/enable/disable/tag, and firmware loading.

Control flow: A serial driver initializes `struct geni_se`, turns resources on, configures FIFO/DMA/GPI mode, sets packing and clocks, issues master/secondary commands, handles IRQ or DMA completion, then disables resources.

State and persistence: State spans SE MMIO registers, clock/interconnect votes, DMA mappings, firmware protocol selection, command active bits, FIFOs, and IRQ masks.

Dependencies and integration: Uses MMIO accessors, clocks, DMA mapping, interconnect framework, and `CONFIG_QCOM_GENI_SE`. Integrates with Qualcomm QUP wrapper and serial peripheral drivers.

Risks and test signals: Hardware-version-specific FIFO depth, command abort/cancel races, ICC votes, and DMA cleanup are high risk. Test FIFO and DMA transfers, protocol detection, resource power cycling, suspend/resume, error IRQs, and disabled-config builds.

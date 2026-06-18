# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2_reg.h

Purpose: defines A83T MIPI CSI-2 receiver register offsets, magic initialization values, interrupt status/mask bits, and configuration field helpers.

Important APIs and constants: covers version/control/RX packet/reserved registers, extensive interrupt status and mask bit definitions for SOT/ECC/CRC/frame/line/data errors, configuration bits for sync, unpack, lane/channel count, sync delay, and VC/data-type routing registers.

Control flow: no executable flow. The controller writes init values during resume, configures lane/channel/unpack/sync settings during stream start, and writes VC-DT routing for channel 0.

State and persistence: hardware register description only.

Dependencies and integration points: consumed by `sun8i_a83t_mipi_csi2.c`; D-PHY register definitions live in the sibling D-PHY header.

Risks: many interrupt bits are defined but no IRQ handler is implemented in this driver, so error visibility depends on downstream failure signals or debug reads. Magic values for reserved registers are hardware-specific. Field helpers mask values without runtime validation.

Test signals: register-dump validation after runtime resume and stream start; hardware error-injection or noisy-link tests if interrupt handling is later added.

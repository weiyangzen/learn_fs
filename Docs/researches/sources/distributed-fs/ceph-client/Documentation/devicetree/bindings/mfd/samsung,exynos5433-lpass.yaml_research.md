# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,exynos5433-lpass.yaml

Purpose: Schema for the Samsung Exynos5433 Low Power Audio Subsystem MFD-style bus node, grouping audio DMA, I2S, and UART child devices under the LPASS register ranges and power domain.

Important schema surface and control flow: the node requires `compatible = "samsung,exynos5433-lpass"`, one clock named `sfr0_ctrl`, two `reg` ranges, `#address-cells = 1`, `#size-cells = 1`, and `ranges`. Optional `power-domains` ties the subsystem to the audio power domain. Child pattern properties reference PL330 DMA, Samsung I2S, and Samsung UART schemas based on unit-addressed node names.

State, dependencies, and integration: persistent DT defines LPASS MMIO windows, bus address translation, clocking, power domain membership, and child device layout. Dependencies include Exynos clock IDs, ARM GIC interrupt bindings, `/schemas/dma/arm,pl330.yaml`, `/schemas/sound/samsung-i2s.yaml`, and `/schemas/serial/samsung_uart.yaml`. Risks include missing `ranges`, incomplete child power-domain or clock definitions, and address/size cell mismatches that prevent child resources from translating. Test signals are `dt_binding_check`, child schema validation, and runtime probe of audio DMA, I2S DAI, and audio UART under the LPASS domain.

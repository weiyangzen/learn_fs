# sources/distributed-fs/ceph-client/arch/arm/boot/dts/microchip/sama7d65-pinfunc.h

Purpose: binding header for SAMA7D65 pin multiplexing. It provides named constants for DTS pinctrl groups across PA0 through PE13, covering roughly 142 pins and the SoC's modern peripheral matrix.

Important APIs/types/functions: `PINMUX_PIN(no, func, ioset)` uses the same Microchip packed integer layout as the SAMA5D2 and SAMA7G5 headers. Macros expose GPIO mode and alternates for SDMMC, multiple FLEXCOM instances, CAN, PWM, PCK, external IRQs, NAND/EBI address/data/control pins, G0/G1 Ethernet, ISC/LCDC display-camera pins, I2SMCC audio, PDMC, SPI, TWI, and timer signals.

Control flow: there is no executable control flow. Build-time macro substitution emits constants into DTB pinctrl properties; runtime interpretation happens in the Microchip pinctrl driver.

State and persistence: no state is stored here. DTBs persist the selected pin functions, while the live pin controller programs mux registers during boot or device probe.

Dependencies and integration: consumed by SAMA7D65 SoC and board DTS files. It depends on the Microchip pinctrl binding's expectation that a single cell carries pin, function, and IO set. Like related Microchip pinfunc headers, it is a pure macro file without a traditional include guard.

Risks: SAMA7D65 exposes many high-density shared functions; a wrong IO set can break peripheral routing even when the named function appears correct. Shared pins for SDMMC boot media, Ethernet, NAND, CAN, PWM, and audio are high impact. Test signals include `make ARCH=arm dtbs`, schema validation of pinctrl nodes, review against the datasheet mux table, and hardware smoke tests for boot media, console, Ethernet PHY link, CAN, and audio/display/camera interfaces touched by a DTS change.

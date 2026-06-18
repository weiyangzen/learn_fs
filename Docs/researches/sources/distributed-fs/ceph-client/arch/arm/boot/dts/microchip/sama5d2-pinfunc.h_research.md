# sources/distributed-fs/ceph-client/arch/arm/boot/dts/microchip/sama5d2-pinfunc.h

Purpose: declares SAMA5D2 pinmux constants for use by Microchip pinctrl DTS nodes. It maps package pins PA0 through PD31, 128 pins total, to GPIO and alternate peripheral functions.

Important APIs/types/functions: the key API is `PINMUX_PIN(no, func, ioset)`, encoding a 16-bit pin number, 4-bit function selector, and 8-bit IO set into one integer cell: pin in bits 0..15, function in bits 16..19, and IO set in bits 20..27. The file exports `PIN_PA0`, `PIN_PA0__GPIO`, and many `PIN_PAx__PERIPH` style macros for SDMMC, QSPI, SPI, TCB timers, FLEXCOM, NAND/EBI address/data pins, I2SC, ISC camera, UART, ADC trigger, IRQ, PCK, and JTAG functions.

Control flow: no runtime control flow. DTS preprocessor expansion produces encoded pinmux cells, and the Microchip pinctrl driver decodes those fields when applying a pin group.

State and persistence: no mutable state. The compiled DTB persists board pin choices; runtime state is held by pinctrl core and hardware registers, not by this header.

Dependencies and integration: integrated by SAMA5D2 `.dts`/`.dtsi` pinctrl groups and the Microchip/AT91 pinctrl binding. The header has no include guard, so it is intended for normal single-include DTS usage rather than repeated C inclusion.

Risks: incorrect `func` or `ioset` values can select a valid-looking but electrically wrong route, especially for multiplexed FLEXCOM, QSPI, SDMMC, NAND, and camera pins. Because the encoding is generic, `dtc` cannot know whether a board-level signal uses the correct IO set. Test with `make ARCH=arm dtbs`, binding checks for pinctrl consumers, and board-level boot validation of storage, serial console, network, display/camera, and interrupt lines.

# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt7623-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt7623-pinfunc.h` defines pinmux constants for the MediaTek MT7623 pin controller. The file was read as a complete 651-line header. It gives DTS authors symbolic constants for pin/function selections across the MT7623 router/networking SoC package.

The header exports 491 `#define` macros. Unlike the contiguous MT6795/MT6797/MT8135 headers in this group, MT7623 is sparse: the macros cover 153 unique pin numbers between 0 and 278, leaving 126 numeric gaps in that range. This reflects the SoC/package pin numbering used by the corresponding driver rather than an error in this header. Each value is encoded as `(MTK_PIN_NO(pin) | function)`, with GPIO selector 0 and alternate selector values 1 through 6.

## Important APIs, Types, and Functions

There are no C functions or types. The exported API is the macro namespace `MT7623_PIN_<n>_<ball_or_signal>_FUNC_<function>`, for example `MT7623_PIN_0_PWRAP_SPI0_MI_FUNC_PWRAP_SPIDO`, `MT7623_PIN_7_SPI1_CSN_FUNC_SPI1_CS`, `MT7623_PIN_18_PCM_CLK_FUNC_PCM_CLK0`, `MT7623_PIN_75_SDA0_FUNC_SDA0`, `MT7623_PIN_111_MSDC0_DAT7_FUNC_MSDC0_DAT7`, `MT7623_PIN_262_G2_TXD0_FUNC_G2_TXD0`, `MT7623_PIN_275_G2_MDC_FUNC_MDC`, and `MT7623_PIN_278_JTAG_RESET_FUNC_JTAG_RESET`.

The naming carries both a pin number and a primary pad/signal label before `_FUNC_`, which is useful for a sparse SoC map. The most common families in the file are connectivity/debug, PCM/audio, AP/MD debug, Ethernet G1/G2, MSDC, PWRAP, SPI, I2C, UART, USB OTG, PCIe, HDMI, NAND, MIPI, and JTAG.

## Control Flow

The header has no executable flow. DTS preprocessing turns each selected macro into a packed pinmux integer. The MT7623 pinctrl driver then decodes the integer and programs mode registers based on its `mt7623_pins`, function, and group tables.

The MT7623 driver has explicit pin/function group arrays for many peripherals, including Ethernet switch, EPHY, external SDIO, HDMI, I2C alternatives, I2S alternatives, MDC/MDIO, multiple MSDC ports, NAND, USB OTG ID/VBUS, PCIe reset/wake/clock request, and UART/SPI paths. This header's macro values must match those group function selectors.

## State and Persistence Behavior

No mutable kernel state is declared here. The file is a stable binding input: once a DTS references a macro, the resulting DTB persists the encoded pin/function selection. The include guard `__DTS_MT7623_PINFUNC_H` protects the macro definitions during preprocessing.

The sparse numbering is a state-contract detail. Consumers must not assume `pin_max + 1` macros or contiguous GPIO coverage from this header; they must rely on the pinctrl driver's advertised pin descriptors and groups.

## Dependencies and Integration Points

The direct include is `dt-bindings/pinctrl/mt65xx.h`, which provides the common MediaTek encoding and decode helpers. The main integration point is `drivers/pinctrl/mediatek/pinctrl-mt7623.c`, which defines the MT7623 register ranges, `mt7623_pins` descriptors, group pins, group functions, and `mt7623_reg_cals`.

Hardware integration surfaces are broad but skew toward networking and board I/O: PWRAP, SPI0-SPI2, keypad columns, UARTs, PCM/I2S/MRG audio, connectivity DSP/JTAG, external frame sync, I2C, MSDC0-MSDC3, NAND, HDMI and MIPI display, USB OTG ID/VBUS, PCIe, Ethernet G1/G2, MDC/MDIO, EPHY/ESW reset and interrupt, and JTAG reset.

## Risks and Edge Cases

The sparse pin map is the most important edge case. A mechanical checker that expects all numbers 0 through 278 to exist would report false positives; a better checker validates only macro-to-`MTK_PIN_NO()` consistency and cross-references the driver's descriptor table. Conversely, adding a missing-looking pin without matching driver support could create an unusable binding name.

Another risk is mismatch between this dt-binding header and the MT7623 driver's group arrays. For example, some driver group arrays use higher function values for alternate/reversed PCIe functions that are not represented by this header's 0-6 selectors, so board authors should use only published binding macros unless the driver binding is extended deliberately. Selector mistakes can disable boot-critical storage, Ethernet, or serial console pins while still passing compilation.

## Test Signals

Static tests should confirm that each macro's numeric `MTK_PIN_NO()` matches the pin number in `MT7623_PIN_<n>_...`, that GPIO alternatives use selector 0, and that no selector exceeds the shared 4-bit function field. DTS/DTC builds for MT7623 boards should catch missing names. Runtime signals include working serial console, PWRAP, MMC/SD, NAND where used, Ethernet G1/G2 and MDIO/MDC, USB/PCIe, I2C/SPI, HDMI/display, and absence of MediaTek pinctrl warnings while applying board pin states.

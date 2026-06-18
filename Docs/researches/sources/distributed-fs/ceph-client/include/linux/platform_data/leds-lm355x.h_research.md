# sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h

## Purpose
`leds-lm355x.h` is a Linux kernel LED/flash/backlight board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lm355x_platform_data`; enumerations such as `enum lm355x_strobe`, `enum lm355x_torch` into
the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LM355x_NAME`, `LM3554_NAME`, `LM3556_NAME`. Types: `struct lm355x_platform_data`,
`enum lm355x_strobe`, `enum lm355x_torch`, `enum lm355x_tx2`, `enum lm355x_ntc`, `enum
lm355x_pmode`. Declared or inline functions: none visible in this header. Important struct details:
struct lm355x_platform_data fields include `enum lm355x_strobe pin_strobe`, `enum lm355x_torch
pin_tx1`, `enum lm355x_tx2 pin_tx2`, `enum lm355x_ntc ntc_pin`, `enum lm355x_pmode pass_mode`.
Important enum details: enum lm355x_strobe values include `LM355x_PIN_STROBE_DISABLE`,
`LM355x_PIN_STROBE_ENABLE`; enum lm355x_torch values include `LM355x_PIN_TORCH_DISABLE`,
`LM3554_PIN_TORCH_ENABLE`, `LM3556_PIN_TORCH_ENABLE`; enum lm355x_tx2 values include
`LM355x_PIN_TX_DISABLE`, `LM3554_PIN_TX_ENABLE`, `LM3556_PIN_TX_ENABLE`; enum lm355x_ntc values
include `LM355x_PIN_NTC_DISABLE`, `LM3554_PIN_NTC_ENABLE`, `LM3556_PIN_NTC_ENABLE`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/leds/leds-lm355x.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/leds/leds-lm355x.c`. It integrates through `struct platform_device` platform data,
board files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace
parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h` completely for this pass (65 lines, 1454 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h_research.md`.

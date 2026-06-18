# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h

## Purpose
`usb-musb-ux500.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct ux500_musb_board_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ASM_ARCH_USB_H`, `UX500_MUSB_DMA_NUM_RX_TX_CHANNELS`. Types: `struct
ux500_musb_board_data`. Declared or inline functions: `bool`. Important struct details: struct
ux500_musb_board_data fields include `void **dma_rx_param_array`, `void **dma_tx_param_array`, `bool
(*dma_filter)(struct dma_chan *chan, void *filter_param)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/musb/ux500_dma.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/dmaengine.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c`. It integrates through `struct
platform_device` platform data, board files, MFD child registration, and legacy non-DT setup paths;
many modern systems may replace parts of this contract with Device Tree, ACPI, or software-node
properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h` completely for this pass (22 lines, 558 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h_research.md`.

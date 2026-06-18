# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun8i-v3s-ccu.h

Source read summary: 82 lines, 2930 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun8i-v3s-ccu.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 27 visible constants or packing macros; representative names are `RST_USB_PHY0`, `RST_MBUS`, `RST_BUS_CE`, `RST_BUS_DMA`, `RST_BUS_MMC0`, `RST_BUS_MMC1`, `RST_BUS_MMC2`, `RST_BUS_DRAM`, `RST_BUS_EMAC`, `RST_BUS_HSTIMER`, `RST_BUS_SPI0`, `RST_BUS_OTG`, `RST_BUS_EHCI0`, `RST_BUS_OHCI0`, `RST_BUS_VE`, `RST_BUS_TCON0` and 11 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

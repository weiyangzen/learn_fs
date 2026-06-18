# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-usb.h

Source read summary: 57 lines, 2314 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-usb.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 8 visible constants or packing macros; representative names are `RST_USB0_HCI`, `RST_USB1_HCI`, `RST_USB2_HCI`, `RST_USB0_PHY`, `RST_USB1_HSIC`, `RST_USB1_PHY`, `RST_USB2_HSIC`, `RST_USB2_PHY`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

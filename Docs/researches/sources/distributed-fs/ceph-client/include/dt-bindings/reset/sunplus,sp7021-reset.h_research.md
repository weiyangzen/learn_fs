# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sunplus,sp7021-reset.h

Source read summary: 88 lines, 2923 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sunplus,sp7021-reset.h` declares numeric reset IDs for the Sunplus SP7021 reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 77 visible constants or packing macros; representative names are `RST_SYSTEM`, `RST_RTC`, `RST_IOCTL`, `RST_IOP`, `RST_OTPRX`, `RST_NOC`, `RST_BR`, `RST_RBUS_L00`, `RST_SPIFL`, `RST_SDCTRL0`, `RST_PERI0`, `RST_A926`, `RST_UMCTL2`, `RST_PERI1`, `RST_DDR_PHY0`, `RST_ACHIP` and 61 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

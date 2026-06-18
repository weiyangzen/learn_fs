# sources/distributed-fs/ceph-client/include/dt-bindings/reset/thead,th1520-reset.h

Source read summary: 237 lines, 8382 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/thead,th1520-reset.h` declares numeric reset IDs for the T-Head TH1520 reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 212 visible constants or packing macros; representative names are `TH1520_RESET_ID_SYSTEM`, `TH1520_RESET_ID_RTC_APB`, `TH1520_RESET_ID_RTC_REF`, `TH1520_RESET_ID_AOGPIO_DB`, `TH1520_RESET_ID_AOGPIO_APB`, `TH1520_RESET_ID_AOI2C_APB`, `TH1520_RESET_ID_PVT_APB`, `TH1520_RESET_ID_E902_CORE`, `TH1520_RESET_ID_E902_HAD`, `TH1520_RESET_ID_AOTIMER_APB`, `TH1520_RESET_ID_AOTIMER_CORE`, `TH1520_RESET_ID_AOWDT_APB`, `TH1520_RESET_ID_APSYS`, `TH1520_RESET_ID_NPUSYS`, `TH1520_RESET_ID_DDRSYS`, `TH1520_RESET_ID_AXI_AP2CP` and 196 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

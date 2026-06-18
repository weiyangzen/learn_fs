# sources/distributed-fs/ceph-client/include/dt-bindings/reset/ti-syscon.h

Source read summary: 30 lines, 777 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/ti-syscon.h` declares numeric reset IDs for the TI syscon reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `ASSERT_NONE`, `DEASSERT_NONE`, `STATUS_NONE`, `ASSERT_SET`, `DEASSERT_SET`, `STATUS_SET`, `ASSERT_CLEAR`, `DEASSERT_CLEAR`, `STATUS_CLEAR`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

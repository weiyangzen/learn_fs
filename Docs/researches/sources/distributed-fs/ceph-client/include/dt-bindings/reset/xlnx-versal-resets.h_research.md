# sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-versal-resets.h

Source read summary: 106 lines, 4143 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-versal-resets.h` declares numeric reset IDs for the Xilinx Versal reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 95 visible constants or packing macros; representative names are `VERSAL_RST_PMC_POR`, `VERSAL_RST_PMC`, `VERSAL_RST_PS_POR`, `VERSAL_RST_PL_POR`, `VERSAL_RST_NOC_POR`, `VERSAL_RST_FPD_POR`, `VERSAL_RST_ACPU_0_POR`, `VERSAL_RST_ACPU_1_POR`, `VERSAL_RST_OCM2_POR`, `VERSAL_RST_PS_SRST`, `VERSAL_RST_PL_SRST`, `VERSAL_RST_NOC`, `VERSAL_RST_NPI`, `VERSAL_RST_SYS_RST_1`, `VERSAL_RST_SYS_RST_2`, `VERSAL_RST_SYS_RST_3` and 79 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

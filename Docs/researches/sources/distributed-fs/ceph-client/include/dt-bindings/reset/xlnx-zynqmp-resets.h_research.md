# sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-zynqmp-resets.h

Source read summary: 131 lines, 4259 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-zynqmp-resets.h` declares numeric reset IDs for the Xilinx ZynqMP reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 120 visible constants or packing macros; representative names are `ZYNQMP_RESET_PCIE_CFG`, `ZYNQMP_RESET_PCIE_BRIDGE`, `ZYNQMP_RESET_PCIE_CTRL`, `ZYNQMP_RESET_DP`, `ZYNQMP_RESET_SWDT_CRF`, `ZYNQMP_RESET_AFI_FM5`, `ZYNQMP_RESET_AFI_FM4`, `ZYNQMP_RESET_AFI_FM3`, `ZYNQMP_RESET_AFI_FM2`, `ZYNQMP_RESET_AFI_FM1`, `ZYNQMP_RESET_AFI_FM0`, `ZYNQMP_RESET_GDMA`, `ZYNQMP_RESET_GPU_PP1`, `ZYNQMP_RESET_GPU_PP0`, `ZYNQMP_RESET_GPU`, `ZYNQMP_RESET_GT` and 104 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

# sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra234-reset.h

Source read summary: 183 lines, 6787 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra234-reset.h` declares numeric reset IDs for the NVIDIA Tegra reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 166 visible constants or packing macros; representative names are `TEGRA234_RESET_ACTMON`, `TEGRA234_RESET_ADSP_ALL`, `TEGRA234_RESET_DSI_CORE`, `TEGRA234_RESET_CAN1`, `TEGRA234_RESET_CAN2`, `TEGRA234_RESET_DLA0`, `TEGRA234_RESET_DLA1`, `TEGRA234_RESET_DPAUX`, `TEGRA234_RESET_OFA`, `TEGRA234_RESET_NVJPG1`, `TEGRA234_RESET_PEX1_CORE_6`, `TEGRA234_RESET_PEX1_CORE_6_APB`, `TEGRA234_RESET_PEX1_COMMON_APB`, `TEGRA234_RESET_PEX2_CORE_7`, `TEGRA234_RESET_PEX2_CORE_7_APB`, `TEGRA234_RESET_NVDISPLAY` and 150 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.

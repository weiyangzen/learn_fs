# subset-b-005833 Research

Grouped research report for device-tree binding, Hyper-V ABI, key-management, and KUnit helper headers. Each section preserves the source path in its title and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun8i-v3s-ccu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun8i-v3s-ccu.h

Source read summary: 82 lines, 2930 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun8i-v3s-ccu.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 27 visible constants or packing macros; representative names are `RST_USB_PHY0`, `RST_MBUS`, `RST_BUS_CE`, `RST_BUS_DMA`, `RST_BUS_MMC0`, `RST_BUS_MMC1`, `RST_BUS_MMC2`, `RST_BUS_DRAM`, `RST_BUS_EMAC`, `RST_BUS_HSTIMER`, `RST_BUS_SPI0`, `RST_BUS_OTG`, `RST_BUS_EHCI0`, `RST_BUS_OHCI0`, `RST_BUS_VE`, `RST_BUS_TCON0` and 11 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun8i-v3s-ccu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-ccu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-ccu.h

Source read summary: 103 lines, 3414 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-ccu.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 51 visible constants or packing macros; representative names are `RST_BUS_FD`, `RST_BUS_VE`, `RST_BUS_GPU_CTRL`, `RST_BUS_SS`, `RST_BUS_MMC`, `RST_BUS_NAND0`, `RST_BUS_NAND1`, `RST_BUS_SDRAM`, `RST_BUS_SATA`, `RST_BUS_TS`, `RST_BUS_SPI0`, `RST_BUS_SPI1`, `RST_BUS_SPI2`, `RST_BUS_SPI3`, `RST_BUS_OTG`, `RST_BUS_OTG_PHY` and 35 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-ccu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-de.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-de.h

Source read summary: 59 lines, 2335 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-de.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 11 visible constants or packing macros; representative names are `RST_FE0`, `RST_FE1`, `RST_FE2`, `RST_DEU0`, `RST_DEU1`, `RST_BE0`, `RST_BE1`, `RST_BE2`, `RST_DRC0`, `RST_DRC1`, `RST_MERGE`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-de.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-usb.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-usb.h

Source read summary: 57 lines, 2314 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-usb.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 8 visible constants or packing macros; representative names are `RST_USB0_HCI`, `RST_USB1_HCI`, `RST_USB2_HCI`, `RST_USB0_PHY`, `RST_USB1_HSIC`, `RST_USB1_PHY`, `RST_USB2_HSIC`, `RST_USB2_PHY`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sun9i-a80-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/suniv-ccu-f1c100s.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/suniv-ccu-f1c100s.h

Source read summary: 39 lines, 912 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/suniv-ccu-f1c100s.h` declares numeric reset IDs for the Allwinner clock/reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 27 visible constants or packing macros; representative names are `RST_USB_PHY0`, `RST_BUS_DMA`, `RST_BUS_MMC0`, `RST_BUS_MMC1`, `RST_BUS_DRAM`, `RST_BUS_SPI0`, `RST_BUS_SPI1`, `RST_BUS_OTG`, `RST_BUS_VE`, `RST_BUS_LCD`, `RST_BUS_DEINTERLACE`, `RST_BUS_CSI`, `RST_BUS_TVD`, `RST_BUS_TVE`, `RST_BUS_DE_BE`, `RST_BUS_DE_FE` and 11 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/suniv-ccu-f1c100s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sunplus,sp7021-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/sunplus,sp7021-reset.h

Source read summary: 88 lines, 2923 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/sunplus,sp7021-reset.h` declares numeric reset IDs for the Sunplus SP7021 reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 77 visible constants or packing macros; representative names are `RST_SYSTEM`, `RST_RTC`, `RST_IOCTL`, `RST_IOP`, `RST_OTPRX`, `RST_NOC`, `RST_BR`, `RST_RBUS_L00`, `RST_SPIFL`, `RST_SDCTRL0`, `RST_PERI0`, `RST_A926`, `RST_UMCTL2`, `RST_PERI1`, `RST_DDR_PHY0`, `RST_ACHIP` and 61 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/sunplus,sp7021-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra124-car.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra124-car.h

Source read summary: 14 lines, 360 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra124-car.h` declares numeric reset IDs for the NVIDIA Tegra reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 2 visible constants or packing macros; representative names are `TEGRA124_RST_DFLL_DVCO`, `TEGRA124_RESET`. Function-like helpers include `TEGRA124_RESET`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra124-car.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra186-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra186-reset.h

Source read summary: 207 lines, 7455 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra186-reset.h` declares numeric reset IDs for the NVIDIA Tegra reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 194 visible constants or packing macros; representative names are `TEGRA186_RESET_ACTMON`, `TEGRA186_RESET_AFI`, `TEGRA186_RESET_CEC`, `TEGRA186_RESET_CSITE`, `TEGRA186_RESET_DP2`, `TEGRA186_RESET_DPAUX`, `TEGRA186_RESET_DSI`, `TEGRA186_RESET_DSIB`, `TEGRA186_RESET_DTV`, `TEGRA186_RESET_DVFS`, `TEGRA186_RESET_ENTROPY`, `TEGRA186_RESET_EXTPERIPH1`, `TEGRA186_RESET_EXTPERIPH2`, `TEGRA186_RESET_EXTPERIPH3`, `TEGRA186_RESET_GPU`, `TEGRA186_RESET_HDA` and 178 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra186-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra194-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra194-reset.h

Source read summary: 153 lines, 5536 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra194-reset.h` declares numeric reset IDs for the NVIDIA Tegra reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 144 visible constants or packing macros; representative names are `TEGRA194_RESET_ACTMON`, `TEGRA194_RESET_ADSP_ALL`, `TEGRA194_RESET_AFI`, `TEGRA194_RESET_CAN1`, `TEGRA194_RESET_CAN2`, `TEGRA194_RESET_DLA0`, `TEGRA194_RESET_DLA1`, `TEGRA194_RESET_DPAUX`, `TEGRA194_RESET_DPAUX1`, `TEGRA194_RESET_DPAUX2`, `TEGRA194_RESET_DPAUX3`, `TEGRA194_RESET_EQOS`, `TEGRA194_RESET_GPCDMA`, `TEGRA194_RESET_GPU`, `TEGRA194_RESET_HDA`, `TEGRA194_RESET_HDA2CODEC_2X` and 128 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra194-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra210-car.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra210-car.h

Source read summary: 15 lines, 405 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra210-car.h` declares numeric reset IDs for the NVIDIA Tegra reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 3 visible constants or packing macros; representative names are `TEGRA210_RST_DFLL_DVCO`, `TEGRA210_RST_ADSP`, `TEGRA210_RESET`. Function-like helpers include `TEGRA210_RESET`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra210-car.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra234-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra234-reset.h

Source read summary: 183 lines, 6787 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra234-reset.h` declares numeric reset IDs for the NVIDIA Tegra reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 166 visible constants or packing macros; representative names are `TEGRA234_RESET_ACTMON`, `TEGRA234_RESET_ADSP_ALL`, `TEGRA234_RESET_DSI_CORE`, `TEGRA234_RESET_CAN1`, `TEGRA234_RESET_CAN2`, `TEGRA234_RESET_DLA0`, `TEGRA234_RESET_DLA1`, `TEGRA234_RESET_DPAUX`, `TEGRA234_RESET_OFA`, `TEGRA234_RESET_NVJPG1`, `TEGRA234_RESET_PEX1_CORE_6`, `TEGRA234_RESET_PEX1_CORE_6_APB`, `TEGRA234_RESET_PEX1_COMMON_APB`, `TEGRA234_RESET_PEX2_CORE_7`, `TEGRA234_RESET_PEX2_CORE_7_APB`, `TEGRA234_RESET_NVDISPLAY` and 150 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/tegra234-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/thead,th1520-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/thead,th1520-reset.h

Source read summary: 237 lines, 8382 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/thead,th1520-reset.h` declares numeric reset IDs for the T-Head TH1520 reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 212 visible constants or packing macros; representative names are `TH1520_RESET_ID_SYSTEM`, `TH1520_RESET_ID_RTC_APB`, `TH1520_RESET_ID_RTC_REF`, `TH1520_RESET_ID_AOGPIO_DB`, `TH1520_RESET_ID_AOGPIO_APB`, `TH1520_RESET_ID_AOI2C_APB`, `TH1520_RESET_ID_PVT_APB`, `TH1520_RESET_ID_E902_CORE`, `TH1520_RESET_ID_E902_HAD`, `TH1520_RESET_ID_AOTIMER_APB`, `TH1520_RESET_ID_AOTIMER_CORE`, `TH1520_RESET_ID_AOWDT_APB`, `TH1520_RESET_ID_APSYS`, `TH1520_RESET_ID_NPUSYS`, `TH1520_RESET_ID_DDRSYS`, `TH1520_RESET_ID_AXI_AP2CP` and 196 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/thead,th1520-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/ti-syscon.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/ti-syscon.h

Source read summary: 30 lines, 777 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/ti-syscon.h` declares numeric reset IDs for the TI syscon reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `ASSERT_NONE`, `DEASSERT_NONE`, `STATUS_NONE`, `ASSERT_SET`, `DEASSERT_SET`, `STATUS_SET`, `ASSERT_CLEAR`, `DEASSERT_CLEAR`, `STATUS_CLEAR`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/ti-syscon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/toshiba,tmpv770x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/toshiba,tmpv770x.h

Source read summary: 49 lines, 1636 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/toshiba,tmpv770x.h` declares numeric reset IDs for the Toshiba TMPV770x reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 40 visible constants or packing macros; representative names are `TMPV770X_RESET_PIETHER_2P5M`, `TMPV770X_RESET_PIETHER_25M`, `TMPV770X_RESET_PIETHER_50M`, `TMPV770X_RESET_PIETHER_125M`, `TMPV770X_RESET_HOX`, `TMPV770X_RESET_PCIE_MSTR`, `TMPV770X_RESET_PCIE_AUX`, `TMPV770X_RESET_PIINTC`, `TMPV770X_RESET_PIETHER_BUS`, `TMPV770X_RESET_PISPI0`, `TMPV770X_RESET_PISPI1`, `TMPV770X_RESET_PISPI2`, `TMPV770X_RESET_PISPI3`, `TMPV770X_RESET_PISPI4`, `TMPV770X_RESET_PISPI5`, `TMPV770X_RESET_PISPI6` and 24 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/toshiba,tmpv770x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-versal-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-versal-resets.h

Source read summary: 106 lines, 4143 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-versal-resets.h` declares numeric reset IDs for the Xilinx Versal reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 95 visible constants or packing macros; representative names are `VERSAL_RST_PMC_POR`, `VERSAL_RST_PMC`, `VERSAL_RST_PS_POR`, `VERSAL_RST_PL_POR`, `VERSAL_RST_NOC_POR`, `VERSAL_RST_FPD_POR`, `VERSAL_RST_ACPU_0_POR`, `VERSAL_RST_ACPU_1_POR`, `VERSAL_RST_OCM2_POR`, `VERSAL_RST_PS_SRST`, `VERSAL_RST_PL_SRST`, `VERSAL_RST_NOC`, `VERSAL_RST_NPI`, `VERSAL_RST_SYS_RST_1`, `VERSAL_RST_SYS_RST_2`, `VERSAL_RST_SYS_RST_3` and 79 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-versal-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-zynqmp-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-zynqmp-resets.h

Source read summary: 131 lines, 4259 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-zynqmp-resets.h` declares numeric reset IDs for the Xilinx ZynqMP reset controller. Device-tree reset specifiers use these names instead of raw integers when wiring consumers to reset-controller cells.

Important APIs, types, and functions: The file exports 120 visible constants or packing macros; representative names are `ZYNQMP_RESET_PCIE_CFG`, `ZYNQMP_RESET_PCIE_BRIDGE`, `ZYNQMP_RESET_PCIE_CTRL`, `ZYNQMP_RESET_DP`, `ZYNQMP_RESET_SWDT_CRF`, `ZYNQMP_RESET_AFI_FM5`, `ZYNQMP_RESET_AFI_FM4`, `ZYNQMP_RESET_AFI_FM3`, `ZYNQMP_RESET_AFI_FM2`, `ZYNQMP_RESET_AFI_FM1`, `ZYNQMP_RESET_AFI_FM0`, `ZYNQMP_RESET_GDMA`, `ZYNQMP_RESET_GPU_PP1`, `ZYNQMP_RESET_GPU_PP0`, `ZYNQMP_RESET_GPU`, `ZYNQMP_RESET_GT` and 104 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS nodes include this header, place a macro in a `resets = <...>` entry, and the reset-controller driver translates the cell number to the SoC register bit or firmware reset line.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: These constants form a stable device-tree ABI. Renumbering, aliasing an ID to the wrong hardware line, or mixing headers from a related SoC can reset the wrong block or keep a dependent driver permanently asserted.

Test signals: Compile board DTS files, compare every ID with clock/reset-controller tables, and boot-test consumers that assert/deassert each reset path during probe, suspend, and error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/xlnx-zynqmp-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm-pmb.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm-pmb.h

Source read summary: 13 lines, 288 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm-pmb.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 5 visible constants or packing macros; representative names are `BCM_PMB_PCIE0`, `BCM_PMB_PCIE1`, `BCM_PMB_PCIE2`, `BCM_PMB_HOST_USB`, `BCM_PMB_SATA`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm-pmb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm2835-pm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm2835-pm.h

Source read summary: 29 lines, 845 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm2835-pm.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 18 visible constants or packing macros; representative names are `BCM2835_POWER_DOMAIN_GRAFX`, `BCM2835_POWER_DOMAIN_GRAFX_V3D`, `BCM2835_POWER_DOMAIN_IMAGE`, `BCM2835_POWER_DOMAIN_IMAGE_PERI`, `BCM2835_POWER_DOMAIN_IMAGE_ISP`, `BCM2835_POWER_DOMAIN_IMAGE_H264`, `BCM2835_POWER_DOMAIN_USB`, `BCM2835_POWER_DOMAIN_DSI0`, `BCM2835_POWER_DOMAIN_DSI1`, `BCM2835_POWER_DOMAIN_CAM0`, `BCM2835_POWER_DOMAIN_CAM1`, `BCM2835_POWER_DOMAIN_CCP2TX`, `BCM2835_POWER_DOMAIN_HDMI`, `BCM2835_POWER_DOMAIN_COUNT`, `BCM2835_RESET_V3D`, `BCM2835_RESET_ISP` and 2 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm2835-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6318-pm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6318-pm.h

Source read summary: 18 lines, 538 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6318-pm.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 10 visible constants or packing macros; representative names are `BCM6318_POWER_DOMAIN_PCIE`, `BCM6318_POWER_DOMAIN_USB`, `BCM6318_POWER_DOMAIN_EPHY0`, `BCM6318_POWER_DOMAIN_EPHY1`, `BCM6318_POWER_DOMAIN_EPHY2`, `BCM6318_POWER_DOMAIN_EPHY3`, `BCM6318_POWER_DOMAIN_LDO2P5`, `BCM6318_POWER_DOMAIN_LDO2P9`, `BCM6318_POWER_DOMAIN_SW1P0`, `BCM6318_POWER_DOMAIN_PAD`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6318-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm63268-pm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm63268-pm.h

Source read summary: 22 lines, 712 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm63268-pm.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 14 visible constants or packing macros; representative names are `BCM63268_POWER_DOMAIN_SAR`, `BCM63268_POWER_DOMAIN_IPSEC`, `BCM63268_POWER_DOMAIN_MIPS`, `BCM63268_POWER_DOMAIN_DECT`, `BCM63268_POWER_DOMAIN_USBH`, `BCM63268_POWER_DOMAIN_USBD`, `BCM63268_POWER_DOMAIN_ROBOSW`, `BCM63268_POWER_DOMAIN_PCM`, `BCM63268_POWER_DOMAIN_PERIPH`, `BCM63268_POWER_DOMAIN_VDSL_PHY`, `BCM63268_POWER_DOMAIN_VDSL_MIPS`, `BCM63268_POWER_DOMAIN_FAP`, `BCM63268_POWER_DOMAIN_PCIE`, `BCM63268_POWER_DOMAIN_WLAN_PADS`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm63268-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6328-pm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6328-pm.h

Source read summary: 18 lines, 547 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6328-pm.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 10 visible constants or packing macros; representative names are `BCM6328_POWER_DOMAIN_ADSL2_MIPS`, `BCM6328_POWER_DOMAIN_ADSL2_PHY`, `BCM6328_POWER_DOMAIN_ADSL2_AFE`, `BCM6328_POWER_DOMAIN_SAR`, `BCM6328_POWER_DOMAIN_PCM`, `BCM6328_POWER_DOMAIN_USBD`, `BCM6328_POWER_DOMAIN_USBH`, `BCM6328_POWER_DOMAIN_PCIE`, `BCM6328_POWER_DOMAIN_ROBOSW`, `BCM6328_POWER_DOMAIN_EPHY`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6328-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6362-pm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6362-pm.h

Source read summary: 22 lines, 695 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6362-pm.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 14 visible constants or packing macros; representative names are `BCM6362_POWER_DOMAIN_SAR`, `BCM6362_POWER_DOMAIN_IPSEC`, `BCM6362_POWER_DOMAIN_MIPS`, `BCM6362_POWER_DOMAIN_DECT`, `BCM6362_POWER_DOMAIN_USBH`, `BCM6362_POWER_DOMAIN_USBD`, `BCM6362_POWER_DOMAIN_ROBOSW`, `BCM6362_POWER_DOMAIN_PCM`, `BCM6362_POWER_DOMAIN_PERIPH`, `BCM6362_POWER_DOMAIN_ADSL_PHY`, `BCM6362_POWER_DOMAIN_GMII_PADS`, `BCM6362_POWER_DOMAIN_FAP`, `BCM6362_POWER_DOMAIN_PCIE`, `BCM6362_POWER_DOMAIN_WLAN_PADS`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6362-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/cpm1-fsl,tsa.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/cpm1-fsl,tsa.h

Source read summary: 14 lines, 342 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/cpm1-fsl,tsa.h` declares device-tree constants for the Freescale PowerQUICC time-slot assigner binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 6 visible constants or packing macros; representative names are `FSL_CPM_TSA_NU`, `FSL_CPM_TSA_SCC2`, `FSL_CPM_TSA_SCC3`, `FSL_CPM_TSA_SCC4`, `FSL_CPM_TSA_SMC1`, `FSL_CPM_TSA_SMC2`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/cpm1-fsl,tsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,apr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,apr.h

Source read summary: 29 lines, 706 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,apr.h` declares device-tree constants for the Qualcomm subsystem binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 19 visible constants or packing macros; representative names are `APR_DOMAIN_SIM`, `APR_DOMAIN_PC`, `APR_DOMAIN_MODEM`, `APR_DOMAIN_ADSP`, `APR_DOMAIN_APPS`, `APR_DOMAIN_MAX`, `APR_SVC_ADSP_CORE`, `APR_SVC_AFE`, `APR_SVC_VSM`, `APR_SVC_VPM`, `APR_SVC_ASM`, `APR_SVC_ADM`, `APR_SVC_ADSP_MVM`, `APR_SVC_ADSP_CVS`, `APR_SVC_ADSP_CVP`, `APR_SVC_USM` and 3 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,apr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gpr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gpr.h

Source read summary: 20 lines, 411 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gpr.h` declares device-tree constants for the Qualcomm subsystem binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 7 visible constants or packing macros; representative names are `GPR_DOMAIN_ID_MODEM`, `GPR_DOMAIN_ID_ADSP`, `GPR_DOMAIN_ID_APPS`, `GPR_APM_MODULE_IID`, `GPR_PRM_MODULE_IID`, `GPR_AMDB_MODULE_IID`, `GPR_VCPM_MODULE_IID`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gpr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gsbi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gsbi.h

Source read summary: 19 lines, 431 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gsbi.h` declares device-tree constants for the Qualcomm subsystem binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `GSBI_PROT_IDLE`, `GSBI_PROT_I2C_UIM`, `GSBI_PROT_I2C`, `GSBI_PROT_SPI`, `GSBI_PROT_UART_W_FC`, `GSBI_PROT_UIM`, `GSBI_PROT_I2C_UART`, `GSBI_CRCI_QUP`, `GSBI_CRCI_UART`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,gsbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,rpmh-rsc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,rpmh-rsc.h

Source read summary: 15 lines, 300 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,rpmh-rsc.h` declares device-tree constants for the Qualcomm subsystem binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 4 visible constants or packing macros; representative names are `SLEEP_TCS`, `WAKE_TCS`, `ACTIVE_TCS`, `CONTROL_TCS`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qcom,rpmh-rsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qe-fsl,tsa.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/qe-fsl,tsa.h

Source read summary: 14 lines, 308 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/qe-fsl,tsa.h` declares device-tree constants for the Freescale PowerQUICC time-slot assigner binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 6 visible constants or packing macros; representative names are `FSL_QE_TSA_NU`, `FSL_QE_TSA_UCC1`, `FSL_QE_TSA_UCC2`, `FSL_QE_TSA_UCC3`, `FSL_QE_TSA_UCC4`, `FSL_QE_TSA_UCC5`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/qe-fsl,tsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,boot-mode.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,boot-mode.h

Source read summary: 17 lines, 452 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,boot-mode.h` declares device-tree constants for the Rockchip SoC binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 5 visible constants or packing macros; representative names are `REBOOT_FLAG`, `BOOT_NORMAL`, `BOOT_BL_DOWNLOAD`, `BOOT_RECOVERY`, `BOOT_FASTBOOT`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,boot-mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,vop2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,vop2.h

Source read summary: 19 lines, 535 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,vop2.h` declares device-tree constants for the Rockchip SoC binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 11 visible constants or packing macros; representative names are `ROCKCHIP_VOP2_EP_RGB0`, `ROCKCHIP_VOP2_EP_HDMI0`, `ROCKCHIP_VOP2_EP_EDP0`, `ROCKCHIP_VOP2_EP_MIPI0`, `ROCKCHIP_VOP2_EP_LVDS0`, `ROCKCHIP_VOP2_EP_MIPI1`, `ROCKCHIP_VOP2_EP_LVDS1`, `ROCKCHIP_VOP2_EP_HDMI1`, `ROCKCHIP_VOP2_EP_EDP1`, `ROCKCHIP_VOP2_EP_DP0`, `ROCKCHIP_VOP2_EP_DP1`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/rockchip,vop2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,boot-mode.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,boot-mode.h

Source read summary: 19 lines, 530 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,boot-mode.h` declares device-tree constants for the Samsung Exynos SoC binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 3 visible constants or packing macros; representative names are `EXYNOSAUTOV9_BOOT_FASTBOOT`, `EXYNOSAUTOV9_BOOT_BOOTLOADER`, `EXYNOSAUTOV9_BOOT_RECOVERY`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,boot-mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,exynos-usi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,exynos-usi.h

Source read summary: 27 lines, 707 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,exynos-usi.h` declares device-tree constants for the Samsung Exynos SoC binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 11 visible constants or packing macros; representative names are `USI_MODE_NONE`, `USI_MODE_UART`, `USI_MODE_SPI`, `USI_MODE_I2C`, `USI_MODE_I2C1`, `USI_MODE_I2C0_1`, `USI_MODE_UART_I2C1`, `USI_V2_NONE`, `USI_V2_UART`, `USI_V2_SPI`, `USI_V2_I2C`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/samsung,exynos-usi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/tegra-pmc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/tegra-pmc.h

Source read summary: 17 lines, 394 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/tegra-pmc.h` declares device-tree constants for the NVIDIA Tegra PMC binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 5 visible constants or packing macros; representative names are `TEGRA_PMC_CLK_OUT_1`, `TEGRA_PMC_CLK_OUT_2`, `TEGRA_PMC_CLK_OUT_3`, `TEGRA_PMC_CLK_BLINK`, `TEGRA_PMC_CLK_MAX`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/tegra-pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/ti,sci_pm_domain.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/soc/ti,sci_pm_domain.h

Source read summary: 10 lines, 227 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/ti,sci_pm_domain.h` declares device-tree constants for the TI SCI power-domain binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 2 visible constants or packing macros; representative names are `TI_SCI_PD_EXCLUSIVE`, `TI_SCI_PD_SHARED`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/soc/ti,sci_pm_domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/adi,adau1977.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/adi,adau1977.h

Source read summary: 16 lines, 465 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/adi,adau1977.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `ADAU1977_MICBIAS_5V0`, `ADAU1977_MICBIAS_5V5`, `ADAU1977_MICBIAS_6V0`, `ADAU1977_MICBIAS_6V5`, `ADAU1977_MICBIAS_7V0`, `ADAU1977_MICBIAS_7V5`, `ADAU1977_MICBIAS_8V0`, `ADAU1977_MICBIAS_8V5`, `ADAU1977_MICBIAS_9V0`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/adi,adau1977.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/apq8016-lpass.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/apq8016-lpass.h

Source read summary: 10 lines, 238 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/apq8016-lpass.h` declares ASoC device-tree constants for the Qualcomm audio binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 0 visible constants or packing macros; representative names are none. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It includes `dt-bindings/sound/qcom,lpass.h` and otherwise depends on the device-tree preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/apq8016-lpass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/audio-graph.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/audio-graph.h

Source read summary: 27 lines, 596 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/audio-graph.h` declares ASoC device-tree constants for the audio routing/controller binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 4 visible constants or packing macros; representative names are `SND_SOC_TRIGGER_LINK`, `SND_SOC_TRIGGER_COMPONENT`, `SND_SOC_TRIGGER_DAI`, `SND_SOC_TRIGGER_SIZE`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/audio-graph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l32.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l32.h

Source read summary: 28 lines, 748 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l32.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 18 visible constants or packing macros; representative names are `CS35L32_BOOST_MGR_AUTO`, `CS35L32_BOOST_MGR_AUTO_AUDIO`, `CS35L32_BOOST_MGR_BYPASS`, `CS35L32_BOOST_MGR_FIXED`, `CS35L32_DATA_CFG_LR_VP`, `CS35L32_DATA_CFG_LR_STAT`, `CS35L32_DATA_CFG_LR`, `CS35L32_DATA_CFG_LR_VPSTAT`, `CS35L32_BATT_THRESH_3_1V`, `CS35L32_BATT_THRESH_3_2V`, `CS35L32_BATT_THRESH_3_3V`, `CS35L32_BATT_THRESH_3_4V`, `CS35L32_BATT_RECOV_3_1V`, `CS35L32_BATT_RECOV_3_2V`, `CS35L32_BATT_RECOV_3_3V`, `CS35L32_BATT_RECOV_3_4V` and 2 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l45.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l45.h

Source read summary: 78 lines, 2107 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l45.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 3 visible constants or packing macros; representative names are `CS35L45_ASP_TX_HIZ_UNUSED`, `CS35L45_ASP_TX_HIZ_DISABLED`, `CS35L45_NUM_GPIOS`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs35l45.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs42l42.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs42l42.h

Source read summary: 70 lines, 1926 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs42l42.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 35 visible constants or packing macros; representative names are `CS42L42_HPOUT_LOAD_1NF`, `CS42L42_HPOUT_LOAD_10NF`, `CS42L42_HPOUT_CLAMP_EN`, `CS42L42_HPOUT_CLAMP_DIS`, `CS42L42_TS_INV_DIS`, `CS42L42_TS_INV_EN`, `CS42L42_TS_DBNCE_0`, `CS42L42_TS_DBNCE_125`, `CS42L42_TS_DBNCE_250`, `CS42L42_TS_DBNCE_500`, `CS42L42_TS_DBNCE_750`, `CS42L42_TS_DBNCE_1000`, `CS42L42_TS_DBNCE_1250`, `CS42L42_TS_DBNCE_1500`, `CS42L42_BTN_DET_INIT_DBNCE_MIN`, `CS42L42_BTN_DET_INIT_DBNCE_DEFAULT` and 19 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs42l42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs48l32.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs48l32.h

Source read summary: 21 lines, 514 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs48l32.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 4 visible constants or packing macros; representative names are `CS48L32_IN_TYPE_DIFF`, `CS48L32_IN_TYPE_SE`, `CS48L32_PDM_SUP_VOUT_MIC`, `CS48L32_PDM_SUP_MICBIAS1`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/cs48l32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/fsl-imx-audmux.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/fsl-imx-audmux.h

Source read summary: 65 lines, 2326 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/fsl-imx-audmux.h` declares ASoC device-tree constants for the audio routing/controller binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 46 visible constants or packing macros; representative names are `MX27_AUDMUX_HPCR1_SSI0`, `MX27_AUDMUX_HPCR2_SSI1`, `MX27_AUDMUX_HPCR3_SSI_PINS_4`, `MX27_AUDMUX_PPCR1_SSI_PINS_1`, `MX27_AUDMUX_PPCR2_SSI_PINS_2`, `MX27_AUDMUX_PPCR3_SSI_PINS_3`, `MX31_AUDMUX_PORT1_SSI0`, `MX31_AUDMUX_PORT2_SSI1`, `MX31_AUDMUX_PORT3_SSI_PINS_3`, `MX31_AUDMUX_PORT4_SSI_PINS_4`, `MX31_AUDMUX_PORT5_SSI_PINS_5`, `MX31_AUDMUX_PORT6_SSI_PINS_6`, `MX31_AUDMUX_PORT7_SSI_PINS_7`, `MX51_AUDMUX_PORT1_SSI0`, `MX51_AUDMUX_PORT2_SSI1`, `MX51_AUDMUX_PORT3` and 30 more. Function-like helpers include `IMX_AUDMUX_V1_PCR_INMMASK`, `IMX_AUDMUX_V1_PCR_RXDSEL`, `IMX_AUDMUX_V1_PCR_RFCSEL`, `IMX_AUDMUX_V1_PCR_TFCSEL`, `IMX_AUDMUX_V2_PTCR_TFSEL`, `IMX_AUDMUX_V2_PTCR_TCSEL`, `IMX_AUDMUX_V2_PTCR_RFSEL`, `IMX_AUDMUX_V2_PTCR_RCSEL`, `IMX_AUDMUX_V2_PDCR_RXDSEL`, `IMX_AUDMUX_V2_PDCR_MODE`, `IMX_AUDMUX_V2_PDCR_INMMASK`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/fsl-imx-audmux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/madera.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/madera.h

Source read summary: 26 lines, 638 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/madera.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 10 visible constants or packing macros; representative names are `MADERA_INMODE_DIFF`, `MADERA_INMODE_SE`, `MADERA_INMODE_DMIC`, `MADERA_DMIC_REF_MICVDD`, `MADERA_DMIC_REF_MICBIAS1`, `MADERA_DMIC_REF_MICBIAS2`, `MADERA_DMIC_REF_MICBIAS3`, `CS47L35_DMIC_REF_MICBIAS1B`, `CS47L35_DMIC_REF_MICBIAS2A`, `CS47L35_DMIC_REF_MICBIAS2B`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/madera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-aiu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-aiu.h

Source read summary: 19 lines, 350 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-aiu.h` declares ASoC device-tree constants for the audio routing/controller binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 10 visible constants or packing macros; representative names are `AIU_CPU`, `AIU_HDMI`, `AIU_ACODEC`, `CPU_I2S_FIFO`, `CPU_SPDIF_FIFO`, `CPU_I2S_ENCODER`, `CPU_SPDIF_ENCODER`, `CTRL_I2S`, `CTRL_PCM`, `CTRL_OUT`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-aiu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-toacodec.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-toacodec.h

Source read summary: 11 lines, 246 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-toacodec.h` declares ASoC device-tree constants for the audio routing/controller binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 4 visible constants or packing macros; representative names are `TOACODEC_IN_A`, `TOACODEC_IN_B`, `TOACODEC_IN_C`, `TOACODEC_OUT`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-toacodec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-tohdmitx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-tohdmitx.h

Source read summary: 14 lines, 351 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-tohdmitx.h` declares ASoC device-tree constants for the audio routing/controller binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 7 visible constants or packing macros; representative names are `TOHDMITX_I2S_IN_A`, `TOHDMITX_I2S_IN_B`, `TOHDMITX_I2S_IN_C`, `TOHDMITX_I2S_OUT`, `TOHDMITX_SPDIF_IN_A`, `TOHDMITX_SPDIF_IN_B`, `TOHDMITX_SPDIF_OUT`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/meson-g12a-tohdmitx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/microchip,pdmc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/microchip,pdmc.h

Source read summary: 14 lines, 362 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/microchip,pdmc.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 4 visible constants or packing macros; representative names are `MCHP_PDMC_DS0`, `MCHP_PDMC_DS1`, `MCHP_PDMC_CLK_POSITIVE`, `MCHP_PDMC_CLK_NEGATIVE`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/microchip,pdmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,lpass.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,lpass.h

Source read summary: 47 lines, 1129 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,lpass.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 35 visible constants or packing macros; representative names are `MI2S_PRIMARY`, `MI2S_SECONDARY`, `MI2S_TERTIARY`, `MI2S_QUATERNARY`, `MI2S_QUINARY`, `LPASS_DP_RX`, `LPASS_CDC_DMA_RX0`, `LPASS_CDC_DMA_RX1`, `LPASS_CDC_DMA_RX2`, `LPASS_CDC_DMA_RX3`, `LPASS_CDC_DMA_RX4`, `LPASS_CDC_DMA_RX5`, `LPASS_CDC_DMA_RX6`, `LPASS_CDC_DMA_RX7`, `LPASS_CDC_DMA_RX8`, `LPASS_CDC_DMA_RX9` and 19 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,lpass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6afe.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6afe.h

Source read summary: 10 lines, 284 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6afe.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 0 visible constants or packing macros; representative names are none. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It includes `dt-bindings/sound/qcom,q6dsp-lpass-ports.h` and otherwise depends on the device-tree preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6afe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6asm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6asm.h

Source read summary: 27 lines, 855 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6asm.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 19 visible constants or packing macros; representative names are `MSM_FRONTEND_DAI_MULTIMEDIA1`, `MSM_FRONTEND_DAI_MULTIMEDIA2`, `MSM_FRONTEND_DAI_MULTIMEDIA3`, `MSM_FRONTEND_DAI_MULTIMEDIA4`, `MSM_FRONTEND_DAI_MULTIMEDIA5`, `MSM_FRONTEND_DAI_MULTIMEDIA6`, `MSM_FRONTEND_DAI_MULTIMEDIA7`, `MSM_FRONTEND_DAI_MULTIMEDIA8`, `MSM_FRONTEND_DAI_MULTIMEDIA9`, `MSM_FRONTEND_DAI_MULTIMEDIA10`, `MSM_FRONTEND_DAI_MULTIMEDIA11`, `MSM_FRONTEND_DAI_MULTIMEDIA12`, `MSM_FRONTEND_DAI_MULTIMEDIA13`, `MSM_FRONTEND_DAI_MULTIMEDIA14`, `MSM_FRONTEND_DAI_MULTIMEDIA15`, `MSM_FRONTEND_DAI_MULTIMEDIA16` and 3 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h

Source read summary: 248 lines, 7859 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 227 visible constants or packing macros; representative names are `HDMI_RX`, `SLIMBUS_0_RX`, `SLIMBUS_0_TX`, `SLIMBUS_1_RX`, `SLIMBUS_1_TX`, `SLIMBUS_2_RX`, `SLIMBUS_2_TX`, `SLIMBUS_3_RX`, `SLIMBUS_3_TX`, `SLIMBUS_4_RX`, `SLIMBUS_4_TX`, `SLIMBUS_5_RX`, `SLIMBUS_5_TX`, `SLIMBUS_6_RX`, `SLIMBUS_6_TX`, `PRIMARY_MI2S_RX` and 211 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd9335.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd9335.h

Source read summary: 15 lines, 378 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd9335.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 7 visible constants or packing macros; representative names are `AIF1_PB`, `AIF1_CAP`, `AIF2_PB`, `AIF2_CAP`, `AIF3_PB`, `AIF3_CAP`, `AIF4_PB`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd9335.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd934x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd934x.h

Source read summary: 17 lines, 446 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd934x.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `AIF1_PB`, `AIF1_CAP`, `AIF2_PB`, `AIF2_CAP`, `AIF3_PB`, `AIF3_CAP`, `AIF4_PB`, `AIF4_VIFEED`, `AIF4_MAD_TX`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,wcd934x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5640.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5640.h

Source read summary: 27 lines, 687 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5640.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 17 visible constants or packing macros; representative names are `RT5640_DMIC1_DATA_PIN_NONE`, `RT5640_DMIC1_DATA_PIN_IN1P`, `RT5640_DMIC1_DATA_PIN_GPIO3`, `RT5640_DMIC2_DATA_PIN_NONE`, `RT5640_DMIC2_DATA_PIN_IN1N`, `RT5640_DMIC2_DATA_PIN_GPIO4`, `RT5640_JD_SRC_GPIO1`, `RT5640_JD_SRC_JD1_IN4P`, `RT5640_JD_SRC_JD2_IN4N`, `RT5640_JD_SRC_GPIO2`, `RT5640_JD_SRC_GPIO3`, `RT5640_JD_SRC_GPIO4`, `RT5640_JD_SRC_HDA_HEADER`, `RT5640_OVCD_SF_0P5`, `RT5640_OVCD_SF_0P75`, `RT5640_OVCD_SF_1P0` and 1 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5640.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5651.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5651.h

Source read summary: 16 lines, 334 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5651.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 8 visible constants or packing macros; representative names are `RT5651_JD_NULL`, `RT5651_JD1_1`, `RT5651_JD1_2`, `RT5651_JD2`, `RT5651_OVCD_SF_0P5`, `RT5651_OVCD_SF_0P75`, `RT5651_OVCD_SF_1P0`, `RT5651_OVCD_SF_1P5`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/rt5651.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/samsung-i2s.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/samsung-i2s.h

Source read summary: 16 lines, 458 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/samsung-i2s.h` declares ASoC device-tree constants for the Samsung Exynos SoC binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 3 visible constants or packing macros; representative names are `CLK_I2S_CDCLK`, `CLK_I2S_RCLK_SRC`, `CLK_I2S_RCLK_PSR`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/samsung-i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/sc7180-lpass.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/sc7180-lpass.h

Source read summary: 10 lines, 236 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/sc7180-lpass.h` declares ASoC device-tree constants for the Qualcomm audio binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 0 visible constants or packing macros; representative names are none. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It includes `dt-bindings/sound/qcom,lpass.h` and otherwise depends on the device-tree preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/sc7180-lpass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/tas2552.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/tas2552.h

Source read summary: 20 lines, 711 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/tas2552.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 11 visible constants or packing macros; representative names are `TAS2552_PLL_CLKIN`, `TAS2552_PDM_CLK`, `TAS2552_CLK_TARGET_MASK`, `TAS2552_PLL_CLKIN_MCLK`, `TAS2552_PLL_CLKIN_BCLK`, `TAS2552_PLL_CLKIN_IVCLKIN`, `TAS2552_PLL_CLKIN_1_8_FIXED`, `TAS2552_PDM_CLK_PLL`, `TAS2552_PDM_CLK_IVCLKIN`, `TAS2552_PDM_CLK_BCLK`, `TAS2552_PDM_CLK_MCLK`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/tas2552.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320adc3xxx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320adc3xxx.h

Source read summary: 29 lines, 1203 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320adc3xxx.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 14 visible constants or packing macros; representative names are `ADC3XXX_GPIO_DISABLED`, `ADC3XXX_GPIO_INPUT`, `ADC3XXX_GPIO_GPI`, `ADC3XXX_GPIO_GPO`, `ADC3XXX_GPIO_CLKOUT`, `ADC3XXX_GPIO_INT1`, `ADC3XXX_GPIO_INT2`, `ADC3XXX_GPIO_SECONDARY_BCLK`, `ADC3XXX_GPIO_SECONDARY_WCLK`, `ADC3XXX_GPIO_ADC_MOD_CLK`, `ADC3XXX_MICBIAS_OFF`, `ADC3XXX_MICBIAS_2_0V`, `ADC3XXX_MICBIAS_2_5V`, `ADC3XXX_MICBIAS_AVDD`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320adc3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320aic31xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320aic31xx.h

Source read summary: 15 lines, 323 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320aic31xx.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 7 visible constants or packing macros; representative names are `MICBIAS_2_0V`, `MICBIAS_2_5V`, `MICBIAS_AVDDV`, `PLL_CLKIN_MCLK`, `PLL_CLKIN_BCLK`, `PLL_CLKIN_GPIO1`, `PLL_CLKIN_DIN`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/sound/tlv320aic31xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/spmi/spmi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/spmi/spmi.h

Source read summary: 11 lines, 221 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/spmi/spmi.h` provides the SPMI group slave ID macro used by device-tree clients that need to address grouped peripheral IDs.

Important APIs, types, and functions: The file exports 2 visible constants or packing macros; representative names are `SPMI_USID`, `SPMI_GSID`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS users place `SPMI_GSID` in SPMI address cells; the SPMI core and PMIC drivers interpret the encoded slave/group selector during device enumeration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Because the header exports a single bus addressing token, the main risk is using it in a cell layout that expects a raw SID rather than a group SID.

Test signals: Compile SPMI DTS files and exercise PMIC child-device enumeration on platforms using grouped SPMI addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/spmi/spmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/lm90.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/lm90.h

Source read summary: 14 lines, 297 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/lm90.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 3 visible constants or packing macros; representative names are `LM90_LOCAL_TEMPERATURE`, `LM90_REMOTE_TEMPERATURE`, `LM90_REMOTE2_TEMPERATURE`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/lm90.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/mediatek,lvts-thermal.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/mediatek,lvts-thermal.h

Source read summary: 113 lines, 3177 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/mediatek,lvts-thermal.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 91 visible constants or packing macros; representative names are `MT7987_CPU`, `MT7987_ETH2P5G`, `MT7988_CPU_0`, `MT7988_CPU_1`, `MT7988_ETH2P5G_0`, `MT7988_ETH2P5G_1`, `MT7988_TOPS_0`, `MT7988_TOPS_1`, `MT7988_ETHWARP_0`, `MT7988_ETHWARP_1`, `MT8186_LITTLE_CPU0`, `MT8186_LITTLE_CPU1`, `MT8186_LITTLE_CPU2`, `MT8186_CAM`, `MT8186_BIG_CPU0`, `MT8186_BIG_CPU1` and 75 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/mediatek,lvts-thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra114-soctherm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra114-soctherm.h

Source read summary: 20 lines, 587 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra114-soctherm.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 8 visible constants or packing macros; representative names are `TEGRA114_SOCTHERM_SENSOR_CPU`, `TEGRA114_SOCTHERM_SENSOR_MEM`, `TEGRA114_SOCTHERM_SENSOR_GPU`, `TEGRA114_SOCTHERM_SENSOR_PLLX`, `TEGRA114_SOCTHERM_THROT_LEVEL_NONE`, `TEGRA114_SOCTHERM_THROT_LEVEL_LOW`, `TEGRA114_SOCTHERM_THROT_LEVEL_MED`, `TEGRA114_SOCTHERM_THROT_LEVEL_HIGH`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra114-soctherm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra124-soctherm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra124-soctherm.h

Source read summary: 21 lines, 591 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra124-soctherm.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `TEGRA124_SOCTHERM_SENSOR_CPU`, `TEGRA124_SOCTHERM_SENSOR_MEM`, `TEGRA124_SOCTHERM_SENSOR_GPU`, `TEGRA124_SOCTHERM_SENSOR_PLLX`, `TEGRA124_SOCTHERM_SENSOR_NUM`, `TEGRA_SOCTHERM_THROT_LEVEL_NONE`, `TEGRA_SOCTHERM_THROT_LEVEL_LOW`, `TEGRA_SOCTHERM_THROT_LEVEL_MED`, `TEGRA_SOCTHERM_THROT_LEVEL_HIGH`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra124-soctherm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra186-bpmp-thermal.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra186-bpmp-thermal.h

Source read summary: 15 lines, 404 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra186-bpmp-thermal.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 5 visible constants or packing macros; representative names are `TEGRA186_BPMP_THERMAL_ZONE_CPU`, `TEGRA186_BPMP_THERMAL_ZONE_GPU`, `TEGRA186_BPMP_THERMAL_ZONE_AUX`, `TEGRA186_BPMP_THERMAL_ZONE_PLLX`, `TEGRA186_BPMP_THERMAL_ZONE_AO`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra186-bpmp-thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra194-bpmp-thermal.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra194-bpmp-thermal.h

Source read summary: 16 lines, 448 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra194-bpmp-thermal.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 6 visible constants or packing macros; representative names are `TEGRA194_BPMP_THERMAL_ZONE_CPU`, `TEGRA194_BPMP_THERMAL_ZONE_GPU`, `TEGRA194_BPMP_THERMAL_ZONE_AUX`, `TEGRA194_BPMP_THERMAL_ZONE_PLLX`, `TEGRA194_BPMP_THERMAL_ZONE_AO`, `TEGRA194_BPMP_THERMAL_ZONE_TJ_MAX`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra194-bpmp-thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra234-bpmp-thermal.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra234-bpmp-thermal.h

Source read summary: 20 lines, 621 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra234-bpmp-thermal.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 9 visible constants or packing macros; representative names are `TEGRA234_BPMP_THERMAL_ZONE_CPU`, `TEGRA234_BPMP_THERMAL_ZONE_GPU`, `TEGRA234_BPMP_THERMAL_ZONE_CV0`, `TEGRA234_BPMP_THERMAL_ZONE_CV1`, `TEGRA234_BPMP_THERMAL_ZONE_CV2`, `TEGRA234_BPMP_THERMAL_ZONE_SOC0`, `TEGRA234_BPMP_THERMAL_ZONE_SOC1`, `TEGRA234_BPMP_THERMAL_ZONE_SOC2`, `TEGRA234_BPMP_THERMAL_ZONE_TJ_MAX`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra234-bpmp-thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal.h

Source read summary: 17 lines, 369 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 1 visible constants or packing macros; representative names are `THERMAL_NO_LIMIT`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal_exynos.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal_exynos.h

Source read summary: 19 lines, 472 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal_exynos.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 5 visible constants or packing macros; representative names are `TYPE_ONE_POINT_TRIMMING`, `TYPE_ONE_POINT_TRIMMING_25`, `TYPE_ONE_POINT_TRIMMING_85`, `TYPE_TWO_POINT_TRIMMING`, `TYPE_NONE`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/thermal/thermal_exynos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/usb/pd.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/usb/pd.h

Source read summary: 505 lines, 17678 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/usb/pd.h` defines the USB Type-C Power Delivery wire-level constants and helper macros used by device trees and drivers to encode PDOs, RDOs, VDOs, SVDMs, cable/plug capabilities, power roles, data roles, and alternate-mode discovery fields.

Important APIs, types, and functions: The file exports 196 visible constants or packing macros; representative names are `PDO_TYPE_FIXED`, `PDO_TYPE_BATT`, `PDO_TYPE_VAR`, `PDO_TYPE_APDO`, `PDO_TYPE_SHIFT`, `PDO_TYPE_MASK`, `PDO_VOLT_MASK`, `PDO_CURR_MASK`, `PDO_PWR_MASK`, `PDO_FIXED_DUAL_ROLE`, `PDO_FIXED_SUSPEND`, `PDO_FIXED_HIGHER_CAP`, `PDO_FIXED_EXTPOWER`, `PDO_FIXED_USB_COMM`, `PDO_FIXED_DATA_SWAP`, `PDO_FIXED_VOLT_SHIFT` and 180 more. Function-like helpers include `PDO_TYPE`, `PDO_FIXED_VOLT`, `PDO_FIXED_CURR`, `PDO_FIXED`, `PDO_BATT_MIN_VOLT`, `PDO_BATT_MAX_VOLT`, `PDO_BATT_MAX_POWER`, `PDO_BATT`, `PDO_VAR_MIN_VOLT`, `PDO_VAR_MAX_VOLT`, `PDO_VAR_MAX_CURR`, `PDO_VAR`, `PDO_APDO_TYPE`, `PDO_PPS_APDO_MIN_VOLT`, `PDO_PPS_APDO_MAX_VOLT`, `PDO_PPS_APDO_MAX_CURR` and 18 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: `PDO_*`, `RDO_*`, `VDO_*`, and `SVDM_*` helpers pack policy-engine choices into protocol bitfields; USB-C controller drivers and board descriptions consume the same constants so advertised source/sink capabilities match the kernel's PD parser.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bit shift, mask, and unit mistakes can advertise unsafe voltage/current combinations or select the wrong alternate mode. The macros intentionally do not validate electrical feasibility, so callers must enforce PD specification constraints.

Test signals: Build DTS users, decode generated PDO/RDO/VDO values against the USB PD spec, run Type-C negotiation tests for fixed, battery, variable, PPS, and AVS supplies, and cover role-swap and alternate-mode discovery messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/usb/pd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/watchdog/aspeed-wdt.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/watchdog/aspeed-wdt.h

Source read summary: 231 lines, 9161 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/watchdog/aspeed-wdt.h` enumerates AST2500, AST2600, and AST2700 watchdog reset-mask bits for peripherals and SoC domains controlled by Aspeed watchdog hardware.

Important APIs, types, and functions: The file exports 208 visible constants or packing macros; representative names are `AST2500_WDT_RESET_CPU`, `AST2500_WDT_RESET_COPROC`, `AST2500_WDT_RESET_SDRAM`, `AST2500_WDT_RESET_AHB`, `AST2500_WDT_RESET_I2C`, `AST2500_WDT_RESET_MAC0`, `AST2500_WDT_RESET_MAC1`, `AST2500_WDT_RESET_GRAPHICS`, `AST2500_WDT_RESET_USB2_HOST_HUB`, `AST2500_WDT_RESET_USB_HOST`, `AST2500_WDT_RESET_HID_EHCI`, `AST2500_WDT_RESET_VIDEO`, `AST2500_WDT_RESET_HAC`, `AST2500_WDT_RESET_LPC`, `AST2500_WDT_RESET_SDIO`, `AST2500_WDT_RESET_MIC` and 192 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Aspeed watchdog device-tree nodes reference these masks to select which blocks are reset on timeout; the watchdog driver writes corresponding hardware reset-mask registers.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The constants are SoC-generation specific. Reusing an AST2500 bit on AST2600/AST2700 hardware, or combining incompatible reset targets, can leave a peripheral out of reset or reset more of the SoC than intended.

Test signals: Compile representative DTS files, compare masks with the SoC datasheet, and exercise watchdog timeout paths on boards where reset scope can be observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/watchdog/aspeed-wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvgdk.h -->
# sources/distributed-fs/ceph-client/include/hyperv/hvgdk.h

Source read summary: 309 lines, 7516 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvgdk.h` defines guest-facing Hyper-V data structures layered on the mini guest definitions, including enlightened VMCS/VMCB state, synthetic exit reasons, connection IDs, partition assist pages, and GPA unmap inputs.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_enlightened_vmcs`, `hv_vmcb_enlightenments`, `hv_partition_assist_pg`, `hv_connection_id`, `hv_input_unmap_gpa_pages`, `__packed`. Important constants/macros: `HV_LINUX_VENDOR_ID`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_NONE`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_IO_BITMAP`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_MSR_BITMAP`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_GRP2`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_GRP1`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_PROC`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_EVENT`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_ENTRY`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_EXCPN`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CRDR`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_XLAT`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_GUEST_BASIC`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_GUEST_GRP1`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_GUEST_GRP2`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_HOST_POINTER` and 7 more.

Control flow: Nested virtualization and Hyper-V guest code include this header when exchanging enlightenments and hypercall payloads with the hypervisor; the structures are copied into architected shared pages or hypercall input/output buffers.

State and persistence behavior: State is shared-memory ABI state, not file persistence. Fields such as VMCS clean bits, VMCB enlightenment controls, and assist pages persist as long as the guest/hypervisor shared page remains mapped.

Dependencies and integration points: It includes `hvgdk_mini.h`, `hvgdk_ext.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The risk is binary-layout drift: packed fields, bitfields, and union aliases must exactly match Hyper-V TLFS expectations or nested virtualization, TLB flush, and assist-page flows can corrupt guest state.

Test signals: Compile with layout-sensitive KVM/Hyper-V users, run nested virtualization smoke tests, validate structure sizes/offsets against TLFS, and exercise enlightened VMCS/VMCB plus GPA unmap hypercalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvgdk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvgdk_ext.h -->
# sources/distributed-fs/ceph-client/include/hyperv/hvgdk_ext.h

Source read summary: 47 lines, 1242 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvgdk_ext.h` adds extended Hyper-V guest hypercall definitions, currently capability query and memory heat/cold-discard hint payloads.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_memory_hint`, `__packed`. Important constants/macros: `HV_EXT_CALL_QUERY_CAPABILITIES`, `HV_EXT_CALL_MEMORY_HEAT_HINT`, `HV_EXT_CAPABILITY_MEMORY_COLD_DISCARD_HINT`, `HV_MEMORY_HINT_MAX_GPA_PAGE_RANGES`, `HV_EXT_MEMORY_HEAT_HINT_TYPE_COLD_DISCARD`.

Control flow: Guest memory-management code can build `hv_memory_hint` ranges and issue an extended hypercall so the host can treat selected GPA ranges as cold or discardable.

State and persistence behavior: The only state is transient hypercall input. Host-side policy may persist the hint, but this header only defines the ABI layout and capability bits.

Dependencies and integration points: It includes `hvgdk_mini.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Range counts are bounded by `HV_MEMORY_HINT_MAX_GPA_PAGE_RANGES`; callers must avoid overflowing the fixed array and must only use features advertised by the capability query.

Test signals: Check structure sizes, issue capability queries on Hyper-V, and test memory-hint calls with zero, one, and maximum range counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvgdk_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvgdk_mini.h -->
# sources/distributed-fs/ceph-client/include/hyperv/hvgdk_mini.h

Source read summary: 1544 lines, 45544 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvgdk_mini.h` is the core Hyper-V guest definition kit: status codes, hypercall numbers, MSRs, synthetic interrupt/VP assist layouts, VP-set formats, partition and isolation constants, VTL permissions, TLB flush inputs, and many register identifiers.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_u128`, `hv_reenlightenment_control`, `hv_tsc_emulation_status`, `hv_tsc_emulation_control`, `hv_output_get_partition_id`, `hv_reference_tsc_msr`, `hv_vpset`, `hv_hypervisor_version_info`, `hv_isolation_type`, `hv_x64_msr_hypercall_contents`, `hv_vp_assist_msr_contents`, `hv_guest_mapping_flush`, `hv_gpa_page_range`, `hv_guest_mapping_flush_list`, `hv_tlb_flush`, `hv_tlb_flush_ex` and 60 more. Important constants/macros: `HV_STATUS_SUCCESS`, `HV_STATUS_INVALID_HYPERCALL_CODE`, `HV_STATUS_INVALID_HYPERCALL_INPUT`, `HV_STATUS_INVALID_ALIGNMENT`, `HV_STATUS_INVALID_PARAMETER`, `HV_STATUS_ACCESS_DENIED`, `HV_STATUS_INVALID_PARTITION_STATE`, `HV_STATUS_OPERATION_DENIED`, `HV_STATUS_UNKNOWN_PROPERTY`, `HV_STATUS_PROPERTY_VALUE_OUT_OF_RANGE`, `HV_STATUS_INSUFFICIENT_MEMORY`, `HV_STATUS_INVALID_PARTITION_ID`, `HV_STATUS_INVALID_VP_INDEX`, `HV_STATUS_NOT_FOUND`, `HV_STATUS_INVALID_PORT_ID`, `HV_STATUS_INVALID_CONNECTION_ID` and 328 more.

Control flow: Low-level Hyper-V guest, KVM-on-Hyper-V, and architecture code include it to compose hypercalls, decode status codes, program synthetic MSRs, and share VP/interrupt/timer state with the hypervisor.

State and persistence behavior: State is external to the header but layout-critical: MSR bitfields, VP assist pages, reference TSC pages, synthetic interrupt controller fields, and hypercall input buffers are live ABI memory shared with Hyper-V.

Dependencies and integration points: It includes `linux/types.h`, `linux/bits.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The file is broad and dense; the main risks are wrong bit numbering, missing packing, endian/layout assumptions, and accidental divergence from the TLFS as new status codes or hypercalls are added.

Test signals: Use build coverage on Hyper-V guest and KVM paths, static size/offset checks where available, hypercall status decoding tests, synthetic interrupt/timer smoke tests, and nested/isolated guest boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvgdk_mini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvhdk.h -->
# sources/distributed-fs/ceph-client/include/hyperv/hvhdk.h

Source read summary: 956 lines, 23516 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvhdk.h` defines host/direct-kernel Hyper-V control-plane structures for partition creation, initialization, properties, processor features, intercepts, synthetic MSRs, registers, ports, messages, and VSM/VTL operations.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_stats_page`, `hv_vp_register_page_interrupt_vectors`, `hv_vp_register_page`, `hv_partition_processor_features`, `hv_partition_processor_xsave_features`, `hv_partition_creation_properties`, `hv_partition_synthetic_processor_features`, `hv_partition_isolation_properties`, `hv_input_create_partition`, `hv_output_create_partition`, `hv_input_initialize_partition`, `hv_input_finalize_partition`, `hv_input_delete_partition`, `hv_input_get_partition_property`, `hv_output_get_partition_property`, `hv_input_set_partition_property` and 64 more. Important constants/macros: `HV_X64_REGISTER_CLASS_GENERAL`, `HV_X64_REGISTER_CLASS_IP`, `HV_X64_REGISTER_CLASS_XMM`, `HV_X64_REGISTER_CLASS_SEGMENT`, `HV_X64_REGISTER_CLASS_FLAGS`, `HV_VP_REGISTER_PAGE_VERSION_1`, `HV_VP_REGISTER_PAGE_MAX_VECTOR_COUNT`, `HV_PARTITION_PROCESSOR_FEATURES_BANKS`, `HV_PARTITION_SYNTHETIC_PROCESSOR_FEATURES_BANKS`, `HV_COMPATIBILITY_21_H2`, `HV_PARTITION_ISOLATION_TYPE_NONE`, `HV_PARTITION_ISOLATION_TYPE_SNP`, `HV_PARTITION_ISOLATION_TYPE_TDX`, `HV_PARTITION_ISOLATION_HOST_TYPE_NONE`, `HV_PARTITION_ISOLATION_HOST_TYPE_HARDWARE`, `HV_PARTITION_ISOLATION_HOST_TYPE_RESERVED` and 30 more.

Control flow: Hyper-V host-side or VMM code uses these definitions to create partitions, configure virtual processors, set partition properties, map GPA pages, send synthetic interrupts, and manage partition lifecycle through hypercalls.

State and persistence behavior: The state described here is partition and VP configuration held by the hypervisor. Header structs are serialized into hypercall input/output pages and must remain layout-compatible for the lifetime of the ABI.

Dependencies and integration points: It includes `linux/build_bug.h`, `hvhdk_mini.h`, `hvgdk.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Feature banks, isolation settings, register classes, and nested unions are easy to misuse; a wrong property code or feature bit can create an unsupported partition shape or expose the wrong CPU capability set.

Test signals: Validate struct sizes with `BUILD_BUG_ON` users, create/destroy test partitions, exercise processor feature negotiation, register get/set paths, GPA mapping, and isolated-partition configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvhdk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvhdk_mini.h -->
# sources/distributed-fs/ceph-client/include/hyperv/hvhdk_mini.h

Source read summary: 551 lines, 13097 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvhdk_mini.h` provides the smaller host Hyper-V definition base shared by the full HVDK header: generic-set encodings, scheduler and statistics enums, partition/system property codes, VMM capabilities, SNP/TDX-related flags, GPA mapping permissions, and processor-property controls.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_generic_set_format`, `hv_scheduler_type`, `hv_stats_area_type`, `hv_stats_object_type`, `hv_stats_object_identity`, `hv_partition_property_code`, `hv_partition_property_vmm_capabilities`, `hv_snp_status`, `hv_system_property`, `hv_pfn_range`, `hv_sleep_state`, `hv_dynamic_processor_feature_property`, `hv_input_get_system_property`, `hv_output_get_system_property`, `hv_sleep_state_info`, `hv_input_set_system_property` and 42 more. Important constants/macros: `HV_MAX_CONTIGUOUS_ALLOCATION_PAGES`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_MASK`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_ANY`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_BYTE`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_WORD`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_DWORD`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_QWORD`, `HV_DOORBELL_FLAG_TRIGGER_ANY_VALUE`, `HV_GENERIC_SET_SHIFT`, `HV_GENERIC_SET_MASK`, `HV_GENERIC_SET_FORMAT`, `HV_PARTITION_VMM_CAPABILITIES_BANK_COUNT`, `HV_PARTITION_VMM_CAPABILITIES_RESERVED_BITFIELD_COUNT`, `HV_PFN_RANGE_PGBITS`, `HV_MAP_GPA_PERMISSIONS_NONE`, `HV_MAP_GPA_READABLE` and 11 more.

Control flow: It is included by host control-plane code and by `hvhdk.h` so hypercall builders share the same property codes, bit masks, and packed payload shapes.

State and persistence behavior: No local storage exists. Values identify hypervisor-owned persistent objects such as partitions, statistics areas, memory mappings, and dynamic processor feature state.

Dependencies and integration points: It includes `hvgdk_mini.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The risk is ABI mismatch in packed enums, property codes, and permission bits; mapping permissions in particular can overgrant access if composed incorrectly.

Test signals: Compile all HVDK users, check property and permission encodings against TLFS, and test GPA map/unmap plus property query/set hypercall flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/hyperv/hvhdk_mini.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/asymmetric-parser.h -->
# sources/distributed-fs/ceph-client/include/keys/asymmetric-parser.h

Source read summary: 36 lines, 1012 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/asymmetric-parser.h` declares the registration interface for asymmetric key parsers that convert raw blobs into key payloads during key instantiation.

Important APIs, types, and functions: Important exported functions or hooks: `register_asymmetric_key_parser`, `unregister_asymmetric_key_parser`. Important types: `key_preparsed_payload`, `asymmetric_key_parser`. Important constants/macros: none.

Control flow: Parser modules fill `struct asymmetric_key_parser` with an owner, name, parser callback, and linked-list node, then call register/unregister helpers so the asymmetric key type can try parsers during preparse.

State and persistence behavior: Registered parsers persist in a global kernel list while their module is loaded; individual preparsed payloads remain request-local until key instantiation succeeds or fails.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Parser ordering, module lifetime, and preparse cleanup are the main hazards. A parser must leave no dangling payload state on failure and must not unregister while in active use.

Test signals: Load/unload parser modules, instantiate X.509/PKCS#7-like blobs through the keyring API, and cover malformed blob cleanup and duplicate parser names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/asymmetric-parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/asymmetric-subtype.h -->
# sources/distributed-fs/ceph-client/include/keys/asymmetric-subtype.h

Source read summary: 61 lines, 1696 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/asymmetric-subtype.h` defines the asymmetric-key subtype interface, public-key query/operation parameter structs, signature payload layout, and callbacks used by RSA/ECDSA or certificate-backed key implementations.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `kernel_pkey_query`, `kernel_pkey_params`, `public_key_signature`, `asymmetric_key_subtype`. Important constants/macros: none.

Control flow: The asymmetric key type delegates describe, destroy, query, encrypt/decrypt, sign/verify, and ID lookup behavior through `struct asymmetric_key_subtype` after a parser installs subtype-specific payloads.

State and persistence behavior: Key payloads persist under key retention rules and may be RCU-protected. Signature and public-key parameter structs are transient operation inputs owned by callers.

Dependencies and integration points: It includes `linux/seq_file.h`, `keys/asymmetric-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Mismatched subtype callbacks or algorithm/hash identifiers can produce false verification results or leaks. Buffer lengths and digest sizes must be validated before crypto operations.

Test signals: Run asymmetric key selftests, signature verification with supported and unsupported algorithms, key destruction under RCU, and parser/subtype handoff failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/asymmetric-subtype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/asymmetric-type.h -->
# sources/distributed-fs/ceph-client/include/keys/asymmetric-type.h

Source read summary: 95 lines, 3050 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/asymmetric-type.h` declares the common asymmetric key type payload layout, key ID helpers, and optional certificate-list loader entry point.

Important APIs, types, and functions: Important exported functions or hooks: `asymmetric_key_id_same`, `asymmetric_key_id_partial`, `x509_load_certificate_list`. Important types: `asymmetric_payload_bits`, `asymmetric_key_id`, `asymmetric_key_ids`. Important constants/macros: none.

Control flow: Callers compare full or partial IDs with `asymmetric_key_id_same()` and `asymmetric_key_id_partial()`, while keyring/certificate code stores ID arrays in `struct asymmetric_key_ids` for lookup and trust decisions.

State and persistence behavior: Key IDs and payload bits persist as part of instantiated key payloads until the key is revoked or garbage-collected. Certificate-list loading affects trusted keyrings during initialization.

Dependencies and integration points: It includes `linux/key-type.h`, `linux/verification.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Partial ID matching can be ambiguous; payload index constants must match subtype parser allocation. Certificate loading failures can reduce trust roots without obvious runtime symptoms.

Test signals: Exercise key lookup by exact and partial ID, boot-time certificate loading, blacklist interaction, and malformed ID payload handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/asymmetric-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/big_key-type.h -->
# sources/distributed-fs/ceph-client/include/keys/big_key-type.h

Source read summary: 24 lines, 816 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/big_key-type.h` declares the `big_key` key-type operations for preparsing, updating, revoking, destroying, describing, and reading large user key payloads.

Important APIs, types, and functions: Important exported functions or hooks: `big_key_preparse`, `big_key_free_preparse`, `big_key_revoke`, `big_key_destroy`, `big_key_describe`, `big_key_read`, `big_key_update`. Important types: none. Important constants/macros: none.

Control flow: The key subsystem calls these hooks through the key type when userspace adds, updates, reads, or revokes a big key; implementation code may store payloads in memory or encrypted temporary storage depending on size.

State and persistence behavior: Payload state persists in the key object until revoke/destroy, with preparse state used only during instantiation/update.

Dependencies and integration points: It includes `linux/key-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Large payload size, update/revoke races, quota accounting, and secure cleanup of temporary/encrypted storage are the important edge cases.

Test signals: Run keyutils add/read/update/revoke tests across small and large payload thresholds, quota limits, and revoke while readers hold references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/big_key-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/ceph-type.h -->
# sources/distributed-fs/ceph-client/include/keys/ceph-type.h

Source read summary: 10 lines, 162 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/ceph-type.h` declares the Ceph key type object consumed by the in-kernel Ceph client for authentication material.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: Ceph authentication code looks up keys of this type from keyrings and interprets payloads in the Ceph auth implementation rather than in this tiny header.

State and persistence behavior: Ceph key payloads persist under normal key retention and revocation semantics.

Dependencies and integration points: It includes `linux/key.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The risk is mostly integration: missing key type registration or wrong key descriptions prevent Ceph mounts from authenticating.

Test signals: Mount Ceph with keyring-provided credentials, cover missing/revoked keys, and build-test Ceph auth users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/ceph-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/dns_resolver-type.h -->
# sources/distributed-fs/ceph-client/include/keys/dns_resolver-type.h

Source read summary: 16 lines, 364 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/dns_resolver-type.h` declares the DNS resolver key type used to cache DNS lookup results in the kernel key retention service.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: Network filesystems and other clients request DNS keys; resolver upcalls instantiate this key type and later consumers read cached resolution payloads.

State and persistence behavior: Resolved records persist in keyrings until timeout, revocation, or garbage collection.

Dependencies and integration points: It includes `linux/key-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Stale or malformed resolver payloads can misdirect network mounts; TTL and negative-result behavior need careful handling in the implementation.

Test signals: Test request-key DNS upcalls, cache expiry, negative lookups, and consumers such as CIFS/NFS/Ceph that rely on resolver keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/dns_resolver-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/encrypted-type.h -->
# sources/distributed-fs/ceph-client/include/keys/encrypted-type.h

Source read summary: 36 lines, 1118 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/encrypted-type.h` defines the RCU-protected payload wrapper for encrypted keys and the external encrypted key type.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `encrypted_key_payload`. Important constants/macros: none.

Control flow: The encrypted key implementation stores decrypted data, IV, encrypted data, datablob metadata, and master-key description in `struct encrypted_key_payload`; key operations update or read that payload through RCU-safe replacement.

State and persistence behavior: Payloads persist inside key objects, while decrypted bytes must be protected in memory and cleared on destroy. RCU allows readers to finish while updates replace payloads.

Dependencies and integration points: It includes `linux/key.h`, `linux/rcupdate.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Incorrect datalen/encrypted_datalen handling, master-key lookup failures, or incomplete zeroization can expose secret material.

Test signals: Run encrypted key add/update/read tests, master-key revoke tests, RCU update stress, and memory-sanitizer checks for cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/encrypted-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/keyring-type.h -->
# sources/distributed-fs/ceph-client/include/keys/keyring-type.h

Source read summary: 15 lines, 337 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/keyring-type.h` declares the keyring key type and the serial-number association-array operations used to index linked keys.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: Keyring implementation code uses the assoc-array operations to insert, find, and unlink keys by serial while exposing a key type that can hold links to other keys.

State and persistence behavior: Keyring contents persist until unlink, revoke, expiry, or garbage collection; assoc-array nodes are in-memory indexing state.

Dependencies and integration points: It includes `linux/key.h`, `linux/assoc_array.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Link cycles, reference counting, quota accounting, and concurrent search/update paths are the primary risks.

Test signals: Exercise keyctl link/unlink/search/revoke operations, concurrent keyring updates, and garbage collection of nested keyrings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/keyring-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/request_key_auth-type.h -->
# sources/distributed-fs/ceph-client/include/keys/request_key_auth-type.h

Source read summary: 34 lines, 747 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/request_key_auth-type.h` defines the authorization key payload used while servicing request-key upcalls.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `request_key_auth`, `__randomize_layout`. Important constants/macros: none.

Control flow: When the kernel asks userspace to instantiate a key, it creates a request-key auth key carrying the target key, credentials, callout info, operation string, and destination keyring pointer.

State and persistence behavior: The authorization payload persists only for the lifetime of the upcall/session and is then revoked or garbage-collected.

Dependencies and integration points: It includes `linux/key.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Credential lifetime, callout-info bounds, and target/destination key references must be handled carefully to avoid privilege or reference leaks.

Test signals: Test request-key upcalls, authorization key revocation, failed instantiation cleanup, and permission checks across user namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/request_key_auth-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/rxrpc-type.h -->
# sources/distributed-fs/ceph-client/include/keys/rxrpc-type.h

Source read summary: 113 lines, 3014 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/rxrpc-type.h` defines RxRPC/AFS key token layouts for rxkad and rxgk security classes, Kerberos-derived tickets, token limits, and legacy v1 payload data.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `rxkad_key`, `rxgk_key`, `rxrpc_key_token`, `rxrpc_key_data_v1`. Important constants/macros: `AFSTOKEN_LENGTH_MAX`, `AFSTOKEN_STRING_MAX`, `AFSTOKEN_DATA_MAX`, `AFSTOKEN_CELL_MAX`, `AFSTOKEN_MAX`, `AFSTOKEN_BDATALN_MAX`, `AFSTOKEN_RK_TIX_MAX`, `AFSTOKEN_GK_KEY_MAX`, `AFSTOKEN_GK_TOKEN_MAX`.

Control flow: AFS/RxRPC authentication code parses key payloads into `struct rxrpc_key_token` entries and uses the embedded keys, tickets, expiry, kvno, and cell/principal names when securing calls.

State and persistence behavior: Tokens persist in key payloads until expiry, revoke, or key destruction. Sensitive ticket and session-key bytes must be protected and cleared.

Dependencies and integration points: It includes `linux/key.h`, `crypto/krb5.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Length limits are security boundaries; malformed token counts, oversized tickets, or unsupported security indexes can lead to failed authentication or memory bugs.

Test signals: Test rxkad/rxgk token parsing, expiry handling, malformed length rejection, and AFS/RxRPC authenticated call setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/rxrpc-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/system_keyring.h -->
# sources/distributed-fs/ceph-client/include/keys/system_keyring.h

Source read summary: 134 lines, 3899 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/system_keyring.h` declares system trusted keyrings, blacklist/revocation helpers, and restriction callbacks used by module signing, kexec, firmware, and certificate trust paths.

Important APIs, types, and functions: Important exported functions or hooks: `restrict_link_by_builtin_trusted`, `restrict_link_by_digsig_builtin`, `load_module_cert`, `restrict_link_by_builtin_and_secondary_trusted`, `restrict_link_by_digsig_builtin_and_secondary`, `add_to_secondary_keyring`, `restrict_link_by_builtin_secondary_and_machine`, `set_machine_trusted_keys`, `mark_hash_blacklisted`, `is_hash_blacklisted`, `is_binary_blacklisted`, `add_key_to_revocation_list`, `is_key_on_revocation_list`, `set_platform_trusted_keys`. Important types: `blacklist_hash_type`, `pkcs7_message`. Important constants/macros: `restrict_link_by_builtin_trusted`, `restrict_link_by_digsig_builtin`, `restrict_link_by_builtin_and_secondary_trusted`, `restrict_link_by_digsig_builtin_and_secondary`, `restrict_link_by_builtin_secondary_and_machine`.

Control flow: Loaders query builtin, secondary, platform, machine, and blacklist keyrings through these helpers; restriction callbacks decide whether a new cert may link into a trusted keyring.

State and persistence behavior: Trust anchors and blacklist hashes persist in global keyrings for the boot lifetime. Some objects are only present under Kconfig options, so many declarations compile to stubs.

Dependencies and integration points: It includes `linux/key.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Configuration-dependent stubs can change security behavior. Incorrect restriction callbacks or blacklist checks can allow untrusted modules/images or reject valid signed content.

Test signals: Run module-signing, kexec/image verification, certificate import, blacklist hash matching, and Kconfig matrix builds for secondary/platform/machine keyrings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/system_keyring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted-type.h -->
# sources/distributed-fs/ceph-client/include/keys/trusted-type.h

Source read summary: 106 lines, 2369 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted-type.h` defines trusted-key payload/options structures, common size limits, backend operation callbacks, and trusted-key source selection for TPM, TEE, CAAM, DCP, or PKWM providers.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `trusted_key_payload`, `trusted_key_options`, `trusted_key_ops`, `trusted_key_source`. Important constants/macros: `MIN_KEY_SIZE`, `MAX_KEY_SIZE`, `MAX_BLOB_SIZE`, `MAX_PCRINFO_SIZE`, `MAX_DIGEST_SIZE`, `TRUSTED_DEBUG`, `pr_fmt`.

Control flow: The trusted key type parses options, selects backend ops, seals/unseals blobs through the active secure hardware/provider, and stores decrypted key material plus sealed blobs in `struct trusted_key_payload`.

State and persistence behavior: Sealed blobs persist in the key payload; decrypted key bytes are in memory while the key is active and must be cleared on destroy. Backend selection is global/configuration-driven.

Dependencies and integration points: It includes `linux/key.h`, `linux/rcupdate.h`, `linux/tpm.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Size limits, PCR/options parsing, RNG quality, backend availability, and secret zeroization are the major risks.

Test signals: Exercise trusted key add/load/update for every enabled backend, PCR policy options, invalid option parsing, and secure cleanup under revoke/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_caam.h -->
# sources/distributed-fs/ceph-client/include/keys/trusted_caam.h

Source read summary: 12 lines, 243 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_caam.h` declares the CAAM trusted-key backend operations object.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: The common trusted key type can select `trusted_key_caam_ops` when CAAM-backed sealing is enabled and available.

State and persistence behavior: No local state exists; sealed blobs and decrypted key bytes are owned by the common trusted-key payload.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Backend registration must match CAAM hardware availability and must fail closed when secure key operations are unavailable.

Test signals: Build CAAM trusted-key configurations and run create/load tests on CAAM-capable hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_caam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_dcp.h -->
# sources/distributed-fs/ceph-client/include/keys/trusted_dcp.h

Source read summary: 12 lines, 194 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_dcp.h` declares the DCP trusted-key backend operations object.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: The common trusted key type can dispatch trusted key seal/unseal operations through `trusted_key_dcp_ops` on supported DCP hardware.

State and persistence behavior: No local state exists; backend hardware and common trusted-key payloads hold the durable wrapped-key state.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Incorrect backend selection or missing DCP support can make trusted keys fail at runtime.

Test signals: Build DCP trusted-key configurations and test add/load/revoke flows with DCP-backed keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_dcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_pkwm.h -->
# sources/distributed-fs/ceph-client/include/keys/trusted_pkwm.h

Source read summary: 34 lines, 799 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_pkwm.h` defines PKWM trusted-key option bits and parsed option storage for hardware-wrapped keys.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `trusted_pkwm_options`. Important constants/macros: none.

Control flow: The PKWM backend reads `trusted_pkwm_options` from trusted-key option parsing to decide whether to create new wrapped material, load an existing blob, or use hardware-specific policy flags.

State and persistence behavior: Options are transient parse state; resulting wrapped keys persist in the trusted-key payload.

Dependencies and integration points: It includes `keys/trusted-type.h`, `linux/bitops.h`, `linux/printk.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Unknown option bits or inconsistent create/load state can make a wrapped key unusable or weaken policy expectations.

Test signals: Test PKWM option parsing, create/load flows, invalid bit rejection, and integration with the common trusted key type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_pkwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_tee.h -->
# sources/distributed-fs/ceph-client/include/keys/trusted_tee.h

Source read summary: 17 lines, 286 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_tee.h` declares the TEE trusted-key backend operations object.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: none. Important constants/macros: none.

Control flow: The common trusted key type can route seal/unseal requests to `trusted_key_tee_ops`, which uses a trusted execution environment service.

State and persistence behavior: No local state exists; wrapped blobs persist in key payloads and any provider state is held by the TEE backend.

Dependencies and integration points: It includes `keys/trusted-type.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: TEE service availability, session lifetime, and blob compatibility must be handled without exposing decrypted key material.

Test signals: Run trusted-key create/load/revoke tests with the TEE backend enabled and cover unavailable TEE service errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_tee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_tpm.h -->
# sources/distributed-fs/ceph-client/include/keys/trusted_tpm.h

Source read summary: 18 lines, 475 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted_tpm.h` declares TPM2 trusted-key seal and unseal helpers used by the TPM backend.

Important APIs, types, and functions: Important exported functions or hooks: `tpm2_seal_trusted`, `tpm2_unseal_trusted`. Important types: none. Important constants/macros: none.

Control flow: The trusted-key implementation passes parsed payload/options into `tpm2_seal_trusted()` or `tpm2_unseal_trusted()` to create or recover sealed key blobs.

State and persistence behavior: TPM-sealed blobs persist in the key payload and are bound to TPM policy/PCR state; decrypted payload bytes are transient secret material.

Dependencies and integration points: It includes `keys/trusted-type.h`, `linux/tpm_command.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: TPM command errors, PCR mismatch, authorization failures, and blob size mismatches must unwind without leaking key bytes.

Test signals: Run TPM2 trusted-key seal/unseal tests, PCR policy changes, wrong authorization, and blob corruption cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/trusted_tpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/user-type.h -->
# sources/distributed-fs/ceph-client/include/keys/user-type.h

Source read summary: 59 lines, 1959 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/user-type.h` declares user and logon key payload structures and shared key-type operations for plain userspace-provided payloads.

Important APIs, types, and functions: Important exported functions or hooks: `user_preparse`, `user_free_preparse`, `user_update`, `user_revoke`, `user_destroy`, `user_describe`, `user_read`. Important types: `user_key_payload`, `key_preparsed_payload`. Important constants/macros: none.

Control flow: The key subsystem invokes the preparse/update/revoke/destroy/describe/read hooks for user and logon key types, with RCU-protected `user_key_payload` replacement on update.

State and persistence behavior: Payload bytes persist in memory until update, revoke, expiry, or destroy. Logon keys restrict readout while still using similar storage mechanics.

Dependencies and integration points: It includes `linux/key.h`, `linux/rcupdate.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Payload length accounting, RCU replacement, read permission differences, and secure cleanup for logon secrets are the important risks.

Test signals: Test keyctl add/read/update/revoke for user and logon keys, permission denial for logon readout, and concurrent readers during update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/keys/user-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/assert.h -->
# sources/distributed-fs/ceph-client/include/kunit/assert.h

Source read summary: 233 lines, 8052 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/assert.h` defines KUnit assertion data structures and formatter prototypes for fail, unary, pointer-not-error, binary, string, pointer, and memory assertions.

Important APIs, types, and functions: Important exported functions or hooks: `kunit_assert_prologue`, `kunit_fail_assert_format`, `kunit_unary_assert_format`, `kunit_ptr_not_err_assert_format`, `kunit_binary_assert_format`, `kunit_binary_ptr_assert_format`, `kunit_binary_str_assert_format`, `kunit_mem_assert_format`, `kunit_assert_print_msg`, `is_literal`, `is_str_literal`, `kunit_assert_hexdump`. Important types: `kunit`, `string_stream`, `kunit_assert_type`, `kunit_loc`, `kunit_assert`, `kunit_fail_assert`, `kunit_unary_assert`, `kunit_ptr_not_err_assert`, `kunit_binary_assert_text`, `kunit_binary_assert`, `kunit_binary_ptr_assert`, `kunit_binary_str_assert`, `kunit_mem_assert`. Important constants/macros: `KUNIT_CURRENT_LOC`.

Control flow: KUnit assertion macros instantiate these structs with a `kunit_loc`, expected/actual expressions, and optional message, then formatter callbacks print a structured failure into a `string_stream`.

State and persistence behavior: Assertion objects are usually stack/static test-time state. They do not persist beyond the running KUnit case except through emitted test logs.

Dependencies and integration points: It includes `linux/err.h`, `linux/printk.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The risk is misleading diagnostics: incorrect format callbacks, expression literal detection, or pointer/error handling can hide the true failing value even if the assertion result is correct.

Test signals: Run KUnit selftests for each assertion kind, verify formatted output, cover literal and nonliteral string handling, and compile with/without assertion-related config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/attributes.h -->
# sources/distributed-fs/ceph-client/include/kunit/attributes.h

Source read summary: 51 lines, 1383 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/attributes.h` declares KUnit suite/test attribute filtering helpers for printing attributes and iterating parsed filter expressions.

Important APIs, types, and functions: Important exported functions or hooks: `kunit_print_attr`, `kunit_get_filter_count`, `kunit_next_attr_filter`. Important types: `kunit_attr_filter`, `kunit_suite`. Important constants/macros: none.

Control flow: The KUnit runner parses attribute filters, counts them, advances with `kunit_next_attr_filter()`, and prints suite attributes for discovery/reporting.

State and persistence behavior: Filter state is per test invocation; suite attributes are static metadata associated with compiled KUnit suites.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Parsing and iteration bugs can skip tests or include tests the user meant to filter out.

Test signals: Run KUnit attribute-filter selftests for multiple filters, malformed filters, empty filters, and printed attribute output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/attributes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/clk.h -->
# sources/distributed-fs/ceph-client/include/kunit/clk.h

Source read summary: 34 lines, 1008 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/clk.h` declares KUnit-managed clock helpers for acquiring, enabling, registering, and providing clock objects with automatic cleanup tied to a test case.

Important APIs, types, and functions: Important exported functions or hooks: `clk_get_kunit`, `of_clk_get_kunit`, `clk_hw_get_clk_kunit`, `clk_hw_get_clk_prepared_enabled_kunit`, `clk_prepare_enable_kunit`, `clk_hw_register_kunit`, `of_clk_hw_register_kunit`, `of_clk_add_hw_provider_kunit`. Important types: `clk`, `clk_hw`, `device`, `device_node`, `of_phandle_args`, `kunit`. Important constants/macros: none.

Control flow: Tests call the `_kunit` clock helpers instead of raw clock APIs so resources are registered with KUnit cleanup and released when the test ends.

State and persistence behavior: Clock handles, providers, and prepared/enabled state persist only for the duration of the KUnit test unless the tested subsystem stores references.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The main risk is cleanup ordering: providers, hardware clocks, and prepared/enabled refs must unwind even when a test fails partway through setup.

Test signals: Write KUnit tests that register providers, get clocks by device tree and clk_hw, prepare/enable them, and intentionally fail after each setup stage to verify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/device.h -->
# sources/distributed-fs/ceph-client/include/kunit/device.h

Source read summary: 81 lines, 2833 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/device.h` declares KUnit-managed device and driver helpers that create or register test devices and automatically unregister them with test cleanup.

Important APIs, types, and functions: Important exported functions or hooks: `kunit_device_unregister`. Important types: `device`, `device_driver`. Important constants/macros: none.

Control flow: Driver tests allocate/register a device through these helpers, bind test drivers, and rely on KUnit cleanup to call unregister after the case exits.

State and persistence behavior: Test devices exist in the driver core only during the test case. Any references that escape cleanup become dangling driver-core state.

Dependencies and integration points: It includes `kunit/test.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Probe/remove ordering, release callbacks, and failed registration cleanup are the highest-risk paths.

Test signals: Run KUnit device-helper tests for allocation failure, successful add/remove, driver bind/unbind, and cleanup after an assertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/of.h -->
# sources/distributed-fs/ceph-client/include/kunit/of.h

Source read summary: 122 lines, 3506 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/of.h` declares KUnit helpers and macros for applying device-tree overlays, declaring overlay blobs, and registering cleanup for OF node references.

Important APIs, types, and functions: Important exported functions or hooks: `of_node_put_kunit`, `of_overlay_fdt_apply_kunit`. Important types: `device_node`. Important constants/macros: `of_overlay_begin`, `of_overlay_end`, `OF_OVERLAY_DECLARE`, `of_overlay_apply_kunit`.

Control flow: Tests use `OF_OVERLAY_DECLARE`, `of_overlay_apply_kunit()`, or `of_overlay_fdt_apply_kunit()` to install a temporary overlay, then KUnit cleanup removes it and drops OF node references.

State and persistence behavior: Overlay state mutates the live OF tree during a test and must be removed before the next test. Node references are scoped to KUnit cleanup.

Dependencies and integration points: It includes `kunit/test.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Overlay lifetime, duplicate symbols, failed partial applies, and leaked node references can contaminate later tests.

Test signals: Run OF overlay KUnit tests for apply/remove, invalid FDT data, nested overlays, node get/put cleanup, and tests that fail after applying an overlay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/platform_device.h -->
# sources/distributed-fs/ceph-client/include/kunit/platform_device.h

Source read summary: 22 lines, 607 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/platform_device.h` declares KUnit helpers for allocating/adding platform devices and registering platform drivers with optional probe-completion synchronization.

Important APIs, types, and functions: Important exported functions or hooks: `kunit_platform_device_alloc`, `kunit_platform_device_add`, `kunit_platform_device_prepare_wait_for_probe`, `kunit_platform_driver_register`. Important types: `completion`, `kunit`, `platform_device`, `platform_driver`. Important constants/macros: none.

Control flow: Platform-driver tests allocate a device, add it to the platform bus, optionally wait for probe completion, and register drivers under KUnit cleanup ownership.

State and persistence behavior: Platform devices and drivers persist only for the running test case and are unregistered by cleanup actions.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Asynchronous probe ordering and cleanup after partial setup are the main edge cases.

Test signals: Test probe success/failure, deferred/asynchronous probe wait paths, driver registration cleanup, and device add failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/platform_device.h -->

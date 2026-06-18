# subset-b-005816 Research

Grouped source research for Linux device-tree clock binding headers under `sources/distributed-fs/ceph-client/include/dt-bindings/clock`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-aoclkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-aoclkc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-aoclkc.h` is a Linux device-tree clock binding header for the Amlogic Meson GXBB clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 75-line, 3090-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `14` `#define` constants, with directly parsed numeric values spanning `0..13`. The largest macro families are `CLKID_AO` (14). Early IDs include `CLKID_AO_REMOTE`, `CLKID_AO_I2C_MASTER`, `CLKID_AO_I2C_SLAVE`, `CLKID_AO_UART1`, `CLKID_AO_UART2`, `CLKID_AO_IR_BLASTER`; the trailing IDs include `CLKID_AO_32K_PRE`, `CLKID_AO_32K_DIV`, `CLKID_AO_32K_SEL`, `CLKID_AO_32K`, `CLKID_AO_CTS_RTC_OSCIN`, `CLKID_AO_CLK81`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `CLKID_AO`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-aoclkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-clkc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-clkc.h` is a Linux device-tree clock binding header for the Amlogic Meson GXBB clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 217-line, 5944-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `206` `#define` constants, with directly parsed numeric values spanning `0..206`. The largest macro families are `CLKID_VCLK2` (19), `CLKID_VCLK` (14), `CLKID_CTS` (13), `CLKID_HDMI` (12), `CLKID_SD` (12), `CLKID_FCLK` (10). Early IDs include `CLKID_SYS_PLL`, `CLKID_HDMI_PLL`, `CLKID_FIXED_PLL`, `CLKID_FCLK_DIV2`, `CLKID_FCLK_DIV3`, `CLKID_FCLK_DIV4`; the trailing IDs include `CLKID_CTS_VDAC`, `CLKID_HDMI_TX`, `CLKID_HDMI_SEL`, `CLKID_HDMI_DIV`, `CLKID_HDMI`, `CLKID_ACODEC`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__GXBB_CLKC_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/gxbb-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3516cv300-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3516cv300-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3516cv300-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 37-line, 1068-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `23` `#define` constants, with directly parsed numeric values spanning `0..21`. The largest macro families are `HI3516CV300_USB2` (7), `HI3516CV300_ETH` (2), `HI3516CV300_APB` (1), `HI3516CV300_DMAC` (1), `HI3516CV300_FMC` (1), `HI3516CV300_MMC0` (1). Early IDs include `HI3516CV300_APB_CLK`, `HI3516CV300_UART0_CLK`, `HI3516CV300_UART1_CLK`, `HI3516CV300_UART2_CLK`, `HI3516CV300_SPI0_CLK`, `HI3516CV300_SPI1_CLK`; the trailing IDs include `HI3516CV300_USB2_OHCI12M_CLK`, `HI3516CV300_USB2_OTG_UTMI_CLK`, `HI3516CV300_USB2_HST_PHY_CLK`, `HI3516CV300_USB2_UTMI0_CLK`, `HI3516CV300_USB2_PHY_CLK`, `HI3516CV300_WDT_CLK`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `hi3516CV300 core CRG`, `hi3516CV300 sysctrl CRG`, `__DTS_HI3516CV300_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3516cv300-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3519-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3519-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3519-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 29-line, 728-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `18` `#define` constants, with directly parsed numeric values spanning `1..18`. The largest macro families are `HI3519_ETH` (3), `HI3519_USB2` (2), `HI3519_DMA` (1), `HI3519_FMC` (1), `HI3519_IR` (1), `HI3519_PWM` (1). Early IDs include `HI3519_FMC_CLK`, `HI3519_SPI0_CLK`, `HI3519_SPI1_CLK`, `HI3519_SPI2_CLK`, `HI3519_UART0_CLK`, `HI3519_UART1_CLK`; the trailing IDs include `HI3519_ETH_PHY_CLK`, `HI3519_ETH_MAC_CLK`, `HI3519_ETH_MACIF_CLK`, `HI3519_USB2_BUS_CLK`, `HI3519_USB2_PORT_CLK`, `HI3519_USB3_CLK`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DTS_HI3519_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3519-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3559av100-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3559av100-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3559av100-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 166-line, 5702-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `132` `#define` constants, with directly parsed numeric values spanning `0..256`. The largest macro families are `HI3559AV100_FIXED` (45), `HI3559AV100_SHUB` (32), `HI3559AV100_EDMAC` (2), `HI3559AV100_EDMAC1` (2), `HI3559AV100_ETH` (2), `HI3559AV100_ETH1` (2). Early IDs include `HI3559AV100_FIXED_1188M`, `HI3559AV100_FIXED_1000M`, `HI3559AV100_FIXED_842M`, `HI3559AV100_FIXED_792M`, `HI3559AV100_FIXED_750M`, `HI3559AV100_FIXED_710M`; the trailing IDs include `HI3559AV100_SHUB_UART3_CLK`, `HI3559AV100_SHUB_UART4_CLK`, `HI3559AV100_SHUB_UART5_CLK`, `HI3559AV100_SHUB_UART6_CLK`, `HI3559AV100_SHUB_EDMAC_CLK`, `HI3559AV100_SHUB_NR_CLKS`. Sentinel or count-style constants visible in this header are `HI3559AV100_CRG_NR_CLKS`, `HI3559AV100_SHUB_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate`, `mux clocks`, `gate clocks`, `complex`, `pll clocks`, `__DTS_HI3559AV100_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3559av100-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3620-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3620-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3620-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 144-line, 3821-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `119` `#define` constants, with directly parsed numeric values spanning `0..219`. The largest macro families are `HI3620_MMC` (6), `HI3620_PLL` (6), `HI3620_RCLK` (4), `HI3620_SD` (4), `HI3620_MMC1` (3), `HI3620_MMC2` (2). Early IDs include `HI3620_NONE_CLOCK`, `HI3620_OSC32K`, `HI3620_OSC26M`, `HI3620_PCLK`, `HI3620_PLL_ARM0`, `HI3620_PLL_ARM1`; the trailing IDs include `HI3620_MCU_CLK`, `HI3620_SD_CIUCLK`, `HI3620_MMC_CIUCLK1`, `HI3620_MMC_CIUCLK2`, `HI3620_MMC_CIUCLK3`, `HI3620_NR_CLKS`. Sentinel or count-style constants visible in this header are `HI3620_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate & fixed factor clocks`, `mux clocks`, `divider clocks`, `gate clocks`, `__DTS_HI3620_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3620-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 215-line, 6747-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `190` `#define` constants, with directly parsed numeric values spanning `0..156`. The largest macro families are `HI3660_CLK` (132), `HI3660_PCLK` (38), `HI3660_ACLK` (5), `HI3660_GATE` (3), `HI3660_AUTODIV` (2), `HI3660_CLKIN` (2). Early IDs include `HI3660_CLKIN_SYS`, `HI3660_CLKIN_REF`, `HI3660_CLK_FLL_SRC`, `HI3660_CLK_PPLL0`, `HI3660_CLK_PPLL1`, `HI3660_CLK_PPLL2`; the trailing IDs include `HI3660_CLK_IOMCU_PERI0`, `HI3660_CLK_STUB_CLUSTER0`, `HI3660_CLK_STUB_CLUSTER1`, `HI3660_CLK_STUB_GPU`, `HI3660_CLK_STUB_DDR`, `HI3660_CLK_STUB_NUM`. Sentinel or count-style constants visible in this header are `HI3660_CLK_STUB_NUM`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate clocks`, `clk in crgctrl`, `clk in pmuctrl`, `clk in pctrl`, `clk in sctrl`, `clk in iomcu`, `clk in stub clock`, `__DTS_HI3660_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3670-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3670-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3670-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 349-line, 11940-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `320` `#define` constants, with directly parsed numeric values spanning `0..220`. The largest macro families are `HI3670_CLK` (219), `HI3670_PCLK` (59), `HI3670_ACLK` (7), `HI3670_ABB` (4), `HI3670_AUTODIV` (3), `HI3670_GATE` (3). Early IDs include `HI3670_CLK_STUB_CLUSTER0`, `HI3670_CLK_STUB_CLUSTER1`, `HI3670_CLK_STUB_GPU`, `HI3670_CLK_STUB_DDR`, `HI3670_CLK_STUB_DDR_VOTE`, `HI3670_CLK_STUB_DDR_LIMIT`; the trailing IDs include `HI3670_CLK_GATE_MMBUF`, `HI3670_PCLK_GATE_MMBUF`, `HI3670_CLK_GATE_ATDIV_VIVO`, `HI3670_CLK_GATE_VDECFREQ`, `HI3670_CLK_GATE_VENCFREQ`, `HI3670_CLK_GATE_ICSFREQ`. Sentinel or count-style constants visible in this header are `HI3670_CLK_STUB_NUM`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `clk in stub clock`, `clk in crg clock`, `clk in sctrl`, `clk in pmuctrl`, `clk in pctrl`, `clk in iomcu`, `clk in media1`, `clk in media2`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3670-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 179-line, 4473-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `133` `#define` constants, with directly parsed numeric values spanning `0..60`. The largest macro families are `HI6220_MMC0` (12), `HI6220_MMC1` (12), `HI6220_MMC2` (12), `HI6220_PLL` (9), `HI6220_ISP` (5), `HI6220_ADE` (4). Early IDs include `HI6220_NONE_CLOCK`, `HI6220_REF32K`, `HI6220_CLK_TCXO`, `HI6220_MMC1_PAD`, `HI6220_MMC2_PAD`, `HI6220_MMC0_PAD`; the trailing IDs include `HI6220_PLL_MEDIA_GATE`, `HI6220_PLL0_BBP_GATE`, `HI6220_DDRC_SRC`, `HI6220_DDRC_AXI1`, `HI6220_POWER_NR_CLKS`, `HI6220_ACPU_SFT_AT_S`. Sentinel or count-style constants visible in this header are `HI6220_AO_NR_CLKS`, `HI6220_SYS_NR_CLKS`, `HI6220_MEDIA_NR_CLKS`, `HI6220_POWER_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `clk in Hi6220 AO (always on) controller`, `fixed rate clocks`, `fixed factor clocks`, `gate clocks`, `clk in Hi6220 systrl`, `gate clock`, `mux clocks`, `divider clocks`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hip04-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hip04-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hip04-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 22-line, 462-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `5` `#define` constants, with directly parsed numeric values spanning `0..64`. The largest macro families are `HIP04_CLK` (2), `HIP04_NONE` (1), `HIP04_NR` (1), `HIP04_OSC50M` (1). Early IDs include `HIP04_NONE_CLOCK`, `HIP04_OSC50M`, `HIP04_CLK_50M`, `HIP04_CLK_168M`, `HIP04_NR_CLKS`; the trailing IDs include `HIP04_NONE_CLOCK`, `HIP04_OSC50M`, `HIP04_CLK_50M`, `HIP04_CLK_168M`, `HIP04_NR_CLKS`. Sentinel or count-style constants visible in this header are `HIP04_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate & fixed factor clocks`, `__DTS_HIP04_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hip04-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/histb-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/histb-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/histb-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 71-line, 1994-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `57` `#define` constants, with directly parsed numeric values spanning `0..50`. The largest macro families are `HISTB_USB2` (8), `HISTB_USB3` (8), `HISTB_MMC` (4), `HISTB_PCIE` (4), `HISTB_SDIO0` (4), `HISTB_ETH0` (2). Early IDs include `HISTB_OSC_CLK`, `HISTB_APB_CLK`, `HISTB_AHB_CLK`, `HISTB_UART1_CLK`, `HISTB_UART2_CLK`, `HISTB_UART3_CLK`; the trailing IDs include `HISTB_MCE_CLK`, `HISTB_IR_CLK`, `HISTB_TIMER01_CLK`, `HISTB_LEDC_CLK`, `HISTB_UART0_CLK`, `HISTB_LSADC_CLK`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `clocks provided by core CRG`, `clocks provided by mcu CRG`, `__DTS_HISTB_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/histb-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hix5hd2-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hix5hd2-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hix5hd2-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 83-line, 2252-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `64` `#define` constants, with directly parsed numeric values spanning `1..256`. The largest macro families are `HIX5HD2_FIXED` (30), `HIX5HD2_MMC` (4), `HIX5HD2_SD` (4), `HIX5HD2_SFC` (3), `HIX5HD2_FWD` (2), `HIX5HD2_I2C0` (2). Early IDs include `HIX5HD2_FIXED_1200M`, `HIX5HD2_FIXED_400M`, `HIX5HD2_FIXED_48M`, `HIX5HD2_FIXED_24M`, `HIX5HD2_FIXED_600M`, `HIX5HD2_FIXED_300M`; the trailing IDs include `HIX5HD2_I2C5_RST`, `HIX5HD2_MAC0_CLK`, `HIX5HD2_MAC1_CLK`, `HIX5HD2_SATA_CLK`, `HIX5HD2_USB_CLK`, `HIX5HD2_NR_CLKS`. Sentinel or count-style constants visible in this header are `HIX5HD2_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate`, `mux clocks`, `gate clocks`, `complex`, `__DTS_HIX5HD2_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hix5hd2-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx1-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx1-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx1-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 37-line, 906-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `26` `#define` constants, with directly parsed numeric values spanning `0..25`. The largest macro families are `IMX1_CLK` (26). Early IDs include `IMX1_CLK_DUMMY`, `IMX1_CLK_CLK32`, `IMX1_CLK_CLK16M_EXT`, `IMX1_CLK_CLK16M`, `IMX1_CLK_CLK32_PREMULT`, `IMX1_CLK_PREM`; the trailing IDs include `IMX1_CLK_BROM_GATE`, `IMX1_CLK_DMA_GATE`, `IMX1_CLK_CSI_GATE`, `IMX1_CLK_MMA_GATE`, `IMX1_CLK_USBD_GATE`, `IMX1_CLK_MAX`. Sentinel or count-style constants visible in this header are `IMX1_CLK_MAX`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `IMX1_CLK`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx1-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx21-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx21-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx21-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 77-line, 2312-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `66` `#define` constants, with directly parsed numeric values spanning `0..65`. The largest macro families are `IMX21_CLK` (66). Early IDs include `IMX21_CLK_DUMMY`, `IMX21_CLK_CKIL`, `IMX21_CLK_CKIH`, `IMX21_CLK_FPM`, `IMX21_CLK_CKIH_DIV1P5`, `IMX21_CLK_MPLL_GATE`; the trailing IDs include `IMX21_CLK_GPT3_IPG_GATE`, `IMX21_CLK_PWM_IPG_GATE`, `IMX21_CLK_RTC_GATE`, `IMX21_CLK_KPP_GATE`, `IMX21_CLK_OWIRE_GATE`, `IMX21_CLK_MAX`. Sentinel or count-style constants visible in this header are `IMX21_CLK_MAX`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `IMX21_CLK`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx21-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx27-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx27-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx27-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 105-line, 3345-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `94` `#define` constants, with directly parsed numeric values spanning `0..93`. The largest macro families are `IMX27_CLK` (94). Early IDs include `IMX27_CLK_DUMMY`, `IMX27_CLK_CKIH`, `IMX27_CLK_CKIL`, `IMX27_CLK_MPLL`, `IMX27_CLK_SPLL`, `IMX27_CLK_MPLL_MAIN2`; the trailing IDs include `IMX27_CLK_RTIC_IPG_GATE`, `IMX27_CLK_MSHC_IPG_GATE`, `IMX27_CLK_RTIC_AHB_GATE`, `IMX27_CLK_MSHC_BAUD_GATE`, `IMX27_CLK_CKIH_GATE`, `IMX27_CLK_MAX`. Sentinel or count-style constants visible in this header are `IMX27_CLK_MAX`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `IMX27_CLK`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx27-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx5-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx5-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx5-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 217-line, 7099-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `206` `#define` constants, with directly parsed numeric values spanning `0..206`. The largest macro families are `IMX5_CLK` (206). Early IDs include `IMX5_CLK_DUMMY`, `IMX5_CLK_CKIL`, `IMX5_CLK_OSC`, `IMX5_CLK_CKIH1`, `IMX5_CLK_CKIH2`, `IMX5_CLK_AHB`; the trailing IDs include `IMX5_CLK_IEEE1588_PRED`, `IMX5_CLK_IEEE1588_SEL`, `IMX5_CLK_IEEE1588_PODF`, `IMX5_CLK_IEEE1588_GATE`, `IMX5_CLK_SCC2_IPG_GATE`, `IMX5_CLK_END`. Sentinel or count-style constants visible in this header are `IMX5_CLK_AHB_MAX`, `IMX5_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_IMX5_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx5-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6qdl-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6qdl-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6qdl-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 281-line, 9689-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `270` `#define` constants, with directly parsed numeric values spanning `0..268`. The largest macro families are `IMX6QDL_CLK` (254), `IMX6QDL_PLL1` (2), `IMX6QDL_PLL2` (2), `IMX6QDL_PLL3` (2), `IMX6QDL_PLL4` (2), `IMX6QDL_PLL5` (2). Early IDs include `IMX6QDL_CLK_DUMMY`, `IMX6QDL_CLK_CKIL`, `IMX6QDL_CLK_CKIH`, `IMX6QDL_CLK_OSC`, `IMX6QDL_CLK_PLL2_PFD0_352M`, `IMX6QDL_CLK_PLL2_PFD1_594M`; the trailing IDs include `IMX6QDL_CLK_MMDC_P0_IPG`, `IMX6QDL_CLK_DCIC1`, `IMX6QDL_CLK_DCIC2`, `IMX6QDL_CLK_ENET_REF_SEL`, `IMX6QDL_CLK_ENET_REF_PAD`, `IMX6QDL_CLK_END`. Sentinel or count-style constants visible in this header are `IMX6QDL_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_IMX6QDL_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6qdl-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sl-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sl-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sl-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 179-line, 5772-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `168` `#define` constants, with directly parsed numeric values spanning `0..167`. The largest macro families are `IMX6SL_CLK` (154), `IMX6SL_PLL1` (2), `IMX6SL_PLL2` (2), `IMX6SL_PLL3` (2), `IMX6SL_PLL4` (2), `IMX6SL_PLL5` (2). Early IDs include `IMX6SL_CLK_DUMMY`, `IMX6SL_CLK_CKIL`, `IMX6SL_CLK_OSC`, `IMX6SL_CLK_PLL1_SYS`, `IMX6SL_CLK_PLL2_BUS`, `IMX6SL_CLK_PLL3_USB_OTG`; the trailing IDs include `IMX6SL_CLK_SSI2_IPG`, `IMX6SL_CLK_SSI3_IPG`, `IMX6SL_CLK_SPDIF_GCLK`, `IMX6SL_CLK_MMDC_P0_IPG`, `IMX6SL_CLK_MMDC_P1_IPG`, `IMX6SL_CLK_END`. Sentinel or count-style constants visible in this header are `IMX6SL_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_IMX6SL_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sl-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sll-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sll-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sll-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 211-line, 6518-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `181` `#define` constants, with directly parsed numeric values spanning `0..180`. The largest macro families are `IMX6SLL_CLK` (167), `IMX6SLL_PLL1` (2), `IMX6SLL_PLL2` (2), `IMX6SLL_PLL3` (2), `IMX6SLL_PLL4` (2), `IMX6SLL_PLL5` (2). Early IDs include `IMX6SLL_CLK_DUMMY`, `IMX6SLL_CLK_CKIL`, `IMX6SLL_CLK_OSC`, `IMX6SLL_PLL1_BYPASS_SRC`, `IMX6SLL_PLL2_BYPASS_SRC`, `IMX6SLL_PLL3_BYPASS_SRC`; the trailing IDs include `IMX6SLL_CLK_GPIO3`, `IMX6SLL_CLK_GPIO4`, `IMX6SLL_CLK_GPIO5`, `IMX6SLL_CLK_GPIO6`, `IMX6SLL_CLK_MMDC_P1_IPG`, `IMX6SLL_CLK_END`. Sentinel or count-style constants visible in this header are `IMX6SLL_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `CCGR 0`, `CCGR 1`, `CCGR2`, `CCGR3`, `CCGR4`, `CCGR 5`, `CCGR 6`, `__DT_BINDINGS_CLOCK_IMX6SLL_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sll-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sx-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sx-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sx-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 282-line, 9119-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `271` `#define` constants, with directly parsed numeric values spanning `0..270`. The largest macro families are `IMX6SX_CLK` (257), `IMX6SX_PLL1` (2), `IMX6SX_PLL2` (2), `IMX6SX_PLL3` (2), `IMX6SX_PLL4` (2), `IMX6SX_PLL5` (2). Early IDs include `IMX6SX_CLK_DUMMY`, `IMX6SX_CLK_CKIL`, `IMX6SX_CLK_CKIH`, `IMX6SX_CLK_OSC`, `IMX6SX_CLK_PLL1_SYS`, `IMX6SX_CLK_PLL2_BUS`; the trailing IDs include `IMX6SX_CLK_LVDS2_SEL`, `IMX6SX_CLK_LVDS2_OUT`, `IMX6SX_CLK_LVDS2_IN`, `IMX6SX_CLK_ANACLK2`, `IMX6SX_CLK_MMDC_P1_IPG`, `IMX6SX_CLK_CLK_END`. Sentinel or count-style constants visible in this header are `IMX6SX_CLK_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_IMX6SX_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6sx-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6ul-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6ul-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6ul-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 268-line, 8630-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `256` `#define` constants, with directly parsed numeric values spanning `0..255`. The largest macro families are `IMX6UL_CLK` (229), `IMX6ULL_CLK` (12), `IMX6UL_PLL1` (2), `IMX6UL_PLL2` (2), `IMX6UL_PLL3` (2), `IMX6UL_PLL4` (2). Early IDs include `IMX6UL_CLK_DUMMY`, `IMX6UL_CLK_CKIL`, `IMX6UL_CLK_CKIH`, `IMX6UL_CLK_OSC`, `IMX6UL_PLL1_BYPASS_SRC`, `IMX6UL_PLL2_BYPASS_SRC`; the trailing IDs include `IMX6UL_CLK_ENET1_REF_125M`, `IMX6UL_CLK_ENET1_REF_SEL`, `IMX6UL_CLK_ENET1_REF_PAD`, `IMX6UL_CLK_ENET2_REF_SEL`, `IMX6UL_CLK_ENET2_REF_PAD`, `IMX6UL_CLK_END`. Sentinel or count-style constants visible in this header are `IMX6UL_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_IMX6UL_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx6ul-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7d-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7d-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7d-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 457-line, 16120-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `447` `#define` constants, with directly parsed numeric values spanning `0..446`. The largest macro families are `IMX7D_PLL` (65), `IMX7D_DRAM` (18), `IMX7D_MIPI` (15), `IMX7D_ARM` (12), `IMX7D_NAND` (12), `IMX7D_ENET` (10). Early IDs include `IMX7D_OSC_24M_CLK`, `IMX7D_PLL_ARM_MAIN`, `IMX7D_PLL_ARM_MAIN_CLK`, `IMX7D_PLL_ARM_MAIN_SRC`, `IMX7D_PLL_ARM_MAIN_BYPASS`, `IMX7D_PLL_SYS_MAIN`; the trailing IDs include `IMX7D_NAND_USDHC_BUS_RAWNAND_CLK`, `IMX7D_SNVS_CLK`, `IMX7D_CAAM_CLK`, `IMX7D_KPP_ROOT_CLK`, `IMX7D_PXP_CLK`, `IMX7D_CLK_END`. Sentinel or count-style constants visible in this header are `IMX7D_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `unused`, `unused`, `unused`, `unused`, `__DT_BINDINGS_CLOCK_IMX7D_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7d-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7ulp-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7ulp-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7ulp-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 120-line, 3349-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `93` `#define` constants, with directly parsed numeric values spanning `0..48`. The largest macro families are `IMX7ULP_CLK` (93). Early IDs include `IMX7ULP_CLK_DUMMY`, `IMX7ULP_CLK_ROSC`, `IMX7ULP_CLK_SOSC`, `IMX7ULP_CLK_FIRC`, `IMX7ULP_CLK_SPLL_PRE_SEL`, `IMX7ULP_CLK_SPLL_PRE_DIV`; the trailing IDs include `IMX7ULP_CLK_PCTLF`, `IMX7ULP_CLK_GPU3D`, `IMX7ULP_CLK_GPU2D`, `IMX7ULP_CLK_PCC3_END`, `IMX7ULP_CLK_ARM`, `IMX7ULP_CLK_SMC1_END`. Sentinel or count-style constants visible in this header are `IMX7ULP_CLK_SCG1_END`, `IMX7ULP_CLK_PCC2_END`, `IMX7ULP_CLK_PCC3_END`, `IMX7ULP_CLK_SMC1_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `SCG1`, `IMX7ULP_CLK_MIPI_PLL is unsupported and shouldn't be used in DT`, `PCC2`, `PCC3`, `SMC1`, `__DT_BINDINGS_CLOCK_IMX7ULP_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx7ulp-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 196-line, 7335-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `171` `#define` constants, with directly parsed numeric values spanning `0..73`. The largest macro families are `IMX_LSIO` (74), `IMX_ADMA` (72), `IMX_CONN` (25). Early IDs include `IMX_LSIO_LPCG_PWM0_IPG_CLK`, `IMX_LSIO_LPCG_PWM0_IPG_S_CLK`, `IMX_LSIO_LPCG_PWM0_IPG_HF_CLK`, `IMX_LSIO_LPCG_PWM0_IPG_SLV_CLK`, `IMX_LSIO_LPCG_PWM0_IPG_MSTR_CLK`, `IMX_LSIO_LPCG_PWM1_IPG_CLK`; the trailing IDs include `IMX_ADMA_ACM_SPDIF0_TX_CLK_SEL`, `IMX_ADMA_ACM_SPDIF1_TX_CLK_SEL`, `IMX_ADMA_ACM_MQS_TX_CLK_SEL`, `IMX_ADMA_ACM_ASRC0_MUX_CLK_SEL`, `IMX_ADMA_ACM_ASRC1_MUX_CLK_SEL`, `IMX_ADMA_ACM_CLK_END`. Sentinel or count-style constants visible in this header are `IMX_LSIO_LPCG_CLK_END`, `IMX_CONN_LPCG_CLK_END`, `IMX_ADMA_LPCG_CLK_END`, `IMX_ADMA_ACM_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `LPCG clocks`, `LSIO SS LPCG`, `Connectivity SS LPCG`, `ADMA SS LPCG`, `__DT_BINDINGS_CLOCK_IMX_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-lpcg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-lpcg.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-lpcg.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 15-line, 321-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `8` `#define` constants, with directly parsed numeric values spanning `0..28`. The largest macro families are `IMX_LPCG` (8). Early IDs include `IMX_LPCG_CLK_0`, `IMX_LPCG_CLK_1`, `IMX_LPCG_CLK_2`, `IMX_LPCG_CLK_3`, `IMX_LPCG_CLK_4`, `IMX_LPCG_CLK_5`; the trailing IDs include `IMX_LPCG_CLK_2`, `IMX_LPCG_CLK_3`, `IMX_LPCG_CLK_4`, `IMX_LPCG_CLK_5`, `IMX_LPCG_CLK_6`, `IMX_LPCG_CLK_7`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `IMX_LPCG`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8-lpcg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mm-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mm-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mm-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 287-line, 9044-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `259` `#define` constants, with directly parsed numeric values spanning `0..258`. The largest macro families are `IMX8MM_CLK` (184), `IMX8MM_SYS` (46), `IMX8MM_AUDIO` (8), `IMX8MM_ARM` (4), `IMX8MM_DRAM` (4), `IMX8MM_GPU` (4). Early IDs include `IMX8MM_CLK_DUMMY`, `IMX8MM_CLK_32K`, `IMX8MM_CLK_24M`, `IMX8MM_OSC_HDMI_CLK`, `IMX8MM_CLK_EXT1`, `IMX8MM_CLK_EXT2`; the trailing IDs include `IMX8MM_CLK_CLKOUT1_DIV`, `IMX8MM_CLK_CLKOUT1`, `IMX8MM_CLK_CLKOUT2_SEL`, `IMX8MM_CLK_CLKOUT2_DIV`, `IMX8MM_CLK_CLKOUT2`, `IMX8MM_CLK_END`. Sentinel or count-style constants visible in this header are `IMX8MM_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `core`, `bus`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mm-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mn-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mn-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mn-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 271-line, 8759-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `244` `#define` constants, with directly parsed numeric values spanning `0..235`. The largest macro families are `IMX8MN_CLK` (161), `IMX8MN_SYS` (46), `IMX8MN_AUDIO` (8), `IMX8MN_VIDEO` (8), `IMX8MN_ARM` (4), `IMX8MN_DRAM` (4). Early IDs include `IMX8MN_CLK_DUMMY`, `IMX8MN_CLK_32K`, `IMX8MN_CLK_24M`, `IMX8MN_OSC_HDMI_CLK`, `IMX8MN_CLK_EXT1`, `IMX8MN_CLK_EXT2`; the trailing IDs include `IMX8MN_CLK_GPT4_ROOT`, `IMX8MN_CLK_GPT5`, `IMX8MN_CLK_GPT5_ROOT`, `IMX8MN_CLK_GPT6`, `IMX8MN_CLK_GPT6_ROOT`, `IMX8MN_CLK_END`. Sentinel or count-style constants visible in this header are `IMX8MN_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `CORE CLOCK ROOT`, `BUS CLOCK ROOT`, `IPG CLOCK ROOT`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mn-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mp-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mp-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mp-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 402-line, 14181-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `386` `#define` constants, with directly parsed numeric values spanning `0..330`. The largest macro families are `IMX8MP_CLK` (311), `IMX8MP_SYS` (46), `IMX8MP_AUDIO` (8), `IMX8MP_ARM` (4), `IMX8MP_DRAM` (4), `IMX8MP_GPU` (4). Early IDs include `IMX8MP_CLK_DUMMY`, `IMX8MP_CLK_32K`, `IMX8MP_CLK_24M`, `IMX8MP_OSC_HDMI_CLK`, `IMX8MP_CLK_EXT1`, `IMX8MP_CLK_EXT2`; the trailing IDs include `IMX8MP_CLK_AUDIOMIX_PDM_SEL`, `IMX8MP_CLK_AUDIOMIX_SAI_PLL_REF_SEL`, `IMX8MP_CLK_AUDIOMIX_SAI_PLL`, `IMX8MP_CLK_AUDIOMIX_SAI_PLL_BYPASS`, `IMX8MP_CLK_AUDIOMIX_SAI_PLL_OUT`, `IMX8MP_CLK_AUDIOMIX_END`. Sentinel or count-style constants visible in this header are `IMX8MP_CLK_END`, `IMX8MP_CLK_AUDIOMIX_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `IMX8MP_CLK`, `IMX8MP_SYS`, `IMX8MP_AUDIO`, `IMX8MP_ARM`, `IMX8MP_DRAM`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are `IMX8MP_CLK_SAI4`; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mp-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mq-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mq-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mq-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 432-line, 11338-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `285` `#define` constants, with directly parsed numeric values spanning `0..303`. The largest macro families are `IMX8MQ_CLK` (198), `IMX8MQ_SYS1` (18), `IMX8MQ_SYS2` (18), `IMX8MQ_AUDIO` (10), `IMX8MQ_DRAM` (9), `IMX8MQ_SYS3` (9). Early IDs include `IMX8MQ_CLK_DUMMY`, `IMX8MQ_CLK_32K`, `IMX8MQ_CLK_25M`, `IMX8MQ_CLK_27M`, `IMX8MQ_CLK_EXT1`, `IMX8MQ_CLK_EXT2`; the trailing IDs include `IMX8MQ_CLK_MON_SYS_PLL3_DIV`, `IMX8MQ_CLK_MON_DRAM_PLL_DIV`, `IMX8MQ_CLK_MON_VIDEO_PLL2_DIV`, `IMX8MQ_CLK_MON_SEL`, `IMX8MQ_CLK_MON_CLK2_OUT`, `IMX8MQ_CLK_END`. Sentinel or count-style constants visible in this header are `IMX8MQ_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `ANAMIX PLL clocks`, `FRAC PLLs`, `ARM PLL`, `GPU PLL`, `VPU PLL`, `AUDIO PLL1`, `AUDIO PLL2`, `VIDEO PLL1`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8mq-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8ulp-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8ulp-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8ulp-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 264-line, 8403-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `236` `#define` constants, with directly parsed numeric values spanning `0..56`. The largest macro families are `IMX8ULP_CLK` (236). Early IDs include `IMX8ULP_CLK_DUMMY`, `IMX8ULP_CLK_SPLL2`, `IMX8ULP_CLK_SPLL3`, `IMX8ULP_CLK_A35_SEL`, `IMX8ULP_CLK_A35_DIV`, `IMX8ULP_CLK_SPLL2_PRE_SEL`; the trailing IDs include `IMX8ULP_CLK_AVD_SIM`, `IMX8ULP_CLK_DSI_TX_ESC`, `IMX8ULP_CLK_PCC5_END`, `IMX8ULP_CLK_SIM_LPAV_HIFI_CORE`, `IMX8ULP_CLK_SIM_LPAV_HIFI_PBCLK`, `IMX8ULP_CLK_SIM_LPAV_HIFI_PLAT`. Sentinel or count-style constants visible in this header are `IMX8ULP_CLK_CGC1_END`, `IMX8ULP_CLK_CGC2_END`, `IMX8ULP_CLK_PCC3_END`, `IMX8ULP_CLK_PCC4_END`, `IMX8ULP_CLK_PCC5_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `CGC1`, `CGC2`, `PCC3`, `PCC4`, `PCC5`, `LPAV SIM`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx8ulp-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx93-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx93-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx93-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 215-line, 6843-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `204` `#define` constants, with directly parsed numeric values spanning `0..207`. The largest macro families are `IMX93_CLK` (199), `IMX91_CLK` (5). Early IDs include `IMX93_CLK_DUMMY`, `IMX93_CLK_24M`, `IMX93_CLK_EXT1`, `IMX93_CLK_SYS_PLL_PFD0`, `IMX93_CLK_SYS_PLL_PFD0_DIV2`, `IMX93_CLK_SYS_PLL_PFD1`; the trailing IDs include `IMX91_CLK_ENET1_QOS_TSN`, `IMX91_CLK_ENET_TIMER`, `IMX91_CLK_ENET2_REGULAR`, `IMX91_CLK_ENET2_REGULAR_GATE`, `IMX91_CLK_ENET1_QOS_TSN_GATE`, `IMX93_CLK_SPDIF_IPG`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `IMX93_CLK`, `IMX91_CLK`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imx93-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imxrt1050-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/imxrt1050-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/imxrt1050-clock.h` is a Linux device-tree clock binding header for the NXP i.MX clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 73-line, 2533-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `61` `#define` constants, with directly parsed numeric values spanning `0..61`. The largest macro families are `IMXRT1050_CLK` (61). Early IDs include `IMXRT1050_CLK_DUMMY`, `IMXRT1050_CLK_CKIL`, `IMXRT1050_CLK_CKIH`, `IMXRT1050_CLK_OSC`, `IMXRT1050_CLK_PLL2_PFD0_352M`, `IMXRT1050_CLK_PLL2_PFD1_594M`; the trailing IDs include `IMXRT1050_CLK_IPG_PDOF`, `IMXRT1050_CLK_PER_CLK_SEL`, `IMXRT1050_CLK_PER_PDOF`, `IMXRT1050_CLK_DMA`, `IMXRT1050_CLK_DMA_MUX`, `IMXRT1050_CLK_END`. Sentinel or count-style constants visible in this header are `IMXRT1050_CLK_END`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_IMXRT1050_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/imxrt1050-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4725b-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4725b-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4725b-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 37-line, 996-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `26` `#define` constants, with directly parsed numeric values spanning `0..25`. The largest macro families are `JZ4725B_CLK` (26). Early IDs include `JZ4725B_CLK_EXT`, `JZ4725B_CLK_OSC32K`, `JZ4725B_CLK_PLL`, `JZ4725B_CLK_PLL_HALF`, `JZ4725B_CLK_CCLK`, `JZ4725B_CLK_HCLK`; the trailing IDs include `JZ4725B_CLK_MMC1`, `JZ4725B_CLK_BCH`, `JZ4725B_CLK_TCU`, `JZ4725B_CLK_EXT512`, `JZ4725B_CLK_RTC`, `JZ4725B_CLK_UDC_PHY`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_JZ4725B_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4725b-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4740-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4740-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4740-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 40-line, 1094-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `23` `#define` constants, with directly parsed numeric values spanning `0..22`. The largest macro families are `JZ4740_CLK` (23). Early IDs include `JZ4740_CLK_EXT`, `JZ4740_CLK_RTC`, `JZ4740_CLK_PLL`, `JZ4740_CLK_PLL_HALF`, `JZ4740_CLK_CCLK`, `JZ4740_CLK_HCLK`; the trailing IDs include `JZ4740_CLK_DMA`, `JZ4740_CLK_IPU`, `JZ4740_CLK_ADC`, `JZ4740_CLK_I2C`, `JZ4740_CLK_AIC`, `JZ4740_CLK_TCU`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_JZ4740_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4740-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4755-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4755-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4755-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 50-line, 1354-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `39` `#define` constants, with directly parsed numeric values spanning `0..38`. The largest macro families are `JZ4755_CLK` (39). Early IDs include `JZ4755_CLK_EXT`, `JZ4755_CLK_OSC32K`, `JZ4755_CLK_PLL`, `JZ4755_CLK_PLL_HALF`, `JZ4755_CLK_EXT_HALF`, `JZ4755_CLK_CCLK`; the trailing IDs include `JZ4755_CLK_IDCT`, `JZ4755_CLK_DB`, `JZ4755_CLK_ME`, `JZ4755_CLK_MC`, `JZ4755_CLK_TSSI`, `JZ4755_CLK_IPU`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_JZ4755_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4755-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4760-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4760-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4760-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 57-line, 1541-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `46` `#define` constants, with directly parsed numeric values spanning `0..45`. The largest macro families are `JZ4760_CLK` (46). Early IDs include `JZ4760_CLK_EXT`, `JZ4760_CLK_OSC32K`, `JZ4760_CLK_PLL0`, `JZ4760_CLK_PLL0_HALF`, `JZ4760_CLK_PLL1`, `JZ4760_CLK_CCLK`; the trailing IDs include `JZ4760_CLK_RTC`, `JZ4760_CLK_LPCLK_DIV`, `JZ4760_CLK_TVE`, `JZ4760_CLK_LPCLK`, `JZ4760_CLK_MDMA`, `JZ4760_CLK_BDMA`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_JZ4760_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4760-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4770-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4770-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4770-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 60-line, 1630-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `49` `#define` constants, with directly parsed numeric values spanning `0..48`. The largest macro families are `JZ4770_CLK` (49). Early IDs include `JZ4770_CLK_EXT`, `JZ4770_CLK_OSC32K`, `JZ4770_CLK_PLL0`, `JZ4770_CLK_PLL1`, `JZ4770_CLK_CCLK`, `JZ4770_CLK_H0CLK`; the trailing IDs include `JZ4770_CLK_VPU`, `JZ4770_CLK_UHC_PHY`, `JZ4770_CLK_OTG_PHY`, `JZ4770_CLK_EXT512`, `JZ4770_CLK_RTC`, `JZ4770_CLK_BDMA`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_JZ4770_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4770-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4780-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4780-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4780-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 92-line, 2643-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `75` `#define` constants, with directly parsed numeric values spanning `0..74`. The largest macro families are `JZ4780_CLK` (75). Early IDs include `JZ4780_CLK_EXCLK`, `JZ4780_CLK_RTCLK`, `JZ4780_CLK_APLL`, `JZ4780_CLK_MPLL`, `JZ4780_CLK_EPLL`, `JZ4780_CLK_VPLL`; the trailing IDs include `JZ4780_CLK_SMB4`, `JZ4780_CLK_DES`, `JZ4780_CLK_X2D`, `JZ4780_CLK_CORE1`, `JZ4780_CLK_EXCLK_DIV512`, `JZ4780_CLK_RTC`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_JZ4780_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,jz4780-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,sysost.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,sysost.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,sysost.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 36-line, 987-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `23` `#define` constants, with directly parsed numeric values spanning `0..15`. The largest macro families are `OST_CLK` (23). Early IDs include `OST_CLK_PERCPU_TIMER`, `OST_CLK_GLOBAL_TIMER`, `OST_CLK_PERCPU_TIMER0`, `OST_CLK_PERCPU_TIMER1`, `OST_CLK_PERCPU_TIMER2`, `OST_CLK_PERCPU_TIMER3`; the trailing IDs include `OST_CLK_EVENT_TIMER10`, `OST_CLK_EVENT_TIMER11`, `OST_CLK_EVENT_TIMER12`, `OST_CLK_EVENT_TIMER13`, `OST_CLK_EVENT_TIMER14`, `OST_CLK_EVENT_TIMER15`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_INGENIC_OST_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,sysost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,tcu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,tcu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,tcu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 21-line, 500-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `10` `#define` constants, with directly parsed numeric values spanning `0..9`. The largest macro families are `TCU_CLK` (10). Early IDs include `TCU_CLK_TIMER0`, `TCU_CLK_TIMER1`, `TCU_CLK_TIMER2`, `TCU_CLK_TIMER3`, `TCU_CLK_TIMER4`, `TCU_CLK_TIMER5`; the trailing IDs include `TCU_CLK_TIMER4`, `TCU_CLK_TIMER5`, `TCU_CLK_TIMER6`, `TCU_CLK_TIMER7`, `TCU_CLK_WDT`, `TCU_CLK_OST`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_INGENIC_TCU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,tcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1000-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1000-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1000-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 59-line, 1650-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `42` `#define` constants, with directly parsed numeric values spanning `0..41`. The largest macro families are `X1000_CLK` (42). Early IDs include `X1000_CLK_EXCLK`, `X1000_CLK_RTCLK`, `X1000_CLK_APLL`, `X1000_CLK_MPLL`, `X1000_CLK_OTGPHY`, `X1000_CLK_SCLKA`; the trailing IDs include `X1000_CLK_EXCLK_DIV512`, `X1000_CLK_RTC`, `X1000_CLK_AIC`, `X1000_CLK_I2SPLLMUX`, `X1000_CLK_I2SPLL`, `X1000_CLK_I2S`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_X1000_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1000-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1830-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1830-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1830-cgu.h` is a Linux device-tree clock binding header for the Ingenic clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 58-line, 1620-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `41` `#define` constants, with directly parsed numeric values spanning `0..40`. The largest macro families are `X1830_CLK` (41). Early IDs include `X1830_CLK_EXCLK`, `X1830_CLK_RTCLK`, `X1830_CLK_APLL`, `X1830_CLK_MPLL`, `X1830_CLK_EPLL`, `X1830_CLK_VPLL`; the trailing IDs include `X1830_CLK_PDMA`, `X1830_CLK_TCU`, `X1830_CLK_DTRNG`, `X1830_CLK_OST`, `X1830_CLK_EXCLK_DIV512`, `X1830_CLK_RTC`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_X1830_CGU_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ingenic,x1830-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,agilex5-clkmgr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,agilex5-clkmgr.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,agilex5-clkmgr.h` is a Linux device-tree clock binding header for the Intel clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 101-line, 3110-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `83` `#define` constants, with directly parsed numeric values spanning `0..82`. The largest macro families are `AGILEX5_I2C` (5), `AGILEX5_MAIN` (5), `AGILEX5_PERIPH` (5), `AGILEX5_S2F` (5), `AGILEX5_EMAC` (4), `AGILEX5_L4` (4). Early IDs include `AGILEX5_OSC1`, `AGILEX5_CB_INTOSC_HS_DIV2_CLK`, `AGILEX5_CB_INTOSC_LS_CLK`, `AGILEX5_F2S_FREE_CLK`, `AGILEX5_MAIN_PLL_CLK`, `AGILEX5_MAIN_PLL_C0_CLK`; the trailing IDs include `AGILEX5_SDMMC_SDPHY_REG_CLK`, `AGILEX5_SDMCLK`, `AGILEX5_SOFTPHY_REG_PCLK`, `AGILEX5_SOFTPHY_PHY_CLK`, `AGILEX5_SOFTPHY_CTRL_CLK`, `AGILEX5_NUM_CLKS`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate clocks`, `PLL clocks`, `fixed factor clocks`, `Gate clocks`, `__DT_BINDINGS_INTEL_AGILEX5_CLKMGR_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,agilex5-clkmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,lgm-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,lgm-clk.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,lgm-clk.h` is a Linux device-tree clock binding header for the Intel clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 166-line, 3837-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `122` `#define` constants, with directly parsed numeric values spanning `1..180`. The largest macro families are `LGM_GCLK` (62), `LGM_CLK` (60). Early IDs include `LGM_CLK_OSC`, `LGM_CLK_PLLPP`, `LGM_CLK_PLL2`, `LGM_CLK_PLL0CZ`, `LGM_CLK_PLL0B`, `LGM_CLK_PLL1`; the trailing IDs include `LGM_GCLK_PPV4`, `LGM_GCLK_GSWIPO`, `LGM_GCLK_CQEM`, `LGM_GCLK_XPCS5`, `LGM_GCLK_USB1`, `LGM_GCLK_USB2`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `PLL clocks`, `clocks from PLLs`, `ROPLL clocks`, `PLL2 clocks`, `PLL0CZ`, `PLL0B`, `PLL1`, `LJPLL3`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/intel,lgm-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/k210-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/k210-clk.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/k210-clk.h` is a Linux device-tree clock binding header for the Kendryte K210 clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 54-line, 1304-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `39` `#define` constants, with directly parsed numeric values spanning `0..38`. The largest macro families are `K210_CLK` (38), `K210_NUM` (1). Early IDs include `K210_CLK_CPU`, `K210_CLK_SRAM0`, `K210_CLK_SRAM1`, `K210_CLK_AI`, `K210_CLK_DMA`, `K210_CLK_FFT`; the trailing IDs include `K210_CLK_FPIOA`, `K210_CLK_SHA`, `K210_CLK_AES`, `K210_CLK_OTP`, `K210_CLK_RTC`, `K210_NUM_CLKS`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `CLOCK_K210_CLK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/k210-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lochnagar.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/lochnagar.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/lochnagar.h` is a Linux device-tree clock binding header for the Cirrus Logic Lochnagar clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 27-line, 715-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `11` `#define` constants, with directly parsed numeric values spanning `0..10`. The largest macro families are `LOCHNAGAR_CDC` (2), `LOCHNAGAR_GF` (2), `LOCHNAGAR_SPDIF` (2), `LOCHNAGAR_ADAT` (1), `LOCHNAGAR_DSP` (1), `LOCHNAGAR_PSIA1` (1). Early IDs include `LOCHNAGAR_CDC_MCLK1`, `LOCHNAGAR_CDC_MCLK2`, `LOCHNAGAR_DSP_CLKIN`, `LOCHNAGAR_GF_CLKOUT1`, `LOCHNAGAR_GF_CLKOUT2`, `LOCHNAGAR_PSIA1_MCLK`; the trailing IDs include `LOCHNAGAR_PSIA1_MCLK`, `LOCHNAGAR_PSIA2_MCLK`, `LOCHNAGAR_SPDIF_MCLK`, `LOCHNAGAR_ADAT_MCLK`, `LOCHNAGAR_SOUNDCARD_MCLK`, `LOCHNAGAR_SPDIF_CLKOUT`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `LOCHNAGAR_CDC`, `LOCHNAGAR_GF`, `LOCHNAGAR_SPDIF`, `LOCHNAGAR_ADAT`, `LOCHNAGAR_DSP`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lochnagar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls1x-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls1x-clk.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls1x-clk.h` is a Linux device-tree clock binding header for the Loongson clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 20-line, 460-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `6` `#define` constants, with directly parsed numeric values spanning `0..4`. The largest macro families are `LS1X_CLKID` (5), `CLK_NR` (1). Early IDs include `LS1X_CLKID_PLL`, `LS1X_CLKID_CPU`, `LS1X_CLKID_DC`, `LS1X_CLKID_AHB`, `LS1X_CLKID_APB`, `CLK_NR_CLKS`; the trailing IDs include `LS1X_CLKID_PLL`, `LS1X_CLKID_CPU`, `LS1X_CLKID_DC`, `LS1X_CLKID_AHB`, `LS1X_CLKID_APB`, `CLK_NR_CLKS`. Sentinel or count-style constants visible in this header are `CLK_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_CLOCK_LS1X_CLK_H__`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls1x-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls2k-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls2k-clk.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls2k-clk.h` is a Linux device-tree clock binding header for the Loongson clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 83-line, 2484-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `70` `#define` constants, with directly parsed numeric values spanning `0..34`. The largest macro families are `LS2K0300_CLK` (32), `LOONGSON2_DC` (3), `LOONGSON2_DDR` (3), `LOONGSON2_NODE` (3), `LOONGSON2_PIX0` (3), `LOONGSON2_PIX1` (3). Early IDs include `LOONGSON2_REF_100M`, `LOONGSON2_NODE_PLL`, `LOONGSON2_DDR_PLL`, `LOONGSON2_DC_PLL`, `LOONGSON2_PIX0_PLL`, `LOONGSON2_PIX1_PLL`; the trailing IDs include `LS2K0300_CLK_APB_GATE`, `LS2K0300_CLK_BOOT_SCALE`, `LS2K0300_CLK_BOOT_GATE`, `LS2K0300_CLK_SDIO_SCALE`, `LS2K0300_CLK_SDIO_GATE`, `LS2K0300_CLK_GMAC_IN`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `LS2K0300_CLK`, `LOONGSON2_DC`, `LOONGSON2_DDR`, `LOONGSON2_NODE`, `LOONGSON2_PIX0`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/loongson,ls2k-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-ccu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-ccu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-ccu.h` is a Linux device-tree clock binding header for the NXP LPC clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 75-line, 2134-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `60` `#define` constants, with directly parsed numeric values spanning `256..2816`. The largest macro families are `CLK_CPU` (33), `CLK_APB3` (6), `CLK_APB1` (5), `CLK_APB0` (3), `CLK_APB2` (3), `CLK_PERIPH` (3). Early IDs include `CLK_APB3_BUS`, `CLK_APB3_I2C1`, `CLK_APB3_DAC`, `CLK_APB3_ADC0`, `CLK_APB3_ADC1`, `CLK_APB3_CAN0`; the trailing IDs include `CLK_APB2_UART2`, `CLK_APB0_UART1`, `CLK_APB0_UART0`, `CLK_APB2_SSP1`, `CLK_APB0_SSP0`, `CLK_SDIO`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `Clock Control Unit 1 (CCU1) clock offsets`, `Clock Control Unit 2 (CCU2) clock offsets`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-ccu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-cgu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-cgu.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-cgu.h` is a Linux device-tree clock binding header for the NXP LPC clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 42-line, 1142-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `29` `#define` constants, with directly parsed numeric values spanning `0..27`. The largest macro families are `BASE_CGU` (2), `BASE_PHY` (2), `BASE_ADCHS` (1), `BASE_APB1` (1), `BASE_APB3` (1), `BASE_AUDIO` (1). Early IDs include `BASE_SAFE_CLK`, `BASE_USB0_CLK`, `BASE_PERIPH_CLK`, `BASE_USB1_CLK`, `BASE_CPU_CLK`, `BASE_SPIFI_CLK`; the trailing IDs include `BASE_RES3_CLK`, `BASE_RES4_CLK`, `BASE_AUDIO_CLK`, `BASE_CGU_OUT0_CLK`, `BASE_CGU_OUT1_CLK`, `BASE_CLK_MAX`. Sentinel or count-style constants visible in this header are `BASE_CLK_MAX`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `LPC18xx/43xx base clock ids`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc18xx-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc32xx-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc32xx-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc32xx-clock.h` is a Linux device-tree clock binding header for the NXP LPC clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 59-line, 1633-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `39` `#define` constants, with directly parsed numeric values spanning `1..36`. The largest macro families are `LPC32XX_CLK` (36), `LPC32XX_USB` (3). Early IDs include `LPC32XX_CLK_RTC`, `LPC32XX_CLK_DMA`, `LPC32XX_CLK_MLC`, `LPC32XX_CLK_SLC`, `LPC32XX_CLK_LCD`, `LPC32XX_CLK_MAC`; the trailing IDs include `LPC32XX_CLK_ADC`, `LPC32XX_CLK_HCLK_PLL`, `LPC32XX_CLK_PERIPH`, `LPC32XX_USB_CLK_I2C`, `LPC32XX_USB_CLK_DEVICE`, `LPC32XX_USB_CLK_HOST`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `LPC32XX System Control Block clocks`, `LPC32XX USB clocks`, `__DT_BINDINGS_LPC32XX_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lpc32xx-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lsi,axm5516-clks.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/lsi,axm5516-clks.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/lsi,axm5516-clks.h` is a Linux device-tree clock binding header for the LSI Axxia clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 34-line, 809-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `23` `#define` constants, with directly parsed numeric values spanning `0..22`. The largest macro families are `AXXIA_CLK` (23). Early IDs include `AXXIA_CLK_FAB_PLL`, `AXXIA_CLK_CPU_PLL`, `AXXIA_CLK_SYS_PLL`, `AXXIA_CLK_SM0_PLL`, `AXXIA_CLK_SM1_PLL`, `AXXIA_CLK_FAB_DIV`; the trailing IDs include `AXXIA_CLK_CPU0`, `AXXIA_CLK_CPU1`, `AXXIA_CLK_CPU2`, `AXXIA_CLK_CPU3`, `AXXIA_CLK_PER`, `AXXIA_CLK_MMC`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `AXXIA_CLK`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/lsi,axm5516-clks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2-audio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2-audio.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2-audio.h` is a Linux device-tree clock binding header for the Marvell clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 10-line, 262-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `3` `#define` constants, with directly parsed numeric values spanning `0..2`. The largest macro families are `MMP2_CLK` (3). Early IDs include `MMP2_CLK_AUDIO_SYSCLK`, `MMP2_CLK_AUDIO_SSPA0`, `MMP2_CLK_AUDIO_SSPA1`; the trailing IDs include `MMP2_CLK_AUDIO_SYSCLK`, `MMP2_CLK_AUDIO_SSPA0`, `MMP2_CLK_AUDIO_SSPA1`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `MMP2_CLK`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2.h` is a Linux device-tree clock binding header for the Marvell clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 95-line, 2622-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `83` `#define` constants, with directly parsed numeric values spanning `1..127`. The largest macro families are `MMP2_CLK` (73), `MMP3_CLK` (10). Early IDs include `MMP2_CLK_CLK32`, `MMP2_CLK_VCTCXO`, `MMP2_CLK_PLL1`, `MMP2_CLK_PLL1_2`, `MMP2_CLK_PLL1_4`, `MMP2_CLK_PLL1_8`; the trailing IDs include `MMP3_CLK_GPU_BUS`, `MMP2_CLK_GPU_3D`, `MMP3_CLK_GPU_3D`, `MMP3_CLK_GPU_2D`, `MMP3_CLK_SDH4`, `MMP2_CLK_AUDIO`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed clocks and plls`, `apb peripherals`, `axi peripherals`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,mmp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa168.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa168.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa168.h` is a Linux device-tree clock binding header for the Marvell clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 67-line, 1865-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `55` `#define` constants, with directly parsed numeric values spanning `1..112`. The largest macro families are `PXA168_CLK` (55). Early IDs include `PXA168_CLK_CLK32`, `PXA168_CLK_VCTCXO`, `PXA168_CLK_PLL1`, `PXA168_CLK_PLL1_2`, `PXA168_CLK_PLL1_4`, `PXA168_CLK_PLL1_8`; the trailing IDs include `PXA168_CLK_CCIC0`, `PXA168_CLK_CCIC0_PHY`, `PXA168_CLK_CCIC0_SPHY`, `PXA168_CLK_SDH3`, `PXA168_CLK_SDH01_AXI`, `PXA168_CLK_SDH23_AXI`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed clocks and plls`, `apb peripherals`, `axi peripherals`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa168.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1908.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1908.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1908.h` is a Linux device-tree clock binding header for the Marvell clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 89-line, 2575-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `75` `#define` constants, with directly parsed numeric values spanning `1..38`. The largest macro families are `PXA1908_CLK` (75). Early IDs include `PXA1908_CLK_CLK32`, `PXA1908_CLK_VCTCXO`, `PXA1908_CLK_PLL1_624`, `PXA1908_CLK_PLL1_416`, `PXA1908_CLK_PLL1_499`, `PXA1908_CLK_PLL1_832`; the trailing IDs include `PXA1908_CLK_VPU`, `PXA1908_CLK_GC`, `PXA1908_CLK_SDH2`, `PXA1908_CLK_GC2D`, `PXA1908_CLK_TRACE`, `PXA1908_CLK_DVC_DFC_DEBUG`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `plls`, `apb (apbc) peripherals`, `apb (apbcp) peripherals`, `axi (apmu) peripherals`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1908.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1928.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1928.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1928.h` is a Linux device-tree clock binding header for the Marvell clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 56-line, 1503-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `39` `#define` constants, with directly parsed numeric values spanning `0..95`. The largest macro families are `PXA1928_CLK` (39). Early IDs include `PXA1928_CLK_RTC`, `PXA1928_CLK_TWSI0`, `PXA1928_CLK_TWSI1`, `PXA1928_CLK_TWSI2`, `PXA1928_CLK_TWSI3`, `PXA1928_CLK_OWIRE`; the trailing IDs include `PXA1928_CLK_SDH2`, `PXA1928_CLK_SDH3`, `PXA1928_CLK_HSIC`, `PXA1928_CLK_SDH4`, `PXA1928_CLK_GC3D`, `PXA1928_CLK_GC2D`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `apb peripherals`, `axi peripherals`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa1928.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa910.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa910.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa910.h` is a Linux device-tree clock binding header for the Marvell clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 59-line, 1610-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `47` `#define` constants, with directly parsed numeric values spanning `1..109`. The largest macro families are `PXA910_CLK` (47). Early IDs include `PXA910_CLK_CLK32`, `PXA910_CLK_VCTCXO`, `PXA910_CLK_PLL1`, `PXA910_CLK_PLL1_2`, `PXA910_CLK_PLL1_4`, `PXA910_CLK_PLL1_8`; the trailing IDs include `PXA910_CLK_USB`, `PXA910_CLK_SPH`, `PXA910_CLK_DISP0`, `PXA910_CLK_CCIC0`, `PXA910_CLK_CCIC0_PHY`, `PXA910_CLK_CCIC0_SPHY`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed clocks and plls`, `apb peripherals`, `axi peripherals`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/marvell,pxa910.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77620.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77620.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77620.h` is a Linux device-tree clock binding header for the Maxim clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 19-line, 486-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `2` `#define` constants, with directly parsed numeric values spanning `0..0`. The largest macro families are `MAX77620_CLK` (1), `MAX77620_CLKS` (1). Early IDs include `MAX77620_CLK_32K_OUT0`, `MAX77620_CLKS_NUM`; the trailing IDs include `MAX77620_CLK_32K_OUT0`, `MAX77620_CLKS_NUM`. Sentinel or count-style constants visible in this header are `MAX77620_CLKS_NUM`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `Fixed rate clocks.`, `Total number of clocks.`, `_DT_BINDINGS_CLOCK_MAXIM_MAX77620_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77620.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77686.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77686.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77686.h` is a Linux device-tree clock binding header for the Maxim clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 21-line, 497-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `4` `#define` constants, with directly parsed numeric values spanning `0..2`. The largest macro families are `MAX77686_CLK` (3), `MAX77686_CLKS` (1). Early IDs include `MAX77686_CLK_AP`, `MAX77686_CLK_CP`, `MAX77686_CLK_PMIC`, `MAX77686_CLKS_NUM`; the trailing IDs include `MAX77686_CLK_AP`, `MAX77686_CLK_CP`, `MAX77686_CLK_PMIC`, `MAX77686_CLKS_NUM`. Sentinel or count-style constants visible in this header are `MAX77686_CLKS_NUM`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `Fixed rate clocks.`, `Total number of clocks.`, `_DT_BINDINGS_CLOCK_MAXIM_MAX77686_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77686.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77802.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77802.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77802.h` is a Linux device-tree clock binding header for the Maxim clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 20-line, 479-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `3` `#define` constants, with directly parsed numeric values spanning `0..1`. The largest macro families are `MAX77802_CLK` (2), `MAX77802_CLKS` (1). Early IDs include `MAX77802_CLK_32K_AP`, `MAX77802_CLK_32K_CP`, `MAX77802_CLKS_NUM`; the trailing IDs include `MAX77802_CLK_32K_AP`, `MAX77802_CLK_32K_CP`, `MAX77802_CLKS_NUM`. Sentinel or count-style constants visible in this header are `MAX77802_CLKS_NUM`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `Fixed rate clocks.`, `Total number of clocks.`, `_DT_BINDINGS_CLOCK_MAXIM_MAX77802_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max77802.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max9485.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max9485.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max9485.h` is a Linux device-tree clock binding header for the Maxim clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 15-line, 304-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `4` `#define` constants, with directly parsed numeric values spanning `0..3`. The largest macro families are `MAX9485_CLKOUT` (1), `MAX9485_CLKOUT1` (1), `MAX9485_CLKOUT2` (1), `MAX9485_MCLKOUT` (1). Early IDs include `MAX9485_MCLKOUT`, `MAX9485_CLKOUT`, `MAX9485_CLKOUT1`, `MAX9485_CLKOUT2`; the trailing IDs include `MAX9485_MCLKOUT`, `MAX9485_CLKOUT`, `MAX9485_CLKOUT1`, `MAX9485_CLKOUT2`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `__DT_BINDINGS_MAX9485_CLK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/maxim,max9485.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-apmixedsys.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-apmixedsys.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-apmixedsys.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 17-line, 433-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `9` `#define` constants, with directly parsed numeric values spanning `0..8`. The largest macro families are `CLK_APMIXED` (9). Early IDs include `CLK_APMIXED_ARMPLL`, `CLK_APMIXED_MAINPLL`, `CLK_APMIXED_UNIVPLL`, `CLK_APMIXED_MMPLL`, `CLK_APMIXED_MSDCPLL`, `CLK_APMIXED_VENCPLL`; the trailing IDs include `CLK_APMIXED_MMPLL`, `CLK_APMIXED_MSDCPLL`, `CLK_APMIXED_VENCPLL`, `CLK_APMIXED_TVDPLL`, `CLK_APMIXED_APLL1`, `CLK_APMIXED_APLL2`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `CLK_APMIXED`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-apmixedsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-imgsys.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-imgsys.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-imgsys.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 16-line, 409-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `8` `#define` constants, with directly parsed numeric values spanning `0..7`. The largest macro families are `CLK_IMG` (8). Early IDs include `CLK_IMG_SMI_LARB2`, `CLK_IMG_CAM_SMI`, `CLK_IMG_CAM_CAM`, `CLK_IMG_SEN_TG`, `CLK_IMG_SEN_CAM`, `CLK_IMG_CAM_SV`; the trailing IDs include `CLK_IMG_CAM_CAM`, `CLK_IMG_SEN_TG`, `CLK_IMG_SEN_CAM`, `CLK_IMG_CAM_SV`, `CLK_IMG_SUFOD`, `CLK_IMG_FD`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `_DT_BINDINGS_CLK_MT6735_IMGSYS_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-imgsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-infracfg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-infracfg.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-infracfg.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 26-line, 672-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `18` `#define` constants, with directly parsed numeric values spanning `0..17`. The largest macro families are `CLK_INFRA` (18). Early IDs include `CLK_INFRA_DBG`, `CLK_INFRA_GCE`, `CLK_INFRA_TRBG`, `CLK_INFRA_CPUM`, `CLK_INFRA_DEVAPC`, `CLK_INFRA_AUDIO`; the trailing IDs include `CLK_INFRA_APXGPT`, `CLK_INFRA_SEJ`, `CLK_INFRA_CCIF0_AP`, `CLK_INFRA_CCIF1_AP`, `CLK_INFRA_PMIC_SPI`, `CLK_INFRA_PMIC_WRAP`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `CLK_INFRA`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-infracfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-mfgcfg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-mfgcfg.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-mfgcfg.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 9-line, 218-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `1` `#define` constants, with directly parsed numeric values spanning `0..0`. The largest macro families are `CLK_MFG` (1). Early IDs include `CLK_MFG_BG3D`; the trailing IDs include `CLK_MFG_BG3D`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `_DT_BINDINGS_CLK_MT6735_MFGCFG_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-mfgcfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-pericfg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-pericfg.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-pericfg.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 38-line, 979-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `30` `#define` constants, with directly parsed numeric values spanning `0..29`. The largest macro families are `CLK_PERI` (30). Early IDs include `CLK_PERI_DISP_PWM`, `CLK_PERI_THERM`, `CLK_PERI_PWM1`, `CLK_PERI_PWM2`, `CLK_PERI_PWM3`, `CLK_PERI_PWM4`; the trailing IDs include `CLK_PERI_I2C1`, `CLK_PERI_I2C2`, `CLK_PERI_I2C3`, `CLK_PERI_AUXADC`, `CLK_PERI_SPI0`, `CLK_PERI_IRTX`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `CLK_PERI`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-pericfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-topckgen.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-topckgen.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-topckgen.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 80-line, 2303-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `70` `#define` constants, with directly parsed numeric values spanning `0..69`. The largest macro families are `CLK_TOP` (70). Early IDs include `CLK_TOP_AD_SYS_26M_CK`, `CLK_TOP_CLKPH_MCK_O`, `CLK_TOP_DMPLL`, `CLK_TOP_DPI_CK`, `CLK_TOP_WHPLL_AUDIO_CK`, `CLK_TOP_SYSPLL_D2`; the trailing IDs include `CLK_TOP_MFG13M_SEL`, `CLK_TOP_AUD1_SEL`, `CLK_TOP_AUD2_SEL`, `CLK_TOP_IRDA_SEL`, `CLK_TOP_IRTX_SEL`, `CLK_TOP_DISPPWM_SEL`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. The dominant macro families are `CLK_TOP`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-topckgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vdecsys.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vdecsys.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vdecsys.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 10-line, 252-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `2` `#define` constants, with directly parsed numeric values spanning `0..1`. The largest macro families are `CLK_VDEC` (2). Early IDs include `CLK_VDEC_VDEC`, `CLK_VDEC_SMI_LARB1`; the trailing IDs include `CLK_VDEC_VDEC`, `CLK_VDEC_SMI_LARB1`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `_DT_BINDINGS_CLK_MT6735_VDECSYS_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vdecsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vencsys.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vencsys.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vencsys.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 12-line, 309-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `4` `#define` constants, with directly parsed numeric values spanning `0..3`. The largest macro families are `CLK_VENC` (4). Early IDs include `CLK_VENC_SMI_LARB3`, `CLK_VENC_VENC`, `CLK_VENC_JPGENC`, `CLK_VENC_JPGDEC`; the trailing IDs include `CLK_VENC_SMI_LARB3`, `CLK_VENC_VENC`, `CLK_VENC_JPGENC`, `CLK_VENC_JPGDEC`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `_DT_BINDINGS_CLK_MT6735_VENCSYS_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6735-vencsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6795-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6795-clk.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6795-clk.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 276-line, 7872-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `249` `#define` constants, with directly parsed numeric values spanning `0..127`. The largest macro families are `CLK_TOP` (128), `CLK_MM` (43), `CLK_PERI` (35), `CLK_INFRA` (17), `CLK_APMIXED` (13), `CLK_MFG` (5). Early IDs include `CLK_TOP_ADSYS_26M`, `CLK_TOP_CLKPH_MCK_O`, `CLK_TOP_USB_SYSPLL_125M`, `CLK_TOP_DSI0_DIG`, `CLK_TOP_DSI1_DIG`, `CLK_TOP_ARMCA53PLL_754M`; the trailing IDs include `CLK_VDEC_NR_CLK`, `CLK_VENC_LARB`, `CLK_VENC_VENC`, `CLK_VENC_JPGENC`, `CLK_VENC_JPGDEC`, `CLK_VENC_NR_CLK`. Sentinel or count-style constants visible in this header are `CLK_TOP_NR_CLK`, `CLK_APMIXED_NR_CLK`, `CLK_INFRA_NR_CLK`, `CLK_PERI_NR_CLK`, `CLK_MFG_NR_CLK`, `CLK_MM_NR_CLK`, `CLK_VDEC_NR_CLK`, `CLK_VENC_NR_CLK`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `TOPCKGEN`, `APMIXED_SYS`, `INFRA_SYS`, `PERI_SYS`, `MFG`, `MM_SYS`, `VDEC_SYS`, `VENC_SYS`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt6795-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7981-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7981-clk.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7981-clk.h` is a Linux device-tree clock binding header for the MediaTek clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 216-line, 6329-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `191` `#define` constants, with directly parsed numeric values spanning `0..109`. The largest macro families are `CLK_TOP` (110), `CLK_INFRA` (61), `CLK_APMIXED` (8), `CLK_ETH` (4), `CLK_SGM0` (4), `CLK_SGM1` (4). Early IDs include `CLK_TOP_CB_CKSQ_40M`, `CLK_TOP_CB_M_416M`, `CLK_TOP_CB_M_D2`, `CLK_TOP_CB_M_D3`, `CLK_TOP_M_D3_D2`, `CLK_TOP_CB_M_D4`; the trailing IDs include `CLK_SGM1_CK1_EN`, `CLK_SGM1_CDR_CK1_EN`, `CLK_ETH_FE_EN`, `CLK_ETH_GP2_EN`, `CLK_ETH_GP1_EN`, `CLK_ETH_WOCPU0_EN`. Sentinel or count-style constants visible in this header are none. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `TOPCKGEN`, `INFRACFG`, `APMIXEDSYS`, `SGMIISYS_0`, `SGMIISYS_1`, `ETHSYS`, `_DT_BINDINGS_CLK_MT7981_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7981-clk.h -->

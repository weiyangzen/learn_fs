# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-clock.h

### Purpose
`imx94-clock.h` defines the i.MX94 clock ID namespace used by device-tree clock specifiers. It maps human-readable `IMX94_CLK_*` names to integer IDs that are passed as the single argument to clock providers such as the SCMI clock protocol in `imx94.dtsi`.

### Important APIs, Types, And Functions
There are no functions or data structures. The public API is 183 integer macros, numbered from `IMX94_CLK_EXT` at 0 through `IMX94_CLK_NPU_CGC` at 182. The list covers fixed/external roots, PLL VCOs and PFD outputs, reserved ABI slots 18-23, bus roots, CPU/M33/M70/M71 clocks, DRAM/display/HSIO roots, network and EtherCAT clocks, LPI2C/LPSPI/LPUART instances, SAI, TPM, USB PHY, USDHC, XSPI, clock-output selectors, and NPU gating.

### Control Flow
This header has no runtime flow. During DTS preprocessing, clock specifiers such as `<&scmi_clk IMX94_CLK_LPUART5>` become numeric IDs in the DTB. At runtime, consumer drivers call the common clock framework with those IDs; the provider, represented in `imx94.dtsi` as SCMI protocol 0x14 with `#clock-cells = <1>`, resolves the ID to firmware-managed clock operations.

### State, Persistence, And Dependencies
The file has no state. Its integer assignments are persistent ABI values between device trees, firmware clock providers, and kernel drivers. The include guard is `__IMX94_CLOCK_H`, and the license is GPL-2.0-only or MIT. `imx94.dtsi` includes this file and uses many IDs for clocks and assigned-clock parents on buses, UARTs, LPI2C/LPSPI, CAN, SAI, USDHC, HSIO, and other SoC nodes.

### Integration Points
The main integration point is `imx94.dtsi`, where `scmi_clk: protocol@14` exposes a one-cell clock provider. Peripheral nodes use `clocks = <&scmi_clk IMX94_CLK_...>` and sometimes `assigned-clocks` and `assigned-clock-parents`, for example CAN nodes selecting `IMX94_CLK_SYSPLL1_PFD1_DIV2` and USDHC nodes selecting `IMX94_CLK_SYSPLL1_PFD1`. The IDs also need to stay consistent with any firmware SCMI clock table and any out-of-tree DTS files that include the same binding.

### Risks
Clock IDs are ABI-sensitive: renumbering, reusing reserved IDs, or inserting a new macro in the middle can make old DTBs request the wrong firmware clock. Reserved entries 18-23 should remain stable unless the firmware/kernel contract explicitly changes. Similar SoCs may have nearby naming but not identical ID maps; replacing this header with another i.MX9 clock binding would compile yet break runtime clock acquisition. Names that distinguish ungated PLL outputs, gated PFD outputs, and divided PFD outputs must remain precise because consumers may depend on rate and gate behavior.

### Test Signals
Useful validation includes building `imx94.dtb`, running `dtbs_check`, booting with clock-provider debug enabled, and checking that every enabled node in `imx94.dtsi` can acquire its clocks. Runtime signals include UART console availability, CAN assigned parent/rate programming, USDHC bus rates, HSIO/USB clocks, network clocks, and absence of SCMI "clock not found" errors. ABI tests should compare generated numeric IDs against firmware documentation or an SCMI clock dump.

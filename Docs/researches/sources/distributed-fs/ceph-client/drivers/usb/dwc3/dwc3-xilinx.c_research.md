# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-xilinx.c

Purpose: Xilinx ZynqMP and Versal DWC3 glue driver. It manages clocks, platform-specific resets, optional USB3 PHY, ULPI reset masking, coherent DMA traffic routing, software-node property injection for coherent children, OF child creation, and PM clock/PHY handling.

Important APIs, types, and functions: `struct dwc3_xlnx` stores bulk clocks, device, wrapper MMIO, platform init callback, and optional USB3 PHY. `dwc3_xlnx_mask_phy_rst()` controls whether the USB controller may reset ULPI PHY. `dwc3_xlnx_set_coherency()` routes DMA through FPD when coherent or IOMMU-mapped. `dwc3_xlnx_init_versal()` and `_init_zynqmp()` implement SoC-specific reset/PHY flows. `dwc3_set_swnode()` injects `snps,gsbuscfg0-reqinfo` when the child DWC3 node is coherent.

Control flow: probe maps registers, selects init callback from OF match data, enables all clocks, runs Versal or ZynqMP init, optionally creates a managed software node, populates child devices, sets runtime PM active, enables devm runtime PM, and runtime-resumes the wrapper. ZynqMP init optionally initializes/powers USB3 PHY, deasserts APB/core/hibernation resets, selects or deselects PIPE clock, handles optional reset GPIO, and sets coherency. Versal masks/unmasks PHY reset around reset assertion/deassertion and configures USB2 traffic route coherency.

State and persistence: platform init writes wrapper reset, PIPE clock, power-present, traffic-route, and PHY reset mask registers. System suspend exits the USB3 PHY and disables clocks; resume enables clocks and reinitializes/powers the PHY. Runtime suspend/resume gates clocks only.

Dependencies and integration: uses OF match data, bulk clocks, reset controls, optional GPIO reset, generic PHY, PM runtime, OF child population, DMA coherency/IOMMU helpers, and managed software nodes. It integrates with child DWC3 by child node population and property injection.

Risks: ZynqMP reset behavior changes depending on whether `usb3-phy` exists; missing DT PHY can avoid resets even when USB3 is actually used. `dwc3_set_swnode()` attaches the software node to the wrapper device, so property inheritance expectations must match DWC3 core behavior. PM paths do not rerun full platform init, only clocks/PHY, so register retention matters. Coherency routing must match DMA/IOMMU configuration.

Test signals: test both compatibles, USB3 PHY present and absent, reset GPIO sequencing, coherent/IOMMU traffic route bits, software-node property creation for coherent child nodes, runtime clock gating, system suspend/resume with PHY reinit, and probe failure unwind after child population.

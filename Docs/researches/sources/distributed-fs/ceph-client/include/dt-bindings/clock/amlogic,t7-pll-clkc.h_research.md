# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-pll-clkc.h

Purpose: defines Amlogic T7 PLL clock IDs for several separate PLL providers or domains.

Important APIs/types/functions: the header groups IDs for GP0, GP1, HIFI, PCIE, MPLL, HDMI, and MCLK PLL families. Each group starts numbering at zero, defining domain-local IDs such as DCO/output pairs, PCIe OD/div2/output, MPLL prediv and MPLL0-3 outputs, HDMI DCO/OD/output, and MCLK selectors/dividers/outputs.

Control flow: compatible-specific PLL provider instances use the IDs for their own domain; DTS must include the appropriate provider node so overlapping numeric IDs are interpreted in the correct clock controller namespace.

State and persistence: constants are DT ABI within each provider namespace, not a single global table.

Dependencies and integration: standalone T7 PLL binding for Amlogic clock drivers.

Risks and test signals: overlapping IDs across groups are intentional but risky if a consumer references the wrong provider. Test each PLL provider instance, PCIe/HDMI/audio rate outputs, and DTS provider phandle correctness.

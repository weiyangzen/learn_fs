<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qmp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qmp.h

Purpose: Qualcomm QMP PHY binding constants for USB4/USB3/DisplayPort clocks and PHY lanes plus PCIe clock indexes.

Important APIs/types/functions: This header exports 7 DT-visible macros in the `phy` binding namespace. Main API surface: `QMP_USB43DP_*` constants distinguish USB3 pipe, DP link/VCO clocks, USB3 PHY, and DP PHY; `QMP_PCIE_*` indexes expose PCIe pipe/aux clocks. First exported macros: `QMP_USB43DP_USB3_PIPE_CLK`, `QMP_USB43DP_DP_LINK_CLK`, `QMP_USB43DP_DP_VCO_DIV_CLK`, `QMP_USB43DP_USB3_PHY`, `QMP_USB43DP_DP_PHY`, `QMP_PCIE_PIPE_CLK`, `QMP_PCIE_PHY_AUX_CLK`. Last exported macros: `QMP_USB43DP_DP_LINK_CLK`, `QMP_USB43DP_DP_VCO_DIV_CLK`, `QMP_USB43DP_USB3_PHY`, `QMP_USB43DP_DP_PHY`, `QMP_PCIE_PIPE_CLK`, `QMP_PCIE_PHY_AUX_CLK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: QMP PHY providers and DT consumers use these IDs in multi-output clock/PHY specifiers. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qmp.h -->

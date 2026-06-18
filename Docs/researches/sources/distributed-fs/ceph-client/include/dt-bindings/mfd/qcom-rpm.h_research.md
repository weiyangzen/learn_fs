<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/qcom-rpm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/qcom-rpm.h

Purpose: Qualcomm RPM resource binding constants plus regulator force-mode constants.

Important APIs/types/functions: This header exports 166 DT-visible macros in the `mfd` binding namespace. Main API surface: `QCOM_RPM_*` IDs map fabric, clock, DDR, switch, and PMIC regulator resources to RPM message resources; `QCOM_RPM_FORCE_MODE_*` selects regulator force behavior. First exported macros: `QCOM_RPM_APPS_FABRIC_ARB`, `QCOM_RPM_APPS_FABRIC_CLK`, `QCOM_RPM_APPS_FABRIC_HALT`, `QCOM_RPM_APPS_FABRIC_IOCTL`, `QCOM_RPM_APPS_FABRIC_MODE`, `QCOM_RPM_APPS_L2_CACHE_CTL`, `QCOM_RPM_CFPB_CLK`, `QCOM_RPM_CXO_BUFFERS`. Last exported macros: `QCOM_RPM_VOLTAGE_CORNER`, `QCOM_RPM_FORCE_MODE_NONE`, `QCOM_RPM_FORCE_MODE_LPM`, `QCOM_RPM_FORCE_MODE_HPM`, `QCOM_RPM_FORCE_MODE_AUTO`, `QCOM_RPM_FORCE_MODE_BYPASS`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: RPM regulator, clock, interconnect, and power-management drivers interpret DT resource specifiers through these stable numeric IDs. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/qcom-rpm.h -->

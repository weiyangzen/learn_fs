<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/aspeed-scu-ic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/aspeed-scu-ic.h

## Purpose
This binding header names interrupt sources for Aspeed SCU interrupt controllers across AST2500, AST2600, and AST2700 generations.

## Important APIs, types, and functions
It exports numeric source IDs for VGA cursor/scratch changes and SoC-specific PCIe PERST/RCRST, LPC reset, and MSI events, such as `ASPEED_AST2500_SCU_IC_PCIE_RESET_LO_TO_HI`, `ASPEED_AST2600_SCU_IC0_PCIE_PERST_*`, and `ASPEED_AST2700_SCU_IC[0-3]_*`.

## Control flow
Board DTS files use these macros in interrupt specifiers for SCU interrupt-controller child events. The driver maps the source ID to a status bit or event line for the selected Aspeed generation.

## State and persistence
The file has no state. Values embedded in DTBs are hardware binding IDs.

## Dependencies and integration points
It integrates with Aspeed SCU syscon/interrupt-controller drivers and platform devices interested in VGA, PCIe reset, LPC reset, or MSI state changes.

## Risks and test signals
Risks include generation-specific ID reuse, inverted rising/falling reset semantics, and using an AST2700 IC bank macro with the wrong SCU interrupt-controller instance. Test signals include DTS validation, reset-edge interrupt tests, and driver logs for each SCU IC bank.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/aspeed-scu-ic.h -->

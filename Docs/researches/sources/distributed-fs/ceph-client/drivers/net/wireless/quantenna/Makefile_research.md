<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Makefile

## Purpose
This Makefile descends into the Quantenna qtnfmac driver directory when the common qtnfmac symbol is enabled.

## Important APIs, Types, And Functions
The build rule is `obj-$(CONFIG_QTNFMAC) += qtnfmac/`.

## Control Flow
Kbuild includes `drivers/net/wireless/quantenna/qtnfmac/` in the build graph when `CONFIG_QTNFMAC` is built-in or modular.

## State And Persistence
No runtime state exists. The persistent effect is build graph membership for qtnfmac.

## Dependencies And Integration Points
Consumes `CONFIG_QTNFMAC` selected by transport-specific options such as `QTNFMAC_PCIE`.

## Risks
If `QTNFMAC_PCIE` selects `QTNFMAC` but this rule is wrong, neither the common nor PCIe modules build. Additional Quantenna drivers would need explicit rules.

## Test Signals
Build with `CONFIG_QTNFMAC_PCIE=m` and confirm both common and PCIe qtnfmac modules are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Makefile -->

# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/Makefile

### Purpose
`qualcomm/emac/Makefile` defines the Qualcomm EMAC driver object composition.

### Important APIs, Types, And Functions
When `CONFIG_QCOM_EMAC` is enabled, it builds `qcom-emac.o` from `emac.o`, `emac-mac.o`, `emac-phy.o`, `emac-sgmii.o`, `emac-ethtool.o`, and three SGMII variant files: `emac-sgmii-fsm9900.o`, `emac-sgmii-qdf2432.o`, and `emac-sgmii-qdf2400.o`.

### Control Flow
Kbuild links the listed component objects into the single driver object. If `QCOM_EMAC=m`, the same composition becomes the module payload; if built-in, it is linked into the kernel image.

### State, Persistence, And Dependencies
There is no runtime state. The file depends on `CONFIG_QCOM_EMAC` from the parent Kconfig and on every listed `.c` file providing compatible symbols.

### Integration Points
This Makefile ties the platform probe/core file to MAC, PHY, SGMII, and ethtool support so the driver is built as one coherent unit.

### Risks
Missing a support object can create link-time failures or silently remove callbacks if symbols are weak elsewhere. Adding SoC-specific SGMII files requires updating this list.

### Test Signals
Compile `CONFIG_QCOM_EMAC=y` and `m`, verify `qcom-emac` contains MAC/PHY/SGMII/ethtool symbols, and run allmodconfig/allyesconfig build coverage.

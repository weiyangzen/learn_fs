## sources/distributed-fs/ceph-client/arch/mips/ralink/Kconfig

### Purpose
This Kconfig fragment selects Ralink/MediaTek MIPS SoC variants, interrupt-controller options, debug illegal-access support, and built-in DTB choices.

### Important APIs, Types, And Functions
It defines `RALINK_ILL_ACC`, `IRQ_INTC`, SoC choices for RT288x, RT305x, RT3883, MT7620/8, and MT7621, and DTB choices for non-MT7621 systems. SoC selections enable PCI, GIC, SMP/CPS, highmem, pinctrl, SOC_BUS, and cache options as appropriate.

### Control Flow
Configuration controls which platform objects build and which architecture facilities are enabled. MT7621 selects generic PCI drivers and MIPS GIC rather than the legacy Ralink INTC path.

### State, Persistence, And Dependencies
No runtime state exists. Build-time dependencies determine IRQ model, PCI framework, SMP support, and DTB linkage.

### Integration Points
The Ralink Makefile consumes these symbols to include SoC, timer, IRQ, PCI, and debugfs components.

### Risks
Incorrect SoC choice can select incompatible IRQ and PCI paths. DTB choices are disabled for MT7621, requiring an external DT flow.

### Test Signals
Build each SoC choice, confirm expected object inclusion, and boot with matching DTB to verify selected IRQ and PCI model.

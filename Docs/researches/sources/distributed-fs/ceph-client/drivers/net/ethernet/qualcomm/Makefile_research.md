# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Makefile

### Purpose
`qualcomm/Makefile` maps Qualcomm Ethernet Kconfig symbols to kernel objects and subdirectories.

### Important APIs, Types, And Functions
It builds `qca_7k_common.o` for `CONFIG_QCA7000`, composes `qcaspi` from `qca_7k.o`, `qca_debug.o`, and `qca_spi.o`, composes `qcauart` from `qca_uart.o`, always descends into `emac/`, and conditionally descends into `ppe/` and `rmnet/`.

### Control Flow
The build system evaluates `obj-$(CONFIG_...)` lines to include objects or modules. `obj-y += emac/` means the subdirectory is always visited, while its own Makefile controls whether `qcom-emac.o` is built.

### State, Persistence, And Dependencies
There is no runtime state. Build state is the selected object list derived from Kconfig. The file depends on matching symbol definitions in `Kconfig` and object names in the Qualcomm source tree.

### Integration Points
This is the parent build glue between `drivers/net/ethernet/` and Qualcomm driver families. It delegates EMAC object composition to `emac/Makefile`.

### Risks
Unconditional descent into `emac/` is safe only because the child Makefile is symbol-gated. Object-list drift from renamed source files causes build failures. Module names are determined by target object names, so changes affect userspace module loading.

### Test Signals
Build with QCA7000 SPI, QCA7000 UART, QCOM_EMAC, QCOM_PPE, and RMNET as built-in/module/off combinations and verify expected modules and no orphan object references.

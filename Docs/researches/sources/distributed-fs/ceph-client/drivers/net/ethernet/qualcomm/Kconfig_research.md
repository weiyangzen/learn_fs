# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Kconfig

### Purpose
`qualcomm/Kconfig` declares the Qualcomm Ethernet driver menu and build-time configuration symbols for QCA7000, Qualcomm EMAC, Qualcomm PPE, and rmnet.

### Important APIs, Types, And Functions
The key symbols are `NET_VENDOR_QUALCOMM`, `QCA7000`, `QCA7000_SPI`, `QCA7000_UART`, `QCOM_EMAC`, and `QCOM_PPE`. It also sources `drivers/net/ethernet/qualcomm/rmnet/Kconfig`.

### Control Flow
Kconfig visibility is gated by `NET_VENDOR_QUALCOMM`. SPI and UART QCA7000 protocol drivers select the common `QCA7000` support symbol and depend on their bus frameworks plus OF. `QCOM_EMAC` depends on DMA and MMIO support and selects `CRC32` and `PHYLIB`. `QCOM_PPE` depends on clocks, MMIO, OF, and either Qualcomm architecture or compile-test.

### State, Persistence, And Dependencies
There is no runtime state. The file persists build selections into kernel configuration and controls which objects the Makefiles can compile. Dependencies express required kernel subsystems for bus access, PHY handling, CRC support, regmap MMIO, and platform availability.

### Integration Points
The symbols are consumed by the Qualcomm Ethernet Makefiles. `QCOM_EMAC` builds the EMAC driver under `emac/`; `QCOM_PPE` builds `ppe/`; QCA7000 symbols build SPI/UART modules.

### Risks
Incorrect dependencies can expose drivers on unsupported builds or hide compile-test coverage. `NET_VENDOR_QUALCOMM` only controls menu visibility, so per-driver dependencies remain the real guardrails.

### Test Signals
Run Kconfig/compile coverage for built-in and module combinations, `COMPILE_TEST`, missing PHYLIB/SPI/SERIAL_DEV_BUS dependencies, and menu visibility when `NET_VENDOR_QUALCOMM=n`.

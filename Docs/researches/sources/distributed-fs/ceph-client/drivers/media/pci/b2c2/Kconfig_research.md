# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/Kconfig

Purpose: Kconfig options for Technisat/B2C2 FlexCop PCI DVB/ATSC cards.

Important APIs/types/functions: `DVB_B2C2_FLEXCOP_PCI` is a tristate depending on `DVB_CORE && I2C`. `DVB_B2C2_FLEXCOP_PCI_DEBUG` depends on the PCI driver and selects shared `DVB_B2C2_FLEXCOP_DEBUG`.

Control flow: enabling the main symbol builds PCI transport support for Air/Sky/CableStar2 cards. Enabling debug exposes the shared FlexCop debug module option across the FlexCop drivers.

State/persistence: kernel configuration only.

Dependencies/integration: integrates PCI transport with DVB core, I2C, and common FlexCop support under `drivers/media/common/b2c2`.

Risks/test signals: debug selection affects common code as well as PCI. Kconfig/build tests should cover driver disabled, module, built-in, and debug enabled combinations, including I2C/DVB dependency absence.

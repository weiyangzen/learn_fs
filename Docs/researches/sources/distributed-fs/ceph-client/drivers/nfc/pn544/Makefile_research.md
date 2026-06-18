# sources/distributed-fs/ceph-client/drivers/nfc/pn544/Makefile

Purpose: Defines Kbuild object composition for PN544 HCI core and transport modules.

Important definitions: `pn544_i2c-objs = i2c.o`, `pn544_mei-objs = mei.o`, `obj-$(CONFIG_NFC_PN544) += pn544.o`, and transport object selections follow `CONFIG_NFC_PN544_I2C` and `CONFIG_NFC_PN544_MEI`.

Control flow: No runtime flow; Kbuild controls object linking.

State and persistence: Build outputs only.

Dependencies and integration points: Must remain aligned with `Kconfig` and exports from `pn544.c`, especially `pn544_hci_probe()` and `pn544_hci_remove()` used by I2C and MEI modules.

Risks: Symbol/object naming drift breaks module linking. Test signals include allmodconfig builds and separate module link checks for I2C and MEI transports.

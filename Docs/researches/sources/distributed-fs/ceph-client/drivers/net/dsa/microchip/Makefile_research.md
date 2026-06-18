# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Makefile

Purpose: composes the Microchip KSZ common module and bus transport modules.

Important APIs/types/functions: `ksz_switch.o` includes common, DCB, KSZ9477, ACL, flower, KSZ8, and LAN937x objects. `ksz_ptp.o` is added conditionally. I2C, SPI, and SMI transports build separate modules.

Control flow: no runtime flow; Kbuild links objects based on configuration.

State and persistence: no runtime state; affects build graph only.

Dependencies and integration: `ksz8.o` is part of the common `ksz_switch` module, while `ksz8863_smi.o` registers devices over SMI/MDIO.

Risks and test signals: missing objects or conditional PTP link errors. Test common-only, SMI, I2C, SPI, and PTP configurations.

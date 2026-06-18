# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/Kconfig

Purpose: defines configuration entries for Silicon Integrated Systems Ethernet drivers.

Important symbols: `NET_VENDOR_SIS` gates the vendor menu and depends on PCI. `SIS900` builds SiS 900/7016 Fast Ethernet support, depends on `PCI && HAS_IOPORT`, and selects CRC32 and MII. `SIS190` builds SiS190/SiS191 gigabit support with the same dependency and helper selections.

Integration and state: controls the SiS Makefile entries for `sis900.o` and `sis190.o`. It has no runtime state.

Risks and tests: drivers require I/O port support, so dependency coverage matters on architectures without PIO. Build-test `SIS900` and `SIS190` as built-in and module where PCI/HAS_IOPORT are available.

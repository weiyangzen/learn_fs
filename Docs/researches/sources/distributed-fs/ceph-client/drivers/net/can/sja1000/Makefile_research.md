# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Makefile

Purpose: this Makefile maps each SJA1000 Kconfig option to its corresponding adapter object and builds the shared SJA1000 core object when `CONFIG_CAN_SJA1000` is enabled.

Important build units: researched entries include `ems_pci.o`, `ems_pcmcia.o`, `f81601.o`, `kvaser_pci.o`, `peak_pci.o`, `peak_pcmcia.o`, and `plx_pci.o`. The file also lists `sja1000.o`, `sja1000_isa.o`, `sja1000_platform.o`, and `tscan1.o`.

Control flow and integration: no runtime flow exists here. The build graph ensures board adapters link independently while sharing the exported SJA1000 core implementation.

State and persistence: only kernel build state is affected. Runtime netdev state is created by adapter probe functions in the corresponding `.c` files.

Risks and test signals: a stale object mapping would break module availability even if Kconfig permits selection. Tests should compile each adapter as built-in and module where the dependency bus is enabled and verify the module names match Kconfig help text.

# sources/distributed-fs/ceph-client/drivers/net/arcnet/Makefile

Purpose: builds the ARCNET core, packet encapsulation plug-ins, and hardware drivers according to Kconfig symbols.

Important entries: `obj-$(CONFIG_ARCNET) += arcnet.o` builds the shared core. Protocol modules include `rfc1201.o`, `rfc1051.o`, `arc-rawmode.o`, and `capmode.o`. Hardware modules include `com90xx.o`, `com90io.o`, `arc-rimi.o`, `com20020.o`, `com20020-isa.o`, `com20020-pci.o`, and `com20020_cs.o`.

Control flow and integration: no runtime flow exists in the Makefile. It controls module boundaries. Packet modules register `struct ArcProto` handlers against exported maps in `arcnet.o`; bus/chipset drivers call exported allocation/open/interrupt helpers from the core and, for COM20020 ISA/PCI, shared functions in `com20020.o`.

State and persistence: build artifacts and module dependency metadata are the only state. Risks include selecting a bus front-end without the shared COM20020 core, or changing object names without Kconfig help/module alias updates. Test signals are `make M=drivers/net/arcnet`, module load/unload ordering for core plus plug-ins, and randconfig coverage for every object line.

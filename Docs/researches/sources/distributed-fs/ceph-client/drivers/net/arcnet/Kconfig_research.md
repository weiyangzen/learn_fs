# sources/distributed-fs/ceph-client/drivers/net/arcnet/Kconfig

Purpose: defines the ARCNET driver family configuration. The top-level `ARCNET` menuconfig depends on `NETDEVICES`, a supported bus (`ISA || PCI || PCMCIA`), and `HAS_IOPORT`, then exposes packet formats and chipset/bus drivers.

Important symbols: `ARCNET_1201`, `ARCNET_1051`, `ARCNET_RAW`, and `ARCNET_CAP` select packet encapsulation modules. `ARCNET_COM90xx`, `ARCNET_COM90xxIO`, `ARCNET_RIM_I`, and `ARCNET_COM20020` select hardware families. `ARCNET_COM20020` depends on `LEDS_CLASS`; `ARCNET_COM20020_ISA`, `_PCI`, and `_CS` depend on the COM20020 core and their buses.

Control flow and integration: no runtime flow exists here. It gates the sibling Makefile and determines whether the core `arcnet.o`, protocol plug-ins, and chipset drivers are available. Help text warns that the core alone is not enough; a matching chipset driver and usually a packet format module are needed.

State and persistence: selections persist in `.config`. Risks are incomplete user configurations, especially enabling ARCNET core without a usable chipset driver or protocol format. The `LEDS_CLASS` dependency for COM20020 matters because COM20020 PCI integrates LED triggers. Test signals include Kconfig dependency checks across ISA/PCI/PCMCIA, allmodconfig builds, and module dependency generation for protocol plug-ins that use exported core symbols.

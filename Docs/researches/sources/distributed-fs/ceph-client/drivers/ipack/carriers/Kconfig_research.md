# sources/distributed-fs/ceph-client/drivers/ipack/carriers/Kconfig

Purpose: Adds the TEWS TPCI-200 IndustryPack PCI carrier board configuration option.

Important APIs/types/functions: `config BOARD_TPCI200`, `tristate`, dependencies `IPACK_BUS` and `PCI`, and default `n`.

Control flow: The option is visible only when the IPACK bus and PCI support are available. Selecting it compiles the TPCI200 carrier driver through the carrier Makefile.

State and persistence: No runtime state. The selected symbol controls whether `tpci200.o` is built.

Dependencies/integration: Bridges PCI carrier support to the IPACK bus core and the child device enumeration path used by IPACK modules.

Risks and test signals: Validate menu visibility with `PCI=n`, modular builds with `IPACK_BUS=m`, and dependency closure so `tpci200.o` cannot build without bus core APIs.

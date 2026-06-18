# sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Kconfig

Purpose: declares the `DVB_DM1105` kernel configuration option for SDMC DM1105 PCI DVB cards such as DvbWorld 2002.

Important APIs/types/functions: option is tristate and depends on `DVB_CORE`, `PCI`, `I2C`, `I2C_ALGOBIT`, `HAS_IOPORT`, and `RC_CORE`. With media subdriver autoselect it selects frontend/tuner helpers including `DVB_PLL`, `DVB_STV0299`, `DVB_STV0288`, `DVB_STB6000`, `DVB_CX24116`, `DVB_SI21XX`, `DVB_DS3000`, and `DVB_TS2020`.

Control flow: Kconfig controls whether `dm1105.o` can be built and whether dependent demod/tuner modules are selected automatically.

State and persistence: no runtime state.

Dependencies/integration: matches `dm1105.c` dependencies: PCI, I/O port access, I2C including bit-banged GPIO, DVB core, and RC core.

Risks and test signals: missing selects cause frontend attach failures at runtime; overbroad dependencies can expose uncompilable combinations. Test with `allyesconfig`, `allmodconfig`, and `COMPILE_TEST`-like build matrix for the media PCI subtree.

# sources/distributed-fs/ceph-client/drivers/net/pse-pd/Makefile

Purpose: maps PSE Kconfig symbols to the objects built in `drivers/net/pse-pd`.

Important build rules: `CONFIG_PSE_CONTROLLER` builds `pse_core.o`; `CONFIG_PSE_REGULATOR` builds `pse_regulator.o`; `CONFIG_PSE_PD692X0`, `CONFIG_PSE_SI3474`, and `CONFIG_PSE_TPS23881` build their corresponding I2C controller drivers.

Control flow: Kbuild includes the framework object whenever the core symbol is enabled, then adds provider objects according to individual driver symbols. Since `pse_core.o` exports symbols consumed by providers and PHY/ethtool code, the Kconfig dependency around `PSE_CONTROLLER` is the main guard against unresolved references.

State and persistence: no runtime state is defined. The file controls object inclusion and module composition only.

Dependencies and integration: integrates with the parent networking driver build and the Kconfig file in the same directory. The output objects implement the framework, a regulator-only provider, and three I2C chip providers.

Risks and test signals: risks are stale object names after source renames or Kconfig mismatches that omit the core while provider code expects exported PSE helpers. Test signals include built-in and module builds for each symbol combination, clean `modpost` symbol resolution, and confirming module names match Kconfig help text.

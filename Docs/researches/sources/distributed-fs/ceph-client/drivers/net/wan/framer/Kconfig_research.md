# sources/distributed-fs/ceph-client/drivers/net/wan/framer/Kconfig

Purpose: Kconfig menu for the WAN framer subsystem. It introduces `FRAMER` as the user-visible subsystem switch, `GENERIC_FRAMER` as the internal core selector, and `FRAMER_PEF2256` as the Lantiq PEF2256/FALC56 framer driver option.

Important APIs, types, and functions: no code APIs are declared, but the config symbols gate compilation of `framer-core.o` and the PEF2256 module. `FRAMER_PEF2256` depends on device tree and I/O memory support, and selects `GENERIC_FRAMER`, `MFD_CORE`, and `REGMAP_MMIO`.

Control flow: build selection starts with `menuconfig FRAMER`; if enabled, users can select the PEF2256 driver. Selecting PEF2256 automatically enables the generic framer core and required infrastructure.

State and persistence: only build-time state. It does not create runtime configuration or persisted settings.

Dependencies and integration points: integrates with the kernel build system, OF/platform device matching, MFD child devices, and MMIO regmap. The help text describes the framer abstraction used by HDLC/TDM consumers such as the QMC HDLC driver.

Risks: if future framer consumers select only `GENERIC_FRAMER` without `FRAMER`, menu visibility and dependency intent should remain coherent. PEF2256 currently depends on OF, so non-DT platforms cannot build/use it through this option.

Test signals: Kconfig tests should cover `FRAMER=n`, `FRAMER=y/m` with `FRAMER_PEF2256=n`, and `FRAMER_PEF2256=y/m`, verifying selected symbols and linked objects.

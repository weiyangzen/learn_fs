## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Makefile

Purpose: this Makefile assembles the SJA1105/SJA1110 DSA driver object from common source files and conditionally includes feature modules for PTP, Time-Aware Scheduling, and Virtual Links.

Important APIs, types, and functions: `obj-$(CONFIG_NET_DSA_SJA1105) += sja1105.o` builds the composite object. Always-included objects are SPI transport, main driver, MDIO, flower classifier support, ethtool, devlink, clocking, static config, and dynamic config. Conditional additions are `sja1105_ptp.o`, `sja1105_tas.o`, and `sja1105_vl.o`.

Control flow: Kconfig symbol selection determines whether the composite object is omitted, built-in, or modular. Optional object inclusion follows feature symbols and therefore must match the prototypes and conditional declarations used by `sja1105.h` and related headers.

State and persistence: there is no runtime state. The build composition controls which runtime features and DSA callbacks are present in `sja1105.o`.

Dependencies and integration points: the Makefile is coupled to the SJA1105 Kconfig options and the C files in this directory. It ensures shared files such as `sja1105_clocking.c` and `sja1105_devlink.c` are present in every base-driver build.

Risks: because feature objects are linked into one composite driver, missing conditional guards in headers or source files can create unresolved symbols when optional features are disabled. The trailing backslash after `sja1105_dynamic_config.o` is accepted here because further conditional appends follow, but edits should preserve valid kbuild syntax.

Test signals: build `CONFIG_NET_DSA_SJA1105` as module and built-in, then repeat with each optional symbol enabled/disabled; inspect `sja1105.o` membership with verbose kbuild output when diagnosing missing symbols.

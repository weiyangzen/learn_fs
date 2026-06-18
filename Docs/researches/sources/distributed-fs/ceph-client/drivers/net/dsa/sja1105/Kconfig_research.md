## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Kconfig

Purpose: this Kconfig file declares build options for the NXP SJA1105/SJA1110 automotive Ethernet switch DSA driver and optional PTP, TAS, and Virtual Link features.

Important APIs, types, and functions: `CONFIG_NET_DSA_SJA1105` is a tristate depending on `NET_DSA`, `SPI`, and optional PTP clock infrastructure. It selects the SJA1105 DSA tagger, PCS XPCS, packing helpers, and CRC32. `CONFIG_NET_DSA_SJA1105_PTP` enables timestamping/PTP clock support. `CONFIG_NET_DSA_SJA1105_TAS` enables Time-Aware Scheduler offload and depends on PTP plus taprio. `CONFIG_NET_DSA_SJA1105_VL` enables Virtual Links and depends on TAS.

Control flow: build selection starts with the base SPI-managed DSA switch driver, then optional symbols layer feature-specific objects into the build through the Makefile. The TAS symbol enforces either built-in taprio support or modular DSA driver compatibility to avoid impossible linkage.

State and persistence: there is no runtime state in Kconfig. The selected symbols control which code is compiled into `sja1105.o`, which directly changes available driver behavior for PTP clocks, scheduled traffic, and flow classification.

Dependencies and integration points: this file integrates with kernel configuration symbols for DSA, SPI, PTP, taprio qdisc, tag protocols, PCS XPCS, packing, and CRC32. It documents supported switch revisions from SJA1105E/T/P/Q/R/S through SJA1110A/B/C/D.

Risks: optional feature dependencies matter because TAS relies on PTP and VL relies on TAS; misconfigured builds should be prevented by Kconfig. Enabling the base driver selects several helper subsystems, increasing build surface even for users not using all chip variants.

Test signals: run build matrix coverage for base-only, base+PTP, base+PTP+TAS, and full VL configurations; verify module/built-in combinations with `NET_SCH_TAPRIO`; and confirm selected tagger and helper libraries are available.

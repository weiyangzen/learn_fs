# sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Kconfig

Purpose: this Kconfig entry exposes the Hirschmann Hellcreek TSN switch driver as `NET_DSA_HIRSCHMANN_HELLCREEK`. It controls whether the Hellcreek DSA platform driver, PTP support, hardware timestamping, LED integration, TAPRIO offload support, and Hellcreek tagging support can be built.

Important APIs, types, and functions: the single config symbol is a tristate named "Hirschmann Hellcreek TSN Switch support". It depends on `HAS_IOMEM`, `NET_DSA`, `PTP_1588_CLOCK`, `LEDS_CLASS`, and `NET_SCH_TAPRIO`, and selects `NET_DSA_TAG_HELLCREEK`.

Control flow: when enabled, the Makefile builds `hellcreek_sw.o` from `hellcreek.o`, `hellcreek_ptp.o`, and `hellcreek_hwtstamp.o`. Selecting the tagger ensures DSA can parse and emit the Hellcreek-specific CPU-port tag format required by the driver.

State and persistence: this file stores no runtime state. It determines whether the driver is compiled in, built as a module, or omitted, and whether required framework symbols must be enabled.

Dependencies and integration points: the dependencies mirror runtime driver needs: MMIO register access, DSA switch registration, PTP clock registration, LED class devices, and TAPRIO schedule offload. The selected tagger is the DSA integration point for packet metadata.

Risks: making PTP, LED, or TAPRIO hard dependencies means the switch driver is unavailable in smaller DSA builds lacking any one subsystem. Missing `NET_DSA_TAG_HELLCREEK` selection would make the driver unusable at runtime.

Test signals: Kconfig dependency resolution for built-in and module builds, automatic tagger selection, and successful compilation of the three-object Hellcreek switch module when all dependencies are enabled.

# sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Makefile

Purpose: this Makefile wires the Hellcreek driver objects into the kernel build when `CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK` is enabled.

Important APIs, types, and functions: `obj-$(CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK) += hellcreek_sw.o` declares the composite module or built-in object. `hellcreek_sw-objs` includes `hellcreek.o`, `hellcreek_ptp.o`, and `hellcreek_hwtstamp.o`.

Control flow: Kbuild links the main DSA/platform driver, the PTP clock implementation, and hardware timestamp support into one driver unit named `hellcreek_sw`.

State and persistence: there is no runtime state. The file controls object composition and therefore which symbols are available inside the driver.

Dependencies and integration points: it is paired with `Kconfig` and relies on the three C files having internal symbol references such as `hellcreek_ptp_setup()`, `hellcreek_hwtstamp_setup()`, and DSA timestamp callbacks.

Risks: omitting any component breaks either link-time references or runtime functionality. The composite object name differs from the platform driver's `.driver.name` (`hellcreek`), so packaging or module-load expectations should follow Kbuild output rather than the platform driver name.

Test signals: `make drivers/net/dsa/hirschmann/` with the config enabled, module symbol resolution across the three objects, and `modinfo`/module load verifying the combined object registers the Hellcreek platform driver.

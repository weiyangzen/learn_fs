<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Kconfig

Purpose: defines the LPDDR and LPDDR2 PCM MTD configuration menu. It gates legacy LPDDR flash command support, QINFO probing, and LPDDR2-NVM PCM support behind `MTD`.

Important APIs, types, and functions: Kconfig symbols are `MTD_LPDDR`, `MTD_QINFO_PROBE`, and `MTD_LPDDR2_NVM`. `MTD_LPDDR` selects `MTD_QINFO_PROBE`; `MTD_QINFO_PROBE` depends on `MTD_LPDDR`; `MTD_LPDDR2_NVM` depends on `MTD && ARM` because the driver uses `writel_relaxed()`.

Control flow: selecting `MTD_LPDDR` builds the QINFO probe and LPDDR command-set object through the Makefile. Selecting `MTD_LPDDR2_NVM` builds the platform driver for LPDDR2-NVM devices.

State and persistence: no runtime state; this file controls which drivers are compiled into the kernel or modules.

Dependencies and integration points: integrates with the parent MTD Kconfig tree and with `drivers/mtd/lpddr/Makefile`. The `select MTD_QINFO_PROBE` relationship ensures LPDDR chip detection is available whenever command support is enabled.

Risks: `MTD_QINFO_PROBE` both depends on and is selected by `MTD_LPDDR`, so it is not useful as an independent probe choice. The ARM-only LPDDR2 guard means non-ARM compile coverage is intentionally absent unless the dependency changes. Test signals are expected object inclusion in `.config`, menu visibility under `MTD`, and successful builds for module and built-in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Kconfig -->

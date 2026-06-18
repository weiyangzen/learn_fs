# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Kconfig

Purpose: Defines the IBM Ethernet vendor menu and top-level selectable IBM network drivers for the kernel networking Kconfig tree.

Important configuration entries: `NET_VENDOR_IBM` is a vendor gate that defaults to `y` and depends on `PPC_PSERIES`, `PPC_DCR`, or `(IBMEBUS && SPARSEMEM)`. `IBMVETH` enables IBM LAN Virtual Ethernet on pSeries. `IBMVETH_KUNIT_TEST` enables KUnit tests for the IBMVETH driver, requiring built-in KUnit and built-in IBMVETH. `source "drivers/net/ethernet/ibm/emac/Kconfig"` includes embedded PowerPC EMAC options. `EHEA` enables the IBM pSeries eHEA adapter driver and depends on `IBMEBUS && SPARSEMEM`. `IBMVNIC` enables IBM Virtual NIC support on pSeries.

Control flow: The file is declarative. The kernel Kconfig frontend evaluates the vendor gate first; when `NET_VENDOR_IBM` is enabled, it exposes IBMVETH, EMAC, EHEA, and IBMVNIC prompts. Selected symbols are consumed by the directory Makefile and subdirectory Makefiles to include the corresponding objects.

State and persistence: Configuration state persists in `.config`, not in this file. The file itself carries dependency topology and help text only. The notable runtime implication is that `CONFIG_EHEA` cannot be selected outside an IBM eBus sparse-memory environment.

Dependencies and integration: Integrates with the global network-device Kconfig hierarchy and the adjacent `drivers/net/ethernet/ibm/Makefile`. The EMAC subtree contributes its own `IBM_EMAC` and feature symbols. IBMVETH and IBMVNIC rely on pSeries platform support; EHEA relies on IBM eBus and sparse memory infrastructure.

Risks: Broad vendor gate defaults can expose prompts in more configurations than strictly needed, but leaf dependencies constrain buildability. `IBMVETH_KUNIT_TEST` requires both KUnit and IBMVETH built in, so module-only IBMVETH configurations will not run that test. EHEA's dependency on sparse memory is essential because its memory-region busmap logic assumes sparsemem sections.

Test signals: Kconfig resolution for pSeries, PPC DCR embedded, IBMEBUS/SPARSEMEM, and unrelated architectures; compile tests for `CONFIG_EHEA=m/y`, `CONFIG_IBM_EMAC=m/y`, `CONFIG_IBMVETH_KUNIT_TEST=y`, and vendor gate disabled.

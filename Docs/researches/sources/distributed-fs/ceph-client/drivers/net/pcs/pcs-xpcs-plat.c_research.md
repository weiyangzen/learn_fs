# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-plat.c

Purpose: Implements a platform driver that exposes memory-mapped Synopsys DesignWare XPCS registers as an MDIO bus/device for the XPCS core.

Important APIs, types, and functions: `struct dw_xpcs_plat` stores platform device, synthetic MDIO bus, direct/indirect register mode, register width, MMIO base, and CSR clock. MMIO accessors implement C22/C45 read/write through direct or viewport-indirect addressing. Probe helpers are `xpcs_plat_init_res()`, `xpcs_plat_init_clk()`, `xpcs_plat_init_bus()`, and `xpcs_plat_init_dev()`. Runtime PM callbacks gate the optional CSR clock.

Control flow: Probe allocates data, parses `reg-io-width`, selects a resource named `"direct"` or `"indirect"`, validates address-space size, maps MMIO, enables runtime PM, registers a synthetic MDIO bus, creates a single MDIO device at address 0, attaches the firmware node and match data, and registers the MDIO device so the XPCS driver core can bind to it. MMIO MDIO operations resume runtime PM around each register access.

State and persistence behavior: Software state is devm-managed and persists for the platform device lifetime. The MDIO bus/device abstracts XPCS CSR access; hardware register state is owned by the XPCS core and PMA helpers.

Dependencies and integration points: It depends on platform resources, OF match data, clocks, runtime PM, MDIO bus/device APIs, and `DW_XPCS_INFO_DECLARE()` entries for compatible PMA IDs. It bridges device-tree `"snps,dw-xpcs*"` nodes to the generic XPCS library.

Risks and edge cases: Direct access requires a large 2 MiB-like window while indirect access uses a 256-register viewport; resource naming and size validation must match bindings. Address formatting combines MMD and register into MMIO offsets and can break if register width is wrong. Each MDIO op resumes/suspends PM, so high-frequency polling can churn clocks. Only MDIO address 0 is valid.

Test signals: Probe with direct and indirect resources, reg-io-width 2 and 4, invalid resource names/sizes, optional clock absent/present, runtime PM suspend/resume around reads, C22 and C45 access correctness, fwnode reuse, and all supported OF compatibles.

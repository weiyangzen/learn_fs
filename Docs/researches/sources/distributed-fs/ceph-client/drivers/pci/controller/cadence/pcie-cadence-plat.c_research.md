<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-plat.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-plat.c

Purpose: generic platform driver for Cadence PCIe controllers in either host or endpoint mode. It allocates the appropriate Cadence RC/EP object, initializes PHYs, enables runtime PM, applies a CPU-to-bus address fixup, and delegates to shared Cadence host or endpoint setup.

Important APIs/types/functions: `struct cdns_plat_pcie`, `cdns_plat_cpu_addr_fixup()`, `cdns_plat_pcie_probe()`, `cdns_plat_pcie_shutdown()`, match data `cdns_plat_pcie_host_of_data` and `cdns_plat_pcie_ep_of_data`, and `cdns_plat_ops`.

Control flow: probe reads match data to determine RC or EP mode, allocates platform state, allocates a host bridge or endpoint structure, initializes generic PHYs through `cdns_pcie_init_phy()`, enables runtime PM, gets an active PM reference, then calls `cdns_pcie_host_setup()` or `cdns_pcie_ep_setup()`. Failure unwinds runtime PM and PHY state. Shutdown drops runtime PM, disables PM, and disables PHY.

State/persistence: `struct cdns_plat_pcie` only points at the active `struct cdns_pcie`. Hardware state is owned by common Cadence setup: PHY power, address translations, link state, and endpoint memory. Runtime PM state is maintained through PM core counters.

Dependencies/integration: OF compatible strings `cdns,cdns-pcie-host` and `cdns,cdns-pcie-ep`, platform resources expected by Cadence common setup, generic PHY framework, runtime PM, and optional build-time host/EP configs.

Risks: probe error paths return 0 after `err_init/err_get_sync`, which can hide setup failures and leave a bound but unusable device. `platform_set_drvdata()` stores `struct cdns_plat_pcie`, while shutdown calls `dev_get_drvdata()` as if it were `struct cdns_pcie *`, which is a type mismatch risk. Device links are deleted manually but PHY devm objects remain.

Test signals: host and endpoint compatible probe, forced PM failure, PHY absent and multi-PHY cases, CPU address fixup behavior, shutdown correctness, and probe failure return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-plat.c -->

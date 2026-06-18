# sources/distributed-fs/ceph-client/drivers/ata/ahci_octeon.c

Purpose: Cavium Octeon III SATA UCTL glue driver programming parent shim endian/DMA settings, then populating child AHCI platform devices.

Important API: `ahci_octeon_probe`, OF compatible `cavium,octeon-7130-sata-uctl`, `CVMX_SATA_UCTL_SHIM_CFG`, and Octeon CSR read/write helpers.

Control flow: probe maps resource 0, reads shim config, clears endian fields, sets DMA/CSR endian according to CPU endianness, enables DMA read command behavior, writes config, validates OF node, and calls `of_platform_populate`.

State/persistence: only hardware shim config and child devices; no private runtime state or PM hooks.

Dependencies/integration: Octeon CSR helpers, platform resources, OF population, and child `ahci-platform` core.

Risks/test signals: wrong endian config breaks AHCI MMIO/DMA; child description errors surface after population. Test child creation, endian-correct I/O, child AHCI probe, and absence of UCTL DMA errors.

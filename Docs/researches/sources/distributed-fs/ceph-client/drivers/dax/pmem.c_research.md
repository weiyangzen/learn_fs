# sources/distributed-fs/ceph-client/drivers/dax/pmem.c

Purpose: libnvdimm PMEM-DAX driver that creates a static dev_dax device from an NVDIMM DAX namespace.

Important APIs/types/functions: `__dax_pmem_probe()`, `dax_pmem_probe()`, `dax_pmem_driver`, and module init/exit.

Control flow and state: probe obtains a namespace, temporarily enables it to read the PFN info block, calls `nvdimm_setup_pfn()` to populate pgmap, disables the namespace, reserves metadata before `dataoff`, parses namespace ID into DAX region/device IDs, adjusts the DAX range to data start, allocates a static DAX region with namespace alignment, and creates a static dev_dax with the pgmap and full data size.

Dependencies and integration: depends on libnvdimm namespace/PFN helpers, nd device drivers, DAX bus, memory resources, and PMEM namespace metadata layout.

Risks and test signals: metadata reservation, namespace-name parsing, PFN superblock alignment/dataoff, static pgmap lifetime, and namespace enable/disable sequencing are key. Test valid and corrupt PFN info, metadata conflicts, namespace naming, different alignments, and static device-DAX binding.

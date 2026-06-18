# sources/distributed-fs/ceph-client/drivers/nvdimm/of_pmem.c

Purpose: Registers Device Tree described `pmem-region` and `pmem-region-v2` memory ranges as libnvdimm regions. It is the OF-specific discovery path for platform persistent or volatile memory without per-DIMM label emulation.

Important APIs and flow: `of_pmem_region_probe()` allocates private bus state, creates an NVDIMM bus descriptor named after the platform device, registers an `nvdimm_bus`, detects the optional `volatile` property, and creates one libnvdimm region per platform resource. Nonvolatile regions set `ND_REGION_PAGEMAP` and `ND_REGION_PERSIST_MEMCTRL`; volatile regions set `ND_REGION_PAGEMAP` and use `nvdimm_volatile_region_create()`. `of_pmem_region_remove()` unregisters the bus and frees the private allocation.

State and persistence behavior: Persistent state is only the platform-described physical resource. Runtime state is `struct of_pmem_private` with the bus descriptor and bus pointer. The driver does not maintain labels, security state, or flush metadata itself.

Dependencies and integration points: Depends on OF matching, platform resources, `nvdimm_bus_register()`, and region creation from `region_devs.c`. The created regions are later probed by the generic region and pmem namespace drivers.

Risks and test signals: Probe continues after individual region creation failures and returns success if the bus registered, which can hide partial resource registration. Tests should cover missing OF node, allocation/register failure cleanup, volatile versus nonvolatile properties, multiple resources, NUMA assignment, and both compatible strings.

# sources/distributed-fs/ceph-client/drivers/dax/Kconfig

Purpose: Kconfig menu for the DAX subsystem and its device, PMEM, HMEM, CXL, FS-DAX-compatible, and KMEM drivers.

Important APIs/types/functions: config symbols `DAX`, `DEV_DAX`, `DEV_DAX_PMEM`, `DEV_DAX_HMEM`, `DEV_DAX_CXL`, `DEV_DAX_HMEM_DEVICES`, `DEV_DAX_FSDEV`, and `DEV_DAX_KMEM`.

Control flow and state: the menu gates which DAX providers and consumers are compiled. `DEV_DAX` requires THP support for deterministic mmap mappings; PMEM depends on libnvdimm/NVDIMM_DAX; HMEM depends on EFI soft reserve and intentionally has CXL dependency tautologies to allow build ordering; CXL DAX depends on CXL bus/region and DAX; FSDEV is selected with FS_DAX; KMEM depends on memory hotplug.

Dependencies and integration: integrates kernel configuration with libnvdimm, CXL, EFI soft-reserve, NUMA memory info, FS_DAX, and memory hotplug.

Risks and test signals: incorrect dependencies can produce link failures or missing runtime drivers. Test allmodconfig/allyesconfig/minimal configs, DAX without KMEM, CXL DAX with/without HMEM, FS_DAX enabled, and NVDIMM_DAX-driven defaults.

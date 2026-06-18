# sources/distributed-fs/ceph-client/drivers/cxl/mem.c

Purpose: CXL bus driver for memory expander devices. It takes a registered `cxl_memdev`, enumerates/attaches it into the CXL port topology, exposes debugfs/sysfs poison controls, optionally creates a CXL NVDIMM, and blocks unsafe suspend while active.

Important APIs/types/functions: `cxl_mem_probe()`, `devm_cxl_add_memdev()`, `trigger_poison_list_store()`, `cxl_mem_visible()`, debugfs handlers for DPA display, poison inject, and poison clear, and `cxl_mem_driver` with `CXL_DEVICE_MEMORY_EXPANDER`.

Control flow and state: probe requires media ready and no pending detach work, creates debugfs entries, calls `devm_cxl_enumerate_ports()`, finds the parent CXL port/dport, adds libnvdimm representation if PMEM capacity exists, adds an endpoint port under either RCH parent or normal port parent, calls optional attach callback, registers EDAC, increments active memdev suspend blocker, and registers devm cleanup. Poison sysfs visibility is controlled by enumerated poison command bits.

Dependencies and integration: depends on CXL core, port enumeration, CXL PCI helpers, CXL poison helpers, libnvdimm PMEM support, EDAC hooks, debugfs, and driver core device locking.

Risks and test signals: failure paths must unwind debugfs and active-suspend refs. Topology races are handled by single-threaded detach/rescan work but remain sensitive to pending detach checks and parent driver presence. Test media-not-ready, missing topology, RCH vs VH endpoint creation, PMEM disabled by platform, poison command visibility, EDAC failure tolerance, detach/rebind, and suspend blocking.

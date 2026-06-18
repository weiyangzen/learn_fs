
# sources/distributed-fs/ceph-client/drivers/cxl/core/core.h

Purpose: private CXL core header declaring shared internal APIs, types, conditional stubs, locks, and device type/attribute exports used across CXL core and platform drivers.

Important APIs, types, and functions: declares CXL nvdimm/pmu types and base attributes; `enum cxl_detach_mode`; `struct cxl_region_context` for endpoint translation setup; region APIs and macros gated by `CONFIG_CXL_REGION`; mailbox query/send APIs; DPA allocation/free helpers; RCRB helpers and PCI capability masks; global `struct cxl_rwsem cxl_rwsem`; memdev/mbox init; poison/RAS/feature APIs; PCI latency/bandwidth and switch dport bandwidth helpers; `port_to_host()` and `dport_to_host()` host-device helpers; HDM decode and possible-dport APIs; and `cxl_rcd_component_reg_phys()`.

Control flow: the header itself has no runtime flow, but conditional inline stubs define no-op behavior when `CONFIG_CXL_REGION` or `CONFIG_CXL_RAS` is disabled. Helper functions derive host devices based on whether a port is root, first-level, or nested.

State and persistence: declares the global CXL rwsems that serialize region HPA/interleave changes and DPA-space changes. Other state is owned by implementation files and devices.

Dependencies and integration points: includes CXL mailbox definitions and Linux rwsem. It is included by CXL core files such as CDAT/ATL and by drivers needing internal CXL APIs. Namespace exports in implementation files correspond to declarations here.

Risks and test signals: stale declarations or stubs can hide missing feature wiring in disabled configs. Locking comments on `cxl_rwsem.region` and `.dpa` define important invariants for region/DPA operations. Test signals include compile coverage with region/RAS/features disabled, lockdep assertions in CDAT/region paths, host helper behavior for root and nested ports, and namespace/export consistency.

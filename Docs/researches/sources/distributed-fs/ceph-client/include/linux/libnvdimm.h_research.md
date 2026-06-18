# sources/distributed-fs/ceph-client/include/linux/libnvdimm.h

Purpose: declares the libnvdimm subsystem provider interface for persistent-memory buses, DIMMs, regions, bad ranges, security, firmware activation, command descriptors, flush behavior, and pmem cache maintenance.

Important APIs and types: `struct badrange` tracks bad physical ranges. Flags describe DIMM states, region persistence/cache capabilities, CXL origin, and adjusted DPA resources. `struct nvdimm_bus_descriptor`, `ndctl_fn`, `struct nd_cmd_desc`, `struct nd_interleave_set`, `struct nd_mapping_desc`, and `struct nd_region_desc` define provider registration and region topology. Security is modeled by `struct nvdimm_security_ops`, passphrase/key types, and security bit states. Firmware activation uses bus and DIMM fw op structs plus state/result/capability enums. APIs register buses, create/delete DIMMs and regions, issue commands, compute command sizes, manage lanes, flush, check cache/overwrite state, and map pmem.

Control flow: a platform provider registers a bus descriptor, creates NVDIMMs with command/security/fw ops, describes regions/mappings, and libnvdimm exposes regions and namespaces. Commands flow through `nvdimm_ctl()` to the provider's `ndctl`; flush and security/fw operations delegate to provider callbacks.

State and persistence: subsystem state is in-memory device-model state, but it describes persistent media, labels, bad ranges, security state, and firmware activation. Flush/cache helpers determine durability semantics for writes to pmem.

Dependencies and integration points: depends on device model, resources, bios, spinlocks, UUIDs, io mapping, and architecture pmem cache APIs. Integrates ACPI NFIT/CXL-style providers with pmem/blk/volatile region drivers.

Risks and test signals: risks include command buffer size validation, badrange locking, stale security flags, unsafe access to locked/overwrite devices, flush capability misreporting, and firmware activation state drift. Test bus/DIMM/region registration, ndctl command sizing, badrange add/forget, pmem flush on platforms with/without cache API, security operations, firmware activation, CXL region flags, and namespace creation.

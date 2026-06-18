# sources/distributed-fs/ceph-client/drivers/cxl/cxl.h

Purpose: central private CXL core header for the port, decoder, region, PMEM, DAX-region, and driver-model objects shared by CXL ACPI/PCI/core services. It defines register offsets and bit fields for component, RAS, device-status, event, and mailbox blocks, plus helpers for HDM decoder count and interleave encoding/decoding.

Important APIs/types/functions: `struct cxl_decoder`, endpoint/switch/root decoder variants, `struct cxl_region` and `struct cxl_region_params`, `struct cxl_port`, `struct cxl_dport`, `struct cxl_ep`, `struct cxl_region_ref`, CXL bus driver registration helpers, and constructors such as `devm_cxl_add_port()`, `devm_cxl_add_endpoint()`, `devm_cxl_add_dport()`, `cxl_*_decoder_alloc()`, `devm_cxl_add_nvdimm_bridge()`, and region/DAX/PMEM conversion helpers.

Control flow and state: the header encodes the topology state machine: roots own ports, ports own dports/endpoints/regions via xarrays, decoders transition through manual/auto/auto-staged and region config states, and region flags track auto assembly, reset-required, lock, and normalized-addressing behavior. Persistence-related state is represented by `cxl_nvdimm`, `cxl_pmem_region`, PMEM mappings, and CXL region UUID/HPA/mode metadata.

Dependencies and integration: depends on Linux driver core, PCI, resource/range handling, libnvdimm, access-coordinate performance data, and CXL UAPI headers. It is the contract used by CXL PCI, port, PMEM, region, DAX, RAS, ACPI, and unit-test code.

Risks and test signals: bugs here affect ABI-like internal contracts across many drivers. Watch interleave conversions, resource lifetime, xarray keying by device pointers, region locking, reset flags, and CONFIG-gated inline fallbacks. Test signals include CXL topology enumeration, decoder sysfs programming, PMEM/DAX region creation, RAS setup, suspend/reset paths, and CXL unit tests that override `__mock`.

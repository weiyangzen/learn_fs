# sources/distributed-fs/ceph-client/drivers/cxl/cxlpci.h

Purpose: private CXL PCI header for register-location discovery, CDAT-over-DOE table layout, restricted CXL-device detection, flit-mode probing, and PCI/RAS integration hooks.

Important APIs/types/functions: `enum cxl_regloc_type`, `struct cdat_header`, `struct cdat_entry_header`, `union cdat_data`, `struct cdat_doe_rsp`, `cxl_pci_flit_256()`, `is_cxl_restricted()`, `read_cdat_data()`, `cxl_pci_setup_regs()`, and CONFIG_CXL_RAS-gated error/RAS setup declarations.

Control flow and state: the header gives CXL PCI code the register-block identifiers used to find component, virtual, memdev, and PMU register blocks. CDAT structures define parsing boundaries for topology/performance data cached in `struct cxl_port`. RCD detection switches path handling to root-complex register block behavior rather than normal upstream-port registers.

Dependencies and integration: depends on PCI core and `cxl.h`; consumed by `pci.c`, `mem.c`, `port.c`, RAS code, CDAT readers, and PMU setup. It connects PCIe capability state and DOE table access to the CXL bus model.

Risks and test signals: CDAT length/checksum/entry handling and RCD path logic are easy to regress because hardware topology differs between VH and RCH modes. Test with normal endpoints, RCiEP/RCD devices, missing register blocks, CONFIG_CXL_RAS off, DOE/CDAT absence, and PCIe flit-mode capability variations.

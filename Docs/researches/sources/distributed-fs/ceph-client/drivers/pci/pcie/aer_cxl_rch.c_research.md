<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_cxl_rch.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_cxl_rch.c

## Purpose
`aer_cxl_rch.c` adapts PCIe AER handling for CXL Root Complex Hierarchy cases. Internal errors logged by an RCEC may represent protocol errors in CXL downstream ports that are not normal visible PCIe ports, so this file forwards those events to CXL memory device drivers associated with the RCEC.

## Important APIs, Types, and Functions
Key helpers are `is_cxl_mem_dev()`, `cxl_error_is_native()`, `cxl_rch_handle_error_iter()`, `cxl_rch_handle_error()`, `handles_cxl_error_iter()`, `handles_cxl_errors()`, and `cxl_rch_enable_rcec()`. `cxl_rch_handle_error()` and `cxl_rch_enable_rcec()` are declared in `portdrv.h` under `CONFIG_CXL_RAS`.

## Control Flow and State
`cxl_rch_enable_rcec()` is called during AER service probe. If the RCEC is native AER-owned and walking its associated endpoints finds a function 0 CXL memory-class device, it unmasks correctable and uncorrectable internal errors on the RCEC. During AER processing, `cxl_rch_handle_error()` checks whether the reporting device is an RCEC and whether the AER status represents an internal error. If so, it walks associated devices and invokes `cor_error_detected()` or `error_detected()` on CXL memory drivers according to severity.

## Dependencies and Integration Points
The file depends on PCI AER helpers, RCEC association walking from port bus support, CXL memory class codes, and driver `pci_error_handlers`. It is called from `aer.c` before generic PCI AER handling, allowing CXL-specific protocol error notification without replacing the standard recovery path.

## Risks and Test Signals
Risks include missing multi-function CXL devices if class/function assumptions change, invoking callbacks when firmware owns AER, or double-notifying if future CXL topology becomes visible through regular downstream ports. Tests should cover native and firmware-owned RCEC configurations, CXL memory devices behind RCH, internal correctable/nonfatal/fatal AER bits, and absence of err_handler callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_cxl_rch.c -->
